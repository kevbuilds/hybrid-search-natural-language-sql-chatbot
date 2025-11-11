"""
Database setup script for SQL RAG POC
Creates a PostgreSQL database with sample e-commerce data
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            port=5432
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create database
        cursor.execute("DROP DATABASE IF EXISTS sql_rag_poc")
        cursor.execute("CREATE DATABASE sql_rag_poc")
        print("✓ Database 'sql_rag_poc' created successfully")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        raise


def setup_tables_and_data():
    """Create tables and insert sample data"""
    try:
        # Connect to the new database
        conn = psycopg2.connect(
            host="localhost",
            database="sql_rag_poc",
            user="postgres",
            password="postgres",
            port=5432
        )
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                country VARCHAR(50),
                signup_date DATE DEFAULT CURRENT_DATE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                category VARCHAR(50),
                price DECIMAL(10, 2) NOT NULL,
                stock_quantity INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                customer_id INTEGER REFERENCES customers(customer_id),
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount DECIMAL(10, 2),
                status VARCHAR(20)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(order_id),
                product_id INTEGER REFERENCES products(product_id),
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10, 2) NOT NULL
            )
        """)
        
        print("✓ Tables created successfully")
        
        # Insert sample data - Customers
        customers_data = [
            ('John', 'Doe', 'john.doe@email.com', 'USA', '2024-01-15'),
            ('Jane', 'Smith', 'jane.smith@email.com', 'UK', '2024-02-20'),
            ('Carlos', 'Garcia', 'carlos.garcia@email.com', 'Spain', '2024-03-10'),
            ('Emma', 'Wilson', 'emma.wilson@email.com', 'Canada', '2024-03-25'),
            ('Liu', 'Wei', 'liu.wei@email.com', 'China', '2024-04-05'),
            ('Sophie', 'Martin', 'sophie.martin@email.com', 'France', '2024-05-12'),
            ('Ahmed', 'Hassan', 'ahmed.hassan@email.com', 'Egypt', '2024-06-01'),
            ('Maria', 'Silva', 'maria.silva@email.com', 'Brazil', '2024-07-18'),
        ]
        
        cursor.executemany(
            "INSERT INTO customers (first_name, last_name, email, country, signup_date) VALUES (%s, %s, %s, %s, %s)",
            customers_data
        )
        
        # Insert sample data - Products
        products_data = [
            ('Laptop Pro 15', 'Electronics', 1299.99, 50),
            ('Wireless Mouse', 'Electronics', 29.99, 200),
            ('USB-C Cable', 'Accessories', 15.99, 500),
            ('Coffee Maker', 'Home & Kitchen', 89.99, 75),
            ('Office Chair', 'Furniture', 249.99, 30),
            ('Desk Lamp', 'Furniture', 45.99, 120),
            ('Headphones', 'Electronics', 199.99, 100),
            ('Water Bottle', 'Accessories', 12.99, 300),
            ('Notebook Set', 'Office Supplies', 8.99, 400),
            ('Standing Desk', 'Furniture', 499.99, 20),
        ]
        
        cursor.executemany(
            "INSERT INTO products (product_name, category, price, stock_quantity) VALUES (%s, %s, %s, %s)",
            products_data
        )
        
        # Insert sample data - Orders
        orders_data = [
            (1, '2024-08-01 10:30:00', 1329.98, 'completed'),
            (2, '2024-08-05 14:15:00', 89.99, 'completed'),
            (3, '2024-08-10 09:45:00', 549.98, 'completed'),
            (1, '2024-08-15 16:20:00', 45.98, 'completed'),
            (4, '2024-09-01 11:00:00', 1299.99, 'shipped'),
            (5, '2024-09-10 13:30:00', 229.98, 'shipped'),
            (6, '2024-10-01 10:00:00', 749.98, 'processing'),
            (7, '2024-10-15 15:45:00', 12.99, 'completed'),
            (8, '2024-11-01 12:20:00', 1799.97, 'processing'),
        ]
        
        cursor.executemany(
            "INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES (%s, %s, %s, %s)",
            orders_data
        )
        
        # Insert sample data - Order Items
        order_items_data = [
            (1, 1, 1, 1299.99),
            (1, 2, 1, 29.99),
            (2, 4, 1, 89.99),
            (3, 5, 1, 249.99),
            (3, 10, 1, 499.99),
            (4, 3, 2, 15.99),
            (4, 8, 1, 12.99),
            (5, 1, 1, 1299.99),
            (6, 7, 1, 199.99),
            (6, 2, 1, 29.99),
            (7, 5, 1, 249.99),
            (7, 10, 1, 499.99),
            (8, 8, 1, 12.99),
            (9, 1, 1, 1299.99),
            (9, 5, 2, 249.99),
        ]
        
        cursor.executemany(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
            order_items_data
        )
        
        conn.commit()
        print("✓ Sample data inserted successfully")
        
        # Display summary
        cursor.execute("SELECT COUNT(*) FROM customers")
        print(f"  - Customers: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM products")
        print(f"  - Products: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        print(f"  - Orders: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM order_items")
        print(f"  - Order Items: {cursor.fetchone()[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error setting up tables: {e}")
        raise


if __name__ == "__main__":
    print("Setting up SQL RAG POC database...")
    print("-" * 50)
    create_database()
    setup_tables_and_data()
    print("-" * 50)
    print("Database setup complete! 🎉")
