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

## How It Works

### Frontend (Next.js)
- Uses `basePath: '/intelligent-triage'` and `assetPrefix: '/intelligent-triage'` in `next.config.mjs`
- All static assets and routing work correctly under the `/intelligent-triage/` path
- API routes call backend with the correct base path

### Backend (FastAPI)
- Uses `root_path="/intelligent-triage"` parameter in FastAPI constructor
- Environment variable `ROOT_PATH=/intelligent-triage` controls the API base path
- All API endpoints automatically work under `/intelligent-triage/` path

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
| `./deploy.sh` | Deploy the application (default) |
| `./deploy.sh deploy` | Deploy the application explicitly |
| `./deploy.sh stop` | Stop all services |
| `./deploy.sh logs` | View service logs |
| `./deploy.sh status` | Check service status |
| `./deploy.sh restart` | Restart all services |
| `./test-deployment.sh` | Test deployment and endpoints |

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