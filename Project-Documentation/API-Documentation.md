# API Documentation

This document provides comprehensive documentation for the AI Triage System REST API, including endpoints, request/response formats, and integration examples.

## Base Configuration

### API Base URL
- **Development**: `http://localhost:9001`
- **Production**: `https://your-domain.com/intelligent-triage`

### Authentication
Currently, no authentication is required for this proof-of-concept system.

### Content Type
All requests should use `Content-Type: application/json`

### CORS
The API supports cross-origin requests from all domains in the current configuration.

## Core Endpoints

### 1. Chat Conversation

#### POST /chat
Main endpoint for conversational triage interactions.

**Request Body:**
```json
{
  "message": "string",
  "session_id": "string (optional)"
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | Yes | User's message or symptom description |
| `session_id` | string | No | Session identifier (auto-generated if not provided) |

**Response:**
```json
{
  "ai_message": "string",
  "emr_data": {
    "chief_complaint": "string",
    "duration": "string",
    "severity": "string",
    "location": "string",
    "onset": "string",
    "associated_symptoms": ["string"],
    "triggers": "string",
    "relief_factors": "string",
    "emergency_flag": "boolean",
    "medical_summary": "string"
  },
  "status": "string",
  "session_id": "string"
}
```

**Status Values:**
- `active`: Conversation in progress
- `emergency_detected`: Critical symptoms identified
- `complete`: Triage session finished
- `error`: System error occurred

**Example Request:**
```bash
curl -X POST http://localhost:9001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have been experiencing severe chest pain for the last hour",
    "session_id": "session_123"
  }'
```

**Example Response:**
```json
{
  "ai_message": "I'm concerned about your chest pain. Can you describe the type of pain - is it sharp, crushing, burning, or pressure-like?",
  "emr_data": {
    "chief_complaint": "severe chest pain",
    "duration": "1 hour",
    "severity": null,
    "location": "chest",
    "onset": "1 hour ago",
    "associated_symptoms": [],
    "triggers": null,
    "relief_factors": null,
    "emergency_flag": true,
    "medical_summary": null
  },
  "status": "emergency_detected",
  "session_id": "session_123"
}
```

### 2. Chat with Text-to-Speech

#### POST /chat/tts
Same as `/chat` but includes audio response generation.

**Request Body:**
```json
{
  "message": "string",
  "session_id": "string (optional)",
  "voice": "string (optional, default: en-IN-priya)"
}
```

**Response:**
```json
{
  "ai_message": "string",
  "emr_data": { /* same as /chat */ },
  "status": "string",
  "session_id": "string",
  "audio_url": "string"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:9001/chat/tts \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My head hurts really bad",
    "session_id": "session_456",
    "voice": "en-IN-priya"
  }'
```

### 3. Single-Turn Triage

#### POST /triage/text
Performs single-turn triage without session management.

**Request Body:**
```json
{
  "user_input": "string"
}
```

**Response:**
```json
{
  "ai_message": "string",
  "emr_data": { /* EMR fields */ },
  "status": "string"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:9001/triage/text \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "I have a fever and sore throat"
  }'
```

### 4. Single-Turn Triage with TTS

#### POST /triage/text/tts
Single-turn triage with audio response.

**Request Body:**
```json
{
  "user_input": "string",
  "voice": "string (optional)"
}
```

**Response:**
```json
{
  "ai_message": "string",
  "emr_data": { /* EMR fields */ },
  "status": "string",
  "audio_url": "string"
}
```

### 5. Medical Summary

#### GET /triage/summary
Generates comprehensive medical summary for a session.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Session identifier |

**Response:**
```json
{
  "medical_summary": "string",
  "emr_data": { /* Complete EMR data */ },
  "session_id": "string"
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:9001/triage/summary?session_id=session_123"
```

**Example Response:**
```json
{
  "medical_summary": "Patient presents with acute onset severe chest pain lasting 1 hour. Pain is described as crushing and pressure-like, located in the center of the chest. Associated symptoms include shortness of breath and nausea. Given the acute nature and characteristics of the chest pain, this requires immediate emergency evaluation to rule out acute coronary syndrome.",
  "emr_data": {
    "chief_complaint": "severe chest pain",
    "duration": "1 hour",
    "severity": "9/10",
    "location": "center of chest",
    "onset": "acute",
    "associated_symptoms": ["shortness of breath", "nausea"],
    "triggers": "none identified",
    "relief_factors": "none",
    "emergency_flag": true,
    "medical_summary": "Acute chest pain requiring emergency evaluation"
  },
  "session_id": "session_123"
}
```

## Text-to-Speech Endpoints

### 6. Generate Audio

#### POST /tts
Converts text to speech audio.

**Request Body:**
```json
{
  "text": "string",
  "voice": "string (optional, default: en-IN-priya)"
}
```

**Response:**
```json
{
  "audio_url": "string",
  "text": "string",
  "voice": "string"
}
```

**Available Voices:**
- `en-IN-priya` (Indian English, Female)
- `en-US-sarah` (US English, Female)
- `en-GB-james` (British English, Male)

**Example Request:**
```bash
curl -X POST http://localhost:9001/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Please describe your symptoms in detail",
    "voice": "en-IN-priya"
  }'
