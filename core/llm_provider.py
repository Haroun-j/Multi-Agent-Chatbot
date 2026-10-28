"""
Single place where chat models are created.

The project talks to Llama 3.3 70B through Groq's API (langchain-groq). The key
is read from GROQ_API_KEY; the model can be changed with GROQ_MODEL. There is
no local or offline backend: without a key the agents cannot answer, which is
why server.py reports a clear error instead of starting half-configured.
"""

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

DEFAULT_MODEL = "llama-3.3-70b-versatile"


def get_chat_model(temperature=0.2, **kwargs):
    """Return a ChatGroq instance configured from the environment."""
    model = os.getenv("GROQ_MODEL", DEFAULT_MODEL)
    return ChatGroq(model=model, temperature=temperature, **kwargs)
