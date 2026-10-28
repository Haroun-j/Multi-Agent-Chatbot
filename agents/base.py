"""
Shared machinery for the specialised agents: the tool-calling loop and the
short-term memory window.

An agent is a system prompt plus a list of LangChain tools. process() sends the
prompt, the last MEMORY_SIZE messages of the conversation and the new user
message to the model; while the model answers with tool calls, the tools are
executed and their results fed back, up to MAX_TOOL_ROUNDS times. The final
text is returned to the orchestrator.
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from core.llm_provider import get_chat_model

MAX_TOOL_ROUNDS = 4   # tool call / result cycles allowed for one user message
MEMORY_SIZE = 10      # previous messages (user + assistant) given to the model


def message_text(content):
    """Model content can be a string or a list of blocks; return plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                parts.append(part.get("text", ""))
            else:
                parts.append(str(part))
        return "".join(parts)
    return str(content)


class ToolAgent:
    name = "AGENT"
    temperature = 0.2
    tools = []

    def __init__(self, llm=None):
        # llm can be injected (tests use a scripted fake model)
        self.llm = llm or get_chat_model(temperature=self.temperature)
        self.llm_with_tools = self.llm.bind_tools(self.tools) if self.tools else self.llm
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        self.last_tool_calls = []   # tool names used for the last answer, shown in the UI trace

    def system_prompt(self):
        raise NotImplementedError

    def process(self, user_message, history=None):
        """Answer one user message. history is the list of previous messages (not modified here)."""
        messages = [SystemMessage(content=self.system_prompt())]
        messages.extend((history or [])[-MEMORY_SIZE:])
        messages.append(HumanMessage(content=user_message))
        self.last_tool_calls = []
        try:
            return self._run(messages)
        except Exception as exc:
            return (
                "Désolé, une erreur technique est survenue "
                f"({type(exc).__name__}). Pouvez-vous reformuler votre demande ?"
            )

    def _run(self, messages):
        for _ in range(MAX_TOOL_ROUNDS):
            response = self.llm_with_tools.invoke(messages)
            tool_calls = getattr(response, "tool_calls", None) or []
            if not tool_calls:
                return message_text(response.content)
            messages.append(response)
            for call in tool_calls:
                messages.append(ToolMessage(
                    content=str(self._call_tool(call)),
                    tool_call_id=call["id"],
                ))
        # The model kept asking for tools: ask for a final answer without them.
        final = self.llm.invoke(messages)
        return message_text(final.content)

    def _call_tool(self, call):
        name = call["name"]
        self.last_tool_calls.append(name)
        tool = self.tools_by_name.get(name)
        if tool is None:
            return f"Outil inconnu: {name}"
        try:
            return tool.invoke(call.get("args") or {})
        except Exception as exc:
            return f"Erreur lors de l'appel de {name}: {exc}"


__all__ = ["ToolAgent", "AIMessage", "HumanMessage", "MEMORY_SIZE", "message_text"]
