"""
Simplified conversational agent for e-commerce customer support.
Uses direct LLM calls with tool integration and manual confirmation handling.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import json
from tools import ALL_TOOLS


class SimpleEcommerceAgent:
    """Simplified e-commerce support agent with CRUD operations."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.llm_with_tools = self.llm.bind_tools(ALL_TOOLS)
        self.messages = []
        self.pending_action = None
        self.awaiting_confirmation = False

    def _get_system_message(self) -> SystemMessage:
        """Get the system message for the agent."""
        return SystemMessage(content="""You are a helpful e-commerce customer support agent. You assist customers with:
- Searching for orders and products (READ operations)
- Creating new orders (CREATE operations - ALWAYS ask for confirmation first)
- Updating order status, prices, stock (UPDATE operations - ALWAYS ask for confirmation first)
- Cancelling orders or removing products (DELETE operations - ALWAYS ask for confirmation first)

IMPORTANT RULES:
1. For READ operations: Execute immediately without confirmation
2. For CREATE/UPDATE/DELETE operations: ALWAYS describe what you're about to do and ask for explicit confirmation
3. Be conversational, friendly, and helpful
4. Provide clear, structured information when displaying results
5. Handle errors gracefully and suggest alternatives

When you need to execute a tool, use the available tools. For read operations like searching or viewing data, call the tool directly. For create/update/delete operations, first explain what you will do and ask for confirmation.""")

    async def process_message(self, user_message: str) -> str:
        """Process a user message and return the agent's response."""

        # Add user message
        self.messages.append(HumanMessage(content=user_message))

        # Check if we're awaiting confirmation
        if self.awaiting_confirmation:
            return await self._handle_confirmation(user_message)

        # Build messages with system message
        all_messages = [self._get_system_message()] + self.messages

        # Call LLM with tools
        response = await self.llm_with_tools.ainvoke(all_messages)

        # Check if there are tool calls
        if response.tool_calls:
            return await self._handle_tool_calls(response)
        else:
            # No tool calls, just conversation
            self.messages.append(response)
            return response.content

    async def _handle_tool_calls(self, response):
        """Handle tool calls from the LLM."""
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # Determine if this is a destructive operation
        destructive_tools = [
            "create_order", "add_product",
            "update_order_status", "update_product_price", "update_product_stock",
            "cancel_order", "delete_product"
        ]

        if tool_name in destructive_tools:
            # Ask for confirmation
            self.pending_action = {
                "tool_name": tool_name,
                "tool_args": tool_args,
                "tool_call": tool_call
            }
            self.awaiting_confirmation = True

            # Generate confirmation message
            confirmation_msg = f"""I'm about to perform the following action:

**Action**: {tool_name.replace('_', ' ').title()}
**Details**: {json.dumps(tool_args, indent=2)}

This action will modify your data. Would you like me to proceed? (Please confirm with 'yes' or 'no')"""

            self.messages.append(AIMessage(content=confirmation_msg))
            return confirmation_msg

        else:
            # Execute read operations immediately
            return await self._execute_tool(tool_name, tool_args)

    async def _execute_tool(self, tool_name: str, tool_args: dict) -> str:
        """Execute a tool and return formatted results."""
        # Find the tool
        tool = next((t for t in ALL_TOOLS if t.name == tool_name), None)

        if not tool:
            return f"Error: Tool '{tool_name}' not found."

        # Execute the tool
        try:
            result = tool.invoke(tool_args)

            # Parse result
            result_data = json.loads(result)

            # Format the result
            if result_data.get("success"):
                formatted = self._format_result(tool_name, result_data)

                # Add AI message to history
                self.messages.append(AIMessage(content=formatted))
                return formatted
            else:
                error_msg = result_data.get("message") or result_data.get("error") or "Operation failed"
                self.messages.append(AIMessage(content=f"⚠️ {error_msg}"))
                return f"⚠️ {error_msg}"

        except Exception as e:
            error_msg = f"Error executing tool: {str(e)}"
            self.messages.append(AIMessage(content=error_msg))
            return error_msg

    def _format_result(self, tool_name: str, result_data: dict) -> str:
        """Format tool results for display."""
        if "orders" in result_data:
            # Format orders
            orders = result_data["orders"]
            output = f"Found {len(orders)} order(s):\n\n"
            for order in orders:
                output += f"**Order {order['order_number']}**\n"
                output += f"  - Customer: {order['customer_name']}\n"
                output += f"  - Product: {order['product_name']}\n"
                output += f"  - Quantity: {order['quantity']}\n"
                output += f"  - Price: ${order['price']:.2f}\n"
                output += f"  - Status: {order['status']}\n\n"
            return output

        elif "products" in result_data:
            # Format products
            products = result_data["products"]
            output = f"Found {len(products)} product(s):\n\n"
            for product in products:
                output += f"**{product['product_name']}**\n"
                output += f"  - Price: ${product['price']:.2f}\n"
                output += f"  - Stock: {product['stock']} units\n"
                output += f"  - Category: {product['category']}\n"
                if product.get('description'):
                    output += f"  - Description: {product['description']}\n"
                output += "\n"
            return output

        elif "order" in result_data:
            # Format single order
            order = result_data["order"]
            output = f"**Order {order['order_number']}**\n"
            output += f"  - Customer: {order['customer_name']}\n"
            output += f"  - Product: {order['product_name']}\n"
            output += f"  - Quantity: {order['quantity']}\n"
            output += f"  - Price: ${order['price']:.2f}\n"
            output += f"  - Status: {order['status']}\n"
            if result_data.get("message"):
                output += f"\n✅ {result_data['message']}"
            return output

        elif "product" in result_data:
            # Format single product
            product = result_data["product"]
            output = f"**{product['product_name']}**\n"
            output += f"  - Price: ${product['price']:.2f}\n"
            output += f"  - Stock: {product['stock']} units\n"
            output += f"  - Category: {product['category']}\n"
            if product.get('description'):
                output += f"  - Description: {product['description']}\n"
            if result_data.get("message"):
                output += f"\n✅ {result_data['message']}"
            return output

        elif result_data.get("message"):
            return f"✅ {result_data['message']}"

        else:
            return f"Operation completed: {json.dumps(result_data, indent=2)}"

    async def _handle_confirmation(self, user_message: str) -> str:
        """Handle confirmation responses."""
        msg_lower = user_message.lower().strip()
        confirmation_keywords = ["yes", "confirm", "ok", "sure", "go ahead", "proceed", "do it"]
        denial_keywords = ["no", "cancel", "don't", "stop", "nevermind", "never mind"]

        if any(word in msg_lower for word in confirmation_keywords):
            # User confirmed - execute the pending action
            if self.pending_action:
                tool_name = self.pending_action["tool_name"]
                tool_args = self.pending_action["tool_args"]

                self.awaiting_confirmation = False
                self.pending_action = None

                result = await self._execute_tool(tool_name, tool_args)
                return result
            else:
                self.awaiting_confirmation = False
                return "No pending action to confirm."

        elif any(word in msg_lower for word in denial_keywords):
            # User declined
            self.awaiting_confirmation = False
            self.pending_action = None
            response = "Understood. I've cancelled that action. How else can I help you?"
            self.messages.append(AIMessage(content=response))
            return response

        else:
            # Unclear confirmation
            return "I didn't quite catch that. Could you please confirm with 'yes' or 'no'?"

    def reset(self):
        """Reset conversation state."""
        self.messages = []
        self.pending_action = None
        self.awaiting_confirmation = False