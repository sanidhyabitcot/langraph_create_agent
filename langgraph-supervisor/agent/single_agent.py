"""
Single Agent
Main agent using LangGraph for state management and tool orchestration
"""
import os
import logging
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from agent.tools import ALL_TOOLS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SingleAgent:
    """
    Single Agent that manages conversation and tool usage
    Uses LangGraph for state management
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4"):
        """
        Initialize the single agent
        
        Args:
            api_key: OpenAI API key (defaults to env variable)
            model_name: OpenAI model to use
        """
        try:
            logger.info(f"Initializing SingleAgent with model: {model_name}")
            
            # Set API key
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
            elif "OPENAI_API_KEY" not in os.environ:
                raise ValueError("OPENAI_API_KEY must be provided or set in environment")
            
            # Initialize OpenAI model
            self.model = ChatOpenAI(
                model=model_name,
                temperature=0.7
            )
            
            # System prompt for the agent with structured output requirement
            self.system_prompt = """You are a helpful AI assistant with access to specialized tools.

Your capabilities:
1. Fetch account details - Retrieve account information, balances, rewards, and facilities
2. Fetch facility details - Get facility information, licenses, and agreements  
3. Save notes - Store meeting minutes or notes for users
4. Fetch notes - Retrieve saved notes by user, date, or recent history

CRITICAL REQUIREMENT - STRUCTURED OUTPUT:
You MUST respond in TWO formats:
1. Natural Language Response - A friendly, conversational response
2. Structured JSON Output - A well-organized JSON structure with the data

Guidelines:
- Be conversational and professional in natural language
- Use tools when needed to answer user questions
- Maintain context from previous messages in the conversation
- Provide clear, structured responses
- When saving notes, confirm what was saved
- When fetching data, present it in a user-friendly format
- If you need more information, ask the user
- ALWAYS structure your response data in JSON format

For structured output, use this format:
{
  "intent": "account_query|facility_query|note_operation|general",
  "entities": {
    "account_id": "string or null",
    "facility_id": "string or null",
    "user_id": "string or null"
  },
  "data": {
    // Extracted data from tools or response
  },
  "metadata": {
    "confidence": "high|medium|low",
    "tools_used": ["tool_names"]
  }
}

ALWAYS do the following when certain IDs are provided:
- If an account_id is present, you MUST call `fetch_account_details(account_id)` and then:
  - set card_key to `account_overview`
  - include the returned account object in `account_overview` as a single-item list
  - summarize the key fields in the natural language final_response as a bullet list
- If a facility_id is present, you MUST call `fetch_facility_details(facility_id)` and set card_key to `facility_overview` similarly.

