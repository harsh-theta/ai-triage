#!/bin/bash

# Deploy for direct access (IP:PORT)
echo "🚀 Deploying for direct access via IP:PORT"

# Stop any running containers
docker-compose down

# Build and start services with direct access override
docker-compose -f docker-compose.yml -f docker-compose.direct.yml up --build -d

echo "✅ Application deployed for direct access!"
echo "📱 Frontend: http://localhost:8010"
echo "🔧 Backend API: http://localhost:9001"
echo "📊 API Docs: http://localhost:9001/docs"
echo ""
echo "🔍 Check status: docker-compose ps"
echo "📋 View logs: docker-compose logs -f"