# TTS Error Handling Improvements

## Overview

This document describes the improvements made to the TTS (Text-to-Speech) system to ensure that API failures, rate limits, or service unavailability do not cause the main application requests to fail.

## Problem Statement

The original concern was that if the TTS API fails due to:
- API rate limits being exhausted
- Network connectivity issues
- Service unavailability
- Invalid API keys or configuration

The main request could fail, even though there's a frontend fallback to browser TTS.

## Solution

### 1. Non-Blocking TTS Generation

All TTS endpoints now handle TTS failures gracefully:
- **Main response is never blocked** by TTS failures
- If TTS succeeds: `audio_url` is included in the response
- If TTS fails: Response continues without `audio_url`, frontend fallback handles it

### 2. Circuit Breaker Pattern

Implemented circuit breaker to prevent repeated calls to failing services:

```python
class CircuitBreaker:
    - CLOSED: Normal operation
    - OPEN: Service is failing, skip TTS calls
    - HALF_OPEN: Testing if service has recovered
```

**Configuration (via environment variables):**
- `TTS_CIRCUIT_BREAKER_THRESHOLD=5` - Failures before opening circuit
- `TTS_CIRCUIT_BREAKER_TIMEOUT=60` - Seconds before trying again

### 3. Retry Logic

Automatic retry with exponential backoff:
- `TTS_MAX_RETRIES=2` - Number of retry attempts
- `TTS_RETRY_DELAY=1.0` - Delay between retries (seconds)

### 4. Enhanced Logging

Comprehensive logging for debugging:
- TTS attempt logs
- Success/failure tracking
- Circuit breaker state changes
- Detailed error messages

## Endpoints Affected

### `/triage/text/tts`
- Returns triage response with optional `audio_url`
- Never fails due to TTS issues

### `/chat/tts`
- Returns chat response with optional `audio_url`
- Never fails due to TTS issues

### `/tts` (standalone)
- Returns success/error status
- Provides detailed error information

### `/tts/health`
- Enhanced with circuit breaker status
- Shows provider configuration
- Monitors service health

## Configuration

### Environment Variables

```bash
# TTS Provider Selection
TTS_PROVIDER="murf"  # or "microservice"

# Microservice Configuration
TTS_SERVICE_URL="http://106.201.228.100:9003"

# Murf Configuration
MURF_API_KEY="your_api_key_here"
MURF_VOICE_ID="en-IN-priya"

# Error Handling Configuration
TTS_MAX_RETRIES=2
TTS_RETRY_DELAY=1.0
TTS_CIRCUIT_BREAKER_THRESHOLD=5
TTS_CIRCUIT_BREAKER_TIMEOUT=60
```

## Testing

### Manual Testing

1. **Normal Operation:**
   ```bash
   curl -X POST http://localhost:8000/chat/tts \
     -H "Content-Type: application/json" \
     -d '{"message": "I have a headache", "session_id": "test"}'
   ```

2. **TTS Failure Simulation:**
   - Stop TTS microservice
   - Use invalid API keys
   - Set invalid service URLs
   - Requests should still succeed without `audio_url`

3. **Health Check:**
   ```bash
   curl http://localhost:8000/tts/health
   ```

### Automated Testing

Run the test script:
```bash
python backend/test_tts_error_handling.py
```

## Error Handling Flow

```
Request → Main Processing → TTS Generation (non-blocking)
                         ↓
                    Circuit Breaker Check
                         ↓
                    Retry Logic (if needed)
                         ↓
                    Success: Add audio_url
                    Failure: Continue without audio_url
                         ↓
                    Return Response (always succeeds)
```

## Monitoring

### Health Endpoint Response

```json
{
  "tts_service_healthy": true,
  "provider_info": {
    "provider": "murf",
    "max_retries": 2,
    "retry_delay": 1.0
  },
  "circuit_breaker_status": {
    "microservice": {
      "state": "CLOSED",
      "failure_count": 0,
      "failure_threshold": 5
    },
    "murf": {
      "state": "CLOSED", 
      "failure_count": 0,
      "failure_threshold": 5
    }
  }
}
```

### Log Messages

- `TTS successful on attempt X`
- `TTS failed after X attempts, circuit breaker state: OPEN`
- `TTS circuit breaker is OPEN for provider, skipping TTS generation`
- `Circuit breaker opened after X failures`

## Benefits

1. **Reliability:** Main application never fails due to TTS issues
2. **Performance:** Circuit breaker prevents wasted calls to failing services
3. **Resilience:** Automatic recovery when services come back online
4. **Observability:** Comprehensive logging and health monitoring
5. **Graceful Degradation:** Seamless fallback to frontend TTS

## Frontend Integration

The frontend should check for the presence of `audio_url` in responses:

```javascript
const response = await fetch('/chat/tts', {
  method: 'POST',
  body: JSON.stringify({message: userInput})
});

const data = await response.json();

if (data.audio_url) {
  // Use server-generated audio
  playAudio(data.audio_url);
} else {
  // Fallback to browser TTS
  speechSynthesis.speak(new SpeechSynthesisUtterance(data.ai_message));
}
```

## Conclusion

These improvements ensure that TTS failures never impact the core functionality of the intelligent triage system. The application gracefully degrades to frontend TTS when server-side TTS is unavailable, providing a seamless user experience.