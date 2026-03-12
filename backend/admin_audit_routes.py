"""
Admin Audit Ledger Routes
API endpoints for viewing and querying the blockchain-style audit ledger
"""

from flask import Blueprint, jsonify, request
from auth.firebase_auth import firebase_role_required
from services.audit_service import audit_service
from datetime import datetime

admin_audit_bp = Blueprint('admin_audit', __name__, url_prefix='/api/admin/audit')


@admin_audit_bp.route('/test', methods=['GET'])
def test_route():
    """Simple test endpoint to verify route registration (no auth required)"""
    return jsonify({
        "success": True,
        "message": "Audit routes are registered",
        "audit_service_initialized": audit_service is not None,
        "audit_service_supabase": audit_service.supabase is not None if audit_service else False
    }), 200


@admin_audit_bp.route('/test-insert', methods=['POST'])
def test_insert():
    """Test endpoint to create a test audit log entry (no auth required for debugging)"""
    try:
        print("[DEBUG] ===== TEST INSERT ENDPOINT CALLED =====")
        
        # Check if audit_service exists
        if not audit_service:
            return jsonify({
                "success": False,
                "error": "audit_service is None or not initialized"
            }), 500
        
        # Check if supabase is initialized
        if not audit_service.supabase:
            return jsonify({
                "success": False,
                "error": "audit_service.supabase is None - Supabase not initialized"
            }), 500
        
        # Check if service_client exists
        if not audit_service.supabase.service_client:
            return jsonify({
                "success": False,
                "error": "audit_service.supabase.service_client is None"
            }), 500
        
        # Try to query the table to see if it exists
        try:
            test_query = audit_service.supabase.service_client.table("audit_ledger").select("id").limit(1).execute()
            print(f"[DEBUG] Table exists, query successful. Count: {len(test_query.data) if test_query.data else 0}")
        except Exception as table_error:
            return jsonify({
                "success": False,
                "error": f"audit_ledger table query failed: {str(table_error)}",
                "hint": "Make sure you've run database/create_audit_ledger.sql in Supabase"
            }), 500
        
        print("[DEBUG] Calling audit_service.log_action...")
        result = audit_service.log_action(
            admin_id="test-user-123",
            admin_email="test@example.com",
            admin_name="Test User",
            action_type="TEST",
            action_description="Test audit log entry",
            entity_type="test",
            entity_id="test-123",
            data_after={"test": "data"},
            ip_address="127.0.0.1",
            user_agent="Test Agent"
        )
        
        if result:
            return jsonify({
                "success": True,
                "message": "Test audit log created successfully",
                "entry_id": result.get("id"),
                "block_number": result.get("block_number"),
                "current_hash": result.get("current_hash")
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Test audit log creation returned None - check backend logs for [ERROR] or [WARNING] messages"
            }), 500
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"[ERROR] Exception in test-insert: {e}")
        print(error_traceback)
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": error_traceback
        }), 500


