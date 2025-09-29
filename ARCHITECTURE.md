# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                                                                 │
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │   CLI Interface  │              │  Web Interface   │        │
│  │  (Terminal-based)│              │ (Browser-based)  │        │
│  └────────┬─────────┘              └─────────┬────────┘        │
│           │                                   │                 │
│           └───────────────┬───────────────────┘                 │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONVERSATION AGENT                           │
│                   (simple_agent.py)                             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Message Processing                                       │  │
│  │  • Parse user input                                       │  │
│  │  • Maintain conversation history                         │  │
│  │  • Track confirmation state                              │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │  OpenAI LLM (GPT-4)                                       │  │
│  │  • Natural language understanding                         │  │
│  │  • Tool calling & decision making                         │  │
│  │  • Response generation                                    │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │  Confirmation Handler                                     │  │
│  │  • Detect confirmation intent                             │  │
│  │  • Manage pending actions                                 │  │
│  │  • Route to tool execution or cancellation               │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TOOL LAYER                                 │
│                      (tools.py)                                 │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ READ Tools   │  │ CREATE Tools │  │ UPDATE Tools │         │
│  │──────────────│  │──────────────│  │──────────────│         │
│  │• search_     │  │• create_     │  │• update_     │         │
│  │  orders      │  │  order       │  │  order_      │         │
│  │• search_     │  │• add_        │  │  status      │         │
│  │  products    │  │  product     │  │• update_     │         │
│  │• get_order_  │  │              │  │  product_    │         │
│  │  details     │  │              │  │  price       │         │
│  │              │  │              │  │• update_     │         │
│  │No confirm ❌ │  │Confirm ✅    │  │  product_    │         │
│  │              │  │              │  │  stock       │         │
│  │              │  │              │  │              │         │
│  │              │  │              │  │Confirm ✅    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐                                              │
│  │ DELETE Tools │                                              │
│  │──────────────│                                              │
│  │• cancel_     │                                              │
│  │  order       │                                              │
│  │• delete_     │                                              │
│  │  product     │                                              │
│  │              │                                              │
│  │Confirm ✅    │                                              │
│  └──────────────┘                                              │
│                                                                 │
│                         │                                       │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                               │
│                   (database.py)                                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SQLite Database (ecommerce.db)                          │  │
│  │                                                          │  │
│  │  ┌────────────────────┐    ┌────────────────────┐       │  │
│  │  │   orders table     │    │  products table    │       │  │
│  │  │────────────────────│    │────────────────────│       │  │
│  │  │• id                │    │• id                │       │  │
│  │  │• order_number      │    │• product_name      │       │  │
│  │  │• customer_name     │    │• description       │       │  │
│  │  │• product_name      │    │• price             │       │  │
│  │  │• quantity          │    │• stock             │       │  │
│  │  │• price             │    │• category          │       │  │
│  │  │• status            │    │• created_at        │       │  │
│  │  │• created_at        │    │                    │       │  │
│  │  │• updated_at        │    │                    │       │  │
│  │  └────────────────────┘    └────────────────────┘       │  │
│  │                                                          │  │
│  │  13 Orders                   15 Products                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Conversation Flow

```
┌─────────────┐
│ User Input  │
└─────┬───────┘
      │
      ▼
┌─────────────────────┐
│ Agent Receives      │
│ Message             │
└─────┬───────────────┘
      │
      ▼
┌─────────────────────┐      Yes      ┌──────────────────────┐
│ Awaiting            ├──────────────► │ Handle Confirmation  │
│ Confirmation?       │                │ • Check yes/no       │
└─────┬───────────────┘                │ • Execute or Cancel  │
      │ No                             └──────────┬───────────┘
      ▼                                           │
┌─────────────────────┐                           │
│ Send to LLM         │                           │
│ with System Message │                           │
│ + Tools             │                           │
└─────┬───────────────┘                           │
      │                                           │
      ▼                                           │
┌─────────────────────┐                           │
│ LLM Decides:        │                           │
│ • Use Tool?         │                           │
│ • Just Respond?     │                           │
└─────┬───────────────┘                           │
      │                                           │
      ├─── Tool Call ────┐                        │
      │                  │                        │
      │                  ▼                        │
      │         ┌──────────────────┐              │
      │         │ Is Destructive   │              │
      │         │ Operation?       │              │
      │         └────┬─────────────┘              │
      │              │                            │
      │    Yes ◄─────┼────► No                    │
      │              │                            │
      │         ┌────▼─────────────┐              │
      │         │ Ask for          │              │
      │         │ Confirmation     │              │
      │         │ • Set pending    │              │
      │         │ • Await response │              │
      │         └──────────────────┘              │
      │                                           │
      │              ┌──────────────────┐         │
      │              │ Execute Tool     │         │
      │              │ • Call function  │         │
      │              │ • Format result  │         │
      │              └──────┬───────────┘         │
      │                     │                     │
      └── Just Response ────┤                     │
                            │                     │
                            ▼                     │
                   ┌──────────────────┐           │
                   │ Return to User   │◄──────────┘
                   └──────────────────┘
```

---

## Intent Detection Flow

