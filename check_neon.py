#!/usr/bin/env python3
"""
Check what's currently in the Neon database
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_neon_database():
    """Check Neon database contents"""
    
    # Get Neon connection string
    neon_dsn = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")
    
    if not neon_dsn:
        print("❌ Error: NEON_DATABASE_URL or DATABASE_URL not found in .env file")
        return False
    
    print("🔌 Connecting to Neon database...")
    
    try:
        # Connect to Neon
        conn = psycopg2.connect(neon_dsn)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\n📊 Existing tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        if not tables:
            print("  (No tables found)")
            return True
        
        # Count rows in each table
        print(f"\n📈 Row counts:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} rows")
        
        # Show sample data from customers
        if any(t[0] == 'customers' for t in tables):
            print(f"\n👥 Sample customers:")
            cursor.execute("SELECT customer_id, first_name, last_name, email FROM customers LIMIT 5")
            customers = cursor.fetchall()
            for customer in customers:
                print(f"  - {customer[0]}: {customer[1]} {customer[2]} ({customer[3]})")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    check_neon_database()
