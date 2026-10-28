"""
Offline tests for the agents' tool-calling loop and the orchestrator's routing
and memory. No Groq key and no database are needed: the chat model is replaced
by a scripted fake and the database functions by stubs.

    python tests/test_tool_loop.py      (also works with pytest)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

# ChatGroq refuses to be built without a key; the fake models below never call it.
os.environ.setdefault("GROQ_API_KEY", "offline-test")

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage  # noqa: E402

import agents.sales as sales  # noqa: E402
import agents.support as support  # noqa: E402
from agents.orchestrator import Orchestrator  # noqa: E402


class FakeModel:
    """Replays scripted replies and records the messages it received."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def bind_tools(self, tools):
        return self

    def invoke(self, messages):
        self.calls.append(list(messages))
        if not self.replies:
            raise AssertionError("fake model called more times than scripted")
        return self.replies.pop(0)


def tool_call(name, args, call_id="call_1"):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id, "type": "tool_call"}])


def test_sales_tool_is_executed_and_result_fed_back(monkeypatch=None):
    fake = FakeModel([
        tool_call("search_products_tool", {"category": "Smartphones"}),
        AIMessage(content="Nous avons l'iPhone 15 à 999€."),
    ])
    original = sales.get_products
    sales.get_products = lambda *a, **k: [
        {"id": 2, "name": "iPhone 15 128GB", "prix_vente": 999, "brand": "Apple", "disponible": 12}
    ]
    try:
        agent = sales.SalesAgent(llm=fake)
        answer = agent.process("smartphones")
    finally:
        sales.get_products = original

    assert answer == "Nous avons l'iPhone 15 à 999€."
    assert agent.last_tool_calls == ["search_products_tool"]
    assert len(fake.calls) == 2
    second_call = fake.calls[1]
    tool_messages = [m for m in second_call if isinstance(m, ToolMessage)]
    assert len(tool_messages) == 1
    assert tool_messages[0].tool_call_id == "call_1"
    assert "iPhone 15 128GB" in tool_messages[0].content
    assert "999" in tool_messages[0].content


def test_history_window_is_passed_to_the_model():
    fake = FakeModel([AIMessage(content="Bonjour !")])
    agent = support.SupportAgent(llm=fake)
    history = [HumanMessage(content=f"m{i}") for i in range(30)]
    agent.process("bonjour", history)
    sent = fake.calls[0]
    # system prompt + last 10 history messages + the new message
    assert len(sent) == 1 + 10 + 1
    assert sent[1].content == "m20"
    assert sent[-1].content == "bonjour"


def test_unknown_tool_does_not_crash_the_loop():
    fake = FakeModel([
        tool_call("does_not_exist", {}),
        AIMessage(content="Je n'ai pas pu vérifier."),
    ])
    agent = support.SupportAgent(llm=fake)
    answer = agent.process("test")
    assert answer == "Je n'ai pas pu vérifier."
    tool_messages = [m for m in fake.calls[1] if isinstance(m, ToolMessage)]
    assert "Outil inconnu" in tool_messages[0].content


def test_model_error_gives_a_polite_answer():
    class Broken(FakeModel):
        def invoke(self, messages):
            raise RuntimeError("network down")

    agent = sales.SalesAgent(llm=Broken([]))
    answer = agent.process("smartphones")
    assert "erreur technique" in answer.lower()


def test_orchestrator_routes_and_remembers_per_conversation():
    router = FakeModel([AIMessage(content="SUPPORT"), AIMessage(content="sales"), AIMessage(content="???")])
    general = FakeModel([AIMessage(content="Bonjour, comment puis-je aider ?")])
    sales_agent = sales.SalesAgent(llm=FakeModel([AIMessage(content="Voici nos laptops.")]))
    support_agent = support.SupportAgent(llm=FakeModel([AIMessage(content="Quel est votre numéro de commande ?")]))
    orch = Orchestrator(router=router, general=general, sales_agent=sales_agent, support_agent=support_agent)

    r1 = orch.process("ma commande est cassée", conversation_id="a")
    assert r1["agent"] == "SUPPORT"
    assert r1["response"] == "Quel est votre numéro de commande ?"

    r2 = orch.process("je veux un laptop", conversation_id="b")
    assert r2["agent"] == "SALES"

    r3 = orch.process("bonjour", conversation_id="a")
    assert r3["agent"] == "GENERAL"   # unparseable decision falls back to GENERAL

    assert len(orch.history("a")) == 4   # two exchanges
    assert len(orch.history("b")) == 2
    # the general chat received conversation "a" history before the new message
    assert [m.content for m in general.calls[0][1:-1]] == ["ma commande est cassée", "Quel est votre numéro de commande ?"]

    orch.reset("a")
    assert orch.history("a") == []
    assert len(orch.history("b")) == 2


def test_parse_decision():
    assert Orchestrator.parse_decision("SALES") == "SALES"
    assert Orchestrator.parse_decision(" support ") == "SUPPORT"
    assert Orchestrator.parse_decision("Réponse: GENERAL.") == "GENERAL"
    assert Orchestrator.parse_decision("") == "GENERAL"


if __name__ == "__main__":
    tests = [obj for name, obj in sorted(globals().items()) if name.startswith("test_") and callable(obj)]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"ok    {test.__name__}")
        except Exception as exc:  # report and continue
            failed += 1
            print(f"FAIL  {test.__name__}: {type(exc).__name__} {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} tests passed")
    sys.exit(1 if failed else 0)
