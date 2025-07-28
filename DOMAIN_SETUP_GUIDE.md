# 🚀 Domain Setup Guide for AI Triage System

## 📋 **What We're Setting Up**

- **Public URL**: `http://demo.thetatechnolabs.com/intelligent-triage/`
- **Actual Server**: `http://106.201.228.100:8010/intelligent-triage/`
- **Setup**: nginx reverse proxy on your domain server

## 🎯 **Architecture**

```
┌─────────────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ demo.thetatechnolabs.com│───▶│ nginx (port 80) │───▶│ 106.201.228.100 │
│ /intelligent-triage/    │    │ (reverse proxy) │    │ :8010           │
└─────────────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📝 **Step-by-Step Setup**

### 1. **Deploy Your Application First**

On your Ubuntu server (`106.201.228.100`):

```bash
# Clone your repository
git clone <your-repo-url>
cd ai-triage

# Deploy the application
./deploy.sh

# Test that it's working
curl http://localhost:8010/intelligent-triage/
```

### 2. **Set Up nginx on Your Domain Server**

On the server where `demo.thetatechnolabs.com` is hosted:

```bash
# Install nginx (if not already installed)
sudo apt update
sudo apt install nginx

# Backup existing config
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# Copy the new configuration
sudo cp server-nginx.conf /etc/nginx/nginx.conf

# Test the configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx

# Check status
sudo systemctl status nginx
```

### 3. **Configure DNS**

Make sure `demo.thetatechnolabs.com` points to the server where you installed nginx.

### 4. **Test the Setup**

```bash
# Test the proxy
curl http://demo.thetatechnolabs.com/intelligent-triage/

# Test API
curl -X POST http://demo.thetatechnolabs.com/intelligent-triage/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "session_id": "test123"}'
```

## 🔧 **Configuration Details**

### **nginx Configuration (`server-nginx.conf`)**

The configuration:
- Listens on port 80 for `demo.thetatechnolabs.com`
- Proxies all `/intelligent-triage/` requests to `http://106.201.228.100:8010/intelligent-triage/`
- Handles CORS headers for API requests
- Includes security headers
- Provides health checks

### **Key Features**

- ✅ **Reverse Proxy**: Routes requests from domain to your server
- ✅ **CORS Support**: Handles cross-origin requests
- ✅ **Security Headers**: Protects against common attacks
- ✅ **Health Checks**: `/health` endpoint for monitoring
- ✅ **Error Handling**: Proper 404 and 50x error pages
- ✅ **Performance**: Gzip compression and caching

## 🧪 **Testing Commands**

```bash
# Test frontend
curl -I http://demo.thetatechnolabs.com/intelligent-triage/

# Test API
curl -X POST http://demo.thetatechnolabs.com/intelligent-triage/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "session_id": "test123"}'

# Test health
curl http://demo.thetatechnolabs.com/health

# Test root redirect
curl -I http://demo.thetatechnolabs.com/
```

## 🔍 **Troubleshooting**

### **If nginx won't start:**

```bash
# Check configuration
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log

# Check if port 80 is in use
sudo netstat -tlnp | grep :80
```

### **If proxy isn't working:**

```bash
# Check if your app is running
curl http://106.201.228.100:8010/intelligent-triage/

# Check nginx logs
sudo tail -f /var/log/nginx/ai_triage_error.log

# Test connectivity
telnet 106.201.228.100 8010
```

### **If DNS isn't working:**

```bash
# Check DNS resolution
nslookup demo.thetatechnolabs.com

# Check if domain points to correct server
dig demo.thetatechnolabs.com
```

## 🎉 **Final Result**

Once everything is set up, your application will be accessible at:

**`http://demo.thetatechnolabs.com/intelligent-triage/`**

And all requests will be properly proxied to your server at `106.201.228.100:8010`.

## 📞 **Support**

If you encounter any issues:

1. Check nginx logs: `sudo tail -f /var/log/nginx/ai_triage_error.log`
2. Check your app logs: `docker-compose logs`
3. Test connectivity between servers
4. Verify DNS configuration

---

**This setup follows the same pattern as your senior's project and should work seamlessly!** 🚀 