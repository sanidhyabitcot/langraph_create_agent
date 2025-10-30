"""
Single Agent
Main agent using LangGraph for state management and tool orchestration
Uses structured output and agentic decision-making
"""
import os
import logging
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from agent.tools import ALL_TOOLS
from api.response_models import AgentOutput

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SingleAgent:
    """
    Single Agent that manages conversation and tool usage
    Uses LangGraph for state management
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o-mini"):
        """
        Initialize the single agent with structured output
        
        Args:
            api_key: OpenAI API key (defaults to env variable)
            model_name: OpenAI model to use (defaults to gpt-4o-mini)
        """
        try:
            logger.info(f"Initializing SingleAgent with model: {model_name}")
            
            # Set API key
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
            elif "OPENAI_API_KEY" not in os.environ:
                raise ValueError("OPENAI_API_KEY must be provided or set in environment")
            
            # Initialize OpenAI model - structured output will be handled by create_agent via response_format
            self.model = ChatOpenAI(
                model=model_name,
                temperature=0.7
            )
            
            # System prompt - guides agent without hardcoded rules
            self.system_prompt = """You are a helpful AI assistant with access to specialized tools.

Your capabilities:
1. Fetch account details - Retrieve account information, balances, rewards, and facilities
2. Fetch facility details - Get facility information, licenses, and agreements  
3. Save notes - Store meeting minutes or notes for users
4. Fetch notes - Retrieve saved notes by user, date, or recent history

IMPORTANT GUIDELINES:
- Always respond to the user's query with a helpful, natural language response in final_response
- DO NOT simply repeat or echo the user's input - provide meaningful information
- Use tools intelligently when needed - decide which tools to call based on the query
- Account ID, facility ID, and user ID are available in the config - extract them when needed for tools
- When a user asks "show account overview" or similar, you MUST:
  1. Call the appropriate tool (e.g., fetch_account_details) to get the data
  2. Extract the relevant information from the tool response
  3. Populate the account_overview field with the structured data
  4. Set card_key to "account_overview" 
  5. Provide a helpful summary in final_response explaining what was retrieved

CARD_KEY SELECTION RULES (read the AgentOutput.card_key field description for details):
- "account_overview": Use when user explicitly requests COMPLETE/FULL account information
- "facility_overview": Use when user explicitly requests COMPLETE/FULL facility information
- "rewards_overview": Use when user explicitly requests COMPLETE/FULL rewards information
- "order_overview": Use when user explicitly requests COMPLETE/FULL order information
- "note_overview": Use when user requests to FETCH/LIST/DISPLAY/SHOW notes
- "other": Use for specific single-field questions, greetings, follow-ups, or analysis requests

When calling tools:
- Extract account_id, facility_id, or user_id from the config if needed
- Process the tool results and populate the appropriate overview fields in structured format
- Provide a clear, helpful summary in final_response

