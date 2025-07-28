# Deployment Guide

This application supports two deployment modes:

## 1. Direct Access (IP:PORT)
For development or direct server access via IP address and port.

### Usage:
```bash
./deploy-local.sh
```

### Access:
- Frontend: `http://localhost:8010` or `http://YOUR_IP:8010`
- Backend API: `http://localhost:9001` or `http://YOUR_IP:9001`

## 2. Proxy Access (Subpath)
For deployment behind a reverse proxy with a base path like `demo.company.com/intelligent-triage/`

### Usage:
```bash
./deploy-proxy.sh
```

### Access:
- Frontend: `demo.company.com/intelligent-triage/`
- Backend API: `demo.company.com/intelligent-triage/api/`

## Configuration Files

### `.env.local` - Direct Access
```
BASE_PATH=
ROOT_PATH=
```

### `.env.proxy` - Proxy Access
```
BASE_PATH=/intelligent-triage
ROOT_PATH=/intelligent-triage
```

## How It Works

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

## Switching Between Modes

You can easily switch between deployment modes:

1. Stop current deployment: `docker-compose down`
2. Run the desired deployment script: `./deploy-local.sh` or `./deploy-proxy.sh`

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