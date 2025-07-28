#!/bin/bash

# Domain Proxy Setup Script for AI Triage System
# This script sets up nginx reverse proxy on the domain server

set -e

echo "🚀 Setting up domain proxy for AI Triage System"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ This script must be run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${BLUE}1. Installing nginx...${NC}"

# Update package list
apt update

# Install nginx if not already installed
if ! command -v nginx &> /dev/null; then
    apt install -y nginx
    echo -e "${GREEN}✅ nginx installed${NC}"
else
    echo -e "${GREEN}✅ nginx already installed${NC}"
fi

echo -e "${BLUE}2. Backing up existing nginx configuration...${NC}"

# Backup existing config
if [ -f /etc/nginx/nginx.conf ]; then
    cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅ Existing configuration backed up${NC}"
else
    echo -e "${YELLOW}⚠️  No existing nginx configuration found${NC}"
fi

echo -e "${BLUE}3. Installing new nginx configuration...${NC}"

# Check if server-nginx.conf exists
if [ ! -f "server-nginx.conf" ]; then
    echo -e "${RED}❌ server-nginx.conf not found in current directory${NC}"
    echo -e "${YELLOW}Please make sure server-nginx.conf is in the same directory as this script${NC}"
    exit 1
fi

# Copy new configuration
cp server-nginx.conf /etc/nginx/nginx.conf
echo -e "${GREEN}✅ New configuration installed${NC}"

echo -e "${BLUE}4. Testing nginx configuration...${NC}"

# Test configuration
if nginx -t; then
    echo -e "${GREEN}✅ nginx configuration is valid${NC}"
else
    echo -e "${RED}❌ nginx configuration test failed${NC}"
    echo -e "${YELLOW}Restoring backup configuration...${NC}"
    cp /etc/nginx/nginx.conf.backup.* /etc/nginx/nginx.conf
    exit 1
fi

echo -e "${BLUE}5. Reloading nginx...${NC}"

# Reload nginx
if systemctl reload nginx; then
    echo -e "${GREEN}✅ nginx reloaded successfully${NC}"
else
    echo -e "${RED}❌ Failed to reload nginx${NC}"
    exit 1
fi

echo -e "${BLUE}6. Checking nginx status...${NC}"

# Check nginx status
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ nginx is running${NC}"
else
    echo -e "${RED}❌ nginx is not running${NC}"
    systemctl status nginx
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Domain proxy setup complete!${NC}"
echo ""
echo "✅ Your nginx reverse proxy is now configured to:"
echo "   - Listen on: demo.thetatechnolabs.com"
echo "   - Proxy to: http://106.201.228.100:8010/intelligent-triage/"
echo ""
echo "📋 Next steps:"
echo "1. Make sure your application is running on 106.201.228.100:8010"
echo "2. Test the proxy: curl http://demo.thetatechnolabs.com/intelligent-triage/"
echo "3. Test the API: curl -X POST http://demo.thetatechnolabs.com/intelligent-triage/chat"
echo ""
echo "🔧 Useful commands:"
echo "   - Check nginx status: systemctl status nginx"
echo "   - View logs: tail -f /var/log/nginx/ai_triage_error.log"
echo "   - Test config: nginx -t"
echo "   - Reload: systemctl reload nginx"
echo ""
echo "📞 If you encounter issues, check the logs and verify:"
echo "   - DNS points to this server"
echo "   - Application is running on 106.201.228.100:8010"
echo "   - Firewall allows connections" 