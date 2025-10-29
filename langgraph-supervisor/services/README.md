# Services Module

This module contains business logic services for various domain operations.

## Files

- `session_service.py` - Conversation session management
- `account_service.py` - Account operations
- `facility_service.py` - Facility operations
- `notes_service.py` - Notes management
- `__init__.py` - Module initialization

## Services

### Session Service
Manages conversation sessions and history:
- `create_session()` - Create new session
- `get_session()` - Get session by ID
- `add_message()` - Add message to session
- `get_conversation_history()` - Get message history
- `delete_session()` - Delete session
- `list_sessions()` - List all sessions

### Account Service
Handles account-related operations:
- `get_account_details(account_id)` - Get account by ID
- `get_all_accounts()` - Get all accounts

### Facility Service
Handles facility-related operations:
- `get_facility_details(facility_id)` - Get facility by ID
- `get_all_facilities()` - Get all facilities

### Notes Service
Manages notes and meeting minutes:
- `save_note(user_id, content)` - Save a note
- `fetch_notes(user_id, date, last_n, order)` - Fetch notes with filters and ordering
  - Supports date formats: "YYYY-MM-DD" or "DD/MM/YYYY" (auto-converted)
  - Supports ordering: "asc" (oldest first) or "desc" (newest first)

## Data Layer

All services use `data.mock_store` for in-memory data storage.

## Logging

All services include comprehensive error logging:
- Initialization logging
- Operation start/complete logging
- Error logging with stack traces
- Success/failure status logging

## Response Format

All service methods return a standardized format:
```python
{
    "success": True/False,
    "data": {...},  # On success
    "error": "message",  # On failure
    ...
}
```

## Error Handling

- Try-except blocks in all methods
- Logging of all errors with stack traces
- Graceful error messages
- Proper exception propagation
