# 🛍️ E-Commerce AI Customer Support Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com/)

A production-ready conversational AI agent built with **LangGraph** and **LangChain** that handles CRUD operations on an e-commerce database through natural language conversations.

🌐 **[Live Demo](https://github.com/kodalisaiteja7/ecom-agent)** | 📖 **[Documentation](INDEX.md)** | 🚀 **[Quick Start](QUICKSTART.md)**

---

📑 **New to the project? Start with [INDEX.md](INDEX.md) for easy navigation!**

## 🚀 Features

- **Stateful Conversation Management**: Uses LangGraph to maintain conversation context and track user intent across messages
- **Intent Detection**: Automatically detects and adapts to changing user intent (CREATE, READ, UPDATE, DELETE, GENERAL)
- **Confirmation Flows**: Requests explicit user confirmation before any destructive operations
- **Database Operations**: Full CRUD support for orders and products with SQLite
- **Natural Language Understanding**: Powered by OpenAI's GPT-4 for intent detection and response generation
- **Error Handling**: Graceful error handling with helpful suggestions
- **Two Interfaces**: CLI and Web-based chat interfaces
- **Modular Design**: Easy to extend with new tools, agents, or database schemas

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key (set as `OPENAI_API_KEY` environment variable)

## 🛠️ Installation

1. **Clone or navigate to the project directory**:
```bash
cd "C:\Users\HARI\Desktop\Teja\CRUD Agent"
```

2. **Install dependencies** (already done):
```bash
pip install langgraph langchain langchain-openai langchain-community openai sqlalchemy
```

3. **Set up OpenAI API key**:
```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac
export OPENAI_API_KEY='your-api-key-here'
```

## 🎮 Usage

### Option 1: Modern Web Interface (Recommended) 🌐

**Easiest: Double-click `run_web.bat`**

Or run:
```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

✨ Features beautiful UI, quick actions, typing indicators, and more!
📖 See [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md) for complete web app documentation.

### Option 2: CLI Interface

```bash
python chat_interface.py
```

You'll be prompted to choose between:
1. **CLI Interface** - Terminal-based chat
2. **Web Interface (Legacy)** - Basic browser chat

### Example Interactions

#### READ - Query Information
```
You: Show me all orders
You: What products do you have?
You: Check order ORD-1001
```

#### CREATE - Add New Data
```
You: I want to order 2 Wireless Mouse for John Doe
You: Add a new product: Tablet, $599, 50 units
```
*Agent will ask for confirmation before creating*

#### UPDATE - Modify Existing Data
```
You: Change order ORD-1001 status to Shipped
You: Update Laptop price to $1199
```
*Agent will ask for confirmation before updating*

#### DELETE - Remove Data
```
You: Cancel order ORD-1002
You: Remove Gaming Keyboard from catalog
```
*Agent will ask for confirmation before deleting*

## 📁 Project Structure

```
CRUD Agent/
├── database.py           # Database initialization and schema
├── tools.py              # CRUD operation tools for LangChain
├── agent.py              # LangGraph agent with state management
├── chat_interface.py     # CLI and web chat interfaces
├── example_transcripts.md # Example conversations
├── README.md             # This file
└── ecommerce.db          # SQLite database (auto-created)
```

## 🏗️ Architecture

### LangGraph State Machine

```
┌─────────────────┐
│  User Message   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Intent Detection│ ◄─── Re-evaluates on every message
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
    ▼          ▼
┌────────┐  ┌──────────────┐
│Confirm?│  │    Agent     │
└───┬────┘  │  (with tools)│
    │       └──────┬───────┘
    │              │
    ▼              ▼
 ┌──────┐      ┌──────┐
 │Cancel│      │Tools │
 │ or   │      │Execute│
 │Execute│      └──────┘
 └──────┘
```

### Database Schema

**Orders Table**:
- id (primary key)
- order_number (unique)
- customer_name
- product_name
- quantity
- price
- status
- created_at
- updated_at

**Products Table**:
- id (primary key)
- product_name (unique)
- description
- price
- stock
- category
- created_at

## 🔧 Configuration

### Extending the Database Schema

Edit `database.py` to modify tables or add new ones:

```python
def init_db(self):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS your_table (
            id INTEGER PRIMARY KEY,
            # ... your columns
        )
    """)
```

### Adding New Tools

Add new tools in `tools.py`:

```python
@tool
def your_new_tool(param1: str, param2: int) -> str:
    """Tool description for the LLM."""
    # Your implementation
    return json.dumps({"success": True, "result": "..."})

# Add to ALL_TOOLS list
ALL_TOOLS = [
    # ... existing tools
    your_new_tool,
]
```

### Customizing the Agent

Modify the system message in `agent.py` to change agent behavior:

```python
system_message = SystemMessage(content="""
Your custom instructions here...
""")
```

## 🎯 Key Components

### 1. Intent Detection (`agent.py`)
- Automatically detects user intent from each message
- Uses GPT-4-mini for fast, accurate classification
- Supports: READ, CREATE, UPDATE, DELETE, GENERAL, CONFIRMATION

### 2. Confirmation Flow
- Destructive operations (CREATE, UPDATE, DELETE) require confirmation
- Handles "yes", "no", "confirm", "cancel", and variations
- Can cancel pending actions gracefully

### 3. State Management
- Tracks conversation history
- Maintains pending actions
- Monitors confirmation status
- Stores conversation context

### 4. Tool Execution
- Structured tools using LangChain's `@tool` decorator
- JSON responses for easy parsing
- Comprehensive error handling
- Stock management for orders

## 📊 Sample Data

The database is automatically seeded with sample data:

**Products**:
- Laptop Pro 15 ($1,299.99)
- Wireless Mouse ($29.99)
- USB-C Hub ($49.99)
- Gaming Keyboard ($89.99)
- 4K Monitor ($399.99)

**Orders**:
- ORD-1001: John Doe - Laptop Pro 15 (Shipped)
- ORD-1002: Jane Smith - Wireless Mouse (Processing)
- ORD-1003: Bob Johnson - USB-C Hub (Delivered)

## 🔍 Example Transcripts

See `example_transcripts.md` for detailed conversation examples demonstrating:
- ✅ READ operations (search, query)
- ✅ CREATE operations (with confirmation)
- ✅ UPDATE operations (with confirmation)
- ✅ DELETE operations (with confirmation)
- ✅ Intent adaptation (changing intent mid-conversation)
- ✅ Multi-operation conversations

## 🚦 Error Handling

The agent handles common errors gracefully:
- Product not found
- Insufficient stock
- Invalid order numbers
- Duplicate products
- Active orders preventing deletion

## 🔐 Security Considerations

For production use, consider:
- Using PostgreSQL/MySQL instead of SQLite
- Adding authentication and authorization
- Implementing rate limiting
- Sanitizing database inputs (currently handled by SQLAlchemy)
- Adding audit logging
- Encrypting sensitive data

## 🚀 Scaling

The architecture is designed for scalability:
- **Async Support**: All agent operations are async-ready
- **Modular Tools**: Easy to add new database operations
- **Configurable Schema**: Database structure is flexible
- **LangGraph**: Supports complex multi-agent workflows
- **Tool Extensibility**: Can integrate external APIs, services

## 📝 Development

### Testing Locally

```bash
# Set a test API key
export OPENAI_API_KEY='your-test-key'

# Run the CLI interface
python chat_interface.py
```

### Debugging

Enable debug logging in `agent.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

To extend this project:

1. Add new tools in `tools.py`
2. Update the agent system message in `agent.py` if needed
3. Modify database schema in `database.py`
4. Test with various conversation flows
5. Update `example_transcripts.md` with new examples

## 📄 License

This project is provided as-is for educational and commercial use.

## 🙋 Support

For issues or questions:
1. Check `example_transcripts.md` for usage examples
2. Review the code comments for implementation details
3. Test with different conversation flows

## 🎉 Credits

Built with:
- **LangGraph**: State machine and workflow management
- **LangChain**: Tool integration and LLM orchestration
- **OpenAI**: GPT-4 for natural language understanding
- **SQLite**: Lightweight database
- **SQLAlchemy**: Database ORM (ready for use, can be integrated)

---

**Happy Building! 🚀**