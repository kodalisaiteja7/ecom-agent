"""
Quick test script to diagnose any issues with the web app.
Run this to check if everything is configured correctly.
"""
import sys
import os
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 70)
print("DIAGNOSTIC TEST FOR WEB APPLICATION")
print("=" * 70)
print()

# Test 1: Check Python version
print("1. Checking Python version...")
print(f"   Python {sys.version}")
if sys.version_info < (3, 8):
    print("   ⚠️  WARNING: Python 3.8+ recommended")
else:
    print("   ✓ Python version OK")
print()

# Test 2: Check required modules
print("2. Checking required modules...")
required_modules = [
    'flask',
    'flask_cors',
    'langchain_openai',
    'dotenv',
]

missing_modules = []
for module in required_modules:
    try:
        __import__(module)
        print(f"   ✓ {module}")
    except ImportError:
        print(f"   ✗ {module} - NOT FOUND")
        missing_modules.append(module)

if missing_modules:
    print(f"\n   ⚠️  Missing modules: {', '.join(missing_modules)}")
    print("   Run: py -m pip install -r requirements.txt")
else:
    print("   ✓ All modules installed")
print()

# Test 3: Check .env file
print("3. Checking .env file...")
if os.path.exists('.env'):
    print("   ✓ .env file exists")

    # Load and check API key
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"   ✓ OPENAI_API_KEY is set ({api_key[:10]}...)")
    else:
        print("   ✗ OPENAI_API_KEY not set in .env file")
else:
    print("   ✗ .env file not found")
    print("   Create a .env file with: OPENAI_API_KEY=your-key-here")
print()

# Test 4: Check database
print("4. Checking database...")
if os.path.exists('ecommerce.db'):
    print("   ✓ Database file exists")
    try:
        from database import db
        products = db.execute_query("SELECT COUNT(*) as count FROM products")
        orders = db.execute_query("SELECT COUNT(*) as count FROM orders")
        print(f"   ✓ Database accessible")
        print(f"   - Products: {products[0]['count']}")
        print(f"   - Orders: {orders[0]['count']}")
    except Exception as e:
        print(f"   ✗ Database error: {e}")
else:
    print("   ⚠️  Database not found (will be created automatically)")
print()

# Test 5: Check templates
print("5. Checking templates...")
if os.path.exists('templates'):
    if os.path.exists('templates/index.html'):
        print("   ✓ templates/index.html exists")
    else:
        print("   ✗ templates/index.html not found")
else:
    print("   ✗ templates directory not found")
print()

# Test 6: Check agent
print("6. Testing agent...")
try:
    from simple_agent import SimpleEcommerceAgent
    print("   ✓ SimpleEcommerceAgent imported")

    # Quick test (without calling API)
    agent = SimpleEcommerceAgent()
    print("   ✓ Agent initialized")
except Exception as e:
    print(f"   ✗ Agent error: {e}")
print()

# Test 7: Check port availability
print("7. Checking port 5000...")
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5000))
    if result == 0:
        print("   ⚠️  Port 5000 is already in use")
        print("   Stop the running server or use a different port")
    else:
        print("   ✓ Port 5000 is available")
    sock.close()
except Exception as e:
    print(f"   ⚠️  Could not check port: {e}")
print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)

if not missing_modules and os.path.exists('.env') and os.getenv('OPENAI_API_KEY'):
    print("✓ All checks passed! You can run the web app with:")
    print()
    print("  py app.py")
    print()
    print("  Or double-click: run_web.bat")
    print()
else:
    print("⚠️  Some issues found. Please fix them and try again.")
    print()
    if missing_modules:
        print("1. Install missing modules:")
        print("   py -m pip install -r requirements.txt")
        print()
    if not os.path.exists('.env') or not os.getenv('OPENAI_API_KEY'):
        print("2. Set up .env file with your OpenAI API key:")
        print("   OPENAI_API_KEY=your-key-here")
        print()

print("=" * 70)