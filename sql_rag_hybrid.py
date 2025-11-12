"""
SQL RAG Engine with HYBRID SEARCH using Embeddings

This is an enhanced version that uses:
1. Vector embeddings for semantic search (finds relevant knowledge)
2. Traditional schema context (table/column structure)
3. Claude Sonnet 4 for SQL generation

HOW IT WORKS:
1. INITIALIZATION:
   - Loads database schema (like before)
   - Creates embeddings of knowledge base (table descriptions, patterns, rules)
   - Stores embeddings in ChromaDB vector database

2. QUERY TIME (Hybrid Retrieval):
   - User asks a question
   - STEP 1: Embed the question using sentence-transformers
   - STEP 2: Search ChromaDB for similar knowledge (semantic search)
   - STEP 3: Retrieve relevant context (descriptions, patterns, rules)
   - STEP 4: Combine with database schema
   - STEP 5: Send everything to Claude
   - STEP 6: Claude generates SQL with richer context
   - STEP 7: Execute SQL and return results

BENEFITS over simple RAG:
- Understands synonyms (e.g., "revenue" = "sales" = "income")
- Finds relevant query patterns automatically
- Applies business rules contextually
- Better at complex questions

🎯 HOW TO IMPROVE YOUR RAG:
=====================================================================
To make your RAG smarter and more effective, add content to knowledge_base.py:

1. ADD BUSINESS RULES:
   - Define calculation rules (e.g., "revenue only includes completed orders")
   - Specify data quality rules (e.g., "ignore orders with null customer_id")
   - Add validation constraints (e.g., "valid status values are: completed, shipped, processing")
   
   Example:
   {
       "id": "revenue_calculation_rule",
       "content": "When calculating revenue, ONLY count orders where status='completed'. 
                   Exclude 'shipped' and 'processing' orders as they haven't been delivered yet.",
       "metadata": {
           "type": "business_rule",
           "category": "finance",
           "keywords": "revenue, sales, income, money, earnings"
       }
   }

2. ADD QUERY PATTERNS:
   - Provide example SQL queries for common questions
   - Show how to handle complex JOINs
   - Demonstrate aggregations and GROUP BY patterns
   
   Example:
   {
       "id": "customer_lifetime_value_pattern",
       "content": "To calculate customer lifetime value: 
                   SELECT c.customer_id, c.first_name, c.last_name, 
                   SUM(o.total_amount) as lifetime_value 
                   FROM customers c 
                   JOIN orders o ON c.customer_id = o.customer_id 
                   WHERE o.status = 'completed' 
                   GROUP BY c.customer_id, c.first_name, c.last_name 
                   ORDER BY lifetime_value DESC",
       "metadata": {
           "type": "query_pattern",
           "complexity": "medium",
           "keywords": "customer value, lifetime, spending, total purchases"
       }
   }

3. ADD TABLE/COLUMN CONTEXT:
   - Explain what columns mean in business terms
   - Document relationships between tables
   - Note any special handling needed
   
   Example:
   {
       "id": "order_status_explanation",
       "content": "The orders.status field has 3 values: 'completed' (delivered and paid), 
                   'shipped' (in transit), 'processing' (being prepared). For analytics, 
                   typically only use 'completed' orders.",
       "metadata": {
           "type": "column_description",
           "table": "orders",
           "column": "status"
       }
   }

4. ADD DOMAIN KNOWLEDGE:
   - Industry-specific terminology
   - Common metrics and KPIs
   - Calculation formulas
   
   Example:
   {
       "id": "average_order_value_definition",
       "content": "Average Order Value (AOV) = Total Revenue / Number of Orders. 
                   Only count completed orders. Formula: 
                   SELECT AVG(total_amount) FROM orders WHERE status = 'completed'",
       "metadata": {
           "type": "domain_knowledge",
           "category": "metrics",
           "keywords": "aov, average order value, basket size"
       }
   }

5. ADD SYNONYMS & VARIATIONS:
   - List alternative ways users might ask questions
   - Map business terms to database fields
   
   Example:
   {
       "id": "revenue_synonyms",
       "content": "Revenue, sales, income, earnings, and turnover all refer to total_amount 
                   in the orders table (where status='completed'). Users might ask about 
                   any of these terms.",
       "metadata": {
           "type": "synonym_mapping",
           "keywords": "revenue, sales, income, earnings, turnover, money"
       }
   }

💡 TIPS FOR EFFECTIVE KNOWLEDGE:
- Use descriptive IDs (e.g., "customer_retention_rule" not "rule_001")
- Add lots of keywords to metadata (helps semantic search)
- Write in natural language (like you're explaining to a person)
- Include SQL examples when possible
- Be specific about edge cases and exceptions

After adding to knowledge_base.py:
1. If ChromaDB is persistent (is_persistent=True), delete ./chroma_db folder to rebuild
2. Restart the app to load new knowledge
3. Test with questions that should trigger the new knowledge
=====================================================================
"""
import os
import psycopg2
from anthropic import Anthropic
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from knowledge_base import DATABASE_KNOWLEDGE

