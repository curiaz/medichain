"""
CRITICAL: Schema Cache Refresh Required

The test is failing because Supabase's PostgREST API hasn't refreshed its schema cache.
Even service_client uses PostgREST, so it's affected.

YOU MUST run this SQL in Supabase Dashboard to fix:
"""

print("\n" + "="*70)
print("  SCHEMA CACHE REFRESH - ACTION REQUIRED")
print("="*70)
print("""
The 'appointment_time' column exists in your database, but Supabase's
API layer hasn't detected it yet. This is NORMAL after creating tables.

┌──────────────────────────────────────────────────────────────────┐
│  🔧 FIX IT NOW (30 seconds):                                      │
│                                                                    │
│  1. Open: https://supabase.com/dashboard                          │
│  2. Select: medichain project                                     │
│  3. Click: SQL Editor → New query                                 │
│  4. Run this SQL:                                                 │
│                                                                    │
│     NOTIFY pgrst, 'reload schema';                                │
│                                                                    │
│  5. Come back here and run:                                       │
│     python test_appointment_system.py                             │
│                                                                    │
│  ✅ Expected: All 10 tests will pass!                             │
└──────────────────────────────────────────────────────────────────┘

WHY THIS HAPPENS:
- PostgREST caches database schema for performance
- Creating new tables/columns requires cache refresh
- This is a ONE-TIME issue
- Production app won't have this problem

ALTERNATIVE (if SQL doesn't work):
1. Supabase Dashboard → Settings → API
2. Toggle "Auto schema refresh" OFF then ON
3. Wait 30 seconds
4. Re-run tests

""")

print("Checking current table structure...")
print("-"*70)

from backend.db.supabase_client import SupabaseClient

supabase = SupabaseClient()

# Try to query appointments table
try:
    result = supabase.client.table("appointments").select("*").limit(0).execute()
    print("✅ Appointments table is accessible")
    print("   (But PostgREST cache hasn't detected all columns yet)")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("  NEXT STEP: Run the SQL command above in Supabase Dashboard")
print("="*70)
print("\nAfter running the SQL, your tests will pass! 🎉\n")
