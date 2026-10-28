# Multi-Agent Chatbot

Customer-service assistant for a small online electronics shop, in French. An orchestrator
reads each message, decides whether it is about buying something, about an existing order
or just small talk, and hands it to a sales agent or a support agent. Both agents run
Llama 3.3 70B through the Groq API with LangChain and call tools that query a MariaDB
database: catalogue, stock, promotions, reviews, clients, orders, deliveries, invoices,
warranties. A Flask server exposes a REST API and a small web UI with a trace panel that
shows which agent answered and which tools it called. NLP module project, CY Tech ING3,
2025-2026, with Amine Filali: Amine set up the Flask server, the web page and the first
orchestrator and prompts; I wrote the MariaDB schema and data layer, the agents' tools and
tool loop, the orchestrator memory, the Docker setup, the tests and the documentation.

![Web UI](docs/screenshots/ui.png)

## How a message is handled

```
browser / curl
     |  POST /api/chat {message, conversation_id, mode}
     v
server.py (Flask)
     v
agents/orchestrator.py   routing prompt -> SALES / SUPPORT / GENERAL
     |                   memory: last 10 messages per conversation_id
     +-- SALES   -> agents/sales.py    5 tools: search, details, stock, promotions, reviews
     +-- SUPPORT -> agents/support.py  7 tools: client by reference or email, orders,
     |                                 order details, delivery, invoice, warranty
     +-- GENERAL -> plain chat answer
                        v
              core/database_mysql.py   parameterised SQL, MariaDB in Docker
                                       (21 tables: 38 products, 6 clients, 15 orders, ...)
```

Routing is one LLM call with a short prompt and the last four messages as context, so a
follow-up question stays with the same agent. Each agent is a system prompt plus a list of
LangChain tools (`agents/base.py`): the model is called with the tools bound, the tool
calls it returns are executed and their results fed back, up to four rounds, then the
final text goes to the user. The prompts ask for short French answers and forbid inventing
a price or an order status when a tool returns nothing. The memory window is shared by
both agents, so a conversation can move from sales to support without losing what was
said. A "baseline" mode (same model, one call, no routing, no tools) is there for
comparison: it cannot check a stock or an order.

## Running it

Python 3.10+, Docker (MariaDB and phpMyAdmin run in containers) and a Groq API key (free
tier at https://console.groq.com).

```bash
pip install -r requirements.txt
cp .env.example .env          # put your GROQ_API_KEY in it
docker compose up -d          # MariaDB on localhost:3308, seeded on first start; phpMyAdmin on :3009
python server.py              # http://localhost:5000
```

`make help` lists the same steps as Make targets; `make db-init` reloads the two SQL files
into a running container. The API takes JSON and returns `response`, `agent` (SALES,
SUPPORT, GENERAL or BASELINE), `tools_used` and a `trace`:

```bash
curl -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" \
  -d '{"message": "Où en est ma commande CMD-2026-0002 ?", "conversation_id": "demo"}'
```

Test data: orders `CMD-2026-0001` to `CMD-2026-0015`, client reference `1000000000123`,
email `alice.martin@gmail.com`, products such as "iPhone 15", "Dell XPS", "PlayStation 5".

## Tests

`python tests/test_tool_loop.py` runs offline, without a key or a database: a scripted fake
model checks that tool calls are executed and fed back, that unknown tools and model errors
are handled, that the memory is a 10-message window kept per conversation, and that the
routing decision is parsed (6 tests). `python tests/test_all_scenarios.py` sends 15
scripted questions (`tests/scenarios.json`) to a running server, checks that the expected
agent answered and that the reply is short, non-empty and free of technical vocabulary, and
writes a JSON report to `tests/results/`. In the January 2026 run all 15 scenarios produced
a valid short French answer; routing accuracy was not measured at the time.

## Limitations

- Everything depends on the Groq API; without a key the server starts but `/api/chat` answers 503.
- Memory lives in the server process and is lost on restart. Clients identify themselves
  by typing a reference or an email; there is no authentication.
- `core/context_manager.py`, `core/smart_extractor.py` and `forms/form_manager.py`
  (progressive data collection with validation) are not plugged into the request path;
  the agents rely on the prompt to ask for missing information. Wiring the form manager
  into the support agent is the next step.
- The scenario runner checks the shape of the answer and the routing, not the facts in it.
- Promotions have fixed dates in the seed data, so the active ones depend on today's date.
