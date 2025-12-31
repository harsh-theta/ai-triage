# Setup and Installation Guide

This guide provides step-by-step instructions for setting up the AI Triage System in both development and production environments.

## Prerequisites

### System Requirements
- **Operating System**: macOS, Linux, or Windows with WSL2
- **Docker**: Version 20.10+ with Docker Compose
- **Node.js**: Version 18+ (for development)
- **Python**: Version 3.9+ (for development)
- **Git**: For cloning the repository

### API Keys Required
- **Google Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Murf API Key**: Get from [Murf.ai](https://murf.ai/) (optional, for TTS features)

### Hardware Requirements
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: 2GB free space for Docker images
- **Network**: Internet connection for API calls

## Quick Start (Docker - Recommended)

### 1. Clone Repository
```bash
git clone <repository-url>
cd ai-triage-system
```

### 2. Environment Configuration
```bash
# Copy environment templates
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Edit backend environment
nano backend/.env
```

Add your API keys to `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MURF_API_KEY=your_murf_api_key_here
MODEL_NAME=gemini-2.5-flash
TTS_SERVICE_URL=http://106.201.228.100:9003
ROOT_PATH=/intelligent-triage
PROXY_DOMAIN=https://demo.thetatechnolabs.com
```

### 3. Start Services
```bash
# Start all services in background
docker-compose up -d

# View logs (optional)
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Verify Installation
- **Frontend**: http://localhost:8010
- **Backend API**: http://localhost:9001/docs (FastAPI documentation)
- **Health Check**: http://localhost:9001/tts/health

### 5. Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (full cleanup)
docker-compose down -v
```

## Development Setup

### Backend Development

#### 1. Python Environment Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

#### 2. Install Dependencies
```bash
# Install all requirements
pip install -r requirements.txt

# Verify installation
pip list
```

#### 3. Environment Configuration
```bash
# Copy and edit environment file
cp .env.example .env
nano .env
```

Required environment variables:
```env
GEMINI_API_KEY=your_gemini_api_key
MURF_API_KEY=your_murf_api_key
MODEL_NAME=gemini-2.5-flash
TTS_SERVICE_URL=http://106.201.228.100:9003
ROOT_PATH=
PROXY_DOMAIN=http://localhost:3000
```

#### 4. Start Development Server
```bash
# Start FastAPI development server
python main.py

# Alternative with uvicorn directly
uvicorn main:app --reload --port 9001
```

The backend will be available at http://localhost:9001

### Frontend Development

#### 1. Node.js Setup
```bash
cd frontend

# Install dependencies
npm install

# Alternative with yarn
yarn install
```

#### 2. Environment Configuration
```bash
# Copy and edit environment file
cp .env.example .env.local
nano .env.local
```

Required environment variables:
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:9001
NEXT_PUBLIC_API_BASE_PATH=
```

#### 3. Start Development Server
```bash
# Start Next.js development server
npm run dev

# Alternative with yarn
yarn dev
```

The frontend will be available at http://localhost:3000

## Production Deployment

### Docker Compose Deployment

#### 1. Production Environment Setup
```bash
# Create production environment file
cp backend/.env.example backend/.env.production
```

Configure for production:
```env
GEMINI_API_KEY=your_production_gemini_key
MURF_API_KEY=your_production_murf_key
MODEL_NAME=gemini-2.5-flash
TTS_SERVICE_URL=http://106.201.228.100:9003
ROOT_PATH=/intelligent-triage
PROXY_DOMAIN=https://your-domain.com
```

#### 2. Build and Deploy
```bash
# Build production images
docker-compose -f docker-compose.yml build

# Start production services
docker-compose -f docker-compose.yml up -d

# Monitor logs
docker-compose logs -f
```

#### 3. Nginx Configuration
The system includes nginx configuration for reverse proxy deployment. Key settings:

```nginx
# Main proxy configuration
location /intelligent-triage/ {
    proxy_pass http://frontend:80/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# API proxy configuration
location /intelligent-triage/api/ {
    proxy_pass http://backend:9001/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### Manual Deployment

#### 1. Backend Deployment
```bash
cd backend

# Install production dependencies
pip install -r requirements.txt

# Start with gunicorn (production WSGI server)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:9001
```

#### 2. Frontend Deployment
```bash
cd frontend

# Build for production
npm run build

# Start production server
npm start

# Alternative: Export static files
npm run build && npm run export
```

## Configuration Details

### Backend Configuration Options

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | - | Yes |
| `MURF_API_KEY` | Murf TTS API key | - | No |
| `MODEL_NAME` | Gemini model name | gemini-2.5-flash | Yes |
| `TTS_SERVICE_URL` | TTS service endpoint | - | No |
| `ROOT_PATH` | API root path for proxy | "" | No |
| `PROXY_DOMAIN` | Frontend domain for CORS | - | No |

### Frontend Configuration Options

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL | http://localhost:9001 | Yes |
| `NEXT_PUBLIC_API_BASE_PATH` | API base path | "" | No |

### Docker Configuration

#### Port Mapping
- **Frontend**: 8010:80 (Nginx serving static files)
- **Backend**: 9001:9001 (FastAPI application)

#### Volume Mounts
- `./backend/responses:/app/responses` - Response storage
- `./backend/uploads:/app/uploads` - File uploads

## Common Setup Issues

### Issue: Docker Build Fails

**Symptoms**: Docker build errors or container startup failures

**Solutions**:
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check Docker daemon status
docker info
```

### Issue: API Key Authentication Errors

**Symptoms**: 401/403 errors from Gemini API

**Solutions**:
1. Verify API key is correct in `.env` file
2. Check API key permissions in Google Cloud Console
3. Ensure no extra spaces or quotes around API key
4. Test API key with curl:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://generativelanguage.googleapis.com/v1beta/models
```

### Issue: TTS Service Unavailable

**Symptoms**: Audio features not working, TTS health check fails

**Solutions**:
1. Check TTS service URL is accessible
2. Verify Murf API key is valid
3. Test without TTS (text-only mode)
4. Check network connectivity to TTS service

### Issue: CORS Errors in Development

**Symptoms**: Browser blocks API requests

**Solutions**:
1. Ensure backend CORS is configured for frontend URL
2. Check `PROXY_DOMAIN` environment variable
3. Use same protocol (http/https) for frontend and backend
4. Clear browser cache and cookies

### Issue: Port Conflicts

**Symptoms**: "Port already in use" errors

**Solutions**:
```bash
# Check what's using the port
lsof -i :9001
lsof -i :8010

# Kill processes using the ports
kill -9 <PID>

# Use different ports in docker-compose.yml
```

## Verification Steps

### 1. Backend Health Check
```bash
# Test API endpoints
curl http://localhost:9001/docs
curl http://localhost:9001/tts/health

# Test triage endpoint
curl -X POST http://localhost:9001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a headache", "session_id": "test"}'
```

### 2. Frontend Verification
- Navigate to http://localhost:8010 (Docker) or http://localhost:3000 (dev)
- Verify chat interface loads
- Test sending a message
- Check EMR preview updates
- Test voice mode toggle (if TTS configured)

### 3. Integration Testing
- Start a triage conversation
- Verify AI responses appear
- Check EMR data populates in real-time
- Test emergency detection with keywords like "chest pain"
- Verify session persistence across page refreshes

## Performance Optimization

### Development Performance
```bash
# Backend: Use reload for faster development
uvicorn main:app --reload --port 9001

# Frontend: Enable fast refresh
npm run dev
```

### Production Performance
```bash
# Backend: Use multiple workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend: Enable static optimization
npm run build && npm run export
```

## Security Considerations

### API Key Security
- Never commit API keys to version control
- Use environment variables for all secrets
- Rotate API keys regularly
- Use different keys for development and production

### Network Security
- Use HTTPS in production
- Configure proper CORS origins
- Implement rate limiting for production
- Use secure headers in nginx configuration

This setup guide should get you running with the AI Triage System in any environment. For additional help, consult the other documentation files or check the troubleshooting section.