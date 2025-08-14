"""
Utility functions for Supabase operations in JobRite project.
"""
from typing import Dict, List, Optional, Any
from django.contrib.auth.models import User
from .supabase_client import supabase_client, supabase_admin_client


class SupabaseAuthManager:
    """Manager for Supabase authentication operations."""
    
    def __init__(self):
        self.client = supabase_client()
        self.admin_client = supabase_admin_client()
    
    def sign_up_user(self, email: str, password: str, user_metadata: Optional[Dict] = None) -> Dict:
        """
        Sign up a new user with Supabase Auth.
        
        Args:
            email: User's email address
            password: User's password
            user_metadata: Optional metadata to store with the user
            
        Returns:
            Dict containing user data and session info
        """
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })
            return response
        except Exception as e:
            raise Exception(f"Failed to sign up user: {str(e)}")
    
    def sign_in_user(self, email: str, password: str) -> Dict:
        """
        Sign in a user with Supabase Auth.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Dict containing user data and session info
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return response
        except Exception as e:
            raise Exception(f"Failed to sign in user: {str(e)}")
    
    def sign_out_user(self) -> None:
        """Sign out the current user."""
        try:
            self.client.auth.sign_out()
        except Exception as e:
            raise Exception(f"Failed to sign out user: {str(e)}")
    
    def get_current_user(self) -> Optional[Dict]:
        """Get the currently authenticated user."""
        try:
            user = self.client.auth.get_user()
            return user.user if user else None
        except Exception as e:
            return None
    
    def reset_password(self, email: str) -> Dict:
        """
        Send password reset email to user.
        
        Args:
            email: User's email address
            
        Returns:
            Dict containing response data
        """
        try:
            response = self.client.auth.reset_password_email(email)
            return response
        except Exception as e:
            raise Exception(f"Failed to send reset password email: {str(e)}")


class SupabaseDataManager:
    """Manager for Supabase database operations."""
    
    def __init__(self):
        self.client = supabase_client()
        self.admin_client = supabase_admin_client()
    
    def create_record(self, table: str, data: Dict, use_admin: bool = False) -> Dict:
        """
        Create a new record in the specified table.
        
        Args:
            table: Table name
            data: Data to insert
            use_admin: Whether to use admin client (bypasses RLS)
            
        Returns:
            Dict containing the created record
        """
        client = self.admin_client if use_admin else self.client
        try:
            response = client.table(table).insert(data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            raise Exception(f"Failed to create record in {table}: {str(e)}")
    
    def get_records(self, table: str, filters: Optional[Dict] = None, 
                   use_admin: bool = False) -> List[Dict]:
        """
        Get records from the specified table.
        
        Args:
            table: Table name
            filters: Optional filters to apply
            use_admin: Whether to use admin client (bypasses RLS)
            
        Returns:
            List of records
        """
        client = self.admin_client if use_admin else self.client
        try:
            query = client.table(table).select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return response.data or []
        except Exception as e:
            raise Exception(f"Failed to get records from {table}: {str(e)}")
    
    def update_record(self, table: str, record_id: str, data: Dict, 
                     use_admin: bool = False) -> Dict:
        """
        Update a record in the specified table.
        
        Args:
            table: Table name
            record_id: ID of the record to update
            data: Data to update
            use_admin: Whether to use admin client (bypasses RLS)
            
        Returns:
            Dict containing the updated record
        """
        client = self.admin_client if use_admin else self.client
        try:
            response = client.table(table).update(data).eq('id', record_id).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            raise Exception(f"Failed to update record in {table}: {str(e)}")
    
    def delete_record(self, table: str, record_id: str, 
                     use_admin: bool = False) -> bool:
        """
        Delete a record from the specified table.
        
        Args:
            table: Table name
            record_id: ID of the record to delete
            use_admin: Whether to use admin client (bypasses RLS)
            
        Returns:
            Boolean indicating success
        """
        client = self.admin_client if use_admin else self.client
        try:
            response = client.table(table).delete().eq('id', record_id).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Failed to delete record from {table}: {str(e)}")


# Global instances
supabase_auth = SupabaseAuthManager()
supabase_data = SupabaseDataManager()
