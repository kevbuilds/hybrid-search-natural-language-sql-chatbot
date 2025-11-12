# 🗄️ Hybrid SQL RAG - Natural Language Database Chatbot

A production-ready SQL RAG (Retrieval Augmented Generation) system that combines **semantic search with embeddings** and **Claude Sonnet 4** to enable natural language database queries. Built with Streamlit, ChromaDB, and Neon PostgreSQL.

## ✨ What Makes This Special?

**Hybrid Search Architecture:**
- 🧠 **Vector Embeddings**: Understands synonyms and intent (e.g., "revenue" = "sales" = "income")
- 📚 **Knowledge Base**: Pre-loaded with business rules, query patterns, and best practices
- 🔍 **Semantic Search**: Automatically finds relevant context using ChromaDB
- 🤖 **Claude Sonnet 4**: State-of-the-art SQL generation with enriched context
- 🔐 **Password Protected**: Secure authentication for demos and production

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Neon PostgreSQL account (free tier available)
- Anthropic API key

### Installation

1. **Clone and install dependencies:**
```bash
git clone https://github.com/kevbuilds/hybrid-search-natural-language-sql-chatbot.git
cd hybrid-search-natural-language-sql-chatbot
pip install -r requirements.txt
```

2. **Configure environment variables:**
Create a `.env` file:
```bash
ANTHROPIC_API_KEY=your-anthropic-api-key
NEON_DATABASE_URL=your-neon-database-url
APP_PASSWORD=your-secure-password
```

3. **Set up database:**
```bash
python setup_neon.py
```

4. **Run the app:**
```bash
streamlit run app_hybrid.py
```

Access at **http://localhost:8501** and login with your password!

## 🌐 Deploy to Streamlit Cloud

See **[STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md)** for complete deployment instructions.

