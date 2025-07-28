#!/bin/bash

# Deploy for proxy access (demo.company.com/intelligent-triage/)
echo "Deploying for proxy access with base path /intelligent-triage/"

# Load proxy environment variables
export $(cat .env.proxy | xargs)

# Build and start services
docker-compose down
docker-compose up --build -d

echo "Application deployed for proxy access at: demo.company.com/intelligent-triage/"
echo "Backend API available at: demo.company.com/intelligent-triage/api/"