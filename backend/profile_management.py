from flask import Blueprint, jsonify, request
import hashlib
import json as _json
from datetime import datetime

# Minimal blueprint to satisfy tests that import profile_mgmt_bp
profile_mgmt_bp = Blueprint('profile_mgmt', __name__, url_prefix='/api/profile-mgmt')

# Expose a supabase attribute so tests can patch it
supabase = None


def generate_blockchain_hash(data: dict) -> str:
	"""Generate a deterministic SHA256 hash from dict-like data."""
	# Ensure stable ordering by dumping with sort_keys=True
	payload = _json.dumps(data, sort_keys=True, separators=(",", ":"))
	return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def allowed_file(filename: str) -> bool:
	"""Validate upload filename by extension."""
	if not isinstance(filename, str) or '.' not in filename:
		return False
	allowed_extensions = {"pdf", "jpg", "jpeg", "png"}
	ext = filename.rsplit('.', 1)[1].lower()
	return ext in allowed_extensions


def create_blockchain_transaction(user_id: str, action: str, data_hash: str, metadata: dict | None = None):
	"""Create a mock blockchain transaction record.
	This function returns a dict with a tx hash to satisfy tests.
	"""
	if metadata is None:
		metadata = {}
	record = {
		"user_id": user_id,
		"action": action,
		"data_hash": data_hash,
		"metadata": metadata,
		"timestamp": datetime.utcnow().isoformat()
	}
	# Deterministic placeholder tx hash derived from record
	tx_hash = hashlib.sha256(_json.dumps(record, sort_keys=True).encode('utf-8')).hexdigest()
	return {"blockchain_tx_hash": tx_hash, **record}


@profile_mgmt_bp.route('/health', methods=['GET'])
def health():
	return jsonify({"success": True, "message": "profile_mgmt healthy"})
