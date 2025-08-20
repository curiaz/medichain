"""
Simple database-only authentication helper functions
Uses a separate user_passwords table for security
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

def create_user(email, password, first_name, last_name, role):
    """Create a new user with password hash in profiles table"""
    try:
        # Generate UUID for user
        user_id = str(uuid.uuid4())
        
        # Check if email already exists
        existing_user = supabase.service_client.table('profiles').select('*').eq('email', email).execute()
        if existing_user.data:
            return {'success': False, 'error': 'Email already registered'}
        
        # Hash the password
        password_hash = hash_password(password)
        
        # Step 1: Create a minimal user record in auth.users table to satisfy foreign key
        try:
            user_data = {
                'id': user_id,
                'email': email,
                'encrypted_password': '',  # We'll use our own password hash
                'email_confirmed_at': 'now()',
                'created_at': 'now()',
                'updated_at': 'now()',
                'raw_app_meta_data': '{}',
                'raw_user_meta_data': '{}',
                'is_super_admin': False,
                'role': 'authenticated'
            }
            
            # Try to insert into users table
            user_response = supabase.service_client.table('users').insert(user_data).execute()
            print(f"DEBUG: Created user in auth.users table: {user_response.data}")
            
        except Exception as user_error:
            print(f"DEBUG: Could not create user in auth.users table: {user_error}")
            # If we can't create in users table, the foreign key constraint is blocking us
            return {'success': False, 'error': 'Cannot create user due to database constraints. Please remove foreign key constraint on profiles table.'}
        
        # Step 2: Create profile record with password hash
        profile_data = {
            'id': user_id,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'password_hash': password_hash
        }
        
        profile_response = supabase.service_client.table('profiles').insert(profile_data).execute()
        
        if not profile_response.data:
            # Clean up user record if profile creation fails
            try:
                supabase.service_client.table('users').delete().eq('id', user_id).execute()
            except:
                pass
            return {'success': False, 'error': 'Failed to create user profile'}
        
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
            'user': profile_response.data[0]
        }
        
    except Exception as e:
        print(f"Create user error: {e}")
        return {'success': False, 'error': str(e)}

def authenticate_user(email, password):
    """Authenticate user with email and password from profiles table"""
    try:
        # Get user profile with password hash
        profile_response = supabase.service_client.table('profiles').select('*').eq('email', email).execute()
        
        if not profile_response.data:
            return {'success': False, 'error': 'User not found'}
        
        user = profile_response.data[0]
        stored_hash = user.get('password_hash')
        
        if not stored_hash:
            return {'success': False, 'error': 'No password set for this user'}
        
        # Verify password
        if verify_password(password, stored_hash):
            # Remove password hash from returned user data for security
            user_data = {key: value for key, value in user.items() if key != 'password_hash'}
            return {
                'success': True,
                'user': user_data
            }
        else:
            return {'success': False, 'error': 'Invalid password'}
            
    except Exception as e:
        print(f"Authenticate user error: {e}")
        return {'success': False, 'error': str(e)}