Always strive to be helpful, accurate, and efficient in your responses."""
            
            # Initialize checkpointer for short-term memory
            self.checkpointer = InMemorySaver()
            
            # Create the agent using LangChain v1's create_agent with checkpointer
            self.agent = create_agent(
                model=self.model,
                tools=ALL_TOOLS,
                system_prompt=self.system_prompt,
                checkpointer=self.checkpointer
            )
            
            logger.info("SingleAgent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing SingleAgent: {str(e)}", exc_info=True)
            raise
    
    def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        account_id: Optional[str] = None,
        facility_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message with conversation context
        
        Args:
            user_message: The current user message
            conversation_history: List of previous messages
            account_id: Optional account ID for context
            facility_id: Optional facility ID for context
            conversation_id: Conversation ID for short-term memory
            
        Returns:
            Dictionary with flat structure matching expected format
        """
        try:
            logger.info(f"Processing message in conversation: {conversation_id}")
            logger.info(f"Message: {user_message[:100]}...")
            
            # Build messages list with history
            messages = conversation_history.copy()
            
            # Add context if IDs provided
            context_message = ""
            if account_id:
                context_message += f"Context: User is asking about account_id: {account_id}. "
            if facility_id:
                context_message += f"Context: User is asking about facility_id: {facility_id}. "
            
            if context_message:
                user_message = context_message + user_message
            
            messages.append({"role": "user", "content": user_message})
            
            # Prepare config with thread_id for short-term memory
            config = {}
            if conversation_id:
                config = {"configurable": {"thread_id": conversation_id}}
            
            # Invoke the agent
            result = self.agent.invoke({"messages": messages}, config)
            
            # Extract the assistant's response
            assistant_message = ""
            tool_calls = []
            structured_response = None
            
            if "messages" in result:
                # Get the last message from the agent
                for msg in reversed(result["messages"]):
                    if hasattr(msg, "content") and msg.content:
                        assistant_message = msg.content
                        break
                    elif isinstance(msg, dict) and msg.get("content"):
                        assistant_message = msg["content"]
                        break
                
                # Extract tool usage information
                for msg in result["messages"]:
                    if hasattr(msg, "additional_kwargs"):
                        if "tool_calls" in msg.additional_kwargs:
                            for tool_call in msg.additional_kwargs["tool_calls"]:
                                tool_calls.append({
                                    "tool": tool_call.get("function", {}).get("name"),
                                    "arguments": tool_call.get("function", {}).get("arguments")
                                })
            
            # Extract structured response if available
            if "structured_response" in result:
                structured_response = result["structured_response"]
                logger.info(f"Structured response received: {structured_response}")
            
            # Determine card_key and extract data based on tools used
            card_key, data_dict = self._extract_data_from_tools(
                tool_calls=tool_calls,
                account_id=account_id,
                facility_id=facility_id,
                structured_response=structured_response,
                user_message=user_message
            )

            # Intent heuristics based on user query
            user_lower = (user_message or "").lower()
            is_overview = any(k in user_lower for k in [
                "overview", "show account", "account summary", "summary"
            ])
            is_specific = any(k in user_lower for k in [
                "how many", "points", "tier", "rewards", "free vial"
            ])
            is_facility = "facility" in user_lower or "facilities" in user_lower

            # Card selection rules
            if account_id:
                if is_overview and data_dict.get("account_overview"):
                    card_key = "account_overview"
                elif is_specific:
                    # For specific questions we surface 'other' card and hide overview payload
                    card_key = "other"
                    data_dict["account_overview"] = []
            if (facility_id or is_facility) and data_dict.get("facility_overview"):
                if is_overview or is_facility:
                    card_key = "facility_overview"
            
            # Optionally enrich natural language summary deterministically from structured data
            nl_response = assistant_message or "I'm here to help! How can I assist you?"
            user_lower = (user_message or "").lower()
            if data_dict.get("account_overview") and len(data_dict["account_overview"]) > 0:
                acc_obj = data_dict["account_overview"][0]
                if any(k in user_lower for k in ["reward", "loyalty", "points", "tier", "free vial", "free vials"]):
                    nl_response = self._build_rewards_summary(acc_obj)
                elif any(k in user_lower for k in ["overview", "show account", "account summary", "summary"]):
                    nl_response = self._build_account_summary(acc_obj)
            elif data_dict.get("facility_overview") and len(data_dict["facility_overview"]) > 0:
                nl_response = self._build_facility_summary(data_dict["facility_overview"][0])
            elif any(k in user_lower for k in ["note", "notes"]):
                # Build note summary if available
                notes = data_dict.get("note_overview") or []
                nl_response = self._build_notes_summary(notes)

            # Build final response with both natural language and structured data
            response = {
                "final_response": nl_response,
                "card_key": card_key,
                "tool_calls": tool_calls,
                "success": True,
                **data_dict
            }
            
            logger.info(f"Message processed successfully. Card key: {card_key}")
            return response
            
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
    
    def _extract_data_from_tools(
        self,
        tool_calls: List[Dict[str, Any]],
        account_id: Optional[str] = None,
        facility_id: Optional[str] = None,
        structured_response: Optional[Any] = None,
        user_message: Optional[str] = None
    ) -> tuple[str, Dict[str, Any]]:
        """Extract data from tool results and determine card_key"""
        from services import account_service, facility_service, notes_service
        
        try:
            logger.info("Extracting data from tools and structured response")
            
            # Initialize response structure
            data_dict = {
                "account_overview": None,
                "rewards_overview": None,
                "facility_overview": None,
                "order_overview": None,
                "note_overview": []
            }
            
            card_key = "general"
            
            # Use structured response if available
            if structured_response:
                if hasattr(structured_response, 'card_key'):
                    card_key = structured_response.card_key
                    logger.info(f"Card key from structured response: {card_key}")
                if hasattr(structured_response, 'data') and structured_response.data:
                    data_dict.update(structured_response.data)
            
            # Check which tools were used and fetch data
            for tool_call in tool_calls:
                tool_name = tool_call.get("tool")
                logger.info(f"Processing tool: {tool_name}")
                
                if tool_name == "fetch_account_details":
                    result = account_service.get_account_details(account_id if account_id else "A-011977763")
                    if result.get("success"):
                        account_data = result.get("data")
                        data_dict["account_overview"] = [account_data]
                        card_key = "account_overview"
                        logger.info("Account data fetched successfully")
                
                elif tool_name == "fetch_facility_details":
                    result = facility_service.get_facility_details(facility_id if facility_id else "F-015766066")
                    if result.get("success"):
                        facility_data = result.get("data")
                        data_dict["facility_overview"] = [facility_data]
                        card_key = "facility_overview"
                        logger.info("Facility data fetched successfully")
                
                elif tool_name == "fetch_notes":
                    result = notes_service.fetch_notes(last_n=5)
                    if result.get("success"):
                        data_dict["note_overview"] = result.get("data", [])
                        card_key = "note_overview"
                        logger.info("Notes fetched successfully")
            
            # Fallbacks: if IDs were supplied but the LLM did not call tools, fetch directly
            if account_id and data_dict.get("account_overview") is None:
                result = account_service.get_account_details(account_id)
                if result.get("success"):
                    data_dict["account_overview"] = [result.get("data")]
                    card_key = "account_overview"
                    logger.info("Account data fetched by fallback")
            if facility_id and data_dict.get("facility_overview") is None:
                result = facility_service.get_facility_details(facility_id)
                if result.get("success"):
                    data_dict["facility_overview"] = [result.get("data")]
                    card_key = "facility_overview"
                    logger.info("Facility data fetched by fallback")

            # Facility intent without facility_id: derive from account
            user_lower = (user_message or "").lower()
            if ("facility" in user_lower or "facilities" in user_lower) and not facility_id:
                # If we have account data, surface its facilities
                try:
                    if not data_dict.get("facility_overview"):
                        from services import facility_service as fac_svc
                        fac_all = fac_svc.get_all_facilities()
                        if fac_all.get("success"):
                            fac_list = fac_all["data"].get("facility_overview", [])
                            filtered = [f for f in fac_list if f.get("account_id") == (account_id or "")]
                            if filtered:
                                data_dict["facility_overview"] = filtered
                                card_key = "facility_overview"
                                logger.info("Facility data derived from account context")
                except Exception as fe:
                    logger.error(f"Error deriving facility overview: {fe}")

            # Notes intent: derive parameters and fetch via service when needed
            if ("note" in user_lower or "notes" in user_lower):
                try:
                    import re
                    m = re.search(r"(last|first)\s+(\d+)", user_lower)
                    order = "desc"
                    last_n = 5
                    if m:
                        pos, num = m.group(1), int(m.group(2))
                        last_n = num
                        if pos == "first":
                            order = "asc"
                    # date extraction like 29/10/2025 or 2025-10-29
                    date = None
                    mdate = re.search(r"(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})", user_lower)
                    if mdate:
                        date = mdate.group(1)
                    from services import notes_service as ns
                    result = ns.fetch_notes(user_id=None, date=date, last_n=last_n, order=order)
                    if result.get("success"):
                        data_dict["note_overview"] = result.get("data", [])
                        card_key = "note_overview"
                        logger.info("Notes fetched via fallback intent handler")
                except Exception as ne:
                    logger.error(f"Error fetching notes: {ne}")

            logger.info(f"Final card key: {card_key}")
            return card_key, data_dict
            
        except Exception as e:
            logger.error(f"Error extracting data from tools: {str(e)}", exc_info=True)
            return "general", {
                "account_overview": None,
                "rewards_overview": None,
                "facility_overview": None,
                "order_overview": None,
                "note_overview": []
            }
    
    def chat(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simplified chat interface
        """
        try:
            logger.info("Chat interface called")
            if conversation_history is None:
                conversation_history = []
            
            return self.process_message(
                user_message,
                conversation_history,
                conversation_id=conversation_id
            )
            
        except Exception as e:
            logger.error(f"Error in chat interface: {str(e)}", exc_info=True)
            return {
                "final_response": f"I encountered an error: {str(e)}",
                "card_key": "error",
                "success": False,
                "error": str(e)
            }

    def _build_account_summary(self, acc: Dict[str, Any]) -> str:
        lines = []
        lines.append("Here is a summary of your account:\n")
        lines.append(f"- Account Name: {acc.get('name','')}\n")
        lines.append(f"- Status: {acc.get('status','')}\n")
        lines.append(f"- Account ID: {acc.get('account_id','')}\n")
        address = ", ".join(filter(None, [acc.get('address_line1',''), acc.get('address_city',''), acc.get('address_state',''), acc.get('address_postal_code','')]))
        lines.append(f"- Address: {address}\n")
        lines.append(f"- Pricing Model: {acc.get('pricing_model','')}\n\n")
        lines.append("Loyalty & Rewards:\n")
        lines.append(f"- Current Loyalty Tier: {acc.get('current_tier','')} (next tier: {acc.get('next_tier','')}, {acc.get('points_to_next_tier',0)} points needed)\n")
        lines.append(f"- Loyalty Points Balance: {acc.get('points_earned_this_quarter',0)} (pending: {acc.get('pending_balance',0)})\n")
        lines.append(f"- Free Vials Available: {acc.get('free_vials_available',0)}\n")
        lines.append(f"- Rewards Redeemed Toward Next Free Vial: {acc.get('rewards_redeemed_towards_next_free_vial', acc.get('rewards_redeemed_towards_next_free_vial', acc.get('rewards_redeemed_towards_next_free_vial', 0)))}\n\n")
        lines.append("Other Details:\n")
        lines.append(f"- Evolux Level: {acc.get('evolux_level','')}\n")
        lines.append(f"- Reward Program Opt-in Status: {acc.get('rewards_status','')}\n\n")
        lines.append("Let me know if you need more detailed information or have other questions!")
        return "".join(lines)

    def _build_rewards_summary(self, acc: Dict[str, Any]) -> str:
        tier = acc.get('current_tier','')
        next_tier = acc.get('next_tier','')
        to_next = acc.get('points_to_next_tier',0)
        balance = acc.get('points_earned_this_quarter',0)
        pending = acc.get('pending_balance',0)
        free_vials = acc.get('free_vials_available',0)
        required_for_free = acc.get('rewards_required_for_next_free_vial',0)
        redeemed_toward_free = acc.get('rewards_redeemed_towards_next_free_vial',0)
        rewards_status = acc.get('rewards_status','')
        lines = []
        lines.append("Here are your current loyalty & rewards details:\n\n")
        lines.append(f"- Current Tier: {tier} (next tier: {next_tier}, {to_next} points needed)\n")
        lines.append(f"- Points Balance: {balance} (pending: {pending})\n")
        lines.append(f"- Free Vials Available: {free_vials}\n")
        lines.append(f"- Progress to Next Free Vial: {redeemed_toward_free}/{required_for_free}\n")
        lines.append(f"- Rewards Opt-in Status: {rewards_status}\n")
        return "".join(lines)

    def _build_facility_summary(self, fac: Dict[str, Any]) -> str:
        lines = []
        lines.append("Here is a summary of the facility:\n")
        lines.append(f"- Facility Name: {fac.get('name','')}\n")
        lines.append(f"- Status: {fac.get('status','')}\n")
        lines.append(f"- Facility ID: {fac.get('id','')}\n")
        lines.append(f"- Medical License: {fac.get('medical_license_number','')} ({fac.get('medical_license_state','')})\n")
        lines.append(f"- Agreement Status: {fac.get('agreement_status','')}\n")
        lines.append(f"- Account: {fac.get('account_name','')} ({fac.get('account_id','')})\n")
        return "".join(lines)

    def _build_notes_summary(self, notes: List[Dict[str, Any]]) -> str:
        if not notes:
            return "No notes found for your query."
        lines = ["Here are your notes:\n\n"]
        for n in notes:
            ts = n.get('created_at') or n.get('updated_at') or ''
            lines.append(f"- ({ts}) {n.get('content','')}\n")
        return "".join(lines)


# Global instance (will be initialized in main.py)
_agent_instance = None


def get_agent() -> SingleAgent:
    """Get the global agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = SingleAgent()
    return _agent_instance


def initialize_agent(api_key: Optional[str] = None, model_name: str = "gpt-4"):
    """Initialize the global agent instance"""
    global _agent_instance
    _agent_instance = SingleAgent(api_key=api_key, model_name=model_name)
    return _agent_instance


