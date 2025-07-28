#!/bin/bash

# Test script for AI Triage deployment
# This script tests all endpoints to ensure proper deployment

echo "🧪 Testing AI Triage Deployment"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $description... "
    
    # Get HTTP status code
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (Status: $status)"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $status)"
        return 1
    fi
}

# Function to test API endpoint
test_api_endpoint() {
    local url=$1
    local description=$2
    
    echo -n "Testing $description... "
    
    # Test if endpoint responds
    response=$(curl -s "$url" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        return 1
    fi
}

# Check if Docker containers are running
echo "📋 Checking Docker containers..."
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Docker containers are running${NC}"
else
    echo -e "${RED}❌ Docker containers are not running${NC}"
    echo "Run './deploy.sh' to start the services"
    exit 1
fi

# Get the domain from environment or use default
DOMAIN=${DOMAIN:-"demo.companyname.com"}
BASE_URL="http://$DOMAIN"

echo ""
echo "🌐 Testing endpoints on $BASE_URL"
echo ""

# Test basic endpoints
test_endpoint "$BASE_URL/intelligent-triage/" "Frontend application" 200
test_endpoint "$BASE_URL/intelligent-triage" "Frontend redirect" 301
test_endpoint "$BASE_URL/" "Root redirect" 301

# Test API endpoints
test_api_endpoint "$BASE_URL/intelligent-triage/docs" "API documentation"
test_api_endpoint "$BASE_URL/intelligent-triage/tts/health" "Backend health check"

# Test that double path doesn't work (should return 404 or redirect)
test_endpoint "$BASE_URL/intelligent-triage/intelligent-triage" "Double path (should fail)" 404

echo ""
echo "🔍 Testing Docker container connectivity..."

# Test internal Docker networking
if docker-compose exec frontend wget -q --spider http://backend:9001/tts/health 2>/dev/null; then
    echo -e "${GREEN}✅ Frontend can connect to backend${NC}"
else
    echo -e "${RED}❌ Frontend cannot connect to backend${NC}"
fi

echo ""
echo "📊 Summary:"
echo "==========="

# Count results
total_tests=6
passed_tests=0

# Re-run tests to count results
for test in "frontend" "redirect" "root" "docs" "health" "double_path"; do
    case $test in
        "frontend")
            if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/intelligent-triage/" | grep -q "200"; then
                ((passed_tests++))
            fi
            ;;
        "redirect")
            if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/intelligent-triage" | grep -q "301"; then
                ((passed_tests++))
            fi
            ;;
        "root")
            if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/" | grep -q "301"; then
                ((passed_tests++))
            fi
            ;;
        "docs")
            if curl -s "$BASE_URL/intelligent-triage/docs" | grep -q "FastAPI"; then
                ((passed_tests++))
            fi
            ;;
        "health")
            if curl -s "$BASE_URL/intelligent-triage/tts/health" | grep -q "OK"; then
                ((passed_tests++))
            fi
            ;;
        "double_path")
            if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/intelligent-triage/intelligent-triage" | grep -q "404"; then
                ((passed_tests++))
            fi
            ;;
    esac
done

echo "Tests passed: $passed_tests/$total_tests"

if [ $passed_tests -eq $total_tests ]; then
    echo -e "${GREEN}🎉 All tests passed! Deployment is working correctly.${NC}"
    echo ""
    echo "✅ Your application is accessible at: $BASE_URL/intelligent-triage/"
    echo "✅ API documentation at: $BASE_URL/intelligent-triage/docs"
    echo "✅ Backend health at: $BASE_URL/intelligent-triage/tts/health"
else
    echo -e "${RED}⚠️  Some tests failed. Please check the configuration.${NC}"
    echo ""
    echo "Common issues:"
    echo "1. Nginx configuration not properly set up"
    echo "2. Docker containers not running"
    echo "3. Domain name not resolving correctly"
    echo ""
    echo "Check logs with: ./deploy.sh logs"
fi

echo ""
echo "📝 Next steps:"
echo "1. Configure your nginx with the provided nginx.conf"
echo "2. Update your DNS to point demo.companyname.com to your server"
echo "3. Test the application manually in a browser"