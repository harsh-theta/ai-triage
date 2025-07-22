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
└── README.md               # This file
```

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
- FastAPI - Web framework
- Python 3.12+ - Programming language
- Google Generative AI - AI/ML capabilities
- LangGraph - AI workflow orchestration
- Uvicorn - ASGI server

### Frontend
- React 18 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- Tailwind CSS - Styling
- Axios - HTTP client

## Environment Variables

### Backend (.env)
```
GOOGLE_API_KEY=your_google_api_key_here
HOST=localhost
PORT=8000
DEBUG=True
FRONTEND_URL=http://localhost:5173
```

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000
VITE_DEV_MODE=true
```