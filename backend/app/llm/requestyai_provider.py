"""
RequestYAI LLM provider implementation for audio transcription.
"""
import httpx
import aiofiles
import logging
from typing import Optional

from app.llm.interface import BaseLLMProvider

logger = logging.getLogger(__name__)


class RequestYaiProvider(BaseLLMProvider):
    """
    RequestYAI implementation of the LLM provider interface.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.requestyai.com", **kwargs):
        """
        Initialize RequestYAI provider.
        
        Args:
            api_key: RequestYAI API key
            base_url: Base URL for RequestYAI API
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.base_url = base_url.rstrip('/')
        self.transcription_endpoint = f"{self.base_url}/v1/audio/transcriptions"
        
        # Configuration options
        self.model = kwargs.get('model', 'whisper-1')
        self.language = kwargs.get('language', 'en')
        self.response_format = kwargs.get('response_format', 'text')
        self.temperature = kwargs.get('temperature', 0.0)
    
    def transcribe_audio(self, audio_path: str) -> str:
        """
        Synchronously transcribe audio file using RequestYAI.
        
        Args:
            audio_path: Path to the audio file to transcribe
            
        Returns:
            Transcribed text
            
        Raises:
            Exception: If transcription fails
        """
        if not self.validate_audio_file(audio_path):
            raise ValueError(f"Invalid audio file: {audio_path}")
        
        try:
            with open(audio_path, 'rb') as audio_file:
                files = {
                    'file': (audio_path, audio_file, 'audio/wav')
                }
                
                data = {
                    'model': self.model,
                    'language': self.language,
                    'response_format': self.response_format,
                    'temperature': self.temperature
                }
                
                headers = {
                    'Authorization': f'Bearer {self.api_key}'
                }
                
                with httpx.Client(timeout=300.0) as client:
                    response = client.post(
                        self.transcription_endpoint,
                        files=files,
                        data=data,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        if self.response_format == 'text':
                            return response.text.strip()
                        else:
                            result = response.json()
                            return result.get('text', '').strip()
                    else:
                        logger.error(f"RequestYAI API error: {response.status_code} - {response.text}")
                        raise Exception(f"Transcription failed: {response.status_code}")
                        
        except Exception as e:
            logger.error(f"Error transcribing audio with RequestYAI: {e}")
            raise
    
    async def transcribe_audio_async(self, audio_path: str) -> str:
        """
        Asynchronously transcribe audio file using RequestYAI.
        
        Args:
            audio_path: Path to the audio file to transcribe
            
        Returns:
            Transcribed text
            
        Raises:
            Exception: If transcription fails
        """
        if not self.validate_audio_file(audio_path):
            raise ValueError(f"Invalid audio file: {audio_path}")
        
        try:
            async with aiofiles.open(audio_path, 'rb') as audio_file:
                audio_content = await audio_file.read()
                
                files = {
                    'file': (audio_path, audio_content, 'audio/wav')
                }
                
                data = {
                    'model': self.model,
                    'language': self.language,
                    'response_format': self.response_format,
                    'temperature': self.temperature
                }
                
                headers = {
                    'Authorization': f'Bearer {self.api_key}'
                }
                
                async with httpx.AsyncClient(timeout=300.0) as client:
                    response = await client.post(
                        self.transcription_endpoint,
                        files=files,
                        data=data,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        if self.response_format == 'text':
                            return response.text.strip()
                        else:
                            result = response.json()
                            return result.get('text', '').strip()
                    else:
                        logger.error(f"RequestYAI API error: {response.status_code} - {response.text}")
                        raise Exception(f"Transcription failed: {response.status_code}")
                        
        except Exception as e:
            logger.error(f"Error transcribing audio with RequestYAI: {e}")
            raise
    
    def get_supported_formats(self) -> list[str]:
        """
        Get RequestYAI supported audio formats.
        
        Returns:
            List of supported file extensions
        """
        return ['.wav', '.mp3', '.m4a', '.ogg', '.flac', '.webm']
