from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from agents.sales import SalesAgent
from agents.support import SupportAgent

class Orchestrator:
    """Orchestrateur qui route intelligemment vers les agents spécialisés"""
    
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
        
        # Créer agents
        self.sales_agent = SalesAgent()
        self.support_agent = SupportAgent()
        
        # Prompt pour routing
        self.routing_prompt = ChatPromptTemplate.from_messages([
            ("system", """Tu es un routeur intelligent qui assigne les demandes aux bons agents.

**AGENTS DISPONIBLES:**
- SALES: Produits, catalogue, promotions, stock, prix, achats
- SUPPORT: Commandes, livraisons, factures, SAV, garanties, retours
- GENERAL: Salutations, questions génériques, blagues, ou hors sujet

**INSTRUCTIONS:**
Analyse la demande et réponds UNIQUEMENT avec: SALES, SUPPORT, ou GENERAL

Exemples:
"Je cherche un smartphone" → SALES
"Où est ma commande?" → SUPPORT
"Bonjour" → GENERAL
"Ça va?" → GENERAL
"Quelles promos?" → SALES
"J'ai un problème avec mon colis" → SUPPORT
"Combien coûte l'iPhone?" → SALES"""),
            ("human", "{input}")
        ])
        
        self.router_chain = self.routing_prompt | self.llm
        self.general_chat = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
    
    def route_message(self, user_message: str) -> str:
        """Détermine l'agent approprié"""
        try:
            result = self.router_chain.invoke({"input": user_message})
            decision = result.content.strip().upper()
            
            if "SALES" in decision:
                return "SALES"
            elif "SUPPORT" in decision:
                return "SUPPORT"
            elif "GENERAL" in decision:
                return "GENERAL"
            else:
                return "GENERAL"  # Fallback plus logique
        except:
            return "GENERAL"  # Fallback
    
    def process(self, user_message: str, conversation_id: str = "default"):
        """
        Traite un message utilisateur avec routage intelligent.
        """
        # Routage intelligent
        assigned_agent = self.route_message(user_message)
        
        # Déléguer ou répondre directement
        if assigned_agent == "SALES":
            response = self.sales_agent.process(user_message)
        elif assigned_agent == "SUPPORT":
            response = self.support_agent.process(user_message)
        else:
            # Réponse directe pour GENERAL
            response = self.general_chat.invoke([
                ("system", "Tu es un assistant e-commerce serviable. Réponds poliment et brièvement. Si l'utilisateur a besoin d'aide pour des produits ou des commandes, guide-le."),
                ("human", user_message)
            ]).content
        
        return {
            'response': response,
            'agent': assigned_agent,
            'conversation_id': conversation_id
        }
