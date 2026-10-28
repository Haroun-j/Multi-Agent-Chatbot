# Agent Test Scenarios

## SALES AGENT Scenarios

### S1: Product Search (Basic)
- User: "show me smartphones"
- Expected: Ask for price range/brand
- Agent should: Activate product search, ask clarifying questions

### S2: Product Search with Filters
- User: "find Apple laptops under 2000€"
- Expected: Direct search results
- Agent should: Use get_products with filters

### S3: Product Details  
- User: "tell me about product 15"
- Expected: Full product info
- Agent should: Call get_product_details(15)

### S4: Stock Check
- User: "is iPhone 15 in stock?"
- Expected: Stock availability
- Agent should: Search product, check stock

### S5: Promotions
- User: "what's on sale?"
- Expected: List active promotions
- Agent should: Call get_active_promotions()

### S6: Product Reviews
- User: "what do people say about this?"
- Expected: Customer reviews
- Agent should: Need product_id, show reviews

### S7: Compare Products
- User: "compare iPhone 15 vs Samsung S24"
- Expected: Side-by-side comparison
- Agent should: Get details for both

### S8: Category Browse
- User: "show gaming consoles"
- Expected: List gaming products
- Agent should: get_products_by_category("Gaming")

---

## SUPPORT AGENT Scenarios

### U1: Order Status (Basic)
- User: "where's my order?"
- Expected: Ask for order number or client ref
- Agent should: Activate form or search

### U2: Order Status (With Number)
- User: "check CMD-2026-0005"
- Expected: Order details
- Agent should: Call get_order_by_number

### U3: Client Orders
- User: "show all my orders"
- Expected: Need client identification
- Agent should: Auth then get_client_orders

### U4: Delivery Tracking
- User: "track my delivery"
- Expected: Tracking info
- Agent should: Need order number, call track_delivery

### U5: Invoice Request
- User: "I need my invoice"
- Expected: Invoice details/PDF
- Agent should: get_invoice_by_order

### U6: Warranty Check
- User: "is my laptop still under warranty?"
- Expected: Warranty status
- Agent should: Find product, check warranty

### U7: Client Lookup (Email)
- User: "alice.martin@gmail.com"
- Expected: Client found
- Agent should: find_client_by_email

### U8: Client Lookup (Reference)
- User: "my ref is 1000000000123"
- Expected: Client found
- Agent should: find_client_by_reference

---

## COMPLEX SCENARIOS

### C1: Multi-Turn Product Search
1. "I need a laptop"
2. "around 1500€"
3. "Apple or Dell"  
4. "show me the Dell"
5. "is it in stock?"
6. "I'll take it"

### C2: Order Problem Resolution
1. "my order is late"
2. Provide order number
3. Check tracking
4. Explain delay
5. Offer compensation

### C3: Product Recommendation
1. "gift for gamer"
2. "under 600€"
3. Suggest PS5/Xbox
4. "what games?"
5. Show bundle options

### C4: Account Management
1. "create account"
2. Collect email, name
3. "what are my orders?"
4. Show order history
5. "cancel last order"
6. Confirm cancellation

### C5: Mixed Intent
1. "check order CMD-2026-0001"
2. "also show me new phones"
3. Switch to sales agent
4. "but I still want my order status"
5. Switch back to support

### C6: Authentication Flow
1. "view my commandes"
2. Ask for name
3. "Alice Martin"
4. Ask for password
5. Wrong password → retry
6. Correct password → show orders

### C7: Progressive Data Collection
1. "find products"
2. "in Audio category"  
3. "Bose brand"
4. "under 300€"
5. "with good reviews"
6. Filter progressively

### C8: Context Switching
1. Talk about phones (sales)
2. Check order (support)
3. Ask about warranty (support)
4. Back to phone promotions (sales)
5. Maintain context throughout

---

## EDGE CASES

### E1: Invalid Reference
- User: "ref 9999999999999"
- Expected: "Not found" + suggest alternatives

### E2: Future Date
- User: "orders from next month"
- Expected: Handle gracefully

### E3: Ambiguous Request
- User: "status"
- Expected: Ask "order status or account status?"

### E4: Empty Results
- User: "find purple laptops"
- Expected: "No results, try other colors?"

### E5: Multiple Matches
- User: "check my order"
- Expected: Show list if multiple, ask which one

### E6: Partial Info
- User: "CMD-2026" (incomplete)
- Expected: Ask for full number

### E7: Language Mix
- User: "je veux un smartphone under 500"
- Expected: Handle mixed French/English

### E8: Rapid Topic Change
- User jumps between 5 different topics quickly
- Expected: Maintain context, handle gracefully

---

## STRESS TESTS

### ST1: Long Conversation (20+ turns)
Ensure context maintained

### ST2: Rapid Fire Questions
10 questions in 30 seconds

### ST3: Contradictory Requests
"Show phones under 500" then "actually over 1000"

### ST4: Invalid Data Spam
Send gibberish, test error handling

### ST5: Form Abandonment
Start form, never complete it

### ST6: Concurrent Requests
Multiple browser tabs

---

## SUCCESS CRITERIA

For each scenario:
- ✅ Responds in French
- ✅ Asks for missing params
- ✅ Calls correct DB function
- ✅ Handles errors gracefully
- ✅ Maintains conversation context
- ✅ Routes to correct agent
- ✅ Provides helpful responses
