# 🩺 Audio Transcription Service

A secure healthcare audio transcription platform for healthcare professionals to record and transcribe patient notes.

## Features

- Google-based authentication
- Long audio recordings with chunk streaming
- Auto transcription via LLM provider
- Dashboard to manage and review transcriptions
- HIPAA-compliant security standards

## Architecture

- **Frontend**: ReactJS with Ant Design
- **Backend**: FastAPI with MySQL
- **Authentication**: Google OAuth2 with JWT
- **Transcription**: Abstracted LLM provider interface

## Quick Start

### 🚀 Deploy on Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/scribe-auggie)

For detailed Railway deployment instructions, see [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md).

### Prerequisites (Local Development)

- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Environment Variables

Create a `.env` file in the root directory:

```env
# Google OAuth2
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# LLM Provider
LLM_API_KEY=your_requestyai_api_key

# Database
MYSQL_URL=mysql://user:password@localhost:3306/audio_transcription
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=audio_transcription
MYSQL_USER=appuser
MYSQL_PASSWORD=apppassword

# Backend
JWT_SECRET=your_jwt_secret_key
AUDIO_STORAGE_PATH=/app/audio_storage

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
```

### Running with Docker

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Restart services
docker compose restart
```

### Management Scripts

Use the provided management scripts for easier operation:

```bash
# Start services
./scripts/manage.sh start

# Stop services
./scripts/manage.sh stop

# Restart services
./scripts/manage.sh restart

# Check status
./scripts/manage.sh status

# View logs
./scripts/manage.sh logs

# Validate all services
./scripts/manage.sh validate

# Clean up (remove volumes)
./scripts/manage.sh clean
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development

#### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

## Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── repositories/   # Repository pattern implementations
│   │   ├── services/       # Business logic
│   │   ├── api/           # API endpoints
│   │   └── core/          # Configuration and utilities
│   ├── tests/             # Backend tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── utils/         # Utilities
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## Security

- All network traffic uses HTTPS/TLS in production
- Bearer token authentication for all protected endpoints
- Audio data and transcriptions encrypted at rest
- HIPAA-compliant design for healthcare use

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🚀 Deployment

### Railway (Recommended)

This project is configured for easy deployment on Railway:

1. **One-Click Deploy**: Use the Railway button above
2. **Manual Deploy**: See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for detailed instructions
3. **Environment Variables**: Configure required variables in Railway dashboard

### Docker Production

```bash
# Build and run in production mode
docker compose -f docker-compose.yml up -d

# Or use the production override
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## License

This project is proprietary software for healthcare use.
