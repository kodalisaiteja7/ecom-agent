"""
LangGraph-based conversational agent for e-commerce customer support.
Handles intent detection, state management, and CRUD operations with confirmation.
"""
from typing import TypedDict, Annotated, Literal, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json
import os

from tools import ALL_TOOLS


# ==================== STATE DEFINITION ====================

class AgentState(TypedDict):
    """State of the conversational agent."""
    messages: Annotated[list, "The conversation history"]
    detected_intent: Optional[str]  # CREATE, READ, UPDATE, DELETE, GENERAL
    pending_action: Optional[dict]  # Action awaiting confirmation
    awaiting_confirmation: bool  # Whether we're waiting for user confirmation
    conversation_context: dict  # Additional context tracking


# ==================== INTENT DETECTION ====================

INTENT_DETECTION_SYSTEM = """You are an expert at detecting user intent in e-commerce customer support conversations.

Analyze the user's message and classify it into ONE of these intents:

1. **READ**: User wants to query/search/view information
   - Examples: "Show me my orders", "What products do you have?", "Check order status"

2. **CREATE**: User wants to add/create something new
   - Examples: "I want to place an order", "Add this to my cart", "Create a new order"

3. **UPDATE**: User wants to modify/change existing data
   - Examples: "Change my order status", "Update the price", "Modify the quantity"

4. **DELETE**: User wants to cancel/remove something
   - Examples: "Cancel my order", "Remove this product", "Delete the item"

5. **GENERAL**: General conversation, greetings, questions, or unclear intent
   - Examples: "Hello", "Can you help me?", "Thank you"

6. **CONFIRMATION**: User is confirming or denying a pending action
   - Examples: "Yes", "Confirm", "No", "Cancel", "Go ahead", "Don't do it"

IMPORTANT:
- If the message is unclear, default to GENERAL
- Look for action verbs to determine intent
- Consider conversation context when available

Respond with ONLY the intent category in uppercase (READ, CREATE, UPDATE, DELETE, GENERAL, or CONFIRMATION)."""


async def detect_intent(state: AgentState) -> str:
    """Detect user intent from the latest message."""
    # If awaiting confirmation, intent should be CONFIRMATION
    if state.get("awaiting_confirmation", False):
        last_message = state["messages"][-1].content.lower().strip()
        confirmation_keywords = ["yes", "confirm", "ok", "sure", "go ahead", "proceed", "do it"]
        denial_keywords = ["no", "cancel", "don't", "stop", "nevermind", "never mind"]

        if any(word in last_message for word in confirmation_keywords):
            return "CONFIRMATION_YES"
        elif any(word in last_message for word in denial_keywords):
            return "CONFIRMATION_NO"
        else:
            return "CONFIRMATION_UNCLEAR"

    # Otherwise, use LLM to detect intent
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Get recent conversation context (last 3 messages)
    recent_messages = state["messages"][-3:] if len(state["messages"]) > 3 else state["messages"]
    context_str = "\n".join([
        f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
        for msg in recent_messages
    ])

    prompt = f"""{INTENT_DETECTION_SYSTEM}

RECENT CONVERSATION:
{context_str}

USER'S LATEST MESSAGE:
{state["messages"][-1].content}

INTENT:"""

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    intent = response.content.strip().upper()

    # Validate intent
    valid_intents = ["READ", "CREATE", "UPDATE", "DELETE", "GENERAL", "CONFIRMATION"]
    if intent not in valid_intents:
        intent = "GENERAL"

    return intent


# ==================== AGENT NODES ====================

async def intent_detection_node(state: AgentState) -> AgentState:
    """Node that detects user intent."""
    intent = await detect_intent(state)
    state["detected_intent"] = intent
    return state


async def handle_confirmation_node(state: AgentState) -> AgentState:
    """Handle confirmation responses."""
    intent = state["detected_intent"]

    if intent == "CONFIRMATION_YES":
        # User confirmed - execute the pending action
        pending = state.get("pending_action")
        if pending:
            # Execute the tool
            tool_node = ToolNode(ALL_TOOLS)

            # Create a tool call message
            tool_call_id = "confirm_action"
            tool_message = ToolMessage(
                content=pending["params"],
                tool_call_id=tool_call_id,
                name=pending["tool_name"]
            )

            # Execute the tool
            result = pending["tool"](**pending["params"])

            # Add result to messages
            state["messages"].append(AIMessage(content=f"Action executed. Result: {result}"))

        state["awaiting_confirmation"] = False
        state["pending_action"] = None

    elif intent == "CONFIRMATION_NO":
        # User declined
        state["messages"].append(AIMessage(content="Understood. I've cancelled that action. How else can I help you?"))
        state["awaiting_confirmation"] = False
        state["pending_action"] = None

    else:
        # Unclear confirmation
        state["messages"].append(AIMessage(content="I didn't quite catch that. Could you please confirm with 'yes' or 'no'?"))

    return state


async def agent_node(state: AgentState) -> AgentState:
    """Main agent reasoning node with tool calling."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    system_message = SystemMessage(content="""You are a helpful e-commerce customer support agent. You assist customers with:
