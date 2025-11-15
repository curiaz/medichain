from flask import Blueprint, request, jsonify

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

@notifications_bp.route("", methods=["GET"])  # /api/notifications
def list_notifications():
    """Return a paginated empty list of notifications (stub)."""
    try:
        user_id = request.args.get("user_id")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))
        # In real impl, fetch from DB by user_id
        return jsonify({
            "success": True,
            "data": {
                "items": [],
                "page": page,
                "per_page": per_page,
                "total": 0
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@notifications_bp.route("/stats", methods=["GET"])  # /api/notifications/stats
def notifications_stats():
    """Return empty notifications stats (stub)."""
    try:
        user_id = request.args.get("user_id")
        # In real impl, compute stats for user_id
        return jsonify({
            "success": True,
            "data": {
                "total": 0,
                "unread": 0,
                "today": 0
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
