# Nginx Deployment Guide for AI Triage System

## Issues Fixed

1. **Incorrect proxy paths**: Frontend was being proxied to wrong paths
2. **Missing static asset handling**: Static files weren't being served correctly
3. **Backend API routing**: API routes weren't being caught properly
4. **CORS configuration**: Missing proper CORS headers

## Quick Fix Commands

### 1. Backup current configuration
```bash
sudo cp /etc/nginx/sites-available/intelligent-triage /etc/nginx/sites-available/intelligent-triage.backup
```

### 2. Update nginx configuration
```bash
# Copy the optimized configuration
sudo cp server-nginx-optimized.conf /etc/nginx/sites-available/intelligent-triage

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

### 3. Verify services are running
```bash
# Check if frontend container is running on port 8010
sudo netstat -tlnp | grep :8010

# Check if backend container is running on port 9001
sudo netstat -tlnp | grep :9001

# Check nginx status
sudo systemctl status nginx
```

### 4. Check logs for errors
```bash
# Check nginx error logs
sudo tail -f /var/log/nginx/intelligent_triage_error.log

# Check nginx access logs
sudo tail -f /var/log/nginx/intelligent_triage_access.log

# Check container logs
docker-compose logs frontend
docker-compose logs backend
```

## Configuration Details

### Key Changes Made:

1. **Frontend Proxy Path**: Changed from `http://localhost:8010/intelligent-triage/` to `http://localhost:8010/`
2. **Static Assets**: Added proper handling for `_next` directory and other static files
3. **API Routes**: Enhanced regex pattern to catch more API endpoints
4. **Caching**: Added proper cache headers for static assets
5. **Error Handling**: Improved error handling and logging

### Port Configuration:
- Frontend: `localhost:8010` (Docker container)
- Backend: `localhost:9001` (Docker container)
- TTS Service: `106.201.228.100:9003` (External service)

## Troubleshooting

### If frontend still doesn't load:

1. **Check if containers are running**:
   ```bash
   docker-compose ps
   ```

2. **Restart containers**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

3. **Check frontend build**:
   ```bash
   docker-compose logs frontend
   ```

4. **Test direct access**:
   ```bash
   curl http://localhost:8010/
   curl http://localhost:9001/docs
   ```

### If API calls fail:

1. **Check backend logs**:
   ```bash
   docker-compose logs backend
   ```

2. **Test API directly**:
   ```bash
   curl http://localhost:9001/docs
   ```

3. **Check CORS headers**:
   ```bash
   curl -H "Origin: https://demo.thetatechnolabs.com" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: X-Requested-With" -X OPTIONS http://localhost:9001/chat
   ```

## Testing the Fix

1. **Access the application**: `https://demo.thetatechnolabs.com/intelligent-triage/`
2. **Check browser console** for any JavaScript errors
3. **Test API calls** by using the chat interface
4. **Check network tab** to ensure static assets are loading

## Rollback (if needed)

```bash
# Restore backup configuration
sudo cp /etc/nginx/sites-available/intelligent-triage.backup /etc/nginx/sites-available/intelligent-triage
sudo nginx -t
sudo systemctl reload nginx
```
