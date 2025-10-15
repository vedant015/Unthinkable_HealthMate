import os
import uuid
import json
import time
from flask import Flask, request, jsonify, render_template
from llm_helper import call_llm
from store import ConversationStore
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
store = ConversationStore(db_path=os.getenv('CONV_DB', 'conversations.db'))
# store.clear_all()    
@app.route('/')
def index():
    return render_template('index.html')


# 🧠 Chat API
@app.route('/api/chat', methods=['POST'])
def chat():
    payload = request.get_json() or {}
    session_id = payload.get('session_id') or str(uuid.uuid4())
    message = (payload.get('message') or '').strip()

    if not message:
        return jsonify({'error': 'message is required'}), 400

    # 🔹 Create session if new
    if not payload.get('session_id'):
        # Create new session record
        store.create_session(session_id, "New Chat")


    # Append user's message to conversation history
    store.append(session_id, 'user', message)

    # Prepare messages for the LLM
    messages = store.get_messages_for_llm(session_id)

    try:
        response_text = call_llm(messages)
    except Exception as e:
        return jsonify({'error': 'LLM call failed', 'details': str(e)}), 500

    # Try to parse JSON output from LLM
    try:
        obj = json.loads(response_text)
    except Exception:
        store.append(session_id, 'assistant', response_text)
        return jsonify({'error': 'LLM output not valid JSON', 'raw': response_text}), 500

    mode = obj.get('mode')

    if mode == 'ask':
        question = obj.get('question')
        store.append(session_id, 'assistant', question)

        # Rename session based on the first user message (for sidebar title)
        store.rename_session(session_id, message[:40])  

        return jsonify({'session_id': session_id, 'mode': 'ask', 'question': question})

    if mode == 'answer':
        store.append(session_id, 'assistant', json.dumps(obj))
        return jsonify({'session_id': session_id, 'mode': 'answer', 'result': obj})

    store.append(session_id, 'assistant', response_text)
    return jsonify({'error': 'Unknown mode from LLM', 'raw': obj}), 500


# 🗂️ Get list of previous chat sessions
@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    sessions = store.get_sessions()
    return jsonify(sessions)


# 💬 Get messages of a specific session
@app.route('/api/messages/<session_id>', methods=['GET'])
def get_messages(session_id):
    messages = store.get_messages(session_id)
    return jsonify(messages)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
