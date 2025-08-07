#!/usr/bin/env python3
"""
Database migration script to add admin functionality
This script adds the is_admin column to existing databases
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_sqlite_database():
    """Add is_admin column to existing SQLite database"""
    db_paths = ['dengue_users.db', 'instance/dengue_users.db']
    
    # Find the actual database file
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("✅ No existing database found - will create new one with admin support")
        return True
    
    print(f"📍 Found database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if is_admin column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_admin' in columns:
            print("✅ Database already has admin support")
            conn.close()
            return True
        
        print("🔧 Adding admin support to existing database...")
        
        # Add is_admin column with default value False
        cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
        
        # Update any existing admin@dengue.com user to be admin
        cursor.execute("UPDATE user SET is_admin = TRUE WHERE email = ?", ('admin@dengue.com',))
        
        conn.commit()
        conn.close()
        
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

def main():
    """Main migration function"""
    print("🔧 Database Migration - Adding Admin Support")
    print("=" * 50)
    
    # Migrate SQLite database
    if migrate_sqlite_database():
        print("\n✅ Migration completed successfully!")
        print("You can now run init_db.py to set up admin users")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above")

if __name__ == '__main__':
    main()
