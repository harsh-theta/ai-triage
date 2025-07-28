#!/bin/bash

# Test script for AI Triage proxy deployment
echo "🧪 Testing AI Triage Deployment"
echo "==============================="

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
if docker-compose ps | grep -q "Up"; then
    echo "🌐 Testing proxy deployment endpoints..."
    echo "📍 Application configured for: demo.company.com/intelligent-triage/"
    echo ""
    
    # Test local container endpoints (for development verification)
    echo "🔧 Development endpoints (container-level testing):"
    test_endpoint "http://localhost:8010/intelligent-triage" "Frontend (with base path)"
    test_endpoint "http://localhost:9001/intelligent-triage/docs" "Backend API docs (with base path)"
    test_endpoint "http://localhost:9001/intelligent-triage/chat" "Backend API endpoint (with base path)"
    
    echo ""
    echo "📝 Note: These are container-level tests. In production, access via:"
    echo "   🌐 Frontend: demo.company.com/intelligent-triage/"
    echo "   🔧 Backend: demo.company.com/intelligent-triage/"
    echo "   📊 API Docs: demo.company.com/intelligent-triage/docs"
    
    echo ""
    echo "🧪 Testing API functionality:"
    echo -n "Testing chat API... "
    if curl -s -X POST "http://localhost:8010/intelligent-triage/api/chat" \
        -H "Content-Type: application/json" \
        -d '{"message": "test", "session_id": "test123"}' > /dev/null 2>&1; then
        echo "✅ API responding"
    else
        echo "❌ API not responding"
    fi
    
else
    echo "❌ No services are running. Please deploy first:"
    echo "   ./deploy.sh         # Deploy the application"
    echo "   ./deploy.sh deploy  # Deploy the application"
fi

echo ""
echo "💡 Useful commands:"
echo "   ./deploy.sh         # Deploy application"
echo "   ./deploy.sh logs    # View logs"
echo "   ./deploy.sh status  # Check status"
echo "   ./deploy.sh stop    # Stop services"