"""
Orchestrator: classifies the intent of each message (SALES / SUPPORT / GENERAL)
and hands it to the right agent. It also owns the conversation memory, one
window of the last messages per conversation_id, shared by both agents so a
hand-off from sales to support keeps the context.
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agents.base import MEMORY_SIZE, message_text
from agents.sales import SalesAgent
from agents.support import SupportAgent
from core.llm_provider import get_chat_model

ROUTING_PROMPT = """Tu es un routeur qui assigne les demandes d'une boutique en ligne au bon agent.

AGENTS DISPONIBLES
- SALES : produits, catalogue, promotions, stock, prix, conseils d'achat
- SUPPORT : commandes, livraisons, factures, SAV, garanties, retours, réclamations
- GENERAL : salutations, questions génériques ou hors sujet

Tiens compte des derniers échanges : une question de suivi reste chez le même agent.
Si un message mêle un achat et un problème de commande, choisis SUPPORT.
Réponds UNIQUEMENT par un mot : SALES, SUPPORT ou GENERAL.

Exemples
"Je cherche un smartphone" -> SALES
"Où est ma commande ?" -> SUPPORT
"Bonjour" -> GENERAL
"Quelles promos ?" -> SALES
"J'ai un problème avec mon colis" -> SUPPORT
"Combien coûte l'iPhone ?" -> SALES
"Votre service de livraison est terrible" -> SUPPORT"""

GENERAL_PROMPT = (
    "Tu es l'assistant d'une boutique en ligne d'électronique. Réponds poliment, "
    "brièvement et en français. Si la personne a besoin d'aide sur des produits "
    "ou des commandes, invite-la à préciser sa demande."
)

BASELINE_PROMPT = (
    "Tu es l'assistant d'une boutique en ligne d'électronique. Réponds en français, "
    "brièvement. Tu n'as pas accès au catalogue ni aux commandes : si on te demande "
    "un prix, un stock ou le statut d'une commande, explique que tu ne peux pas le vérifier."
)

AGENTS = ("SALES", "SUPPORT", "GENERAL")


class Orchestrator:
    def __init__(self, router=None, general=None, sales_agent=None, support_agent=None):
        # The models can be injected (tests use scripted fakes).
        self.router = router or get_chat_model(temperature=0.0)
        self.general_chat = general or get_chat_model(temperature=0.7)
        self.sales_agent = sales_agent or SalesAgent()
        self.support_agent = support_agent or SupportAgent()
        self.conversations = {}   # conversation_id -> list of HumanMessage / AIMessage

    # --- memory -----------------------------------------------------------

    def history(self, conversation_id):
        return self.conversations.setdefault(conversation_id, [])

    def remember(self, conversation_id, user_message, answer):
        history = self.history(conversation_id)
        history.append(HumanMessage(content=user_message))
        history.append(AIMessage(content=answer))
        del history[:-MEMORY_SIZE]

    def reset(self, conversation_id=None):
        if conversation_id is None:
            self.conversations.clear()
        else:
            self.conversations.pop(conversation_id, None)

    # --- routing ----------------------------------------------------------

    @staticmethod
    def parse_decision(text):
        decision = (text or "").strip().upper()
        for agent in AGENTS:
            if agent in decision:
                return agent
        return "GENERAL"

    def route_message(self, user_message, history=None):
        """Return SALES, SUPPORT or GENERAL. Falls back to GENERAL if the model fails."""
        messages = [SystemMessage(content=ROUTING_PROMPT)]
        messages.extend((history or [])[-4:])   # a short context helps follow-up questions
        messages.append(HumanMessage(content=user_message))
        try:
            result = self.router.invoke(messages)
            return self.parse_decision(message_text(result.content))
        except Exception as exc:
            print(f"[orchestrator] routing failed, using GENERAL: {exc}")
            return "GENERAL"

    # --- entry points -----------------------------------------------------

    def process(self, user_message, conversation_id="default"):
        """Route the message, let the chosen agent answer, update the memory."""
        history = self.history(conversation_id)
        agent = self.route_message(user_message, history)
        tools_used = []

        if agent == "SALES":
            answer = self.sales_agent.process(user_message, history)
            tools_used = list(self.sales_agent.last_tool_calls)
        elif agent == "SUPPORT":
            answer = self.support_agent.process(user_message, history)
            tools_used = list(self.support_agent.last_tool_calls)
        else:
            answer = self._chat(self.general_chat, GENERAL_PROMPT, user_message, history)

        self.remember(conversation_id, user_message, answer)
        return {
            'response': answer,
            'agent': agent,
            'tools_used': tools_used,
            'conversation_id': conversation_id,
        }

    def baseline(self, user_message, conversation_id="default"):
        """Single-model answer without routing or tools, used as the comparison point in the UI."""
        key = f"{conversation_id}:baseline"
        history = self.history(key)
        answer = self._chat(self.general_chat, BASELINE_PROMPT, user_message, history)
        self.remember(key, user_message, answer)
        return {
            'response': answer,
            'agent': 'BASELINE',
            'tools_used': [],
            'conversation_id': conversation_id,
        }

    @staticmethod
    def _chat(model, system_prompt, user_message, history):
        messages = [SystemMessage(content=system_prompt)]
        messages.extend(history[-MEMORY_SIZE:])
        messages.append(HumanMessage(content=user_message))
        try:
            return message_text(model.invoke(messages).content)
        except Exception as exc:
            return (
                "Désolé, une erreur technique est survenue "
                f"({type(exc).__name__}). Pouvez-vous reformuler votre demande ?"
            )
