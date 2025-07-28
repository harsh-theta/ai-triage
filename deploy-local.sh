#!/bin/bash

# Deploy for direct access (IP:PORT)
echo "Deploying for direct access via IP:PORT"

# Load local environment variables
export $(cat .env.local | xargs)

# Build and start services
docker-compose down
docker-compose up --build -d

echo "Application deployed for direct access at: http://localhost:8010"
echo "Backend API available at: http://localhost:9001"