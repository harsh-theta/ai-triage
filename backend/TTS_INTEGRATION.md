# TTS Microservice Integration

This document describes the integration of the external TTS microservice with the medical triage application.

## Overview

The application now uses an external TTS microservice running on port 9003 instead of the previous in-built TTS implementation. This provides better performance, scalability, and separation of concerns.

## Configuration

### Environment Variables

Add the following to your `.env` file:

```
TTS_SERVICE_URL="http://localhost:9003"
```

### Dependencies

The following dependencies were removed from `requirements.txt`:
- `elevenlabs` (no longer needed)

## API Endpoints

### TTS Endpoints

#### `POST /tts`
Convert text to speech using the TTS microservice.

**Request:**
```json
{
  "text": "Hello, how can I help you?",
  "voice": "female"
}
```

**Response:**
```json
{
  "audio_path": "audio/response_abc123.wav",
  "status": "success"
}
```

#### `GET /audio/{filename}`
Serve generated audio files.

#### `GET /tts/health`
Check TTS microservice health status.

**Response:**
```json
{
  "tts_service_healthy": true,
  "tts_service_url": "http://localhost:9003"
}
```

### Enhanced Chat Endpoints

#### `POST /chat/tts`
Chat endpoint that returns both text and audio responses.

**Request:**
```json
{
  "message": "I have a headache",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "ai_message": "I understand you have a headache...",
  "status": "active",
  "audio_path": "audio/response_def456.wav",
  "audio_url": "/audio/response_def456.wav",
  "emr_data": {...}
}
```

#### `POST /triage/text/tts`
Triage endpoint with TTS support.

## TTS Client

The `TTSClient` class in `tts_client.py` handles communication with the TTS microservice:

```python
from tts_client import tts_client

# Generate speech
audio_path = tts_client.text_to_speech("Hello world", voice="female")

# Check service health
is_healthy = tts_client.health_check()
```

## Testing

Run the test script to verify TTS integration:

```bash
python test_tts.py
```

This will test:
- TTS microservice health
- Direct TTS client functionality
- API endpoints
- Chat integration

## File Structure

```
backend/
├── tts_client.py          # TTS microservice client
├── test_tts.py           # TTS integration tests
├── audio/                # Generated audio files
└── main.py              # Updated with TTS endpoints
```

## Migration Notes

### Removed Files/Directories
- `backend/TTS/` - Old TTS implementation
- `elevenlabs` dependency

### Added Files
- `tts_client.py` - New TTS microservice client
- `test_tts.py` - Integration tests
- `TTS_INTEGRATION.md` - This documentation

### Modified Files
- `main.py` - Added TTS endpoints and integration
- `requirements.txt` - Removed TTS dependencies
- `.env` - Added TTS service URL configuration

## Troubleshooting

1. **TTS service not available**: Ensure the TTS microservice is running on port 9003
2. **Audio files not found**: Check that the `audio/` directory exists and has write permissions
3. **Connection errors**: Verify the `TTS_SERVICE_URL` in your `.env` file

## Usage Examples

### Basic TTS
```python
# Direct client usage
from tts_client import tts_client
audio_path = tts_client.text_to_speech("Hello patient, how are you feeling?")
```

### API Usage
```bash
# Test TTS endpoint
curl -X POST "http://localhost:8000/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "voice": "female"}'

# Chat with TTS
curl -X POST "http://localhost:8000/chat/tts" \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a fever", "session_id": "test"}'
```