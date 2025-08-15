#!/usr/bin/env python3
"""
Temporary workaround for email verification
This script helps you manually verify users while setting up email
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobrite_project.settings')
os.environ['DATABASE_URL'] = ''  # Use SQLite for local testing
django.setup()

from django.contrib.auth.models import User
from users.models import EmailVerification

def list_unverified_users():
    """List all unverified users"""
    print("📋 Unverified Users:")
    print("-" * 40)
    
    unverified_users = User.objects.filter(is_active=False)
    
    if not unverified_users.exists():
        print("✅ No unverified users found!")
        return []
    
    for user in unverified_users:
        try:
            verification = user.email_verification
            print(f"👤 {user.username} ({user.email})")
            print(f"   Created: {user.date_joined.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Token: {verification.token}")
            print(f"   Verification URL: http://localhost:8000/users/verify-email/{verification.token}/")
            print()
        except EmailVerification.DoesNotExist:
            print(f"👤 {user.username} ({user.email}) - No verification record")
            print()
    
    return list(unverified_users)

def verify_user_manually(username_or_email):
    """Manually verify a user"""
    try:
        # Try to find user by username or email
        if '@' in username_or_email:
            user = User.objects.get(email=username_or_email)
        else:
            user = User.objects.get(username=username_or_email)
        
        # Activate the user
        user.is_active = True
        user.save()
        
        # Mark email as verified
        try:
            verification = user.email_verification
            verification.is_verified = True
            verification.verified_at = django.utils.timezone.now()
            verification.save()
        except EmailVerification.DoesNotExist:
            # Create verification record if it doesn't exist
            EmailVerification.objects.create(
                user=user,
                is_verified=True,
                verified_at=django.utils.timezone.now()
            )
        
        print(f"✅ Successfully verified user: {user.username} ({user.email})")
        print(f"   User can now log in at: http://localhost:8000/users/login/")
        return True
        
    except User.DoesNotExist:
        print(f"❌ User not found: {username_or_email}")
        return False
    except Exception as e:
        print(f"❌ Error verifying user: {str(e)}")
        return False

def verify_all_users():
    """Verify all unverified users"""
    unverified_users = User.objects.filter(is_active=False)
    
    if not unverified_users.exists():
        print("✅ No users to verify!")
        return
    
    count = 0
    for user in unverified_users:
        if verify_user_manually(user.username):
            count += 1
    
    print(f"\n🎉 Verified {count} users successfully!")

def main():
    print("📧 JobRite Email Verification Workaround")
    print("=" * 45)
    print("This tool helps you manually verify users while setting up email.")
    print()
    
    while True:
        print("\nOptions:")
        print("1. List unverified users")
        print("2. Verify specific user")
        print("3. Verify all users")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            list_unverified_users()
        
        elif choice == '2':
            username_or_email = input("Enter username or email: ").strip()
            if username_or_email:
                verify_user_manually(username_or_email)
        
        elif choice == '3':
            confirm = input("Verify ALL unverified users? (y/N): ").strip().lower()
            if confirm == 'y':
                verify_all_users()
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()