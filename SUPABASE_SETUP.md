# Supabase Setup Guide for JobRite

This guide will help you set up Supabase as the backend for your JobRite Django application.

## Prerequisites

1. A Supabase account (sign up at [supabase.com](https://supabase.com))
2. Python environment with the required packages installed

## Step 1: Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - Name: `jobrite`
   - Database Password: Choose a strong password (save this!)
   - Region: Choose the closest to your users
5. Click "Create new project"
6. Wait for the project to be created (this takes a few minutes)

## Step 2: Get Your Project Credentials

Once your project is ready:

1. Go to Settings → API
2. Copy the following values:
   - **Project URL** (something like `https://xxxxx.supabase.co`)
   - **anon public key** (starts with `eyJ...`)
   - **service_role secret key** (starts with `eyJ...`)

## Step 3: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and replace the placeholder values:
   ```env
   # Replace with your actual Supabase project URL
   SUPABASE_URL=https://your-project-ref.supabase.co
   
   # Replace with your anon public key
   SUPABASE_KEY=your_supabase_anon_key_here
   
   # Replace with your service role key
   SUPABASE_SERVICE_KEY=your_supabase_service_role_key_here
   
   # Replace with your database connection string
   # Format: postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   DATABASE_URL=postgresql://postgres:your_password@db.your-project-ref.supabase.co:5432/postgres
   ```

   To get the DATABASE_URL:
   - Go to Settings → Database in your Supabase dashboard
   - Copy the connection string under "Connection string"
   - Replace `[YOUR-PASSWORD]` with the database password you set when creating the project

## Step 4: Create Database Tables

1. Generate the SQL commands:
   ```bash
   python manage.py setup_supabase --create-tables
   ```

2. Copy the generated SQL commands
3. Go to your Supabase dashboard → SQL Editor
4. Paste and run each SQL command one by one

## Step 5: Set Up Row Level Security (RLS) Policies

1. Generate the RLS policy SQL:
   ```bash
   python manage.py setup_supabase --create-policies
   ```

2. Copy the generated SQL commands
3. Go to your Supabase dashboard → SQL Editor
4. Paste and run each policy set one by one

## Step 6: Test the Connection

1. Run Django migrations (this will use your Supabase database):
   ```bash
   python manage.py migrate
   ```

2. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

3. Start the development server:
   ```bash
   python manage.py runserver
   ```

4. Visit `http://localhost:8000/admin` and log in to verify everything works

## Step 7: Enable Authentication (Optional)

If you want to use Supabase Auth instead of Django's built-in authentication:

1. Go to Authentication → Settings in your Supabase dashboard
2. Configure your site URL: `http://localhost:8000`
3. Add any additional redirect URLs you need
4. Configure email templates if desired

## Using Supabase in Your Code

### Basic Database Operations

```python
from jobrite_project.supabase_utils import supabase_data

# Create a record
job_data = {
    'title': 'Software Developer',
    'company': 'Tech Corp',
    'location': 'Remote'
}
job = supabase_data.create_record('jobs', job_data)

# Get records
jobs = supabase_data.get_records('jobs', {'is_active': True})

# Update a record
updated_job = supabase_data.update_record('jobs', job_id, {'title': 'Senior Software Developer'})

# Delete a record
success = supabase_data.delete_record('jobs', job_id)
```

### Authentication Operations

```python
from jobrite_project.supabase_utils import supabase_auth

# Sign up a user
response = supabase_auth.sign_up_user('user@example.com', 'password123')

# Sign in a user
response = supabase_auth.sign_in_user('user@example.com', 'password123')

# Get current user
user = supabase_auth.get_current_user()

# Sign out
supabase_auth.sign_out_user()
```

## Troubleshooting

### Common Issues

1. **Connection refused**: Check your DATABASE_URL format and credentials
2. **Permission denied**: Ensure RLS policies are set up correctly
3. **Table doesn't exist**: Make sure you ran all the table creation SQL commands

### Checking Your Setup

1. Verify environment variables are loaded:
   ```bash
   python manage.py shell
   >>> import os
   >>> print(os.environ.get('SUPABASE_URL'))
   ```

2. Test Supabase connection:
   ```bash
   python manage.py shell
   >>> from jobrite_project.supabase_client import supabase_client
   >>> client = supabase_client()
   >>> print("Connection successful!")
   ```

## Production Considerations

1. **Environment Variables**: Use proper environment variable management in production
2. **SSL**: Ensure `CSRF_COOKIE_SECURE` and `SESSION_COOKIE_SECURE` are `True` in production
3. **Allowed Hosts**: Update `ALLOWED_HOSTS` with your production domain
4. **Database Connection Pooling**: Consider using connection pooling for better performance
5. **Backup**: Set up regular database backups in Supabase dashboard

## Next Steps

- Set up real-time subscriptions for live updates
- Configure file storage using Supabase Storage
- Set up email authentication flows
- Implement advanced RLS policies for multi-tenant scenarios
