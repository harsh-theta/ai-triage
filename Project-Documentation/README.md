# AI Triage System

An intelligent, protocol-guided patient triage system that uses conversational AI to guide patients through symptom assessment, automatically detect emergencies, and generate structured Electronic Medical Records (EMR) data.

## Project Overview

This proof-of-concept demonstrates a full-stack web application that combines modern web technologies with AI to create an interactive medical triage experience. The system engages users in natural conversation to understand their symptoms, follows medical protocols, and captures structured data suitable for healthcare systems.

## Key Features

- **Conversational Triage**: Natural language interaction with AI-powered symptom assessment
- **Emergency Detection**: Automatic identification of critical symptoms requiring immediate attention
- **EMR Generation**: Real-time structured data capture for Electronic Medical Records
- **Multi-Modal Interface**: Text-based chat with optional text-to-speech audio
- **Session Management**: Stateful conversations with up to 12 interaction turns
- **Protocol-Guided Logic**: Follows specific medical protocols based on patient complaints

## Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Frontend** | Next.js (React + TypeScript) | 15.2.4 |
| **UI Framework** | Tailwind CSS + shadcn/ui | 3.4.17 |
| **Backend** | FastAPI (Python) | Latest |
| **AI Orchestration** | LangGraph | Latest |
| **LLM** | Google Gemini API | gemini-2.5-flash |
| **Text-to-Speech** | Murf API | Cloud Service |
| **Containerization** | Docker + Docker Compose | Latest |
| **Web Server** | Nginx (Alpine) | Latest |

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Google Gemini API key
- Murf API key (for TTS features)

### Environment Setup
1. Clone the repository
2. Copy environment files:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env.local
   ```
3. Add your API keys to `backend/.env`:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   MURF_API_KEY=your_murf_api_key
   MODEL_NAME=gemini-2.5-flash
   ```

### Running with Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The application will be available at:
- Frontend: http://localhost:8010
- Backend API: http://localhost:9001

### Development Mode
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Frontend (in new terminal)
cd frontend
npm install
npm run dev
```

## Project Structure

```
ai-triage-system/
├── backend/                    # FastAPI backend
│   ├── main.py                # API endpoints and server setup
│   ├── triage_agent.py        # Core triage conversation logic
│   ├── murf_client.py         # Text-to-speech integration
│   ├── prompts.py             # LLM prompts and templates
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Backend container config
│   └── .env                  # Environment variables
├── frontend/                  # Next.js frontend
│   ├── app/                  # Next.js app directory
│   │   ├── page.tsx          # Main triage interface
│   │   └── layout.tsx        # Root layout
│   ├── components/           # React components
│   │   ├── chat-interface.tsx
│   │   ├── emr-preview.tsx
│   │   └── emergency-alert.tsx
│   ├── lib/                  # Utilities and helpers
│   ├── package.json          # Node.js dependencies
│   ├── Dockerfile           # Frontend container config
│   └── .env.local           # Environment variables
├── docs/                     # Original project documentation
├── Project-Documentation/    # Generated comprehensive docs
├── docker-compose.yml       # Multi-container orchestration
├── nginx.conf              # Reverse proxy configuration
└── README.md              # This file
```

## Core Workflows

1. **Patient Triage Session**
   - User starts conversation with chief complaint
   - AI asks follow-up questions (up to 12 turns)
   - System extracts EMR data progressively
   - Emergency detection runs continuously
   - Final medical summary generated

2. **Emergency Detection**
   - AI analyzes symptoms for critical conditions
   - Immediate alert displayed if emergency detected
   - Session locked to prevent further interaction
   - Recommendation to seek immediate medical attention

3. **EMR Data Capture**
   - Structured data extracted in real-time
   - Fields include: chief complaint, duration, severity, location
   - JSON format suitable for healthcare system integration
   - Medical summary generated at session completion

## Documentation Index

This documentation is organized into focused sections for easy navigation:

- **[Architecture](./Architecture.md)** - System design, components, and data flows
- **[Setup and Installation](./Setup-and-Installation.md)** - Detailed environment setup guide
- **[Usage and Workflows](./Usage-and-Workflows.md)** - How to use the system and core workflows
- **[API Documentation](./API-Documentation.md)** - Complete API reference with examples
- **[Data and Models](./Data-and-Models.md)** - Data structures, EMR fields, and schemas
- **[Deployment and Maintenance](./Deployment-and-Maintenance.md)** - Production deployment guide

## Getting Help

- Check the [Setup Guide](./Setup-and-Installation.md) for installation issues
- Review [API Documentation](./API-Documentation.md) for integration questions
- See [Usage Guide](./Usage-and-Workflows.md) for workflow explanations
- Consult [Architecture](./Architecture.md) for system design details

## License

This is a proof-of-concept project for demonstration purposes.