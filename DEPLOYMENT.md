# Deployment Guide

This application is configured for **proxy deployment only** with the base path `/intelligent-triage/`.

## Quick Start

```bash
# Deploy the application
./deploy.sh

# Stop all services
./deploy.sh stop

# View logs
./deploy.sh logs

# Check status
./deploy.sh status

# Restart services
./deploy.sh restart
```

## Proxy Access Configuration

The application is designed to work behind a reverse proxy with the base path `/intelligent-triage/`.

**Usage:**
```bash
./deploy.sh
# or
./deploy.sh deploy
```

**Access:**
- Frontend: `demo.company.com/intelligent-triage/`
- Backend API: `demo.company.com/intelligent-triage/`
- API Docs: `demo.company.com/intelligent-triage/docs`

## Docker Compose Configuration

### Main Configuration (`docker-compose.yml`)
Configured for proxy deployment with `/intelligent-triage/` base path:
- `ROOT_PATH=/intelligent-triage` for backend
- Frontend configured with hardcoded base path in `next.config.mjs`
- Backend URL set to `http://backend:9001` for Docker networking

## How It Works

### Frontend (Next.js)
- Uses `basePath: '/intelligent-triage'` and `assetPrefix: '/intelligent-triage'` in `next.config.mjs`
- All static assets and routing work correctly under the `/intelligent-triage/` path
- API routes call backend with the correct base path
- Uses relative URLs in production to avoid CORS issues

### Backend (FastAPI)
- Uses `root_path="/intelligent-triage"` parameter in FastAPI constructor
- Environment variable `ROOT_PATH=/intelligent-triage` controls the API base path
- All API endpoints automatically work under `/intelligent-triage/` path

## Reverse Proxy Configuration

### Nginx Configuration

Use the provided `nginx.conf` file or create your own with this configuration:

```nginx
server {
    listen 80;
    server_name demo.companyname.com;

    # Frontend - Next.js application
    location /intelligent-triage/ {
        # Only proxy API calls, not static assets
        location ~ ^/intelligent-triage/(chat|triage|tts|docs|openapi) {
            proxy_pass http://localhost:9001/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Prefix /intelligent-triage;
            
            # Handle CORS
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
            
            # Handle preflight requests
            if ($request_method = 'OPTIONS') {
                add_header Access-Control-Allow-Origin *;
                add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
                add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
                add_header Access-Control-Max-Age 1728000;
                add_header Content-Type 'text/plain; charset=utf-8';
                add_header Content-Length 0;
                return 204;
            }
        }
        
        # All other /intelligent-triage/ requests go to frontend
        proxy_pass http://localhost:8010/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Prefix /intelligent-triage;
        
        # Handle Next.js routing
        proxy_redirect off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Redirect root to intelligent-triage
    location = / {
        return 301 /intelligent-triage/;
    }

    # Health check endpoint
    location /health {
        return 200 "OK";
        add_header Content-Type text/plain;
    }
}
```

### Key Configuration Points

1. **API Routing**: The nginx configuration uses regex matching to route API calls (`/intelligent-triage/chat`, `/intelligent-triage/triage`, etc.) to the backend, while all other requests go to the frontend.

2. **CORS Handling**: Proper CORS headers are set for API requests to allow cross-origin requests.

3. **Next.js Headers**: The `X-Forwarded-Prefix` header is set to `/intelligent-triage` so Next.js knows about the base path.

## Available Scripts

| Script | Description |
|--------|-------------|
| `./deploy.sh` | Deploy the application (default) |
| `./deploy.sh deploy` | Deploy the application explicitly |
| `./deploy.sh stop` | Stop all services |
| `./deploy.sh logs` | View service logs |
| `./deploy.sh status` | Check service status |
| `./deploy.sh restart` | Restart all services |
| `./test-deployment.sh` | Test deployment and endpoints |

## Troubleshooting

### Common Issues

#### 1. 404 Errors on `/intelligent-triage`
**Problem**: The application returns 404 when accessing `demo.company.com/intelligent-triage`
**Solution**: Ensure your nginx configuration matches the one provided above. The key is the regex matching for API routes.

#### 2. Double Path Issues (`/intelligent-triage/intelligent-triage`)
**Problem**: The application works at `demo.company.com/intelligent-triage/intelligent-triage` but not at the correct path
**Solution**: This indicates incorrect nginx configuration. Use the provided nginx.conf file.

#### 3. Backend Connection Issues
**Problem**: Frontend can't connect to backend in Docker
**Solution**: 
- Ensure `NEXT_PUBLIC_BACKEND_URL=http://backend:9001` in docker-compose.yml
- Check that both containers are running: `docker-compose ps`
- Verify backend logs: `docker-compose logs backend`

#### 4. CORS Errors
**Problem**: Browser shows CORS errors when making API calls
**Solution**: 
- The nginx configuration includes proper CORS headers
- In production, the frontend uses relative URLs to avoid CORS issues
- Check that the nginx configuration is properly loaded

### Frontend Issues
- Check that `NEXT_PUBLIC_BASE_PATH` matches your proxy configuration
- Verify static assets are loading correctly
- Check browser developer tools for 404 errors on assets

### Backend Issues
- Ensure `ROOT_PATH` matches your proxy API path
- Check FastAPI docs at `/docs` endpoint (with base path if configured)
- Verify CORS settings allow requests from your domain

### Both Modes Not Working
- Ensure Docker containers are running: `docker-compose ps`
- Check logs: `docker-compose logs frontend` or `docker-compose logs backend`
- Verify environment variables are loaded correctly

## Testing the Deployment

After deployment, test these endpoints:

1. **Frontend**: `http://demo.companyname.com/intelligent-triage/`
2. **API Health**: `http://demo.companyname.com/intelligent-triage/docs`
3. **Backend Health**: `http://demo.companyname.com/intelligent-triage/tts/health`

All should return appropriate responses without 404 errors.