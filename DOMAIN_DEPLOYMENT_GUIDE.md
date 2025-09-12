# Domain Deployment Guide

## Current Setup Understanding

You have a **two-tier nginx setup**:

1. **Main Server Nginx** (handles HTTPS and forwards to your app server)
   - `https://demo.thetatechnolabs.com/intelligent-triage` → `http://192.168.1.254:8010`

2. **App Server Nginx** (this server, handles the actual application)
   - `http://192.168.1.254:8010` → Frontend container
   - `http://192.168.1.254:8010/intelligent-triage/chat` → Backend container

## The Problem

The redirect loop was happening because:
- Main server forwards `/intelligent-triage` to your app server
- App server nginx was redirecting `/` to `/intelligent-triage`
- This created a loop: domain → app server → redirect → domain → repeat

## The Solution

I've updated the configurations to handle both access methods:

### 1. Frontend Nginx (`frontend/nginx.conf`)
- **Direct IP access** (`http://192.168.1.254:8010`): Redirects `/` to `/intelligent-triage`
- **Domain access** (`https://demo.thetatechnolabs.com/intelligent-triage`): Serves the app directly

### 2. Server Nginx (`server-nginx.conf`)
- **API calls** (`/intelligent-triage/chat`, etc.): Proxies to backend container
- **Everything else**: Proxies to frontend container

## Deployment Steps

### 1. Update Frontend Container
```bash
# Rebuild the frontend container with the updated nginx config
docker-compose down
docker-compose up -d --build frontend
```

### 2. Update Server Nginx (if needed)
If you need to update the server nginx configuration:
```bash
# Copy the updated server nginx config
sudo cp server-nginx.conf /etc/nginx/sites-available/intelligent-triage

# Test the configuration
sudo nginx -t

# If test passes, restart nginx
sudo systemctl restart nginx
```

## Expected Behavior

### ✅ Direct IP Access
- `http://192.168.1.254:8010` → Redirects to `/intelligent-triage`
- `http://192.168.1.254:8010/intelligent-triage` → Loads the app
- `http://192.168.1.254:8010/intelligent-triage/chat` → API works

### ✅ Domain Access
- `https://demo.thetatechnolabs.com/intelligent-triage` → Loads the app directly
- `https://demo.thetatechnolabs.com/intelligent-triage/chat` → API works
- No redirect loops

## Testing

### Test Direct Access
```bash
curl -I http://192.168.1.254:8010/intelligent-triage
# Should return 200 OK
```

### Test Domain Access
```bash
curl -I https://demo.thetatechnolabs.com/intelligent-triage
# Should return 200 OK (no redirects)
```

### Test API
```bash
curl -X POST https://demo.thetatechnolabs.com/intelligent-triage/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
# Should return 200 OK with JSON response
```

## Troubleshooting

If you still get redirect loops:

1. **Check nginx logs**:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

2. **Test the redirect chain**:
   ```bash
   curl -L -I https://demo.thetatechnolabs.com/intelligent-triage
   ```

3. **Verify containers are running**:
   ```bash
   docker ps
   ```

4. **Check if there are multiple nginx configs**:
   ```bash
   ls -la /etc/nginx/sites-enabled/
   ```

## Key Changes Made

1. **Frontend nginx**: Keeps the redirect for direct IP access but serves the app directly for domain access
2. **Server nginx**: Simple proxy setup that forwards everything to the frontend container
3. **No complex redirects**: Eliminated the redirect loop by simplifying the proxy chain

This setup should work for both access methods without breaking either one!
