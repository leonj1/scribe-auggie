"""
Tests for recording endpoints.
"""
import pytest
import io
from unittest.mock import patch


class TestRecordingEndpoints:
    """Test recording endpoints."""
    
    def test_create_recording_success(self, client, auth_headers):
        """Test successful recording creation."""
        response = client.post("/recordings/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "active"
        assert "user_id" in data
        assert "created_at" in data
    
    def test_create_recording_unauthorized(self, client):
        """Test recording creation without authentication."""
        response = client.post("/recordings/")
        
        assert response.status_code == 401
    
    def test_list_recordings(self, client, auth_headers, test_recording):
        """Test listing recordings."""
        response = client.get("/recordings/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "recordings" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert len(data["recordings"]) >= 1
    
    def test_get_recording_success(self, client, auth_headers, test_recording):
        """Test getting a specific recording."""
        response = client.get(f"/recordings/{test_recording.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_recording.id
        assert data["status"] == test_recording.status.value
    
    def test_get_recording_not_found(self, client, auth_headers):
        """Test getting a non-existent recording."""
        response = client.get("/recordings/nonexistent", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_upload_chunk_success(self, client, auth_headers, test_recording):
        """Test successful chunk upload."""
        # Create a mock audio file
        audio_data = b"fake audio data"
        files = {
            "audio_chunk": ("chunk.wav", io.BytesIO(audio_data), "audio/wav")
        }
        data = {
            "chunk_index": 0,
            "duration_seconds": 30.0
        }
        
        response = client.post(
            f"/recordings/{test_recording.id}/chunks",
            headers=auth_headers,
            files=files,
            data=data
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert "message" in response_data
        assert "chunk_id" in response_data
        assert response_data["chunk_index"] == 0
    
    def test_upload_chunk_invalid_recording(self, client, auth_headers):
        """Test chunk upload to non-existent recording."""
        audio_data = b"fake audio data"
        files = {
            "audio_chunk": ("chunk.wav", io.BytesIO(audio_data), "audio/wav")
        }
        data = {
            "chunk_index": 0
        }
        
        response = client.post(
            "/recordings/nonexistent/chunks",
            headers=auth_headers,
            files=files,
            data=data
        )
        
        assert response.status_code == 404
    
    def test_pause_recording(self, client, auth_headers, test_recording):
        """Test pausing a recording."""
        response = client.patch(f"/recordings/{test_recording.id}/pause", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paused"
    
    def test_finish_recording(self, client, auth_headers, test_recording):
        """Test finishing a recording."""
        with patch('app.api.recordings.TranscriptionService') as mock_service:
            mock_service.return_value.process_recording_async.return_value = None
            
            response = client.post(f"/recordings/{test_recording.id}/finish", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ended"
    
    def test_update_recording_notes(self, client, auth_headers, test_recording):
        """Test updating recording notes."""
        notes = "This is a test note for the recording."
        
        response = client.patch(
            f"/recordings/{test_recording.id}/notes",
            headers=auth_headers,
            json={"notes": notes}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == notes


class TestRecordingRepository:
    """Test recording repository."""
    
    def test_create_recording(self, test_db, test_user):
        """Test creating a recording."""
        from app.repositories.mysql_recording_repository import MySQLRecordingRepository
        
        repo = MySQLRecordingRepository(test_db)
        recording = repo.create_recording(test_user.id)
        
        assert recording.id is not None
        assert recording.user_id == test_user.id
        assert recording.status.value == "active"
        assert recording.created_at is not None
    
    def test_get_recording(self, test_db, test_recording):
        """Test getting a recording."""
        from app.repositories.mysql_recording_repository import MySQLRecordingRepository
        
        repo = MySQLRecordingRepository(test_db)
        recording = repo.get_recording(test_recording.id)
        
        assert recording is not None
        assert recording.id == test_recording.id
    
    def test_list_recordings(self, test_db, test_user, test_recording):
        """Test listing recordings."""
        from app.repositories.mysql_recording_repository import MySQLRecordingRepository
        
        repo = MySQLRecordingRepository(test_db)
        recordings = repo.list_recordings(test_user.id)
        
        assert len(recordings) >= 1
        assert recordings[0].user_id == test_user.id
    
    def test_add_chunk(self, test_db, test_recording):
        """Test adding a chunk to a recording."""
        from app.repositories.mysql_recording_repository import MySQLRecordingRepository
        
        repo = MySQLRecordingRepository(test_db)
        chunk = repo.add_chunk(
            recording_id=test_recording.id,
            chunk_index=0,
            audio_blob_path="/path/to/chunk.wav",
            duration_seconds=30.0
        )
        
        assert chunk.id is not None
        assert chunk.recording_id == test_recording.id
        assert chunk.chunk_index == 0
        assert chunk.duration_seconds == 30.0
    
    def test_update_recording_status(self, test_db, test_recording):
        """Test updating recording status."""
        from app.repositories.mysql_recording_repository import MySQLRecordingRepository
        
        repo = MySQLRecordingRepository(test_db)
        updated_recording = repo.update_recording_status(test_recording.id, "paused")
        
        assert updated_recording is not None
        assert updated_recording.status.value == "paused"
