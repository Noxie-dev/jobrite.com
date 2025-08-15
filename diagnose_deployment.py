#!/usr/bin/env python3
"""
Deployment diagnostic script for JobRite
Run this to check if your deployment is ready
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobrite_project.settings')
django.setup()

def check_environment():
    """Check environment variables"""
    print("🔍 Checking Environment Variables...")
    
    required_vars = [
        'SECRET_KEY',
        'SUPABASE_URL', 
        'SUPABASE_KEY',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: Set ({'*' * min(len(value), 10)})")
        else:
            print(f"❌ {var}: Missing")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def check_database():
    """Check database connection"""
    print("\n🗄️ Checking Database Connection...")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            print("✅ Database connection: Working")
            return True
    except Exception as e:
        print(f"❌ Database connection: Failed - {str(e)}")
        return False

def check_static_files():
    """Check static files configuration"""
    print("\n📁 Checking Static Files...")
    
    from django.conf import settings
    
    static_root = getattr(settings, 'STATIC_ROOT', None)
    if static_root and Path(static_root).exists():
        file_count = len(list(Path(static_root).rglob('*')))
        print(f"✅ Static files: {file_count} files in {static_root}")
        return True
    else:
        print(f"❌ Static files: STATIC_ROOT not found or empty")
        return False

def check_migrations():
    """Check if migrations are applied"""
    print("\n🔄 Checking Migrations...")
    
    try:
        from django.core.management import execute_from_command_line
        from io import StringIO
        import sys
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            execute_from_command_line(['manage.py', 'showmigrations', '--plan'])
            output = captured_output.getvalue()
            sys.stdout = old_stdout
            
            if '[X]' in output:
                applied_count = output.count('[X]')
                print(f"✅ Migrations: {applied_count} migrations applied")
                return True
            else:
                print("❌ Migrations: No migrations applied")
                return False
        except:
            sys.stdout = old_stdout
            print("❌ Migrations: Could not check migration status")
            return False
            
    except Exception as e:
        print(f"❌ Migrations: Error checking - {str(e)}")
        return False

def check_apps():
    """Check if Django apps are working"""
    print("\n📱 Checking Django Apps...")
    
    try:
        from django.apps import apps
        app_configs = apps.get_app_configs()
        
        expected_apps = ['jobs', 'users', 'blog', 'moneyrite']
        found_apps = [app.name for app in app_configs if app.name in expected_apps]
        
        print(f"✅ Django apps: {len(found_apps)}/{len(expected_apps)} apps loaded")
        for app in found_apps:
            print(f"   - {app}")
        
        return len(found_apps) == len(expected_apps)
        
    except Exception as e:
        print(f"❌ Django apps: Error - {str(e)}")
        return False

def main():
    """Run all diagnostic checks"""
    print("🚀 JobRite Deployment Diagnostics")
    print("=" * 40)
    
    checks = [
        ("Environment Variables", check_environment),
        ("Database Connection", check_database),
        ("Static Files", check_static_files),
        ("Migrations", check_migrations),
        ("Django Apps", check_apps),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}: Unexpected error - {str(e)}")
            results.append((name, False))
    
    print("\n" + "=" * 40)
    print("📊 Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Your deployment should work.")
    else:
        print("⚠️  Some checks failed. Fix these issues before deploying.")
        
        print("\n🔧 Suggested fixes:")
        if not any(result for name, result in results if name == "Environment Variables"):
            print("- Set missing environment variables in your deployment platform")
        if not any(result for name, result in results if name == "Database Connection"):
            print("- Check your DATABASE_URL and Supabase configuration")
        if not any(result for name, result in results if name == "Static Files"):
            print("- Run: python manage.py collectstatic --noinput")
        if not any(result for name, result in results if name == "Migrations"):
            print("- Run: python manage.py migrate")

if __name__ == "__main__":
    main()