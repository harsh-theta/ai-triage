#!/bin/bash

# Frontend Deployment Script for AI Triage System
# This script rebuilds and deploys the frontend with the optimized nginx configuration

set -e

echo "🚀 Starting frontend deployment with optimized nginx configuration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run this script from the project root directory."
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    print_error "Frontend directory not found."
    exit 1
fi

print_status "Stopping existing frontend container..."
docker-compose stop frontend || true

print_status "Removing existing frontend container..."
docker-compose rm -f frontend || true

print_status "Building frontend with optimized nginx configuration..."
docker-compose build frontend

print_status "Starting frontend container..."
docker-compose up -d frontend

print_status "Waiting for frontend to be ready..."
sleep 10

# Check if frontend is healthy
print_status "Checking frontend health..."
if curl -f http://localhost:8010/health > /dev/null 2>&1; then
    print_status "✅ Frontend is healthy and responding!"
else
    print_warning "⚠️  Frontend health check failed, but container might still be starting..."
fi

# Check if frontend serves the main page
print_status "Testing frontend main page..."
if curl -f http://localhost:8010/ > /dev/null 2>&1; then
    print_status "✅ Frontend main page is accessible!"
else
    print_error "❌ Frontend main page is not accessible!"
    print_error "Check the logs with: docker-compose logs frontend"
    exit 1
fi

# Check if static assets are served correctly
print_status "Testing static assets..."
if curl -f http://localhost:8010/_next/ > /dev/null 2>&1; then
    print_status "✅ Static assets are being served correctly!"
else
    print_warning "⚠️  Static assets might not be ready yet..."
fi

print_status "🎉 Frontend deployment completed successfully!"
print_status "Frontend is now running on http://localhost:8010"
print_status "Health check endpoint: http://localhost:8010/health"

# Show container status
print_status "Container status:"
docker-compose ps frontend

# Show recent logs
print_status "Recent logs:"
docker-compose logs --tail=20 frontend

echo ""
print_status "Next steps:"
echo "1. Update your server nginx configuration with server-nginx-optimized.conf"
echo "2. Test the full application at https://demo.thetatechnolabs.com/intelligent-triage/"
echo "3. Check logs if there are any issues: docker-compose logs frontend"
