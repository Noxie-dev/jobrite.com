#!/usr/bin/env python3
"""
JobRite Deployment Verification Script
Checks if all components are working correctly after deployment
"""

import os
import sys
import subprocess
import requests
from urllib.parse import urljoin

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status="info"):
    """Print colored status message"""
    color_map = {
        "success": Colors.GREEN,
        "error": Colors.RED,
        "warning": Colors.YELLOW,
        "info": Colors.BLUE
    }
    color = color_map.get(status, Colors.BLUE)
    print(f"{color}{'✅' if status == 'success' else '❌' if status == 'error' else '⚠️' if status == 'warning' else 'ℹ️'} {message}{Colors.ENDC}")

def check_django_setup():
    """Check if Django is properly configured"""
    print_status("Checking Django setup...", "info")
    
    try:
        # Check if manage.py exists
        if not os.path.exists('manage.py'):
            print_status("manage.py not found - are you in the project directory?", "error")
            return False
        
        # Run Django system check
        result = subprocess.run(['python', 'manage.py', 'check', '--deploy'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_status("Django system check passed", "success")
            return True
        else:
            print_status(f"Django system check failed: {result.stderr}", "error")
            return False
            
    except Exception as e:
        print_status(f"Error checking Django setup: {e}", "error")
        return False

def check_static_files():
    """Check if static files are properly collected"""
    print_status("Checking static files...", "info")
    
    try:
        # Check if staticfiles directory exists
        if not os.path.exists('staticfiles'):
            print_status("staticfiles directory not found", "error")
            return False
        
        # Check for key CSS files
        required_files = [
            'staticfiles/css/tailwind.css',
            'staticfiles/css/main.css',
            'staticfiles/js/main.js'
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                print_status(f"Found {os.path.basename(file_path)}", "success")
            else:
                print_status(f"Missing {os.path.basename(file_path)}", "error")
                return False
        
        return True
        
    except Exception as e:
        print_status(f"Error checking static files: {e}", "error")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    print_status("Checking environment variables...", "info")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print_status(f"Missing environment variables: {', '.join(missing_vars)}", "warning")
        print_status("Set these in your deployment platform (Vercel, Heroku, etc.)", "info")
        return False
    else:
        print_status("All required environment variables are set", "success")
        return True

def check_deployment_url(url):
    """Check if the deployed site is accessible"""
    if not url:
        print_status("No deployment URL provided, skipping URL check", "warning")
        return True
    
    print_status(f"Checking deployment URL: {url}", "info")
    
    try:
        # Check homepage
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print_status("Homepage is accessible", "success")
            
            # Check if CSS is loading
            if 'text/html' in response.headers.get('content-type', ''):
                content = response.text
                if 'JobRite.com' in content:
                    print_status("Homepage content looks correct", "success")
                else:
                    print_status("Homepage content may be incorrect", "warning")
                    
                # Check for CSS links
                if '/static/css/' in content:
                    print_status("Static CSS links found in HTML", "success")
                else:
                    print_status("No static CSS links found - may be an issue", "warning")
            
            return True
        else:
            print_status(f"Homepage returned status code: {response.status_code}", "error")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status(f"Error accessing deployment URL: {e}", "error")
        return False

def main():
    """Main verification function"""
    print(f"{Colors.BOLD}{Colors.BLUE}🚀 JobRite Deployment Verification{Colors.ENDC}")
    print("=" * 50)
    
    # Get deployment URL from command line argument
    deployment_url = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run all checks
    checks = [
        ("Django Setup", check_django_setup),
        ("Static Files", check_static_files),
        ("Environment Variables", check_environment_variables),
        ("Deployment URL", lambda: check_deployment_url(deployment_url))
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n{Colors.BOLD}--- {check_name} ---{Colors.ENDC}")
        result = check_func()
        results.append((check_name, result))
    
    # Summary
    print(f"\n{Colors.BOLD}📋 SUMMARY{Colors.ENDC}")
    print("=" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print_status("🎉 All checks passed! Your deployment should be working correctly.", "success")
        return 0
    else:
        print_status(f"⚠️ {total - passed} checks failed. Please address the issues above.", "warning")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
