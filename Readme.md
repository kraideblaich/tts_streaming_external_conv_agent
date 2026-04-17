# External Conversation Stream

A [Home Assistant](https://www.home-assistant.io/) custom integration that enables streaming conversations with external AI agents. This integration allows you to connect Home Assistant's conversation component to any external endpoint that supports streaming responses.

## Features

- 🔄 **Streaming Responses** - Real-time streaming of conversation responses
- 🔐 **Optional Authentication** - Bearer token support for secure endpoints
- 📱 **Device Integration** - Passes device and agent context to external endpoints

## Installation

### Via HACS

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Add this repository to HACS as a custom integration
3. Search for "External Conversation Stream" and install it
4. Restart Home Assistant
5. Go to **Settings** → **Devices & Services** → **Create Automation** and add a new integration
6. Select "External Conversation Stream" and configure your endpoint

### Manual Installation

1. Download the repository
2. Copy the `streaming_external_conversation` folder to your `custom_components` directory
3. Restart Home Assistant
4. Set up through the UI as described above

## Configuration

The integration requires the following configuration:

| Field | Required | Description |
|-------|----------|-------------|
| **Name** | ✅ Yes | A friendly name for this conversation agent |
| **Endpoint URL** | ✅ Yes | The URL of your external streaming conversation endpoint |
| **Bearer Token** | ❌ No | Optional authentication token for secure endpoints |

## API Specification

### Request Format

The integration sends POST requests to your endpoint with the following JSON payload:

```json
{
  "text": "user message",
  "language": "en",
  "conversation_id": "conversation_id_string",
  "device_id": "device_id_string",
  "agent_id": "agent_id_string",
  "extra_system_prompt": "optional system prompt"
}
```

### Response Format

Your endpoint should return **newline-delimited JSON (NDJSON)** with streaming events:

#### Assistant Start Event
```json
{"type": "assistant_start"}
```

#### Assistant Content Delta Event
```json
{"type": "assistant_delta", "content": "streamed response text"}
```

#### Tool Result Event
```json
{
  "type": "tool_result",
  "tool_call_id": "call_id",
  "tool_name": "tool_name",
  "tool_result": "result data"
}
```

#### Completion Event
```json
{
  "type": "done",
  "continue_conversation": false
}
```

## Usage

Once configured, the conversation agent will be available in Home Assistant's conversation component. You can:

- Chat with your agent through the UI
- Use it in automations and scripts
- Integrate it with voice assistants and other Home Assistant services

## Example External Endpoint

Here's a minimal example of what your external endpoint might look like (Python/FastAPI):

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

@app.post("/conversation")
async def conversation(request: dict):
    """Handle streaming conversation requests."""
    user_text = request.get("text")
    
    async def event_generator():
        # Send assistant start event
        yield json.dumps({"type": "assistant_start"}).encode() + b"\n"
        
        # Stream response
        response_text = f"You said: {user_text}"
        for char in response_text:
            yield json.dumps({
                "type": "assistant_delta",
                "content": char
            }).encode() + b"\n"
        
        # Send done event
        yield json.dumps({
            "type": "done",
            "continue_conversation": False
        }).encode() + b"\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson"
    )
```

## Requirements

- Home Assistant 2024.1.0 or later
- External streaming endpoint that supports NDJSON format
