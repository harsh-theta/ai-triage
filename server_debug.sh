#!/bin/bash

echo "=== Server Debug Script for AI Triage ==="
echo "Run this script on your server to debug deployment issues"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Warning: This script should be run as root for full access"
    echo "   Some commands may fail without sudo"
    echo ""
fi

echo "🔍 1. Checking Docker containers..."
echo "----------------------------------------"
docker ps -a
echo ""

echo "🔍 2. Checking Docker container logs..."
echo "----------------------------------------"
echo "Frontend container logs:"
docker-compose logs --tail=20 frontend
echo ""

echo "Backend container logs:"
docker-compose logs --tail=20 backend
echo ""

echo "🔍 3. Checking if containers are accessible internally..."
echo "----------------------------------------"
echo "Testing frontend container on port 8010:"
curl -I http://localhost:8010/ 2>/dev/null || echo "❌ Frontend container not accessible"
echo ""

echo "Testing backend container on port 9001:"
curl -I http://localhost:9001/docs 2>/dev/null || echo "❌ Backend container not accessible"
echo ""

echo "🔍 4. Checking nginx configuration..."
echo "----------------------------------------"
echo "Testing nginx config syntax:"
nginx -t 2>&1 || echo "❌ Nginx configuration has errors"
echo ""

echo "🔍 5. Checking nginx status and logs..."
echo "----------------------------------------"
echo "Nginx status:"
systemctl status nginx --no-pager -l 2>/dev/null || echo "❌ Cannot check nginx status"
echo ""

echo "Recent nginx error logs:"
tail -10 /var/log/nginx/error.log 2>/dev/null || echo "❌ Cannot access nginx error logs"
echo ""

echo "🔍 6. Checking port availability..."
echo "----------------------------------------"
echo "Checking if port 8010 is listening:"
netstat -tlnp | grep :8010 2>/dev/null || echo "❌ Port 8010 not listening"
echo ""

echo "Checking if port 9001 is listening:"
netstat -tlnp | grep :9001 2>/dev/null || echo "❌ Port 9001 not listening"
echo ""

echo "🔍 7. Checking firewall status..."
echo "----------------------------------------"
echo "Checking UFW status:"
ufw status 2>/dev/null || echo "❌ UFW not available or not running"
echo ""

echo "🔍 8. Testing external connectivity..."
echo "----------------------------------------"
echo "Testing from server to localhost:8010:"
curl -I http://localhost:8010/intelligent-triage/ 2>/dev/null || echo "❌ Cannot access from server"
echo ""

echo "🔍 9. Checking DNS resolution..."
echo "----------------------------------------"
echo "Resolving demo.thetatechnolabs.com:"
nslookup demo.thetatechnolabs.com 2>/dev/null || echo "❌ Cannot resolve domain"
echo ""

echo "🔍 10. Checking server nginx configuration..."
echo "----------------------------------------"
echo "Server nginx sites-available:"
ls -la /etc/nginx/sites-available/ 2>/dev/null || echo "❌ Cannot access nginx sites"
echo ""

echo "Server nginx sites-enabled:"
ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "❌ Cannot access nginx sites"
echo ""

echo "=== Debug Summary ==="
echo "If you see ❌ errors above, those are the issues to fix."
echo ""
echo "Common fixes:"
echo "1. If containers not running: docker-compose up -d"
echo "2. If nginx config errors: Check /etc/nginx/sites-enabled/"
echo "3. If port not listening: Check if containers are running"
echo "4. If firewall blocking: ufw allow 8010, ufw allow 9001"
echo "5. If DNS issues: Check domain configuration"
echo ""
echo "After fixing issues, restart services:"
echo "docker-compose restart"
echo "sudo systemctl reload nginx" 