```

### 7. TTS Health Check

#### GET /tts/health
Checks the health status of the text-to-speech service.

**Response:**
```json
{
  "status": "string",
  "service": "string",
  "timestamp": "string"
}
```

**Status Values:**
- `healthy`: TTS service is operational
- `unhealthy`: TTS service is unavailable
- `degraded`: TTS service has limited functionality

**Example Request:**
```bash
curl -X GET http://localhost:9001/tts/health
```

## Error Responses

### Standard Error Format
```json
{
  "detail": "string",
  "error_code": "string",
  "timestamp": "string"
}
```

### Common Error Codes

#### 400 Bad Request
```json
{
  "detail": "Invalid request format or missing required fields",
  "error_code": "INVALID_REQUEST",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error occurred",
  "error_code": "INTERNAL_ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 503 Service Unavailable
```json
{
  "detail": "External service (Gemini API or TTS) unavailable",
  "error_code": "SERVICE_UNAVAILABLE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. For production deployment, consider implementing:
- **Per-IP limits**: 100 requests per minute
- **Per-session limits**: 20 requests per session
- **Burst limits**: 10 requests per 10 seconds

## Integration Examples

### JavaScript/TypeScript Integration

```typescript
interface TriageResponse {
  ai_message: string;
  emr_data: {
    chief_complaint?: string;
    duration?: string;
    severity?: string;
    location?: string;
    emergency_flag?: boolean;
    medical_summary?: string;
  };
  status: 'active' | 'emergency_detected' | 'complete' | 'error';
  session_id: string;
  audio_url?: string;
}

class TriageClient {
  private baseUrl: string;
  private sessionId: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.sessionId = this.generateSessionId();
  }

  async sendMessage(message: string, withAudio = false): Promise<TriageResponse> {
    const endpoint = withAudio ? '/chat/tts' : '/chat';
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: this.sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    return response.json();
  }

  async getSummary(): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/triage/summary?session_id=${this.sessionId}`
    );
    
    if (!response.ok) {
      throw new Error(`Summary request failed: ${response.status}`);
    }

    return response.json();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Usage example
const client = new TriageClient('http://localhost:9001');

async function startTriage() {
  try {
    const response = await client.sendMessage('I have a headache');
    console.log('AI Response:', response.ai_message);
    console.log('EMR Data:', response.emr_data);
    
    if (response.status === 'emergency_detected') {
      alert('Emergency detected! Seek immediate medical attention.');
    }
  } catch (error) {
    console.error('Triage error:', error);
  }
}
```

### Python Integration

```python
import requests
import uuid
from typing import Dict, Any, Optional

class TriageClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session_id = f"session_{uuid.uuid4()}"
    
    def send_message(self, message: str, with_audio: bool = False) -> Dict[str, Any]:
        """Send a message to the triage system."""
        endpoint = '/chat/tts' if with_audio else '/chat'
        
        payload = {
            'message': message,
            'session_id': self.session_id
        }
        
        response = requests.post(
            f"{self.base_url}{endpoint}",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get medical summary for the session."""
        response = requests.get(
            f"{self.base_url}/triage/summary",
            params={'session_id': self.session_id}
        )
        
        response.raise_for_status()
        return response.json()
    
    def check_tts_health(self) -> Dict[str, Any]:
        """Check TTS service health."""
        response = requests.get(f"{self.base_url}/tts/health")
        response.raise_for_status()
        return response.json()

# Usage example
client = TriageClient('http://localhost:9001')

try:
    # Start triage conversation
    response = client.send_message("I have chest pain")
    print(f"AI: {response['ai_message']}")
    print(f"Status: {response['status']}")
    
    # Continue conversation
    response = client.send_message("It started an hour ago")
    print(f"AI: {response['ai_message']}")
    
    # Get final summary
    summary = client.get_summary()
    print(f"Summary: {summary['medical_summary']}")
    
except requests.exceptions.RequestException as e:
    print(f"API Error: {e}")
```

## OpenAPI Specification

The API automatically generates OpenAPI documentation available at:
- **Interactive Docs**: `http://localhost:9001/docs`
- **ReDoc**: `http://localhost:9001/redoc`
- **OpenAPI JSON**: `http://localhost:9001/openapi.json`

## Webhook Integration (Future Enhancement)

For real-time notifications, consider implementing webhooks:

```json
{
  "event": "emergency_detected",
  "session_id": "session_123",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "emr_data": { /* EMR fields */ },
    "ai_message": "Emergency detected message"
  }
}
```

This API documentation provides comprehensive coverage for integrating with the AI Triage System. For additional technical details, refer to the Architecture and Setup documentation.