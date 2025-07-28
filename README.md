# AI Triage System

An intelligent, protocol-guided patient triage system with emergency detection capabilities. This proof-of-concept uses conversational AI to guide patients through triage protocols, automatically detect emergencies, and generate structured data for Electronic Medical Records (EMR).

The system demonstrates a full-stack application with a React-based frontend and a Python/FastAPI backend powered by LangGraph and the Google Gemini API.

## Key Features

- **Conversational Triage**: Engages users in a natural conversation to understand their symptoms.
- **Protocol-Guided Logic**: Follows specific medical protocols (e.g., for headaches) based on the user's complaint.
- **Emergency Detection**: Identifies critical symptoms and immediately flags the situation as an emergency.
- **Structured Data Capture**: Generates a structured JSON object in real-time, suitable for EMR integration.
- **In-Memory State**: Manages conversation state per-session without requiring a database.

## Project Structure

```
ai-triage-system/
├── backend/                 # FastAPI backend
│   ├── venv/               # Python virtual environment
│   ├── main.py             # FastAPI application entry point
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
├── frontend/               # React + TypeScript frontend
│   ├── src/                # Source code
│   ├── package.json        # Node.js dependencies
│   └── .env.example        # Environment variables template
├── nginx.conf              # Nginx reverse proxy configuration
├── deploy.sh               # Deployment script
├── test-deployment.sh      # Deployment testing script
└── README.md               # This file
```

## Quick Start (Docker)

The easiest way to run the application is using Docker Compose:

```bash
# Deploy the application (configured for demo.company.com/intelligent-triage/)
./deploy.sh

# Stop all services
./deploy.sh stop

# View logs
./deploy.sh logs

# Check status
./deploy.sh status

# Test deployment
./test-deployment.sh
```

## Deployment Configuration

This application is configured for **proxy deployment only** with the base path `/intelligent-triage/`.

- **Access URL**: `demo.company.com/intelligent-triage/`
- **Backend API**: `demo.company.com/intelligent-triage/`
- **API Documentation**: `demo.company.com/intelligent-triage/docs`

### Recent Fixes (v1.1)

**Fixed Issues:**
1. **Docker Networking**: Frontend now correctly connects to backend using `http://backend:9001`
2. **URL Routing**: Fixed nginx configuration to properly handle `/intelligent-triage/` paths
3. **CORS Issues**: Added proper CORS headers and relative URL handling for production
4. **Double Path Issue**: Resolved the `/intelligent-triage/intelligent-triage` routing problem

**New Files:**
- `nginx.conf`: Complete nginx reverse proxy configuration
- `test-deployment.sh`: Comprehensive deployment testing script

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions and reverse proxy configuration.

## Development Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

5. Add your Google API key to the `.env` file

6. Run the development server:
   ```bash
   python main.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **LangGraph**: State machine for conversation flow
- **Google Gemini**: Large language model for AI responses
- **Pydantic**: Data validation and serialization

### Frontend
- **Next.js**: React framework with server-side rendering
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Modern UI component library

## Troubleshooting

### Common Deployment Issues

1. **404 on `/intelligent-triage`**: Use the provided `nginx.conf` file
2. **Double path working**: This indicates incorrect nginx configuration
3. **Backend connection errors**: Ensure `NEXT_PUBLIC_BACKEND_URL=http://backend:9001` in docker-compose.yml
4. **CORS errors**: The nginx configuration includes proper CORS headers

### Testing Deployment

Run the test script to verify everything is working:

```bash
./test-deployment.sh
```

This will test all endpoints and provide a detailed report of any issues.

## Security Considerations

- **No Persistent Storage**: All data is stored in memory only
- **Session Isolation**: Each conversation session is isolated
- **Input Validation**: All inputs are validated using Pydantic models
- **CORS Configuration**: Properly configured for production deployment