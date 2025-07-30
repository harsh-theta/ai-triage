# TTS Providers Integration

This document describes the dual TTS provider system implemented in the intelligent triage backend.

## Overview

The system now supports two TTS providers:
1. **Microservice** - The original TTS microservice
2. **Murf** - Murf AI TTS API

You can switch between providers using environment variables without changing any code.

## Configuration

### Environment Variables

Add these variables to your `.env` file:

```bash
# TTS Configuration
TTS_PROVIDER="microservice"  # Options: "microservice" or "murf"
MURF_API_KEY="your-murf-api-key"
MURF_VOICE_ID="en-IN-priya"  # Default voice for Murf
```

### Provider Options

#### Microservice Provider
- Uses the existing TTS microservice
- Requires `TTS_SERVICE_URL` to be set
- Returns proxied URLs through the intelligent triage domain
- Supports "female" and "male" voice parameters

#### Murf Provider
- Uses Murf AI TTS API
- Requires `MURF_API_KEY` to be set
- Returns direct URLs from Murf's CDN
- Uses voice IDs (e.g., "en-IN-priya")

## API Endpoints

### Existing Endpoints (unchanged)
- `POST /tts` - Convert text to speech
- `POST /chat/tts` - Chat with TTS response
- `POST /triage/text/tts` - Triage with TTS response

### New Endpoints
- `GET /tts/provider` - Get current TTS provider information
- `GET /tts/health` - Enhanced health check with provider info

## Usage Examples

### Switching to Murf
```bash
# In .env file
TTS_PROVIDER="murf"
MURF_API_KEY="your-api-key"
MURF_VOICE_ID="en-IN-priya"
```

### Switching to Microservice
```bash
# In .env file
TTS_PROVIDER="microservice"
TTS_SERVICE_URL="http://106.201.228.100:9003"
```

## Testing

Run the test scripts to verify both providers work:

```bash
# Test both providers
python test_tts_providers.py

# Test integration
python test_integration.py
```

## Voice Mapping

### Microservice
- `"female"` → Uses female voice
- `"male"` → Uses male voice

### Murf
- `"female"` → Uses `MURF_VOICE_ID` (default: "en-IN-priya")
- `"male"` → Uses `MURF_MALE_VOICE_ID` if set, otherwise default voice

## Error Handling

- If Murf API fails, the system logs the error and returns `None`
- If microservice fails, it falls back gracefully
- Health checks verify provider availability
- Missing API keys or configuration will disable the respective provider

## Dependencies

Make sure to install the Murf library:

```bash
pip install murf
```

## Implementation Details

The `TTSClient` class automatically detects the configured provider and routes requests accordingly. No changes are needed in the main application code - just update the environment variables to switch providers.