# Nginx Deployment Guide for AI Triage System

## Overview

This guide explains how to properly deploy the AI Triage System with nginx to achieve the following access patterns:

1. **Domain access**: `https://demo.thetatechnolabs.com/intelligent-triage`
2. **IP access**: `http://{server_IP}:8010` and `http://{server_IP}:8010/intelligent-triage`

## File Structure

After cleanup, you now have only 2 nginx configuration files:

1. **`frontend/nginx.conf`** - Configuration for the frontend container (handles serving the Next.js app at `/intelligent-triage`)
2. **`server-nginx.conf`** - Configuration for the server nginx (handles domain routing and API proxying)

## Deployment Steps

### 1. Start the Docker Containers

```bash
# Navigate to your project directory
cd /path/to/ai-triage

# Start the services
docker-compose up -d
```

This will start:
- Backend on port 9001
- Frontend on port 8010

### 2. Configure Server Nginx

#### Option A: Using the provided configuration file

```bash
# Copy the server nginx configuration
sudo cp server-nginx.conf /etc/nginx/sites-available/intelligent-triage

# Enable the site
sudo ln -s /etc/nginx/sites-available/intelligent-triage /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

#### Option B: Add to existing nginx configuration

If you already have nginx running with other sites, you can add the server block from `server-nginx.conf` to your existing nginx configuration.

### 3. Verify Access

After deployment, you should be able to access:

1. **Domain access**: `https://demo.thetatechnolabs.com/intelligent-triage`
2. **IP access**: `http://{your_server_ip}:8010/intelligent-triage`
3. **Direct IP access**: `http://{your_server_ip}:8010` (redirects to `/intelligent-triage`)

## How It Works

### Frontend Container (Port 8010)
- Serves the Next.js application at `/intelligent-triage/`
- Handles static assets with proper caching
- Redirects root `/` to `/intelligent-triage/`

### Server Nginx (Port 80)
- Listens for requests to `demo.thetatechnolabs.com`
- Proxies API requests (`/intelligent-triage/chat`, `/intelligent-triage/triage`, etc.) to backend on port 9001
- Proxies frontend requests to the frontend container on port 8010
- Handles CORS headers for API requests

### Direct IP Access (Port 8010)
- The frontend container is directly accessible on port 8010
- This provides direct access without going through the server nginx
- API calls from the frontend will still go to the backend on port 9001

## Troubleshooting

### Check if services are running
```bash
docker-compose ps
```

### Check nginx status
```bash
sudo systemctl status nginx
```

### Check nginx logs
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Test nginx configuration
```bash
sudo nginx -t
```

### Check if ports are accessible
```bash
# Check if frontend is accessible
curl http://localhost:8010/health

# Check if backend is accessible
curl http://localhost:9001/health
```

## Environment Variables

Make sure your backend `.env` file contains:
```
TTS_SERVICE_URL=http://106.201.228.100:9003
ROOT_PATH=/intelligent-triage
PROXY_DOMAIN=https://demo.thetatechnolabs.com
```

## Security Notes

- The current configuration allows CORS from any origin (`*`). For production, consider restricting this to specific domains.
- Consider adding SSL/TLS certificates for HTTPS access.
- The server nginx configuration includes basic security headers.

## File Cleanup

The following files were removed as they were redundant:
- `nginx.conf` (root level)
- `server-nginx.conf` (old version)
- `server-nginx-intelligent-triage.conf` (redundant)

Only `frontend/nginx.conf` and `server-nginx.conf` are now needed.