# Server Deployment Fix for Redirect Loop

## Problem
The domain `https://demo.thetatechnolabs.com/intelligent-triage` is showing "too many redirects" error because of conflicting redirect rules between server nginx and frontend nginx.

## Solution
Update the server nginx configuration to match the frontend nginx configuration.

## Steps to Fix

### 1. Update Server Nginx Configuration
Replace the content of `/etc/nginx/sites-available/intelligent-triage` with the updated configuration from `server-nginx.conf`:

```bash
# Copy the updated configuration
sudo cp server-nginx.conf /etc/nginx/sites-available/intelligent-triage

# Test the nginx configuration
sudo nginx -t

# If test passes, restart nginx
sudo systemctl restart nginx
```

### 2. Key Changes Made

1. **Removed trailing slash redirects** - No more redirect from `/intelligent-triage` to `/intelligent-triage/`
2. **Updated static asset handling** - Now proxies `/_next/` and other static assets directly to `localhost:8010`
3. **Fixed frontend proxy** - Now proxies `/intelligent-triage` to `localhost:8010/intelligent-triage` (without trailing slash)
4. **Updated root redirect** - Now redirects to `/intelligent-triage` (without trailing slash)

### 3. Verify the Fix

After updating the configuration, test these URLs:

- `https://demo.thetatechnolabs.com/` → Should redirect to `/intelligent-triage`
- `https://demo.thetatechnolabs.com/intelligent-triage` → Should load the frontend
- `https://demo.thetatechnolabs.com/intelligent-triage/chat` → Should work for API calls
- `https://demo.thetatechnolabs.com/_next/static/...` → Should load static assets

### 4. Check Nginx Logs

If there are still issues, check the nginx logs:

```bash
# Check error logs
sudo tail -f /var/log/nginx/error.log

# Check access logs
sudo tail -f /var/log/nginx/access.log
```

## Expected Behavior

- **Domain access**: `https://demo.thetatechnolabs.com/intelligent-triage` should work without redirects
- **IP access**: `http://192.168.1.254:8010/intelligent-triage` should continue working
- **API calls**: Backend API should work through the domain
- **Static assets**: CSS, JS, and other assets should load correctly

## Troubleshooting

If you still get redirect loops:

1. **Clear browser cache** - The browser might be caching the redirect
2. **Check for other nginx configs** - Make sure there are no other nginx configurations interfering
3. **Verify docker containers** - Ensure both frontend and backend containers are running
4. **Check nginx status** - `sudo systemctl status nginx`
