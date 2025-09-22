"""
Supabase client configuration for medical records
"""
import os
import ssl
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from the parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

class SupabaseClient:
    """Handles all Supabase database operations for medical records"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')  # Service role key
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        try:            
            # Create client with anon key for regular operations
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            
            # Create service client for admin operations (bypasses RLS)
            if self.supabase_service_key:
                self.service_client: Client = create_client(self.supabase_url, self.supabase_service_key)
            else:
                print("Warning: SUPABASE_SERVICE_KEY not found. Some operations may fail due to RLS.")
                self.service_client = self.client
                
        except Exception as ssl_error:
            print(f"Error creating Supabase client: {ssl_error}")
            raise
    
    def create_health_record(self, record_data):
        """Create a new encrypted health record"""
        try:
            response = self.client.table('health_records').insert(record_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating health record: {e}")
            return None
    
    def get_health_record(self, record_id):
        """Retrieve a health record by ID"""
        try:
            response = self.client.table('health_records').select('*').eq('id', record_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error retrieving health record: {e}")
            return None
    
    def get_health_records_by_patient(self, patient_id):
        """Retrieve all health records for a patient"""
        try:
            response = self.client.table('health_records').select('*').eq('patient_id', patient_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error retrieving patient health records: {e}")
            return []
    
    def update_health_record(self, record_id, update_data):
        """Update an existing health record"""
        try:
            response = self.client.table('health_records').update(update_data).eq('id', record_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating health record: {e}")
            return None
    
    def delete_health_record(self, record_id):
        """Delete a health record"""
        try:
            response = self.client.table('health_records').delete().eq('id', record_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error deleting health record: {e}")
            return None
    
    def create_blockchain_transaction(self, transaction_data):
        """Create a blockchain transaction record"""
        try:
            response = self.client.table('blockchain_transactions').insert(transaction_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating blockchain transaction: {e}")
            return None
    
    def get_blockchain_transactions_by_record(self, health_record_id):
        """Get all blockchain transactions for a health record"""
        try:
            response = self.client.table('blockchain_transactions').select('*').eq('health_record_id', health_record_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error retrieving blockchain transactions: {e}")
            return []