@admin_audit_bp.route('/health', methods=['GET'])
@firebase_role_required(["admin"])
def audit_health_check():
    """Health check for audit ledger system (admin only)"""
    try:
        from db.supabase_client import SupabaseClient
        supabase = SupabaseClient()
        
        # Test table access
        test_response = supabase.service_client.table("audit_ledger").select("id", count="exact").limit(1).execute()
        
        return jsonify({
            "success": True,
            "audit_service_initialized": audit_service is not None,
            "supabase_initialized": audit_service.supabase is not None if audit_service else False,
            "table_accessible": True,
            "total_entries": test_response.count if hasattr(test_response, 'count') else 0,
            "message": "Audit ledger system is operational"
        }), 200
    except Exception as e:
        import traceback
        return jsonify({
            "success": False,
            "audit_service_initialized": audit_service is not None,
            "supabase_initialized": audit_service.supabase is not None if audit_service else False,
            "table_accessible": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@admin_audit_bp.route('/ledger', methods=['GET'])
@firebase_role_required(["admin"])
def get_audit_ledger():
    """Get audit ledger entries with filters (admin only)"""
    try:
        print(f"[DEBUG] get_audit_ledger called. Query params: {dict(request.args)}")
        print(f"[DEBUG] audit_service initialized: {audit_service is not None}")
        print(f"[DEBUG] audit_service.supabase: {audit_service.supabase is not None if audit_service else None}")
        
        # Check if audit_service is properly initialized
        if not audit_service:
            print("[ERROR] audit_service is None!")
            return jsonify({"success": False, "error": "Audit service not initialized"}), 500
        
        if not audit_service.supabase:
            print("[ERROR] audit_service.supabase is None!")
            return jsonify({"success": False, "error": "Supabase client not initialized in audit service"}), 500
        # Get query parameters
        admin_id = request.args.get('admin_id')
        action_type = request.args.get('action_type')
        entity_type = request.args.get('entity_type')
        entity_id = request.args.get('entity_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit
        
        # Parse dates
        start_datetime = None
        end_datetime = None
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                pass
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                pass
        
        # Query audit ledger
        print(f"[DEBUG] Calling audit_service.get_ledger_entries with filters...")
        result = audit_service.get_ledger_entries(
            admin_id=admin_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            start_date=start_datetime,
            end_date=end_datetime,
            limit=limit,
            offset=offset
        )
        
        print(f"[DEBUG] Result from audit_service: {type(result)}, keys: {result.keys() if isinstance(result, dict) else 'not a dict'}")
        
        if "error" in result:
            error_msg = result.get("error", "Unknown error")
            print(f"[ERROR] audit_service returned error: {error_msg}")
            return jsonify({"success": False, "error": error_msg}), 500
        
        print(f"[DEBUG] Returning success response with {len(result.get('entries', []))} entries")
        return jsonify({
            "success": True,
            "entries": result.get("entries", []),
            "pagination": {
                "page": page,
                "limit": limit,
                "total": result.get("total", 0),
                "total_pages": (result.get("total", 0) + limit - 1) // limit if result.get("total", 0) else 0
            }
        }), 200
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Error fetching audit ledger: {e}")
        print(f"[ERROR] Full traceback:\n{error_trace}")
        return jsonify({"success": False, "error": str(e), "details": error_trace}), 500


@admin_audit_bp.route('/ledger/<entry_id>', methods=['GET'])
@firebase_role_required(["admin"])
def get_audit_entry(entry_id):
    """Get single audit ledger entry by ID (admin only)"""
    try:
        # Query for specific entry
        result = audit_service.get_ledger_entries(
            entity_id=entry_id,
            limit=1
        )
        
        if "error" in result:
            return jsonify({"success": False, "error": result["error"]}), 500
        
        if not result["entries"]:
            return jsonify({"success": False, "error": "Entry not found"}), 404
        
        return jsonify({
            "success": True,
            "entry": result["entries"][0]
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error fetching audit entry: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_audit_bp.route('/ledger/verify', methods=['GET'])
@firebase_role_required(["admin"])
def verify_ledger_integrity():
    """Verify the integrity of the audit ledger chain (admin only)"""
    try:
        result = audit_service.verify_chain_integrity()
        
        return jsonify({
            "success": True,
            "verification": result
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error verifying ledger integrity: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_audit_bp.route('/ledger/stats', methods=['GET'])
@firebase_role_required(["admin"])
def get_audit_stats():
    """Get audit ledger statistics (admin only)"""
    try:
        from services.audit_service import audit_service
        from db.supabase_client import SupabaseClient
        
        supabase = SupabaseClient()
        
        # Get total entries
        total_response = supabase.service_client.table("audit_ledger")\
            .select("*", count="exact")\
            .execute()
        
        total_entries = total_response.count or 0
        
        # Get actions by type
        actions_response = supabase.service_client.table("audit_ledger")\
            .select("action_type")\
            .execute()
        
        action_counts = {}
        for entry in (actions_response.data or []):
            action = entry.get("action_type", "UNKNOWN")
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Get entities by type
        entities_response = supabase.service_client.table("audit_ledger")\
            .select("entity_type")\
            .execute()
        
        entity_counts = {}
        for entry in (entities_response.data or []):
            entity = entry.get("entity_type", "unknown")
            entity_counts[entity] = entity_counts.get(entity, 0) + 1
        
        # Get recent activity (last 24 hours)
        from datetime import datetime, timedelta
        twenty_four_hours_ago = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        recent_response = supabase.service_client.table("audit_ledger")\
            .select("*", count="exact")\
            .gte("created_at", twenty_four_hours_ago)\
            .execute()
        
        recent_entries = recent_response.count or 0
        
        # Get unique admins
        admins_response = supabase.service_client.table("audit_ledger")\
            .select("admin_id")\
            .execute()
        
        unique_admins = len(set(entry.get("admin_id") for entry in (admins_response.data or [])))
        
        return jsonify({
            "success": True,
            "stats": {
                "total_entries": total_entries,
                "recent_entries_24h": recent_entries,
                "unique_admins": unique_admins,
                "actions_by_type": action_counts,
                "entities_by_type": entity_counts
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error fetching audit stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_audit_bp.route('/ledger/entity/<entity_type>/<entity_id>', methods=['GET'])
@firebase_role_required(["admin"])
def get_entity_history(entity_type, entity_id):
    """Get complete audit history for a specific entity (admin only)"""
    try:
        result = audit_service.get_ledger_entries(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=100  # Get full history
        )
        
        if "error" in result:
            return jsonify({"success": False, "error": result["error"]}), 500
        
        return jsonify({
            "success": True,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "history": result["entries"],
            "total_events": result["total"]
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error fetching entity history: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_audit_bp.route('/ledger/admin/<admin_id>', methods=['GET'])
@firebase_role_required(["admin"])
def get_admin_activity(admin_id):
    """Get all audit entries for a specific admin (admin only)"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit
        
        result = audit_service.get_ledger_entries(
            admin_id=admin_id,
            limit=limit,
            offset=offset
        )
        
        if "error" in result:
            return jsonify({"success": False, "error": result["error"]}), 500
        
        return jsonify({
            "success": True,
            "admin_id": admin_id,
            "entries": result["entries"],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": result["total"],
                "total_pages": (result["total"] + limit - 1) // limit if result["total"] else 0
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error fetching admin activity: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


print("[OK] Admin audit routes loaded!")
print("[INFO] Available endpoints:")
print("   - GET /api/admin/audit/ledger - Get audit ledger with filters")
print("   - GET /api/admin/audit/ledger/<id> - Get single entry")
print("   - GET /api/admin/audit/ledger/verify - Verify chain integrity")
print("   - GET /api/admin/audit/ledger/stats - Get statistics")
print("   - GET /api/admin/audit/ledger/entity/<type>/<id> - Get entity history")
print("   - GET /api/admin/audit/ledger/admin/<admin_id> - Get admin activity")
print("[SECURITY] All endpoints require admin role")

