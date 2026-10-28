"""
Flask API and web UI for the multi-agent assistant.

Endpoints
  GET  /              chat interface (templates/index.html)
  POST /api/chat      {"message": ..., "conversation_id": ..., "mode": "multi"|"mono"}
  GET  /api/history   messages exchanged since the server started
  POST /api/clear     forget the conversation(s)
  GET  /api/health    server and database status
"""

import os
import traceback
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, request, send_from_directory  # noqa: E402
from flask_cors import CORS  # noqa: E402

from agents.orchestrator import Orchestrator  # noqa: E402
from core import database_mysql as db  # noqa: E402

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

try:
    orchestrator = Orchestrator()
    print("Orchestrator ready: sales agent (5 tools), support agent (7 tools)")
except Exception as exc:  # usually a missing GROQ_API_KEY
    orchestrator = None
    print(f"Orchestrator not initialised: {exc}")
    print("Set GROQ_API_KEY in .env (see .env.example); the UI will load but cannot answer.")

message_history = []


@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get('message') or '').strip()
    mode = data.get('mode', 'multi')            # 'multi' (orchestrator + agents) or 'mono' (baseline)
    conversation_id = data.get('conversation_id', 'default')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    if orchestrator is None:
        return jsonify({'error': 'Orchestrator not initialised (missing GROQ_API_KEY?)'}), 503

    start = datetime.now()
    trace = [f"[{start.strftime('%H:%M:%S')}] message reçu (conversation {conversation_id})"]
    agent = 'N/A'
    tools_used = []

    try:
        if mode == 'mono':
            trace.append("Mode : baseline, un seul modèle sans routage ni outils")
            result = orchestrator.baseline(user_message, conversation_id)
        else:
            trace.append("Mode : multi-agents")
            result = orchestrator.process(user_message, conversation_id)
            trace.append(f"Agent assigné : {result['agent']}")
            if result['tools_used']:
                trace.append("Outils appelés : " + ", ".join(result['tools_used']))
            else:
                trace.append("Outils appelés : aucun")
        response_text = result['response']
        agent = result['agent']
        tools_used = result['tools_used']
    except Exception as exc:
        trace.append(f"ERREUR : {exc}")
        response_text = "Désolé, une erreur interne est survenue. Pouvez-vous réessayer ?"
        traceback.print_exc()

    elapsed = (datetime.now() - start).total_seconds()
    trace.append(f"Réponse en {elapsed:.1f}s ({len(response_text)} caractères)")

    message_history.append({'role': 'user', 'content': user_message,
                            'conversation_id': conversation_id, 'timestamp': start.isoformat()})
    message_history.append({'role': 'assistant', 'content': response_text, 'agent': agent,
                            'conversation_id': conversation_id, 'timestamp': datetime.now().isoformat()})

    return jsonify({
        'response': response_text,
        'agent': agent,
        'tools_used': tools_used,
        'trace': trace,
        'timestamp': datetime.now().isoformat(),
        'conversation_id': conversation_id,
    })


@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify({'messages': message_history})


@app.route('/api/clear', methods=['POST'])
def clear_history():
    global message_history
    data = request.get_json(silent=True) or {}
    conversation_id = data.get('conversation_id')
    if orchestrator is not None:
        orchestrator.reset(conversation_id)
    if conversation_id:
        message_history = [m for m in message_history if m.get('conversation_id') != conversation_id]
    else:
        message_history = []
    return jsonify({'status': 'cleared'})


@app.route('/api/health', methods=['GET'])
def health():
    db_ok = db.test_connection()
    status = 'healthy' if (db_ok and orchestrator is not None) else 'degraded'
    return jsonify({
        'status': status,
        'database': 'connected' if db_ok else 'disconnected',
        'orchestrator': 'ready' if orchestrator is not None else 'not initialised',
        'timestamp': datetime.now().isoformat(),
    }), (200 if status == 'healthy' else 503)


if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    print(f"Multi-agent e-commerce assistant on http://localhost:{port}")
    app.run(host='127.0.0.1', port=port, debug=os.getenv('FLASK_DEBUG') == '1')
