# Apache Redirect Loop Fix

## Problem Solved ✅

The redirect loop was caused by a mismatch between:
1. **Apache server** forwarding `https://demo.thetatechnolabs.com/intelligent-triage` → `http://192.168.1.254:8010/intelligent-triage`
2. **Next.js configuration** not having the correct `basePath` and `assetPrefix` settings
3. **Frontend nginx** not properly handling the base path for static assets

## Solution Applied

### 1. Updated Next.js Configuration (`frontend/next.config.mjs`)
```javascript
// Added basePath and assetPrefix for proper static asset handling
basePath: '/intelligent-triage',
assetPrefix: '/intelligent-triage',
```

### 2. Updated Frontend Nginx Configuration (`frontend/nginx.conf`)
```nginx
# Handle Next.js static assets with base path
location /intelligent-triage/_next/ {
    alias /usr/share/nginx/html/_next/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Handle other static assets with base path
location ~ ^/intelligent-triage/(.*\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot))$ {
    alias /usr/share/nginx/html/$1;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. Kept API Proxy Configuration
```nginx
# Handle API calls - proxy to backend
location ~ ^/intelligent-triage/(chat|triage|tts|docs|openapi) {
    proxy_pass http://backend:9001;
    # ... CORS headers and proxy settings
}
```

## Current Setup Flow

### ✅ Direct IP Access
1. `http://192.168.1.254:8010` → Redirects to `/intelligent-triage`
2. `http://192.168.1.254:8010/intelligent-triage` → Serves the app
3. `http://192.168.1.254:8010/intelligent-triage/chat` → API calls work

### ✅ Domain Access (Apache Forwarding)
1. `https://demo.thetatechnolabs.com/intelligent-triage` → Apache forwards to `http://192.168.1.254:8010/intelligent-triage`
2. Frontend nginx serves the app directly (no redirects)
3. Static assets load from `/intelligent-triage/_next/` and other paths
4. API calls work through `/intelligent-triage/chat`

## Testing Results

### ✅ Frontend Access
```bash
curl -I http://localhost:8010/intelligent-triage
# Returns: HTTP/1.1 200 OK
```

### ✅ API Access
```bash
curl -X POST http://localhost:8010/intelligent-triage/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
# Returns: Valid JSON response
```

## Key Changes Made

1. **Next.js Configuration**: Added `basePath` and `assetPrefix` to handle the `/intelligent-triage` path
2. **Frontend Nginx**: Updated static asset handling to work with the base path
3. **No Redirect Changes**: Kept the existing redirect logic for direct IP access
4. **API Proxy**: Maintained the existing API proxy configuration

## Expected Behavior

- ✅ **Direct IP**: `http://192.168.1.254:8010/intelligent-triage` works
- ✅ **Domain**: `https://demo.thetatechnolabs.com/intelligent-triage` works (no redirects)
- ✅ **API**: Both access methods support API calls
- ✅ **Static Assets**: CSS, JS, and other assets load correctly
- ✅ **No Redirect Loops**: Apache forwarding works without conflicts

## Deployment

The containers have been rebuilt and are running. The configuration should now work for both access methods without any redirect loops.

## Troubleshooting

If you still experience issues:

1. **Check Apache logs** for any forwarding issues
2. **Check nginx logs**: `docker logs ai-triage-frontend-1`
3. **Test direct access** first: `http://192.168.1.254:8010/intelligent-triage`
4. **Clear browser cache** to remove any cached redirects

The redirect loop issue should now be completely resolved! 🎉
