"""
File serving routes for appointment documents
"""
from flask import Blueprint, send_file, jsonify, request
from functools import wraps
import os
from db.supabase_client import SupabaseClient

file_bp = Blueprint('files', __name__, url_prefix='/api/files')

# Initialize Supabase client
try:
    supabase = SupabaseClient()
    print("✅ Supabase client initialized for file routes")
except Exception as e:
    print(f"⚠️  Warning: Supabase client initialization failed in file routes: {e}")
    supabase = None

def auth_required(f):
    """Decorator that accepts both Firebase and JWT tokens"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return jsonify({"error": "No authorization header provided"}), 401
        
        try:
            token = auth_header.split(" ")[1]  # Remove 'Bearer ' prefix
            
            # Try Firebase token verification
            if supabase:
                user_info = supabase.verify_firebase_token(token)
                if user_info:
                    request.firebase_user = user_info
                    return f(*args, **kwargs)
            
            # If Firebase verification fails, try JWT (for backward compatibility)
            # For now, we'll just check if token exists
            # In production, you'd verify JWT here
            
        except Exception as e:
            print(f"Error verifying token: {e}")
            return jsonify({"error": "Invalid or expired token"}), 401
        
        return jsonify({"error": "Authentication failed"}), 401
    
    return decorated_function

@file_bp.route('/appointments/<appointment_id>/documents/<filename>', methods=['GET'])
@auth_required
def get_appointment_document(appointment_id, filename):
    """
    Serve appointment document files
    Supports files stored in:
    1. Local uploads folder
    2. Supabase Storage
    3. Base64 data in database
    """
    try:
        if not supabase or not supabase.service_client:
            return jsonify({"error": "Database connection failed"}), 500
        
        # Get the appointment to verify access and get documents
        appointment_response = supabase.service_client.table("appointments").select("documents, patient_firebase_uid, doctor_firebase_uid").eq("id", appointment_id).execute()
        
        if not appointment_response.data:
            return jsonify({"error": "Appointment not found"}), 404
        
        appointment = appointment_response.data[0]
        documents = appointment.get("documents", [])
        
        # Handle case where documents might be None or not a list
        if documents is None:
            documents = []
        if not isinstance(documents, list):
            print(f"⚠️  Documents is not a list: {type(documents)}, value: {documents}")
            documents = []
        
        print(f"📄 Looking for file '{filename}' in {len(documents)} documents for appointment {appointment_id}")
        
        # Verify user has access (must be patient or doctor for this appointment)
        firebase_user = request.firebase_user
        user_uid = firebase_user.get("user_id") or firebase_user.get("uid")
        
        patient_uid = appointment.get("patient_firebase_uid")
        doctor_uid = appointment.get("doctor_firebase_uid")
        
        if user_uid not in [patient_uid, doctor_uid]:
            print(f"❌ Access denied: user {user_uid} not authorized for appointment {appointment_id}")
            return jsonify({"error": "Access denied"}), 403
        
        # Find the document in the documents array
        document = None
        for doc in documents:
            doc_name = doc.get("name") or doc.get("filename")
            if doc_name == filename:
                document = doc
                print(f"✅ Found document: {doc}")
                break
        
        if not document:
            print(f"❌ Document '{filename}' not found in documents array")
            print(f"   Available documents: {[doc.get('name') or doc.get('filename') for doc in documents]}")
            return jsonify({"error": f"Document '{filename}' not found in appointment"}), 404
        
        # Check if file has base64 data
        if document.get("data") or document.get("base64"):
            import base64
            from io import BytesIO
            
            base64_data = document.get("data") or document.get("base64")
            if not base64_data:
                print(f"⚠️  Document has 'data' or 'base64' key but value is empty")
                return jsonify({"error": "File data is empty"}), 400
            
            # Remove data URL prefix if present
            if isinstance(base64_data, str) and "," in base64_data:
                base64_data = base64_data.split(",")[1]
            
            try:
                file_data = base64.b64decode(base64_data)
                file_obj = BytesIO(file_data)
                
                # Determine content type
                content_type = document.get("type") or "application/octet-stream"
                if filename.lower().endswith('.pdf'):
                    content_type = 'application/pdf'
                elif filename.lower().endswith(('.jpg', '.jpeg')):
                    content_type = 'image/jpeg'
                elif filename.lower().endswith('.png'):
                    content_type = 'image/png'
                
                print(f"✅ Serving file from base64 data: {filename} ({len(file_data)} bytes, {content_type})")
                return send_file(
                    file_obj,
                    mimetype=content_type,
                    as_attachment=False,
                    download_name=filename
                )
            except Exception as e:
                print(f"❌ Error decoding base64 data: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({"error": f"Invalid file data: {str(e)}"}), 400
        
        # Check if file has a file_path pointing to local storage
        file_path = document.get("file_path") or document.get("file_url")
        if file_path:
            # If it's a full URL, redirect or proxy it
            if file_path.startswith("http"):
                # For external URLs, we could proxy or redirect
                # For now, return the URL as JSON
                return jsonify({"url": file_path}), 200
            
            # Check local uploads folder
            uploads_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "appointments")
            local_file_path = os.path.join(uploads_folder, appointment_id, filename)
            
            if os.path.exists(local_file_path):
                # Determine content type
                content_type = document.get("type") or "application/octet-stream"
                if filename.lower().endswith('.pdf'):
                    content_type = 'application/pdf'
                elif filename.lower().endswith(('.jpg', '.jpeg')):
                    content_type = 'image/jpeg'
                elif filename.lower().endswith('.png'):
                    content_type = 'image/png'
                
                return send_file(
                    local_file_path,
                    mimetype=content_type,
                    as_attachment=False,
                    download_name=filename
                )
        
        # If file_path is a Supabase Storage path, try to get signed URL
        if file_path and file_path.startswith("documents/"):
            try:
                # Try to get file from Supabase Storage
                # This would require Supabase Storage setup
                # For now, return error
                print(f"⚠️  Supabase Storage not configured for path: {file_path}")
                return jsonify({"error": "File storage not configured. Files need to be uploaded with base64 data."}), 501
            except Exception as e:
                print(f"❌ Error accessing Supabase Storage: {e}")
                return jsonify({"error": "File not accessible"}), 404
        
        # If we get here, the document exists but has no file data
        print(f"⚠️  Document '{filename}' found but has no file data (no base64, no file_path)")
        print(f"   Document structure: {document}")
        return jsonify({
            "error": "File data not available",
            "message": "The document metadata exists but the actual file was not uploaded. Files need to be uploaded when creating the appointment.",
            "document": {
                "name": document.get("name") or document.get("filename"),
                "size": document.get("size"),
                "type": document.get("type")
            }
        }), 404
        
    except Exception as e:
        print(f"Error serving file: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@file_bp.route('/<path:file_path>', methods=['GET'])
@auth_required
def get_file(file_path):
    """
    Generic file serving endpoint
    """
    try:
        # Security: prevent directory traversal
        if ".." in file_path or file_path.startswith("/"):
            return jsonify({"error": "Invalid file path"}), 400
        
        # Check local uploads folder
        uploads_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        local_file_path = os.path.join(uploads_folder, file_path)
        
        # Normalize path to prevent directory traversal
        local_file_path = os.path.normpath(local_file_path)
        uploads_folder = os.path.normpath(uploads_folder)
        
        if not local_file_path.startswith(uploads_folder):
            return jsonify({"error": "Invalid file path"}), 400
        
        if os.path.exists(local_file_path) and os.path.isfile(local_file_path):
            # Determine content type from extension
            content_type = "application/octet-stream"
            if file_path.lower().endswith('.pdf'):
                content_type = 'application/pdf'
            elif file_path.lower().endswith(('.jpg', '.jpeg')):
                content_type = 'image/jpeg'
            elif file_path.lower().endswith('.png'):
                content_type = 'image/png'
            
            return send_file(
                local_file_path,
                mimetype=content_type,
                as_attachment=False
            )
        
        return jsonify({"error": "File not found"}), 404
        
    except Exception as e:
        print(f"Error serving file: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

