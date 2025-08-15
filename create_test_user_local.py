#!/usr/bin/env python
"""
Create a test user for local testing (uses SQLite)
"""
import os
import django

# Setup Django with SQLite (ignore Supabase for local testing)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobrite_project.settings')
os.environ['DATABASE_URL'] = ''  # Force SQLite usage
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

def create_test_user():
    """Create a test user with profile"""
    
    # Check if user already exists
    if User.objects.filter(username='testuser').exists():
        print("Test user already exists. Deleting and recreating...")
        User.objects.filter(username='testuser').delete()
    
    # Create user
    user = User.objects.create_user(
        username='testuser',
        email='test@jobrite.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    
    # Create profile
    profile = UserProfile.objects.create(
        user=user,
        bio='I am a test user for the JobRite platform.',
        location='Johannesburg, South Africa',
        skills='Customer Service, Communication, Problem Solving',
        experience_level='mid',
        onboarding_completed=True,
        preferred_job_categories=['customer-care', 'sales'],
        preferred_locations=['johannesburg', 'remote']
    )
    
    print(f"✅ Created test user: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Password: testpass123")
    print(f"   Profile ID: {profile.id}")
    print(f"   Onboarding completed: {profile.onboarding_completed}")
    print(f"\n🚀 You can now login at: http://localhost:8000/users/login/")
    print(f"   Username: testuser")
    print(f"   Password: testpass123")
    
    return user, profile

def create_admin_user():
    """Create admin user for local testing"""
    if User.objects.filter(username='admin').exists():
        print("Admin user already exists.")
        return
    
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@jobrite.com',
        password='admin123'
    )
    print(f"✅ Created admin user: {admin.username}")
    print(f"   Email: {admin.email}")
    print(f"   Password: admin123")
    print(f"   Admin panel: http://localhost:8000/admin/")

if __name__ == '__main__':
    print("🚀 Creating test users for local development...")
    create_admin_user()
    create_test_user()
    print("\n🎉 Test users created successfully!")