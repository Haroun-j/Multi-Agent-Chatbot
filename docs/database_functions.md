# Database Functions Catalog

## Product Functions (8 functions)

### `get_products(category, min_price, max_price, brand, keyword)`
Search products with filters.
**Params**: All optional
**Returns**: List of products

### `get_product_details(product_id)`
Full product information.
**Params**: `product_id` (int)
**Returns**: Product dict with specs, warranty, stock

### `get_product_stock(product_id)`
Stock availability.
**Params**: `product_id` (int)
**Returns**: {quantity, reserved, disponible}

### `get_products_by_category(category_name)`
All products in category.
**Params**: `category_name` (str)

### `get_products_on_promotion()`
Products with active promotions.
**Params**: None

### `get_product_reviews(product_id)`
Customer reviews.
**Params**: `product_id` (int)

### `get_product_warranty(product_id)`
Warranty information.
**Params**: `product_id` (int)

### `get_active_promotions()`
All current promotions.
**Params**: None

---

## Client Functions (4 functions)

### `get_client_by_reference(client_reference)`
Find client by 13-digit reference.
**Params**: `client_reference` (str, 13 digits)

### `get_client_by_email(email)`
Find client by email.
**Params**: `email` (str)

### `get_client_orders(client_id, limit=10)`
Client's order history.
**Params**: `client_id` (int), `limit` (int, optional)

### `get_client_deliveries(client_id)`
Client's delivery history.
**Params**: `client_id` (int)

---

## Order Functions (5 functions)

### `get_order_by_number(order_number)`
Complete order details.
**Params**: `order_number` (str, "CMD-YYYY-NNNN")

### `get_order_items(order_id)`
Items in order.
**Params**: `order_id` (int)

### `get_order_delivery_status(order_number)`
Tracking information.
**Params**: `order_number` (str)

### `get_invoice_by_order(order_number)`
Invoice details.
**Params**: `order_number` (str)

### `get_recent_orders(days=30, limit=20)`
Recent orders across all clients.
**Params**: `days` (int), `limit` (int)

---

## Usage Examples

```python
# Search smartphones under 1000€
products = get_products(category="Smartphones", max_price=1000)

# Get client by reference
client = get_client_by_reference("1000000000123")

# Get order details
order = get_order_by_number("CMD-2026-0001")

# Check stock
stock = get_product_stock(15)  # product_id=15
```

---

## Total: 17 Core Functions
- Products: 8
- Clients: 4  
- Orders: 5
