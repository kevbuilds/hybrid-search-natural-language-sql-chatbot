"""
Streamlit UI for HYBRID SQL RAG Chatbot with Embeddings
"""
import streamlit as st
import pandas as pd
import os
import hashlib
from sql_rag_hybrid import SQLRAGHybridEngine

# Page config
st.set_page_config(
    page_title="Hybrid SQL RAG Chatbot",
    page_icon="🗄️",
    layout="wide"
)

# 🔐 PASSWORD PROTECTION
# =====================
# This checks for password before allowing access to the app
# Password is stored in Streamlit secrets (not in code!)

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # Get password from Streamlit secrets (deployed) or environment variable (local)
        correct_password = st.secrets.get("APP_PASSWORD", os.getenv("APP_PASSWORD", "demo123"))
        
        # Hash the entered password for comparison
        entered_password = st.session_state["password"]
        
        if entered_password == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run, show password input
    if "password_correct" not in st.session_state:
        st.markdown("## 🔐 Authentication Required")
        st.markdown("Please enter the password to access the SQL RAG Chatbot.")
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    
    # Password not correct, show error and input again
    elif not st.session_state["password_correct"]:
        st.markdown("## 🔐 Authentication Required")
        st.error("😕 Password incorrect. Please try again.")
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    
    # Password correct
    else:
        return True

# Check password before showing the app
if not check_password():
    st.stop()  # Don't continue if password check failed

# Initialize RAG engine
@st.cache_resource
def get_rag_engine():
    return SQLRAGHybridEngine()

# Header
st.title("🗄️ Hybrid SQL RAG - Talk to Your Database")
st.markdown("Ask questions about your database in natural language, powered by **Claude Sonnet 4** + **Embeddings**")

# Sidebar with info
with st.sidebar:
    st.header("About")
    st.markdown("""
    This is an **ENHANCED** SQL RAG system with:
    
    1. 📝 Natural language questions
    2. 🧠 **Semantic search** using embeddings
    3. 🔍 **Hybrid retrieval** (schema + knowledge)
    4. 🤖 Claude Sonnet 4 for SQL generation
    5. 🗄️ Execution on PostgreSQL
    6. 💬 Natural language answers
    
    ### What's New? ✨
    
    **Embeddings & Vector Search:**
    - Understands synonyms and intent
    - Finds relevant query patterns
    - Applies business rules automatically
    - Smarter context selection
    
    ### Database Schema
    - **customers**: Customer information
    - **products**: Product catalog
    - **orders**: Order records
    - **order_items**: Order line items
    """)
    
    # Add expandable section to view actual data
    with st.expander("📊 View Database Schema & Sample Data"):
        st.markdown("### Table Structures")
        
        st.markdown("**customers**")
        st.code("""
customer_id | name           | email                | country
------------|----------------|---------------------|----------
1           | John Doe       | john@example.com    | USA
2           | Jane Smith     | jane@example.com    | UK
3           | Bob Johnson    | bob@example.com     | Canada
        """, language="text")
        
        st.markdown("**products**")
        st.code("""
product_id | name          | category     | price  | stock
-----------|---------------|--------------|--------|-------
1          | Laptop Pro    | Electronics  | 1200   | 15
2          | Wireless Mouse| Electronics  | 25     | 100
3          | Office Chair  | Furniture    | 350    | 30
        """, language="text")
        
        st.markdown("**orders**")
        st.code("""
order_id | customer_id | order_date | status
---------|-------------|------------|----------
1        | 1           | 2024-01-15 | completed
2        | 2           | 2024-01-20 | pending
3        | 3           | 2024-01-22 | completed
        """, language="text")
        
        st.markdown("**order_items**")
        st.code("""
item_id | order_id | product_id | quantity | price
--------|----------|------------|----------|-------
1       | 1        | 1          | 1        | 1200
2       | 1        | 2          | 2        | 25
3       | 2        | 3          | 1        | 350
        """, language="text")
    
    st.divider()
    
    st.header("Example Questions")
    st.markdown("""
    **Try these complex queries:**
    
    - What's our total revenue?
    - Show me the top spenders
    - Which products are running low?
    - How many customers from Europe?
    - What did John Doe buy?
    - Show me expensive electronics
    - Which orders are pending?
    """)

# Main content
try:
    rag = get_rag_engine()
    
    # Query input
    st.subheader("Ask a Question")
    user_query = st.text_input(
        "Enter your question:",
        placeholder="e.g., What's the total revenue from completed orders?",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.rerun()
    
    if ask_button and user_query:
        with st.spinner("🤔 Thinking..."):
            try:
                # Query the database
                result = rag.query(user_query)
                
                # Show what knowledge was retrieved
                if result.get('relevant_knowledge'):
                    with st.expander("💡 Relevant Knowledge Retrieved", expanded=False):
                        for i, item in enumerate(result['relevant_knowledge'], 1):
                            st.markdown(f"""
                            **{i}. {item['metadata'].get('type', 'Unknown').replace('_', ' ').title()}**
                            
                            {item['content']}
                            
                            *Similarity: {1 - item.get('distance', 0):.2%}*
                            """)
                            st.divider()
                
                # Display SQL query
                st.subheader("Generated SQL")
                st.code(result['sql'], language='sql')
                
                # Display results
                st.subheader("Query Results")
                
                if result['results']['row_count'] > 0:
                    # Convert to DataFrame for better display
                    df = pd.DataFrame(
                        result['results']['rows'],
                        columns=result['results']['columns']
                    )
                    
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"📊 {result['results']['row_count']} row(s) returned")
                    
                    # Get natural language answer
                    with st.spinner("✍️ Generating answer..."):
                        answer = rag.explain_results(
                            user_query,
                            result['sql'],
                            result['results']
                        )
                    
                    st.subheader("Answer")
                    st.success(answer)
                    
                else:
                    st.info("No results found for this query.")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    elif ask_button:
        st.warning("Please enter a question!")

except Exception as e:
    st.error(f"""
    **Unable to initialize the system.**
    
    Error: {str(e)}
    
    Please make sure:
    1. PostgreSQL is running
    2. The database 'sql_rag_poc' exists
    3. Dependencies are installed
    """)

# Footer
st.divider()
st.caption("Powered by Claude Sonnet 4 (Anthropic) + Embeddings (sentence-transformers) + PostgreSQL")
