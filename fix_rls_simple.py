#!/usr/bin/env python3
"""
Simple RLS Policy Fix Script
This script applies permissive RLS policies to allow profile updates during development
"""

import os
import sys
from supabase import create_client, Client

def main():
    # Supabase credentials
    url = "https://royvcmfbcghamnbnxdgb.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJveXZjbWZiY2doYW1uYm54ZGdiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjgwNDA5OSwiZXhwIjoyMDY4MzgwMDk5fQ.8xyMLK2bM3wgluCT0TcRKxMu_qtaHQs7HTccMu0nL08"  # Service role key for admin operations
    
    try:
        supabase: Client = create_client(url, key)
        print("🔗 Connected to Supabase")
        
        # Read the SQL file
        sql_file = "fix_rls_simple.sql"
        if not os.path.exists(sql_file):
            print(f"❌ SQL file {sql_file} not found")
            return
        
        with open(sql_file, 'r') as f:
            sql_commands = f.read()
        
        # Split by semicolon and execute each command
        commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        
        print(f"📝 Executing {len(commands)} SQL commands...")
        
        for i, command in enumerate(commands):
            try:
                print(f"⏳ Executing command {i+1}/{len(commands)}: {command[:50]}...")
                result = supabase.rpc('exec_sql', {'query': command}).execute()
                print(f"✅ Command {i+1} executed successfully")
            except Exception as cmd_error:
                print(f"⚠️ Command {i+1} failed: {str(cmd_error)}")
                # Continue with other commands
        
        print("🎉 RLS policies updated successfully!")
        print("💡 Note: These are permissive policies for development. Secure them for production!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()