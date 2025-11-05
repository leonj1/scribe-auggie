# Railway Deployment Guide

This guide explains how to deploy the Audio Transcription Service on Railway.

## 🚀 Quick Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/scribe-auggie)

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: This repository must be accessible to Railway
3. **Environment Variables**: Prepare the required environment variables

## 🏗️ Architecture on Railway

The application will be deployed as separate services:

- **Backend Service**: FastAPI application (Python)
- **Frontend Service**: React application (Node.js)
- **Database Service**: MySQL database

## 🔧 Environment Variables

### Backend Service Variables

```env
# Database (Railway will provide these automatically if using Railway MySQL)
MYSQL_URL=mysql://user:password@host:port/database
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=audio_transcription
MYSQL_USER=appuser
MYSQL_PASSWORD=apppassword

# Authentication
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET=your_jwt_secret_key

# LLM Provider
LLM_API_KEY=your_requestyai_api_key

# Application
DEBUG=false
LOG_LEVEL=INFO
AUDIO_STORAGE_PATH=/app/audio_storage
PORT=8000
PYTHONPATH=/app
```

### Frontend Service Variables

```env
# API Configuration
REACT_APP_API_URL=https://your-backend-service.railway.app
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id

# Railway
PORT=3000
NODE_ENV=production
```

## 📦 Deployment Steps

### Option 1: Deploy from GitHub (Recommended)

1. **Connect Repository**:
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `leonj1/scribe-auggie`

2. **Deploy Backend**:
   - Railway will detect the `backend/railway.json` configuration
   - Add environment variables in Railway dashboard
   - Deploy will start automatically

3. **Deploy Frontend**:
   - Create a new service in the same project
   - Connect to the same repository
   - Set root directory to `frontend`
   - Add frontend environment variables
   - Deploy will start automatically

4. **Add Database**:
   - In your Railway project, click "New Service"
   - Select "Database" → "MySQL"
   - Railway will automatically provide connection details

### Option 2: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy backend
cd backend
railway up

# Deploy frontend (in new terminal)
cd frontend
railway up

# Add MySQL database
railway add mysql
```

## 🔗 Service Configuration

### Backend Service

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Health Check**: `/health`
- **Port**: `8000`

### Frontend Service

- **Build Command**: `npm install && npm run build`
- **Start Command**: `npx serve -s build -l $PORT`
- **Health Check**: `/`
- **Port**: `3000`

### Database Service

- **Type**: MySQL 8.0
- **Auto-generated**: Connection string, credentials
- **Persistent**: Data persists across deployments

## 🌐 Custom Domains

1. Go to your service in Railway dashboard
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Update DNS records as instructed
5. Update `REACT_APP_API_URL` in frontend environment variables

## 📊 Monitoring

Railway provides built-in monitoring:

- **Logs**: Real-time application logs
- **Metrics**: CPU, Memory, Network usage
- **Health Checks**: Automatic health monitoring
- **Alerts**: Email notifications for issues

## 🔧 Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check build logs in Railway dashboard
   - Verify all dependencies are listed in requirements.txt/package.json
   - Ensure environment variables are set

2. **Database Connection Issues**:
   - Verify MYSQL_URL format: `mysql://user:password@host:port/database`
   - Check if database service is running
   - Ensure backend can reach database service

3. **Frontend API Connection**:
   - Verify `REACT_APP_API_URL` points to backend service URL
   - Check CORS configuration in backend
   - Ensure both services are in the same Railway project

### Debug Commands

```bash
# View logs
railway logs

# Check service status
railway status

# Connect to database
railway connect mysql

# Run commands in service
railway run <command>
```

## 💰 Pricing

Railway offers:
- **Hobby Plan**: $5/month per service
- **Pro Plan**: Usage-based pricing
- **Free Tier**: Limited resources for testing

## 🔒 Security

- All traffic is HTTPS by default
- Environment variables are encrypted
- Private networking between services
- Automatic security updates

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Railway Templates](https://railway.app/templates)
- [Railway Discord](https://discord.gg/railway)
- [Railway Status](https://status.railway.app)

## 🚀 Post-Deployment

After successful deployment:

1. **Test the application**: Visit your frontend URL
2. **Configure Google OAuth**: Add Railway URLs to Google Console
3. **Set up monitoring**: Configure alerts and notifications
4. **Update documentation**: Share the live URLs with your team
