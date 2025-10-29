# 🚀 Quick Start Guide

Get your Supervisor Agent running in 5 minutes!

## Prerequisites

- Python 3.8+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Step 1: Install Dependencies (1 minute)

```bash
cd langgraph-supervisor
pip install -r requirements.txt --break-system-packages
```

## Step 2: Configure API Key (30 seconds)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

Or directly:
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

## Step 3: Start Server (30 seconds)

```bash
python main.py
```

✅ Server running at: **http://localhost:8000**  
📚 API Docs: **http://localhost:8000/docs**

## Step 4: Test It! (2 minutes)

### Option A: Postman
1. Open Postman
2. Import `tests/postman_collection.json`
3. Run "Create Session"
4. Run "Chat" requests

### Option B: Test Script
```bash
cd tests
./test_script.sh
```

### Option C: Quick cURL Test
```bash
# Health check
curl http://localhost:8000/health

# Create session
SESSION_ID=$(curl -s -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user123"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"message\":\"What is the status of account A-011977763?\"}"
```

## 🎉 You're Done!

Your agent is now:
- ✅ Running with LangGraph
- ✅ Using OpenAI GPT-4
- ✅ Ready to chat
- ✅ Managing sessions
- ✅ Using 4 specialized tools

## Next Steps

- 📖 Read the [API Reference](API_REFERENCE.md)
- 🏗️ Check [Architecture docs](ARCHITECTURE.md)
- 🧪 Explore [Testing guide](../tests/README.md)
- 📁 Review directory READMEs for details

## Common Issues

**"OPENAI_API_KEY not found"**
→ Create .env file with your API key

**"Port 8000 already in use"**
→ Change port in .env: `PORT=8001`

**"Module not found"**
→ Install dependencies: `pip install -r requirements.txt`

Happy building! 🚀
