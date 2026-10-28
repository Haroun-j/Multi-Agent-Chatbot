// API endpoint
const API_URL = '/api';

// Get DOM elements
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const clearButton = document.getElementById('clearButton');
const agentMode = document.getElementById('agentMode');
const traceLog = document.getElementById('traceLog');

// Add message to chat
function addMessage(content, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `<div>${escapeHtml(content)}</div>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add trace entry
function addTrace(text) {
    const entry = document.createElement('div');
    entry.className = 'trace-entry';
    entry.textContent = text;
    traceLog.appendChild(entry);
    traceLog.scrollTop = traceLog.scrollHeight;
}

function escapeHtml(text) {
    // Simple escape
    return text.replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function sendMessage(message) {
    try {
        const mode = agentMode.value;
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message, mode: mode })
        });

        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();

        // Render Trace
        if (data.trace) {
            data.trace.forEach(line => addTrace(line));
        }

        return data.response;

    } catch (error) {
        console.error('Error:', error);
        addTrace(`ERREUR: ${error.message}`);
        return "Désolé, j'ai rencontré une erreur technique.";
    }
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    messageInput.value = '';
    messageInput.disabled = true;
    sendButton.disabled = true;

    const response = await sendMessage(message);
    addMessage(response, 'assistant');

    messageInput.disabled = false;
    sendButton.disabled = false;
    messageInput.focus();
});

clearButton.addEventListener('click', async () => {
    await fetch(`${API_URL}/clear`, { method: 'POST' });
    chatMessages.innerHTML = '';
    traceLog.innerHTML = '<div class="trace-entry">Historique effacé.</div>';
    addMessage("Historique de conversation effacé !", "assistant");
});
