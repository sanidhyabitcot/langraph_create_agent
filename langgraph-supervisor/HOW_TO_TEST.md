# How to Test and Get Expected Output

This guide shows you **exactly** how to test to get the expected output you shared.

## Expected Output Format

Based on your requirements, you should get responses like:

```json
{
    "conversation_id": "0de73ced-0e12-4bff-b1c2-ae4d7136a3be",
    "final_response": "Here is a summary of your account:\n\n- Account Name: Dimod Account\n- Status: ACTIVE\n...",
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

## Step-by-Step Testing Guide

### Step 1: Set Up Environment

```bash
# Navigate to project
cd langgraph-supervisor

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### Step 2: Choose Your Testing Method

## Method 1: Using API Server (Recommended)

### A. Start the Server

```bash
python main.py
```

You should see:
```
🚀 Starting Supervisor Agent API
📍 Server: http://0.0.0.0:8000
📚 Docs: http://0.0.0.0:8000/docs
```

### B. Create a Session

```bash
curl -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "kaushal.sethia.c@evolus.com"}'
```

**Response:**
```json
{
  "conversation_id": "abc123-def456",
  "user_id": "kaushal.sethia.c@evolus.com",
  "created_at": "2024-01-01T00:00:00",
  "message": "Conversation created successfully"
}
```

**Copy the `conversation_id`!**

### C. Send Chat Request

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "show account overview",
    "user_id": "kaushal.sethia.c@evolus.com",
    "account_id": "A-011977763",
    "conversation_id": "abc123-def456"
  }'
```

### D. Expected Response

```json
{
  "conversation_id": "abc123-def456",
  "final_response": "Here is a summary of your account...",
  "card_key": "account_overview",
  "account_overview": [
    {
      "account_id": "A-011977763",
      "name": "Dimod Account",
      "status": "ACTIVE",
      "is_tna": false,
      "created_at": "2025-02-18T04:46:02.486+00:00",
      "pricing_model": "ACCOUNT_LOYALTY",
      "address_line1": "100 WYCLIFFE",
      "address_line2": "",
      "address_city": "IRVINE",
      "address_state": "CA",
      "address_postal_code": "92602-1206",
      "address_country": "",
      "facilities": [...],
      "current_balance": 0,
      "pending_balance": 50,
      "current_tier": "Member",
      "next_tier": "silver",
      ...
    }
  ],
  "rewards_overview": null,
  "facility_overview": null,
  "order_overview": null,
  "note_overview": []
}
```

## Method 2: Using Test Script

```bash
python test_complete.py
```

This will automatically:
1. Initialize the agent
2. Create a session
3. Send account query
4. Test memory with follow-up
5. Test facility query
6. Show all outputs with card_keys

## Method 3: Using CLI

### Create Session

```bash
python main.py --start-session --user-id "test@example.com"
```

Output: `✅ Session created: <session_id>`

### Send Message

```bash
python main.py \
  --message "show account overview" \
  --session-id "<session_id>" \
  --user-id "test@example.com" \
  --verbose
```

## Method 4: Using Postman

1. Import `tests/postman_collection.json` into Postman
2. Create session: `POST /sessions` with `{"user_id": "..."}`
3. Chat: `POST /chat` with your request payload

## Testing Different Scenarios

### Scenario 1: Account Query

**Request:**
```json
{
  "text": "show account overview",
  "user_id": "user@example.com",
  "account_id": "A-011977763",
  "conversation_id": "<your-session-id>"
}
```

**Expected:**
- `card_key`: "account_overview"
- `account_overview`: Contains account data
- `final_response`: Natural language explanation

### Scenario 2: Facility Query

**Request:**
```json
{
  "text": "show facility details",
  "user_id": "user@example.com",
  "facility_id": "F-015766066",
  "conversation_id": "<your-session-id>"
}
```

**Expected:**
- `card_key`: "facility_overview"
- `facility_overview`: Contains facility data

### Scenario 3: Memory Test

**Message 1:**
```json
{
  "text": "what's my account name?",
  "account_id": "A-011977763",
  "conversation_id": "session-123"
}
```

**Message 2 (no account_id needed):**
```json
{
  "text": "what's the status?",
  "conversation_id": "session-123"
}
```

**Expected:** Agent remembers account from message 1

## Troubleshooting

### Issue: Agent returns error
**Solution:** Check `.env` has valid OPENAI_API_KEY

### Issue: Session not found
**Solution:** Create session first, use returned conversation_id

### Issue: No structured output
**Solution:** Check `response_format=StructuredResponse` in agent initialization

### Issue: No memory
**Solution:** Ensure `conversation_id` is same across requests

## Expected Output Structure

Always verify you get:

1. ✅ `conversation_id` - Same as request
2. ✅ `final_response` - Natural language text
3. ✅ `card_key` - Appropriate card type
4. ✅ `account_overview` / `facility_overview` / `note_overview` - Based on query
5. ✅ Other fields: null or empty arrays

## Verification Checklist

- [ ] Session created successfully
- [ ] Chat endpoint returns response
- [ ] Response has `final_response` field
- [ ] Response has `card_key` field
- [ ] Response has appropriate overview data
- [ ] Natural language and JSON both present
- [ ] Memory works across multiple messages
- [ ] No errors in console/logs

## Quick Test Command

```bash
# One-liner test (after starting server)
SESSION_ID=$(curl -s -X POST http://localhost:8000/sessions -H "Content-Type: application/json" -d '{"user_id":"test@example.com"}' | jq -r .conversation_id)
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"text\":\"show account overview\",\"user_id\":\"test@example.com\",\"account_id\":\"A-011977763\",\"conversation_id\":\"$SESSION_ID\"}" | jq
```

This creates a session and immediately sends a chat message, showing the full response.

