import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearAuthToken();
          window.location.href = '/';
        }
        return Promise.reject(error.response?.data || error.message);
      }
    );
  }

  setAuthToken(token) {
    this.authToken = token;
  }

  getAuthToken() {
    return this.authToken || localStorage.getItem('auth_token');
  }

  clearAuthToken() {
    this.authToken = null;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  }

  // Authentication endpoints
  async authenticateWithGoogle(idToken) {
    return this.client.post('/auth/google/token', {
      id_token: idToken,
    });
  }

  // Recording endpoints
  async createRecording() {
    return this.client.post('/recordings/');
  }

  async getRecordings(limit = 50, offset = 0) {
    return this.client.get('/recordings/', {
      params: { limit, offset },
    });
  }

  async getRecording(recordingId) {
    return this.client.get(`/recordings/${recordingId}`);
  }

  async uploadChunk(recordingId, chunkIndex, audioBlob, durationSeconds = null) {
    const formData = new FormData();
    formData.append('chunk_index', chunkIndex);
    formData.append('audio_chunk', audioBlob, `chunk_${chunkIndex}.wav`);
    if (durationSeconds !== null) {
      formData.append('duration_seconds', durationSeconds);
    }

    return this.client.post(`/recordings/${recordingId}/chunks`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  async pauseRecording(recordingId) {
    return this.client.patch(`/recordings/${recordingId}/pause`);
  }

  async finishRecording(recordingId) {
    return this.client.post(`/recordings/${recordingId}/finish`);
  }

  async updateRecordingNotes(recordingId, notes) {
    return this.client.patch(`/recordings/${recordingId}/notes`, {
      notes,
    });
  }

  // Health check
  async healthCheck() {
    return this.client.get('/health');
  }
}

const apiService = new ApiService();
export default apiService;
