#!/usr/bin/env python3
"""
Firebase deployment script for JobRite Django application
"""
import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting Firebase deployment for JobRite...")
    
    # Check if Firebase CLI is installed
    if not run_command("firebase --version", "Checking Firebase CLI"):
        print("❌ Firebase CLI not found. Install it with: npm install -g firebase-tools")
        sys.exit(1)
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("❌ Failed to collect static files")
        sys.exit(1)
    
    # Copy Django project to functions directory
    print("\n🔄 Copying Django project to functions directory...")
    functions_dir = Path("functions")
    
    # Create symlinks or copy necessary Django files
    django_files = [
        "jobrite_project",
        "jobs", 
        "users",
        "blog",
        "moneyrite",
        "templates",
        "manage.py"
    ]
    
    for file_path in django_files:
        src = Path(file_path)
        dst = functions_dir / file_path
        
        if src.exists():
            if dst.exists():
                if dst.is_symlink():
                    dst.unlink()
                elif dst.is_dir():
                    import shutil
                    shutil.rmtree(dst)
                else:
                    dst.unlink()
            
            # Create symlink
            try:
                dst.symlink_to(src.resolve())
                print(f"✅ Linked {file_path}")
            except OSError:
                # Fallback to copying if symlinks don't work
                import shutil
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                print(f"✅ Copied {file_path}")
    
    # Deploy to Firebase
    if not run_command("firebase deploy", "Deploying to Firebase"):
        print("❌ Firebase deployment failed")
        sys.exit(1)
    
    print("\n🎉 Deployment completed successfully!")
    print("🌐 Your app should be available at: https://jobrite-ea97a.web.app")

if __name__ == "__main__":
    main()