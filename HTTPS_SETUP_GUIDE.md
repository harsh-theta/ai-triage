# HTTPS Setup Guide for Domain Access

## Problem Identified ✅

Your Apache server forwards `https://demo.thetatechnolabs.com/intelligent-triage` to your app server, but the app server nginx only listens on port 80 (HTTP). This causes an "HTTPS not supported" error.

## Solution Required

The app server nginx needs to be configured to handle HTTPS traffic. You have two options:

### Option 1: Let's Encrypt SSL Certificate (Recommended)

This is the best option for production use.

#### Step 1: Install Certbot
```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# On CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

#### Step 2: Get SSL Certificate
```bash
# Get certificate for your domain
sudo certbot --nginx -d demo.thetatechnolabs.com

# This will automatically:
# 1. Get the certificate from Let's Encrypt
# 2. Update your nginx configuration
# 3. Set up automatic renewal
```

#### Step 3: Update Server Nginx Configuration
The `server-nginx.conf` file has been updated with the correct SSL configuration. You need to:

1. **Copy the updated configuration**:
   ```bash
   sudo cp server-nginx.conf /etc/nginx/sites-available/intelligent-triage
   ```

2. **Uncomment the Let's Encrypt lines** in the config:
   ```nginx
   ssl_certificate /etc/letsencrypt/live/demo.thetatechnolabs.com/fullchain.pem;
   ssl_certificate_key /etc/letsencrypt/live/demo.thetatechnolabs.com/privkey.pem;
   ```

3. **Test and restart nginx**:
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Option 2: Self-Signed Certificate (Quick Test)

For testing purposes only, not recommended for production.

#### Step 1: Generate Self-Signed Certificate
```bash
# Create SSL directory
sudo mkdir -p /etc/ssl/certs /etc/ssl/private

# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-selfsigned.key \
  -out /etc/ssl/certs/nginx-selfsigned.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=demo.thetatechnolabs.com"
```

#### Step 2: Update Server Nginx Configuration
1. **Copy the updated configuration**:
   ```bash
   sudo cp server-nginx.conf /etc/nginx/sites-available/intelligent-triage
   ```

2. **Uncomment the self-signed certificate lines**:
   ```nginx
   ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
   ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;
   ```

3. **Test and restart nginx**:
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## Current Configuration

The `server-nginx.conf` file now includes:

1. **HTTP to HTTPS redirect**:
   ```nginx
   server {
       listen 80;
       server_name demo.thetatechnolabs.com;
       return 301 https://$server_name$request_uri;
   }
   ```

2. **HTTPS server block**:
   ```nginx
   server {
       listen 443 ssl http2;
       server_name demo.thetatechnolabs.com;
       # SSL configuration and proxy rules
   }
   ```

3. **API proxy** (unchanged):
   ```nginx
   location ~ ^/intelligent-triage/(chat|triage|tts|docs|openapi) {
       proxy_pass http://localhost:9001;
       # ... proxy headers
   }
   ```

4. **Frontend proxy** (unchanged):
   ```nginx
   location / {
       proxy_pass http://localhost:8010;
       # ... proxy headers
   }
   ```

## Testing

After setting up SSL, test with:

```bash
# Test HTTPS connection
curl -I https://demo.thetatechnolabs.com/intelligent-triage

# Test API
curl -X POST https://demo.thetatechnolabs.com/intelligent-triage/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

## Expected Result

- ✅ **HTTP**: `http://demo.thetatechnolabs.com/intelligent-triage` → Redirects to HTTPS
- ✅ **HTTPS**: `https://demo.thetatechnolabs.com/intelligent-triage` → Works without errors
- ✅ **API**: Backend API works through HTTPS
- ✅ **Static Assets**: Logo, CSS, JS load correctly through HTTPS

## Troubleshooting

If you still get HTTPS errors:

1. **Check nginx logs**: `sudo tail -f /var/log/nginx/error.log`
2. **Verify SSL certificate**: `sudo nginx -t`
3. **Check port 443**: `sudo netstat -tlnp | grep :443`
4. **Test SSL handshake**: `openssl s_client -connect demo.thetatechnolabs.com:443`

## Important Notes

- **Let's Encrypt certificates expire every 90 days** but auto-renewal is set up
- **Self-signed certificates** will show browser warnings (click "Advanced" → "Proceed")
- **Firewall**: Ensure port 443 is open: `sudo ufw allow 443`
- **DNS**: Make sure `demo.thetatechnolabs.com` points to your server IP

The HTTPS setup is essential for the domain access to work properly! 🔒
