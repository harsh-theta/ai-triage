# Deployment Guide

This application supports two deployment modes using Docker Compose, with **proxy mode as the default**.

## Quick Start

```bash
# Deploy in proxy mode (default)
./deploy.sh

# Or explicitly specify proxy mode
./deploy.sh proxy

# Deploy in direct access mode
./deploy.sh direct

# Stop all services
./deploy.sh stop

# View logs
./deploy.sh logs

# Check status
./deploy.sh status
```

## Deployment Modes

### 1. Proxy Access (Default)
For deployment behind a reverse proxy with base path `/intelligent-triage/`

**Usage:**
```bash
./deploy.sh proxy
# or simply
./deploy.sh
```

**Access:**
- Frontend: `demo.company.com/intelligent-triage/`
- Backend API: `demo.company.com/intelligent-triage/`
- API Docs: `demo.company.com/intelligent-triage/docs`

### 2. Direct Access (IP:PORT)
For development or direct server access via IP address and port.

**Usage:**
```bash
./deploy.sh direct
```

**Access:**
- Frontend: `http://localhost:8010` or `http://YOUR_IP:8010`
- Backend API: `http://localhost:9001` or `http://YOUR_IP:9001`
- API Docs: `http://localhost:9001/docs`

## Docker Compose Configuration

### Main Configuration (`docker-compose.yml`)
Default configuration with proxy mode enabled:
- `ROOT_PATH=/intelligent-triage` for backend
- `NEXT_PUBLIC_BASE_PATH=/intelligent-triage` for frontend

### Override Configuration (`docker-compose.direct.yml`)
Override for direct access mode:
- `ROOT_PATH=""` for backend (no base path)
- `NEXT_PUBLIC_BASE_PATH=""` for frontend (no base path)

## How It Works

### Docker Compose Strategy
- **Default**: `docker-compose up` runs in proxy mode
- **Direct Mode**: `docker-compose -f docker-compose.yml -f docker-compose.direct.yml up` overrides environment variables for direct access
- **Easy Switching**: Use deployment scripts to switch between modes

### Frontend (Next.js)
- Uses `basePath` and `assetPrefix` in `next.config.mjs` to handle subpath routing
- Environment variable `NEXT_PUBLIC_BASE_PATH` controls the base path
- API routes automatically prepend the root path when calling backend

### Backend (FastAPI)
- Uses `root_path` parameter in FastAPI constructor
- Environment variable `ROOT_PATH` controls the API base path
- All routes automatically work under the specified root path

## Reverse Proxy Configuration

If you're using nginx, your configuration should look like:

```nginx
location /intelligent-triage/ {
    proxy_pass http://your-server:8010/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /intelligent-triage/api/ {
    proxy_pass http://your-server:9001/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## Available Scripts

| Script | Description |
|--------|-------------|
| `./deploy.sh` | Deploy in proxy mode (default) |
| `./deploy.sh proxy` | Deploy in proxy mode explicitly |
| `./deploy.sh direct` | Deploy in direct access mode |
| `./deploy.sh stop` | Stop all services |
| `./deploy.sh logs` | View service logs |
| `./deploy.sh status` | Check service status |
| `./deploy-proxy.sh` | Direct proxy deployment script |
| `./deploy-local.sh` | Direct local deployment script |

## Switching Between Modes

You can easily switch between deployment modes:

```bash
# Switch to proxy mode
./deploy.sh proxy

# Switch to direct mode  
./deploy.sh direct

# Stop everything
./deploy.sh stop
```

## Troubleshooting

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