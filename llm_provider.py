import os
from dotenv import load_dotenv
try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import SystemMessage, HumanMessage
except ImportError:
    ChatGroq = None

load_dotenv()

class LLMProvider:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_key = os.getenv("GROQ_API_KEY")
        # Set force_mock to False to use the Real AI (Groq)
        self.force_mock = False 
        
        self.llm = None
        if self.api_key and not self.force_mock and ChatGroq:
            try:
                self.llm = ChatGroq(
                    temperature=0, 
                    groq_api_key=self.api_key, 
                    model_name="llama-3.3-70b-versatile"
                )
            except Exception as e:
                print(f"Failed to init ChatGroq: {e}")
    
    def generate(self, system_prompt, user_message):
        """
        Generates a response from the LLM or Mock.
        """
        if self.force_mock or not self.llm:
            return self.mock_generate(system_prompt, user_message)
            
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"LLM Error: {e}")
            return self.mock_generate(system_prompt, user_message)

    def mock_generate(self, system_prompt, user_message):
        """Simple rule-based mock for testing without API cost/latency"""
        msg = user_message.lower()
        
        # Orchestrator Mock
        if "orchestrator" in system_prompt.lower():
            if any(w in msg for w in ['buy', 'price', 'iphone', 'macbook', 'samsung', 'stock']):
                return 'SALES'
            if any(w in msg for w in ['order', 'status', 'broken', 'return', 'help']):
                return 'SUPPORT'
            return 'CHIT_CHAT'
            
        # Sales Mock
        if "sales agent" in system_prompt.lower():
            return "Mock Sales: I can see you are interested in our products! We have iPhones and MacBooks in stock."
            
        # Support Mock
        if "support agent" in system_prompt.lower():
            return "Mock Support: Please provide your Order ID so I can look up the status."
            
        # Supervisor Mock
        if "supervisor" in system_prompt.lower():
            return "APPROVED"
            
        return "I am a simple Mock Agent. Set force_mock=False in llm_provider.py to use real AI."

# Singleton instance
try:
    llm_provider = LLMProvider()
except Exception as e:
    print(f"Failed to initialize LLM Provider: {e}")
    llm_provider = None
