from supabase import create_client, Client
import os
from typing import Optional

class SupabaseClient:
    _instance: Optional[Client] = None

    def __init__(self):
        """Initialize Supabase client with environment variables"""
        if not SupabaseClient._instance:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_KEY')  # Changed to SUPABASE_SERVICE_KEY
            
            if not supabase_url or not supabase_key:
                raise ValueError(
                    "Missing Supabase credentials. Please ensure SUPABASE_URL and "
                    "SUPABASE_SERVICE_KEY are set in your environment variables."
                )
            
            SupabaseClient._instance = create_client(supabase_url, supabase_key)
    
    @property
    def client(self) -> Client:
        """Get the Supabase client instance"""
        if not SupabaseClient._instance:
            raise RuntimeError("Supabase client not initialized")
        return SupabaseClient._instance

    def get_bookings(self):
        """Fetch all active bookings"""
        return self.client.table('bookings').select('*').eq('active', True).execute()

    def update_price_history(self, booking_id: str, price_data: dict):
        """Insert a new price history record"""
        return self.client.table('price_histories').insert(price_data).execute()

# Helper function to get a configured client
def get_supabase_client() -> SupabaseClient:
    try:
        return SupabaseClient()
    except Exception as e:
        print(f"Error initializing Supabase client: {str(e)}")
        raise