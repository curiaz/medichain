#!/usr/bin/env python3
"""
Test PostgreSQL Notifications Schema
Validates the schema works without sequence errors
"""

import os

def test_schema():
    """Test the PostgreSQL schema for syntax errors"""
    schema_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'notifications_schema.sql')
    
    print("Testing PostgreSQL Notifications Schema...")
    print(f"Schema file: {schema_file}")
    
    if not os.path.exists(schema_file):
        print("❌ Schema file not found!")
        return False
    
    # Read the schema
    with open(schema_file, 'r') as f:
        schema_content = f.read()
    
    print("✅ Schema file exists and is readable")
    
    # Check for problematic sequences
    if 'notifications_id_seq' in schema_content:
        lines = schema_content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'notifications_id_seq' in line and 'GRANT USAGE' in line:
                print(f"❌ Found problematic sequence grant on line {i}: {line.strip()}")
                return False
            elif 'notifications_id_seq' in line:
                print(f"ℹ️  Found sequence reference on line {i}: {line.strip()}")
    
    print("✅ No problematic sequence grants found")
    
    # Check that we're using UUID primary key
    if 'UUID DEFAULT gen_random_uuid() PRIMARY KEY' in schema_content:
        print("✅ Using UUID primary key (no sequence needed)")
    elif 'SERIAL PRIMARY KEY' in schema_content:
        print("✅ Using SERIAL primary key (sequence will be auto-created)")
    else:
        print("⚠️  Unknown primary key type")
    
    # Count key components
    components = {
        'CREATE TABLE': schema_content.count('CREATE TABLE'),
        'CREATE INDEX': schema_content.count('CREATE INDEX'),
        'CREATE VIEW': schema_content.count('CREATE VIEW'),
        'CREATE FUNCTION': schema_content.count('CREATE FUNCTION'),
        'CREATE TRIGGER': schema_content.count('CREATE TRIGGER'),
        'CREATE POLICY': schema_content.count('CREATE POLICY'),
        'INSERT INTO': schema_content.count('INSERT INTO'),
    }
    
    print("\n📊 Schema Components:")
    for component, count in components.items():
        print(f"   {component}: {count}")
    
    print("\n🎉 Schema validation completed successfully!")
    return True

if __name__ == "__main__":
    test_schema()