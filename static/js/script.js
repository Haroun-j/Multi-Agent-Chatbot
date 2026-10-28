// Chat UI: sends messages to /api/chat and shows the orchestrator trace on the right.
const API_URL = '/api';

// One conversation id per page load, so the server keeps a separate memory per tab.
const CONVERSATION_ID = 'web-' + Math.random().toString(36).slice(2, 10);

const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const clearButton = document.getElementById('clearButton');
const agentMode = document.getElementById('agentMode');
const traceLog = document.getElementById('traceLog');

function escapeHtml(text) {
    return text.replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function addMessage(content, role, agent) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    let html = `<div>${escapeHtml(content)}</div>`;
    if (agent) {
        html += `<div class="agent-tag">${escapeHtml(agent)}</div>`;
    }
    messageDiv.innerHTML = html;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addTrace(text) {
    const entry = document.createElement('div');
    entry.className = 'trace-entry';
    entry.textContent = text;
    traceLog.appendChild(entry);
    traceLog.scrollTop = traceLog.scrollHeight;
}

async function sendMessage(message) {
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                mode: agentMode.value,
                conversation_id: CONVERSATION_ID
            })
        });

        const data = await response.json();
        if (data.trace) {
            data.trace.forEach(line => addTrace(line));
        }
        if (!response.ok) {
            addTrace(`ERREUR: ${data.error || response.status}`);
            return { text: "Désolé, le serveur n'a pas pu répondre.", agent: null };
        }
        return { text: data.response, agent: data.agent };
    } catch (error) {
        console.error('Error:', error);
        addTrace(`ERREUR: ${error.message}`);
        return { text: "Désolé, j'ai rencontré une erreur technique.", agent: null };
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

    const reply = await sendMessage(message);
    addMessage(reply.text, 'assistant', reply.agent);

    messageInput.disabled = false;
    sendButton.disabled = false;
    messageInput.focus();
});

clearButton.addEventListener('click', async () => {
    await fetch(`${API_URL}/clear`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation_id: CONVERSATION_ID })
    });
    chatMessages.innerHTML = '';
    traceLog.innerHTML = '<div class="trace-entry">Historique effacé.</div>';
    addMessage("Historique de conversation effacé.", "assistant");
});
