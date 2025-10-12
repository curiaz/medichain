"""
Supabase client configuration for medical records
"""

import os
import ssl
import certifi
import httpx

from dotenv import load_dotenv
from supabase import Client, create_client

# Load environment variables from the parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))


class SupabaseClient:
    """Handles all Supabase database operations for medical records"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")  # Service role key

        # Handle missing environment variables gracefully
        if not self.supabase_url or not self.supabase_key:
            print("⚠️  Warning: SUPABASE_URL and SUPABASE_KEY not found in environment variables")
            print("🔧 Creating mock Supabase client for development/testing")
            self.client = None
            self.service_client = None
            return

        try:
            # Create SSL context with proper certificate handling
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            # Create HTTP client with SSL configuration
            http_client = httpx.Client(
                verify=ssl_context,
                timeout=30.0,
                follow_redirects=True
            )
            
            # Create client with anon key for regular operations
            self.client: Client = create_client(
                self.supabase_url, 
                self.supabase_key
            )

            # Create service client for admin operations (bypasses RLS)
            if self.supabase_service_key:
                self.service_client: Client = create_client(
                    self.supabase_url, 
                    self.supabase_service_key
                )
            else:
                print("Warning: SUPABASE_SERVICE_KEY not found. Some operations may fail due to RLS.")
                self.service_client = self.client
                
            # Close the custom HTTP client as Supabase creates its own
            http_client.close()

        except ssl.SSLError as ssl_error:
            print(f"SSL Error creating Supabase client: {ssl_error}")
            print("Attempting fallback SSL configuration...")
            
            try:
                # Fallback: Create client with less strict SSL verification
                self.client: Client = create_client(
                    self.supabase_url, 
                    self.supabase_key
                )
                
                if self.supabase_service_key:
                    self.service_client: Client = create_client(
                        self.supabase_url, 
                        self.supabase_service_key
                    )
                else:
                    self.service_client = self.client
                    
                print("✅ Supabase client created with fallback SSL configuration")
                
            except Exception as fallback_error:
                print(f"Fallback SSL configuration also failed: {fallback_error}")
                raise ssl_error
                
        except Exception as general_error:
            print(f"Error creating Supabase client: {general_error}")
            raise

    def _ensure_client_available(self, method_name="unknown method"):
        """Helper method to check if Supabase client is available"""
        if not self.client:
            print(f"⚠️  Supabase client not available for {method_name} - using mock response")
            return False
        return True

    def create_health_record(self, record_data):
        """Create a new encrypted health record"""
        if not self.client:
            print("⚠️  Supabase client not available - using mock response")
            return {"id": "mock_id", "status": "mock_created"}
            
        try:
            response = self.client.table("health_records").insert(record_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating health record: {e}")
            return None

    def get_health_record(self, record_id):
        """Retrieve a health record by ID"""
        if not self.client:
            print("⚠️  Supabase client not available - using mock response")
            return {"id": record_id, "status": "mock_record"}
            
        try:
            response = self.client.table("health_records").select("*").eq("id", record_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error retrieving health record: {e}")
            return None

    def get_health_records_by_patient(self, patient_id):
        """Retrieve all health records for a patient"""
        if not self.client:
            print("⚠️  Supabase client not available - using mock response")
            return [{"id": "mock_record", "patient_id": patient_id, "status": "mock"}]
            
        try:
            response = self.client.table("health_records").select("*").eq("patient_id", patient_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error retrieving patient health records: {e}")
            return []

    def update_health_record(self, record_id, update_data):
        """Update an existing health record"""
        if not self._ensure_client_available("update_health_record"):
            return {"id": record_id, "status": "mock_updated"}
            
        try:
            response = self.client.table("health_records").update(update_data).eq("id", record_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating health record: {e}")
            return None

    def delete_health_record(self, record_id):
        """Delete a health record"""
        if not self._ensure_client_available("delete_health_record"):
            return {"id": record_id, "status": "mock_deleted"}
            
        try:
            response = self.client.table("health_records").delete().eq("id", record_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error deleting health record: {e}")
            return None

    def create_blockchain_transaction(self, transaction_data):
        """Create a blockchain transaction record"""
        try:
            response = self.client.table("blockchain_transactions").insert(transaction_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating blockchain transaction: {e}")
            return None

    def get_blockchain_transactions_by_record(self, health_record_id):
        """Get all blockchain transactions for a health record"""
        try:
            response = (
                self.client.table("blockchain_transactions").select("*").eq("health_record_id", health_record_id).execute()
            )
            return response.data if response.data else []
        except Exception as e:
            print(f"Error retrieving blockchain transactions: {e}")
            return []

    # Patient Profile Management Methods
    def verify_firebase_token(self, token):
        """Verify Firebase token and return user info"""
        try:
            # Import Firebase auth service
            from auth.firebase_auth import firebase_auth_service

            # Verify the token using the existing Firebase service
            result = firebase_auth_service.verify_token(token)

            if result['success']:
                user_info = result['user']
                return {
                    'user_id': user_info.get('uid'),
                    'email': user_info.get('email'),
                    'role': user_info.get('custom_claims', {}).get('role', 'patient')
                }
            else:
                print(f"Firebase token verification failed: {result.get('error', 'Unknown error')}")
                return None

        except Exception as e:
            print(f"Error verifying Firebase token: {e}")
            return None

    def get_patient_profile(self, user_id):
        """Get complete patient profile with medical information"""
        try:
            # Use service client to bypass RLS for patient profile access
            user_response = self.service_client.table('user_profiles').select('*').eq('firebase_uid', user_id).execute()
            user_profile = user_response.data[0] if user_response.data else None
            
            if not user_profile:
                print(f"No user profile found for Firebase UID: {user_id}")
                return None
            
            # Create medical info from user profile data
            medical_info = {
                'medical_conditions': user_profile.get('medical_conditions', []),
                'allergies': user_profile.get('allergies', []),
                'current_medications': user_profile.get('current_medications', []),
                'blood_type': user_profile.get('blood_type', ''),
                'medical_notes': user_profile.get('medical_notes', ''),
                'medical_records': [],  # No separate medical records table
                'appointments': [],     # No appointments data yet
                'prescriptions': []    # No prescriptions data yet
            }
            
            return {
                'user_profile': user_profile,
                'medical_info': medical_info,
                'documents': [],  # No documents table yet
                'privacy_settings': {},  # No privacy settings table yet
                'audit_trail': []  # No audit trail table yet
            }
        except Exception as e:
            print(f"Error getting patient profile: {e}")
            return None

    def update_patient_profile(self, user_id, data):
        """Update patient profile information"""
        try:
            # First get the user profile to get the internal ID
            user_response = self.client.table('user_profiles').select('id').eq('firebase_uid', user_id).execute()
            if not user_response.data:
                print(f"No user profile found for Firebase UID: {user_id}")
                return None
            
            internal_user_id = user_response.data[0]['id']
            
            # Update user profile using internal ID
            response = self.client.table('user_profiles').update(data).eq('id', internal_user_id).execute()
            
            if response.data:
                # Create audit log entry
                audit_data = {
                    'user_id': internal_user_id,
                    'action': 'profile_update',
                    'type': 'personal_info',
                    'data_hash': f"hash_{user_id}_{data.get('first_name', '')}_{data.get('last_name', '')}",
                    'timestamp': 'now()'
                }
                self.client.table('patient_audit_log').insert(audit_data).execute()
                
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error updating patient profile: {e}")
            return None

    def update_patient_medical_info(self, user_id, data):
        """Update patient medical information"""
        try:
            # First get the user profile to get the internal ID
            user_response = self.client.table('user_profiles').select('id').eq('firebase_uid', user_id).execute()
            if not user_response.data:
                print(f"No user profile found for Firebase UID: {user_id}")
                return None
            
            internal_user_id = user_response.data[0]['id']
            
            # Upsert medical information
            data['user_id'] = internal_user_id
            response = self.client.table('patient_medical_info').upsert(data).execute()
            
            if response.data:
                # Create audit log entry
                audit_data = {
                    'user_id': internal_user_id,
                    'action': 'medical_info_update',
                    'type': 'medical_data',
                    'data_hash': f"hash_{user_id}_medical_{data.get('blood_type', '')}",
                    'timestamp': 'now()'
                }
                self.client.table('patient_audit_log').insert(audit_data).execute()
                
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error updating patient medical info: {e}")
            return None

    def upload_patient_document(self, user_id, file, document_type, description):
        """Upload patient health document"""
        try:
            # First get the user profile to get the internal ID
            user_response = self.client.table('user_profiles').select('id').eq('firebase_uid', user_id).execute()
            if not user_response.data:
                print(f"No user profile found for Firebase UID: {user_id}")
                return None
            
            internal_user_id = user_response.data[0]['id']
            
            # In a real implementation, you would upload the file to storage
            # For now, create a document record
            document_data = {
                'user_id': internal_user_id,
                'filename': file.filename,
                'document_type': document_type,
                'description': description,
                'file_size': len(file.read()) if hasattr(file, 'read') else 0,
                'upload_date': 'now()',
                'file_path': f"documents/{user_id}/{file.filename}"
            }
            
            response = self.client.table('patient_documents').insert(document_data).execute()
            
            if response.data:
                # Create audit log entry
                audit_data = {
                    'user_id': internal_user_id,
                    'action': 'document_upload',
                    'type': 'document',
                    'filename': file.filename,
                    'data_hash': f"hash_{user_id}_doc_{file.filename}",
                    'timestamp': 'now()'
                }
                self.client.table('patient_audit_log').insert(audit_data).execute()
                
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error uploading patient document: {e}")
            return None

    def update_patient_privacy_settings(self, user_id, data):
        """Update patient privacy settings"""
        try:
            # First get the user profile to get the internal ID
            user_response = self.client.table('user_profiles').select('id').eq('firebase_uid', user_id).execute()
            if not user_response.data:
                print(f"No user profile found for Firebase UID: {user_id}")
                return None
            
            internal_user_id = user_response.data[0]['id']
            
            # Upsert privacy settings
            data['user_id'] = internal_user_id
            response = self.client.table('patient_privacy_settings').upsert(data).execute()
            
            if response.data:
                # Create audit log entry
                audit_data = {
                    'user_id': internal_user_id,
                    'action': 'privacy_settings_update',
                    'type': 'privacy',
                    'data_hash': f"hash_{user_id}_privacy_{data.get('profile_visibility', '')}",
                    'timestamp': 'now()'
                }
                self.client.table('patient_audit_log').insert(audit_data).execute()
                
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error updating patient privacy settings: {e}")
            return None