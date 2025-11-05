"""
Mock LLM provider for testing purposes.
"""
import asyncio
import logging
from typing import Optional

from app.llm.interface import BaseLLMProvider

logger = logging.getLogger(__name__)


class MockLLMProvider(BaseLLMProvider):
    """
    Mock implementation of the LLM provider interface for testing.
    """
    
    def __init__(self, api_key: str = "mock_key", **kwargs):
        """
        Initialize mock provider.
        
        Args:
            api_key: Mock API key (not used)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.mock_transcription = kwargs.get(
            'mock_transcription', 
            "This is a mock transcription of the audio file. The patient reports feeling well today with no significant symptoms."
        )
        self.simulate_delay = kwargs.get('simulate_delay', True)
        self.delay_seconds = kwargs.get('delay_seconds', 2.0)
        self.should_fail = kwargs.get('should_fail', False)
        self.failure_message = kwargs.get('failure_message', "Mock transcription failure")
    
    def transcribe_audio(self, audio_path: str) -> str:
        """
        Mock synchronous transcription.
        
        Args:
            audio_path: Path to the audio file (not actually read)
            
        Returns:
            Mock transcribed text
            
        Raises:
            Exception: If configured to fail
        """
        if not self.validate_audio_file(audio_path):
            raise ValueError(f"Invalid audio file: {audio_path}")
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        if self.simulate_delay:
            import time
            time.sleep(self.delay_seconds)
        
        logger.info(f"Mock transcription completed for: {audio_path}")
        return f"{self.mock_transcription} [File: {audio_path}]"
    
    async def transcribe_audio_async(self, audio_path: str) -> str:
        """
        Mock asynchronous transcription.
        
        Args:
            audio_path: Path to the audio file (not actually read)
            
        Returns:
            Mock transcribed text
            
        Raises:
            Exception: If configured to fail
        """
        if not self.validate_audio_file(audio_path):
            raise ValueError(f"Invalid audio file: {audio_path}")
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        if self.simulate_delay:
            await asyncio.sleep(self.delay_seconds)
        
        logger.info(f"Mock async transcription completed for: {audio_path}")
        return f"{self.mock_transcription} [File: {audio_path}]"
    
    def get_supported_formats(self) -> list[str]:
        """
        Get mock supported audio formats.
        
        Returns:
            List of supported file extensions
        """
        return ['.wav', '.mp3', '.m4a', '.ogg', '.flac', '.mock']
