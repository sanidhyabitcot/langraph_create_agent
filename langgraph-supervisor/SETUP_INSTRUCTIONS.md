# Setup Instructions

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

### Option A: Edit .env file

The `.env` file has been created for you. Simply:

1. Open `langgraph-supervisor/.env` in any text editor
2. Replace `your-openai-api-key-here` with your actual OpenAI API key
3. Save the file

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY-HERE
OPENAI_MODEL=gpt-4

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Logging Configuration
LOG_LEVEL=INFO
```

### Option B: Set environment variable

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-proj-YOUR-KEY-HERE"

# Windows CMD
set OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE

# Linux/Mac
export OPENAI_API_KEY="sk-proj-YOUR-KEY-HERE"
```

## Step 3: Verify Setup

```bash
cd langgraph-supervisor
python -c "from agent import get_agent; print('✅ Setup complete!')"
```

You should see:
```
INFO:services.account_service:Initializing AccountService
...
✅ Setup complete!
```

## Step 4: Start the Server

```bash
python main.py
```

You should see:
```
🚀 Starting Supervisor Agent API
📍 Server: http://0.0.0.0:8000
📚 Docs: http://0.0.0.0:8000/docs
```

## Step 5: Test the API

### Create a Session

```bash
curl -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test@example.com"}'
```

### Send a Chat Message

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "show account overview",
    "user_id": "test@example.com",
    "account_id": "A-011977763",
    "conversation_id": "YOUR_SESSION_ID_FROM_ABOVE"
  }'
```

## Troubleshooting

### Error: OPENAI_API_KEY not found

**Solution:** Edit `.env` file and add your API key:
```env
OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE
```

### Error: Module not found

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Port already in use

**Solution:** Change port in `.env`:
```env
PORT=8001
```

## Next Steps

- Read [QUICK_START.md](QUICK_START.md) for quick testing
- Read [HOW_TO_TEST.md](HOW_TO_TEST.md) for detailed testing guide
- Read [README.md](README.md) for complete documentation

