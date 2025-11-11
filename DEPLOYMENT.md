# 🚀 Deployment Guide: Supabase + Streamlit Cloud

## Step 1: Set Up Supabase (FREE PostgreSQL Database)

### 1.1 Create Supabase Account
1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up with GitHub (recommended)

### 1.2 Create New Project
1. Click "New Project"
2. Name: `sql-rag-demo` (or any name)
3. Database Password: **Save this!** You'll need it
4. Region: Choose closest to you
5. Click "Create new project" (takes ~2 minutes)

### 1.3 Set Up Database Tables
1. In your Supabase dashboard, go to **SQL Editor**
2. Click "New query"
3. Copy and paste ALL contents from `setup_supabase.sql`
4. Click "Run" to execute
5. ✅ Verify tables created under **Table Editor**

### 1.4 Get Database Credentials
1. Go to **Project Settings** (gear icon) → **Database**
2. Scroll to **Connection String** → **URI**
3. Copy the connection details:
   - **Host:** `db.xxxxxxxxxxxxx.supabase.co`
   - **Database:** `postgres`
   - **User:** `postgres`
   - **Password:** (your database password)
   - **Port:** `5432`

---

## Step 2: Deploy to Streamlit Cloud (FREE Hosting)

### 2.1 Push Code to GitHub
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 2.2 Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click **"New app"**
4. Select:
   - **Repository:** `your-username/natural-language-sql-llm-chatbot`
   - **Branch:** `main`
   - **Main file path:** `app_cloud.py`
5. Click **"Advanced settings"**

### 2.3 Configure Secrets
In the **Secrets** section, paste this (replace with your actual values):

```toml
ANTHROPIC_API_KEY = "sk-ant-api03-..."

DB_HOST = "db.xxxxxxxxxxxxx.supabase.co"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "your-supabase-password"
DB_PORT = "5432"
```

### 2.4 Deploy!
1. Click **"Deploy!"**
2. Wait 3-5 minutes for first deployment
3. ✅ Your app will be live at: `https://your-app-name.streamlit.app`

---

## Step 3: Share with Your Boss! 🎉

You'll get a public URL like:
```
https://sql-rag-demo.streamlit.app
```

### What to Show:
1. ✅ Ask: "What's our total revenue?"
2. ✅ Show the semantic search results (expander)
3. ✅ Show the generated SQL
4. ✅ Show the natural language answer
5. ✅ Ask: "Show me top spenders" to demonstrate pattern matching
6. ✅ Ask: "Which products are low in stock?" to show business logic

---

## 💰 Total Cost: $0

- ✅ Supabase Free Tier: 500MB database (plenty for demo)
- ✅ Streamlit Cloud Free Tier: Public apps
- ✅ You only pay for Anthropic API usage (~$0.01-0.05 per query)

---

## 🔧 Troubleshooting

### Database Connection Error
- Verify Supabase credentials in Streamlit secrets
- Check if Supabase project is active (not paused)
- Test connection in Supabase SQL Editor first

### App Not Loading
- Check Streamlit logs (click "Manage app" → "Logs")
- Verify all secrets are set correctly
- Ensure `requirements.txt` includes all dependencies

### Slow First Load
- First load takes ~30 seconds (downloading embedding model)
- Subsequent loads are cached and much faster

---

## 📊 Usage Limits (Free Tier)

### Supabase
- 500 MB database storage
- Unlimited API requests
- 2 GB bandwidth/month
- **Perfect for demo!**

### Streamlit Cloud
- 1 GB RAM per app
- Unlimited public apps
- Community support
- **Perfect for showing off!**

---

## 🎯 Next Steps After Demo

If your boss loves it:
1. **Upgrade Supabase:** $25/month for 8GB + backups
2. **Private Streamlit:** $20/month for password protection
3. **Custom Domain:** Point your own domain
4. **More Data:** Scale the database with real production data

---

## 📝 Quick Reference

**Your App URL:** (will be provided after deployment)
**Supabase Dashboard:** https://app.supabase.com
**Streamlit Cloud:** https://share.streamlit.io

**Need Help?**
- Supabase Docs: https://supabase.com/docs
- Streamlit Docs: https://docs.streamlit.io

---

Good luck with your demo! 🚀