# Try to import streamlit for secrets support
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

load_dotenv()


class SQLRAGHybridEngine:
    def __init__(self):
        """
        Initialize the Hybrid SQL RAG engine with embeddings
        
        Sets up:
        1. Anthropic client for Claude API
        2. Database connection
        3. Embedding model (sentence-transformers)
        4. ChromaDB vector database
        5. Loads and embeds knowledge base
        """
        print("🚀 Initializing Hybrid SQL RAG Engine...")
        
        # Initialize Claude client
        # Try Streamlit secrets first, then environment variables
        if HAS_STREAMLIT and hasattr(st, 'secrets'):
            api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
        else:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or Streamlit secrets")
        
        self.client = Anthropic(api_key=api_key)
        
        # Database configuration - prefer a Neon/DATABASE URL if provided
        # Try Streamlit secrets first, then environment variables
        if HAS_STREAMLIT and hasattr(st, 'secrets'):
            self.neon_dsn = st.secrets.get("NEON_DATABASE_URL") or st.secrets.get("DATABASE_URL") or os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")
        else:
            self.neon_dsn = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")
        
        if self.neon_dsn:
            print("🔌 Using Neon/DATABASE URL from environment")
            # We'll store a simple dict and pass either dsn or kwargs to psycopg2.connect
            self.db_config = {"dsn": self.neon_dsn}
        else:
            db_host = os.getenv("DB_HOST", "localhost")
            self.db_config = {
                "host": db_host,
                "database": os.getenv("DB_NAME", "sql_rag_poc"),
                "user": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", "postgres"),
                "port": int(os.getenv("DB_PORT", 5432))
            }
        
        # Load traditional schema context (still useful!)
        print("📊 Loading database schema...")
        self.schema_context = self._get_schema_context()
        
        # Initialize embedding model
        # Using all-MiniLM-L6-v2: Fast, good quality, runs locally
        print("🧠 Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB (vector database)
        # 
        # 💾 PERSISTENCE OPTIONS:
        # =======================
        # Option 1: In-Memory (Current Setting - is_persistent=False)
        #   ✅ Good for: Development, testing, frequently changing knowledge
        #   ✅ Pro: Always fresh, no stale data
        #   ❌ Con: Slower startup (re-embeds on every restart)
        #   ❌ Con: Lost on restart
        #
        # Option 2: Persistent (is_persistent=True)
        #   ✅ Good for: Production, stable knowledge base
        #   ✅ Pro: Fast startup (embeddings cached on disk)
        #   ✅ Pro: Survives restarts
        #   ⚠️  Con: Must manually delete ./chroma_db to update knowledge
        #   ⚠️  Con: Creates a folder in your project directory
        #
        # 🔧 TO ENABLE PERSISTENCE:
        # 1. Change is_persistent=False to is_persistent=True below
        # 2. Add persist_directory="./chroma_db" to Settings()
        # 3. Add ./chroma_db to .gitignore (don't commit embeddings)
        # 4. To update knowledge: delete ./chroma_db folder and restart
        #
        # Example for persistent storage:
        # self.chroma_client = chromadb.Client(Settings(
        #     anonymized_telemetry=False,
        #     is_persistent=True,
        #     persist_directory="./chroma_db"  # Where to save embeddings
        # ))
        print("💾 Initializing vector database...")
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            is_persistent=False  # ⚠️ CHANGE TO True FOR PERSISTENCE (see notes above)
        ))
        
        # Create or get collection for our knowledge
        self.collection = self.chroma_client.get_or_create_collection(
            name="sql_knowledge",
            metadata={"description": "SQL database knowledge and patterns"}
        )
        
        # Load knowledge base into vector database
        print("📚 Embedding knowledge base...")
        self._load_knowledge_base()
        
        print("✅ Hybrid SQL RAG Engine ready!")
    
    def _get_schema_context(self):
        """
        Get database schema (same as before - still important!)
        This provides the structural context about tables/columns
        """
        try:
            # Support either DSN (Neon/DATABASE_URL) or kwargs
            if 'dsn' in self.db_config:
                conn = psycopg2.connect(self.db_config['dsn'])
            else:
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
        """
        Load knowledge base into ChromaDB with embeddings
        
        This is the KEY STEP for hybrid search!
        
        PROCESS:
        1. Take each piece of knowledge from knowledge_base.py
        2. Generate embedding using sentence-transformers
        3. Store in ChromaDB with metadata
        
        ChromaDB will use these embeddings to find similar content later
        
        🔄 HOW TO UPDATE YOUR KNOWLEDGE BASE:
        =====================================
        1. Edit knowledge_base.py and add new items to DATABASE_KNOWLEDGE list
        2. If ChromaDB is persistent (is_persistent=True):
           - Delete the ./chroma_db folder to force rebuild
           - Or change collection name in __init__ method
        3. If in-memory (is_persistent=False):
           - Just restart the app, it will auto-reload
        
        💡 WHAT GETS EMBEDDED:
        - The "content" field becomes a vector (semantic meaning)
        - The "metadata" helps with filtering and debugging
        - The "id" must be unique for each knowledge item
        
        📊 MONITORING:
        - Check console for "Embedded X knowledge items" on startup
        - More items = better coverage but slower startup
        - Typical sweet spot: 20-100 items for most use cases
        """
        # Check if already loaded (prevents duplicate embeddings)
        existing_count = self.collection.count()
        if existing_count > 0:
            print(f"   Knowledge base already loaded ({existing_count} items)")
            return
        
        # Prepare data for ChromaDB
        documents = []  # The actual text content that gets embedded
        metadatas = []  # Metadata for filtering and debugging (not embedded)
        ids = []        # Unique IDs for each knowledge item
        
        # Load from knowledge_base.py
        # 👉 TO ADD MORE: Edit knowledge_base.py and add items to DATABASE_KNOWLEDGE
        for item in DATABASE_KNOWLEDGE:
            documents.append(item["content"])
            metadatas.append(item["metadata"])
            ids.append(item["id"])
        
        # Add to ChromaDB (it will automatically create embeddings)
        # This is where the magic happens - text becomes vectors!
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"   Embedded {len(documents)} knowledge items")
    
    def _search_knowledge(self, query: str, n_results: int = 5):
        """
        Search knowledge base using semantic similarity
        
        This is the HYBRID part - semantic search!
        
        PROCESS:
        1. User's query is embedded
        2. ChromaDB finds most similar knowledge items
        3. Returns relevant context
        
        Args:
            query: User's natural language question
            n_results: How many relevant items to retrieve
            
        Returns:
            List of relevant knowledge items with similarity scores
        """
        # Query ChromaDB - it will embed the query and find similar items
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
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
        """
        Generate SQL using HYBRID approach
        
        ENHANCED PROCESS:
        1. Perform semantic search to find relevant knowledge
        2. Combine: schema + relevant knowledge + user query
        3. Send enriched context to Claude
        4. Claude generates better SQL with more context
        
        Returns:
            Tuple of (sql_query, relevant_knowledge_used)
        """
        
        # STEP 1: Semantic search for relevant knowledge
        print(f"🔍 Searching knowledge base for: '{natural_language_query}'")
        relevant_knowledge = self._search_knowledge(natural_language_query, n_results=5)
        
        # STEP 2: Build enhanced context
        knowledge_context = "\n\nRELEVANT KNOWLEDGE:\n"
        for i, item in enumerate(relevant_knowledge, 1):
            knowledge_context += f"\n{i}. {item['content']}\n"
        
        # STEP 3: Build comprehensive prompt
        prompt = f"""{self.schema_context}
{knowledge_context}

USER QUESTION: {natural_language_query}

Using the database schema and relevant knowledge above, generate a PostgreSQL query to answer this question.
Return ONLY the SQL query, no explanations or markdown formatting.
Make sure to follow any business rules mentioned in the knowledge."""

        try:
            # STEP 4: Ask Claude with enriched context
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            sql_query = message.content[0].text.strip()
            
            # Clean up markdown if present
            if sql_query.startswith("```sql"):
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            elif sql_query.startswith("```"):
                sql_query = sql_query.replace("```", "").strip()
            
            # Log what knowledge was used
            print(f"✨ Used {len(relevant_knowledge)} relevant knowledge items")
            
            return sql_query, relevant_knowledge
            
        except Exception as e:
            raise Exception(f"Error generating SQL: {str(e)}")
    
    def execute_sql(self, sql_query: str):
        """Execute SQL query (same as before)"""
        try:
            # Support either DSN (Neon/DATABASE_URL) or kwargs
            if 'dsn' in self.db_config:
                conn = psycopg2.connect(self.db_config['dsn'])
            else:
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
        """
        Complete HYBRID RAG pipeline
        
        Now includes semantic search for better context!
        """
        # Generate SQL with hybrid search
        sql_query, relevant_knowledge = self.generate_sql(natural_language_query)
        
        # Execute SQL
        results = self.execute_sql(sql_query)
        
        return {
            "sql": sql_query,
            "results": results,
            "relevant_knowledge": relevant_knowledge  # NEW: Show what knowledge was used
        }
    
    def explain_results(self, natural_language_query: str, sql_query: str, results: dict) -> str:
        """Generate natural language explanation (same as before)"""
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


