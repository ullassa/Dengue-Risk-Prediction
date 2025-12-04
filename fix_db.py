#!/usr/bin/env python3
"""
Quick database fix to add missing columns
"""

import sqlite3
import os
from datetime import datetime

# Find the database
db_path = 'instance/dengue_users.db'
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(user)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Existing columns: {columns}")
        
        # Add missing columns
        if 'date_joined' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN date_joined TEXT")
            print("Added date_joined column")
        
        if 'last_updated' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN last_updated TEXT")
            print("Added last_updated column")
        
        # Set default values for existing users
        cursor.execute("UPDATE user SET date_joined = ? WHERE date_joined IS NULL", (datetime.utcnow().isoformat(),))
        cursor.execute("UPDATE user SET last_updated = ? WHERE last_updated IS NULL", (datetime.utcnow().isoformat(),))
        
        conn.commit()
        conn.close()
        print("✅ Database updated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ Database not found")