**Quick steps:**
1. Push code to GitHub
2. Deploy on [share.streamlit.io](https://share.streamlit.io)
3. Add secrets (password, API key, database URL)
4. Share URL + password with your team

## 🏗️ Architecture

```
Natural Language Question
         ↓
┌─────────────────────────────┐
│  Semantic Search (ChromaDB) │ → Finds relevant knowledge
└─────────────────────────────┘
         ↓
┌─────────────────────────────┐
│   Hybrid Context Builder    │ → Schema + Knowledge + Question
└─────────────────────────────┘
         ↓
┌─────────────────────────────┐
│   Claude Sonnet 4 (LLM)    │ → Generates SQL with rich context
└─────────────────────────────┘
         ↓
┌─────────────────────────────┐
│   Neon PostgreSQL (Cloud)   │ → Executes query
└─────────────────────────────┘
         ↓
    Natural Language Answer
```

## 🎯 Features

### Core Capabilities
- ✅ **Natural Language to SQL**: Ask questions in plain English
- ✅ **Semantic Understanding**: Recognizes synonyms and business terms
- ✅ **Business Rules**: Automatically applies domain-specific logic
- ✅ **Complex Queries**: Handles JOINs, GROUP BY, aggregations, subqueries
- ✅ **Context-Aware**: Uses relevant examples and patterns
- ✅ **Explainable**: Shows SQL generated and knowledge used

### Enhanced RAG
- 📊 **Vector Search**: ChromaDB with all-MiniLM-L6-v2 embeddings
- 📚 **Knowledge Base**: Extensible system for rules, patterns, descriptions
- 🔄 **Hybrid Retrieval**: Combines schema + semantic search
- 🎓 **Learning System**: Add examples to improve accuracy

### Security & Production
- 🔐 **Password Authentication**: Secure access control
- 🔒 **Cloud Database**: Encrypted Neon PostgreSQL connection
- 🚀 **Streamlit Cloud Ready**: One-click deployment
- ⚡ **Fast**: Embedding model runs locally (no API calls)

## 📊 Sample Database

E-commerce database with realistic data:
- **Customers** (8 records): Customer profiles with countries
- **Products** (10 records): Electronics, Furniture, Office Supplies
- **Orders** (9 records): Orders with statuses (completed, shipped, processing)
- **Order Items** (15 records): Line items linking orders to products

## 💬 Example Questions

**Basic Queries:**
- "How many customers do we have?"
- "Show me all products in the Electronics category"
- "What's the total revenue?"

**Advanced Queries:**
- "Who are the top 5 customers by spending?"
- "What's the average order value by country?"
- "Which products are frequently ordered together?"
- "Show me monthly revenue trends"

**Business Intelligence:**
- "What's our customer retention rate?"
- "Which products are running low on stock?"
- "What's the most popular product category?"

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | Claude Sonnet 4 (Anthropic) |
| **Embeddings** | all-MiniLM-L6-v2 (sentence-transformers) |
| **Vector DB** | ChromaDB (in-memory) |
| **Database** | Neon PostgreSQL (cloud) |
| **Backend** | Python 3.11 |
| **UI** | Streamlit 1.39.0 |
| **Libraries** | anthropic, chromadb, psycopg2, pandas |

## 📚 Customization

### Adding Business Rules

Edit `knowledge_base.py` to add your own knowledge:

```python
{
    "id": "custom_revenue_rule",
    "content": "When calculating revenue, exclude refunded orders and only count completed transactions.",
    "metadata": {
        "type": "business_rule",
        "keywords": "revenue, sales, income, refund"
    }
}
```

See detailed instructions in `knowledge_base.py` comments.

### Persistence

Enable ChromaDB persistence in `sql_rag_hybrid.py`:

```python
# Change this line:
is_persistent=False  # In-memory

# To:
is_persistent=True  # Persistent to disk
persist_directory="./chroma_db"
```

## 🔒 Security Notes

**Current Setup (Demo/POC):**
- ✅ Password authentication
- ✅ Encrypted database connection (SSL)
- ✅ API keys in environment variables
- ✅ No credentials in code

**For Production, Add:**
- 🔐 Enterprise SSO/OAuth
- 🛡️ SQL injection protection
- 📝 Query validation and whitelisting
- 👥 Role-based access control
- 📊 Query cost limits and monitoring
- 🔍 Audit logging

## 📁 Project Structure

```
├── app_hybrid.py              # Main Streamlit UI (with auth)
├── sql_rag_hybrid.py          # Hybrid RAG engine
├── knowledge_base.py          # Embeddings knowledge base
├── setup_neon.py              # Database setup script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (local)
├── .streamlit/
│   └── secrets.toml          # Streamlit secrets (template)
├── STREAMLIT_DEPLOY.md       # Deployment guide
└── README.md                 # This file
```

## 🐛 Troubleshooting

**"Authentication Error" with Anthropic:**
- Verify `ANTHROPIC_API_KEY` in `.env` file
- Check API key is valid at console.anthropic.com

**Database Connection Error:**
- Verify `NEON_DATABASE_URL` in `.env` file
- Check Neon database is not paused (free tier auto-pauses)
- Ensure `sslmode=require` in connection string

**"ModuleNotFoundError":**
```bash
pip install -r requirements.txt
```

**Slow Startup:**
- First run loads embedding model (~30 seconds)
- Subsequent runs are faster (model cached)

**Wrong SQL Generated:**
- Add more examples to `knowledge_base.py`
- Be specific in your question
- Check relevant knowledge retrieved (shown in UI)

## 📖 Documentation

- **[STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md)**: Complete deployment guide
- **Code Comments**: Extensive inline documentation
- **knowledge_base.py**: Examples and templates for adding knowledge

## 🤝 Contributing

This is a demo project. Feel free to fork and adapt for your use case!

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **Anthropic** for Claude Sonnet 4
- **Neon** for serverless PostgreSQL
- **Streamlit** for the amazing UI framework
- **ChromaDB** for vector search capabilities

---

**Built by [@kevbuilds](https://github.com/kevbuilds)** | **[Report Issues](https://github.com/kevbuilds/hybrid-search-natural-language-sql-chatbot/issues)**
