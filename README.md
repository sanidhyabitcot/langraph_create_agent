# LangGraph Agent

Build a single-agent, end-to-end local architecture that can be exercised from Postman, the terminal, or any frontend. The agent supports multi-turn conversations and retains short-term memory of prior messages so it can reason over the conversation history.

## 🎯 Overview

A production-ready single agent architecture using LangGraph and LangChain v1 for multi-tool agentic systems with structured output, short-term memory, and comprehensive logging.

## ✨ Features

- ✅ **Single Agent Architecture** - Uses LangChain v1's `create_agent`
- ✅ **Structured Output** - Returns both JSON and natural language
- ✅ **Short-Term Memory** - Thread-based conversation context using LangGraph checkpoints
- ✅ **Card Key System** - Dynamic UI rendering (`account_overview`, `facility_overview`, `note_overview`, `other`)
- ✅ **Error Logging** - Comprehensive logging throughout
- ✅ **Clean Architecture** - Separated modules with clear responsibilities
- ✅ **Multiple Interfaces** - API, CLI, and test scripts
- ✅ **LangChain v1 Compatible** - Uses latest `langchain.agents.create_agent` with `system_prompt`

## 🏗️ Architecture

```
langgraph-supervisor/
├── agent/          # LangGraph supervisor agent
├── api/            # FastAPI endpoints and schemas
├── services/       # Business logic layer
├── data/           # Data models and mock store
├── docs/           # Documentation
├── tests/          # Test collections and scripts
└── main.py         # Application entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API Key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/sanidhyabitcot/langraph_create_agent.git
cd langraph_create_agent/langgraph-supervisor
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file:
```env
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

4. **Run the API server**
```bash
python main.py
```

The API will be available at:
- **Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 Usage

### API Mode (Default)

#### 1. Create a Session

```bash
curl -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user@example.com"}'
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "user_id": "user@example.com",
  "created_at": "2024-01-01T00:00:00",
  "message": "Conversation created successfully"
}
```

#### 2. Send a Chat Message

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "show account overview",
    "user_id": "user@example.com",
    "account_id": "A-011977763",
    "conversation_id": "uuid"
  }'
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "final_response": "Here is your account overview...",
  "card_key": "account_overview",
  "account_overview": [
    {
      "account_id": "A-011977763",
      "name": "Dimod Account",
      "status": "ACTIVE",
      "balance": 15000.00
    }
  ],
  "rewards_overview": null,
  "facility_overview": null,
  "order_overview": null,
  "note_overview": []
}
```

### CLI Mode

#### Create a Session
```bash
python main.py --start-session --user-id "user@example.com"
```

#### Send a Message
```bash
python main.py --message "show account overview" \
  --session-id "uuid" \
  --user-id "user@example.com" \
  --verbose
```

## 🔧 Architecture Details

### Single Agent

The system uses a single LangChain v1 agent that:
- Manages all tool orchestration
- Maintains conversation context
- Provides structured responses
- Uses short-term memory via checkpoints
- Intelligent card key selection based on query intent

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

### Structured Output

The agent returns both:
1. **Natural Language** - Human-readable response
2. **Structured JSON** - Machine-readable data

Card keys determine UI rendering:
- `account_overview` - Account data (when overview requested)
- `facility_overview` - Facility data (when facility details requested)
- `note_overview` - Notes data (when notes fetched)
- `other` - Specific follow-ups, greetings, and non-overview queries

### Short-Term Memory

Uses LangGraph's `InMemorySaver` checkpointer:
```python
from langchain.agents import create_agent

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,  # LangChain v1 uses system_prompt
    checkpointer=InMemorySaver()  # Enable memory
)
```

### Available Tools

The agent has access to 4 tools:
1. **`fetch_account_details(account_id)`** - Get account information
2. **`fetch_facility_details(facility_id)`** - Get facility information
3. **`save_note(user_id, content)`** - Save notes for users
4. **`fetch_notes(user_id, date, last_n, order)`** - Retrieve notes with filtering and ordering
   - Supports: "fetch all notes", "fetch last N notes", "fetch first N notes", "fetch notes for DD/MM/YYYY"

## 📝 Request/Response Format

### Chat Request Payload

```json
{
  "text": "show account overview",
  "user_id": "user@example.com",
  "account_id": "A-011977763",
  "facility_id": "F-015766066",
  "conversation_id": "uuid"
}
```

**Fields:**
- `text` - User message (required)
- `user_id` - User identifier (required)
- `account_id` - Account ID for context (optional)
- `facility_id` - Facility ID for context (optional)
- `conversation_id` - Session ID for memory (required)

## 🧪 Testing

### Using Postman

1. Import the collection from `tests/postman_collection.json`
2. Start the API server: `python main.py`
3. Use Postman to test endpoints

### Using Test Script

```bash
chmod +x tests/test_script.sh
./tests/test_script.sh
```

### Using CLI

```bash
# Create session
python main.py --start-session --user-id "test@example.com"

