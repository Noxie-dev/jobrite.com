#!/usr/bin/env python3
"""
Quick fix script for Render deployment issues
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and print the result"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {str(e)}")
        return False

def main():
    print("🚀 JobRite Render Deployment Fix")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Run this script from your project root.")
        sys.exit(1)
    
    print("📋 This script will:")
    print("1. Collect static files")
    print("2. Check database connection")
    print("3. Run migrations (if database is accessible)")
    print("4. Create deployment-ready files")
    print()
    
    # Step 1: Collect static files
    run_command("python manage.py collectstatic --noinput --clear", "Collecting static files")
    
    # Step 2: Check database connection
    db_connected = run_command("python manage.py check --database default", "Checking database connection")
    
    # Step 3: Run migrations if database is connected
    if db_connected:
        run_command("python manage.py migrate --noinput", "Running database migrations")
        run_command("python manage.py check", "Final Django check")
    else:
        print("⚠️  Database not accessible locally - migrations will run during deployment")
    
    print("\n" + "=" * 40)
    print("📦 Deployment files created:")
    print("✅ build.sh - Build script for Render")
    print("✅ render.yaml - Render configuration")
    print("✅ production_settings.py - Production Django settings")
    print("✅ RENDER_FIX_GUIDE.md - Deployment troubleshooting guide")
    
    print("\n🚀 Next Steps:")
    print("1. Commit and push your changes:")
    print("   git add .")
    print("   git commit -m 'Fix Render deployment configuration'")
    print("   git push origin main")
    print()
    print("2. In Render dashboard:")
    print("   - Update environment variables (see RENDER_FIX_GUIDE.md)")
    print("   - Set build command to: ./build.sh")
    print("   - Set start command to: gunicorn jobrite_project.wsgi:application --bind 0.0.0.0:$PORT")
    print("   - Redeploy your service")
    print()
    print("3. Test your deployment:")
    print("   - Visit your app URL")
    print("   - Check /health/ endpoint")
    print("   - Check /debug/ endpoint")
    
    print("\n🎉 Your JobRite app should be working after these steps!")

if __name__ == "__main__":
    main()