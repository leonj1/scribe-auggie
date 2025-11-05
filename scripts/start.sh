#!/bin/bash

# Audio Transcription Service - Start Script

echo "🩺 Starting Audio Transcription Service..."
echo "========================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual configuration values"
fi

# Start services
echo "🚀 Starting Docker services..."
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
echo "   This may take a few minutes on first run..."

# Function to check service health
check_health() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker compose ps $service | grep -q "healthy"; then
            echo "✅ $service is healthy"
            return 0
        fi
        echo "   Waiting for $service... (attempt $attempt/$max_attempts)"
        sleep 10
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service failed to become healthy"
    return 1
}

# Check each service
check_health mysql
check_health backend
check_health frontend

echo ""
echo "🎉 Audio Transcription Service is running!"
echo "========================================"
echo "📱 Frontend:     http://localhost:3000"
echo "🔧 Backend API:  http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/docs"
echo "🗄️  MySQL:       localhost:3306"
echo ""
echo "📋 To view logs: docker compose logs -f"
echo "🛑 To stop:      docker compose down"
echo "🔄 To restart:   docker compose restart"
