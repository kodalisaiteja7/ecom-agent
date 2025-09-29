"""
Flask Web Application for E-Commerce AI Customer Support.
Modern, responsive chat interface with real-time AI responses.
"""
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import asyncio
import os
import secrets
from datetime import datetime
from simple_agent import SimpleEcommerceAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Store agent instances per session
agents = {}


def get_agent():
    """Get or create agent for current session."""
    session_id = session.get('session_id')

    if not session_id:
        session_id = secrets.token_hex(8)
        session['session_id'] = session_id

    if session_id not in agents:
        agents[session_id] = SimpleEcommerceAgent()

    return agents[session_id]


@app.route('/')
def index():
    """Render the main chat interface."""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the user."""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Get agent for this session
        agent = get_agent()

        # Process message synchronously using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(agent.process_message(user_message))
        loop.close()

        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        import traceback
        print(f"Error in chat endpoint: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset the conversation."""
    try:
        session_id = session.get('session_id')

        if session_id and session_id in agents:
            agents[session_id].reset()

        return jsonify({'message': 'Conversation reset successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(agents)
    })


if __name__ == '__main__':
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\nERROR: OPENAI_API_KEY environment variable not set!")
        print("Please check your .env file.\n")
        print("Current .env file should contain:")
        print("OPENAI_API_KEY=your-key-here\n")
        exit(1)

    print("\n" + "=" * 70)
    print("E-COMMERCE AI CUSTOMER SUPPORT - WEB APPLICATION")
    print("=" * 70)
    print("\nStarting server...")
    print("Open your browser and navigate to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70 + "\n")

    try:
        # Run Flask app
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except Exception as e:
        print(f"\nError starting server: {e}")
        print("Try running on a different port:")
        print("py app.py --port 5001")
        exit(1)