- Searching for orders and products (READ operations)
- Creating new orders (CREATE operations - ALWAYS ask for confirmation first)
- Updating order status, prices, stock (UPDATE operations - ALWAYS ask for confirmation first)
- Cancelling orders or removing products (DELETE operations - ALWAYS ask for confirmation first)

IMPORTANT RULES:
1. For READ operations: Execute immediately without confirmation
2. For CREATE/UPDATE/DELETE operations: ALWAYS describe what you're about to do and ask for explicit confirmation
3. Be conversational, friendly, and helpful
4. If intent changes mid-conversation, adapt gracefully
5. Provide clear, structured information when displaying results
6. Handle errors gracefully and suggest alternatives

Current Intent: {intent}""")

    intent = state.get("detected_intent", "GENERAL")

    # Build prompt with system message
    prompt_messages = [
        SystemMessage(content=system_message.content.format(intent=intent))
    ] + state["messages"]

    # Call LLM
    response = await llm_with_tools.ainvoke(prompt_messages)

    # Check if there are tool calls
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]

        # Determine if this is a destructive operation
        destructive_tools = [
            "create_order", "add_product",
            "update_order_status", "update_product_price", "update_product_stock",
            "cancel_order", "delete_product"
        ]

        if tool_name in destructive_tools and not state.get("awaiting_confirmation"):
            # Ask for confirmation
            state["pending_action"] = {
                "tool_name": tool_name,
                "tool": [t for t in ALL_TOOLS if t.name == tool_name][0],
                "params": tool_call["args"]
            }
            state["awaiting_confirmation"] = True

            # Generate confirmation message
            confirmation_msg = f"""I'm about to perform the following action:

**Action**: {tool_name.replace('_', ' ').title()}
**Details**: {json.dumps(tool_call['args'], indent=2)}

This action will modify your data. Would you like me to proceed? (Please confirm with 'yes' or 'no')"""

            state["messages"].append(AIMessage(content=confirmation_msg))

        else:
            # Execute read operations immediately
            state["messages"].append(response)
    else:
        # No tool calls, just conversation
        state["messages"].append(response)

    return state


async def tool_node(state: AgentState) -> AgentState:
    """Execute tools that have been called."""
    tool_executor = ToolNode(ALL_TOOLS)
    result = await tool_executor.ainvoke(state)
    return result


# ==================== ROUTING LOGIC ====================

def route_after_intent(state: AgentState) -> Literal["handle_confirmation", "agent"]:
    """Route based on detected intent."""
    intent = state.get("detected_intent", "GENERAL")

    if intent.startswith("CONFIRMATION"):
        return "handle_confirmation"
    else:
        return "agent"


def route_after_agent(state: AgentState) -> Literal["tools", "end"]:
    """Route after agent decision."""
    last_message = state["messages"][-1]

    # If awaiting confirmation, don't execute tools
    if state.get("awaiting_confirmation"):
        return "end"

    # If the last message has tool calls and it's a read operation, execute
    if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        tool_name = last_message.tool_calls[0]["name"]
        read_tools = ["search_orders", "search_products", "get_order_details"]

        if tool_name in read_tools:
            return "tools"

    return "end"


def route_after_tools(state: AgentState) -> Literal["agent", "end"]:
    """Route after tool execution."""
    # After tools execute, go back to agent to generate response
    return "agent"


# ==================== GRAPH CONSTRUCTION ====================

def create_agent_graph():
    """Create the LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("detect_intent", intent_detection_node)
    workflow.add_node("handle_confirmation", handle_confirmation_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    # Add edges
    workflow.set_entry_point("detect_intent")

    workflow.add_conditional_edges(
        "detect_intent",
        route_after_intent,
        {
            "handle_confirmation": "handle_confirmation",
            "agent": "agent"
        }
    )

    workflow.add_edge("handle_confirmation", END)

    workflow.add_conditional_edges(
        "agent",
        route_after_agent,
        {
            "tools": "tools",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "tools",
        route_after_tools,
        {
            "agent": "agent",
            "end": END
        }
    )

    return workflow.compile()


# ==================== AGENT CLASS ====================

class EcommerceAgent:
    """High-level interface for the e-commerce support agent."""

    def __init__(self):
        self.graph = create_agent_graph()
        self.state = {
            "messages": [],
            "detected_intent": None,
            "pending_action": None,
            "awaiting_confirmation": False,
            "conversation_context": {}
        }

    async def process_message(self, user_message: str) -> str:
        """Process a user message and return the agent's response."""
        # Add user message to state
        self.state["messages"].append(HumanMessage(content=user_message))

        # Run the graph
        result = await self.graph.ainvoke(self.state)

        # Update state
        self.state = result

        # Get last AI message
        last_message = [msg for msg in result["messages"] if isinstance(msg, AIMessage)][-1]

        return last_message.content

    def reset(self):
        """Reset conversation state."""
        self.state = {
            "messages": [],
            "detected_intent": None,
            "pending_action": None,
            "awaiting_confirmation": False,
            "conversation_context": {}
        }