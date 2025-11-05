"""
Recording and RecordingChunk models for the Audio Transcription Service.
"""
from sqlalchemy import Column, String, DateTime, Text, Float, Integer, ForeignKey, Enum
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class RecordingStatus(enum.Enum):
    """Enumeration for recording status."""
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


class Recording(Base):
    """
    Recording model representing an audio recording session.
    """
    __tablename__ = "recordings"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(Enum(RecordingStatus), default=RecordingStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    audio_file_path = Column(Text, nullable=True)
    transcription_text = Column(Text, nullable=True)
    llm_provider = Column(String(100), default="requestyai", nullable=False)
    notes = Column(Text, nullable=True)  # User notes on the recording session
    
    # Relationships
    user = relationship("User", back_populates="recordings")
    chunks = relationship("RecordingChunk", back_populates="recording", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Recording(id={self.id}, user_id={self.user_id}, status={self.status})>"
    
    def to_dict(self):
        """Convert recording to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "audio_file_path": self.audio_file_path,
            "transcription_text": self.transcription_text,
            "llm_provider": self.llm_provider,
            "notes": self.notes,
            "chunk_count": len(self.chunks) if self.chunks else 0
        }


class RecordingChunk(Base):
    """
    RecordingChunk model representing individual audio chunks of a recording.
    """
    __tablename__ = "recording_chunks"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recording_id = Column(CHAR(36), ForeignKey("recordings.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    audio_blob_path = Column(Text, nullable=False)
    duration_seconds = Column(Float, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    recording = relationship("Recording", back_populates="chunks")
    
    def __repr__(self):
        return f"<RecordingChunk(id={self.id}, recording_id={self.recording_id}, chunk_index={self.chunk_index})>"
    
    def to_dict(self):
        """Convert recording chunk to dictionary for API responses."""
        return {
            "id": self.id,
            "recording_id": self.recording_id,
            "chunk_index": self.chunk_index,
            "audio_blob_path": self.audio_blob_path,
            "duration_seconds": self.duration_seconds,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }
