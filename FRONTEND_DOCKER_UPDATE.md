# Frontend Docker Configuration Update

## Overview
Updated the frontend Dockerfile to use an optimized nginx configuration that works seamlessly with the server-side nginx setup.

## Changes Made

### 1. Created `frontend/nginx-optimized.conf`
- **Simplified configuration**: Removed complex proxy rules since server nginx handles routing
- **Optimized static file serving**: Better handling of Next.js `_next` directory and static assets
- **Improved error handling**: Graceful handling of missing files
- **Enhanced caching**: Proper cache headers for static assets
- **SPA routing support**: Handles client-side routing correctly

### 2. Updated `frontend/Dockerfile`
- **Changed nginx config**: Now uses `nginx-optimized.conf` instead of `nginx.conf`
- **Added nginx cache directory**: Better performance with proper cache setup
- **Added health check**: Container health monitoring with wget
- **Improved permissions**: Better file ownership and permissions

### 3. Created `deploy-frontend.sh`
- **Automated deployment**: One-command deployment script
- **Health checks**: Verifies frontend is working correctly
- **Error handling**: Proper error reporting and troubleshooting
- **Status reporting**: Shows container status and logs

## Key Improvements

### Performance
- ✅ Better static asset caching (1 year for immutable assets)
- ✅ Optimized gzip compression
- ✅ Proper nginx cache directory setup
- ✅ Reduced configuration complexity

### Reliability
- ✅ Health check endpoint (`/health`)
- ✅ Graceful error handling for missing files
- ✅ Proper SPA routing support
- ✅ Better logging configuration

### Maintainability
- ✅ Simplified nginx configuration
- ✅ Clear separation of concerns (server nginx vs container nginx)
- ✅ Automated deployment script
- ✅ Better error reporting

## Architecture

```
Internet → Server Nginx → Frontend Container (Port 8010)
                    ↓
              Backend Container (Port 9001)
                    ↓
              TTS Service (External)
```

### Server Nginx Responsibilities:
- Handle `/intelligent-triage/` routing
- Proxy API calls to backend
- Proxy static files to frontend
- Handle CORS and security headers

### Frontend Container Nginx Responsibilities:
- Serve static Next.js files
- Handle SPA routing
- Optimize static asset delivery
- Provide health check endpoint

## Deployment Instructions

### 1. Deploy Frontend Container
```bash
# Run the deployment script
./deploy-frontend.sh
```

### 2. Update Server Nginx (if not done already)
```bash
# Copy optimized server configuration
sudo cp server-nginx-optimized.conf /etc/nginx/sites-available/intelligent-triage

# Test and reload
sudo nginx -t && sudo systemctl reload nginx
```

### 3. Verify Deployment
```bash
# Check container status
docker-compose ps

# Check frontend health
curl http://localhost:8010/health

# Check logs
docker-compose logs frontend
```

## Testing

### Local Testing
```bash
# Test frontend directly
curl http://localhost:8010/

# Test health endpoint
curl http://localhost:8010/health

# Test static assets
curl http://localhost:8010/_next/
```

### Full Application Testing
1. Access: `https://demo.thetatechnolabs.com/intelligent-triage/`
2. Check browser console for errors
3. Test API calls through the chat interface
4. Verify static assets load correctly

## Troubleshooting

### Frontend Not Loading
```bash
# Check container logs
docker-compose logs frontend

# Check if container is running
docker-compose ps frontend

# Restart container
docker-compose restart frontend
```

### Static Assets Not Loading
```bash
# Check nginx configuration
docker exec -it ai-triage-frontend-1 nginx -t

# Check file permissions
docker exec -it ai-triage-frontend-1 ls -la /usr/share/nginx/html/
```

### Health Check Failing
```bash
# Check nginx status inside container
docker exec -it ai-triage-frontend-1 nginx -s status

# Check if health endpoint exists
docker exec -it ai-triage-frontend-1 curl localhost/health
```

## Configuration Files

- `frontend/nginx-optimized.conf` - Optimized nginx config for frontend container
- `frontend/Dockerfile` - Updated Dockerfile with new nginx config
- `server-nginx-optimized.conf` - Server-side nginx configuration
- `deploy-frontend.sh` - Automated deployment script

## Benefits

1. **Better Performance**: Optimized static file serving and caching
2. **Improved Reliability**: Health checks and better error handling
3. **Easier Maintenance**: Simplified configuration and automated deployment
4. **Better Debugging**: Enhanced logging and status reporting
5. **Production Ready**: Proper nginx configuration for production use
