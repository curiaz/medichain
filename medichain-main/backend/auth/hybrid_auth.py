"""
Hybrid authentication using Supabase Auth with database password fallback
Works with the improved profile trigger that handles null values
"""
import bcrypt
import uuid
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from db.supabase_client import SupabaseClient

supabase = SupabaseClient()

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user_hybrid(email, password, first_name, last_name, role):
    """Create user using Supabase Auth with proper metadata for the trigger"""
    try:
        # Check if email already exists
        existing_user = supabase.service_client.table('profiles').select('*').eq('email', email).execute()
        if existing_user.data:
            return {'success': False, 'error': 'Email already registered'}
        
        # Hash the password for our own storage
        password_hash = hash_password(password)
        
        # Create user with Supabase Auth admin API with proper metadata
        auth_response = supabase.service_client.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,  # Skip email confirmation
            "user_metadata": {
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
                "full_name": f"{first_name} {last_name}"
            }
        })
        
        if not auth_response.user:
            return {'success': False, 'error': 'Failed to create user account'}
        
        user_id = auth_response.user.id
        print(f"DEBUG: Created user with ID: {user_id}")
        
        # The trigger should have created the profile, but let's verify and update it
        # Wait a moment for the trigger to execute
        import time
        time.sleep(0.5)
        
        # Get the profile created by the trigger
        profile_response = supabase.service_client.table('profiles').select('*').eq('id', user_id).execute()
        
        if not profile_response.data:
            # If trigger didn't work, create profile manually
            profile_data = {
                'id': user_id,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'password_hash': password_hash
            }
            profile_response = supabase.service_client.table('profiles').insert(profile_data).execute()
        else:
            # Update the existing profile with our data and password hash
            update_data = {
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'password_hash': password_hash
            }
            profile_response = supabase.service_client.table('profiles').update(update_data).eq('id', user_id).execute()
        
        if not profile_response.data:
            # Clean up auth user if profile creation/update fails
            try:
                supabase.service_client.auth.admin.delete_user(user_id)
            except:
                pass
            return {'success': False, 'error': 'Failed to create user profile'}
        
        profile = profile_response.data[0]
        
        # Create role-specific record
        try:
            if role == 'patient':
                patient_data = {'user_id': user_id}
                supabase.service_client.table('patients').insert(patient_data).execute()
            elif role == 'doctor':
                doctor_data = {'user_id': user_id}
                supabase.service_client.table('doctors').insert(doctor_data).execute()
        except Exception as role_error:
            print(f"Warning: Could not create role-specific record: {role_error}")
        
        return {
            'success': True,
            'user': profile
        }
        
    except Exception as e:
        print(f"Create user hybrid error: {e}")
        return {'success': False, 'error': str(e)}

def authenticate_user_hybrid(email, password):
    """Authenticate user - try database password first, then Supabase Auth as fallback"""
    try:
        # Get user profile
        profile_response = supabase.service_client.table('profiles').select('*').eq('email', email).execute()
        
        if not profile_response.data:
            return {'success': False, 'error': 'User not found'}
        
        user = profile_response.data[0]
        stored_hash = user.get('password_hash')
        
        # Try our database password first
        if stored_hash and verify_password(password, stored_hash):
            print("DEBUG: Authenticated with database password")
            user_data = {key: value for key, value in user.items() if key != 'password_hash'}
            return {
                'success': True,
                'user': user_data
            }
        
        # Fallback to Supabase Auth for existing users without password_hash
        try:
            print("DEBUG: Trying Supabase Auth fallback")
            auth_response = supabase.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                print("DEBUG: Authenticated with Supabase Auth")
                # Optionally update the profile with password hash for future use
                password_hash = hash_password(password)
                supabase.service_client.table('profiles').update({
                    'password_hash': password_hash
                }).eq('id', user['id']).execute()
                
                user_data = {key: value for key, value in user.items() if key != 'password_hash'}
                return {
                    'success': True,
                    'user': user_data
                }
        except Exception as auth_error:
            print(f"DEBUG: Supabase Auth fallback failed: {auth_error}")
        
        return {'success': False, 'error': 'Invalid password'}
            
    except Exception as e:
        print(f"Authenticate user hybrid error: {e}")
        return {'success': False, 'error': str(e)}
