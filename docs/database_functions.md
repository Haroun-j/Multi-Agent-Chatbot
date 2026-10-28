# Database functions

All SQL lives in `core/database_mysql.py`. Each function returns plain dicts
(or `None` / `[]`), so the agents' tools only format text. The 17 functions
below are the ones designed for the agents; the sales and support tools are
built on 13 of them. The module also has a few reporting helpers (best sellers,
unpaid invoices, low stock, sales report, client statistics) that are not
exposed as tools yet.

## Products (8)

| Function | Parameters | Used by tool |
|---|---|---|
| `get_products(category, min_price, max_price, brand, keyword, limit=20)` | all optional; category matches the category or its parent | `search_products_tool` (sales) |
| `get_product_details(product_id)` | int | `get_product_details_tool` (sales) |
| `get_product_stock(product_id)` | int, returns quantity / reserved / disponible | `check_product_stock_tool` (sales) |
| `get_product_reviews(product_id)` | int | `get_product_reviews_tool` (sales) |
| `get_active_promotions()` | - | `get_active_promotions_tool` (sales) |
| `get_product_warranty(product_id)` | int, warranty length + active warranties on sold units | `check_warranty_tool` (support) |
| `get_products_by_category(category_name)` | exact category name | - |
| `get_products_on_promotion()` | - | - |

## Clients (4)

| Function | Parameters | Used by tool |
|---|---|---|
| `get_client_by_reference(client_reference)` | 13-digit string | `find_client_by_reference_tool` (support) |
| `get_client_by_email(email)` | case-insensitive | `find_client_by_email_tool` (support) |
| `get_client_orders(client_id, limit=10)` | internal id | `get_client_orders_tool` (support) |
| `get_client_deliveries(client_id, limit=10)` | internal id | - |

## Orders (5)

| Function | Parameters | Used by tool |
|---|---|---|
| `get_order_by_number(order_number)` | `CMD-YYYY-NNNN`, returns the order with its items | `get_order_details_tool` (support) |
| `get_order_items(order_id)` | internal id | via `get_order_by_number` |
| `get_order_delivery_status(order_number)` | falls back to the order status if nothing shipped yet | `track_delivery_tool` (support) |
| `get_invoice_by_order(order_number)` | | `get_invoice_tool` (support) |
| `get_recent_orders(days=30, limit=20)` | all clients | - |

## Test data worth knowing

- Clients: references `1000000000123` (Alice Martin), `1000000000456` (Robert Dupont),
  `1000000000789` (Claire Bernard), `1000000001012`, `1000000001345`, `1000000001678`.
- Orders: `CMD-2026-0001` to `CMD-2026-0015`; deliveries exist for 10 of them after `db/seed_extra.sql`.
- Catalogue: 38 products in 8 categories (Smartphones, Ordinateurs, Audio, Photo & Vidéo,
  Gaming, Wearables, Smart Home, Accessoires).
- Promotions have fixed dates in 2026; `get_active_promotions()` only returns the ones
  whose window contains today.

```python
from core.database_mysql import get_products, get_client_by_reference, get_order_by_number

get_products(category="Smartphones", max_price=1000)
get_client_by_reference("1000000000123")
get_order_by_number("CMD-2026-0001")["items"]
```
