# Agent Module

This module contains the core LangChain v1 single agent implementation.

## Files

- `single_agent.py` - Main agent implementation using LangChain v1's `create_agent`
- `tools.py` - Tool definitions for the agent
- `__init__.py` - Module initialization

## Features

### Single Agent Architecture
- Uses LangChain v1's `create_agent` from `langchain.agents`
- No multi-agent architecture - single agent handles all operations
- Migrated from `create_react_agent` to LangChain v1 API

### Structured Output
- Returns both natural language and structured JSON responses
- Card key based system for UI rendering decisions
- Supports: `account_overview`, `facility_overview`, `note_overview`, `other`

### Short-Term Memory
- Uses `InMemorySaver` checkpointer for conversation state
- Thread-based memory using `thread_id` in config
- Maintains context across conversation turns

### Card Key Logic
- `account_overview`: When user asks for account overview with account_id
- `facility_overview`: When user asks for facility details (with or without facility_id)
- `note_overview`: When user asks to fetch notes
- `other`: For specific follow-up questions, greetings, etc.

### Tools
The agent has access to the following tools:
1. `fetch_account_details(account_id)` - Retrieve account information
2. `fetch_facility_details(facility_id)` - Get facility information
3. `save_note(user_id, content)` - Save notes for users
4. `fetch_notes(user_id, date, last_n, order)` - Retrieve saved notes with filtering

## Usage

```python
from agent import get_agent

agent = get_agent()
result = agent.process_message(
    user_message="show account overview",
    conversation_history=[],
    account_id="A-011977763",
    conversation_id="thread-123"
)
```

## Response Format

The agent returns both natural language and structured data:

```python
{
    "final_response": "Natural language explanation...",
    "card_key": "account_overview",
    "account_overview": [...],
    "rewards_overview": None,
    "facility_overview": None,
    "order_overview": None,
    "note_overview": []
}
```

## Dependencies

- `langgraph` - State management and agent orchestration
- `langchain-openai` - LLM interface
- `api.response_models` - Structured output models
- `services` - Business logic layer