# Send message
python main.py --message "Hello" --session-id "uuid" --user-id "test@example.com"
```

## 📦 Module Structure

- **`agent/`** - Main agent implementation (LangChain v1), tool definitions
- **`api/`** - FastAPI endpoints, request/response models, structured output models
- **`services/`** - Session management, account/facility/notes operations
- **`data/`** - Pydantic models, in-memory storage, sample data
- **`docs/`** - Additional documentation
- **`tests/`** - Postman collections and test scripts

## 📋 Requirements Met

- ✅ **Single Agent Architecture** - No multi-agent setup
- ✅ **Structured Output** - Both JSON and natural language
- ✅ **Prompt for Structured Output** - System prompt enforces structure
- ✅ **Short-Term Memory** - Checkpointer-based memory
- ✅ **Account/Facility ID Support** - Separate fields in request
- ✅ **Card Key System** - Dynamic UI rendering
- ✅ **Dual Response** - JSON + natural language
- ✅ **Clean Architecture** - Separated modules with READMEs
- ✅ **Error Logging** - Comprehensive logging everywhere
- ✅ **Multiple Testing Methods** - Postman, CLI, scripts

## 📚 Dependencies

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic>=2.5.0,<3.0.0
python-dotenv==1.2.1
openai>=1.3.0
langchain>=0.1.0
langchain-openai>=0.0.2
langgraph>=1.0.1
httpx>=0.25.2
langchain-core>=0.1.0
```

**Note:** This project uses LangChain v1 which requires `langchain>=0.1.0` and `langgraph>=1.0.1`. The agent uses `create_agent` from `langchain.agents` with `system_prompt` parameter.

## 🔨 Development

### Running with Debug Logging

```bash
LOG_LEVEL=DEBUG python main.py
```

### Adding New Tools

1. Define tool in `agent/tools.py`:
```python
@tool
def my_new_tool(param: str) -> str:
    """Tool description"""
    return "result"
```

2. Add to `ALL_TOOLS` list
3. Implement service logic in `services/`
4. Agent will automatically have access

## 🐛 Troubleshooting

### OpenAI API Key Not Found
Set `OPENAI_API_KEY` in `.env` file or environment variables.

### Module Import Errors
Ensure you're running from the correct directory:
```bash
cd langgraph-supervisor
python main.py
```

### Agent Not Returning Structured Output
The agent returns structured data based on query intent. Ensure you're passing correct `account_id` or `facility_id` in requests for overview queries.

### LangChain v1 Migration Issues
If you see errors about `prompt` parameter, ensure you're using `system_prompt` instead. The import should be `from langchain.agents import create_agent`.

## 📖 Additional Documentation

- [Quickstart Guide](langgraph-supervisor/docs/QUICKSTART.md)
- [CLI Guide](langgraph-supervisor/docs/CLI_GUIDE.md)
- [Agent Documentation](langgraph-supervisor/agent/README.md)
- [API Documentation](langgraph-supervisor/api/README.md)
- [Services Documentation](langgraph-supervisor/services/README.md)
- [Data Documentation](langgraph-supervisor/data/README.md)

## 📄 License

MIT

## 👤 Author

LangGraph Supervisor Agent Implementation

