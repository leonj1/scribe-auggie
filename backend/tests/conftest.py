"""
Pytest configuration and fixtures for backend tests.
"""
import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.core.config import settings
from app.models import User, Recording, RecordingChunk
from main import app


# Test database URL (SQLite for testing)
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    # Clean up test database file
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    # Override the get_db dependency
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield session
    
    # Clean up
    session.rollback()
    session.close()
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    user = User(
        google_id="test_google_id_123",
        email="test@example.com",
        display_name="Test User",
        avatar_url="https://example.com/avatar.jpg"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_recording(test_db, test_user):
    """Create a test recording."""
    recording = Recording(
        user_id=test_user.id,
        status="active"
    )
    test_db.add(recording)
    test_db.commit()
    test_db.refresh(recording)
    return recording


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user."""
    from app.core.security import create_access_token
    
    token_data = {
        "sub": test_user.id,
        "email": test_user.email,
        "display_name": test_user.display_name
    }
    token = create_access_token(token_data)
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def temp_audio_file():
    """Create a temporary audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        # Write some dummy audio data
        temp_file.write(b"RIFF" + b"\x00" * 36 + b"WAVE" + b"\x00" * 100)
        temp_file_path = temp_file.name
    
    yield temp_file_path
    
    # Clean up
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)


@pytest.fixture
def mock_llm_provider():
    """Create a mock LLM provider for testing."""
    from app.llm.mock_provider import MockLLMProvider
    
    return MockLLMProvider(
        mock_transcription="This is a test transcription.",
        simulate_delay=False,
        should_fail=False
    )
