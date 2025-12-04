#!/usr/bin/env python3
"""
Database migration script to add user profile functionality
This script adds the profile columns to existing databases
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_sqlite_database():
    """Add profile columns to existing SQLite database"""
    db_paths = ['dengue_users.db', 'instance/dengue_users.db']
    
    # Find the actual database file
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("✅ No existing database found - will create new one with profile support")
        return True
    
    print(f"📍 Found database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(user)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # Profile columns to add
        profile_columns = [
            ('is_admin', 'BOOLEAN DEFAULT FALSE'),
            ('age', 'INTEGER'),
            ('gender', 'VARCHAR(20)'),
            ('phone', 'VARCHAR(20)'),
            ('city', 'VARCHAR(100)'),
            ('state', 'VARCHAR(100) DEFAULT "Karnataka"'),
            ('occupation', 'VARCHAR(100)'),
            ('medical_conditions', 'TEXT'),
            ('emergency_contact', 'TEXT'),
            ('emergency_phone', 'VARCHAR(20)'),
            ('notification_preferences', 'TEXT'),
            ('profile_visibility', 'BOOLEAN DEFAULT TRUE'),
            ('date_joined', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ('last_updated', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ('total_predictions', 'INTEGER DEFAULT 0'),
            ('risk_assessments', 'INTEGER DEFAULT 0'),
            ('alerts_received', 'INTEGER DEFAULT 0'),
            ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP')
        ]
        
        # Add missing columns
        columns_added = 0
        for col_name, col_definition in profile_columns:
            if col_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE user ADD COLUMN {col_name} {col_definition}")
                    print(f"✅ Added column: {col_name}")
                    columns_added += 1
                except sqlite3.Error as e:
                    print(f"❌ Error adding column {col_name}: {e}")
        
        if columns_added == 0:
            print("✅ Database already has complete profile support")
        else:
            print(f"✅ Added {columns_added} profile columns")
        
        # Update existing users with default values
        cursor.execute("UPDATE user SET date_joined = CURRENT_TIMESTAMP WHERE date_joined IS NULL")
        cursor.execute("UPDATE user SET last_updated = CURRENT_TIMESTAMP WHERE last_updated IS NULL")
        cursor.execute("UPDATE user SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        cursor.execute("UPDATE user SET state = 'Karnataka' WHERE state IS NULL")
        
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
