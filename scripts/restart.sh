#!/bin/bash

# Audio Transcription Service - Restart Script

echo "🔄 Restarting Audio Transcription Service..."
echo "============================================"

# Restart all services
docker compose restart

echo "⏳ Waiting for services to be ready..."
sleep 15

echo "✅ Services restarted successfully!"
echo ""
echo "📱 Frontend:     http://localhost:3000"
echo "🔧 Backend API:  http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/docs"
