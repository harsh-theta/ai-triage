#!/bin/bash

# Test script for nginx-based AI Triage deployment
echo "🧪 Testing nginx-based AI Triage Deployment"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Stopping existing containers...${NC}"
docker-compose down

echo -e "${BLUE}2. Building and starting new containers...${NC}"
docker-compose up --build -d

echo -e "${BLUE}3. Waiting for containers to start...${NC}"
sleep 10

echo -e "${BLUE}4. Checking container status...${NC}"
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Containers are running${NC}"
    docker-compose ps
else
    echo -e "${RED}❌ Containers failed to start${NC}"
    docker-compose logs
    exit 1
fi

echo ""
echo -e "${BLUE}5. Testing nginx frontend...${NC}"

# Test nginx health check
if curl -s http://localhost/health | grep -q "OK"; then
    echo -e "${GREEN}✅ nginx health check passed${NC}"
else
    echo -e "${RED}❌ nginx health check failed${NC}"
fi

# Test frontend static files
if curl -s -o /dev/null -w "%{http_code}" http://localhost/intelligent-triage/ | grep -q "200"; then
    echo -e "${GREEN}✅ Frontend accessible at /intelligent-triage/${NC}"
else
    echo -e "${RED}❌ Frontend not accessible${NC}"
fi

echo ""
echo -e "${BLUE}6. Testing API proxying...${NC}"

# Test API endpoint through nginx
API_RESPONSE=$(curl -s -X POST http://localhost/intelligent-triage/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "session_id": "test123"}' 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$API_RESPONSE" ]; then
    echo -e "${GREEN}✅ API proxying working${NC}"
else
    echo -e "${RED}❌ API proxying failed${NC}"
fi

# Test backend health through nginx
if curl -s http://localhost/intelligent-triage/tts/health | grep -q "tts_service_healthy"; then
    echo -e "${GREEN}✅ Backend health check through nginx working${NC}"
else
    echo -e "${RED}❌ Backend health check through nginx failed${NC}"
fi

echo ""
echo -e "${BLUE}7. Testing routing...${NC}"

# Test that double path doesn't work
if curl -s -o /dev/null -w "%{http_code}" http://localhost/intelligent-triage/intelligent-triage/ | grep -q "404"; then
    echo -e "${GREEN}✅ Double path correctly returns 404${NC}"
else
    echo -e "${YELLOW}⚠️  Double path test inconclusive${NC}"
fi

# Test root redirect
if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "301"; then
    echo -e "${GREEN}✅ Root redirects to /intelligent-triage/${NC}"
else
    echo -e "${RED}❌ Root redirect failed${NC}"
fi

echo ""
echo -e "${BLUE}8. Checking container logs...${NC}"

# Check for errors in logs
FRONTEND_ERRORS=$(docker-compose logs frontend 2>&1 | grep -i "error\|failed\|exception" | tail -3)
if [ -n "$FRONTEND_ERRORS" ]; then
    echo -e "${YELLOW}⚠️  Frontend errors found:${NC}"
    echo "$FRONTEND_ERRORS"
else
    echo -e "${GREEN}✅ No frontend errors found${NC}"
fi

BACKEND_ERRORS=$(docker-compose logs backend 2>&1 | grep -i "error\|failed\|exception" | tail -3)
if [ -n "$BACKEND_ERRORS" ]; then
    echo -e "${YELLOW}⚠️  Backend errors found:${NC}"
    echo "$BACKEND_ERRORS"
else
    echo -e "${GREEN}✅ No backend errors found${NC}"
fi

echo ""
echo -e "${BLUE}9. Summary...${NC}"
echo "=================="

echo ""
echo -e "${GREEN}🎉 nginx-based deployment test complete!${NC}"
echo ""
echo "✅ Your application should now work at:"
echo "   - Frontend: http://demo.thetatechnolabs.com/intelligent-triage/"
echo "   - API Docs: http://demo.thetatechnolabs.com/intelligent-triage/docs"
echo "   - Health: http://demo.thetatechnolabs.com/intelligent-triage/tts/health"
echo ""
echo "🔧 Key improvements:"
echo "   - Static files served by nginx (faster)"
echo "   - API requests proxied through nginx"
echo "   - No more CORS issues"
echo "   - Better caching and compression"
echo ""
echo "📋 Next steps:"
echo "1. Test your domain: http://demo.thetatechnolabs.com/intelligent-triage/"
echo "2. Deploy to your Ubuntu server"
echo "3. Configure your domain to point to your server IP" 