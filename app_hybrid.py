"""
Streamlit UI for HYBRID SQL RAG Chatbot with Embeddings
ChatGPT-style interface with sidebar chat history
"""
import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from sql_rag_hybrid import SQLRAGHybridEngine

# Page config
st.set_page_config(
    page_title="Hybrid SQL RAG Chatbot",
    page_icon="🗄️",
    layout="wide"
)

# Initialize session state for ChatGPT-style interface
if "chats" not in st.session_state:
    st.session_state.chats = []  # List of all chats: [{id, title, messages, created_at}]
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None  # Currently active chat

# Helper function to strip markdown formatting
def strip_markdown(text):
    """Remove ALL markdown formatting characters aggressively"""
    if not text:
        return text
    
    import re
    
    # Remove bold **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    
    # Remove italic *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # Remove any remaining asterisks, underscores, backticks
    text = text.replace('*', '')
    text = text.replace('_', '')
    text = text.replace('`', '')
    text = text.replace('~', '')
    
    # Remove markdown links [text](url)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    # Remove markdown headers
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    return text

# Helper functions for visualization
def should_create_chart(query):
    """Detect if user explicitly asks for a visualization"""
    query_lower = query.lower()
    chart_keywords = [
        'plot', 'chart', 'graph', 'visualize', 'visualization', 'show me a',
        'bar chart', 'line chart', 'pie chart', 'scatter plot', 'histogram'
    ]
    return any(keyword in query_lower for keyword in chart_keywords)

