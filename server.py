from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os
import traceback

# Import Orchestrator  
from agents.orchestrator import Orchestrator

app = Flask(__name__, static_folder='.')
CORS(app)

# Initialize Orchestrator
try:
    orchestrator = Orchestrator()
    print("✅ Orchestrateur Initialisé (Agents avec Outils DB)")
    print("   → Sales Agent: 5 outils (produits, stock, promos)")
    print("   → Support Agent: 7 outils (commandes, livraisons, factures)")
except Exception as e:
    print(f"❌ Erreur init: {e}")
    traceback.print_exc()

# Global message history
message_history = []

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    mode = data.get('mode', 'multi')  # 'multi' or 'mono'
    conversation_id = data.get('conversation_id', 'default')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Trace log to send back to UI
    trace_log = []
    response_text = ""
    
    start_time = datetime.now()
    
    try:
        # Log start
        trace_log.append(f"[{start_time.strftime('%H:%M:%S')}] New message received")
        trace_log.append(f"Mode: {'MULTI-AGENT (Advanced)' if mode == 'multi' else 'MONO-AGENT'}")
        trace_log.append(f"Conversation ID: {conversation_id}")
        
        if mode == 'mono':
            # Simple fallback for mono mode
            trace_log.append("Using fallback mono-agent mode")
            response_text = "Mono-agent mode...Running in multi-agent mode is recommended for better functionality. Try switching to multi-agent!"
        else:
            # Multi-Agent with Tool Calling
            trace_log.append("=" * 50)
            trace_log.append("🤖 Orchestrateur Multi-Agents")
            
            # Process with routing
            result = orchestrator.process(user_message, conversation_id)
            
            agent_used = result.get('agent', 'N/A')
            trace_log.append(f"📍 Agent assigné: {agent_used}")
            trace_log.append(f"🛠️  Outils DB disponibles: {'5 tools' if agent_used == 'SALES' else '7 tools'}")
            
            response_text = result.get('response', 'Erreur traitement')
            
            trace_log.append("=" * 50)
            trace_log.append(f"Réponse: {len(response_text)} chars")
            
    except Exception as e:
        trace_log.append(f"ERROR: {str(e)}")
        trace_log.append("Stack trace:")
        trace_log.extend(traceback.format_exc().split('\n'))
        response_text = f"❌ Internal Error: {str(e)}\n\nPlease try again or rephrase your question."
        print(f"Error in chat processing: {e}")
        traceback.print_exc()

    # Store history
    message_history.append({
        'role': 'user',
        'content': user_message,
        'timestamp': start_time.isoformat()
    })
    message_history.append({
        'role': 'assistant',
        'content': response_text,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({
        'response': response_text,
        'trace': trace_log,
        'timestamp': datetime.now().isoformat(),
        'conversation_id': conversation_id
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify({'messages': message_history})

@app.route('/api/clear', methods=['POST'])
def clear_history():
    global message_history
    message_history = []
    return jsonify({'status': 'cleared'})

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        import database_mysql as db
        db_connected = db.test_connection()
        return jsonify({
            'status': 'healthy',
            'database': 'connected' if db_connected else 'disconnected',
            'orchestrator': 'advanced',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 SYSTÈME MULTI-AGENTS E-COMMERCE")
    print("=" * 60)
    print("Server: http://localhost:5000")
    print("Architecture:")
    print("  🤖 Agents avec outils DB (LangChain)")
    print("  🧠 Contexte: 10 derniers messages")
    print("  🔧 12 fonctions database (tools)")
    print("  💬 Questions intelligentes pour params")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5000)
