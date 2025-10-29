# Testing Guide

This guide shows you how to test the LangGraph Supervisor Agent system using different methods.

## Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Copy the example file
cp env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your-key-here
```

## Testing Methods

### 1. Using the Test Script

Run the complete system test:

```bash
python test_complete.py
```

This will:
- Initialize the agent
- Create a session
- Test account queries with memory
- Test facility queries
- Verify structured output

Expected output:
```
============================================
LangGraph Supervisor Agent - Complete System Test
============================================

1. Initializing agent...
✅ Agent initialized successfully

2. Creating session...
✅ Session created: <uuid>

3. Testing message with account context...
💬 User: show me my account details
🤖 Agent: [Natural language response]
📊 Card Key: account_overview
📊 Success: True
📊 Account Data: 1 item(s)

...
```

### 2. Using the API Server

#### Start the Server

```bash
python main.py
```

Server will start at `http://localhost:8000`

#### Test with cURL

##### Create a Session

```bash
curl -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test@example.com"}'
```

Expected response:
```json
{
  "conversation_id": "abc-123-def-456",
  "user_id": "test@example.com",
  "created_at": "2024-01-01T00:00:00",
  "message": "Conversation created successfully"
}
```

##### Send a Chat Message

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "show account overview",
    "user_id": "test@example.com",
    "account_id": "A-011977763",
    "conversation_id": "abc-123-def-456"
  }'
```

Expected response:
```json
{
  "conversation_id": "abc-123-def-456",
  "final_response": "Here is your account overview...",
  "card_key": "account_overview",
  "account_overview": [
    {
      "account_id": "A-011977763",
      "name": "Dimod Account",
      "status": "ACTIVE",
      ...
    }
  ],
  "rewards_overview": null,
  "facility_overview": null,
  "order_overview": null,
  "note_overview": []
}
```

##### Test Follow-up with Memory

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "what about my facilities?",
    "user_id": "test@example.com",
    "account_id": "A-011977763",
    "conversation_id": "abc-123-def-456"
  }'
```

The agent should remember the previous conversation about accounts and respond about facilities.

### 3. Using Postman

1. Import the collection from `tests/postman_collection.json`

2. Create a session:
   - POST `/sessions`
   - Body: `{"user_id": "test@example.com"}`
   - Copy the `conversation_id` from response

3. Send chat messages:
   - POST `/chat`
   - Body:
   ```json
   {
     "text": "show account overview",
     "user_id": "test@example.com",
     "account_id": "A-011977763",
     "conversation_id": "<your-conversation-id>"
   }
   ```

4. Test memory with follow-ups:
   - Same endpoint, different message
   - Agent should remember context

### 4. Using CLI Mode

#### Create a Session

```bash
python main.py --start-session --user-id "test@example.com"
```

Output:
```
✅ Session created: abc-123-def-456
👤 User ID: test@example.com
```

#### Send a Message

```bash
python main.py \
  --message "show account overview" \
  --session-id "abc-123-def-456" \
  --user-id "test@example.com" \
  --verbose
```

Output:
```
💬 You: show account overview
🤖 Agent: Here is your account overview...

📊 Structured Output:
{
  "final_response": "...",
  "card_key": "account_overview",
  "account_overview": [...]
}

🔧 Tools used: 1
   - fetch_account_details
```

## Testing Scenarios

### Test 1: Account Query

**Input:**
```json
{
  "text": "show account overview",
  "user_id": "user@example.com",
  "account_id": "A-011977763",
  "conversation_id": "session-123"
}
```

**Expected:**
- `card_key`: "account_overview"
- `account_overview`: Contains account data
- `final_response`: Natural language explanation

### Test 2: Facility Query

**Input:**
```json
{
  "text": "show facility details",
  "user_id": "user@example.com",
  "facility_id": "F-015766066",
  "conversation_id": "session-123"
}
```

**Expected:**
- `card_key`: "facility_overview"
- `facility_overview`: Contains facility data
- `final_response`: Natural language explanation

### Test 3: Memory Test

**Message 1:**
```json
{
  "text": "what's my account name?",
  "account_id": "A-011977763",
  "conversation_id": "session-123"
}
```

**Message 2:**
```json
{
  "text": "what's the status of my facilities?",
  "conversation_id": "session-123"
}
```

**Expected:**
- Agent remembers account context from message 1
- Agent can answer about facilities without repeating account_id

### Test 4: Notes Query

**Input:**
```json
{
  "text": "show my recent notes",
  "user_id": "user@example.com",
  "conversation_id": "session-123"
}
```

**Expected:**
- `card_key`: "note_overview"
- `note_overview`: Contains notes list
- `final_response`: Natural language explanation

## Verification Checklist

- [ ] Agent initializes without errors
- [ ] Session creation works
- [ ] Chat endpoint returns responses
- [ ] Structured output includes both JSON and natural language
- [ ] Card key is properly set based on query
- [ ] Account queries return account data
- [ ] Facility queries return facility data
- [ ] Memory works across multiple messages
- [ ] Error handling works for invalid inputs
- [ ] Logging shows detailed information

## Troubleshooting

### Agent Not Responding

Check logs for errors:
```bash
python main.py 2>&1 | tee output.log
```

### Memory Not Working

Ensure `conversation_id` is consistent across requests and check that checkpointer is enabled in agent initialization.

### Structured Output Not Coming Through

Verify that `response_format=StructuredResponse` is set in `agent/supervisor.py`.

### Tool Not Being Called

Check tool definitions in `agent/tools.py` and verify tool names match exactly.

## Sample Test Cases

See `test_complete.py` for a comprehensive test suite that validates:
- Agent initialization
- Session management
- Account queries with structured output
- Memory persistence
- Facility queries
- Error handling

Run it with:
```bash
python test_complete.py
```

