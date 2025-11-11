# Deployment Guide - Streamlit Cloud

This guide walks you through deploying Ensina AI to Streamlit Cloud.

## Prerequisites

1. **Anthropic API Key**: Get one from https://console.anthropic.com/
2. **GitHub Account**: Your code must be in a GitHub repository
3. **Streamlit Cloud Account**: Sign up at https://share.streamlit.io/

## Step 1: Push Code to GitHub

Your code is already in this repository. Make sure all changes are pushed:

```bash
git push origin main
```

## Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**: https://share.streamlit.io/

2. **Click "New app"**

3. **Configure your app:**
   - **Repository**: Select your GitHub repository (`obronco/ensina-ai`)
   - **Branch**: `claude/ai-math-tutor-setup-011CUxQ7NT6ZwsAn8ZGbkmxE` (or `main` if merged)
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom URL (e.g., `ensina-ai`)

4. **Click "Advanced settings"**

5. **Add Secrets**: Copy and paste this into the Secrets text box:

```toml
# Required: Your Anthropic API Key
ANTHROPIC_API_KEY = "sk-ant-api03-your-actual-key-here"

# Optional: Customize these if needed
APP_NAME = "Ensina AI"
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
DATABASE_PATH = "data/ensina.db"
```

⚠️ **IMPORTANT**: Replace `"sk-ant-api03-your-actual-key-here"` with your actual Anthropic API key!

6. **Click "Deploy"**

Streamlit will:
- Install dependencies from `requirements.txt`
- Start the app
- Give you a public URL (e.g., https://ensina-ai.streamlit.app)

## Step 3: Initial Setup

Once deployed, visit your app and:

1. **Go to "Setup" page**
2. **Add a Teacher**:
   - Name: Your name
   - Email: Your email
   - School: (optional)

3. **Add a Student**:
   - Name: Student name
   - Grade Level: 5-12
   - Parent Email: Your email

4. **Test the flow:**
   - Go to "Teacher View" → Create an assignment
   - Go to "Student" → Select the assignment, chat with AI
   - Click "New Session" to submit
   - Go to "Teacher View" → Review Submissions

## Important Notes

### Database Persistence

⚠️ **Streamlit Cloud uses ephemeral storage** - the database will be reset when:
- The app restarts
- You redeploy
- After periods of inactivity

For production use, you would need to:
- Use a persistent database (PostgreSQL, MySQL)
- Store the SQLite file in a mounted volume
- Or export/backup data regularly

For testing/demo purposes, the ephemeral database is fine.

### API Costs

Each interaction with students calls the Claude API:
- Cost per message: ~$0.003-0.015 (depends on message length)
- Monitor usage at https://console.anthropic.com/

### Security

- Never commit `.env` files with real API keys
- Always use Streamlit Secrets for sensitive data
- The app currently has no authentication - anyone with the URL can access it

## Updating the Deployment

To update your deployed app:

1. Make changes to your code
2. Commit and push to GitHub:
```bash
git add .
git commit -m "Update description"
git push
```

3. Streamlit Cloud will automatically redeploy (usually within 1-2 minutes)

## Troubleshooting

### App won't start
- Check logs in Streamlit Cloud dashboard
- Verify `requirements.txt` has all dependencies
- Ensure `ANTHROPIC_API_KEY` is set in Secrets

### "API key not found" error
- Go to app settings → Secrets
- Verify `ANTHROPIC_API_KEY` is set correctly
- Make sure there are no extra quotes or spaces

### Database errors
- The app creates `data/ensina.db` automatically
- If errors persist, try restarting the app

### API rate limits
- Anthropic has rate limits on API keys
- Monitor usage in console.anthropic.com
- Consider implementing rate limiting for students

## Monitoring

**Check API usage:**
- https://console.anthropic.com/settings/usage

**Check app logs:**
- Streamlit Cloud dashboard → Your app → "Manage app" → "Logs"

**Check app status:**
- Green = running
- Red = crashed (check logs)
- Yellow = deploying

## Next Steps for Production

For a production deployment, consider:

1. **Authentication**: Add login for students/teachers/parents
2. **Persistent Database**: Migrate to PostgreSQL or MySQL
3. **Rate Limiting**: Prevent abuse of API
4. **Analytics**: Track usage, costs, student engagement
5. **Backups**: Regular database exports
6. **Custom Domain**: Point your own domain to Streamlit app
7. **Error Monitoring**: Sentry or similar service

## Cost Estimation

**Anthropic API:**
- $3 per million input tokens (~$0.003 per message)
- $15 per million output tokens (~$0.015 per response)
- Average session (10 messages): ~$0.10-0.20

**Streamlit Cloud:**
- Free tier: 1 app, limited resources
- Community tier: $20/month, more resources
- Enterprise: Custom pricing

**Example:**
- 100 students
- 2 sessions/week
- 10 messages/session
- = 2000 sessions/week = ~$200-400/week in API costs

## Support

If you encounter issues:
- Streamlit docs: https://docs.streamlit.io/
- Anthropic docs: https://docs.anthropic.com/
- GitHub issues: https://github.com/obronco/ensina-ai/issues
