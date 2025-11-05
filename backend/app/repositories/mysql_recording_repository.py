"""
MySQL implementation of RecordingRepository.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging

from app.models.recording import Recording, RecordingChunk, RecordingStatus
from app.repositories.interfaces import RecordingRepository

logger = logging.getLogger(__name__)


class MySQLRecordingRepository:
    """MySQL implementation of RecordingRepository interface."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_recording(self, user_id: str) -> Recording:
        """Create a new recording session."""
        try:
            recording = Recording(
                user_id=user_id,
                status=RecordingStatus.ACTIVE
            )
            self.db.add(recording)
            self.db.commit()
            self.db.refresh(recording)
            logger.info(f"Created recording: {recording.id} for user: {user_id}")
            return recording
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create recording for user {user_id}: {e}")
            raise
    
    def get_recording(self, recording_id: str) -> Optional[Recording]:
        """Get recording by ID."""
        return self.db.query(Recording).filter(Recording.id == recording_id).first()
    
    def list_recordings(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Recording]:
        """List recordings for a user."""
        return (
            self.db.query(Recording)
            .filter(Recording.user_id == user_id)
            .order_by(desc(Recording.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def update_recording_status(self, recording_id: str, status: str) -> Optional[Recording]:
        """Update recording status."""
        recording = self.get_recording(recording_id)
        if not recording:
            return None
        
        try:
            recording.status = RecordingStatus(status)
            self.db.commit()
            self.db.refresh(recording)
            logger.info(f"Updated recording {recording_id} status to {status}")
            return recording
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update recording {recording_id} status: {e}")
            raise
    
    def update_recording_transcription(self, recording_id: str, transcription_text: str, audio_file_path: str) -> Optional[Recording]:
        """Update recording with transcription and final audio file path."""
        recording = self.get_recording(recording_id)
        if not recording:
            return None
        
        try:
            recording.transcription_text = transcription_text
            recording.audio_file_path = audio_file_path
            self.db.commit()
            self.db.refresh(recording)
            logger.info(f"Updated recording {recording_id} with transcription")
            return recording
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update recording {recording_id} transcription: {e}")
            raise
    
    def update_recording_notes(self, recording_id: str, notes: str) -> Optional[Recording]:
        """Update recording notes."""
        recording = self.get_recording(recording_id)
        if not recording:
            return None
        
        try:
            recording.notes = notes
            self.db.commit()
            self.db.refresh(recording)
            logger.info(f"Updated recording {recording_id} notes")
            return recording
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update recording {recording_id} notes: {e}")
            raise
    
    def add_chunk(self, recording_id: str, chunk_index: int, audio_blob_path: str, duration_seconds: Optional[float] = None) -> RecordingChunk:
        """Add an audio chunk to a recording."""
        try:
            chunk = RecordingChunk(
                recording_id=recording_id,
                chunk_index=chunk_index,
                audio_blob_path=audio_blob_path,
                duration_seconds=duration_seconds
            )
            self.db.add(chunk)
            self.db.commit()
            self.db.refresh(chunk)
            logger.info(f"Added chunk {chunk_index} to recording {recording_id}")
            return chunk
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add chunk to recording {recording_id}: {e}")
            raise
    
    def get_chunks(self, recording_id: str) -> List[RecordingChunk]:
        """Get all chunks for a recording, ordered by chunk_index."""
        return (
            self.db.query(RecordingChunk)
            .filter(RecordingChunk.recording_id == recording_id)
            .order_by(RecordingChunk.chunk_index)
            .all()
        )
    
    def delete_recording(self, recording_id: str) -> bool:
        """Delete a recording and all its chunks."""
        recording = self.get_recording(recording_id)
        if not recording:
            return False
        
        try:
            self.db.delete(recording)
            self.db.commit()
            logger.info(f"Deleted recording {recording_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete recording {recording_id}: {e}")
            raise
