"""
Sales agent: catalogue, prices, stock, promotions and customer reviews.
Five tools, each a thin wrapper over core/database_mysql.py.
"""

from langchain_core.tools import tool

from agents.base import ToolAgent
from core.database_mysql import (
    get_active_promotions,
    get_product_details,
    get_product_reviews,
    get_product_stock,
    get_products,
)

CATEGORIES = "Smartphones, Ordinateurs, Audio, Photo & Vidéo, Gaming, Wearables, Smart Home, Accessoires"


# === TOOLS ===

@tool
def search_products_tool(category: str = None, min_price: float = None, max_price: float = None,
                         brand: str = None, keyword: str = None):
    """
    Recherche de produits dans le catalogue. Tous les filtres sont optionnels.

    Args:
        category: catégorie parmi Smartphones, Ordinateurs, Audio, Photo & Vidéo,
                  Gaming, Wearables, Smart Home, Accessoires
        min_price: prix minimum en euros
        max_price: prix maximum en euros
        brand: marque (ex: "Apple", "Samsung", "Dell")
        keyword: mot-clé dans le nom, le modèle ou la description

    Returns: liste de produits avec id, prix et stock disponible
    """
    results = get_products(category, min_price, max_price, brand, keyword)
    if not results:
        return "Aucun produit trouvé avec ces critères"

    output = f"{len(results)} produit(s) trouvé(s):\n"
    for p in results[:8]:
        output += f"\n- [id {p['id']}] {p['name']} - {p['prix_vente']}€"
        if p.get('brand'):
            output += f" ({p['brand']})"
        if p.get('disponible') is not None:
            output += f" - stock: {p['disponible']}"
    return output


@tool
def get_product_details_tool(product_id: int):
    """
    Fiche complète d'un produit.

    Args:
        product_id: identifiant du produit (donné par la recherche)

    Returns: prix, stock, garantie, marque, catégorie, description
    """
    details = get_product_details(product_id)
    if not details:
        return f"Produit {product_id} non trouvé"

    return (
        f"Produit: {details['name']}\n"
        f"Prix: {details['prix_vente']}€\n"
        f"Marque: {details.get('brand') or 'N/A'} - Modèle: {details.get('model') or 'N/A'}\n"
        f"Catégorie: {details.get('category_name') or 'N/A'}\n"
        f"Stock disponible: {details.get('stock_disponible', 'N/A')} unités\n"
        f"Garantie: {details.get('warranty_months', 24)} mois\n"
        f"Description: {details.get('description') or 'N/A'}"
    )


@tool
def get_active_promotions_tool():
    """
    Liste les promotions en cours (nom, remise en pourcentage, période).

    Returns: promotions actives
    """
    promos = get_active_promotions()
    if not promos:
        return "Aucune promotion active actuellement"

    output = "Promotions en cours:\n"
    for promo in promos:
        output += f"\n- {promo['name']} - {promo['discount_percentage']}%"
        if promo.get('description'):
            output += f" : {promo['description']}"
        if promo.get('end_date'):
            output += f" (jusqu'au {promo['end_date']})"
    return output


@tool
def check_product_stock_tool(product_id: int):
    """
    Stock disponible d'un produit.

    Args:
        product_id: identifiant du produit

    Returns: quantité disponible, totale et réservée
    """
    stock = get_product_stock(product_id)
    if stock is None:
        return f"Stock non disponible pour le produit {product_id}"
    return (
        f"Stock disponible: {stock['disponible']} unités "
        f"(total: {stock['quantity']}, réservé: {stock['reserved']})"
    )


@tool
def get_product_reviews_tool(product_id: int):
    """
    Avis clients sur un produit.

    Args:
        product_id: identifiant du produit

    Returns: note moyenne et derniers avis
    """
    reviews = get_product_reviews(product_id)
    if not reviews:
        return "Aucun avis client pour ce produit"

    avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
    output = f"Note moyenne: {avg_rating:.1f}/5 ({len(reviews)} avis)\n"
    for review in reviews[:3]:
        output += f"\n- {review['rating']}/5 - {review.get('title') or 'Sans titre'}"
        if review.get('comment'):
            output += f" : {review['comment']}"
    return output


# === AGENT ===

SYSTEM_PROMPT = f"""Tu es l'assistant commercial d'une boutique en ligne d'électronique.

RÈGLES
1. Réponds toujours en français, en une ou deux phrases.
2. Pour toute question sur les produits, les prix, le stock, les promotions ou les avis,
   utilise les outils avant de répondre. N'invente jamais un produit, un prix ou un stock :
   si l'outil ne renvoie rien, dis-le simplement.
3. Ne mentionne jamais les outils, les fonctions ou la base de données : donne directement le résultat.
4. Si la demande est vague ("je veux un laptop"), propose les résultats trouvés et pose une
   question pour préciser (budget, marque, usage).
5. Salutations ou demande d'aide : réponds "Bonjour ! Que puis-je faire pour vous aujourd'hui ?".

Catégories du catalogue : {CATEGORIES}.

EXEMPLE
Client : "smartphones"
Toi (après recherche) : "Nous avons l'iPhone 15 (999€), le Galaxy S24 (899€) et le Pixel 8 Pro (999€). Lequel vous intéresse ?"
"""


class SalesAgent(ToolAgent):
    name = "SALES"
    temperature = 0.3
    tools = [
        search_products_tool,
        get_product_details_tool,
        get_active_promotions_tool,
        check_product_stock_tool,
        get_product_reviews_tool,
    ]

    def system_prompt(self):
        return SYSTEM_PROMPT
