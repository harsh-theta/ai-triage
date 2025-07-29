# Server Deployment Fix Guide

## 🔍 **Issues Identified**

1. **Port 8010 is working correctly** ✅
   - `http://106.201.228.100:8010/intelligent-triage/` returns 200 OK
   - Your application is running properly on the server

2. **Domain has redirect loop** ❌
   - `demo.thetatechnolabs.com/intelligent-triage/` has "Exceeded 30 redirects"
   - The domain is serving a different application (Theta Technolabs showcase)

3. **Domain configuration conflict** ⚠️
   - The domain is configured to serve another application
   - There's a conflict between the existing app and your AI Triage app

## 🚀 **Quick Solution (Recommended)**

**Use the direct IP with port for now:**
```
http://106.201.228.100:8010/intelligent-triage/
```

This URL works perfectly and gives you immediate access to your application.

## 🔧 **Permanent Fix Options**

### **Option 1: Update Server Nginx Configuration**

1. **SSH into your server**
2. **Backup current nginx config:**
   ```bash
   sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup
   ```

3. **Create new nginx configuration:**
   ```bash
   sudo nano /etc/nginx/sites-available/intelligent-triage
   ```
   
4. **Copy the configuration from `server-nginx-intelligent-triage.conf`**

5. **Enable the new configuration:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/intelligent-triage /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### **Option 2: Use a Subdomain**

1. **Create a subdomain** like `ai-triage.thetatechnolabs.com`
2. **Point it to your server IP**
3. **Configure nginx for the subdomain**

### **Option 3: Use a Different Port**

1. **Expose your application on a different port** (e.g., 8080)
2. **Configure nginx to proxy to that port**

## 🛠️ **Debugging Steps**

### **Run the server debug script:**
```bash
# On your server
chmod +x server_debug.sh
./server_debug.sh
```

### **Check current nginx configuration:**
```bash
sudo nginx -t
sudo cat /etc/nginx/sites-enabled/*
```

### **Check Docker containers:**
```bash
docker ps
docker-compose logs
```

### **Test the working URL:**
```bash
curl -I http://localhost:8010/intelligent-triage/
```

## 📋 **Immediate Actions**

1. **✅ Use the working URL**: `http://106.201.228.100:8010/intelligent-triage/`
2. **🔧 Run the debug script** to identify server issues
3. **📝 Check current nginx configuration** on the server
4. **🔄 Update nginx configuration** using the provided config file

## 🎯 **Expected Results**

After fixing the nginx configuration:
- `demo.thetatechnolabs.com/intelligent-triage/` should work
- No more redirect loops
- Your application should be accessible via the domain

## 🚨 **If Issues Persist**

1. **Check server logs:**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   docker-compose logs -f
   ```

2. **Verify Docker containers are running:**
   ```bash
   docker ps
   docker-compose ps
   ```

3. **Test internal connectivity:**
   ```bash
   curl -I http://localhost:8010/intelligent-triage/
   curl -I http://localhost:9001/docs
   ```

## 📞 **Support**

If you need help implementing these fixes, provide:
1. Output from `server_debug.sh`
2. Current nginx configuration
3. Docker container status
4. Any error messages from logs 