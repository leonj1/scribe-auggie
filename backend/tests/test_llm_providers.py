"""
Tests for LLM providers.
"""
import pytest
import tempfile
import os
from unittest.mock import patch, AsyncMock


class TestMockLLMProvider:
    """Test mock LLM provider."""
    
    def test_mock_provider_initialization(self):
        """Test mock provider initialization."""
        from app.llm.mock_provider import MockLLMProvider
        
        provider = MockLLMProvider(
            mock_transcription="Test transcription",
            simulate_delay=False,
            should_fail=False
        )
        
        assert provider.mock_transcription == "Test transcription"
        assert provider.simulate_delay is False
        assert provider.should_fail is False
    
    def test_mock_provider_transcribe_success(self, temp_audio_file):
        """Test successful transcription with mock provider."""
        from app.llm.mock_provider import MockLLMProvider
        
        provider = MockLLMProvider(
            mock_transcription="This is a test transcription.",
            simulate_delay=False,
            should_fail=False
        )
        
        result = provider.transcribe_audio(temp_audio_file)
        
        assert "This is a test transcription." in result
        assert temp_audio_file in result
    
    def test_mock_provider_transcribe_failure(self, temp_audio_file):
        """Test transcription failure with mock provider."""
        from app.llm.mock_provider import MockLLMProvider
        
        provider = MockLLMProvider(
            should_fail=True,
            failure_message="Mock transcription failure"
        )
        
        with pytest.raises(Exception) as exc_info:
            provider.transcribe_audio(temp_audio_file)
        
        assert "Mock transcription failure" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_mock_provider_transcribe_async(self, temp_audio_file):
        """Test async transcription with mock provider."""
        from app.llm.mock_provider import MockLLMProvider
        
        provider = MockLLMProvider(
            mock_transcription="Async test transcription.",
            simulate_delay=False,
            should_fail=False
        )
        
        result = await provider.transcribe_audio_async(temp_audio_file)
        
        assert "Async test transcription." in result
        assert temp_audio_file in result
    
    def test_mock_provider_invalid_file(self):
        """Test transcription with invalid file."""
        from app.llm.mock_provider import MockLLMProvider
        
        provider = MockLLMProvider()
        
        with pytest.raises(ValueError) as exc_info:
            provider.transcribe_audio("/nonexistent/file.wav")
        
        assert "Invalid audio file" in str(exc_info.value)


class TestRequestYaiProvider:
    """Test RequestYAI provider."""
    
    def test_requestyai_provider_initialization(self):
        """Test RequestYAI provider initialization."""
        from app.llm.requestyai_provider import RequestYaiProvider
        
        provider = RequestYaiProvider(
            api_key="test_key",
            base_url="https://api.test.com"
        )
        
        assert provider.api_key == "test_key"
        assert provider.base_url == "https://api.test.com"
        assert provider.transcription_endpoint == "https://api.test.com/v1/audio/transcriptions"
    
    @patch('httpx.Client')
    def test_requestyai_provider_transcribe_success(self, mock_client, temp_audio_file):
        """Test successful transcription with RequestYAI provider."""
        from app.llm.requestyai_provider import RequestYaiProvider
        
        # Mock the HTTP response
        mock_response = mock_client.return_value.__enter__.return_value.post.return_value
        mock_response.status_code = 200
        mock_response.text = "This is the transcribed text."
        
        provider = RequestYaiProvider(api_key="test_key")
        result = provider.transcribe_audio(temp_audio_file)
        
        assert result == "This is the transcribed text."
    
    @patch('httpx.Client')
    def test_requestyai_provider_transcribe_failure(self, mock_client, temp_audio_file):
        """Test transcription failure with RequestYAI provider."""
        from app.llm.requestyai_provider import RequestYaiProvider
        
        # Mock the HTTP response
        mock_response = mock_client.return_value.__enter__.return_value.post.return_value
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        provider = RequestYaiProvider(api_key="test_key")
        
        with pytest.raises(Exception) as exc_info:
            provider.transcribe_audio(temp_audio_file)
        
        assert "Transcription failed: 400" in str(exc_info.value)
    
    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_requestyai_provider_transcribe_async_success(self, mock_client, temp_audio_file):
        """Test successful async transcription with RequestYAI provider."""
        from app.llm.requestyai_provider import RequestYaiProvider
        
        # Mock the HTTP response
        mock_response = mock_client.return_value.__aenter__.return_value.post.return_value
        mock_response.status_code = 200
        mock_response.text = "Async transcribed text."
        
        provider = RequestYaiProvider(api_key="test_key")
        result = await provider.transcribe_audio_async(temp_audio_file)
        
        assert result == "Async transcribed text."


class TestTranscriptionService:
    """Test transcription service."""
    
    def test_transcription_service_initialization(self, test_db, mock_llm_provider):
        """Test transcription service initialization."""
        from app.services.transcription_service import TranscriptionService
        from app.repositories.mysql_recording_repository import MySQLRecordingRepository
        
        repo = MySQLRecordingRepository(test_db)
        service = TranscriptionService(repo, mock_llm_provider)
        
        assert service.recording_repository == repo
        assert service.llm_provider == mock_llm_provider
    
    @pytest.mark.asyncio
    async def test_assemble_and_transcribe_no_recording(self, test_db, mock_llm_provider):
        """Test transcription with non-existent recording."""
        from app.services.transcription_service import TranscriptionService
        from app.repositories.mysql_recording_repository import MySQLRecordingRepository
        
        repo = MySQLRecordingRepository(test_db)
        service = TranscriptionService(repo, mock_llm_provider)
        
        result = await service.assemble_and_transcribe("nonexistent_id")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_assemble_and_transcribe_no_chunks(self, test_db, test_recording, mock_llm_provider):
        """Test transcription with recording but no chunks."""
        from app.services.transcription_service import TranscriptionService
        from app.repositories.mysql_recording_repository import MySQLRecordingRepository
        
        repo = MySQLRecordingRepository(test_db)
        service = TranscriptionService(repo, mock_llm_provider)
        
        result = await service.assemble_and_transcribe(test_recording.id)
        
        assert result is False
