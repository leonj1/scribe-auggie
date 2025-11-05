#!/bin/bash

# Audio Transcription Service - Stop Script

echo "🛑 Stopping Audio Transcription Service..."
echo "========================================="

# Stop and remove containers
docker compose down

echo "✅ All services stopped successfully!"
echo ""
echo "💡 To start again: ./scripts/start.sh"
echo "🗑️  To remove volumes: docker compose down -v"
