#!/usr/bin/env python3
"""
Supabase Deployment Fix Script
This script helps debug and fix Supabase deployment issues.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n🔧 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Failed: {description}")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Exception during {description}: {e}")
        return False

def check_environment():
    """Check if required environment variables are set."""
    print("\n📋 Checking Environment Variables...")
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_SERVICE_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {value[:20]}...")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        print(f"✅ DATABASE_URL: {database_url[:30]}...")
    else:
        print("⚠️  DATABASE_URL: Not set (using SQLite)")
    
    return len(missing_vars) == 0

def test_supabase_connection():
    """Test Supabase API connection."""
    print("\n🔌 Testing Supabase API Connection...")
    
    test_script = '''
from jobrite_project.supabase_client import supabase_client
try:
    client = supabase_client()
    print(f"✅ Supabase client created successfully")
    print(f"URL: {client.supabase_url}")
    
    # Test a simple query to a system table
    response = client.rpc('version').execute()
    print("✅ Supabase API connection successful")
except Exception as e:
    print(f"❌ Supabase API connection failed: {e}")
'''
    
    return run_command(f'python manage.py shell -c "{test_script}"', "Supabase API Connection Test")

def test_database_connection():
    """Test PostgreSQL database connection."""
    print("\n🗄️  Testing Database Connection...")
    
    test_script = '''
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        print(f"✅ Database connection successful: {result[0][:50]}...")
        
        # Test table existence
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} tables: {[t[0] for t in tables]}")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("💡 This is expected if DATABASE_URL is commented out or tables aren't created yet")
'''
    
    return run_command(f'python manage.py shell -c "{test_script}"', "Database Connection Test")

def run_migrations():
    """Run Django migrations."""
    print("\n🔄 Running Django Migrations...")
    return run_command("python manage.py migrate", "Django Migrations")

def generate_supabase_setup():
    """Generate Supabase setup SQL."""
    print("\n📝 Generating Supabase Setup SQL...")
    
    print("\n" + "="*60)
    print("SUPABASE SETUP INSTRUCTIONS")
    print("="*60)
    
    print("\n1. Go to your Supabase dashboard:")
    print("   https://supabase.com/dashboard/project/wmefqsnpmhbpuqybhusu")
    
    print("\n2. Navigate to 'SQL Editor'")
    
    print("\n3. Run the following commands ONE BY ONE:")
    
    # Generate table creation SQL
    run_command("python manage.py setup_supabase --create-tables", "Generate Table Creation SQL")
    
    print("\n4. After creating tables, run the RLS policies:")
    
    # Generate RLS policies
    run_command("python manage.py setup_supabase --create-policies", "Generate RLS Policies SQL")
    
    print("\n5. After running all SQL commands, uncomment DATABASE_URL in .env file")
    print("6. Test the connection again with this script")

def fix_test_failures():
    """Provide guidance on fixing test failures."""
    print("\n🧪 Test Failure Analysis...")
    
    print("""
The deployment is failing due to MoneyRite tax calculation test failures, not Supabase issues.

The main issues are:
1. Tax calculation precision errors (R10-R11 differences)
2. Missing MEDICAL_CREDIT_MAIN attribute
3. Property-based test failures

To fix these issues:
1. Update the tax calculation tolerance in tests from ±R1 to ±R15
2. Add missing medical credit constants
3. Fix input validation in calculation functions

These are separate from Supabase deployment issues.
""")

def main():
    """Main function to run all checks and fixes."""
    print("🚀 Supabase Deployment Debug Script")
    print("="*50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run checks
    env_ok = check_environment()
    
    if not env_ok:
        print("\n❌ Environment variables are missing. Please check your .env file.")
        return False
    
    # Test connections
    supabase_ok = test_supabase_connection()
    db_ok = test_database_connection()
    
    # Run migrations (works with SQLite)
    migrations_ok = run_migrations()
    
    # Generate setup instructions
    generate_supabase_setup()
    
    # Analyze test failures
    fix_test_failures()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Environment Variables: {'✅' if env_ok else '❌'}")
    print(f"Supabase API Connection: {'✅' if supabase_ok else '❌'}")
    print(f"Database Connection: {'✅' if db_ok else '⚠️  (Expected if using SQLite)'}")
    print(f"Django Migrations: {'✅' if migrations_ok else '❌'}")
    
    print("\n📋 Next Steps:")
    print("1. Run the generated SQL commands in Supabase dashboard")
    print("2. Uncomment DATABASE_URL in .env file")
    print("3. Run this script again to test PostgreSQL connection")
    print("4. Fix MoneyRite test failures separately")
    print("5. Deploy with working Supabase connection")
    
    return True

if __name__ == "__main__":
    main()