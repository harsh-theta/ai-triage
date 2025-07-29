# Routing Fixes for AI Triage System

## Overview

This document outlines the routing fixes implemented to ensure the AI Triage system works correctly when accessed via `demo.thetatechnolabs.com/intelligent-triage`.

## Issues Fixed

### 1. Nginx Configuration Conflicts
**Problem**: The original nginx.conf had conflicting location blocks for `/intelligent-triage/` where both frontend and backend were trying to handle the same path.

**Solution**: 
- Separated API routing from frontend routing
- API calls (`/intelligent-triage/chat`, `/intelligent-triage/triage`, etc.) are routed to backend
- All other `/intelligent-triage/` requests are routed to frontend

### 2. Missing Redirect Logic
**Problem**: No redirects from `/intelligent-triage` to `/intelligent-triage/` or from `/intelligent-triage/backend` to `/intelligent-triage/`

**Solution**: Added explicit redirect rules:
```nginx
# Redirect /intelligent-triage to /intelligent-triage/
location = /intelligent-triage {
    return 301 /intelligent-triage/;
}

# Redirect /intelligent-triage/backend to /intelligent-triage/
location = /intelligent-triage/backend {
    return 301 /intelligent-triage/;
}
```

### 3. Backend API Routing
**Problem**: Backend was configured with `ROOT_PATH=/intelligent-triage` but nginx wasn't properly routing API calls

**Solution**: Fixed API proxy configuration to correctly route API calls to backend:
```nginx
location ~ ^/intelligent-triage/(chat|triage|tts|docs|openapi) {
    proxy_pass http://localhost:9001/;
    # ... other proxy settings
}
```

## Configuration Files Updated

### 1. Root nginx.conf
- Fixed conflicting location blocks
- Added redirect rules
- Proper API routing

### 2. Frontend nginx.conf
- Fixed API proxy configuration
- Added redirect rules
- Proper static file serving

### 3. Frontend next.config.mjs
- Enhanced webpack configuration for base path handling
- Added experimental app directory support

## URL Structure

### Working URLs
- `demo.thetatechnolabs.com/` → Redirects to `/intelligent-triage/`
- `demo.thetatechnolabs.com/intelligent-triage` → Redirects to `/intelligent-triage/`
- `demo.thetatechnolabs.com/intelligent-triage/` → Frontend application
- `demo.thetatechnolabs.com/intelligent-triage/backend` → Redirects to `/intelligent-triage/`
- `demo.thetatechnolabs.com/intelligent-triage/chat` → Backend API
- `demo.thetatechnolabs.com/intelligent-triage/triage` → Backend API
- `demo.thetatechnolabs.com/intelligent-triage/tts` → Backend API
- `demo.thetatechnolabs.com/intelligent-triage/docs` → Backend API docs

### API Endpoints
- `POST /intelligent-triage/chat` - Chat endpoint
- `POST /intelligent-triage/chat/tts` - Chat with TTS
- `POST /intelligent-triage/triage/text` - Text triage
- `POST /intelligent-triage/tts` - Text-to-speech
- `GET /intelligent-triage/docs` - API documentation

## Testing

Run the routing test to verify all fixes work:
```bash
python test_routing_fixes.py
```

This test checks:
1. Root redirect to `/intelligent-triage/`
2. `/intelligent-triage` redirect to `/intelligent-triage/`
3. `/intelligent-triage/backend` redirect to `/intelligent-triage/`
4. Frontend accessibility at `/intelligent-triage/`
5. Backend API accessibility via proxy
6. Chat API functionality
7. TTS API functionality
8. Health check endpoint

## Deployment

### Local Development
```bash
# Start services
docker-compose up -d

# Test routing
python test_routing_fixes.py
```

### Production Deployment
1. Update nginx configuration on server
2. Restart nginx service
3. Rebuild and restart Docker containers
4. Test all endpoints

## Troubleshooting

### Common Issues

1. **Frontend not loading**: Check if nginx is properly serving static files at `/intelligent-triage/`
2. **API calls failing**: Verify backend is running and nginx is correctly proxying API requests
3. **Redirects not working**: Ensure nginx configuration is reloaded after changes
4. **Static assets not loading**: Check if Next.js basePath configuration is correct

### Debug Commands
```bash
# Check nginx configuration
nginx -t

# Check container logs
docker-compose logs frontend
docker-compose logs backend

# Test specific endpoints
curl -I http://localhost/intelligent-triage/
curl -I http://localhost/intelligent-triage/docs
```

## Security Considerations

- CORS headers are properly configured for API endpoints
- Health check endpoint is available for monitoring
- Proper error handling for unknown routes
- Secure proxy headers are set

## Performance Optimizations

- Static assets are cached with appropriate headers
- Gzip compression is enabled
- API responses include proper caching headers
- Frontend assets are optimized for production

## Future Improvements

1. Add rate limiting for API endpoints
2. Implement proper authentication
3. Add monitoring and logging
4. Optimize static asset delivery
5. Add CDN support for static assets 