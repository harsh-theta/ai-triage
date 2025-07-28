# nginx-based AI Triage Deployment

This guide explains the new nginx-based deployment approach that follows your senior's pattern.

## How It Works

### Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Your Domain   │───▶│   nginx (port 80) │───▶│  Backend (port 9001) │
│ demo.company.com│    │  (static files) │    │  (FastAPI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Static Frontend │
                       │ (built files)   │
                       └─────────────────┘
```

### Key Benefits
1. **Static File Serving**: nginx serves the frontend static files (faster than Node.js)
2. **API Proxying**: nginx proxies API requests to the backend container
3. **No CORS Issues**: Everything served from the same origin
4. **Better Performance**: nginx is optimized for serving static files
5. **Production Ready**: This is the standard approach for production deployments

## Files Changed

### 1. `frontend/Dockerfile`
- **Before**: Node.js server running on port 8010
- **After**: Multi-stage build that creates static files and serves them with nginx

### 2. `frontend/nginx.conf`
- **New**: Custom nginx configuration that:
  - Serves static files at `/intelligent-triage/`
  - Proxies API requests to backend
  - Handles CORS headers
  - Includes caching and compression

### 3. `frontend/next.config.mjs`
- **Added**: `output: 'export'` to generate static files
- **Added**: `distDir: 'out'` to specify output directory

### 4. `docker-compose.yml`
- **Changed**: Frontend now exposes port 80 (nginx) instead of 8010 (Node.js)
- **Removed**: Environment variables (not needed with nginx proxying)

### 5. `frontend/app/page.tsx`
- **Simplified**: Uses relative URLs for API calls
- **Removed**: Complex production detection logic

## Deployment Steps

### 1. Build and Deploy
```bash
# Deploy the application
./deploy.sh

# Test the deployment
./test-nginx-deployment.sh
```

### 2. Test Locally
```bash
# Test frontend
curl http://localhost:8010/intelligent-triage/

# Test API
curl -X POST http://localhost:8010/intelligent-triage/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "session_id": "test123"}'

# Test health
curl http://localhost:8010/intelligent-triage/tts/health
```

### 3. Test Your Domain
```bash
# Replace with your actual domain
curl http://demo.companyname.com:8010/intelligent-triage/
```

## Configuration Details

### nginx Configuration Features

1. **Static File Serving**:
   ```nginx
   location /intelligent-triage/ {
       alias /usr/share/nginx/html/;
       try_files $uri $uri/ /intelligent-triage/index.html;
   }
   ```

2. **API Proxying**:
   ```nginx
   location ~ ^/intelligent-triage/(chat|triage|tts|docs|openapi) {
       proxy_pass http://backend:9001/intelligent-triage/$1;
   }
   ```

3. **CORS Headers**:
   ```nginx
   add_header Access-Control-Allow-Origin *;
   add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
   ```

4. **Caching**:
   ```nginx
   location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

### Docker Configuration

1. **Multi-stage Build**:
   - Stage 1: Node.js build environment
   - Stage 2: nginx production environment

2. **Health Checks**:
   ```dockerfile
   HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
       CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1
   ```

## Troubleshooting

### Common Issues

1. **Build Fails**:
   ```bash
   # Check if Next.js static export is working
   cd frontend
   npm run build
   ls -la out/
   ```

2. **nginx Not Starting**:
   ```bash
   # Check nginx configuration
   docker-compose logs frontend
   ```

3. **API Calls Fail**:
   ```bash
   # Test backend directly
   curl http://localhost:9001/intelligent-triage/tts/health
   
   # Test through nginx
   curl http://localhost:8010/intelligent-triage/tts/health
   ```

4. **Static Files Not Loading**:
   ```bash
   # Check if files exist in container
   docker-compose exec frontend ls -la /usr/share/nginx/html/
   ```

### Debug Commands

```bash
# View container logs
docker-compose logs frontend
docker-compose logs backend

# Check container status
docker-compose ps

# Test nginx configuration
docker-compose exec frontend nginx -t

# Check file permissions
docker-compose exec frontend ls -la /usr/share/nginx/html/
```

## Production Considerations

### 1. Domain Configuration
- Point your domain to your server IP
- Configure your server to forward port 80 to 8010, or
- Use a reverse proxy (Apache/nginx) to forward requests

### 2. SSL/HTTPS
- Add SSL certificate to nginx configuration
- Update nginx.conf to listen on port 443
- Redirect HTTP to HTTPS

### 3. Monitoring
- Set up log monitoring for nginx access/error logs
- Monitor container health checks
- Set up alerts for container restarts

### 4. Scaling
- Use Docker Swarm or Kubernetes for multiple instances
- Set up load balancing for high traffic
- Consider CDN for static assets

## Migration from Previous Setup

If you're migrating from the previous Node.js-based setup:

1. **Backup your data** (if any)
2. **Stop existing containers**:
   ```bash
   docker-compose down
   ```
3. **Deploy new setup**:
   ```bash
   ./deploy.sh
   ```
4. **Test thoroughly**:
   ```bash
   ./test-nginx-deployment.sh
   ```

## Performance Benefits

1. **Faster Loading**: Static files served by nginx are faster than Node.js
2. **Better Caching**: nginx has better caching mechanisms
3. **Lower Memory Usage**: No Node.js runtime needed for serving files
4. **Better Compression**: nginx gzip compression is more efficient
5. **No CORS Issues**: Everything served from same origin

## Security Considerations

1. **File Permissions**: nginx runs as non-root user
2. **CORS Headers**: Properly configured for API requests
3. **Health Checks**: Regular health monitoring
4. **Logging**: Comprehensive access and error logging
5. **Rate Limiting**: Can be added to nginx configuration

This nginx-based approach is the industry standard for production deployments and should resolve all your previous issues with routing and CORS. 