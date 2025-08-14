# 🆓 Free Deployment Guide for JobRite

Since Railway requires a paid account, here are the **completely free** alternatives for deploying your school project!

## 🎯 Recommended: Render + Supabase (100% Free)

### Why This Combo?
- ✅ **Render Free Tier**: 750 hours/month (enough for demos)
- ✅ **Supabase Free Tier**: 500MB database, 50MB storage
- ✅ **No Credit Card Required**
- ✅ **Perfect for School Projects**

## 🚀 Step-by-Step Deployment

### Step 1: Set Up Supabase (5 minutes)

1. Go to [supabase.com](https://supabase.com) and create account
2. Create new project: `jobrite-school-project`
3. Wait for setup (2-3 minutes)
4. Go to Settings → API and copy:
   - Project URL
   - anon public key
   - service_role key
5. Go to Settings → Database and copy connection string

### Step 2: Set Up Render (5 minutes)

1. Go to [render.com](https://render.com) and create account
2. Connect your GitHub account
3. Push your code to GitHub (if not already there)

### Step 3: Deploy to Render

1. In Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name**: `jobrite-school-project`
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn jobrite_project.wsgi:application`

### Step 4: Set Environment Variables

In Render, go to Environment and add:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
DJANGO_SETTINGS_MODULE=jobrite_project.production_settings
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
DATABASE_URL=postgresql://postgres:password@db.project.supabase.co:5432/postgres
DJANGO_USE_HTTPS=true
```

### Step 5: Set Up Database Tables

1. Run the setup command locally:
   ```bash
   python manage.py setup_supabase --create-tables --create-policies
   ```

2. Copy the generated SQL
3. Go to Supabase → SQL Editor
4. Run the SQL commands

### Step 6: Deploy!

1. Click "Deploy" in Render
2. Wait 5-10 minutes for build
3. Your app will be live at `https://your-app-name.onrender.com`

## 🔄 Alternative Free Options

### Option 2: Vercel + Supabase
- Great for modern web apps
- Excellent performance
- Easy GitHub integration

### Option 3: Netlify + Supabase  
- Perfect for static sites
- Great for frontend-heavy apps

### Option 4: PythonAnywhere + Supabase
- Traditional Django hosting
- Good for learning deployment

## 💡 Pro Tips for School Projects

### 1. **Keep It Simple**
- Use Render + Supabase combo
- Don't overcomplicate the setup

### 2. **Document Everything**
- Keep deployment notes
- Screenshot the working app
- Save environment variables securely

### 3. **Test Locally First**
- Make sure everything works with Supabase locally
- Test with `DEBUG=False` before deploying

### 4. **Backup Your Work**
- Export Supabase data regularly
- Keep your code in GitHub
- Document your database schema

## 🛠️ Troubleshooting

### Common Issues:

**Build Fails on Render:**
- Check `build.sh` is executable: `chmod +x build.sh`
- Verify all requirements are in `requirements.txt`

**Database Connection Error:**
- Double-check DATABASE_URL format
- Ensure Supabase project is active
- Verify environment variables are set

**Static Files Not Loading:**
- Run `python manage.py collectstatic` locally first
- Check WhiteNoise is configured correctly

**403 Forbidden:**
- Add your Render domain to `ALLOWED_HOSTS`
- Check `DJANGO_USE_HTTPS=true` is set

## 📊 Free Tier Limits

### Render Free Tier:
- 750 hours/month (31 days = 744 hours)
- 512MB RAM
- Sleeps after 15 minutes of inactivity
- **Perfect for school demos!**

### Supabase Free Tier:
- 500MB database storage
- 50MB file storage
- 50,000 monthly active users
- **More than enough for school projects!**

## 🎓 For Your School Presentation

### Demo Script:
1. Show the live website
2. Demonstrate user registration/login
3. Show job posting/application features
4. Highlight the MoneyRite salary calculator
5. Show admin panel (if applicable)

### What to Mention:
- "Deployed using modern cloud infrastructure"
- "Uses PostgreSQL database with Supabase"
- "Implements proper security practices"
- "Scalable architecture ready for production"

## 🔗 Quick Links

- **Your App**: `https://your-app-name.onrender.com`
- **Supabase Dashboard**: `https://app.supabase.com`
- **Render Dashboard**: `https://dashboard.render.com`
- **GitHub Repo**: Your repository URL

## 📝 Submission Checklist

- [ ] App is live and accessible
- [ ] All features work correctly
- [ ] Database is properly set up
- [ ] Environment variables are secure
- [ ] Documentation is complete
- [ ] Screenshots/demo video ready

---

**Need Help?** The setup files are already created in your project:
- `render.yaml` - Render configuration
- `build.sh` - Build script
- `production_settings.py` - Production Django settings
- `SUPABASE_SETUP.md` - Detailed Supabase guide

Your project is ready for free deployment! 🚀
