"""
Support agent: client identification, orders, deliveries, invoices and warranties.
Seven tools, each a thin wrapper over core/database_mysql.py.
"""

from langchain_core.tools import tool

from agents.base import ToolAgent
from core.database_mysql import (
    get_client_by_email,
    get_client_by_reference,
    get_client_orders,
    get_invoice_by_order,
    get_order_by_number,
    get_order_delivery_status,
    get_product_warranty,
)


# === TOOLS ===

def _format_client(client):
    return (
        f"Client trouvé (id {client['id']}):\n"
        f"Nom: {client['first_name']} {client['last_name']}\n"
        f"Référence: {client.get('client_reference') or 'N/A'}\n"
        f"Email: {client['email']}\n"
        f"Type: {client['client_type']}\n"
        f"Points fidélité: {client['points_fidelite']}"
    )


@tool
def find_client_by_reference_tool(client_reference: str):
    """
    Trouve un client par sa référence client (13 chiffres).

    Args:
        client_reference: référence client (ex: "1000000000123")

    Returns: identité du client et son id interne (à utiliser pour ses commandes)
    """
    client = get_client_by_reference(client_reference)
    if not client:
        return f"Client {client_reference} non trouvé"
    return _format_client(client)


@tool
def find_client_by_email_tool(email: str):
    """
    Trouve un client par son adresse email.

    Args:
        email: adresse email

    Returns: identité du client et son id interne (à utiliser pour ses commandes)
    """
    client = get_client_by_email(email)
    if not client:
        return f"Aucun client avec l'email {email}"
    return _format_client(client)


@tool
def get_client_orders_tool(client_id: int):
    """
    Liste les commandes d'un client.

    Args:
        client_id: id interne du client (donné par la recherche client)

    Returns: numéros de commande, statut et montant
    """
    orders = get_client_orders(client_id)
    if not orders:
        return "Aucune commande trouvée"

    output = f"{len(orders)} commande(s):\n"
    for order in orders:
        output += (
            f"\n- {order['order_number']} - {order['status']} - {order['total_ttc']}€"
            f" ({order['item_count']} article(s), le {order['created_at']})"
        )
    return output


@tool
def get_order_details_tool(order_number: str):
    """
    Détails complets d'une commande.

    Args:
        order_number: numéro de commande (ex: "CMD-2026-0001")

    Returns: statut, montant, date, client et produits commandés
    """
    details = get_order_by_number(order_number)
    if not details:
        return f"Commande {order_number} non trouvée"

    output = (
        f"Commande {details['order_number']}\n"
        f"Client: {details['first_name']} {details['last_name']}\n"
        f"Statut: {details['status']}\n"
        f"Total TTC: {details['total_ttc']}€\n"
        f"Date: {details.get('created_at', 'N/A')}"
    )
    items = details.get('items', [])
    if items:
        output += "\nProduits:"
        for item in items:
            output += f"\n- {item['name']} x{item['quantity']} - {item['total']}€"
    return output


@tool
def track_delivery_tool(order_number: str):
    """
    Suivi de livraison d'une commande.

    Args:
        order_number: numéro de commande

    Returns: statut de livraison, transporteur, numéro de suivi, dates
    """
    tracking = get_order_delivery_status(order_number)
    if not tracking:
        return f"Aucune commande {order_number}"

    output = (
        f"Livraison {order_number}:\n"
        f"Statut: {tracking.get('status') or 'N/A'}\n"
        f"Transporteur: {tracking.get('carrier') or 'pas encore expédiée'}\n"
        f"Numéro de suivi: {tracking.get('tracking_number') or 'N/A'}"
    )
    if tracking.get('shipped_date'):
        output += f"\nExpédiée le: {tracking['shipped_date']}"
    if tracking.get('delivery_date'):
        output += f"\nLivrée le: {tracking['delivery_date']}"
    return output


@tool
def get_invoice_tool(order_number: str):
    """
    Facture d'une commande.

    Args:
        order_number: numéro de commande

    Returns: numéro de facture, montants HT/TVA/TTC, statut de paiement
    """
    invoice = get_invoice_by_order(order_number)
    if not invoice:
        return f"Aucune facture pour {order_number}"

    return (
        f"Facture {invoice['facture_number']}\n"
        f"Montant HT: {invoice['total_ht']}€\n"
        f"TVA: {invoice['total_tva']}€\n"
        f"Total TTC: {invoice['total_ttc']}€\n"
        f"Statut: {invoice['status']}\n"
        f"Émise le: {invoice.get('date_emission', 'N/A')}"
    )


@tool
def check_warranty_tool(product_id: int):
    """
    Garantie d'un produit : durée constructeur et garanties actives sur les unités vendues.

    Args:
        product_id: identifiant du produit

    Returns: durée de garantie et date de fin si une garantie est active
    """
    warranty = get_product_warranty(product_id)
    if not warranty:
        return f"Produit {product_id} non trouvé"

    output = f"{warranty['name']}: garantie de {warranty.get('warranty_months', 24)} mois"
    active = warranty.get('active_warranties') or []
    if active:
        output += f"\n{len(active)} garantie(s) active(s):"
        for g in active:
            output += f"\n- {g['type']} jusqu'au {g['end_date']} (commande {g['order_number']})"
    else:
        output += "\nAucune garantie active enregistrée sur ce produit"
    return output


# === AGENT ===

SYSTEM_PROMPT = """Tu es l'agent du service client d'une boutique en ligne d'électronique.

RÈGLES
1. Réponds toujours en français, en une ou deux phrases.
2. Pour toute question sur une commande, une livraison, une facture ou une garantie,
   utilise les outils avant de répondre. N'invente jamais un statut : si l'outil ne trouve
   rien, dis-le et demande de vérifier le numéro.
3. Ne mentionne jamais les outils, les fonctions ou la base de données : donne directement le résultat.
4. Les numéros de commande ont la forme CMD-AAAA-NNNN, les références client ont 13 chiffres.
   Si le client ne donne ni numéro de commande, ni référence, ni email, demande-lui l'un des trois.
5. Pour "mes commandes", identifie d'abord le client (référence ou email) puis liste ses commandes.
6. Salutations, remerciements ou demande d'aide : réponds "Bonjour ! Que puis-je faire pour vous aujourd'hui ?".

EXEMPLE
Client : "ma commande CMD-2026-0002"
Toi (après vérification) : "Votre commande CMD-2026-0002 a été expédiée par Colissimo, numéro de suivi TRACK-FR-002345678."
"""


class SupportAgent(ToolAgent):
    name = "SUPPORT"
    temperature = 0.2
    tools = [
        find_client_by_reference_tool,
        find_client_by_email_tool,
        get_client_orders_tool,
        get_order_details_tool,
        track_delivery_tool,
        get_invoice_tool,
        check_warranty_tool,
    ]

    def system_prompt(self):
        return SYSTEM_PROMPT
