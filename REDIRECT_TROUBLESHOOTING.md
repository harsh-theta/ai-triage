# Redirect Loop Troubleshooting Guide

## Current Issue
You're still getting a redirect error on `https://demo.thetatechnolabs.com/intelligent-triage`.

## Simplified Approach
I've simplified the server nginx configuration to:
1. **Proxy API calls** directly to `localhost:9001` (backend)
2. **Proxy everything else** to `localhost:8010` (frontend container)
3. **Remove complex redirects** that might cause loops

## Debugging Steps

### 1. Check Current Nginx Configuration
```bash
# Check if the configuration is valid
sudo nginx -t

# Check which nginx configs are enabled
ls -la /etc/nginx/sites-enabled/

# Check if there are multiple configs for the same domain
grep -r "demo.thetatechnolabs.com" /etc/nginx/sites-available/
grep -r "demo.thetatechnolabs.com" /etc/nginx/sites-enabled/
```

### 2. Check Nginx Logs
```bash
# Check error logs for redirect issues
sudo tail -f /var/log/nginx/error.log

# Check access logs to see the redirect chain
sudo tail -f /var/log/nginx/access.log
```

### 3. Test with curl to see the redirect chain
```bash
# Test the domain and see what redirects happen
curl -I http://demo.thetatechnolabs.com/intelligent-triage
curl -I https://demo.thetatechnolabs.com/intelligent-triage

# Follow redirects to see the full chain
curl -L -I http://demo.thetatechnolabs.com/intelligent-triage
curl -L -I https://demo.thetatechnolabs.com/intelligent-triage
```

### 4. Check Docker Containers
```bash
# Make sure both containers are running
docker ps

# Check container logs
docker logs ai-triage-frontend-1
docker logs ai-triage-backend-1
```

### 5. Test Direct Access
```bash
# Test direct access to frontend container
curl -I http://localhost:8010/intelligent-triage

# Test direct access to backend
curl -I http://localhost:9001/docs
```

## Possible Issues

### Issue 1: Multiple Nginx Configurations
If you have multiple nginx configurations for the same domain, they might conflict.

**Solution:**
```bash
# Disable all other configs for this domain
sudo rm /etc/nginx/sites-enabled/default
sudo rm /etc/nginx/sites-enabled/other-config

# Only keep the intelligent-triage config
sudo ln -sf /etc/nginx/sites-available/intelligent-triage /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Issue 2: Frontend Nginx Redirecting
The frontend nginx might be redirecting, causing a loop.

**Solution:**
Check if the frontend nginx is redirecting by testing:
```bash
curl -I http://localhost:8010/intelligent-triage
```

If it redirects, we need to fix the frontend nginx configuration.

### Issue 3: HTTPS vs HTTP
If you're accessing via HTTPS but nginx is only configured for HTTP.

**Solution:**
Either:
1. Access via HTTP: `http://demo.thetatechnolabs.com/intelligent-triage`
2. Or configure HTTPS in nginx (requires SSL certificates)

### Issue 4: DNS Issues
The domain might not be pointing to your server.

**Solution:**
```bash
# Check if domain resolves to your server
nslookup demo.thetatechnolabs.com
dig demo.thetatechnolabs.com
```

## Quick Fix Test

Try this minimal nginx configuration to test:

```nginx
server {
    listen 80;
    server_name demo.thetatechnolabs.com;
    
    # Proxy everything to frontend
    location / {
        proxy_pass http://localhost:8010;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Next Steps

1. **Run the debugging commands** above
2. **Share the output** of the curl commands and nginx logs
3. **Check if there are multiple nginx configs** for the same domain
4. **Test direct access** to the containers

This will help us identify exactly where the redirect loop is happening.
