"""
Streamlit UI for HYBRID SQL RAG - Cloud Deployment Version
Optimized for Streamlit Cloud with Supabase PostgreSQL
"""
import streamlit as st
import pandas as pd
from sql_rag_cloud import SQLRAGHybridEngine

# Page config
st.set_page_config(
    page_title="Hybrid SQL RAG Chatbot",
    page_icon="🗄️",
    layout="wide"
)

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
    5. 🗄️ Execution on PostgreSQL (Supabase)
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
    - What are the top 5 products by price?
    """)
    
    st.divider()
    
    st.caption("💡 **Tip:** The system uses hybrid search to understand your intent and apply business rules automatically!")

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
                    with st.expander("💡 Relevant Knowledge Retrieved (Semantic Search)", expanded=False):
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
                
                # Show debug info in expander
                with st.expander("🔧 Debug Information"):
                    st.code(str(e))
    
    elif ask_button:
        st.warning("Please enter a question!")

except Exception as e:
    st.error(f"""
    **Unable to initialize the system.**
    
    Error: {str(e)}
    
    Please make sure:
    1. Supabase PostgreSQL is configured
    2. Database credentials are in Streamlit secrets
    3. Tables are created and populated
    4. ANTHROPIC_API_KEY is set
    """)
    
    # Show debug info
    with st.expander("🔧 Debug Information"):
        st.code(str(e))

# Footer
st.divider()
st.caption("Powered by Claude Sonnet 4 (Anthropic) + Embeddings (sentence-transformers) + PostgreSQL (Supabase)")
st.caption("🚀 Deployed on Streamlit Cloud")
