# hass-external-conversation-agent

A Home Assistant custom component that registers as a conversation agent and forwards requests to an external HTTP endpoint.

This lets you plug any custom logic into Home Assistant's Assist voice pipeline without having to run it inside HA itself.

## How It Works

```
User (voice/text)
      │
      ▼
Home Assistant Assist pipeline
      │  (conversation.process)
      ▼
ExternalConversationAgent  ← this component
      │  (HTTP POST)
      ▼
Your external service
      │  (JSON response)
      ▼
Spoken reply back to user
```

## Installation

Copy `custom_components/external_conversation/` into your Home Assistant `custom_components/` directory and restart HA.

Then add the integration via **Settings → Integrations → Add Integration → External Conversation Agent**.

## Configuration

| Field | Required | Description |
|-------|----------|-------------|
| Name | Yes | Display name for this agent instance |
| Endpoint URL | Yes | HTTP(S) URL that receives conversation requests |
| Bearer Token | No | Authorization token sent as `Authorization: Bearer <token>` |

All fields can be changed after setup via **Settings → Integrations → External Conversation Agent → Configure**.

## HTTP Contract

### Request (POST to your endpoint)

```json
{
  "text": "Turn off the kitchen lights",
  "language": "en",
  "conversation_id": "01J...",
  "device_id": "abc123",
  "agent_id": "external_conversation.my_agent"
}
```

### Response (from your endpoint)

```json
{
  "message": "Done, kitchen lights are off.",
  "continue_conversation": false
}
```

Set `continue_conversation: true` to keep the microphone open for a follow-up turn.

## Development

Initialize the project:
```
make init
```

Add dependencies:
```
make install <package-name>
```

Run the project:
```
make start
```

Deploy the custom component to a Home Assistant server:
```
make deploy
```

Build a Docker container image:
```
make build
```
