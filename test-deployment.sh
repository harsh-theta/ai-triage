#!/bin/bash

# Test script to verify both deployment modes
echo "🧪 Testing Deployment Modes"
echo "=========================="

test_endpoint() {
    local url=$1
    local description=$2
    echo -n "Testing $description... "
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|404"; then
        echo "✅ Accessible"
    else
        echo "❌ Failed"
    fi
}

echo ""
echo "🔍 Current Docker status:"
docker-compose ps

echo ""
echo "📡 Testing endpoints..."

# Test based on current deployment
if docker-compose ps | grep -q "Up"; then
    # Check if we're in proxy mode by looking at environment variables
    if docker-compose exec -T frontend printenv NEXT_PUBLIC_BASE_PATH | grep -q "/intelligent-triage"; then
        echo "🌐 Detected PROXY mode deployment"
        echo ""
        echo "Note: These tests assume you're accessing via proxy (demo.company.com/intelligent-triage/)"
        echo "For local testing, you can test direct endpoints:"
        test_endpoint "http://localhost:8010" "Frontend (direct)"
        test_endpoint "http://localhost:9001/docs" "Backend API docs (direct)"
        test_endpoint "http://localhost:9001/triage/text" "Backend API endpoint (direct)"
    else
        echo "🔗 Detected DIRECT mode deployment"
        test_endpoint "http://localhost:8010" "Frontend"
        test_endpoint "http://localhost:9001/docs" "Backend API docs"
        test_endpoint "http://localhost:9001/triage/text" "Backend API endpoint"
    fi
else
    echo "❌ No services are running. Please deploy first:"
    echo "   ./deploy.sh proxy   # for proxy mode"
    echo "   ./deploy.sh direct  # for direct mode"
fi

echo ""
echo "💡 Useful commands:"
echo "   ./deploy.sh logs    # View logs"
echo "   ./deploy.sh status  # Check status"
echo "   ./deploy.sh stop    # Stop services"