```
┌──────────────────────┐
│ User Message         │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Awaiting Confirmation?           │
└──────┬────────────────────┬──────┘
       │ Yes                │ No
       │                    │
       ▼                    ▼
┌────────────────┐    ┌──────────────────┐
│ Pattern Match  │    │ Send to LLM      │
│ • yes/confirm  │    │ for Intent       │
│ • no/cancel    │    │ Classification   │
│ • unclear      │    └────────┬─────────┘
└────────┬───────┘             │
         │                     │
         │                     ▼
         │            ┌─────────────────┐
         │            │ Agent Behavior  │
         │            │ Adapts Based    │
         │            │ on Intent       │
         │            └─────────────────┘
         │
         └──────────────┐
                        │
                        ▼
               ┌──────────────────┐
               │ Execute Action   │
               │ or Cancel        │
               └──────────────────┘
```

---

## Data Flow

```
User Input
    │
    ▼
Agent (simple_agent.py)
    │
    ├──► LLM (OpenAI GPT-4) ──► Tool Selection
    │                                │
    │                                ▼
    │                           Tool Execution
    │                                │
    │                                ▼
    │                           Tools (tools.py)
    │                                │
    │                                ▼
    │                           Database (database.py)
    │                                │
    │                                ▼
    │                           SQLite (ecommerce.db)
    │                                │
    │                                ▼
    │                           Query Results
    │                                │
    ▼                                ▼
Format & Return ◄────────────── Process Results
    │
    ▼
User Response
```

---

## File Dependencies

```
chat_interface.py
    │
    ├──► simple_agent.py
    │       │
    │       ├──► tools.py
    │       │       │
    │       │       └──► database.py
    │       │               │
    │       │               └──► ecommerce.db
    │       │
    │       └──► langchain_openai (ChatOpenAI)
    │
    └──► .env (API keys)


demo.py
    │
    └──► simple_agent.py (same dependencies as above)


create_sample_data.py
    │
    └──► database.py
            │
            └──► ecommerce.db
```

---

## Component Responsibilities

### 1. **Chat Interface** (`chat_interface.py`)
- **Purpose**: User interaction layer
- **Responsibilities**:
  - Accept user input (CLI or Web)
  - Display agent responses
  - Handle special commands (help, reset, quit)
  - Manage conversation loop

### 2. **Simple Agent** (`simple_agent.py`)
- **Purpose**: Core conversational logic
- **Responsibilities**:
  - Process user messages
  - Maintain conversation state
  - Integrate with OpenAI LLM
  - Handle tool calls
  - Manage confirmation flows
  - Format responses

### 3. **Tools** (`tools.py`)
- **Purpose**: Database operation wrappers
- **Responsibilities**:
  - Define 10 CRUD operation tools
  - Validate inputs
  - Execute database queries
  - Return structured JSON results
  - Handle errors gracefully

### 4. **Database** (`database.py`)
- **Purpose**: Data persistence layer
- **Responsibilities**:
  - Initialize SQLite database
  - Create schema (orders & products tables)
  - Seed initial data
  - Provide query/update methods
  - Manage connections

### 5. **Demo** (`demo.py`)
- **Purpose**: Automated demonstration
- **Responsibilities**:
  - Showcase all CRUD operations
  - Run without user interaction
  - Demonstrate confirmation flows
  - Show intent adaptation

---

## Design Patterns Used

### 1. **Tool Pattern** (LangChain Tools)
- Each database operation is a discrete tool
- Tools are composable and reusable
- LLM selects appropriate tool based on user intent

### 2. **State Management Pattern**
- Agent maintains conversation state
- Tracks pending actions
- Manages confirmation awaiting state
- Preserves conversation history

### 3. **Confirmation Pattern**
- All destructive operations gated behind confirmation
- Clear two-step process:
  1. Describe action + ask
  2. Execute or cancel based on response

### 4. **Factory Pattern**
- Database connection management
- Tool instantiation
- Message formatting

### 5. **Strategy Pattern**
- Different handling for read vs. write operations
- Conditional confirmation logic
- Response formatting based on result type

---

## Security Layers

```
User Input
    │
    ▼
Input Validation (Length, Type)
    │
    ▼
Intent Classification (LLM)
    │
    ▼
Tool Selection & Validation
    │
    ▼
Confirmation Gate (for destructive ops)
    │
    ▼
Parameterized Queries (SQL Injection Prevention)
    │
    ▼
Database Constraints (UNIQUE, NOT NULL, etc.)
    │
    ▼
Result Formatting & Sanitization
    │
    ▼
Output to User
```

---

## Scalability Considerations

### Current (Single-User, Development)
- SQLite database
- Synchronous for simplicity in some areas
- In-memory conversation state
- Single-threaded

### Future (Multi-User, Production)
- PostgreSQL/MySQL with connection pooling
- Fully async operations
- Redis for state management
- Load balancing across multiple instances
- Horizontal scaling with stateless agents
- Message queue for background processing

---

## Extension Points

### 1. **Add New Tools**
Location: `tools.py`
```python
@tool
def new_tool(param: str) -> str:
    """Tool description."""
    # Implementation
    return json.dumps(result)
```

### 2. **Modify Database Schema**
Location: `database.py`
```python
def init_db(self):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS new_table (...)
    """)
```

### 3. **Add New Agent Capabilities**
Location: `simple_agent.py`
```python
async def new_capability(self):
    # Implementation
    pass
```

### 4. **Customize UI**
Location: `chat_interface.py`
- Modify `print_header()` for branding
- Add new special commands
- Change formatting

---

**Architecture designed for clarity, maintainability, and extensibility!**