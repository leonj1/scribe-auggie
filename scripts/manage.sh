#!/bin/bash

# Audio Transcription Service - Management Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

show_help() {
    echo "🩺 Audio Transcription Service Management"
    echo "========================================"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start all services"
    echo "  stop      Stop all services"
    echo "  restart   Restart all services"
    echo "  status    Show service status"
    echo "  logs      Show logs for all services"
    echo "  logs-f    Follow logs for all services"
    echo "  validate  Validate all services are working"
    echo "  clean     Stop services and remove volumes"
    echo "  build     Rebuild all containers"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs backend"
    echo "  $0 validate"
}

case "$1" in
    start)
        echo "🚀 Starting Audio Transcription Service..."
        docker compose up -d
        echo ""
        echo "⏳ Waiting for services to be ready..."
        sleep 15
        echo ""
        echo "✅ Services started!"
        echo "📱 Frontend:     http://localhost:3000"
        echo "🔧 Backend API:  http://localhost:8000"
        echo "📚 API Docs:     http://localhost:8000/docs"
        ;;
    
    stop)
        echo "🛑 Stopping Audio Transcription Service..."
        docker compose down
        echo "✅ All services stopped!"
        ;;
    
    restart)
        echo "🔄 Restarting Audio Transcription Service..."
        docker compose restart
        echo "⏳ Waiting for services to be ready..."
        sleep 15
        echo "✅ Services restarted!"
        ;;
    
    status)
        echo "📊 Service Status:"
        docker compose ps
        ;;
    
    logs)
        if [ -n "$2" ]; then
            echo "📜 Showing logs for $2..."
            docker compose logs -f "$2"
        else
            echo "📜 Showing logs for all services..."
            docker compose logs -f
        fi
        ;;
    
    logs-f)
        echo "📜 Following logs for all services..."
        docker compose logs -f
        ;;
    
    validate)
        echo "🔍 Validating services..."
        ./scripts/validate.sh
        ;;
    
    clean)
        echo "🧹 Cleaning up services and volumes..."
        docker compose down -v
        echo "✅ Cleanup complete!"
        ;;
    
    build)
        echo "🔨 Rebuilding all containers..."
        docker compose build --no-cache
        echo "✅ Build complete!"
        ;;
    
    help|--help|-h)
        show_help
        ;;
    
    "")
        show_help
        ;;
    
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
