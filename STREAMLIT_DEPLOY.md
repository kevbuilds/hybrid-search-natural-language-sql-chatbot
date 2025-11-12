# 🚀 Streamlit Cloud Deployment Guide

## Prerequisites

1. ✅ GitHub account
2. ✅ Your code pushed to GitHub
3. ✅ Neon PostgreSQL database setup
4. ✅ Anthropic API key

## Step-by-Step Deployment

### 1. Push Your Code to GitHub

```bash
# Make sure you're in your project directory
cd /Users/kevin/Documents/GitHub/natural-language-sql-llm-chatbot

# Add all files
git add .

# Commit
git commit -m "Add password protection for Streamlit Cloud deployment"

# Push to GitHub
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in the form:
   - **Repository**: `kevbuilds/hybrid-search-natural-language-sql-chatbot`
   - **Branch**: `main`
   - **Main file path**: `app_hybrid.py`
   - **App URL** (optional): Choose a custom URL like `sql-rag-demo`

### 3. Configure Secrets (IMPORTANT! 🔐)

After creating the app, it will fail to start. That's expected! You need to add secrets:

1. In your app dashboard, click **⚙️ Settings** (top right)
2. Click **"Secrets"** in the left menu
3. Copy the values from your local `.env` file and paste in this format:

```toml
# 🔐 App Password - Use a secure password for production!
APP_PASSWORD = "your-password-from-env-file"

# 🤖 Anthropic API Key - Copy from your .env file
ANTHROPIC_API_KEY = "your-anthropic-key-from-env-file"

# 🗄️ Neon Database Connection - Copy from your .env file
NEON_DATABASE_URL = "your-neon-url-from-env-file"
```

**📋 Where to find these values:**
- Open your local `.env` file
- Copy the values for `APP_PASSWORD`, `ANTHROPIC_API_KEY`, and `NEON_DATABASE_URL`
- Paste them into Streamlit Cloud secrets (without quotes)

4. Click **"Save"**
5. The app will automatically restart with the secrets

### 4. Test Your Deployment

1. Wait for the app to restart (usually 1-2 minutes)
2. Visit your app URL (e.g., `https://sql-rag-demo.streamlit.app`)
3. You should see the password prompt
4. Enter your password (the one you set in `APP_PASSWORD`)
5. Test with a query like "What's our total revenue?"

## 🔐 Security Notes

### Password Protection

- **Default password**: `demo123` (for local testing only!)
- **For production**: Change `APP_PASSWORD` in Streamlit secrets to something secure
- **Share with your boss**: Send them the password separately (not in email, use Slack/Teams)

### What's Protected

- ✅ The password is stored in Streamlit secrets (not in code)
- ✅ Users must enter password before accessing the app
- ✅ Password is NOT stored in browser (session only)
- ✅ Database credentials are hidden in secrets
- ✅ API keys are hidden in secrets

### What's NOT Protected

- ⚠️ This is basic password protection for demos
- ⚠️ Not suitable for sensitive production data
- ⚠️ For enterprise: Use Streamlit's SSO or OAuth

## 📊 Monitoring Your App

### View Logs

1. Go to your app on Streamlit Cloud
2. Click **"Manage app"** (bottom right)
3. Click **"Logs"** to see real-time output
4. Check for errors during startup

### Common Issues

**Issue**: "ModuleNotFoundError"
- **Fix**: Make sure `requirements.txt` includes all dependencies

**Issue**: "Connection refused" or database errors
- **Fix**: Check your `NEON_DATABASE_URL` in secrets is correct
- **Fix**: Verify Neon database is accessible (not paused)

**Issue**: App is slow to start
- **Fix**: Normal! Embedding model loads on first run (~30 seconds)
- **Fix**: After first load, it's cached and fast

## 🎯 Demo Tips for Your Boss

### Preparation

1. **Test queries beforehand**:
   - "What's our total revenue?"
   - "Who are the top 5 customers by spending?"
   - "Which products are low on stock?"
   - "Show me recent orders from the UK"

2. **Show the hybrid search**:
   - Point out the "💡 Relevant Knowledge Retrieved" section
   - Explain how it finds relevant context automatically

3. **Highlight the benefits**:
   - ✅ No SQL knowledge needed
   - ✅ Understands business terminology
   - ✅ Applies business rules automatically
   - ✅ Works with complex queries (JOINs, aggregations)

### During the Demo

1. **Start with simple queries**: "How many customers do we have?"
2. **Build up to complex**: "What's the average order value by country?"
3. **Show the SQL**: Expand the "🔍 Generated SQL" section
4. **Explain the knowledge**: Show relevant knowledge that was used
5. **Try synonyms**: Ask same question different ways

### Questions They Might Ask

**Q**: "Is this secure?"
- **A**: "Yes, password protected and uses encrypted database connection. For production, we can add enterprise SSO."

**Q**: "Can it handle our real data?"
- **A**: "Yes! Just point it to your database and add business rules to the knowledge base."

**Q**: "How accurate is it?"
- **A**: "It uses Claude Sonnet 4 (state-of-the-art) plus our custom knowledge base. You can verify the SQL before executing."

**Q**: "What if it generates wrong SQL?"
- **A**: "We can add more business rules and query patterns to guide it. The hybrid search learns from examples."

## 🔄 Updating Your App

After deployment, to push updates:

```bash
# Make changes to your code
# Then commit and push
git add .
git commit -m "Your update message"
git push origin main

# Streamlit Cloud auto-deploys changes!
# No need to restart manually
```

## 📞 Support

- **Streamlit Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **Status Page**: https://streamlit.statuspage.io/
- **Community Forum**: https://discuss.streamlit.io/

## 🎉 You're Ready!

Your app is now deployed and password-protected. Share the URL and password with your boss for tomorrow's demo!

**Next Steps**:
1. Push code to GitHub
2. Deploy on Streamlit Cloud
3. Add secrets (password, API key, database URL)
4. Test the deployment
5. Prepare your demo queries
6. Share URL + password with your boss

Good luck with your demo! 🚀
