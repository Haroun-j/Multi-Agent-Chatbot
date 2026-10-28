import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3308,
    'user': 'root',
    'password': '',
    'database': 'ecommerce'
}

def get_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def test_connection():
    """Test database connection and show tables with row counts"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print("\n" + "="*60)
            print("✅ DATABASE CONNECTED SUCCESSFULLY!")
            print("="*60)
            print(f"\n📊 Found {len(tables)} tables in 'ecommerce' database:\n")
            
            total_rows = 0
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                total_rows += count
                print(f"   📁 {table_name:25s} : {count:5d} rows")
            
            print(f"\n{'='*60}")
            print(f"   TOTAL RECORDS: {total_rows}")
            print(f"{'='*60}\n")
            
            cursor.close()
            conn.close()
            return True
        except Error as e:
            print(f"Error: {e}")
            return False
    return False

def execute_query(query, params=None):
    """Execute a SELECT query and return results as list of dictionaries"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        except Error as e:
            print(f"Query error: {e}")
            return []
    return []

def execute_update(query, params=None):
    """Execute an INSERT, UPDATE, or DELETE query"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            conn.close()
            return affected_rows
        except Error as e:
            print(f"Update error: {e}")
            return 0
    return 0

# ========================================
# PRODUCT QUERIES
# ========================================

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

# ========================================
# CLIENT & ORDER QUERIES
# ========================================

def get_client_by_username(username):
    """Get client information"""
    query = "SELECT * FROM clients WHERE username = %s"
    results = execute_query(query, (username,))
    return results[0] if results else None

def get_client_by_reference(client_reference):
    """Get client information by reference number"""
    query = "SELECT * FROM clients WHERE client_reference = %s"
    results = execute_query(query, (client_reference,))
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

def get_order_details(order_id):
    """Get complete order details with items"""
    query = """
        SELECT c.*, cl.username, cl.email, cl.first_name, cl.last_name
        FROM commandes c
        JOIN clients cl ON c.client_id = cl.id
        WHERE c.id = %s
    """
    order = execute_query(query, (order_id,))
    
    if order:
        items_query = """
            SELECT ci.*, p.name as product_name, p.brand, p.model
            FROM commande_items ci
            JOIN produits p ON ci.produit_id = p.id
            WHERE ci.commande_id = %s
        """
        items = execute_query(items_query, (order_id,))
        order[0]['items'] = items
        return order[0]
    return None

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
# WARRANTY & INSURANCE QUERIES
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

# ========================================
# DELIVERY & RETURN QUERIES
# ========================================

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
# ANALYTICS & REPORTS
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
# EXAMPLE USAGE
# ========================================

if __name__ == "__main__":
    print("Testing comprehensive database connection...\n")
    test_connection()
    
    print("\n" + "="*60)
    print("📦 SAMPLE DATA PREVIEW")
    print("="*60)
    
    # Show best sellers
    print("\n🏆 Top 5 Best Sellers:")
    best = get_best_sellers(5)
    for i, product in enumerate(best, 1):
        print(f"   {i}. {product['name']:30s} - {product['total_sold']:3d} sold - €{product['revenue']:,.2f}")
    
    # Show products on promotion
    print("\n🎉 Products on Promotion:")
    promos = get_products_on_promotion()
    for product in promos[:5]:
        print(f"   • {product['name']:30s} - {product['discount_percentage']}% OFF ({product['promo_name']})")
    
    # Show low stock
    print("\n⚠️  Low Stock Alerts:")
    low_stock = get_low_stock_products()
    if low_stock:
        for item in low_stock[:5]:
            print(f"   • {item['name']:30s} - Only {item['disponible']} left (min: {item['min_stock']})")
    else:
        print("   ✅ All products adequately stocked!")
    
    # Show pending orders
    print("\n📋 Pending Orders:")
    pending = get_pending_orders()
    for order in pending[:5]:
        print(f"   • {order['order_number']} - {order['username']} - €{order['total_ttc']:.2f} ({order['status']})")
    
    print("\n" + "="*60 + "\n")
