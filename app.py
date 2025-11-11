"""
Streamlit UI for SQL RAG Chatbot
"""
import streamlit as st
import pandas as pd
from sql_rag import SQLRAGEngine

# Page config
st.set_page_config(
    page_title="SQL RAG Chatbot",
    page_icon="🗄️",
    layout="wide"
)

# Initialize RAG engine
@st.cache_resource
def get_rag_engine():
    return SQLRAGEngine()

# Header
st.title("🗄️ SQL RAG - Talk to Your Database")
st.markdown("Ask questions about your database in natural language, powered by **Claude 3.5 Sonnet**")

# Sidebar with info
with st.sidebar:
    st.header("About")
    st.markdown("""
    This POC demonstrates a **SQL RAG system** that:
    
    1. 📝 Takes natural language questions
    2. 🤖 Uses Claude 3.5 to generate SQL
    3. 🗄️ Executes queries on PostgreSQL
    4. 💬 Returns natural language answers
    
    ### Database Schema
    - **customers**: Customer information
    - **products**: Product catalog
    - **orders**: Order records
    - **order_items**: Order line items
    """)
    
    st.divider()
    
    st.header("Example Questions")
    st.markdown("""
    - How many customers do we have?
    - What are the top 5 products by price?
    - Show me orders from the last month
    - What's the total revenue?
    - Which customer spent the most?
    - What products are low in stock?
    - Show me all electronics products
    """)

# Main content
try:
    rag = get_rag_engine()
    
    # Query input
    st.subheader("Ask a Question")
    user_query = st.text_input(
        "Enter your question:",
        placeholder="e.g., How many orders were placed in October 2024?",
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
    **Unable to connect to the database.**
    
    Please make sure:
    1. PostgreSQL is running on localhost:5432
    2. The database 'sql_rag_poc' exists
    3. Run `python database_setup.py` first
    
    Error: {str(e)}
    """)

# Footer
st.divider()
st.caption("Powered by Claude 3.5 Sonnet (Anthropic) & PostgreSQL")
