"""
Complete System Test Script
Tests the supervisor agent with structured output and memory
"""
import asyncio
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agent import initialize_agent, get_agent
from services import session_service


async def test_complete_system():
    """Test the complete system with structured output and memory"""
    
    print("=" * 80)
    print("LangGraph Supervisor Agent - Complete System Test")
    print("=" * 80)
    
    # Initialize agent
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment")
        return
    
    try:
        print("\n1. Initializing agent...")
        initialize_agent(api_key=api_key, model_name="gpt-4")
        agent = get_agent()
        print("✅ Agent initialized successfully")
        
        # Create a session
        print("\n2. Creating session...")
        session = session_service.create_session(user_id="test@example.com")
        session_id = session.session_id
        print(f"✅ Session created: {session_id}")
        
        # Test message with account context
        print("\n3. Testing message with account context...")
        user_message = "show me my account details"
        
        print(f"\n💬 User: {user_message}")
        print("🤖 Agent: ", end="", flush=True)
        
        conversation_history = session_service.get_conversation_history(session_id)
        
        result = agent.process_message(
            user_message=user_message,
            conversation_history=conversation_history,
            account_id="A-011977763",
            conversation_id=session_id
        )
        
        print(result["final_response"])
        print(f"\n📊 Card Key: {result['card_key']}")
        print(f"📊 Success: {result['success']}")
        
        if result.get("account_overview"):
            print(f"📊 Account Data: {len(result['account_overview'])} item(s)")
        
        # Save to session
        session_service.add_message(session_id, "user", user_message)
        session_service.add_message(session_id, "assistant", result["final_response"])
        
        # Test second message with memory
        print("\n\n4. Testing follow-up message with memory...")
        follow_up = "what about my facilities?"
        
        print(f"\n💬 User: {follow_up}")
        print("🤖 Agent: ", end="", flush=True)
        
        conversation_history = session_service.get_conversation_history(session_id)
        
        result = agent.process_message(
            user_message=follow_up,
            conversation_history=conversation_history,
            account_id="A-011977763",
            conversation_id=session_id
        )
        
        print(result["final_response"])
        print(f"\n📊 Card Key: {result['card_key']}")
        print(f"📊 Success: {result['success']}")
        
        # Test facility query
        print("\n\n5. Testing facility query...")
        facility_query = "show facility F-015766066 details"
        
        print(f"\n💬 User: {facility_query}")
        print("🤖 Agent: ", end="", flush=True)
        
        conversation_history = session_service.get_conversation_history(session_id)
        
        result = agent.process_message(
            user_message=facility_query,
            conversation_history=conversation_history,
            facility_id="F-015766066",
            conversation_id=session_id
        )
        
        print(result["final_response"])
        print(f"\n📊 Card Key: {result['card_key']}")
        print(f"📊 Success: {result['success']}")
        
        if result.get("facility_overview"):
            print(f"📊 Facility Data: {len(result['facility_overview'])} item(s)")
        
        print("\n" + "=" * 80)
        print("✅ All tests completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_complete_system())

