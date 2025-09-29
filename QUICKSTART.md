# Quick Start Guide

## ✅ Setup Complete!

Your E-Commerce AI Customer Support Agent is ready to use.

## 🚀 Running the Agent

### Option 1: Modern Web Interface (RECOMMENDED) 🌐
```
Double-click: run_web.bat
```
Then open your browser to: **http://localhost:5000**

**Features:**
- Beautiful modern UI
- Quick action buttons
- Typing indicators
- Mobile-friendly design
- Real-time chat

📖 Full guide: [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md)

### Option 2: CLI Interface
```
Double-click: run.bat
```
Or:
```bash
py chat_interface.py
```

### Option 3: Run the demo
```bash
py demo.py
```

## 💬 Example Conversations

### Search for Products
```
You: Show me all electronics
You: What products are under $50?
You: Show me accessories
```

### Check Orders
```
You: Show me all orders
You: Check order ORD-1001
You: Find orders for John Doe
```

### Create an Order (requires confirmation)
```
You: I want to order 2 Wireless Mouse for Sarah Brown
Agent: [Asks for confirmation]
You: yes
```

### Update Order Status (requires confirmation)
```
You: Update order ORD-1002 to Delivered
Agent: [Asks for confirmation]
You: confirm
```

### Cancel an Order (requires confirmation)
```
You: Cancel order ORD-1005
Agent: [Asks for confirmation]
You: yes
```

## 🎯 Key Features

✅ **Natural Language** - Talk naturally, the AI understands intent
✅ **Confirmation Required** - All destructive operations ask for confirmation
✅ **Intent Adaptation** - Change your mind mid-conversation
✅ **Error Handling** - Graceful error messages with suggestions
✅ **Rich Database** - 15 products, 13 orders ready to use

## 📊 Current Database

**Products**: 15 items (Electronics, Accessories, Furniture)
**Orders**: 13 orders (Processing, Shipped, Delivered)

## 🔧 Special Commands

- `help` - Show help message
- `reset` - Start a new conversation
- `quit` / `exit` / `bye` - Exit the application

## 🆘 Troubleshooting

**If you get an error about OpenAI API key:**
- Check that `.env` file exists
- Verify the OPENAI_API_KEY is set correctly

**If packages are missing:**
```bash
py -m pip install -r requirements.txt
```

**To reset the database:**
```bash
py create_sample_data.py
```

## 📖 Learn More

- See `README.md` for full documentation
- See `example_transcripts.md` for detailed conversation examples
- See `demo.py` for automated demonstrations

---

**Ready to start? Double-click `run.bat` or run `py chat_interface.py`!**