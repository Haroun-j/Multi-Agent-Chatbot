"""
MariaDB access layer for the e-commerce database.

Each function opens a short-lived connection, runs one parameterised query and
returns plain dicts, so the agents' tools never see SQL. Connection settings
come from the environment (see .env.example); the defaults match
docker-compose.yml (root without password on localhost:3308).
"""

import os

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3308')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'ecommerce'),
}


# ========================================
# CONNECTION HELPERS
# ========================================

def get_connection():
    """Open a connection, or return None (and log) if the database is unreachable."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Database connection error: {e}")
        return None


def test_connection(verbose=False):
    """Return True if the database answers. With verbose=True, print row counts per table."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        if verbose:
            print(f"Connected to '{DB_CONFIG['database']}' ({len(tables)} tables)")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                print(f"  {table:20s} {cursor.fetchone()[0]:5d} rows")
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Error: {e}")
        return False


def execute_query(query, params=None):
    """Run a SELECT and return the rows as a list of dicts ([] on error)."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Error as e:
        print(f"Query error: {e}")
        return []


def execute_update(query, params=None):
    """Run an INSERT/UPDATE/DELETE and return the number of affected rows."""
    conn = get_connection()
    if not conn:
        return 0
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        conn.close()
        return affected_rows
    except Error as e:
        print(f"Update error: {e}")
        return 0


# ========================================
# PRODUCT QUERIES
# ========================================

def get_products(category=None, min_price=None, max_price=None, brand=None, keyword=None, limit=20):
    """Search the catalogue with optional filters. Category matches the category or its parent."""
    conditions = []
    params = []
    if category:
        conditions.append("(c.name LIKE %s OR parent.name LIKE %s)")
        params += [f"%{category}%", f"%{category}%"]
    if min_price is not None:
        conditions.append("p.prix_vente >= %s")
        params.append(min_price)
    if max_price is not None:
        conditions.append("p.prix_vente <= %s")
        params.append(max_price)
    if brand:
        conditions.append("p.brand LIKE %s")
        params.append(f"%{brand}%")
    if keyword:
        conditions.append("(p.name LIKE %s OR p.description LIKE %s OR p.model LIKE %s)")
        params += [f"%{keyword}%"] * 3
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    query = f"""
        SELECT p.id, p.name, p.brand, p.model, p.prix_vente, p.warranty_months,
               c.name AS category_name, s.disponible
        FROM produits p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN categories parent ON c.parent_id = parent.id
        LEFT JOIN stock s ON p.id = s.produit_id
        {where}
        ORDER BY p.prix_vente ASC
        LIMIT %s
    """
    params.append(limit)
    return execute_query(query, tuple(params))


def get_product_details(product_id):
    """Full product sheet: price, brand, warranty, category, supplier and stock."""
    query = """
        SELECT p.*, c.name AS category_name, f.name AS fournisseur_name,
               s.quantity, s.reserved, s.disponible AS stock_disponible, s.location
        FROM produits p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN fournisseurs f ON p.fournisseur_id = f.id
        LEFT JOIN stock s ON p.id = s.produit_id
        WHERE p.id = %s
    """
    results = execute_query(query, (product_id,))
    return results[0] if results else None


def get_product_stock(product_id):
    """Stock line of a product: quantity, reserved, disponible, location, min_stock."""
    query = """
        SELECT quantity, reserved, disponible, location, min_stock
        FROM stock
        WHERE produit_id = %s
    """
    results = execute_query(query, (product_id,))
    return results[0] if results else None


def get_product_warranty(product_id):
    """Warranty length of a product plus the warranties currently active on sold units."""
    product = execute_query(
        "SELECT id, name, warranty_months FROM produits WHERE id = %s", (product_id,)
    )
    if not product:
        return None
    info = product[0]
    info['active_warranties'] = execute_query("""
        SELECT g.type, g.start_date, g.end_date, g.status, c.order_number
        FROM garanties g
        JOIN commande_items ci ON g.commande_item_id = ci.id
        JOIN commandes c ON ci.commande_id = c.id
        WHERE ci.produit_id = %s AND g.status = 'active'
        ORDER BY g.end_date DESC
    """, (product_id,))
    if info['active_warranties']:
        info['end_date'] = info['active_warranties'][0]['end_date']
    return info


def get_all_products(limit=50):
    """Get all products with category and stock info"""
    query = """
        SELECT p.*, c.name as category_name, s.quantity, s.disponible, f.name as fournisseur_name
        FROM produits p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN stock s ON p.id = s.produit_id
        LEFT JOIN fournisseurs f ON p.fournisseur_id = f.id
        ORDER BY p.created_at DESC
        LIMIT %s
    """
    return execute_query(query, (limit,))


def get_product_by_id(product_id):
    """Get detailed product information"""
    query = """
        SELECT p.*, c.name as category_name, s.quantity, s.disponible, s.location,
               f.name as fournisseur_name
        FROM produits p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN stock s ON p.id = s.produit_id
        LEFT JOIN fournisseurs f ON p.fournisseur_id = f.id
        WHERE p.id = %s
    """
    results = execute_query(query, (product_id,))
    return results[0] if results else None


def search_products(search_term):
    """Search products by name, brand, or description"""
    query = """
        SELECT p.*, c.name as category_name, s.disponible
        FROM produits p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN stock s ON p.id = s.produit_id
        WHERE p.name LIKE %s OR p.brand LIKE %s OR p.description LIKE %s
        ORDER BY p.prix_vente ASC
        LIMIT 20
    """
    search = f"%{search_term}%"
    return execute_query(query, (search, search, search))


def get_products_by_category(category_name):
    """Get all products in a specific category"""
    query = """
        SELECT p.*, s.disponible
        FROM produits p
        JOIN categories c ON p.category_id = c.id
        LEFT JOIN stock s ON p.id = s.produit_id
        WHERE c.name = %s
        ORDER BY p.prix_vente ASC
    """
    return execute_query(query, (category_name,))


def get_best_sellers(limit=10):
    """Get best selling products"""
    query = """
        SELECT p.name, p.prix_vente, bp.total_sold, bp.revenue, bp.avg_rating
        FROM best_products bp
        JOIN produits p ON bp.produit_id = p.id
        ORDER BY bp.total_sold DESC
        LIMIT %s
    """
    return execute_query(query, (limit,))


def get_products_on_promotion():
    """Get all products currently on promotion"""
    query = """
        SELECT DISTINCT p.*, pr.name as promo_name, pr.discount_percentage
        FROM produits p
        JOIN produits_promotions pp ON p.id = pp.produit_id
        JOIN promotions pr ON pp.promotion_id = pr.id
        WHERE pr.active = TRUE
        AND pr.start_date <= NOW()
        AND (pr.end_date IS NULL OR pr.end_date >= NOW())
    """
    return execute_query(query)


def get_product_reviews(product_id):
    """Get all reviews for a product"""
    query = """
        SELECT a.*, c.username, c.first_name, c.last_name
        FROM avis a
        JOIN clients c ON a.client_id = c.id
        WHERE a.produit_id = %s
        ORDER BY a.created_at DESC
    """
    return execute_query(query, (product_id,))


# ========================================
# CLIENT QUERIES
# ========================================

def get_client_by_username(username):
    """Get client information"""
    query = "SELECT * FROM clients WHERE username = %s"
    results = execute_query(query, (username,))
    return results[0] if results else None


def get_client_by_reference(client_reference):
    """Get client information by reference number (13 digits)"""
    query = "SELECT * FROM clients WHERE client_reference = %s"
    results = execute_query(query, (client_reference,))
    return results[0] if results else None


def get_client_by_email(email):
    """Get client information by e-mail address (case-insensitive)"""
    query = "SELECT * FROM clients WHERE LOWER(email) = LOWER(%s)"
    results = execute_query(query, (email,))
    return results[0] if results else None


def get_client_orders(client_id, limit=10):
    """Get all orders for a specific client"""
    query = """
        SELECT c.*, COUNT(ci.id) as item_count
        FROM commandes c
        LEFT JOIN commande_items ci ON c.id = ci.commande_id
        WHERE c.client_id = %s
        GROUP BY c.id
        ORDER BY c.created_at DESC
        LIMIT %s
    """
    return execute_query(query, (client_id, limit))


def get_client_deliveries(client_id, limit=10):
    """Get deliveries for a specific client"""
    query = """
        SELECT l.*, c.order_number
        FROM livraisons l
        JOIN commandes c ON l.commande_id = c.id
        WHERE c.client_id = %s
        ORDER BY l.shipped_date DESC
        LIMIT %s
    """
    return execute_query(query, (client_id, limit))


def get_client_statistics(client_id):
    """Get comprehensive statistics for a client"""
    query = """
        SELECT
            COUNT(DISTINCT c.id) as total_orders,
            SUM(c.total_ttc) as total_spent,
            AVG(c.total_ttc) as avg_order_value,
            COUNT(DISTINCT a.id) as total_reviews,
            cl.points_fidelite
        FROM clients cl
        LEFT JOIN commandes c ON cl.id = c.client_id AND c.status != 'cancelled'
        LEFT JOIN avis a ON cl.id = a.client_id
        WHERE cl.id = %s
        GROUP BY cl.id
    """
    results = execute_query(query, (client_id,))
    return results[0] if results else None


# ========================================
# ORDER QUERIES
# ========================================

def get_order_items(order_id):
    """Lines of an order with the product name, brand and model"""
    query = """
        SELECT ci.id, ci.quantity, ci.prix_unitaire, ci.discount_percentage, ci.total,
               p.id AS produit_id, p.name, p.brand, p.model
        FROM commande_items ci
        JOIN produits p ON ci.produit_id = p.id
        WHERE ci.commande_id = %s
    """
    return execute_query(query, (order_id,))


def get_order_by_number(order_number):
    """Order found by its public number (CMD-YYYY-NNNN), with its client and items"""
    query = """
        SELECT c.*, cl.first_name, cl.last_name, cl.email, cl.client_reference
        FROM commandes c
        JOIN clients cl ON c.client_id = cl.id
        WHERE c.order_number = %s
    """
    results = execute_query(query, (order_number,))
    if not results:
        return None
    order = results[0]
    order['items'] = get_order_items(order['id'])
    return order


def get_order_details(order_id):
    """Get complete order details with items (by internal id)"""
    query = """
        SELECT c.*, cl.username, cl.email, cl.first_name, cl.last_name
        FROM commandes c
        JOIN clients cl ON c.client_id = cl.id
        WHERE c.id = %s
    """
    order = execute_query(query, (order_id,))
    if order:
        order[0]['items'] = get_order_items(order_id)
        return order[0]
    return None


def get_order_delivery_status(order_number):
    """Latest delivery record of an order; falls back to the order status if nothing shipped yet"""
    query = """
        SELECT l.*, c.order_number, c.status AS order_status
        FROM livraisons l
        JOIN commandes c ON l.commande_id = c.id
        WHERE c.order_number = %s
        ORDER BY l.shipped_date DESC
        LIMIT 1
    """
    results = execute_query(query, (order_number,))
    if results:
        return results[0]
    order = execute_query(
        "SELECT order_number, status FROM commandes WHERE order_number = %s", (order_number,)
    )
    if not order:
        return None
    return {
        'order_number': order[0]['order_number'],
        'order_status': order[0]['status'],
        'status': order[0]['status'],
        'carrier': None,
        'tracking_number': None,
    }


def get_invoice_by_order(order_number):
    """Invoice attached to an order"""
    query = """
        SELECT f.*, c.order_number
        FROM factures f
        JOIN commandes c ON f.commande_id = c.id
        WHERE c.order_number = %s
        ORDER BY f.date_emission DESC
        LIMIT 1
    """
    results = execute_query(query, (order_number,))
    return results[0] if results else None


def get_recent_orders(days=30, limit=20):
    """Orders placed in the last N days, all clients"""
    query = """
        SELECT c.*, cl.username, cl.email
        FROM commandes c
        JOIN clients cl ON c.client_id = cl.id
        WHERE c.created_at >= NOW() - INTERVAL %s DAY
        ORDER BY c.created_at DESC
        LIMIT %s
    """
    return execute_query(query, (days, limit))


def get_pending_orders():
    """Get all pending orders"""
    query = """
        SELECT c.*, cl.username, cl.email
        FROM commandes c
        JOIN clients cl ON c.client_id = cl.id
        WHERE c.status IN ('pending', 'confirmed', 'processing')
        ORDER BY c.created_at DESC
    """
    return execute_query(query)


# ========================================
# INVOICE & PAYMENT QUERIES
# ========================================

def get_unpaid_invoices():
    """Get all unpaid invoices"""
    query = """
        SELECT f.*, c.order_number, cl.username, cl.email
        FROM factures f
        JOIN commandes c ON f.commande_id = c.id
        JOIN clients cl ON c.client_id = cl.id
        WHERE f.status IN ('unpaid', 'partial', 'overdue')
        ORDER BY f.date_echeance ASC
    """
    return execute_query(query)


def get_client_invoices(client_id, limit=20):
    """Get all invoices for a client"""
    query = """
        SELECT f.*, c.order_number
        FROM factures f
        JOIN commandes c ON f.commande_id = c.id
        WHERE c.client_id = %s
        ORDER BY f.date_emission DESC
        LIMIT %s
    """
    return execute_query(query, (client_id, limit))


def get_unpaid_invoices_by_client(client_id):
    """Get unpaid invoices for a specific client"""
    query = """
        SELECT f.*, c.order_number
        FROM factures f
        JOIN commandes c ON f.commande_id = c.id
        WHERE c.client_id = %s
        AND f.status IN ('unpaid', 'partial', 'overdue')
        ORDER BY f.date_echeance ASC
    """
    return execute_query(query, (client_id,))


def get_payment_history(limit=20):
    """Get recent payment history"""
    query = """
        SELECT p.*, f.facture_number, m.name as payment_method
        FROM paiements p
        JOIN factures f ON p.facture_id = f.id
        JOIN modes_paiement m ON p.mode_paiement_id = m.id
        ORDER BY p.payment_date DESC
        LIMIT %s
    """
    return execute_query(query, (limit,))


# ========================================
# STOCK & INVENTORY QUERIES
# ========================================

def get_low_stock_products():
    """Get products with stock below minimum threshold"""
    query = """
        SELECT p.name, p.sku, s.quantity, s.disponible, s.min_stock, s.location
        FROM stock s
        JOIN produits p ON s.produit_id = p.id
        WHERE s.disponible < s.min_stock
        ORDER BY s.disponible ASC
    """
    return execute_query(query)


def get_stock_by_location(location):
    """Get all stock in a specific location"""
    query = """
        SELECT p.name, p.sku, s.quantity, s.reserved, s.disponible
        FROM stock s
        JOIN produits p ON s.produit_id = p.id
        WHERE s.location = %s
    """
    return execute_query(query, (location,))


# ========================================
# COUPON & PROMOTION QUERIES
# ========================================

def validate_coupon(coupon_code):
    """Validate if a coupon is active and available"""
    query = """
        SELECT * FROM coupons
        WHERE code = %s
        AND active = TRUE
        AND (usage_limit IS NULL OR used_count < usage_limit)
        AND (valid_until IS NULL OR valid_until >= NOW())
    """
    results = execute_query(query, (coupon_code,))
    return results[0] if results else None


def get_active_promotions():
    """Get all currently active promotions"""
    query = """
        SELECT * FROM promotions
        WHERE active = TRUE
        AND start_date <= NOW()
        AND (end_date IS NULL OR end_date >= NOW())
    """
    return execute_query(query)


# ========================================
# WARRANTY, INSURANCE, DELIVERY & RETURN QUERIES
# ========================================

def get_active_warranties(client_id):
    """Get all active warranties for a client"""
    query = """
        SELECT g.*, p.name as product_name, c.order_number
        FROM garanties g
        JOIN commande_items ci ON g.commande_item_id = ci.id
        JOIN commandes c ON ci.commande_id = c.id
        JOIN produits p ON ci.produit_id = p.id
        WHERE c.client_id = %s
        AND g.status = 'active'
        AND g.end_date >= CURDATE()
    """
    return execute_query(query, (client_id,))


def get_active_insurances(client_id):
    """Get all active insurance policies for a client"""
    query = """
        SELECT a.*, p.name as product_name, c.order_number
        FROM assurances a
        JOIN commande_items ci ON a.commande_item_id = ci.id
        JOIN commandes c ON ci.commande_id = c.id
        JOIN produits p ON ci.produit_id = p.id
        WHERE c.client_id = %s
        AND a.status = 'active'
    """
    return execute_query(query, (client_id,))


def track_delivery(tracking_number):
    """Track a delivery by tracking number"""
    query = """
        SELECT l.*, c.order_number, cl.username, cl.email
        FROM livraisons l
        JOIN commandes c ON l.commande_id = c.id
        JOIN clients cl ON c.client_id = cl.id
        WHERE l.tracking_number = %s
    """
    results = execute_query(query, (tracking_number,))
    return results[0] if results else None


def get_pending_returns():
    """Get all pending return requests"""
    query = """
        SELECT r.*, p.name as product_name, c.order_number, cl.username
        FROM retours r
        JOIN commande_items ci ON r.commande_item_id = ci.id
        JOIN produits p ON ci.produit_id = p.id
        JOIN commandes c ON ci.commande_id = c.id
        JOIN clients cl ON c.client_id = cl.id
        WHERE r.status IN ('requested', 'approved', 'received')
        ORDER BY r.request_date DESC
    """
    return execute_query(query)


# ========================================
# ANALYTICS
# ========================================

def get_sales_report(start_date=None, end_date=None):
    """Get sales report for a date range"""
    if not start_date:
        start_date = '2026-01-01'
    if not end_date:
        end_date = '2026-12-31'

    query = """
        SELECT
            COUNT(*) as total_orders,
            SUM(total_ttc) as total_revenue,
            AVG(total_ttc) as average_order_value,
            SUM(discount_amount) as total_discounts
        FROM commandes
        WHERE created_at BETWEEN %s AND %s
        AND status NOT IN ('cancelled', 'refunded')
    """
    results = execute_query(query, (start_date, end_date))
    return results[0] if results else None


if __name__ == "__main__":
    # python -m core.database_mysql  -> quick connectivity check with row counts
    if not test_connection(verbose=True):
        raise SystemExit("Database unreachable: is the MariaDB container running? (make db-up)")