# Example usage
if __name__ == "__main__":
    print("\n" + "="*80)
    print("HYBRID SQL RAG ENGINE - Demo")
    print("="*80 + "\n")
    
    rag = SQLRAGHybridEngine()
    
    # Test queries that benefit from hybrid search
    test_queries = [
        "What's our total revenue?",  # Should use revenue business rule
        "Show me top spenders",       # Should use customer spending pattern
        "Which products are running low?",  # Should use inventory pattern
        "How many customers from Europe?",  # Should understand geography
    ]
    
    for query in test_queries:
        print(f"\n📝 Question: {query}")
        print("-" * 80)
        
        try:
            result = rag.query(query)
            
            print(f"🔍 SQL: {result['sql']}")
            print(f"📊 Results: {result['results']['row_count']} rows")
            
            if result['results']['row_count'] > 0:
                for i, row in enumerate(result['results']['rows'][:3]):
                    print(f"   Row {i+1}: {row}")
            
            # Show what knowledge was used
            if result['relevant_knowledge']:
                print(f"\n💡 Used knowledge:")
                for item in result['relevant_knowledge'][:2]:
                    print(f"   - {item['metadata'].get('type', 'unknown')}: {item['content'][:100]}...")
            
            answer = rag.explain_results(query, result['sql'], result['results'])
            print(f"\n💬 Answer: {answer}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