def create_chart(df, query):
    """
    Intelligently create a chart based on the data and query
    Returns a plotly figure or None
    """
    if df is None or df.empty or len(df) == 0:
        return None
    
    query_lower = query.lower()
    
    # Get column names
    columns = df.columns.tolist()
    if len(columns) < 2:
        return None
    
    # Determine chart type based on keywords and data
    if 'pie' in query_lower and len(columns) >= 2:
        # Pie chart - first column as labels, second as values
        fig = px.pie(df, names=columns[0], values=columns[1], 
                     title=f"{columns[1]} by {columns[0]}")
        
    elif ('line' in query_lower or 'trend' in query_lower or 'over time' in query_lower) and len(columns) >= 2:
        # Line chart
        fig = px.line(df, x=columns[0], y=columns[1], 
                      title=f"{columns[1]} over {columns[0]}",
                      markers=True)
        
    elif 'scatter' in query_lower and len(columns) >= 2:
        # Scatter plot
        fig = px.scatter(df, x=columns[0], y=columns[1],
                        title=f"{columns[1]} vs {columns[0]}")
        
    else:
        # Default: Bar chart (most common)
        # Use first column as x-axis, second as y-axis
        fig = px.bar(df, x=columns[0], y=columns[1],
                     title=f"{columns[1]} by {columns[0]}")
    
    # Update layout for dark theme
    fig.update_layout(
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

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

# Helper functions for chat management
def create_new_chat():
    """Create a new chat session"""
    chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_chat = {
        "id": chat_id,
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now()
    }
    st.session_state.chats.insert(0, new_chat)  # Add to beginning
    st.session_state.current_chat_id = chat_id
    return chat_id

def get_current_chat():
    """Get the currently active chat"""
    if not st.session_state.current_chat_id:
        return None
    for chat in st.session_state.chats:
        if chat["id"] == st.session_state.current_chat_id:
            return chat
    return None

def add_message_to_chat(question, sql, results, relevant_knowledge, answer, chart_data=None, error=None):
    """Add a message to the current chat"""
    current_chat = get_current_chat()
    if current_chat:
        message = {
            "question": question,
            "sql": sql,
            "results": results,
            "relevant_knowledge": relevant_knowledge,
            "answer": answer,
            "chart_data": chart_data,  # Store dataframe for chart regeneration
            "error": error,
            "timestamp": datetime.now()
        }
        current_chat["messages"].append(message)
        
        # Update chat title from first question
        if len(current_chat["messages"]) == 1 and current_chat["title"] == "New Chat":
            # Use first 50 chars of question as title
            current_chat["title"] = question[:50] + ("..." if len(question) > 50 else "")

def switch_chat(chat_id):
    """Switch to a different chat"""
    st.session_state.current_chat_id = chat_id

def delete_chat(chat_id):
    """Delete a chat"""
    st.session_state.chats = [c for c in st.session_state.chats if c["id"] != chat_id]
    if st.session_state.current_chat_id == chat_id:
        st.session_state.current_chat_id = st.session_state.chats[0]["id"] if st.session_state.chats else None

# Sidebar with chat history (ChatGPT-style)
with st.sidebar:
    st.title("💬 Chats")
    
    # New Chat button (prominent)
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        create_new_chat()
        st.rerun()
    
    st.divider()
    
    # Display chat history list
    if st.session_state.chats:
        st.markdown("### Recent Conversations")
        for chat in st.session_state.chats:
            # Skip the current empty "New Chat"
            if chat["title"] == "New Chat" and len(chat.get("messages", [])) == 0:
                continue
            
            # Chat item container
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Make chat title clickable
                is_current = chat["id"] == st.session_state.current_chat_id
                button_type = "primary" if is_current else "secondary"
                
                # Show message count in button label
                msg_count = len(chat.get("messages", []))
                button_label = f"💬 {chat['title']}"
                
                if st.button(
                    button_label, 
                    key=f"chat_{chat['id']}", 
                    use_container_width=True,
                    type=button_type if is_current else "secondary"
                ):
                    switch_chat(chat["id"])
                    st.rerun()
                
                # Show message count and time below
                if msg_count > 0:
                    time_str = chat["created_at"].strftime("%b %d, %I:%M %p")
                    st.caption(f"    💬 {msg_count} message{'s' if msg_count != 1 else ''} • {time_str}")
            
            with col2:
                # Delete button
                if st.button("🗑️", key=f"del_{chat['id']}", help="Delete chat"):
                    delete_chat(chat["id"])
                    st.rerun()
    else:
        st.info("No chats yet. Click '➕ New Chat' to start!")
    
    st.divider()
    
    # Collapsible info section
    with st.expander("ℹ️ About"):
        st.markdown("""
        **Hybrid SQL RAG** with:
        - 🧠 Semantic search
        - 🔍 Smart context retrieval
        - 🤖 Claude Sonnet 4
        - 📊 Sample data embeddings
        
        **Database Tables:**
        - customers
        - products  
        - orders
        - order_items
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
        
        st.markdown("### 📖 Data Dictionary")
        
        st.markdown("**customers**")
        st.markdown("""
        - `customer_id`: Unique customer identifier (Primary Key)
        - `name`: Full name of the customer
        - `email`: Contact email address
        - `country`: Customer's country of residence
        """)
        
        st.markdown("**products**")
        st.markdown("""
        - `product_id`: Unique product identifier (Primary Key)
        - `name`: Product name/title
        - `category`: Product category (Electronics, Furniture, etc.)
        - `price`: Current price in USD
        - `stock`: Available inventory count
        - **Business Rule**: Products with stock < 20 are considered "low stock"
        """)
        
        st.markdown("**orders**")
        st.markdown("""
        - `order_id`: Unique order identifier (Primary Key)
        - `customer_id`: Reference to customer who placed order (Foreign Key)
        - `order_date`: Date when order was placed
        - `status`: Order status (pending, completed, cancelled)
        - **Business Rule**: Only completed orders count toward revenue
        """)
        
        st.markdown("**order_items**")
        st.markdown("""
        - `item_id`: Unique line item identifier (Primary Key)
        - `order_id`: Reference to parent order (Foreign Key)
        - `product_id`: Reference to product purchased (Foreign Key)
        - `quantity`: Number of units ordered
        - `price`: Price per unit at time of purchase
        - **Business Rule**: Total revenue = SUM(quantity × price)
        """)
    
    
    with st.expander("💡 Example Questions"):
        st.markdown("""
        - What's our total revenue?
        - Show me the top spenders
        - Which products are running low?
        - What did John Doe buy?
        """)

# Main content area
try:
    rag = get_rag_engine()
    
    # Create new chat if none exists
    if not st.session_state.current_chat_id:
        create_new_chat()
    
    current_chat = get_current_chat()
    
    # Header
    st.title("🗄️ SQL RAG Chatbot")
    st.markdown("Ask questions about your database in natural language")
    st.divider()
    
    # Display chat messages or welcome screen
    if current_chat and current_chat["messages"]:
        for msg in current_chat["messages"]:
            # User message
            with st.chat_message("user"):
                st.markdown(msg["question"])
            
            # Assistant message
            with st.chat_message("assistant"):
                if msg.get("error"):
                    st.error(f"❌ {msg['error']}")
                else:
                    # Show answer prominently (strip markdown and display as plain text)
                    if msg.get("answer"):
                        clean_text = strip_markdown(msg["answer"])
                        st.text(clean_text)
                    
                    # Show chart if it exists
                    if msg.get("chart_data") is not None:
                        with st.expander("📊 Visualization", expanded=True):
                            fig = create_chart(msg["chart_data"], msg["question"])
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                    
                    # Technical details in expanders
                    with st.expander("🔍 View SQL Query"):
                        st.code(msg["sql"], language='sql')
                    
                    if msg.get("results") and msg["results"]["row_count"] > 0:
                        with st.expander(f"📊 View Results ({msg['results']['row_count']} rows)"):
                            df = pd.DataFrame(
                                msg["results"]["rows"],
                                columns=msg["results"]["columns"]
                            )
                            st.dataframe(df, use_container_width=True)
                    
                    if msg.get("relevant_knowledge"):
                        with st.expander("💡 Relevant Knowledge Retrieved"):
                            for i, item in enumerate(msg['relevant_knowledge'], 1):
                                st.markdown(f"""
                                **{i}. {item['metadata'].get('type', 'Unknown').replace('_', ' ').title()}**
                                
                                {item['content']}
                                
                                *Similarity: {1 - item.get('distance', 0):.2%}*
                                """)
                                if i < len(msg['relevant_knowledge']):
                                    st.divider()
    else:
        # Welcome screen when no messages
        st.markdown("### 👋 Welcome to SQL RAG Chatbot!")
        st.markdown("I can help you query your database using natural language. Just ask a question below!")
        
        st.markdown("")
        
        # Example questions in a nice grid with containers
        st.markdown("### 💡 Try asking:")
        
        col1, col2 = st.columns(2, gap="medium")
        
        with col1:
            with st.container(border=True):
                st.markdown("**📊 Analytics Questions**")
                st.markdown("""
                - What's our total revenue?
                - Show me the top 5 customers by spending
                - How many orders were placed this month?
                - What's the average order value?
                """)
            
            with st.container(border=True):
                st.markdown("**📦 Inventory Questions**")
                st.markdown("""
                - Which products are running low on stock?
                - Show me all Electronics products
                - What's the most expensive product?
                - List products under $50
                """)
        
        with col2:
            with st.container(border=True):
                st.markdown("**👥 Customer Questions**")
                st.markdown("""
                - How many customers do we have?
                - Show me customers from USA
                - Which customer spent the most?
                - List customers who joined this year
                """)
            
            with st.container(border=True):
                st.markdown("**📦 Order Questions**")
                st.markdown("""
                - Show me pending orders
                - What did John Doe buy?
                - List completed orders from last week
                - Show me orders over $500
                """)
        
        st.markdown("")
        st.success("💬 **Pro tip:** Add 'plot', 'chart', or 'graph' to your question to visualize results!")
    
    # Chat input at bottom
    user_query = st.chat_input("Ask a question about your database...")
    
    if user_query:
        # Add user message immediately
        with st.chat_message("user"):
            st.markdown(user_query)
        
        # Process query
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    # Get conversation history for context
                    current_chat = get_current_chat()
                    chat_history = current_chat["messages"] if current_chat else []
                    
                    # Query the database with conversation context
                    result = rag.query(user_query, conversation_history=chat_history)
                    
                    # Get natural language answer
                    answer = None
                    if result['results']['row_count'] > 0:
                        answer = rag.explain_results(
                            user_query,
                            result['sql'],
                            result['results']
                        )
                    else:
                        answer = "No results found for this query."
                    
                    # Check if user wants a chart
                    chart_df = None
                    if should_create_chart(user_query) and result['results']['row_count'] > 0:
                        chart_df = pd.DataFrame(
                            result['results']['rows'],
                            columns=result['results']['columns']
                        )
                    
                    # Show answer (strip markdown and display as plain text)
                    clean_text = strip_markdown(answer)
                    st.text(clean_text)
                    
                    # Show chart if requested
                    if chart_df is not None:
                        with st.expander("📊 Visualization", expanded=True):
                            fig = create_chart(chart_df, user_query)
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Unable to create chart with this data structure.")
                    
                    # Add to chat history
                    add_message_to_chat(
                        user_query,
                        result['sql'],
                        result['results'],
                        result.get('relevant_knowledge', []),
                        answer,
                        chart_data=chart_df
                    )
                    
                    # Show technical details
                    if result.get('relevant_knowledge'):
                        with st.expander("💡 Relevant Knowledge Retrieved"):
                            for i, item in enumerate(result['relevant_knowledge'], 1):
                                st.markdown(f"""
                                **{i}. {item['metadata'].get('type', 'Unknown').replace('_', ' ').title()}**
                                
                                {item['content']}
                                
                                *Similarity: {1 - item.get('distance', 0):.2%}*
                                """)
                                if i < len(result['relevant_knowledge']):
                                    st.divider()
                    
                    with st.expander("🔍 View SQL Query"):
                        st.code(result['sql'], language='sql')
                    
                    if result['results']['row_count'] > 0:
                        with st.expander(f"📊 View Results ({result['results']['row_count']} rows)"):
                            df = pd.DataFrame(
                                result['results']['rows'],
                                columns=result['results']['columns']
                            )
                            st.dataframe(df, use_container_width=True)
                    
                except Exception as e:
                    error_msg = str(e)
                    st.error(f"❌ {error_msg}")
                    add_message_to_chat(user_query, None, None, [], None, chart_data=None, error=error_msg)
        
        st.rerun()

except Exception as e:
    st.error(f"""
    **Unable to initialize the system.**
    
    Error: {str(e)}
    
    Please make sure:
    1. PostgreSQL is running
    2. The database exists
    3. Dependencies are installed
    """)

# Footer
st.divider()
st.caption("Powered by Claude Sonnet 4 + PostgreSQL + Vector Search")
