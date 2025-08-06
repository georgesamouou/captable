#!/usr/bin/env python3
"""
Database setup script for Cap Table Management System
"""
import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Cap Table Management System - Database Setup")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found.")
        print("   Please create a .env file based on env.example")
        print("   Continuing with default configuration...")
    
    # Check if PostgreSQL is available
    print("🔍 Checking PostgreSQL connection...")
    database_url = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/cap_table_db")
    
    # Initialize Alembic if not already done
    if not os.path.exists('alembic/versions'):
        print("📁 Initializing Alembic...")
        if not run_command("alembic init alembic", "Initializing Alembic"):
            print("❌ Failed to initialize Alembic. Please check your setup.")
            return False
    
    # Create initial migration
    print("📝 Creating initial migration...")
    if not run_command("alembic revision --autogenerate -m 'Initial migration'", "Creating initial migration"):
        print("❌ Failed to create migration. Please check your database connection.")
        return False
    
    # Run migrations
    print("🔄 Running database migrations...")
    if not run_command("alembic upgrade head", "Running migrations"):
        print("❌ Failed to run migrations. Please check your database connection.")
        return False
    
    print("\n✅ Database setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Start the application: python start.py")
    print("   2. Access the API documentation: http://localhost:8000/docs")
    print("   3. Login with default admin: admin@company.com / admin123")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 