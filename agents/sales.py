from langchain_groq import ChatGroq
from langchain.tools import tool
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database_mysql import *

# === TOOLS: Database Functions === 

@tool
def search_products_tool(category: str = None, min_price: float = None, max_price: float = None, 
                         brand: str = None, keyword: str = None):
    """
    Recherche de produits dans le catalogue.
    
    Args:
        category: Nom de catégorie (ex: "Smartphones", "Audio")
        min_price: Prix minimum
        max_price: Prix maximum  
        brand: Marque (ex: "Apple", "Samsung")
        keyword: Mot-clé dans nom/description
    
    Returns: Liste de produits avec détails
    """
    results = get_products(category, min_price, max_price, brand, keyword)
    if not results:
        return "Aucun produit trouvé avec ces critères"
    
    output = f"Trouvé {len(results)} produit(s):\n"
    for p in results[:5]:  # Limite 5 pour éviter surcharge
        output += f"\n📱 {p['name']} - {p['prix_vente']}€"
        if p.get('brand'):
            output += f" ({p['brand']})"
    return output

@tool
def get_product_details_tool(product_id: int):
    """
    Détails complets d'un produit.
    
    Args:
        product_id: ID du produit
        
    Returns: Informations complètes (prix, stock, garantie, etc)
    """
    details = get_product_details(product_id)
    if not details:
        return f"Produit {product_id} non trouvé"
    
    return f"""
    Produit: {details['name']}
    Prix: {details['prix_vente']}€
    Stock: {details.get('stock_disponible', 'N/A')} unités
    Garantie: {details.get('warranty_months', 24)} mois
    Marque: {details.get('brand', 'N/A')}
    """

@tool
def get_active_promotions_tool():
    """
    Liste toutes les promotions en cours.
    
    Returns: Promotions actives avec réductions
    """
    promos = get_active_promotions()
    if not promos:
        return "Aucune promotion active actuellement"
    
    output = "🎉 Promotions en cours:\n"
    for promo in promos:
        output += f"\n• {promo['name']} - {promo['discount_percentage']}%"
        if promo.get('description'):
            output += f"\n  {promo['description']}"
    return output

@tool
def check_product_stock_tool(product_id: int):
    """
    Vérifie le stock disponible d'un produit.
    
    Args:
        product_id: ID du produit
        
    Returns: Quantité en stock
    """
    stock = get_product_stock(product_id)
    if stock is None:
        return f"Stock non disponible pour produit {product_id}"
    return f"Stock disponible: {stock['disponible']} unités (Total: {stock['quantity']}, Réservé: {stock['reserved']})"

@tool
def get_product_reviews_tool(product_id: int):
    """
    Avis clients sur un produit.
    
    Args:
        product_id: ID du produit
        
    Returns: Liste des avis avec notes
    """
    reviews = get_product_reviews(product_id)
    if not reviews:
        return "Aucun avis client pour ce produit"
    
    avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
    output = f"⭐ Note moyenne: {avg_rating:.1f}/5 ({len(reviews)} avis)\n"
    
    for review in reviews[:3]:
        output += f"\n{review['rating']}⭐ - {review.get('title', 'Sans titre')}"
    return output

# === AGENT CONFIGURATION ===

class SalesAgent:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)
        
        # Tools disponibles
        self.tools = [
            search_products_tool,
            get_product_details_tool,
            get_active_promotions_tool,
            check_product_stock_tool,
            get_product_reviews_tool
        ]
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Historique
        self.message_history = []
    
    def _summarize_context(self):
        """Résumé des 10 derniers messages"""
        if not self.message_history:
            return "Nouvelle conversation"
        
        recent = self.message_history[-10:]
        summary = f"Derniers {len(recent)} échanges:\n"
        for msg in recent:
            role = "Client" if msg['role'] == 'user' else "Moi"
            summary += f"{role}: {msg['content'][:60]}...\n"
        return summary
    
    def process(self, user_message: str):
        """Traite un message utilisateur"""
        self.message_history.append({'role': 'user', 'content': user_message})
        
        context_summary = self._summarize_context()
        
        system_msg = f"""Assistant commercial intelligent.

REGLES ABSOLUES:
1. FRANÇAIS UNIQUEMENT - jamais d'anglais
2. JAMAIS mentionner "fonction", "outil", "base de données", "tool", "search_products_tool" ou tout terme technique
3. AGIS DIRECTEMENT - si user demande smartphones, CHERCHE immédiatement (appel silencieux)
4. REPONSES ULTRA-COURTES - 1-2 phrases max
5. Questions génériques ("aide", "bonjour", "help"): réponds gentiment en français

CONTEXTE: {context_summary}

COMPORTEMENT:
- "smartphones" → CHERCHE direct, liste résultats
- "laptops gaming" → CHERCHE category=Laptops, keyword=gaming, liste résultats  
- "promotions" → LISTE promos direct
- "aide" ou "help" → "Que puis-je faire pour vous aujourd'hui?"
- "bonjour" → "Bonjour! Que puis-je faire pour vous aujourd'hui?"

EXEMPLE PARFAIT:
User: "smartphones"
Toi: [APPEL SILENCIEUX search_products_tool] "Nous avons iPhone 15 (999€), Samsung S24 (850€), Pixel 8 (699€). Lequel vous intéresse?"

EXEMPLE INTERDIT:
Toi: "Je vais utiliser search_products_tool pour..." ❌
Toi: "Laissez-moi chercher dans la base..." ❌

DONNE LE RESULTAT, PAS LE PROCESSUS."""

        try:
            # Simple invocation without agent executor
            response = self.llm.invoke([
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_message}
            ])
            
            response_text = response.content
            self.message_history.append({'role': 'assistant', 'content': response_text})
            
            return response_text
            
        except Exception as e:
            error_msg = f"Erreur: {str(e)}"
            self.message_history.append({'role': 'assistant', 'content': error_msg})
            return error_msg
