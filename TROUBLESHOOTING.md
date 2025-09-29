# 🔧 Troubleshooting Guide

## Common Issues and Solutions

---

### Issue 1: Port 5000 Already in Use

**Error**: "Port 5000 is already in use" or "Address already in use"

**Solution Option 1: Stop the existing server**
1. Find the running process:
```bash
netstat -ano | findstr :5000
```
2. Kill the process (replace PID with the number from above):
```bash
taskkill /PID <PID> /F
```

**Solution Option 2: Use a different port**
1. Edit `app.py` and change the port:
```python
app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
```
2. Then access: http://localhost:5001

**Solution Option 3: The server might already be running!**
- Simply open your browser to: **http://localhost:5000**
- If you see the chat interface, it's already working!

---

### Issue 2: Module Not Found Error

**Error**: `ModuleNotFoundError: No module named 'flask'` (or langchain, etc.)

**Solution**:
```bash
cd "C:\Users\HARI\Desktop\Teja\CRUD Agent"
py -m pip install -r requirements.txt
```

---

### Issue 3: OpenAI API Key Error

**Error**: "OPENAI_API_KEY environment variable not set"

**Solution**:
1. Check if `.env` file exists in the project folder
2. Open `.env` and verify it contains:
```
OPENAI_API_KEY=sk-proj-...your-key-here...
```
3. Make sure there are no extra spaces or quotes

---

### Issue 4: Database Error

**Error**: "Database error" or "no such table: orders"

**Solution**:
```bash
# Recreate the database
py create_sample_data.py
```

---

### Issue 5: Template Not Found

**Error**: `jinja2.exceptions.TemplateNotFound: index.html`

**Solution**:
1. Check that `templates` folder exists
2. Check that `templates/index.html` exists
3. Run from the correct directory:
```bash
cd "C:\Users\HARI\Desktop\Teja\CRUD Agent"
py app.py
```

---

### Issue 6: Async/Await Errors

**Error**: "RuntimeError: Event loop is closed" or similar

**This has been fixed in the updated app.py**. If you still see this:
1. Make sure you're using the latest `app.py`
2. The code now uses `asyncio.new_event_loop()` to handle async properly

---

### Issue 7: Can't Access from Browser

**Error**: Browser can't connect or shows "Connection refused"

**Solution**:
1. Check the server is actually running (look for "Running on http://...")
2. Try these URLs in order:
   - http://localhost:5000
   - http://127.0.0.1:5000
   - http://0.0.0.0:5000
3. Check Windows Firewall isn't blocking Python
4. Make sure you're in the right browser tab (not trying to access an old URL)

---

### Issue 8: Chat Not Working / No Response

**Error**: Messages send but no response comes back

**Solution**:
1. Open browser console (Press F12 → Console tab)
2. Look for error messages
3. Check the Python terminal for errors
4. Verify your OpenAI API key is valid
5. Check your internet connection

**Common console errors**:
- `Failed to fetch` → Server not running or wrong URL
- `500 Internal Server Error` → Check Python terminal for detailed error
- `Empty message` → Input field was empty

---

### Issue 9: Slow Responses

**Issue**: AI takes a long time to respond

**This is normal!** OpenAI's API can take 1-5 seconds depending on:
- Your internet speed
- OpenAI's server load
- Complexity of the query

**To speed up**:
1. Use a faster model in `simple_agent.py`:
```python
self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

---

### Issue 10: CORS Errors

**Error**: "CORS policy" errors in browser console

**Solution**: Already fixed! The app includes `flask-cors`. If you still see this:
```bash
py -m pip install flask-cors
```

---

## 🛠️ Diagnostic Tool

**Run the diagnostic script to check everything**:
```bash
py test_app.py
```

This will check:
- ✓ Python version
- ✓ Required modules
- ✓ .env file and API key
- ✓ Database
- ✓ Templates
- ✓ Agent initialization
- ✓ Port availability

---

## 📞 Quick Checks

### Is the server running?
Look for this in your terminal:
```
* Running on http://127.0.0.1:5000
```

### Is the database working?
```bash
py -c "from database import db; print(db.execute_query('SELECT COUNT(*) FROM products'))"
```

### Is the API key set?
```bash
py -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Key found' if os.getenv('OPENAI_API_KEY') else 'Key NOT found')"
```

---

## 🔍 Common Error Messages & Fixes

| Error | Meaning | Fix |
|-------|---------|-----|
| `Port 5000 is already in use` | Server already running | Open browser or kill process |
| `ModuleNotFoundError` | Missing Python package | Run `pip install -r requirements.txt` |
| `OPENAI_API_KEY not set` | No API key in .env | Add key to .env file |
| `Template not found` | Missing templates folder | Check templates/index.html exists |
| `Database is locked` | Another process using DB | Close other connections |
| `Failed to fetch` | Server not running | Start server with `py app.py` |

---

## 🚀 Clean Restart

If nothing works, try a clean restart:

```bash
# 1. Stop any running servers (Ctrl+C)

# 2. Check everything is installed
py test_app.py

# 3. Kill any process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# 4. Start fresh
py app.py

# 5. Open browser
# Go to: http://localhost:5000
```

---

## 💡 Still Having Issues?

1. **Check the terminal output** - Most errors are shown there
2. **Check browser console** (F12) - Frontend errors appear here
3. **Run the diagnostic**: `py test_app.py`
4. **Verify file structure**:
```
CRUD Agent/
├── app.py              ← Main server file
├── simple_agent.py     ← AI agent
├── database.py         ← Database
├── tools.py            ← CRUD tools
├── .env                ← API key here
├── templates/
│   └── index.html      ← Web interface
└── ecommerce.db        ← Database file
```

---

## ✅ Success Checklist

Before running the app, ensure:
- [ ] All dependencies installed (`py -m pip install -r requirements.txt`)
- [ ] `.env` file exists with valid `OPENAI_API_KEY`
- [ ] `templates/index.html` file exists
- [ ] Database created (`py create_sample_data.py`)
- [ ] Port 5000 is available (or use different port)
- [ ] Running from correct directory

---

**Most Common Issue**: The server is already running! Just open http://localhost:5000 in your browser.