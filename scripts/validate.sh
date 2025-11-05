#!/bin/bash

# Audio Transcription Service - Validation Script

echo "🔍 Validating Audio Transcription Service..."
echo "============================================"

# Function to test endpoint
test_endpoint() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $description... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --max-time 30 "$url")
    
    if [ "$response" = "$expected_status" ]; then
        echo "✅ OK ($response)"
        return 0
    else
        echo "❌ FAILED ($response)"
        return 1
    fi
}

# Check if services are running
echo "📊 Checking service status..."
docker compose ps

echo ""
echo "🌐 Testing endpoints..."

# Test frontend
test_endpoint "http://localhost:3000" "Frontend (React App)"

# Test backend health
test_endpoint "http://localhost:8000/health" "Backend Health Check"

# Test backend root
test_endpoint "http://localhost:8000/" "Backend Root"

# Test Swagger docs
test_endpoint "http://localhost:8000/docs" "Backend Swagger Documentation"

# Test backend API endpoints (should return 401 without auth)
test_endpoint "http://localhost:8000/recordings/" "Backend API (Recordings)" 401

echo ""
echo "🗄️ Testing MySQL connection..."
if docker compose exec -T mysql mysql -u root -p${MYSQL_ROOT_PASSWORD:-rootpassword123} -e "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ MySQL connection OK"
else
    echo "❌ MySQL connection FAILED"
fi

echo ""
echo "📋 Container health status:"
docker compose ps --format "table {{.Name}}\t{{.Status}}"

echo ""
echo "🎯 Validation complete!"