Always be helpful, accurate, and efficient. Make tool calls when you need data to answer the user's question."""
            
            # Initialize checkpointer for short-term memory
            self.checkpointer = InMemorySaver()
            
            # Create the agent using LangChain v1's create_agent with response_format
            # This automatically selects ProviderStrategy for OpenAI models or ToolStrategy for others
            # The structured response will be in result["structured_response"]
            self.agent = create_agent(
                model=self.model,
                tools=ALL_TOOLS,
                system_prompt=self.system_prompt,
                checkpointer=self.checkpointer,
                response_format=AgentOutput  # Pass schema type directly - auto-selects best strategy
            )
            
            logger.info("SingleAgent initialized successfully with structured output")
            
        except Exception as e:
            logger.error(f"Error initializing SingleAgent: {str(e)}", exc_info=True)
            raise
    
    def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        account_id: Optional[str] = None,
        facility_id: Optional[str] = None,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message with conversation context
        
        Args:
            user_message: The current user message
            conversation_history: List of previous messages
            account_id: Optional account ID (passed via config)
            facility_id: Optional facility ID (passed via config)
            user_id: Optional user ID (passed via config)
            conversation_id: Conversation ID for short-term memory
            
        Returns:
            Dictionary with flat structure matching expected format
        """
        try:
            logger.info(f"Processing message in conversation: {conversation_id}")
            logger.info(f"Message: {user_message[:100]}...")
            
            # Build messages list with history
            messages = conversation_history.copy()
            messages.append({"role": "user", "content": user_message})
            
            # Prepare config with thread_id and IDs for tools
            config = {"configurable": {}}
            if conversation_id:
                config["configurable"]["thread_id"] = conversation_id
            if account_id:
                config["configurable"]["account_id"] = account_id
            if facility_id:
                config["configurable"]["facility_id"] = facility_id
            if user_id:
                config["configurable"]["user_id"] = user_id
            
            logger.info(f"Config: account_id={account_id}, facility_id={facility_id}, user_id={user_id}")
            
            # Invoke the agent - structured output will be in result["structured_response"]
            result = self.agent.invoke({"messages": messages}, config)
            
            # Extract structured output from agent response
            # According to LangChain docs, structured output is in result["structured_response"]
            structured_output = None
            assistant_message = ""
            tool_calls = []
            
            # Check for structured_response in result (as per LangChain documentation)
            if "structured_response" in result:
                structured_output = result["structured_response"]
                if isinstance(structured_output, AgentOutput):
                    assistant_message = structured_output.final_response
                    logger.info(f"Found structured_response in result. Card key: {structured_output.card_key}")
            
            # Also extract messages for tool calls and fallback content
            if "messages" in result:
                # Get assistant message content for fallback
                for msg in reversed(result["messages"]):
                    if hasattr(msg, "content") and msg.content and not assistant_message:
                        if isinstance(msg.content, str):
                            assistant_message = msg.content
                    elif isinstance(msg, dict) and msg.get("content") and not assistant_message:
                        assistant_message = msg.get("content", "")
                    
                    if assistant_message:
                        break
                
                # Extract tool usage information
                for msg in result["messages"]:
                    if hasattr(msg, "additional_kwargs") and "tool_calls" in getattr(msg, "additional_kwargs", {}):
                        for tool_call in msg.additional_kwargs["tool_calls"]:
                            tool_calls.append({
                                "tool": tool_call.get("function", {}).get("name"),
                                "arguments": tool_call.get("function", {}).get("arguments")
                            })
                    elif isinstance(msg, dict) and msg.get("additional_kwargs", {}).get("tool_calls"):
                        for tool_call in msg["additional_kwargs"]["tool_calls"]:
                            tool_calls.append({
                                "tool": tool_call.get("function", {}).get("name"),
                                "arguments": tool_call.get("function", {}).get("arguments")
                            })
            
            # If we got structured output, use it directly
            if structured_output and isinstance(structured_output, AgentOutput):
                logger.info(f"Using structured output from agent. Card key: {structured_output.card_key}")
                # Convert AgentOutput to dict format
                response = {
                    "final_response": structured_output.final_response,
                    "card_key": structured_output.card_key,
                    "account_overview": [
                        acc.model_dump() for acc in (structured_output.account_overview or [])
                    ] if structured_output.account_overview else None,
                    "rewards_overview": [
                        rew.model_dump() for rew in (structured_output.rewards_overview or [])
                    ] if structured_output.rewards_overview else None,
                    "facility_overview": [
                        fac.model_dump() for fac in (structured_output.facility_overview or [])
                    ] if structured_output.facility_overview else None,
                    "order_overview": [
                        ord.model_dump() for ord in (structured_output.order_overview or [])
                    ] if structured_output.order_overview else None,
                    "note_overview": [
                        note.model_dump() for note in (structured_output.note_overview or [])
                    ],
                    "tool_calls": tool_calls,
                    "success": True
                }
                logger.info(f"Message processed successfully. Card key: {structured_output.card_key}")
                return response
            
            # Try parsing assistant_message as JSON and creating AgentOutput
            if assistant_message and not structured_output:
                try:
                    import json
                    # Try parsing as JSON
                    if isinstance(assistant_message, str):
                        parsed = json.loads(assistant_message)
                    else:
                        parsed = assistant_message
                    
                    if isinstance(parsed, dict):
                        # Try to create AgentOutput from parsed dict
                        structured_output = AgentOutput(**parsed)
                        logger.info("Parsed structured output from message content")
                        return {
                            "final_response": structured_output.final_response,
                            "card_key": structured_output.card_key,
                            "account_overview": [
                                acc.model_dump() for acc in (structured_output.account_overview or [])
                            ] if structured_output.account_overview else None,
                            "rewards_overview": [
                                rew.model_dump() for rew in (structured_output.rewards_overview or [])
                            ] if structured_output.rewards_overview else None,
                            "facility_overview": [
                                fac.model_dump() for fac in (structured_output.facility_overview or [])
                            ] if structured_output.facility_overview else None,
                            "order_overview": [
                                ord.model_dump() for ord in (structured_output.order_overview or [])
                            ] if structured_output.order_overview else None,
                            "note_overview": [
                                note.model_dump() for note in (structured_output.note_overview or [])
                            ],
                            "tool_calls": tool_calls,
                            "success": True
                        }
                except Exception as parse_error:
                    logger.debug(f"Could not parse structured output: {parse_error}")
            
            # Ultimate fallback - return basic response
            logger.warning("Structured output not found, using basic fallback response")
            return {
                "final_response": assistant_message or "I'm here to help! How can I assist you?",
                "card_key": "other",
                "account_overview": None,
                "rewards_overview": None,
                "facility_overview": None,
                "order_overview": None,
                "note_overview": [],
                "tool_calls": tool_calls,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return {
                "final_response": f"I encountered an error: {str(e)}",
                "card_key": "error",
                "account_overview": None,
                "rewards_overview": None,
                "facility_overview": None,
                "order_overview": None,
                "note_overview": [],
                "success": False,
                "error": str(e)
            }
    


# Global instance (will be initialized in main.py)
_agent_instance = None


def get_agent() -> SingleAgent:
    """Get the global agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = SingleAgent()
    return _agent_instance


def initialize_agent(api_key: Optional[str] = None, model_name: str = "gpt-4o-mini"):
    """Initialize the global agent instance"""
    global _agent_instance
    _agent_instance = SingleAgent(api_key=api_key, model_name=model_name)
    return _agent_instance


