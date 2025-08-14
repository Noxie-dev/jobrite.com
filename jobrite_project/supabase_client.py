"""
Supabase client configuration for JobRite project.
"""
import os
from supabase import create_client, Client
from django.conf import settings

def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance.
    
    Returns:
        Client: Configured Supabase client
    """
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
        )
    
    return create_client(url, key)

def get_supabase_admin_client() -> Client:
    """
    Create and return a Supabase client instance with service role key.
    Use this for admin operations that bypass RLS policies.
    
    Returns:
        Client: Configured Supabase admin client
    """
    url = os.environ.get('SUPABASE_URL')
    service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not url or not service_key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables"
        )
    
    return create_client(url, service_key)

# Global client instances (lazy initialization)
_supabase_client = None
_supabase_admin_client = None

def supabase_client() -> Client:
    """Get the global Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = get_supabase_client()
    return _supabase_client

def supabase_admin_client() -> Client:
    """Get the global Supabase admin client instance."""
    global _supabase_admin_client
    if _supabase_admin_client is None:
        _supabase_admin_client = get_supabase_admin_client()
    return _supabase_admin_client
