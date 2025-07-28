#!/bin/bash

# Debug script for AI Triage deployment issues
# This script will help identify what's working and what's not

echo "🔍 AI Triage Deployment Debug Script"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Checking Docker containers...${NC}"
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Docker containers are running${NC}"
    docker-compose ps
else
    echo -e "${RED}❌ Docker containers are not running${NC}"
    echo "Run './deploy.sh' to start the services"
    exit 1
fi

echo ""
echo -e "${BLUE}2. Testing container connectivity...${NC}"

# Test frontend container
if docker-compose exec frontend wget -q --spider http://backend:9001/intelligent-triage/tts/health 2>/dev/null; then
    echo -e "${GREEN}✅ Frontend can connect to backend${NC}"
else
    echo -e "${RED}❌ Frontend cannot connect to backend${NC}"
fi

echo ""
echo -e "${BLUE}3. Testing local endpoints...${NC}"

# Test frontend locally
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8010/intelligent-triage | grep -q "200"; then
    echo -e "${GREEN}✅ Frontend accessible at localhost:8010${NC}"
else
    echo -e "${RED}❌ Frontend not accessible at localhost:8010${NC}"
fi

# Test backend locally
if curl -s -o /dev/null -w "%{http_code}" http://localhost:9001/intelligent-triage/docs | grep -q "200"; then
    echo -e "${GREEN}✅ Backend accessible at localhost:9001${NC}"
else
    echo -e "${RED}❌ Backend not accessible at localhost:9001${NC}"
fi

echo ""
echo -e "${BLUE}4. Testing API endpoints...${NC}"

# Test API endpoint
API_RESPONSE=$(curl -s -X POST http://localhost:9001/intelligent-triage/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "session_id": "test123"}' 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$API_RESPONSE" ]; then
    echo -e "${GREEN}✅ API endpoint responding${NC}"
else
    echo -e "${RED}❌ API endpoint not responding${NC}"
fi

echo ""
echo -e "${BLUE}5. Checking environment variables...${NC}"

# Check docker-compose environment
echo "Docker Compose Environment:"
echo "NEXT_PUBLIC_BACKEND_URL: $(docker-compose exec frontend printenv NEXT_PUBLIC_BACKEND_URL)"
echo "NEXT_PUBLIC_API_BASE_PATH: $(docker-compose exec frontend printenv NEXT_PUBLIC_API_BASE_PATH)"
echo "ROOT_PATH: $(docker-compose exec backend printenv ROOT_PATH)"

echo ""
echo -e "${BLUE}6. Checking frontend logs for errors...${NC}"
FRONTEND_ERRORS=$(docker-compose logs frontend 2>&1 | grep -i "error\|failed\|exception" | tail -5)
if [ -n "$FRONTEND_ERRORS" ]; then
    echo -e "${YELLOW}⚠️  Frontend errors found:${NC}"
    echo "$FRONTEND_ERRORS"
else
    echo -e "${GREEN}✅ No frontend errors found${NC}"
fi

echo ""
echo -e "${BLUE}7. Checking backend logs for errors...${NC}"
BACKEND_ERRORS=$(docker-compose logs backend 2>&1 | grep -i "error\|failed\|exception" | tail -5)
if [ -n "$BACKEND_ERRORS" ]; then
    echo -e "${YELLOW}⚠️  Backend errors found:${NC}"
    echo "$BACKEND_ERRORS"
else
    echo -e "${GREEN}✅ No backend errors found${NC}"
fi

echo ""
echo -e "${BLUE}8. Network connectivity test...${NC}"

# Test if ports are accessible
if netstat -tuln 2>/dev/null | grep -q ":8010 "; then
    echo -e "${GREEN}✅ Port 8010 is listening${NC}"
else
    echo -e "${RED}❌ Port 8010 is not listening${NC}"
fi

if netstat -tuln 2>/dev/null | grep -q ":9001 "; then
    echo -e "${GREEN}✅ Port 9001 is listening${NC}"
else
    echo -e "${RED}❌ Port 9001 is not listening${NC}"
fi

echo ""
echo -e "${BLUE}9. Apache/Apache2 status check...${NC}"

# Check if Apache is running
if command -v apache2ctl >/dev/null 2>&1; then
    if sudo apache2ctl -M 2>/dev/null | grep -q "proxy_module"; then
        echo -e "${GREEN}✅ Apache proxy module is loaded${NC}"
    else
        echo -e "${YELLOW}⚠️  Apache proxy module not loaded${NC}"
        echo "Run: sudo a2enmod proxy && sudo systemctl restart apache2"
    fi
    
    if sudo apache2ctl -M 2>/dev/null | grep -q "headers_module"; then
        echo -e "${GREEN}✅ Apache headers module is loaded${NC}"
    else
        echo -e "${YELLOW}⚠️  Apache headers module not loaded${NC}"
        echo "Run: sudo a2enmod headers && sudo systemctl restart apache2"
    fi
else
    echo -e "${YELLOW}⚠️  Apache2 not found or not accessible${NC}"
fi

echo ""
echo -e "${BLUE}10. Summary and recommendations...${NC}"
echo "=========================================="

echo ""
echo "🔧 If you're still having issues:"
echo ""
echo "1. For 404 errors on your domain:"
echo "   - Check if Apache is configured with the provided apache.conf"
echo "   - Ensure your domain points to the correct server IP"
echo "   - Test with IP directly: http://YOUR_SERVER_IP/intelligent-triage/"
echo ""
echo "2. For double path issues (/intelligent-triage/intelligent-triage):"
echo "   - This indicates incorrect Apache configuration"
echo "   - Use the provided apache.conf file"
echo ""
echo "3. For CORS errors:"
echo "   - Check browser developer tools for specific error messages"
echo "   - Ensure CORS headers are set in Apache configuration"
echo ""
echo "4. For backend connection issues:"
echo "   - The Docker networking is working correctly"
echo "   - Check if your domain is resolving to the correct server"
echo ""
echo "📋 Next steps:"
echo "1. Follow the APACHE_SETUP.md guide"
echo "2. Configure Apache with the provided apache.conf"
echo "3. Test your domain: http://demo.companyname.com/intelligent-triage/"
echo "4. Check Apache logs: sudo tail -f /var/log/apache2/ai-triage_error.log" 