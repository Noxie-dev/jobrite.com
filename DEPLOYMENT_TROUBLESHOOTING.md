# 🚨 JobRite Deployment Troubleshooting Guide

## Fixed Issues (2025-08-15)

### ✅ Static Files Not Loading (500 Error)

**Problem:** Deployed site showing 500 errors with CSS/JS files not loading
**Root Cause:** Missing WhiteNoise middleware and improper static file configuration
**Solution Applied:**

1. **Added WhiteNoise Middleware** to `settings.py`:
   ```python
   MIDDLEWARE = [
       "django.middleware.security.SecurityMiddleware",
       "whitenoise.middleware.WhiteNoiseMiddleware",  # Added this
       "django.contrib.sessions.middleware.SessionMiddleware",
       # ... rest of middleware
   ]
   ```

2. **Updated Static Files Configuration**:
   ```python
   STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
   WHITENOISE_USE_FINDERS = True
   WHITENOISE_AUTOREFRESH = DEBUG
   ```

3. **Fixed Vercel Configuration** (`vercel.json`):
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "jobrite_project/wsgi.py",
         "use": "@vercel/python",
         "config": { 
           "maxLambdaSize": "15mb", 
           "runtime": "python3.12"
         }
       },
       {
         "src": "staticfiles/**",
         "use": "@vercel/static"
       }
     ],
     "routes": [
       {
         "src": "/static/(.*)",
         "dest": "/staticfiles/$1"
       }
     ]
   }
   ```

4. **Added Critical CSS Fallback** in `base.html` for when external CSS fails to load

### ✅ Console ReferenceError

**Problem:** JavaScript errors in browser console
**Root Cause:** Tailwind CSS variables not defined when external CSS fails
**Solution:** Added inline critical CSS with all necessary variables and basic styling

## Current Deployment Status

✅ **Fixed Issues:**
- Static file serving with WhiteNoise
- Vercel configuration corrected
- Critical CSS fallback added
- Python runtime updated to 3.12

✅ **Verified Working:**
- Local development server
- Static files collection
- CSS/JS loading
- Basic functionality

## Deployment Steps

### 1. Push Latest Changes
```bash
git push origin main
```

### 2. Redeploy on Vercel
- Go to your Vercel dashboard
- Find your JobRite project
- Click "Redeploy" or trigger a new deployment
- Check deployment logs for any errors

### 3. Set Environment Variables
Make sure these are set in your Vercel dashboard:

```env
DEBUG=False
SECRET_KEY=your_production_secret_key
SUPABASE_URL=https://wmefqsnpmhbpuqybhusu.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
ALLOWED_HOSTS=your-domain.vercel.app
```

## Troubleshooting Commands

### Check Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput --clear

# Verify static files exist
ls -la staticfiles/css/
```

### Test Locally
```bash
# Test with production-like settings
DEBUG=False python manage.py runserver
```

### Check Deployment Logs
- In Vercel dashboard, click on your deployment
- Check "Functions" tab for any Python errors
- Look at build logs for static file issues

## Common Issues & Solutions

### Issue: 500 Error on Homepage
**Likely Cause:** Database connection or missing static files
**Solution:**
1. Check environment variables are set correctly
2. Verify static files are being served
3. Check server logs for specific error

### Issue: CSS Not Loading
**Likely Cause:** Static file configuration
**Solution:**
1. Verify `collectstatic` completed successfully
2. Check WhiteNoise is in middleware
3. Confirm static file paths in templates

### Issue: Database Errors
**Likely Cause:** Missing or incorrect database configuration
**Solution:**
1. Verify Supabase credentials
2. Check if migrations need to be run
3. Test database connection independently

## Emergency Rollback

If deployment fails completely:

1. **Revert to last working commit:**
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Or redeploy previous version on Vercel dashboard**

## Contact & Support

- **GitHub Issues:** Create an issue in your repository
- **Vercel Support:** Check Vercel documentation or support
- **Django Debug:** Enable debug mode temporarily to see full error

## Monitoring

After successful deployment, monitor:
- Homepage loads without errors
- Static files (CSS/JS) load correctly  
- User registration/login works
- Job search functionality works
- MoneyRite tools are accessible

---

**Last Updated:** August 15, 2025
**Status:** ✅ Issues Fixed, Ready for Deployment
