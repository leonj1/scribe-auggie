# Manual Railway Deployment Instructions

Since the Railway CLI requires interactive authentication, here are step-by-step instructions to deploy the Audio Transcription Service manually.

## 🔐 Authentication

The provided token: `20727ba7-8cd3-4a1b-a566-c2014ce081da`

### Option 1: Railway Dashboard (Recommended)

1. **Login to Railway**:
   - Go to [railway.app](https://railway.app)
   - Login with your account
   - If you have the token, you can use it in the API calls

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect to `leonj1/scribe-auggie`

### Option 2: Railway CLI (Interactive)

```bash
# Install Railway CLI (already done)
npm install -g @railway/cli

# Login interactively
railway login

# This will open a browser for authentication
```

## 🚀 Deployment Steps

### Step 1: Create Project and Deploy Backend

```bash
# Initialize project
railway init

# Navigate to backend
cd backend

# Set environment variables
railway variables set PORT=8000
railway variables set PYTHONPATH=/app
railway variables set DEBUG=false
railway variables set LOG_LEVEL=INFO

# Add required environment variables (you'll need to set these)
railway variables set MYSQL_URL="mysql://user:password@host:port/database"
railway variables set GOOGLE_CLIENT_ID="your_google_client_id"
railway variables set GOOGLE_CLIENT_SECRET="your_google_client_secret"
railway variables set JWT_SECRET="your_jwt_secret"
railway variables set LLM_API_KEY="your_llm_api_key"
railway variables set AUDIO_STORAGE_PATH="/app/audio_storage"

# Deploy backend
railway up

cd ..
```

### Step 2: Add Frontend Service

```bash
# Add new service for frontend
railway service create

# Navigate to frontend
cd frontend

# Link to the frontend service
railway service link

# Set frontend environment variables
railway variables set PORT=3000
railway variables set NODE_ENV=production
railway variables set REACT_APP_API_URL="https://your-backend-service.railway.app"
railway variables set REACT_APP_GOOGLE_CLIENT_ID="your_google_client_id"

# Deploy frontend
railway up

cd ..
```

### Step 3: Add MySQL Database

```bash
# Add MySQL database service
railway add mysql

# The database connection details will be automatically available
# Update the MYSQL_URL in your backend service with the provided connection string
```

## 🌐 Alternative: GitHub Integration

### Deploy via GitHub (Easier)

1. **Go to Railway Dashboard**:
   - Visit [railway.app/dashboard](https://railway.app/dashboard)
   - Click "New Project"

2. **Connect Repository**:
   - Select "Deploy from GitHub repo"
   - Choose `leonj1/scribe-auggie`
   - Railway will detect the configuration files

3. **Configure Services**:
   - Railway will create services based on the `railway.json` files
   - Backend service (from `/backend` directory)
   - Frontend service (from `/frontend` directory)

4. **Add Database**:
   - In your project, click "New Service"
   - Select "Database" → "MySQL"

5. **Set Environment Variables**:
   - Go to each service settings
   - Add the required environment variables

## 📋 Required Environment Variables

### Backend Service
```env
PORT=8000
PYTHONPATH=/app
DEBUG=false
LOG_LEVEL=INFO
MYSQL_URL=mysql://user:password@host:port/database
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET=your_jwt_secret_key
LLM_API_KEY=your_requestyai_api_key
AUDIO_STORAGE_PATH=/app/audio_storage
```

### Frontend Service
```env
PORT=3000
NODE_ENV=production
REACT_APP_API_URL=https://your-backend-service.railway.app
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
```

## 🔧 Using the Provided Token

If you want to use the token programmatically:

```bash
# Set the token as environment variable
export RAILWAY_TOKEN=20727ba7-8cd3-4a1b-a566-c2014ce081da

# Try Railway commands (may still require interactive login)
railway whoami
railway status
```

## 🎯 Post-Deployment Steps

1. **Get Service URLs**:
   ```bash
   railway status
   ```

2. **Update Frontend Environment**:
   - Update `REACT_APP_API_URL` with the actual backend URL

3. **Configure Google OAuth**:
   - Add Railway URLs to Google Console
   - Update redirect URIs

4. **Test the Application**:
   - Visit the frontend URL
   - Test authentication and functionality

## 🔍 Troubleshooting

### If Railway CLI doesn't work with token:

1. **Use Railway Dashboard**: Deploy via web interface
2. **Manual API calls**: Use the Railway GraphQL API directly
3. **GitHub Actions**: Set up automated deployment

### Common Issues:

- **Authentication**: Railway CLI requires interactive login
- **Environment Variables**: Must be set in Railway dashboard
- **Service Linking**: Ensure services can communicate

## 📞 Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- GitHub Issues: Create an issue in the repository
