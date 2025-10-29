# API Module

This module contains the FastAPI application and routes for the LangChain v1 single agent API.

## Files

- `routes.py` - API endpoints
- `schemas.py` - Request/response models using Pydantic
- `response_models.py` - Structured output models
- `__init__.py` - Module initialization

## Endpoints

### Root
- `GET /` - API information and available endpoints

### Health
- `GET /health` - Health check with agent status

### Sessions
- `POST /sessions` - Create a new conversation session
- `GET /sessions` - List all sessions (optional user_id filter)
- `GET /sessions/{session_id}` - Get session information
- `DELETE /sessions/{session_id}` - Delete a session
- `GET /sessions/{session_id}/history` - Get conversation history

### Chat
- `POST /chat` - Send message to the single agent
  - Supports account queries (card_key: account_overview or other)
  - Supports facility queries (card_key: facility_overview)
  - Supports note operations (card_key: note_overview)
  - Returns both natural language and structured JSON responses

## Request/Response Models

### Chat Request
```json
{
    "text": "show account overview",
    "user_id": "user@example.com",
    "account_id": "A-011977763",
    "facility_id": "F-015766066",
    "conversation_id": "uuid"
}
```

### Chat Response
```json
{
    "conversation_id": "uuid",
    "final_response": "Natural language response...",
    "card_key": "account_overview",
    "account_overview": [...],
    "rewards_overview": null,
    "facility_overview": null,
    "order_overview": null,
    "note_overview": []
}
```

## Features

### Logging
- Comprehensive error logging throughout API layer
- Request/response logging for debugging
- Exception details captured with stack traces

### Error Handling
- Proper HTTP status codes
- Detailed error messages
- Graceful degradation

### Integration
- Uses `services.session_service` for session management
- Uses `agent.get_agent()` for message processing
- Passes `conversation_id` for short-term memory

## Testing

Test endpoints using:
- Postman collections in `tests/`
- CLI mode via `main.py`
- Direct API calls
