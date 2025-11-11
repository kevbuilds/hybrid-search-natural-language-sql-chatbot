# SQL RAG - Talk to Your Database 🗄️

A Proof of Concept (POC) that demonstrates a SQL RAG (Retrieval Augmented Generation) system using PostgreSQL and Claude 3.5 Sonnet.

## 🚀 Quick Start with Docker (Recommended)

**Prerequisites:** Docker and Docker Compose installed

### One Command Setup:

```bash
docker-compose up
```

That's it! The app will:
1. Start PostgreSQL in a container
2. Create and populate the database with sample data
3. Launch the Streamlit app

**Access the app at:** http://localhost:8501

### Stop the app:
```bash
docker-compose down
```

### Stop and remove all data:
```bash
docker-compose down -v
```

---

## Architecture

```
Natural Language Question
         ↓
    Claude 3.5 Sonnet (with DB schema context)
         ↓
    Generated SQL Query
         ↓
    PostgreSQL Database
         ↓
    Query Results
         ↓
    Claude 3.5 Sonnet (result interpretation)
         ↓
    Natural Language Answer
```

## Features

- 🤖 **AI-Powered SQL Generation**: Uses Claude 3.5 Sonnet to convert natural language to SQL
- 🗄️ **PostgreSQL Integration**: Real database with sample e-commerce data
- 📊 **Rich Context**: Automatically includes database schema in prompts
- 💬 **Natural Language Answers**: Results are explained in plain English
- 🎨 **Interactive UI**: Streamlit-based web interface

## Sample Database

The POC includes a sample e-commerce database with:
- **Customers**: 8 customers from different countries
- **Products**: 10 products across various categories
- **Orders**: 9 orders with different statuses
- **Order Items**: Line items linking orders to products

## Prerequisites

1. **PostgreSQL** installed and running on `localhost:5432`
   - Default username: `postgres`
   - Default password: `postgres`
   
2. **Python 3.8+**

3. **Anthropic API Key** (already in `.env`)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up the database:
```bash
python database_setup.py
```

This will:
- Create a database named `sql_rag_poc`
- Create tables (customers, products, orders, order_items)
- Populate them with sample data

## Usage

### Option 1: Streamlit UI (Recommended)

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Option 2: Python Script

```bash
python sql_rag.py
```

This will run some test queries and show the results.

### Option 3: Python API

```python
from sql_rag import SQLRAGEngine

rag = SQLRAGEngine()

# Ask a question
result = rag.query("How many customers do we have?")

print(f"SQL: {result['sql']}")
print(f"Results: {result['results']}")

# Get natural language answer
answer = rag.explain_results(
    "How many customers do we have?",
    result['sql'],
    result['results']
)
print(f"Answer: {answer}")
```

## Example Questions

- How many customers do we have?
- What are the top 5 most expensive products?
- Show me all orders from customers in the USA
- What's the total revenue from completed orders?
- Which customer has spent the most money?
- What products are in the Electronics category?
- Show me orders placed in October 2024
- What's the average order value?
- Which products have low stock (less than 50 units)?

## Configuration

Edit database connection settings in `sql_rag.py`:

```python
self.db_config = {
    "host": "localhost",
    "database": "sql_rag_poc",
    "user": "postgres",
    "password": "postgres",
    "port": 5432
}
```

## How It Works

1. **Schema Context**: The system reads your database schema and includes it in the prompt
2. **SQL Generation**: Claude 3.5 uses the schema to generate accurate SQL queries
3. **Query Execution**: The generated SQL is executed against PostgreSQL
4. **Result Interpretation**: Results are sent back to Claude for a natural language explanation

## Security Notes

⚠️ This is a **POC/Demo only**. For production use:
- Add SQL injection protection
- Implement query validation and whitelisting
- Add user authentication
- Set up proper database access controls
- Use read-only database users
- Add query cost limits
- Sanitize all inputs

## Technology Stack

- **LLM**: Claude 3.5 Sonnet (Anthropic)
- **Database**: PostgreSQL
- **Backend**: Python 3.8+
- **UI**: Streamlit
- **Libraries**: anthropic, psycopg2, pandas, python-dotenv

## License

MIT

## Troubleshooting

### PostgreSQL Connection Error
- Make sure PostgreSQL is running: `pg_ctl status` or `brew services list`
- Check credentials match your PostgreSQL setup
- Verify port 5432 is available

### API Key Error
- Make sure your `.env` file contains `ANTHROPIC_API_KEY`
- Verify the API key is valid

### Module Not Found
- Run `pip install -r requirements.txt`
- Make sure you're using the correct Python environment
