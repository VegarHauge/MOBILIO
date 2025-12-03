#!/usr/bin/env python3
"""
Admin User Seeding Script

This script creates an admin user in the database for administrative access.
The admin user can access admin-only endpoints and manage the system.

Usage:
    python seed_admin.py

Features:
- Creates a single admin user with secure password hashing
- Uses Argon2 password hashing for security
- Checks if admin already exists to avoid duplicates
- Provides default credentials that should be changed in production
"""

import sys
import os
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import from the backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import SessionLocal
from models.user import User
from services.auth_service import AuthService

def create_admin_user():
    """Create an admin user in the database"""
    db: Session = SessionLocal()
    
    try:
        # Admin user details - CHANGE THESE IN PRODUCTION!
        admin_email = "admin@mail.com"
        admin_name = "System Administrator"
        admin_password = "admin123"  # Simple password for development
        
        print("🔧 ADMIN USER SEEDING")
        print("=" * 50)
        
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if existing_admin:
            print(f"⚠️  Admin user already exists!")
            print(f"   Email: {existing_admin.email}")
            print(f"   Name: {existing_admin.name}")
            print(f"   Role: {existing_admin.role}")
            print(f"   ID: {existing_admin.id}")
            
            if existing_admin.role != "admin":
                print(f"\n🔄 Updating existing user to admin role...")
                existing_admin.role = "admin"
                db.commit()
                print(f"✅ User {existing_admin.email} is now an admin!")
            else:
                print(f"\n✅ Admin user is already set up correctly.")
                
            print(f"\n🔑 LOGIN CREDENTIALS:")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
            
            return existing_admin
        
        # Create new admin user
        print(f"👤 Creating admin user...")
        print(f"   Email: {admin_email}")
        print(f"   Name: {admin_name}")
        print(f"   Role: admin")
        
        # Hash the password using Argon2
        hashed_password = AuthService.get_password_hash(admin_password)
        
        # Create admin user
        admin_user = User(
            name=admin_name,
            email=admin_email,
            password=hashed_password,
            role="admin"
        )
        
        # Save to database
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"\n✅ ADMIN USER CREATED SUCCESSFULLY!")
        print(f"=" * 50)
        print(f"   ID: {admin_user.id}")
        print(f"   Name: {admin_user.name}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role}")
        
        print(f"\n🔑 LOGIN CREDENTIALS:")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        
        print(f"\n⚠️  SECURITY NOTICE:")
        print(f"   🔒 Change the default password in production!")
        print(f"   🔒 Use a strong password for real deployments!")
        
        print(f"\n🎯 ADMIN CAPABILITIES:")
        print(f"   • Access admin dashboard (/admin/dashboard)")
        print(f"   • Manage all products (CRUD operations)")
        print(f"   • View system statistics (/admin/stats)")
        print(f"   • Access all admin-only endpoints")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_admin_access():
    """Verify that the admin user can authenticate"""
    db: Session = SessionLocal()
    
    try:
        from services.auth_service import UserService
        
        admin_email = "admin@shopify.com"
        admin_password = "admin123"
        
        print(f"\n🔍 VERIFYING ADMIN ACCESS...")
        
        # Test authentication
        user = UserService.authenticate_user(db, admin_email, admin_password)
        
        if user and user.role == "admin":
            print(f"✅ Admin authentication successful!")
            print(f"   User ID: {user.id}")
            print(f"   Role: {user.role}")
            
            # Test JWT token creation
            from services.auth_service import AuthService
            token = AuthService.create_access_token(
                data={
                    "sub": str(user.id),
                    "name": user.name,
                    "email": user.email,
                    "role": user.role
                }
            )
            print(f"✅ JWT token generation successful!")
            print(f"   Token length: {len(token)} characters")
            
            return True
        else:
            print(f"❌ Admin authentication failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying admin access: {str(e)}")
        return False
    finally:
        db.close()

def main():
    """Main function"""
    print("🚀 STARTING ADMIN USER SETUP")
    print("=" * 60)
    
    try:
        # Create admin user
        admin_user = create_admin_user()
        
        # Verify admin can login
        if verify_admin_access():
            print(f"\n🎉 ADMIN SETUP COMPLETE!")
            print(f"=" * 60)
            print(f"Ready to use admin features!")
        else:
            print(f"\n⚠️  Admin created but verification failed.")
            
    except Exception as e:
        print(f"\n❌ SETUP FAILED: {str(e)}")
        print(f"\nPossible issues:")
        print(f"- Database connection problems")
        print(f"- Missing dependencies")
        print(f"- Database schema not created")

if __name__ == "__main__":
    main()