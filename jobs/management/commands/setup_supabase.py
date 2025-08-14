"""
Django management command to set up Supabase tables and policies.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Set up Supabase tables and Row Level Security policies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-tables',
            action='store_true',
            help='Create tables in Supabase',
        )
        parser.add_argument(
            '--create-policies',
            action='store_true',
            help='Create RLS policies in Supabase',
        )

    def handle(self, *args, **options):
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            self.stdout.write(
                self.style.ERROR(
                    'SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables'
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS('Supabase configuration found!')
        )
        
        if options['create_tables']:
            self.create_tables()
        
        if options['create_policies']:
            self.create_policies()
        
        if not options['create_tables'] and not options['create_policies']:
            self.show_help()

    def create_tables(self):
        """Create tables in Supabase."""
        self.stdout.write('Creating Supabase tables...')
        
        # SQL to create tables that mirror your Django models
        sql_commands = [
            """
            -- Enable UUID extension
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            """,
            """
            -- Create profiles table (extends auth.users)
            CREATE TABLE IF NOT EXISTS public.profiles (
                id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                phone_number TEXT,
                location TEXT,
                bio TEXT,
                skills TEXT[],
                experience_level TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            """
            -- Create jobs table
            CREATE TABLE IF NOT EXISTS public.jobs (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                description TEXT,
                requirements TEXT,
                salary_min INTEGER,
                salary_max INTEGER,
                job_type TEXT,
                experience_level TEXT,
                posted_by UUID REFERENCES auth.users(id) ON DELETE CASCADE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_active BOOLEAN DEFAULT TRUE
            );
            """,
            """
            -- Create job applications table
            CREATE TABLE IF NOT EXISTS public.job_applications (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                job_id UUID REFERENCES public.jobs(id) ON DELETE CASCADE,
                applicant_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
                cover_letter TEXT,
                resume_url TEXT,
                status TEXT DEFAULT 'pending',
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(job_id, applicant_id)
            );
            """,
            """
            -- Create blog posts table
            CREATE TABLE IF NOT EXISTS public.blog_posts (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                content TEXT,
                excerpt TEXT,
                author_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
                published BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
        ]
        
        self.stdout.write('Tables creation SQL generated. Please run these in your Supabase SQL editor:')
        for i, sql in enumerate(sql_commands, 1):
            self.stdout.write(f'\n--- Command {i} ---')
            self.stdout.write(sql)

    def create_policies(self):
        """Create RLS policies in Supabase."""
        self.stdout.write('Creating RLS policies...')
        
        policies = [
            """
            -- Enable RLS on all tables
            ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
            ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
            ALTER TABLE public.job_applications ENABLE ROW LEVEL SECURITY;
            ALTER TABLE public.blog_posts ENABLE ROW LEVEL SECURITY;
            """,
            """
            -- Profiles policies
            CREATE POLICY "Users can view all profiles" ON public.profiles
                FOR SELECT USING (true);
            
            CREATE POLICY "Users can update own profile" ON public.profiles
                FOR UPDATE USING (auth.uid() = id);
            
            CREATE POLICY "Users can insert own profile" ON public.profiles
                FOR INSERT WITH CHECK (auth.uid() = id);
            """,
            """
            -- Jobs policies
            CREATE POLICY "Anyone can view active jobs" ON public.jobs
                FOR SELECT USING (is_active = true);
            
            CREATE POLICY "Authenticated users can create jobs" ON public.jobs
                FOR INSERT WITH CHECK (auth.role() = 'authenticated');
            
            CREATE POLICY "Users can update own jobs" ON public.jobs
                FOR UPDATE USING (auth.uid() = posted_by);
            """,
            """
            -- Job applications policies
            CREATE POLICY "Users can view own applications" ON public.job_applications
                FOR SELECT USING (auth.uid() = applicant_id);
            
            CREATE POLICY "Job posters can view applications for their jobs" ON public.job_applications
                FOR SELECT USING (
                    auth.uid() IN (
                        SELECT posted_by FROM public.jobs WHERE id = job_id
                    )
                );
            
            CREATE POLICY "Users can create applications" ON public.job_applications
                FOR INSERT WITH CHECK (auth.uid() = applicant_id);
            """,
            """
            -- Blog posts policies
            CREATE POLICY "Anyone can view published posts" ON public.blog_posts
                FOR SELECT USING (published = true);
            
            CREATE POLICY "Authors can view own posts" ON public.blog_posts
                FOR SELECT USING (auth.uid() = author_id);
            
            CREATE POLICY "Authors can create posts" ON public.blog_posts
                FOR INSERT WITH CHECK (auth.uid() = author_id);
            
            CREATE POLICY "Authors can update own posts" ON public.blog_posts
                FOR UPDATE USING (auth.uid() = author_id);
            """
        ]
        
        self.stdout.write('RLS policies SQL generated. Please run these in your Supabase SQL editor:')
        for i, policy in enumerate(policies, 1):
            self.stdout.write(f'\n--- Policy Set {i} ---')
            self.stdout.write(policy)

    def show_help(self):
        """Show help information."""
        self.stdout.write(
            self.style.WARNING(
                'Use --create-tables to generate table creation SQL\n'
                'Use --create-policies to generate RLS policy SQL\n'
                'Example: python manage.py setup_supabase --create-tables --create-policies'
            )
        )
