"""
Audit Ledger Service - Blockchain-style Immutable Audit Log
Tracks all admin actions with hash chaining for integrity verification
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
from db.supabase_client import SupabaseClient
import traceback


class AuditService:
    """Service for creating and managing audit ledger entries"""
    
    def __init__(self):
        try:
            self.supabase = SupabaseClient()
            print("[OK] AuditService initialized")
        except Exception as e:
            print(f"[WARNING] AuditService initialization failed: {e}")
            self.supabase = None
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of entry data"""
        # Convert data to JSON string (sorted keys for consistency)
        data_str = json.dumps(data, sort_keys=True, default=str)
        # Calculate hash
        hash_obj = hashlib.sha256(data_str.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def _get_previous_hash(self) -> str:
        """Get the hash of the most recent ledger entry"""
        try:
            if not self.supabase:
                return ""
            
            # Get the latest entry - order by created_at first (always exists), then block_number
            response = self.supabase.service_client.table("audit_ledger")\
                .select("current_hash")\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0].get("current_hash", "")
            
            return ""  # First entry has no previous hash
        except Exception as e:
            print(f"[WARNING] Error getting previous hash: {e}")
            return ""
    
    def _get_next_block_number(self) -> int:
        """Get the next block number in the chain"""
        try:
            if not self.supabase:
                return 1
            
            # Get the latest block number - order by created_at first, then block_number
            response = self.supabase.service_client.table("audit_ledger")\
                .select("block_number")\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            if response.data and len(response.data) > 0:
                latest_block = response.data[0].get("block_number", 0)
                return latest_block + 1
            
            return 1  # First block
        except Exception as e:
            print(f"[WARNING] Error getting next block number: {e}")
            return 1
    
    def _calculate_data_diff(self, data_before: Optional[Dict], data_after: Optional[Dict]) -> Dict[str, Any]:
        """Calculate the difference between before and after data"""
        if not data_before and not data_after:
            return {}
        
        if not data_before:
            return {"created": data_after}
        
        if not data_after:
            return {"deleted": data_before}
        
        # Find changed fields
        changes = {}
        all_keys = set(data_before.keys()) | set(data_after.keys())
        
        for key in all_keys:
            before_val = data_before.get(key)
            after_val = data_after.get(key)
            
            if before_val != after_val:
                changes[key] = {
                    "before": before_val,
                    "after": after_val
                }
        
        return changes
    
    def log_action(
        self,
        admin_id: str,
        admin_email: Optional[str] = None,
        admin_name: Optional[str] = None,
        action_type: str = "UNKNOWN",
        action_description: Optional[str] = None,
        entity_type: str = "unknown",
        entity_id: Optional[str] = None,
        data_before: Optional[Dict[str, Any]] = None,
        data_after: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Log an admin action to the audit ledger
        
        Args:
            admin_id: Firebase UID of admin performing action
            admin_email: Email of admin (optional)
            admin_name: Name of admin (optional)
            action_type: Type of action (CREATE, UPDATE, DELETE, VIEW, APPROVE, etc.)
            action_description: Human-readable description
            entity_type: Type of entity (user, appointment, doctor_profile, etc.)
            entity_id: ID of affected entity
            data_before: State before action (for UPDATE/DELETE)
            data_after: State after action (for CREATE/UPDATE)
            ip_address: IP address of requester
            user_agent: User agent string
            request_id: Unique request identifier
            metadata: Additional metadata
        
        Returns:
            Created ledger entry or None if failed
        """
        try:
            print(f"[DEBUG] ===== AUDIT SERVICE LOG_ACTION CALLED =====")
            print(f"[DEBUG] action_type={action_type}, entity_type={entity_type}, admin_id={admin_id}")
            if not self.supabase:
                print("[ERROR] AuditService: Supabase not initialized, skipping audit log")
                print("[ERROR] This means audit_service.supabase is None - check SupabaseClient initialization")
                return None
            if not self.supabase.service_client:
                print("[ERROR] AuditService: Supabase service_client not initialized, skipping audit log")
                print("[ERROR] This means audit_service.supabase.service_client is None")
                return None
            
            # Get chain info
            previous_hash = self._get_previous_hash()
            block_number = self._get_next_block_number()
            
            # Calculate data changes
            data_changes = self._calculate_data_diff(data_before, data_after)
            
            # Prepare entry data
            entry_data = {
                "previous_hash": previous_hash,
                "admin_id": admin_id,
                "admin_email": admin_email,
                "admin_name": admin_name,
                "action_type": action_type.upper(),
                "action_description": action_description or f"{action_type} on {entity_type}",
                "entity_type": entity_type.lower(),
                "entity_id": entity_id,
                "block_number": block_number,
                "user_agent": user_agent,
                "request_id": request_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Handle IP address - convert to string if needed (INET type accepts string)
            if ip_address:
                entry_data["ip_address"] = str(ip_address)
            
            # Add JSONB fields
            if data_before:
                entry_data["data_before"] = data_before
            if data_after:
                entry_data["data_after"] = data_after
            if data_changes:
                entry_data["data_changes"] = data_changes
            if metadata:
                entry_data["metadata"] = metadata
            
            # Calculate current hash (include ALL data for true blockchain immutability)
            # This ensures any tampering will be detected through hash verification
            hash_data = {
                "previous_hash": previous_hash,
                "block_number": block_number,
                "admin_id": admin_id,
                "admin_email": admin_email,
                "action_type": action_type.upper(),
                "action_description": action_description or f"{action_type} on {entity_type}",
                "entity_type": entity_type.lower(),
                "entity_id": entity_id,
                "data_before": data_before,  # Include full before state
                "data_after": data_after,    # Include full after state
                "data_changes": data_changes,
                "timestamp": entry_data["created_at"],
                "ip_address": ip_address,
                "user_agent": user_agent
            }
            current_hash = self._calculate_hash(hash_data)
            entry_data["current_hash"] = current_hash
            
            # Insert into database
            print(f"[DEBUG] Inserting audit log entry: action_type={action_type}, entity_type={entity_type}, admin_id={admin_id}")
            print(f"[DEBUG] Entry data keys: {list(entry_data.keys())}")
            print(f"[DEBUG] Entry data sample: admin_id={admin_id}, action_type={action_type}, block_number={block_number}")
            
            try:
                response = self.supabase.service_client.table("audit_ledger").insert(entry_data).execute()
                
                print(f"[DEBUG] Insert response type: {type(response)}")
                print(f"[DEBUG] Insert response: data={response.data is not None}, count={len(response.data) if response.data else 0}")
                
                if response.data and len(response.data) > 0:
                    print(f"[OK] Audit log created: {action_type} on {entity_type} by {admin_email or admin_id} (ID: {response.data[0].get('id', 'unknown')})")
                    return response.data[0]
                else:
                    print(f"[ERROR] Audit log insert returned no data.")
                    print(f"[ERROR] Response object: {response}")
                    print(f"[ERROR] Response type: {type(response)}")
                    if hasattr(response, 'error'):
                        print(f"[ERROR] Supabase error: {response.error}")
                    if hasattr(response, 'data'):
                        print(f"[ERROR] Response.data: {response.data}")
                    if hasattr(response, 'status_code'):
                        print(f"[ERROR] Status code: {response.status_code}")
                    return None
            except Exception as insert_error:
                print(f"[ERROR] Exception during insert: {insert_error}")
                print(f"[ERROR] Exception type: {type(insert_error)}")
                import traceback
                traceback.print_exc()
                return None
                
        except Exception as e:
            print(f"[ERROR] Error creating audit log: {e}")
            traceback.print_exc()
            return None
    
    def get_ledger_entries(
        self,
        admin_id: Optional[str] = None,
        action_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Query audit ledger entries with filters
        
        Returns:
            Dictionary with entries and pagination info
        """
        try:
            if not self.supabase:
                return {"entries": [], "total": 0, "error": "Supabase not initialized"}
            
            # First, try a simple query to check if table exists and is accessible
            try:
                test_query = self.supabase.service_client.table("audit_ledger").select("id", count="exact").limit(1).execute()
                print(f"[DEBUG] Audit ledger table accessible. Total entries: {test_query.count or 0}")
            except Exception as test_error:
                print(f"[ERROR] Cannot access audit_ledger table: {test_error}")
                traceback.print_exc()
                return {"entries": [], "total": 0, "error": f"Cannot access audit_ledger table: {str(test_error)}"}
            
            query = self.supabase.service_client.table("audit_ledger").select("*", count="exact")
            
            # Apply filters
            if admin_id:
                query = query.eq("admin_id", admin_id)
            if action_type:
                query = query.eq("action_type", action_type.upper())
            if entity_type:
                query = query.eq("entity_type", entity_type.lower())
            if entity_id:
                query = query.eq("entity_id", entity_id)
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            if end_date:
                query = query.lte("created_at", end_date.isoformat())
            
            # Order and paginate - use created_at (always exists, NOT NULL)
            # This handles empty tables gracefully
            query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
            
            print(f"[DEBUG] Executing audit ledger query with offset={offset}, limit={limit}")
            response = query.execute()
            
            # Safely extract data and count (matching pattern from admin_routes.py)
            entries = response.data if response.data else []
            total = response.count if hasattr(response, 'count') and response.count is not None else len(entries)
            
            print(f"[DEBUG] Query executed. Found {len(entries)} entries, total count: {total}")
            
            return {
                "entries": entries,
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            print(f"[ERROR] Error querying audit ledger: {e}")
            traceback.print_exc()
            return {"entries": [], "total": 0, "error": str(e)}
    
    def verify_chain_integrity(self) -> Dict[str, Any]:
        """
        Verify the integrity of the audit ledger chain
        
        Returns:
            Dictionary with verification results
        """
        try:
            if not self.supabase:
                return {"verified": False, "error": "Supabase not initialized"}
            
            # Get all entries ordered by block number
            response = self.supabase.service_client.table("audit_ledger")\
                .select("*")\
                .order("block_number", desc=False)\
                .execute()
            
            entries = response.data or []
            
            if not entries:
                return {"verified": True, "message": "Ledger is empty", "entries_checked": 0}
            
            broken_links = []
            tampered_entries = []
            
            for i, entry in enumerate(entries):
                if i == 0:
                    # First entry should have empty previous_hash
                    if entry.get("previous_hash"):
                        broken_links.append({
                            "block_number": entry.get("block_number"),
                            "issue": "First entry has non-empty previous_hash"
                        })
                    # Verify first entry's hash
                    hash_data = {
                        "previous_hash": entry.get("previous_hash") or "",
                        "block_number": entry.get("block_number"),
                        "admin_id": entry.get("admin_id"),
                        "admin_email": entry.get("admin_email"),
                        "action_type": entry.get("action_type"),
                        "action_description": entry.get("action_description"),
                        "entity_type": entry.get("entity_type"),
                        "entity_id": entry.get("entity_id"),
                        "data_before": entry.get("data_before"),
                        "data_after": entry.get("data_after"),
                        "data_changes": entry.get("data_changes"),
                        "timestamp": entry.get("created_at"),
                        "ip_address": entry.get("ip_address"),
                        "user_agent": entry.get("user_agent")
                    }
                    recalculated_hash = self._calculate_hash(hash_data)
                    stored_hash = entry.get("current_hash")
                    if recalculated_hash != stored_hash:
                        tampered_entries.append({
                            "block_number": entry.get("block_number"),
                            "stored_hash": stored_hash,
                            "recalculated_hash": recalculated_hash,
                            "issue": "Hash mismatch - data may have been tampered"
                        })
                    continue
                
                # Check if previous hash matches (chain link)
                previous_entry = entries[i - 1]
                expected_previous_hash = previous_entry.get("current_hash")
                actual_previous_hash = entry.get("previous_hash")
                
                if expected_previous_hash != actual_previous_hash:
                    broken_links.append({
                        "block_number": entry.get("block_number"),
                        "expected": expected_previous_hash,
                        "actual": actual_previous_hash,
                        "issue": "Chain link broken"
                    })
                
                # Verify current entry's hash (detect tampering)
                hash_data = {
                    "previous_hash": entry.get("previous_hash") or "",
                    "block_number": entry.get("block_number"),
                    "admin_id": entry.get("admin_id"),
                    "admin_email": entry.get("admin_email"),
                    "action_type": entry.get("action_type"),
                    "action_description": entry.get("action_description"),
                    "entity_type": entry.get("entity_type"),
                    "entity_id": entry.get("entity_id"),
                    "data_before": entry.get("data_before"),
                    "data_after": entry.get("data_after"),
                    "data_changes": entry.get("data_changes"),
                    "timestamp": entry.get("created_at"),
                    "ip_address": entry.get("ip_address"),
                    "user_agent": entry.get("user_agent")
                }
                recalculated_hash = self._calculate_hash(hash_data)
                stored_hash = entry.get("current_hash")
                if recalculated_hash != stored_hash:
                    tampered_entries.append({
                        "block_number": entry.get("block_number"),
                        "stored_hash": stored_hash,
                        "recalculated_hash": recalculated_hash,
                        "issue": "Hash mismatch - data may have been tampered"
                    })
            
            verified = len(broken_links) == 0 and len(tampered_entries) == 0
            
            return {
                "verified": verified,
                "entries_checked": len(entries),
                "broken_links": broken_links,
                "tampered_entries": tampered_entries,
                "message": "Chain verified - all entries are immutable and linked correctly" if verified else f"Chain integrity compromised: {len(broken_links)} broken link(s), {len(tampered_entries)} tampered entries"
            }
            
        except Exception as e:
            print(f"[ERROR] Error verifying chain integrity: {e}")
            traceback.print_exc()
            return {"verified": False, "error": str(e)}


# Singleton instance
audit_service = AuditService()

