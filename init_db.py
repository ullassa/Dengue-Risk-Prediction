#!/usr/bin/env python3
"""
Database initialization script for Dengue Detection System
This script helps set up and manage the database (SQLite or PostgreSQL)
"""

import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, History
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize the database with tables"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Get admin credentials from environment variables
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@dengue.com')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            
            # Check if admin user exists
            admin_user = User.query.filter_by(email=admin_email).first()
            if not admin_user:
                # Create admin user with environment variables
                admin_user = User(
                    name='Admin User',
                    email=admin_email,
                    password_hash=generate_password_hash(admin_password),
                    is_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Admin user created!")
                print(f"   Email: {admin_email}")
                print("   Password: [HIDDEN]")
                print("   Role: Administrator")
            else:
                # Make sure existing admin user has admin privileges
                if not admin_user.is_admin:
                    admin_user.is_admin = True
                    db.session.commit()
                    print("✅ Admin privileges granted to existing admin user")
                print("ℹ️  Admin user already exists")
                
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        return False
    
    return True

def check_database_connection():
    """Check if database connection is working"""
    try:
        with app.app_context():
            # Get database info
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            if 'postgresql' in db_uri:
                db_type = "PostgreSQL"
            else:
                db_type = "SQLite"
            
            print(f"📊 Database Type: {db_type}")
            print(f"🔗 Connection URI: {db_uri}")
            
            # Test connection by counting users
            user_count = User.query.count()
            history_count = History.query.count()
            
            print(f"👥 Users in database: {user_count}")
            print(f"📈 History records: {history_count}")
            
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    try:
        with app.app_context():
            # Check if sample user exists
            sample_user = User.query.filter_by(email='user@example.com').first()
            if not sample_user:
                # Create sample user
                sample_user = User(
                    name='Sample User',
                    email='user@example.com',
                    password_hash=generate_password_hash('password123'),
                    is_admin=False
                )
                db.session.add(sample_user)
                db.session.commit()
                
                # Create sample history entries
                sample_histories = [
                    History(
                        user_id=sample_user.id,
                        city_name='Bangalore',
                        risk_level='Medium',
                        temperature=28.5,
                        humidity=75.0,
                        date_time=datetime.now()
                    ),
                    History(
                        user_id=sample_user.id,
                        city_name='Mumbai',
                        risk_level='High',
                        temperature=32.0,
                        humidity=85.0,
                        date_time=datetime.now()
                    )
                ]
                
                for history in sample_histories:
                    db.session.add(history)
                
                db.session.commit()
                print("✅ Sample data created!")
                print("   Sample User: user@example.com / password123")
            else:
                print("ℹ️  Sample data already exists")
                
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")

def main():
    """Main function"""
    print("🩺 Dengue Detection System - Database Setup")
    print("=" * 50)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️  python-dotenv not available, using system environment")
    
    # Check database connection
    print("\n📊 Checking database connection...")
    if not check_database_connection():
        print("\n❌ Database connection failed!")
        print("Please check your database configuration in .env file")
        return
    
    # Initialize database
    print("\n🔧 Initializing database...")
    if init_database():
        print("\n✅ Database initialized successfully!")
    else:
        print("\n❌ Failed to initialize database!")
        return
    
    # Create sample data
    print("\n📝 Creating sample data...")
    create_sample_data()
    
    print("\n✅ Database setup complete!")
    print("\nYou can now:")
    print("1. Start the Flask application: python app.py")
    print("2. Visit http://localhost:5000/admin for database management")
    print("3. Login with admin@dengue.com / admin123")

if __name__ == '__main__':
    main()
