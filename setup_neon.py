#!/usr/bin/env python3
"""
Setup script for Neon PostgreSQL database
Runs the setup_supabase.sql script against Neon database
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_neon_database():
    """Setup Neon database with tables and sample data"""
    
    # Get Neon connection string
    neon_dsn = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")
    
    if not neon_dsn:
        print("❌ Error: NEON_DATABASE_URL or DATABASE_URL not found in .env file")
        return False
    
    print("🔌 Connecting to Neon database...")
    
    try:
        # Connect to Neon
        conn = psycopg2.connect(neon_dsn)
        conn.autocommit = False  # Use transactions
        cursor = conn.cursor()
        
        # Read the SQL script
        with open('setup_supabase.sql', 'r') as f:
            sql_script = f.read()
        
        print("📝 Executing SQL script...")
        
        # Execute the script
        cursor.execute(sql_script)
        
        # Commit the transaction
        conn.commit()
        
        print("✅ Database setup complete!")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\n📊 Created tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Count rows in each table
        print(f"\n📈 Sample data inserted:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} rows")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 Setting up Neon PostgreSQL database...\n")
    success = setup_neon_database()
    
    if success:
        print("\n✨ All done! Your Neon database is ready to use.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
