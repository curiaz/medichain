#!/usr/bin/env python3
"""
Initialize Notifications Database
Creates the notifications database with proper schema
"""

import sqlite3
import os

def init_database():
    """Initialize the notifications database"""
    # Database paths
    backend_dir = os.path.dirname(__file__)
    db_path = os.path.join(backend_dir, 'notifications.db')
    schema_path = os.path.join(backend_dir, '..', 'database', 'notifications_sqlite_schema.sql')
    
    print(f"Initializing database at: {db_path}")
    print(f"Using schema from: {schema_path}")
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database")
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Read schema file
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            # Execute schema
            cursor.executescript(schema_sql)
            print("Schema executed successfully")
            
            # Verify tables were created
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Created tables: {[table[0] for table in tables]}")
            
            # Check sample data
            cursor.execute("SELECT COUNT(*) FROM notifications")
            count = cursor.fetchone()[0]
            print(f"Sample notifications inserted: {count}")
            
            conn.commit()
            print("Database initialization completed successfully!")
            
        else:
            print(f"Schema file not found at: {schema_path}")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    except Exception as e:
        print(f"Unexpected error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()