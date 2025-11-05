"""
Transcription service for assembling audio chunks and triggering transcription.
"""
import os
import asyncio
import logging
from typing import List, Optional
from pydub import AudioSegment

from app.core.config import settings
from app.llm.interface import LLMProvider
from app.llm.requestyai_provider import RequestYaiProvider
from app.llm.mock_provider import MockLLMProvider
from app.repositories.mysql_recording_repository import MySQLRecordingRepository
from app.models.recording import RecordingChunk

logger = logging.getLogger(__name__)


class TranscriptionService:
    """
    Service for handling audio assembly and transcription.
    """
    
    def __init__(self, recording_repository: MySQLRecordingRepository, llm_provider: Optional[LLMProvider] = None):
        """
        Initialize transcription service.
        
        Args:
            recording_repository: Repository for recording operations
            llm_provider: Optional LLM provider (will create default if not provided)
        """
        self.recording_repository = recording_repository
        self.llm_provider = llm_provider or self._create_default_provider()
    
    def _create_default_provider(self) -> LLMProvider:
        """
        Create default LLM provider based on configuration.
        
        Returns:
            LLM provider instance
        """
        if settings.debug or settings.llm_provider == "mock":
            return MockLLMProvider()
        else:
            return RequestYaiProvider(api_key=settings.llm_api_key)
    
    async def assemble_and_transcribe(self, recording_id: str) -> bool:
        """
        Assemble audio chunks and transcribe the complete recording.
        
        Args:
            recording_id: ID of the recording to process
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get recording and chunks
            recording = self.recording_repository.get_recording(recording_id)
            if not recording:
                logger.error(f"Recording {recording_id} not found")
                return False
            
            chunks = self.recording_repository.get_chunks(recording_id)
            if not chunks:
                logger.warning(f"No chunks found for recording {recording_id}")
                return False
            
            # Assemble audio chunks
            assembled_audio_path = await self._assemble_chunks(recording_id, chunks)
            if not assembled_audio_path:
                logger.error(f"Failed to assemble chunks for recording {recording_id}")
                return False
            
            # Transcribe assembled audio
            transcription = await self.llm_provider.transcribe_audio_async(assembled_audio_path)
            
            # Update recording with transcription
            self.recording_repository.update_recording_transcription(
                recording_id=recording_id,
                transcription_text=transcription,
                audio_file_path=assembled_audio_path
            )
            
            logger.info(f"Successfully transcribed recording {recording_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing recording {recording_id}: {e}")
            return False
    
    async def _assemble_chunks(self, recording_id: str, chunks: List[RecordingChunk]) -> Optional[str]:
        """
        Assemble audio chunks into a single file.
        
        Args:
            recording_id: Recording ID
            chunks: List of audio chunks to assemble
            
        Returns:
            Path to assembled audio file or None if failed
        """
        try:
            # Sort chunks by index
            sorted_chunks = sorted(chunks, key=lambda x: x.chunk_index)
            
            # Initialize combined audio
            combined_audio = None
            
            for chunk in sorted_chunks:
                if not os.path.exists(chunk.audio_blob_path):
                    logger.warning(f"Chunk file not found: {chunk.audio_blob_path}")
                    continue
                
                try:
                    # Load audio chunk
                    chunk_audio = AudioSegment.from_wav(chunk.audio_blob_path)
                    
                    if combined_audio is None:
                        combined_audio = chunk_audio
                    else:
                        combined_audio += chunk_audio
                        
                except Exception as e:
                    logger.warning(f"Failed to load chunk {chunk.chunk_index}: {e}")
                    continue
            
            if combined_audio is None:
                logger.error(f"No valid chunks found for recording {recording_id}")
                return None
            
            # Save assembled audio
            output_path = os.path.join(
                settings.audio_storage_path, 
                recording_id, 
                "assembled_audio.wav"
            )
            
            combined_audio.export(output_path, format="wav")
            logger.info(f"Assembled audio saved to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error assembling chunks for recording {recording_id}: {e}")
            return None
    
    async def process_recording_async(self, recording_id: str):
        """
        Asynchronously process a recording (for background tasks).
        
        Args:
            recording_id: Recording ID to process
        """
        await self.assemble_and_transcribe(recording_id)
