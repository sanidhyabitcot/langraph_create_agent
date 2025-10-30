"""
Main Application
Entry point for the LangGraph Single Agent API
Supports both API server and CLI modes
"""
import os
import sys
import argparse
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from api import router
from agent import initialize_agent, get_agent
from services import session_service


# Load environment variables
load_dotenv()

# Lifespan handler to avoid deprecated on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize agent
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        print("WARNING: OPENAI_API_KEY not found in environment. Set it in .env to enable the agent.")
    else:
        try:
            initialize_agent(api_key=api_key, model_name=model_name)
            print("SUCCESS: Agent initialized")
            print(f"Model: {model_name}")
        except Exception as e:
            print(f"ERROR: Error initializing agent: {e}")
    # Yield to run app
    yield
    # Shutdown
    print("Shutting down Single Agent API")


# Initialize FastAPI app with lifespan
app = FastAPI(
        title="LangGraph Single Agent API",
    description="LangGraph + OpenAI Multi-Tool Agentic System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)


def run_cli(args):
    """Run in CLI mode"""
    # Initialize agent
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in .env file")
        sys.exit(1)
    
    initialize_agent(api_key=api_key, model_name=model_name)
    agent = get_agent()
    
    if args.start_session:
        # Create new session
        session = session_service.create_session(user_id=args.user_id)
        print(f"SUCCESS: Session created: {session.session_id}")
        if args.user_id:
            print(f"User ID: {args.user_id}")
        return
    
    if args.message:
        # Handle message
        session_id = args.session_id
        
        # If no session provided, create one
        if not session_id:
            session = session_service.create_session(user_id=args.user_id)
            session_id = session.session_id
            print(f"SUCCESS: Created new session: {session_id}")
        
        # Verify session exists
        session = session_service.get_session(session_id)
        if not session:
            print(f"ERROR: Session '{session_id}' not found")
            sys.exit(1)
        
        print(f"You: {args.message}")
        print("Agent: ", end="", flush=True)
        
        # Get conversation history
        conversation_history = session_service.get_conversation_history(session_id)
        
        # Get user_id from session if available
        user_id = session.user_id if session else args.user_id
        
        # Process message (support memory via conversation_id)
        result = agent.process_message(
            args.message,
            conversation_history,
            user_id=user_id,
            conversation_id=session_id,
        )
        
        # Save to session
        session_service.add_message(session_id, "user", args.message)
        session_service.add_message(session_id, "assistant", result.get("final_response", ""))
        
        # Print response
        print(result.get("final_response", ""))
        
        # Print structured output if verbose
        if args.verbose:
            print("\nStructured Output:")
            import json
            # Show key structured fields
            summary = {
                "card_key": result.get("card_key"),
                "account_overview": result.get("account_overview"),
                "facility_overview": result.get("facility_overview"),
                "note_overview": result.get("note_overview"),
            }
            print(json.dumps(summary, indent=2))
        
        # Print tool usage if any
        if result.get("tool_calls"):
            print(f"\nTools used: {len(result['tool_calls'])}")
            for tool in result["tool_calls"]:
                print(f"   - {tool.get('tool', 'unknown')}")
        
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="LangGraph Single Agent - API Server or CLI Mode"
    )
    
    # Mode selection
    parser.add_argument(
        "--api",
        action="store_true",
        help="Start FastAPI server (default mode)"
    )
    
    # CLI mode arguments
    parser.add_argument(
        "--start-session",
        action="store_true",
        help="Create a new session (CLI mode)"
    )
    parser.add_argument(
        "--session-id",
        type=str,
        help="Session ID to use (CLI mode)"
    )
    parser.add_argument(
        "--message",
        type=str,
        help="Message to send to agent (CLI mode)"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        help="User ID for session (CLI mode)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show structured output in CLI mode"
    )
    
    args = parser.parse_args()
    
    # Determine mode
    if args.start_session or args.message:
        # CLI mode
        run_cli(args)
    else:
        # API mode (default)
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8000))
        
        print("Starting Single Agent API")
        print(f"Server: http://{host}:{port}")
        print(f"Docs: http://{host}:{port}/docs")
        print(f"ReDoc: http://{host}:{port}/redoc")
        print()
        
        # Run the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
