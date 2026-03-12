# Files to Delete Manually

The following CSV files need to be deleted manually as they are currently in use by another process:

## CSV Files (Data now in Supabase)
- `backend/condition - Sheet1.csv`
- `backend/condition_reason - Sheet1.csv`
- `backend/action_medication - Sheet1.csv`

**Action Required:**
1. Close any Excel, VS Code, or other programs that might have these files open
2. Delete these files manually or run the cleanup script again

## Already Deleted ✅
- `backend/streamlined_model_v5.pkl` (old model)
- `backend/comprehensive_ai_diagnosis.py` (deprecated)
- `backend/simple_ai_server.py` (deprecated)
- `backend/nlp_app.py` (deprecated)

## Files to Keep
- `backend/app.py` (main backend with Supabase integration)
- `backend/test_supabase_ai_data.py` (Supabase data validation)
- `backend/test_ai_supabase.py` (AI system testing)
- `backend/test_api_endpoint.py` (API testing)
- All authentication and route files
- Database client files

## New Model Files
The system now generates:
- `streamlined_model_v6.pkl` (Supabase-based model - will be created on next run)
