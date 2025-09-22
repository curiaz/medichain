#!/usr/bin/env python3
"""
Check if the firebase_uid sync trigger was applied successfully
"""

from db.supabase_client import SupabaseClient

def check_triggers():
    supabase = SupabaseClient()

    print("🔍 Checking if firebase_uid sync triggers were applied...")

    try:
        # Check for triggers on user_profiles table
        result = supabase.service_client.rpc('get_table_triggers', {
            'table_name': 'user_profiles'
        })

        if result.data:
            print("✅ Triggers found on user_profiles:")
            for trigger in result.data:
                print(f"  - {trigger.get('trigger_name', 'Unknown')}")
        else:
            print("❌ No triggers found on user_profiles")

        # Check for triggers on doctor_profiles table
        result2 = supabase.service_client.rpc('get_table_triggers', {
            'table_name': 'doctor_profiles'
        })

        if result2.data:
            print("✅ Triggers found on doctor_profiles:")
            for trigger in result2.data:
                print(f"  - {trigger.get('trigger_name', 'Unknown')}")
        else:
            print("❌ No triggers found on doctor_profiles")

    except Exception as e:
        print(f"❌ Error checking triggers: {e}")
        print("This might mean the triggers weren't applied or there's a permission issue")

    # Alternative: Try to query the information_schema
    print("\n🔍 Checking information_schema for triggers...")
    try:
        triggers_query = """
        SELECT
            event_object_table,
            trigger_name,
            event_manipulation,
            action_timing
        FROM information_schema.triggers
        WHERE event_object_table IN ('user_profiles', 'doctor_profiles')
        ORDER BY event_object_table, trigger_name;
        """

        # This might not work with Supabase client, but let's try
        print("Manual check needed in Supabase SQL Editor:")
        print("Run this query to see if triggers exist:")
        print(triggers_query)

    except Exception as e:
        print(f"❌ Error with information_schema query: {e}")

if __name__ == '__main__':
    check_triggers()
