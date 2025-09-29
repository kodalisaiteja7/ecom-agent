"""
User-friendly chat interface for the e-commerce AI agent.
Provides both CLI and web-based interfaces.
"""
import asyncio
import os
import sys
import io
from datetime import datetime
from simple_agent import SimpleEcommerceAgent as EcommerceAgent
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# ==================== CLI INTERFACE ====================

class CLIChatInterface:
    """Command-line interface for the chat agent."""

    def __init__(self):
        self.agent = EcommerceAgent()
        self.running = True

    def print_header(self):
        """Print welcome header."""
        print("\n" + "=" * 70)
        print("E-COMMERCE AI CUSTOMER SUPPORT")
        print("=" * 70)
        print("\nWelcome! I'm your AI shopping assistant.")
        print("I can help you with:")
        print("  • Searching for orders and products")
        print("  • Creating new orders")
        print("  • Updating order status, prices, and stock")
        print("  • Cancelling orders")
        print("\nType 'quit', 'exit', or 'bye' to end the conversation.")
        print("Type 'reset' to start a new conversation.")
        print("Type 'help' for more information.")
        print("-" * 70 + "\n")

    def print_help(self):
        """Print help information."""
        print("\n" + "=" * 70)
        print("HELP - AVAILABLE COMMANDS")
        print("=" * 70)
        print("""
QUERY EXAMPLES (READ operations):
  • "Show me all orders"
  • "Find orders for John Doe"
  • "What products do you have?"
  • "Show me electronics under $500"
  • "Check order ORD-1001"

CREATE EXAMPLES:
  • "I want to place an order for a Laptop Pro 15"
  • "Create an order for 2 Wireless Mouse for Jane Smith"
  • "Add a new product: Tablet Pro, $599, 50 units"

UPDATE EXAMPLES:
  • "Change order ORD-1001 status to Shipped"
  • "Update Laptop Pro 15 price to $1199"
  • "Set stock for Wireless Mouse to 200"

DELETE EXAMPLES:
  • "Cancel order ORD-1002"
  • "Remove Gaming Keyboard from catalog"

SPECIAL COMMANDS:
  • quit/exit/bye - End the conversation
  • reset - Start a new conversation
  • help - Show this help message
        """)
        print("=" * 70 + "\n")

    async def run(self):
        """Run the CLI interface."""
        self.print_header()

        while self.running:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nThank you for shopping with us! Goodbye!\n")
                    self.running = False
                    break

                if user_input.lower() == 'reset':
                    self.agent.reset()
                    print("\nConversation reset. Starting fresh!\n")
                    continue

                if user_input.lower() == 'help':
                    self.print_help()
                    continue

                # Show typing indicator
                print("\nAssistant: ", end="", flush=True)

                # Process message
                response = await self.agent.process_message(user_input)

                # Print response with formatting
                print(f"{response}\n")

            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!\n")
                self.running = False
                break
            except Exception as e:
                print(f"\nError: {str(e)}\n")
                print("Please try again or type 'help' for assistance.\n")


# ==================== WEB INTERFACE (OPTIONAL) ====================

