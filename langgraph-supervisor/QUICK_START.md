# 🚀 Quick Start - Get Your Expected Output

## Setup (One Time)

```bash
cd langgraph-supervisor
pip install -r requirements.txt
echo "OPENAI_API_KEY=your-key" > .env
```

## Test Now (3 Steps)

### Step 1: Start Server
```bash
python main.py
```

### Step 2: Create Session
```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test@example.com"}'
```
**Copy the `conversation_id` from response**

### Step 3: Send Chat Request
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "show account overview",
    "user_id": "test@example.com",
    "account_id": "A-011977763",
    "conversation_id": "YOUR_SESSION_ID_HERE"
  }'
```

## Expected Output

```json
{
  "conversation_id": "...",
  "final_response": "Here is your account overview...",
  "card_key": "account_overview",
  "account_overview": [{...}],
  "rewards_overview": null,
  "facility_overview": null,
  "order_overview": null,
  "note_overview": []
}
```

## All Requirements Met ✅

- ✅ Single Agent (LangChain v1 `create_agent`)
- ✅ Structured Output (JSON + Natural Language)
- ✅ Short-Term Memory (InMemorySaver checkpointer)
- ✅ Card Key System (`account_overview`, `facility_overview`, `note_overview`, `other`)
- ✅ Account/Facility ID support (separate request fields)
- ✅ Notes Operations (save, fetch with filtering and ordering)
- ✅ Error Logging (comprehensive throughout)
- ✅ Clean Architecture (separated modules)
- ✅ Testing Ready (Postman, CLI, scripts)

**That's it! You should now get the expected output format.**

