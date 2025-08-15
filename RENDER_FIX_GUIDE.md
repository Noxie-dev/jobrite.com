# 🚨 JobRite Render Deployment Fix Guide

## Current Issue: 500 Server Error

Your JobRite app is showing a 500 error on Render. Here's how to fix it:

## 🔧 Immediate Fixes

### 1. Update Your Render Service Settings

In your Render dashboard:

1. **Go to your service** (jobrite-portal)
2. **Settings** → **Environment**
3. **Add/Update these environment variables:**

```
DJANGO_SETTINGS_MODULE=jobrite_project.production_settings
DATABASE_URL=postgresql://postgres:MashavelliIntheArea123@db.wmefqsnpmhbpuqybhusu.supabase.co:5432/postgres
DEBUG=False
SECRET_KEY=(let Render generate this)
SUPABASE_URL=https://wmefqsnpmhbpuqybhusu.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndtZWZxc25wbWhicHVxeWJodXN1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxNjYyMTQsImV4cCI6MjA3MDc0MjIxNH0.V5H-LLnIvVYQ0WvY5ftwWq5ZnFKOkPNt4czcaiuH4WM
```

### 2. Update Build & Start Commands

In Render dashboard → Settings:

- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn jobrite_project.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 2`

### 3. Deploy the Latest Changes

```bash
git add .
git commit -m "Fix Render deployment configuration"
git push origin main
```

## 🔍 Troubleshooting Steps

### Step 1: Check Logs
In Render dashboard → Logs, look for:
- Database connection errors
- Missing environment variables
- Static file issues
- Import errors

### Step 2: Test Database Connection
Your app should connect to Supabase PostgreSQL. Common issues:
- Wrong DATABASE_URL format
- Supabase database not accessible
- SSL connection issues

### Step 3: Verify Static Files
Make sure the build script runs:
- `python manage.py collectstatic --noinput`
- Files should be in `/staticfiles/` directory

## 🚀 Quick Deploy Commands

If you want to redeploy immediately:

```bash
# 1. Commit latest changes
git add .
git commit -m "Production deployment fixes"
git push origin main

# 2. In Render dashboard, click "Manual Deploy"
```

## 🔧 Alternative: Use render.yaml

Your project now has a `render.yaml` file. To use it:

1. **Delete your current service** in Render dashboard
2. **Create new service** → **Import from render.yaml**
3. **Connect your GitHub repo**
4. **Deploy automatically**

## 📊 Health Check

Once deployed, test these URLs:
- `https://your-app.onrender.com/` - Main site
- `https://your-app.onrender.com/health/` - Health check
- `https://your-app.onrender.com/debug/` - Debug info

## 🆘 If Still Failing

1. **Check Render logs** for specific error messages
2. **Run diagnostics locally:**
   ```bash
   python diagnose_deployment.py
   ```
3. **Test database connection** in Supabase dashboard
4. **Verify all environment variables** are set correctly

## 📞 Common Error Solutions

### "Application failed to start"
- Check `DJANGO_SETTINGS_MODULE` is set correctly
- Verify `requirements.txt` has all dependencies

### "Database connection failed"
- Check `DATABASE_URL` format
- Verify Supabase database is running
- Check SSL requirements

### "Static files not found"
- Ensure `collectstatic` runs in build command
- Check `STATIC_ROOT` and `STATIC_URL` settings

Your app should be working after these fixes! 🎉