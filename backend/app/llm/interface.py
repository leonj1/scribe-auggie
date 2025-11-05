"""
LLM Provider interface for audio transcription.
"""
from typing import Protocol, Optional
from abc import ABC, abstractmethod


class LLMProvider(Protocol):
    """
    Protocol for LLM providers that can transcribe audio.
    """
    
    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file to transcribe
            
        Returns:
            Transcribed text
            
        Raises:
            Exception: If transcription fails
        """
        ...
    
    async def transcribe_audio_async(self, audio_path: str) -> str:
        """
        Asynchronously transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file to transcribe
            
        Returns:
            Transcribed text
            
        Raises:
            Exception: If transcription fails
        """
        ...


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the LLM provider.
        
        Args:
            api_key: API key for the LLM service
            **kwargs: Additional configuration parameters
        """
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file to transcribe
            
        Returns:
            Transcribed text
            
        Raises:
            Exception: If transcription fails
        """
        pass
    
    @abstractmethod
    async def transcribe_audio_async(self, audio_path: str) -> str:
        """
        Asynchronously transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file to transcribe
            
        Returns:
            Transcribed text
            
        Raises:
            Exception: If transcription fails
        """
        pass
    
    def validate_audio_file(self, audio_path: str) -> bool:
        """
        Validate that the audio file exists and is readable.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            True if file is valid, False otherwise
        """
        import os
        return os.path.exists(audio_path) and os.path.isfile(audio_path)
    
    def get_supported_formats(self) -> list[str]:
        """
        Get list of supported audio formats.
        
        Returns:
            List of supported file extensions
        """
        return ['.wav', '.mp3', '.m4a', '.ogg', '.flac']
