"""
SQL RAG Engine using Claude Sonnet 4
Converts natural language queries to SQL and executes them

HOW IT WORKS:
1. Loads database schema (table/column structure) on initialization
2. When user asks a question:
   - Takes the question + schema context
   - Sends to Claude to generate SQL
   - Executes the SQL on PostgreSQL
   - Returns results
3. Optionally: Sends results back to Claude for natural language explanation

NOTE: This is a SIMPLE RAG approach - no embeddings or vector search yet!
It just uses the database schema as context.
"""
import os
import psycopg2
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file (API keys, DB config)
load_dotenv()


class SQLRAGEngine:
    def __init__(self):
        """
        Initialize the SQL RAG engine
        
        Sets up:
        1. Anthropic client for Claude API
        2. Database connection configuration
        3. Database schema context (loaded once at startup)
        """
        # Initialize Claude client with API key
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Database configuration - supports both local and Docker environments
        # In Docker: DB_HOST=postgres (service name)
        # Locally: DB_HOST=localhost
        db_host = os.getenv("DB_HOST", "localhost")
        self.db_config = {
            "host": db_host,
            "database": "sql_rag_poc",
            "user": "postgres",
            "password": "postgres",
            "port": 5432
        }
        
        # Load database schema once at initialization
        # This is the "context" for our RAG system - no embeddings, just schema structure
        self.schema_context = self._get_schema_context()
    
    def _get_schema_context(self):
        """
        Get database schema for context (the "Retrieval" part of RAG)
        
        This method:
        1. Connects to PostgreSQL
        2. Queries the information_schema to get all table/column metadata
        3. Formats it as readable text
        4. Returns this as context to be sent to Claude
        
        WHY: This schema context helps Claude understand what tables/columns exist
        so it can generate accurate SQL queries.
        
        NOTE: No embeddings here - just plain text schema description!
        """
        try:
            # Connect to the database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Query PostgreSQL's metadata to get all table and column information
            # information_schema.columns contains metadata about every column in the database
            cursor.execute("""
                SELECT 
                    table_name,      -- Which table this column belongs to
                    column_name,     -- Name of the column
                    data_type,       -- Data type (INTEGER, VARCHAR, etc.)
                    is_nullable      -- Whether NULL values are allowed
                FROM information_schema.columns
                WHERE table_schema = 'public'  -- Only get user tables (not system tables)
                ORDER BY table_name, ordinal_position  -- Group by table, keep column order
            """)
            
            schema_info = cursor.fetchall()
            
            # Format schema as human-readable text
            # This will be sent to Claude as context
            schema_text = "DATABASE SCHEMA:\n\n"
            current_table = None
            
            # Loop through each column and format nicely
            for table, column, dtype, nullable in schema_info:
                # When we encounter a new table, add a header
                if table != current_table:
                    if current_table is not None:
                        schema_text += "\n"
                    schema_text += f"Table: {table}\n"
                    current_table = table
                
                # Add column information
                null_str = "NULL" if nullable == "YES" else "NOT NULL"
                schema_text += f"  - {column}: {dtype} ({null_str})\n"
            
            # Add foreign key relationships manually
            # (In a production system, you'd query this from information_schema too)
            schema_text += "\nRELATIONSHIPS:\n"
            schema_text += "- orders.customer_id → customers.customer_id\n"
            schema_text += "- order_items.order_id → orders.order_id\n"
            schema_text += "- order_items.product_id → products.product_id\n"
            
            # Clean up database connection
            cursor.close()
            conn.close()
            
            return schema_text
            
        except Exception as e:
            print(f"Error getting schema: {e}")
            return ""
    
    def generate_sql(self, natural_language_query: str) -> str:
        """
        Convert natural language to SQL using Claude (the "Generation" part of RAG)
        
        This is where the magic happens:
        1. Takes user's natural language question
        2. Combines it with database schema context
        3. Sends to Claude Sonnet 4
        4. Claude generates SQL based on the context
        
        Args:
            natural_language_query: User's question in plain English
            
        Returns:
            SQL query string that answers the question
            
        Example:
            Input: "How many customers do we have?"
            Output: "SELECT COUNT(*) FROM customers;"
        """
        
        # Build the prompt for Claude
        # IMPORTANT: We include the schema context so Claude knows what tables/columns exist
        prompt = f"""{self.schema_context}

USER QUESTION: {natural_language_query}

Generate a PostgreSQL query to answer this question. Return ONLY the SQL query, no explanations or markdown formatting.
Make sure the query is safe and uses proper JOINs where needed."""

        try:
            # Call Claude Sonnet 4 API
            # This sends the prompt and gets back SQL
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",  # Latest Claude model
                max_tokens=1024,  # Max length of response
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the SQL from Claude's response
            sql_query = message.content[0].text.strip()
            
            # Clean up any markdown formatting if Claude included it
            # Sometimes Claude wraps SQL in ```sql code blocks
            if sql_query.startswith("```sql"):
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            elif sql_query.startswith("```"):
                sql_query = sql_query.replace("```", "").strip()
            
            return sql_query
            
        except Exception as e:
            raise Exception(f"Error generating SQL: {str(e)}")
    
    def execute_sql(self, sql_query: str):
        """
        Execute SQL query and return results
        
        This is the "data retrieval" step - actually runs the SQL against PostgreSQL
        
        Args:
            sql_query: The SQL query to execute (generated by Claude)
            
        Returns:
            Dictionary containing:
            - columns: List of column names
            - rows: List of tuples with actual data
            - row_count: Number of rows returned
            
        Example:
            Input: "SELECT COUNT(*) FROM customers"
            Output: {
                "columns": ["count"],
                "rows": [(8,)],
                "row_count": 1
            }
        """
        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Execute the SQL query that Claude generated
            cursor.execute(sql_query)
            
            # Get column names from the cursor description
            # cursor.description contains metadata about the result columns
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Fetch all rows from the result
            # Returns a list of tuples, e.g., [(1, 'John', 'Doe'), (2, 'Jane', 'Smith')]
            results = cursor.fetchall()
            
            # Clean up database connection
            cursor.close()
            conn.close()
            
            # Return structured result
            return {
                "columns": columns,
                "rows": results,
                "row_count": len(results)
            }
            
        except Exception as e:
            raise Exception(f"Error executing SQL: {str(e)}")
    
    def query(self, natural_language_query: str):
        """
        Complete RAG pipeline - this is the main method!
        
        STEP-BY-STEP PROCESS:
        1. User asks question in natural language
        2. generate_sql() → Sends question + schema to Claude → Gets SQL back
        3. execute_sql() → Runs SQL on PostgreSQL → Gets data back
        4. Returns both SQL and results
        
        This is called "RAG" because:
        - Retrieval: We retrieve the schema context
        - Augmented: We augment the user's question with that context
        - Generation: Claude generates SQL based on the augmented prompt
        
        Args:
            natural_language_query: User's question (e.g., "How many orders?")
            
        Returns:
            Dictionary with:
            - sql: The generated SQL query
            - results: The query results (columns, rows, count)
        """
        # STEP 1: Generate SQL from natural language using Claude + schema context
        sql_query = self.generate_sql(natural_language_query)
        
        # STEP 2: Execute the SQL on PostgreSQL
        results = self.execute_sql(sql_query)
        
        # STEP 3: Return everything
        return {
            "sql": sql_query,
            "results": results
        }
    
    def explain_results(self, natural_language_query: str, sql_query: str, results: dict) -> str:
        """
        Use Claude to generate a natural language explanation of results
        
        This is an OPTIONAL step that makes the chatbot more user-friendly.
        Instead of just showing raw SQL results, we ask Claude to explain them
        in natural language.
        
        PROCESS:
        1. Take the user's original question
        2. Take the SQL we generated
        3. Take the results from the database
        4. Send all of this to Claude
        5. Claude writes a natural language answer
        
        Args:
            natural_language_query: Original user question
            sql_query: The SQL that was generated
            results: The data returned from the database
            
        Returns:
            Natural language explanation (e.g., "You have 8 customers in total.")
        """
        
        # Format results into readable text for Claude
        results_text = f"Columns: {', '.join(results['columns'])}\n"
        results_text += f"Row count: {results['row_count']}\n\n"
        
        # Include sample data (first 10 rows) so Claude can see what was returned
        if results['row_count'] > 0:
            results_text += "Sample data:\n"
            for i, row in enumerate(results['rows'][:10]):  # Show first 10 rows
                results_text += f"Row {i+1}: {row}\n"
        
        # Build prompt asking Claude to explain the results
        prompt = f"""The user asked: "{natural_language_query}"

The SQL query generated was:
{sql_query}

The results are:
{results_text}

Provide a clear, concise natural language answer to the user's question based on these results. Be specific with numbers and details."""

        try:
            # Ask Claude to explain the results in natural language
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
    rag = SQLRAGEngine()
    
    # Test queries
    test_queries = [
        "How many customers do we have?",
        "What are the top 5 most expensive products?",
        "Show me all orders from customers in the USA",
        "What's the total revenue from completed orders?",
    ]
    
    print("Testing SQL RAG Engine")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n📝 Question: {query}")
        print("-" * 80)
        
        try:
            result = rag.query(query)
            print(f"🔍 SQL: {result['sql']}")
            print(f"📊 Results: {result['results']['row_count']} rows")
            
            if result['results']['row_count'] > 0:
                print(f"   Columns: {result['results']['columns']}")
                for i, row in enumerate(result['results']['rows'][:3]):
                    print(f"   Row {i+1}: {row}")
            
            # Get natural language answer
            answer = rag.explain_results(query, result['sql'], result['results'])
            print(f"\n💬 Answer: {answer}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
