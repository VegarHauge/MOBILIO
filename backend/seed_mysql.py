#!/usr/bin/env python3
"""
MySQL Database Seeding Script

This script connects to the running MySQL database and seeds it with:
- Admin user
- 1000 test users (with realistic names)
- Products from CSV files in dataset/products/
- Realistic orders with user behavior profiles

Usage:
    python seed_mysql.py [--skip-orders] [--users N]

Options:
    --skip-orders    Skip order generation (only seed users and products)
    --users N        Number of users to create (default: 1000)

Requirements:
    - MySQL container must be running (docker compose up -d)
    - DATABASE_URL in .env must point to MySQL
"""

import sys
import os
import time
from sqlalchemy import text

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.session import SessionLocal, engine
from db.utils.seed_admin import create_admin_user
from db.utils.seed_users import seed_users
from db.utils.seed_products import seed_products_from_csv
from db.utils.seed_orders import seed_realistic_orders
from models.user import User
from models.product import Product
from models.order import Order
from core.config import settings

def wait_for_mysql(max_retries=10, retry_delay=2):
    """Wait for MySQL to be ready"""
    print("🔄 Waiting for MySQL to be ready...")
    
    for attempt in range(1, max_retries + 1):
        try:
            # Try to connect and execute a simple query
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ MySQL is ready!")
            return True
        except Exception as e:
            if attempt < max_retries:
                print(f"⏳ Attempt {attempt}/{max_retries} - MySQL not ready yet, waiting {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"❌ Failed to connect to MySQL after {max_retries} attempts")
                print(f"   Error: {str(e)}")
                return False
    
    return False

def check_database_status():
    """Check current database status"""
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        admin_count = db.query(User).filter(User.role == "admin").count()
        customer_count = db.query(User).filter(User.role == "customer").count()
        product_count = db.query(Product).count()
        order_count = db.query(Order).count()
        
        return {
            'users': user_count,
            'admins': admin_count,
            'customers': customer_count,
            'products': product_count,
            'orders': order_count,
            'is_empty': user_count == 0 and product_count == 0
        }
    finally:
        db.close()

def print_summary():
    """Print summary of database contents"""
    status = check_database_status()
    
    print("\n" + "=" * 60)
    print("📊 DATABASE SUMMARY")
    print("=" * 60)
    print(f"👥 Users: {status['users']}")
    print(f"   • Admins: {status['admins']}")
    print(f"   • Customers: {status['customers']}")
    print(f"📦 Products: {status['products']}")
    print(f"🛒 Orders: {status['orders']}")
    
    if status['admins'] > 0:
        print("\n🔑 ADMIN LOGIN:")
        print("   Email: admin@shopify.com")
        print("   Password: admin123")
    
    if status['customers'] > 0:
        print("\n🔑 TEST USER LOGIN (any of these):")
        print("   Password: password")
        print("   Examples:")
        db = SessionLocal()
        try:
            sample_users = db.query(User).filter(User.role == "customer").limit(3).all()
            for user in sample_users:
                print(f"   • {user.email}")
        finally:
            db.close()
    
    print("\n✅ Database ready!")
    print("=" * 60)

def main():
    """Main seeding function"""
    print("� MYSQL DATABASE SEEDING")
    print("=" * 60)
    print(f"Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'MySQL'}")
    print("=" * 60)
    
    # Parse command line arguments
    skip_orders = '--skip-orders' in sys.argv
    num_users = 1000
    
    for i, arg in enumerate(sys.argv):
        if arg == '--users' and i + 1 < len(sys.argv):
            try:
                num_users = int(sys.argv[i + 1])
            except ValueError:
                print(f"⚠️  Invalid user count: {sys.argv[i + 1]}, using default 1000")
    
    # Wait for MySQL to be ready
    if not wait_for_mysql():
        print("\n❌ Cannot proceed - MySQL is not ready")
        print("   Make sure MySQL container is running: docker compose up -d")
        sys.exit(1)
    
    # Check current database status
    status = check_database_status()
    
    print(f"\n📊 Current database status:")
    print(f"   Users: {status['users']} ({status['admins']} admins, {status['customers']} customers)")
    print(f"   Products: {status['products']}")
    print(f"   Orders: {status['orders']}")
    
    if not status['is_empty']:
        print("\n⚠️  Database already contains data!")
        print_summary()
        return
    
    try:
        # 1. Seed admin user
        print("\n" + "=" * 60)
        print("👤 STEP 1: SEEDING ADMIN USER")
        print("=" * 60)
        create_admin_user()
        
        # 2. Seed test users
        print("\n" + "=" * 60)
        print(f"👥 STEP 2: SEEDING {num_users} TEST USERS")
        print("=" * 60)
        seed_users(num_users)
        
        # 3. Seed products from CSV files
        print("\n" + "=" * 60)
        print("� STEP 3: SEEDING PRODUCTS FROM CSV")
        print("=" * 60)
        seed_products_from_csv()
        
        # 4. Seed orders (optional)
        if not skip_orders:
            print("\n" + "=" * 60)
            print("� STEP 4: SEEDING REALISTIC ORDERS")
            print("=" * 60)
            print("This will generate realistic orders based on user behavior profiles...")
            print("(This may take a few minutes)")
            seed_realistic_orders()
        else:
            print("\n⏭️  Skipping order generation (--skip-orders flag)")
        
        # Print final summary
        print("\n" + "=" * 60)
        print("✅ SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print_summary()
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
