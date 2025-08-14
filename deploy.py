#!/usr/bin/env python
"""
Simple deployment script for JobRite Django application
"""
import os
import sys
import subprocess
import django

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobrite_project.production_settings')
    django.setup()

def collect_static():
    """Collect static files"""
    print("📦 Collecting static files...")
    result = subprocess.run([
        sys.executable, 'manage.py', 'collectstatic', '--noinput', '--clear'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Static files collected successfully")
    else:
        print(f"❌ Error collecting static files: {result.stderr}")
        return False
    return True

def migrate_database():
    """Run database migrations"""
    print("🗄️ Running database migrations...")
    result = subprocess.run([
        sys.executable, 'manage.py', 'migrate', '--noinput'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Database migrations completed successfully")
    else:
        print(f"❌ Error running migrations: {result.stderr}")
        return False
    return True

def create_superuser():
    """Create superuser if needed"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            print("👤 Creating superuser...")
            username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
            email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@jobrite.com')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
            
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"✅ Superuser '{username}' created successfully")
        else:
            print("👤 Superuser already exists")
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return False
    return True

def populate_sample_data():
    """Populate sample data if needed"""
    try:
        print("📊 Populating sample data...")
        result = subprocess.run([
            sys.executable, 'manage.py', 'populate_sample_data'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Sample data populated successfully")
        else:
            print(f"⚠️ Sample data population: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Sample data population warning: {e}")

def main():
    """Main deployment function"""
    print("🚀 Starting JobRite deployment...")
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Setup Django
    setup_django()
    
    # Run deployment steps
    steps = [
        ("Collecting static files", collect_static),
        ("Running migrations", migrate_database),
        ("Creating superuser", create_superuser),
        ("Populating sample data", populate_sample_data),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        success = step_func()
        if not success and step_func != populate_sample_data:
            print(f"💥 Deployment failed at: {step_name}")
            sys.exit(1)
    
    print("\n🎉 JobRite deployment completed successfully!")
    print("\n📋 Deployment Summary:")
    print("   • Static files collected and ready")
    print("   • Database migrations applied")
    print("   • Admin user configured")
    print("   • Sample data available")
    print("\n🌐 Your JobRite application is ready to serve users!")

if __name__ == '__main__':
    main()
