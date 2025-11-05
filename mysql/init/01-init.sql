-- Initialize database for Audio Transcription Service
-- This script runs when the MySQL container starts for the first time

-- Ensure the database exists
CREATE DATABASE IF NOT EXISTS audio_transcription;
USE audio_transcription;

-- Grant privileges to the application user
GRANT ALL PRIVILEGES ON audio_transcription.* TO 'appuser'@'%';
FLUSH PRIVILEGES;

-- Set timezone
SET time_zone = '+00:00';

-- Create indexes for better performance (tables will be created by SQLAlchemy)
-- These will be applied after the tables are created by the application
