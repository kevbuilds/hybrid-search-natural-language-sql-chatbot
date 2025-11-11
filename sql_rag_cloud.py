"""
SQL RAG Engine with HYBRID SEARCH - Cloud Version for Streamlit Cloud

Modified to work with Streamlit secrets and cloud PostgreSQL (Supabase)
"""
import os
import psycopg2
from anthropic import Anthropic
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from knowledge_base import DATABASE_KNOWLEDGE
import streamlit as st


class SQLRAGHybridEngine:
    def __init__(self):
        """Initialize with Streamlit secrets support"""
        print("🚀 Initializing Hybrid SQL RAG Engine (Cloud)...")
        
        # Get API key from Streamlit secrets or environment
        api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=api_key)
        
        # Database configuration from Streamlit secrets or env vars
        self.db_config = {
            "host": st.secrets.get("DB_HOST") or os.getenv("DB_HOST", "localhost"),
            "database": st.secrets.get("DB_NAME") or os.getenv("DB_NAME", "postgres"),
            "user": st.secrets.get("DB_USER") or os.getenv("DB_USER", "postgres"),
            "password": st.secrets.get("DB_PASSWORD") or os.getenv("DB_PASSWORD", "postgres"),
            "port": int(st.secrets.get("DB_PORT", "5432") or os.getenv("DB_PORT", "5432"))
        }
        
        # Load schema
        print("📊 Loading database schema...")
        self.schema_context = self._get_schema_context()
        
        # Initialize embedding model
        print("🧠 Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB (in-memory for cloud)
        print("💾 Initializing vector database...")
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            is_persistent=False
        ))
        
        self.collection = self.chroma_client.get_or_create_collection(
            name="sql_knowledge",
            metadata={"description": "SQL database knowledge and patterns"}
        )
        
        # Load knowledge base
        print("📚 Embedding knowledge base...")
        self._load_knowledge_base()
        
        print("✅ Hybrid SQL RAG Engine ready!")
    
    def _get_schema_context(self):
        """Get database schema from cloud PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    table_name,
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """)
            
            schema_info = cursor.fetchall()
            
            schema_text = "DATABASE SCHEMA:\n\n"
            current_table = None
            
            for table, column, dtype, nullable in schema_info:
                if table != current_table:
                    if current_table is not None:
                        schema_text += "\n"
                    schema_text += f"Table: {table}\n"
                    current_table = table
                
                null_str = "NULL" if nullable == "YES" else "NOT NULL"
                schema_text += f"  - {column}: {dtype} ({null_str})\n"
            
            schema_text += "\nRELATIONSHIPS:\n"
            schema_text += "- orders.customer_id → customers.customer_id\n"
            schema_text += "- order_items.order_id → orders.order_id\n"
            schema_text += "- order_items.product_id → products.product_id\n"
            
            cursor.close()
            conn.close()
            
            return schema_text
            
        except Exception as e:
            print(f"Error getting schema: {e}")
            return ""
    
    def _load_knowledge_base(self):
        """Load knowledge base into ChromaDB"""
        existing_count = self.collection.count()
        if existing_count > 0:
            print(f"   Knowledge base already loaded ({existing_count} items)")
            return
        
        documents = []
        metadatas = []
        ids = []
        
        for item in DATABASE_KNOWLEDGE:
            documents.append(item["content"])
            metadatas.append(item["metadata"])
            ids.append(item["id"])
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"   Embedded {len(documents)} knowledge items")
    
    def _search_knowledge(self, query: str, n_results: int = 5):
        """Search knowledge base using semantic similarity"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        relevant_knowledge = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                relevant_knowledge.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else None
                })
        
        return relevant_knowledge
    
    def generate_sql(self, natural_language_query: str) -> tuple:
        """Generate SQL using hybrid approach"""
        print(f"🔍 Searching knowledge base for: '{natural_language_query}'")
        relevant_knowledge = self._search_knowledge(natural_language_query, n_results=5)
        
        knowledge_context = "\n\nRELEVANT KNOWLEDGE:\n"
        for i, item in enumerate(relevant_knowledge, 1):
            knowledge_context += f"\n{i}. {item['content']}\n"
        
        prompt = f"""{self.schema_context}
{knowledge_context}

USER QUESTION: {natural_language_query}

Using the database schema and relevant knowledge above, generate a PostgreSQL query to answer this question.
Return ONLY the SQL query, no explanations or markdown formatting.
Make sure to follow any business rules mentioned in the knowledge."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            sql_query = message.content[0].text.strip()
            
            if sql_query.startswith("```sql"):
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            elif sql_query.startswith("```"):
                sql_query = sql_query.replace("```", "").strip()
            
            print(f"✨ Used {len(relevant_knowledge)} relevant knowledge items")
            
            return sql_query, relevant_knowledge
            
        except Exception as e:
            raise Exception(f"Error generating SQL: {str(e)}")
    
    def execute_sql(self, sql_query: str):
        """Execute SQL query"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute(sql_query)
            
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                "columns": columns,
                "rows": results,
                "row_count": len(results)
            }
            
        except Exception as e:
            raise Exception(f"Error executing SQL: {str(e)}")
    
    def query(self, natural_language_query: str):
        """Complete hybrid RAG pipeline"""
        sql_query, relevant_knowledge = self.generate_sql(natural_language_query)
        results = self.execute_sql(sql_query)
        
        return {
            "sql": sql_query,
            "results": results,
            "relevant_knowledge": relevant_knowledge
        }
    
    def explain_results(self, natural_language_query: str, sql_query: str, results: dict) -> str:
        """Generate natural language explanation"""
        results_text = f"Columns: {', '.join(results['columns'])}\n"
        results_text += f"Row count: {results['row_count']}\n\n"
        
        if results['row_count'] > 0:
            results_text += "Sample data:\n"
            for i, row in enumerate(results['rows'][:10]):
                results_text += f"Row {i+1}: {row}\n"
        
        prompt = f"""The user asked: "{natural_language_query}"

The SQL query generated was:
{sql_query}

The results are:
{results_text}

Provide a clear, concise natural language answer to the user's question based on these results. Be specific with numbers and details."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text.strip()
            
        except Exception as e:
            return f"Error generating explanation: {str(e)}"
