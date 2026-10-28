from langchain_groq import ChatGroq
from langchain.tools import tool
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database_mysql import *

# === TOOLS: Database Functions ===

@tool
def find_client_by_reference_tool(client_reference: str):
    """
    Trouve un client par sa référence (13 chiffres).
    
    Args:
        client_reference: Référence client (ex: "1000000000123")
        
    Returns: Informations client
    """
    client = get_client_by_reference(client_reference)
    if not client:
        return f"Client {client_reference} non trouvé"
    
    return f"""
    Client trouvé:
    Nom: {client['first_name']} {client['last_name']}
    Email: {client['email']}
    Type: {client['client_type']}
    Points fidélité: {client['points_fidelite']}
    """

@tool
def find_client_by_email_tool(email: str):
    """
    Trouve un client par email.
    
    Args:
        email: Adresse email
        
    Returns: Informations client
    """
    try:
        client = get_client_by_email(email)
        if not client:
            return f"Aucun client avec l'email {email}"
        
        return f"Client: {client['first_name']} {client['last_name']} (Ref: {client['client_reference']})"
    except Exception as e:
        return f"Erreur recherche email: {str(e)}"

@tool
def get_client_orders_tool(client_id: int):
    """
    Récupère toutes les commandes d'un client.
    
    Args:
        client_id: ID du client
        
    Returns: Liste des commandes
    """
    orders = get_client_orders(client_id)
    if not orders:
        return "Aucune commande trouvée"
    
    output = f"📦 {len(orders)} commande(s):\n"
    for order in orders:
        output += f"\n• {order['order_number']} - {order['status']} - {order['total_ttc']}€"
    return output

@tool
def get_order_details_tool(order_number: str):
    """
    Détails complets d'une commande.
    
    Args:
        order_number: Numéro de commande (ex: "CMD-2026-0001")
        
    Returns: Détails avec produits, prix, statut
    """
    details = get_order_by_number(order_number)
    if not details:
        return f"Commande {order_number} non trouvée"
    
    output = f"""
    📋 Commande {details['order_number']}
    Statut: {details['status']}
    Total: {details['total_ttc']}€
    Date: {details.get('created_at', 'N/A')}
    """
    
    # Ajouter items si disponibles
    items = details.get('items', [])
    if items:
        output += "\n\nProduits:"
        for item in items:
            output += f"\n• {item.get('name', 'Produit')} x{item['quantity']} - {item['total']}€"
    
    return output

@tool
def track_delivery_tool(order_number: str):
    """
    Suivi de livraison d'une commande.
    
    Args:
        order_number: Numéro de commande
        
    Returns: Informations de livraison et tracking
    """
    tracking = get_order_delivery_status(order_number)
    if not tracking:
        return f"Aucune information de livraison pour {order_number}"
    
    return f"""
    🚚 Livraison {order_number}:
    Statut: {tracking.get('status', 'N/A')}
    Transporteur: {tracking.get('carrier', 'N/A')}
    Numéro de suivi: {tracking.get('tracking_number', 'N/A')}
    """

@tool
def get_invoice_tool(order_number: str):
    """
    Récupère la facture d'une commande.
    
    Args:
        order_number: Numéro de commande
        
    Returns: Détails de facturation
    """
    invoice = get_invoice_by_order(order_number)
    if not invoice:
        return f"Aucune facture pour {order_number}"
    
    return f"""
    🧾 Facture {invoice['facture_number']}
    Montant HT: {invoice['total_ht']}€
    TVA: {invoice['total_tva']}€
    Total TTC: {invoice['total_ttc']}€
    Statut: {invoice['status']}
    """

@tool
def check_warranty_tool(product_id: int):
    """
    Vérifie la garantie d'un produit.
    
    Args:
        product_id: ID du produit
        
    Returns: Informations de garantie
    """
    warranty = get_product_warranty(product_id)
    if not warranty:
        return f"Aucune garantie active pour produit {product_id}"
    
    return f"""
    ✅ Garantie active
    Durée: {warranty.get('warranty_months', 24)} mois
    Fin: {warranty.get('end_date', 'N/A')}
    """

# === AGENT CONFIGURATION ===

class SupportAgent:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
        
        # Tools
        self.tools = [
            find_client_by_reference_tool,
            find_client_by_email_tool,
            get_client_orders_tool,
            get_order_details_tool,
            track_delivery_tool,
            get_invoice_tool,
            check_warranty_tool
        ]
        
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
        
        system_msg = f"""Agent support intelligent.

REGLES ABSOLUES:
1. FRANÇAIS UNIQUEMENT
2. JAMAIS dire "fonction", "outil", "tool", "get_order_details_tool" ou mots techniques
3. AGIS IMMEDIATEMENT - si numéro commande donné, CHERCHE direct
4. ULTRA-BREF - 1-2 phrases
5. Questions générales ("aide", "help"): réponds aimablement en français

CONTEXTE: {context_summary}

COMPORTEMENT:
- "commande CMD-2026-0001" → CHERCHE direct, donne statut
- "ref 1000000000123" → TROUVE client direct, salue par nom
- "où est ma commande" → Si contexte a numéro: cherche. Sinon: "Quel est votre numéro de commande?"
- "aide" ou "help" → "Que puis-je faire pour vous aujourd'hui?"
- "bonjour" ou "merci" → "Bonjour! Que puis-je faire pour vous aujourd'hui?"

EXEMPLE PARFAIT:
User: "ma commande CMD-2026-0005"
Toi: [APPEL SILENCIEUX get_order_details_tool] "Votre commande est en livraison, arrivée prévue demain midi."

EXEMPLE INTERDIT:
Toi: "Je vais vérifier avec get_order_details_tool..." ❌
Toi: "Laissez-moi accéder à la base de données..." ❌

RESULTAT DIRECT UNIQUEMENT."""

        try:
            response = self.llm.invoke([
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_message}
            ])
            
            response_text = response.content
            self.message_history.append({'role': 'assistant', 'content': response_text})
            
            return response_text
            
        except Exception as e:
            error_msg = f"Erreur support: {str(e)}"
            self.message_history.append({'role': 'assistant', 'content': error_msg})
            return error_msg
