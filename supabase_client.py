# src/lib/supabase/client.py

"""
Supabase client configuration and helper functions for interacting with the database.
Provides functions for fetching price histories and holding prices.
"""

import os
from typing import List, Dict, Optional
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not url or not key:
        raise ValueError("Missing Supabase configuration. Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables.")
    
    return create_client(url, key)

def get_holding_price_histories(booking_id: str) -> List[Dict]:
    """
    Fetch holding price histories for a booking from Supabase
    
    Args:
        booking_id: The ID of the booking to fetch histories for
        
    Returns:
        List of holding price history records sorted by effective_from date
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table('holding_price_histories') \
            .select('*') \
            .eq('booking_id', booking_id) \
            .order('effective_from', desc=False) \
            .execute()
            
        return response.data
    except Exception as e:
        print(f"Error fetching holding price histories: {str(e)}")
        return []