"""
Repository interfaces for the Audio Transcription Service.
"""
from typing import Protocol, List, Optional
from app.models.user import User
from app.models.recording import Recording, RecordingChunk


class UserRepository(Protocol):
    """Interface for user repository operations."""
    
    def create_user(self, google_id: str, email: str, display_name: str, avatar_url: Optional[str] = None) -> User:
        """Create a new user."""
        ...
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        ...
    
    def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        ...
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        ...
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user information."""
        ...


class RecordingRepository(Protocol):
    """Interface for recording repository operations."""
    
    def create_recording(self, user_id: str) -> Recording:
        """Create a new recording session."""
        ...
    
    def get_recording(self, recording_id: str) -> Optional[Recording]:
        """Get recording by ID."""
        ...
    
    def list_recordings(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Recording]:
        """List recordings for a user."""
        ...
    
    def update_recording_status(self, recording_id: str, status: str) -> Optional[Recording]:
        """Update recording status."""
        ...
    
    def update_recording_transcription(self, recording_id: str, transcription_text: str, audio_file_path: str) -> Optional[Recording]:
        """Update recording with transcription and final audio file path."""
        ...
    
    def update_recording_notes(self, recording_id: str, notes: str) -> Optional[Recording]:
        """Update recording notes."""
        ...
    
    def add_chunk(self, recording_id: str, chunk_index: int, audio_blob_path: str, duration_seconds: Optional[float] = None) -> RecordingChunk:
        """Add an audio chunk to a recording."""
        ...
    
    def get_chunks(self, recording_id: str) -> List[RecordingChunk]:
        """Get all chunks for a recording, ordered by chunk_index."""
        ...
    
    def delete_recording(self, recording_id: str) -> bool:
        """Delete a recording and all its chunks."""
        ...
