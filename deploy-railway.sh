#!/bin/bash

# Railway Deployment Script for Audio Transcription Service
# This script helps deploy the project to Railway

set -e

echo "🚀 Railway Deployment Script for Audio Transcription Service"
echo "============================================================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

echo "📋 Railway CLI Version: $(railway --version)"

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo ""
    echo "🔐 Authentication Required"
    echo "=========================="
    echo "You need to login to Railway first."
    echo ""
    echo "Option 1: Interactive Login"
    echo "  railway login"
    echo ""
    echo "Option 2: Use provided token"
    echo "  If you have a Railway token, you can set it as an environment variable:"
    echo "  export RAILWAY_TOKEN=your_token_here"
    echo ""
    echo "Please login and run this script again."
    exit 1
fi

echo "✅ Authenticated as: $(railway whoami)"

# Create new project
echo ""
echo "🏗️  Creating Railway Project..."
echo "==============================="

if ! railway status &> /dev/null; then
    echo "Creating new Railway project..."
    railway init
else
    echo "✅ Already linked to a Railway project"
fi

# Deploy Backend Service
echo ""
echo "🐍 Deploying Backend Service..."
echo "==============================="

cd backend
echo "📦 Deploying FastAPI backend..."

# Set backend environment variables
echo "Setting backend environment variables..."
railway variables set PORT=8000
railway variables set PYTHONPATH=/app
railway variables set DEBUG=false
railway variables set LOG_LEVEL=INFO

# Deploy backend
railway up

cd ..

# Deploy Frontend Service
echo ""
echo "⚛️  Deploying Frontend Service..."
echo "================================="

# Create a new service for frontend
railway add

cd frontend
echo "📦 Deploying React frontend..."

# Set frontend environment variables
echo "Setting frontend environment variables..."
railway variables set PORT=3000
railway variables set NODE_ENV=production

# Deploy frontend
railway up

cd ..

# Add MySQL Database
echo ""
echo "🗄️  Adding MySQL Database..."
echo "============================"

railway add mysql

echo ""
echo "✅ Deployment Complete!"
echo "======================="
echo ""
echo "🎯 Next Steps:"
echo "1. Configure environment variables in Railway dashboard"
echo "2. Set up custom domains if needed"
echo "3. Configure Google OAuth with Railway URLs"
echo "4. Test the deployed application"
echo ""
echo "📊 View your project: railway open"
echo "📜 View logs: railway logs"
echo "📋 Check status: railway status"
echo ""
echo "🌐 Your services should be available at:"
echo "   Backend: https://your-backend-service.railway.app"
echo "   Frontend: https://your-frontend-service.railway.app"
