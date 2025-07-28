#!/bin/bash

# Deploy for proxy access (demo.company.com/intelligent-triage/)
echo "🚀 Deploying for proxy access with base path /intelligent-triage/"

# Stop any running containers
docker-compose down

# Build and start services with default configuration (proxy mode)
docker-compose up --build -d

echo "✅ Application deployed for proxy access!"
echo "📱 Frontend: demo.company.com/intelligent-triage/"
echo "🔧 Backend API: demo.company.com/intelligent-triage/"
echo "📊 API Docs: demo.company.com/intelligent-triage/docs"
echo ""
echo "🔍 Check status: docker-compose ps"
echo "📋 View logs: docker-compose logs -f"