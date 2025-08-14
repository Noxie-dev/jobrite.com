#!/bin/bash

echo "🚀 DEPLOYING JOBRITE TO PRODUCTION"
echo "=================================="

# Commit latest changes
echo "📝 Committing latest changes..."
git add .
git commit -m "Final deployment: JobRite with Supabase integration ready for production"
git push origin main

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "🎯 NEXT STEPS - Choose your deployment platform:"
echo ""
echo "1️⃣  RENDER.COM (Recommended - Free):"
echo "   → Go to: https://render.com"
echo "   → Connect your GitHub repo"
echo "   → Use the settings from DEPLOY_NOW.md"
echo ""
echo "2️⃣  HEROKU:"
echo "   → Install Heroku CLI"
echo "   → Run: heroku create jobrite-portal"
echo "   → Follow commands in DEPLOY_NOW.md"
echo ""
echo "3️⃣  RAILWAY:"
echo "   → Go to: https://railway.app"
echo "   → Deploy from GitHub"
echo "   → Add environment variables"
echo ""
echo "🎉 YOUR APP IS READY TO GO LIVE!"
echo "📋 See DEPLOY_NOW.md for detailed instructions"