#!/bin/bash

# Audio Transcription Service - Logs Script

echo "📋 Audio Transcription Service Logs"
echo "==================================="

if [ "$1" = "" ]; then
    echo "📜 Showing logs for all services..."
    docker compose logs -f
elif [ "$1" = "mysql" ] || [ "$1" = "backend" ] || [ "$1" = "frontend" ]; then
    echo "📜 Showing logs for $1..."
    docker compose logs -f $1
else
    echo "❌ Invalid service name. Available services: mysql, backend, frontend"
    echo "💡 Usage: ./scripts/logs.sh [service_name]"
    echo "   Example: ./scripts/logs.sh backend"
    echo "   Or just: ./scripts/logs.sh (for all services)"
fi
