#!/bin/bash

# Supervisor Agent - Automated Test Script
# Tests all endpoints with LangGraph agent

BASE_URL="http://localhost:8000"
COLOR_GREEN='\033[0;32m'
COLOR_BLUE='\033[0;34m'
COLOR_YELLOW='\033[1;33m'
COLOR_NC='\033[0m'

echo -e "${COLOR_BLUE}╔════════════════════════════════════════════════╗${COLOR_NC}"
echo -e "${COLOR_BLUE}║   Supervisor Agent Test Script (LangGraph)    ║${COLOR_NC}"
echo -e "${COLOR_BLUE}╚════════════════════════════════════════════════╝${COLOR_NC}"
echo ""

# 1. Health Check
echo -e "${COLOR_YELLOW}[1] Health Check...${COLOR_NC}"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""
echo ""

# 2. Create Session
echo -e "${COLOR_YELLOW}[2] Creating Session...${COLOR_NC}"
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/sessions" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}')

SESSION_ID=$(echo $SESSION_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")
echo "Session ID: $SESSION_ID"
echo "$SESSION_RESPONSE" | python3 -m json.tool
echo ""
echo ""

# 3. Chat - Account Query
echo -e "${COLOR_YELLOW}[3] Chat - Account Query...${COLOR_NC}"
echo "Message: 'What is the status of account A-011977763?'"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"What is the status of account A-011977763?\"
  }" | python3 -m json.tool
echo ""
echo ""

# 4. Chat - Follow-up (tests memory)
echo -e "${COLOR_YELLOW}[4] Chat - Follow-up Question (tests memory)...${COLOR_NC}"
echo "Message: 'What facilities does it have?'"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"What facilities does it have?\"
  }" | python3 -m json.tool
echo ""
echo ""

# 5. Chat - Save Note
echo -e "${COLOR_YELLOW}[5] Chat - Save Note...${COLOR_NC}"
echo "Message: 'Save a note for user123: Test completed successfully'"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"Save a note for user123: Test completed successfully on $(date)\"
  }" | python3 -m json.tool
echo ""
echo ""

# 6. Chat - Fetch Notes
echo -e "${COLOR_YELLOW}[6] Chat - Fetch Notes...${COLOR_NC}"
echo "Message: 'Show me my last 3 notes'"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"Show me my last 3 notes\"
  }" | python3 -m json.tool
echo ""
echo ""

# 7. Get Conversation History
echo -e "${COLOR_YELLOW}[7] Get Conversation History...${COLOR_NC}"
curl -s "$BASE_URL/sessions/$SESSION_ID/history?include_metadata=true" | python3 -m json.tool
echo ""
echo ""

# 8. List Sessions
echo -e "${COLOR_YELLOW}[8] List All Sessions...${COLOR_NC}"
curl -s "$BASE_URL/sessions" | python3 -m json.tool
echo ""
echo ""

echo -e "${COLOR_GREEN}╔════════════════════════════════════════════════╗${COLOR_NC}"
echo -e "${COLOR_GREEN}║   Test Complete! ✓                            ║${COLOR_NC}"
echo -e "${COLOR_GREEN}║   Session ID: $SESSION_ID${COLOR_NC}"
echo -e "${COLOR_GREEN}╚════════════════════════════════════════════════╝${COLOR_NC}"
