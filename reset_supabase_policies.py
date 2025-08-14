#!/usr/bin/env python3
"""
Reset Supabase Policies Script
This script generates SQL to clean up existing policies and recreate them properly.
"""

def generate_cleanup_sql():
    """Generate SQL to drop existing policies and recreate them."""
    
    print("="*60)
    print("SUPABASE POLICY CLEANUP & RESET")
    print("="*60)
    
    print("\n1. Go to your Supabase dashboard SQL Editor:")
    print("   https://supabase.com/dashboard/project/wmefqsnpmhbpuqybhusu")
    
    print("\n2. First, run this cleanup SQL to remove existing policies:")
    print("\n--- CLEANUP EXISTING POLICIES ---")
    
    cleanup_sql = """
-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view all profiles" ON public.profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;

DROP POLICY IF EXISTS "Anyone can view active jobs" ON public.jobs;
DROP POLICY IF EXISTS "Authenticated users can create jobs" ON public.jobs;
DROP POLICY IF EXISTS "Users can update own jobs" ON public.jobs;

DROP POLICY IF EXISTS "Users can view own applications" ON public.job_applications;
DROP POLICY IF EXISTS "Job posters can view applications for their jobs" ON public.job_applications;
DROP POLICY IF EXISTS "Users can create applications" ON public.job_applications;

DROP POLICY IF EXISTS "Anyone can view published posts" ON public.blog_posts;
DROP POLICY IF EXISTS "Authors can view own posts" ON public.blog_posts;
DROP POLICY IF EXISTS "Authors can create posts" ON public.blog_posts;
DROP POLICY IF EXISTS "Authors can update own posts" ON public.blog_posts;
"""
    
    print(cleanup_sql)
    
    print("\n3. After cleanup, run the new policies:")
    print("\n--- RECREATE POLICIES ---")
    
    # Updated policies with better naming to avoid conflicts
    policies = [
        """
-- Enable RLS on all tables (safe to run multiple times)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.blog_posts ENABLE ROW LEVEL SECURITY;
""",
        """
-- Profiles policies
CREATE POLICY "profiles_select_policy" ON public.profiles
    FOR SELECT USING (true);

CREATE POLICY "profiles_update_policy" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "profiles_insert_policy" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);
""",
        """
-- Jobs policies
CREATE POLICY "jobs_select_policy" ON public.jobs
    FOR SELECT USING (is_active = true);

CREATE POLICY "jobs_insert_policy" ON public.jobs
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "jobs_update_policy" ON public.jobs
    FOR UPDATE USING (auth.uid() = posted_by);
""",
        """
-- Job applications policies
CREATE POLICY "applications_select_own_policy" ON public.job_applications
    FOR SELECT USING (auth.uid() = applicant_id);

CREATE POLICY "applications_select_employer_policy" ON public.job_applications
    FOR SELECT USING (
        auth.uid() IN (
            SELECT posted_by FROM public.jobs WHERE id = job_id
        )
    );

CREATE POLICY "applications_insert_policy" ON public.job_applications
    FOR INSERT WITH CHECK (auth.uid() = applicant_id);
""",
        """
-- Blog posts policies
CREATE POLICY "blog_select_published_policy" ON public.blog_posts
    FOR SELECT USING (published = true);

CREATE POLICY "blog_select_own_policy" ON public.blog_posts
    FOR SELECT USING (auth.uid() = author_id);

CREATE POLICY "blog_insert_policy" ON public.blog_posts
    FOR INSERT WITH CHECK (auth.uid() = author_id);

CREATE POLICY "blog_update_policy" ON public.blog_posts
    FOR UPDATE USING (auth.uid() = author_id);
"""
    ]
    
    for i, policy in enumerate(policies, 1):
        print(f"\n--- Policy Set {i} ---")
        print(policy)
    
    print("\n" + "="*60)
    print("ALTERNATIVE: Quick Fix")
    print("="*60)
    print("\nIf you just want to continue without recreating policies,")
    print("you can ignore the policy errors since they already exist.")
    print("The important thing is that your tables are created.")
    
    print("\nTo test if everything is working:")
    print("1. Uncomment DATABASE_URL in your .env file")
    print("2. Run: python manage.py shell")
    print("3. Test: from django.db import connection; connection.cursor().execute('SELECT 1')")

if __name__ == "__main__":
    generate_cleanup_sql()