class WebChatInterface:
    """
    Web-based chat interface using Flask.
    This is an optional alternative to the CLI interface.
    """

    def __init__(self, port=5000):
        self.port = port
        self.agent = EcommerceAgent()

    def create_app(self):
        """Create Flask web application."""
        try:
            from flask import Flask, render_template_string, request, jsonify
        except ImportError:
            print("Flask not installed. Install with: pip install flask")
            return None

        app = Flask(__name__)

        # HTML template
        HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>E-Commerce AI Support</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 50px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f5f5f5;
        }

        .message {
            margin-bottom: 15px;
            display: flex;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            justify-content: flex-end;
        }

        .message-content {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 18px;
            word-wrap: break-word;
        }

        .message.user .message-content {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }

        .message.assistant .message-content {
            background: white;
            color: #333;
            border-bottom-left-radius: 4px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .chat-input {
            display: flex;
            padding: 20px;
            background: white;
            border-top: 1px solid #ddd;
        }

        #user-input {
            flex: 1;
            padding: 12px 18px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border 0.3s;
        }

        #user-input:focus {
            border-color: #667eea;
        }

        #send-button {
            margin-left: 10px;
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }

        #send-button:hover {
            transform: scale(1.05);
        }

        #send-button:active {
            transform: scale(0.95);
        }

        .typing-indicator {
            display: none;
            padding: 12px 18px;
            background: white;
            border-radius: 18px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            width: fit-content;
        }

        .typing-indicator.active {
            display: block;
        }

        .typing-indicator span {
            height: 10px;
            width: 10px;
            background: #667eea;
            border-radius: 50%;
            display: inline-block;
            margin: 0 2px;
            animation: bounce 1.4s infinite ease-in-out both;
        }

        .typing-indicator span:nth-child(1) {
            animation-delay: -0.32s;
        }

        .typing-indicator span:nth-child(2) {
            animation-delay: -0.16s;
        }

        @keyframes bounce {
            0%, 80%, 100% {
                transform: scale(0);
            }
            40% {
                transform: scale(1);
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            🛍️ E-Commerce AI Customer Support
        </div>
        <div class="chat-messages" id="chat-messages">
            <div class="message assistant">
                <div class="message-content">
                    Hello! I'm your AI shopping assistant. I can help you with orders, products, and more. How can I assist you today?
                </div>
            </div>
        </div>
        <div class="chat-input">
            <input type="text" id="user-input" placeholder="Type your message here..." autofocus>
            <button id="send-button">Send</button>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chat-messages');
        const userInput = document.getElementById('user-input');
        const sendButton = document.getElementById('send-button');

        function addMessage(content, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;

            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;

            messageDiv.appendChild(contentDiv);
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function showTypingIndicator() {
            const indicator = document.createElement('div');
            indicator.className = 'typing-indicator active';
            indicator.id = 'typing-indicator';
            indicator.innerHTML = '<span></span><span></span><span></span>';
            chatMessages.appendChild(indicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function hideTypingIndicator() {
            const indicator = document.getElementById('typing-indicator');
            if (indicator) {
                indicator.remove();
            }
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            addMessage(message, true);
            userInput.value = '';
            userInput.disabled = true;
            sendButton.disabled = true;

            showTypingIndicator();

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message }),
                });

                const data = await response.json();
                hideTypingIndicator();

                if (data.response) {
                    addMessage(data.response, false);
                } else {
                    addMessage('Sorry, I encountered an error. Please try again.', false);
                }
            } catch (error) {
                hideTypingIndicator();
                addMessage('Sorry, I encountered an error. Please try again.', false);
            }

            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus();
        }

        sendButton.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
        """

        @app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE)

        @app.route('/chat', methods=['POST'])
        async def chat():
            data = request.json
            user_message = data.get('message', '')

            try:
                response = await self.agent.process_message(user_message)
                return jsonify({'response': response})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        return app

    def run(self):
        """Run the web interface."""
        app = self.create_app()
        if app:
            print(f"\nStarting web interface on http://localhost:{self.port}")
            print("Press Ctrl+C to stop\n")
            app.run(host='0.0.0.0', port=self.port, debug=False)
        else:
            print("Could not start web interface. Using CLI instead.")
            cli = CLIChatInterface()
            asyncio.run(cli.run())


# ==================== MAIN ENTRY POINT ====================

async def main():
    """Main entry point for the application."""
    print("\nSelect interface mode:")
    print("1. CLI (Command Line Interface) - Recommended")
    print("2. Web Interface (requires Flask)")

    choice = input("\nEnter your choice (1 or 2, default=1): ").strip()

    if choice == "2":
        web = WebChatInterface()
        web.run()
    else:
        cli = CLIChatInterface()
        await cli.run()


if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\nWARNING: OPENAI_API_KEY environment variable not set!")
        print("Please set it with: set OPENAI_API_KEY=your-key-here\n")
        exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!\n")