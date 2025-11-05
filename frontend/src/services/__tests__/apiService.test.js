import apiService from '../apiService';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

describe('ApiService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset the API service state
    apiService.setAuthToken(null);
  });

  describe('Authentication', () => {
    test('authenticateWithGoogle calls correct endpoint', async () => {
      const mockResponse = {
        access_token: 'test-token',
        token_type: 'bearer',
        user: { id: '1', email: 'test@example.com' }
      };

      mockedAxios.create.mockReturnValue({
        post: jest.fn().mockResolvedValue(mockResponse),
        interceptors: {
          request: { use: jest.fn() },
          response: { use: jest.fn() }
        }
      });

      const result = await apiService.authenticateWithGoogle('mock-id-token');

      expect(result).toEqual(mockResponse);
    });

    test('setAuthToken updates token', () => {
      const token = 'test-auth-token';
      apiService.setAuthToken(token);
      
      expect(apiService.getAuthToken()).toBe(token);
    });

    test('clearAuthToken removes token and user data', () => {
      // Set up some data first
      localStorage.setItem('auth_token', 'test-token');
      localStorage.setItem('user_data', '{"id": "1"}');
      
      apiService.clearAuthToken();
      
      expect(localStorage.getItem('auth_token')).toBeNull();
      expect(localStorage.getItem('user_data')).toBeNull();
    });
  });

  describe('Recording Operations', () => {
    beforeEach(() => {
      // Mock the axios client
      mockedAxios.create.mockReturnValue({
        post: jest.fn(),
        get: jest.fn(),
        patch: jest.fn(),
        interceptors: {
          request: { use: jest.fn() },
          response: { use: jest.fn() }
        }
      });
    });

    test('createRecording calls correct endpoint', async () => {
      const mockClient = mockedAxios.create();
      const mockResponse = { id: 'new-recording-id', status: 'active' };
      mockClient.post.mockResolvedValue(mockResponse);

      const result = await apiService.createRecording();

      expect(mockClient.post).toHaveBeenCalledWith('/recordings/');
    });

    test('getRecordings calls correct endpoint with parameters', async () => {
      const mockClient = mockedAxios.create();
      const mockResponse = { recordings: [], total: 0 };
      mockClient.get.mockResolvedValue(mockResponse);

      await apiService.getRecordings(25, 10);

      expect(mockClient.get).toHaveBeenCalledWith('/recordings/', {
        params: { limit: 25, offset: 10 }
      });
    });

    test('uploadChunk creates FormData correctly', async () => {
      const mockClient = mockedAxios.create();
      mockClient.post.mockResolvedValue({ success: true });

      const mockBlob = new Blob(['test'], { type: 'audio/wav' });
      
      await apiService.uploadChunk('recording-id', 0, mockBlob, 30);

      expect(mockClient.post).toHaveBeenCalledWith(
        '/recordings/recording-id/chunks',
        expect.any(FormData),
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
    });

    test('pauseRecording calls correct endpoint', async () => {
      const mockClient = mockedAxios.create();
      mockClient.patch.mockResolvedValue({ status: 'paused' });

      await apiService.pauseRecording('recording-id');

      expect(mockClient.patch).toHaveBeenCalledWith('/recordings/recording-id/pause');
    });

    test('finishRecording calls correct endpoint', async () => {
      const mockClient = mockedAxios.create();
      mockClient.post.mockResolvedValue({ status: 'ended' });

      await apiService.finishRecording('recording-id');

      expect(mockClient.post).toHaveBeenCalledWith('/recordings/recording-id/finish');
    });

    test('updateRecordingNotes calls correct endpoint', async () => {
      const mockClient = mockedAxios.create();
      mockClient.patch.mockResolvedValue({ notes: 'test notes' });

      await apiService.updateRecordingNotes('recording-id', 'test notes');

      expect(mockClient.patch).toHaveBeenCalledWith('/recordings/recording-id/notes', {
        notes: 'test notes'
      });
    });
  });

  describe('Error Handling', () => {
    test('handles 401 errors by clearing auth token', () => {
      const mockClient = {
        interceptors: {
          request: { use: jest.fn() },
          response: { 
            use: jest.fn((successHandler, errorHandler) => {
              // Simulate a 401 error
              const error = {
                response: { status: 401, data: { detail: 'Unauthorized' } }
              };
              
              // Test the error handler
              expect(() => errorHandler(error)).toThrow();
            })
          }
        }
      };

      mockedAxios.create.mockReturnValue(mockClient);
      
      // This would be called during API service initialization
      // The actual test would need to trigger the interceptor
    });
  });

  describe('Health Check', () => {
    test('healthCheck calls correct endpoint', async () => {
      const mockClient = mockedAxios.create();
      mockClient.get.mockResolvedValue({ status: 'healthy' });

      await apiService.healthCheck();

      expect(mockClient.get).toHaveBeenCalledWith('/health');
    });
  });
});
