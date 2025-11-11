"""
Knowledge Base for SQL RAG with Embeddings

This file contains structured knowledge about the database:
- Table descriptions and business context
- Column meanings and usage examples
- Sample queries and common patterns
- Business rules and relationships

This knowledge will be embedded and stored in ChromaDB for semantic search.
"""

# Database knowledge that will be embedded for semantic search
DATABASE_KNOWLEDGE = [
    {
        "id": "customers_table",
        "content": "The customers table stores customer information including their name, email, country, and signup date. Use this table to get customer details, count customers by country, or find when customers joined.",
        "metadata": {
            "type": "table_description",
            "table": "customers",
            "keywords": "customer, user, client, people, email, country, signup"
        }
    },
    {
        "id": "products_table",
        "content": "The products table is a catalog of all available products with their names, categories (Electronics, Furniture, Office Supplies, etc.), prices, and stock quantities. Use this to find products by category, check inventory, or get pricing information.",
        "metadata": {
            "type": "table_description",
            "table": "products",
            "keywords": "product, item, catalog, inventory, stock, price, category"
        }
    },
    {
        "id": "orders_table",
        "content": "The orders table tracks all customer orders with order dates, total amounts, and status (completed, shipped, processing). Each order is linked to a customer via customer_id. Use this for order history, revenue calculations, and tracking order statuses.",
        "metadata": {
            "type": "table_description",
            "table": "orders",
            "keywords": "order, purchase, transaction, sale, revenue, status"
        }
    },
    {
        "id": "order_items_table",
        "content": "The order_items table stores individual line items for each order, linking products to orders with quantities and prices. This is a junction table that connects orders and products. Use this to see what products were in an order or analyze product sales.",
        "metadata": {
            "type": "table_description",
            "table": "order_items",
            "keywords": "order item, line item, product sale, order detail"
        }
    },
    
    # Column-specific knowledge
    {
        "id": "customer_country",
        "content": "The country column in customers table shows where each customer is located (USA, UK, Spain, Canada, etc.). Useful for geographic analysis, filtering by region, or counting customers per country.",
        "metadata": {
            "type": "column_description",
            "table": "customers",
            "column": "country",
            "keywords": "location, geography, region, country, where from"
        }
    },
    {
        "id": "product_category",
        "content": "Products are categorized into: Electronics (laptops, mice, headphones), Furniture (chairs, desks, lamps), Office Supplies (notebooks), Home & Kitchen (coffee makers), and Accessories (cables, bottles). Use category to filter or group products.",
        "metadata": {
            "type": "column_description",
            "table": "products",
            "column": "category",
            "keywords": "category, type, group, electronics, furniture"
        }
    },
    {
        "id": "order_status",
        "content": "Order status can be: 'completed' (order delivered), 'shipped' (order in transit), or 'processing' (order being prepared). Use status to filter orders by their current state or count orders in each status.",
        "metadata": {
            "type": "column_description",
            "table": "orders",
            "column": "status",
            "keywords": "status, state, completed, shipped, processing, pending"
        }
    },
    
    # Sample queries and patterns
    {
        "id": "count_customers",
        "content": "To count total customers: SELECT COUNT(*) FROM customers. To count by country: SELECT country, COUNT(*) FROM customers GROUP BY country.",
        "metadata": {
            "type": "query_pattern",
            "intent": "counting",
            "keywords": "how many, count, total, number of"
        }
    },
    {
        "id": "revenue_calculation",
        "content": "To calculate total revenue: SELECT SUM(total_amount) FROM orders WHERE status = 'completed'. Revenue should only include completed orders, not shipped or processing ones.",
        "metadata": {
            "type": "query_pattern",
            "intent": "revenue",
            "keywords": "revenue, sales, total sales, earnings, income, money made"
        }
    },
    {
        "id": "top_products",
        "content": "To find top/most expensive products: SELECT * FROM products ORDER BY price DESC LIMIT N. To find cheapest: ORDER BY price ASC. Replace N with the number of products wanted.",
        "metadata": {
            "type": "query_pattern",
            "intent": "ranking",
            "keywords": "top, most, highest, lowest, best, expensive, cheap"
        }
    },
    {
        "id": "customer_spending",
        "content": "To find how much a customer spent: SELECT c.first_name, c.last_name, SUM(o.total_amount) FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id. To find top spender: add ORDER BY SUM(o.total_amount) DESC LIMIT 1.",
        "metadata": {
            "type": "query_pattern",
            "intent": "customer_analysis",
            "keywords": "customer spent, top customer, best customer, biggest spender"
        }
    },
    {
        "id": "low_stock",
        "content": "To find low stock products: SELECT * FROM products WHERE stock_quantity < threshold ORDER BY stock_quantity. Common thresholds are 50 units for low stock or 20 for critical stock.",
        "metadata": {
            "type": "query_pattern",
            "intent": "inventory",
            "keywords": "low stock, out of stock, inventory, running out, need to reorder"
        }
    },
    {
        "id": "recent_orders",
        "content": "To get recent/latest orders: SELECT * FROM orders ORDER BY order_date DESC LIMIT N. To get orders from a specific time period: WHERE order_date >= 'YYYY-MM-DD' AND order_date < 'YYYY-MM-DD'.",
        "metadata": {
            "type": "query_pattern",
            "intent": "time_based",
            "keywords": "recent, latest, last week, last month, today, yesterday"
        }
    },
    
    # Business rules
    {
        "id": "revenue_rule",
        "content": "IMPORTANT: When calculating revenue or sales, ONLY include orders with status='completed'. Shipped and processing orders should not be counted as revenue yet since they haven't been delivered.",
        "metadata": {
            "type": "business_rule",
            "keywords": "revenue, sales, total sales, income"
        }
    },
    {
        "id": "join_pattern",
        "content": "Common JOIN patterns: customers to orders (customers.customer_id = orders.customer_id), orders to order_items (orders.order_id = order_items.order_id), products to order_items (products.product_id = order_items.product_id).",
        "metadata": {
            "type": "business_rule",
            "keywords": "join, relationship, connect tables"
        }
    },
    {
        "id": "date_filtering",
        "content": "The database contains orders from August 2024 to November 2024. When users ask for 'recent' or 'last month' orders, use October 2024 (2024-10-01 to 2024-10-31) as the reference.",
        "metadata": {
            "type": "business_rule",
            "keywords": "date, time, recent, last month, when"
        }
    }
]
