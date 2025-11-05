"""
Recording API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel
import os
import aiofiles
import asyncio
import logging

from app.models.user import User
from app.models.recording import Recording
from app.repositories.mysql_recording_repository import MySQLRecordingRepository
from app.api.dependencies import get_current_user, get_recording_repository
from app.core.config import settings
from app.services.transcription_service import TranscriptionService

router = APIRouter()
logger = logging.getLogger(__name__)


class RecordingResponse(BaseModel):
    """Response model for recording operations."""
    id: str
    user_id: str
    status: str
    created_at: str
    updated_at: str
    audio_file_path: Optional[str]
    transcription_text: Optional[str]
    llm_provider: str
    notes: Optional[str]
    chunk_count: int


class RecordingListResponse(BaseModel):
    """Response model for listing recordings."""
    recordings: List[RecordingResponse]
    total: int
    limit: int
    offset: int


class UpdateNotesRequest(BaseModel):
    """Request model for updating recording notes."""
    notes: str


@router.post("/", response_model=RecordingResponse)
async def create_recording(
    current_user: User = Depends(get_current_user),
    recording_repository: MySQLRecordingRepository = Depends(get_recording_repository)
):
    """
    Create a new recording session.
    
    Args:
        current_user: Current authenticated user
        recording_repository: Recording repository dependency
        
    Returns:
        Created recording information
    """
    try:
        recording = recording_repository.create_recording(current_user.id)
        
        # Create directory for this recording's chunks
        recording_dir = os.path.join(settings.audio_storage_path, recording.id)
        os.makedirs(recording_dir, exist_ok=True)
        
        return RecordingResponse(**recording.to_dict())
    except Exception as e:
        logger.error(f"Failed to create recording for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create recording"
        )


@router.get("/", response_model=RecordingListResponse)
async def list_recordings(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    recording_repository: MySQLRecordingRepository = Depends(get_recording_repository)
):
    """
    List recordings for the current user.
    
    Args:
        limit: Maximum number of recordings to return
        offset: Number of recordings to skip
        current_user: Current authenticated user
        recording_repository: Recording repository dependency
        
    Returns:
        List of user's recordings
    """
    try:
        recordings = recording_repository.list_recordings(current_user.id, limit, offset)
        
        recording_responses = [
            RecordingResponse(**recording.to_dict()) 
            for recording in recordings
        ]
        
        return RecordingListResponse(
            recordings=recording_responses,
            total=len(recording_responses),  # In a real app, you'd get the actual total count
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Failed to list recordings for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recordings"
        )


@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(
    recording_id: str,
    current_user: User = Depends(get_current_user),
    recording_repository: MySQLRecordingRepository = Depends(get_recording_repository)
):
    """
    Get a specific recording by ID.
    
    Args:
        recording_id: Recording ID
        current_user: Current authenticated user
        recording_repository: Recording repository dependency
        
    Returns:
        Recording information
        
    Raises:
        HTTPException: If recording not found or access denied
    """
    recording = recording_repository.get_recording(recording_id)
    
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return RecordingResponse(**recording.to_dict())


@router.post("/{recording_id}/chunks")
async def upload_chunk(
    recording_id: str,
    chunk_index: int = Form(...),
    audio_chunk: UploadFile = File(...),
    duration_seconds: Optional[float] = Form(None),
    current_user: User = Depends(get_current_user),
    recording_repository: MySQLRecordingRepository = Depends(get_recording_repository)
):
    """
    Upload an audio chunk for a recording.
    
    Args:
        recording_id: Recording ID
        chunk_index: Sequential index of the chunk
        audio_chunk: Audio file chunk
        duration_seconds: Optional duration of the chunk
        current_user: Current authenticated user
        recording_repository: Recording repository dependency
        
    Returns:
        Success message with chunk information
        
    Raises:
        HTTPException: If recording not found, access denied, or upload fails
    """
    # Verify recording exists and belongs to user
    recording = recording_repository.get_recording(recording_id)
    
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if recording.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload chunks to non-active recording"
        )
    
    try:
        # Save chunk file
        recording_dir = os.path.join(settings.audio_storage_path, recording_id)
        os.makedirs(recording_dir, exist_ok=True)
        
        chunk_filename = f"chunk_{chunk_index:04d}.wav"
        chunk_path = os.path.join(recording_dir, chunk_filename)
        
        async with aiofiles.open(chunk_path, 'wb') as f:
            content = await audio_chunk.read()
            await f.write(content)
        
        # Add chunk to database
        chunk = recording_repository.add_chunk(
            recording_id=recording_id,
            chunk_index=chunk_index,
            audio_blob_path=chunk_path,
            duration_seconds=duration_seconds
        )
        
        logger.info(f"Uploaded chunk {chunk_index} for recording {recording_id}")
        
        return {
            "message": "Chunk uploaded successfully",
            "chunk_id": chunk.id,
            "chunk_index": chunk_index,
            "file_size": len(content)
        }
        
    except Exception as e:
        logger.error(f"Failed to upload chunk for recording {recording_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload chunk"
        )


@router.patch("/{recording_id}/pause")
async def pause_recording(
    recording_id: str,
    current_user: User = Depends(get_current_user),
    recording_repository: MySQLRecordingRepository = Depends(get_recording_repository)
):
    """
    Pause a recording.

    Args:
        recording_id: Recording ID
        current_user: Current authenticated user
        recording_repository: Recording repository dependency

    Returns:
        Updated recording information

    Raises:
        HTTPException: If recording not found or access denied
    """
    # Verify recording exists and belongs to user
    recording = recording_repository.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        updated_recording = recording_repository.update_recording_status(recording_id, "paused")
        logger.info(f"Paused recording {recording_id}")

        return RecordingResponse(**updated_recording.to_dict())

    except Exception as e:
        logger.error(f"Failed to pause recording {recording_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause recording"
        )


@router.post("/{recording_id}/finish")
async def finish_recording(
    recording_id: str,
    current_user: User = Depends(get_current_user),
    recording_repository: MySQLRecordingRepository = Depends(get_recording_repository)
):
    """
    Finish a recording and trigger transcription.

    Args:
        recording_id: Recording ID
        current_user: Current authenticated user
        recording_repository: Recording repository dependency

    Returns:
        Updated recording information

    Raises:
        HTTPException: If recording not found or access denied
    """
    # Verify recording exists and belongs to user
    recording = recording_repository.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        # Mark recording as ended
        updated_recording = recording_repository.update_recording_status(recording_id, "ended")

        # Trigger audio assembly and transcription in background
        transcription_service = TranscriptionService(recording_repository)
        asyncio.create_task(transcription_service.process_recording_async(recording_id))

        logger.info(f"Finished recording {recording_id} - transcription started")

        return RecordingResponse(**updated_recording.to_dict())

    except Exception as e:
        logger.error(f"Failed to finish recording {recording_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to finish recording"
        )


@router.patch("/{recording_id}/notes")
async def update_recording_notes(
    recording_id: str,
    notes_request: UpdateNotesRequest,
    current_user: User = Depends(get_current_user),
    recording_repository: MySQLRecordingRepository = Depends(get_recording_repository)
):
    """
    Update notes for a recording.

    Args:
        recording_id: Recording ID
        notes_request: Notes update request
        current_user: Current authenticated user
        recording_repository: Recording repository dependency

    Returns:
        Updated recording information

    Raises:
        HTTPException: If recording not found or access denied
    """
    # Verify recording exists and belongs to user
    recording = recording_repository.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        updated_recording = recording_repository.update_recording_notes(
            recording_id,
            notes_request.notes
        )
        logger.info(f"Updated notes for recording {recording_id}")

        return RecordingResponse(**updated_recording.to_dict())

    except Exception as e:
        logger.error(f"Failed to update notes for recording {recording_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notes"
        )
