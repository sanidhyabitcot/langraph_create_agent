# 🖥️ CLI Usage Guide

The Supervisor Agent supports **Command Line Interface (CLI)** mode for quick testing and automation.

## 🚀 CLI Modes

### Mode 1: API Server (Default)
```bash
python main.py
# or
python main.py --api
```

### Mode 2: CLI (Interactive)
```bash
python main.py --start-session
python main.py --session-id <id> --message "Your message"
```

---

## 📋 CLI Commands

### 1. Create a Session

```bash
python main.py --start-session
```

**Output:**
```
✅ Session created: 550e8400-e29b-41d4-a716-446655440000
```

**With User ID:**
```bash
python main.py --start-session --user-id user123
```

**Output:**
```
✅ Session created: 550e8400-e29b-41d4-a716-446655440000
👤 User ID: user123
```

---

### 2. Send a Message (Existing Session)

```bash
python main.py --session-id <session-id> --message "What is the status of account A-011977763?"
```

**Example:**
```bash
python main.py \
  --session-id 550e8400-e29b-41d4-a716-446655440000 \
  --message "What is the status of account A-011977763?"
```

**Output:**
```
💬 You: What is the status of account A-011977763?
🤖 Agent: The account A-011977763 (Dimod Account) is currently ACTIVE. It has a pending balance of 50 points...

🔧 Tools used: 1
   - fetch_account_details
```

---

### 3. Send Message (Auto-create Session)

If you don't provide a session ID, one is created automatically:

```bash
python main.py --message "Tell me about account A-011977763"
```

**Output:**
```
✅ Created new session: 7c3b9f2a-8e4d-4a5f-b6c7-9d8e7f6a5b4c
💬 You: Tell me about account A-011977763
🤖 Agent: The account A-011977763...
```

---

## 💡 Complete CLI Examples

### Example 1: Basic Usage

```bash
# Step 1: Create session
SESSION_ID=$(python main.py --start-session | grep -oP '(?<=: )[a-f0-9-]+')

# Step 2: Use the session
python main.py --session-id $SESSION_ID --message "What is the status of account A-011977763?"
```

### Example 2: Multi-turn Conversation

```bash
# Create session
SESSION_ID=$(python main.py --start-session | grep -oP '(?<=: )[a-f0-9-]+')

# First message
python main.py --session-id $SESSION_ID --message "Tell me about account A-011977763"

# Follow-up (agent remembers context!)
python main.py --session-id $SESSION_ID --message "What facilities does it have?"

# Another follow-up
python main.py --session-id $SESSION_ID --message "Show me the active facility"
```

### Example 3: Account Query

```bash
python main.py --message "What is the status of account A-011977763?"
```

### Example 4: Facility Query

```bash
python main.py --message "Show me details for facility F-015766066"
```

### Example 5: Save Note

```bash
python main.py --message "Save a note for user123: Meeting completed at 3pm"
```

### Example 6: Fetch Notes

```bash
python main.py --message "Show me my last 5 notes for user123"
```

---

## 🔄 CLI vs API Comparison

| Feature | CLI | API |
|---------|-----|-----|
| **Usage** | Terminal commands | HTTP requests |
| **Best For** | Quick testing, scripts | Production, frontends |
| **Session** | Manual ID management | Automatic via API |
| **Output** | Terminal text | JSON responses |
| **Automation** | Shell scripts | Any HTTP client |

---

## 🛠️ CLI Arguments Reference

```bash
python main.py [OPTIONS]

Options:
  --api               Start API server (default if no CLI args)
  --start-session     Create new session (CLI mode)
  --session-id ID     Session ID to use (CLI mode)
  --message "text"    Message to send (CLI mode)
  --user-id ID        User ID for session (CLI mode)
  -h, --help          Show help message
```

---

## 📝 Shell Script Examples

### Auto Test Script

```bash
#!/bin/bash

echo "Creating session..."
SESSION_ID=$(python main.py --start-session | grep -oP '(?<=: )[a-f0-9-]+')

echo "Session: $SESSION_ID"
echo ""

echo "Testing account query..."
python main.py --session-id $SESSION_ID \
  --message "What is the status of account A-011977763?"

echo ""
echo "Testing follow-up..."
python main.py --session-id $SESSION_ID \
  --message "What facilities does it have?"
```

### Batch Processing

```bash
#!/bin/bash

# Process multiple queries
for query in \
  "Account A-011977763 status?" \
  "Facility F-015766066 details?" \
  "Save note for user123: Batch test complete"
do
  echo "Query: $query"
  python main.py --message "$query"
  echo "---"
done
```

---

## 🎯 Use Cases

### Development & Testing
```bash
# Quick test during development
python main.py --message "Test query"
```

### Automation Scripts
```bash
# Scheduled task
python main.py --message "Save daily report for user123"
```

### CI/CD Pipeline
```bash
# Integration tests
python main.py --message "Test account A-011977763" || exit 1
```

### Data Migration
```bash
# Bulk operations
for account in $(cat accounts.txt); do
  python main.py --message "Process account $account"
done
```

---

## 🐛 Troubleshooting

### "OPENAI_API_KEY not found"
**Solution:** Create `.env` file with your API key
```bash
echo "OPENAI_API_KEY=sk-your-key" > .env
```

### Session not found
**Solution:** Create session first or let it auto-create
```bash
python main.py --start-session
```

### No response
**Solution:** Check your OpenAI API key and network
```bash
# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## ⚡ Pro Tips

1. **Save Session ID**: Store in variable for multiple commands
   ```bash
   export SESSION_ID=$(python main.py --start-session | grep -oP '(?<=: )[a-f0-9-]+')
   ```

2. **Use Aliases**: Create shortcuts
   ```bash
   alias agent="python main.py --message"
   agent "Your query here"
   ```

3. **Pipe Output**: Process responses
   ```bash
   python main.py --message "Query" | grep "keyword"
   ```

4. **Background Jobs**: Run in background
   ```bash
   python main.py --message "Long query" &
   ```

---

## 📊 CLI vs API Quick Reference

**Start CLI Mode:**
```bash
python main.py --start-session
python main.py --message "query"
```

**Start API Mode:**
```bash
python main.py
# or
python main.py --api
```

**Check Mode:**
- If you see server starting → API mode ✅
- If you see "Session created" → CLI mode ✅

---

## 🎉 You Now Have CLI Support!

Your agent works in **TWO modes**:

1. **API Mode** - For production, frontends, integrations
2. **CLI Mode** - For testing, scripts, automation

**Both modes use the same LangGraph agent!** 🚀

---

*CLI makes testing super easy!*
