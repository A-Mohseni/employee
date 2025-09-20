#!/usr/bin/env python3
"""
Script to create the first super admin
Run this script once to bootstrap the admin system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_db
from utils.password_hash import hash_password
from datetime import datetime
from bson import ObjectId

def create_super_admin():
    """Create the first super admin"""
    db = get_db()
    admins = db["admins"]
    
    # Check if admin already exists
    if admins.count_documents({}) > 0:
        print("❌ Admin already exists!")
        print("Use the bootstrap-admin endpoint or login with existing admin credentials.")
        return False
    
    # Admin data
    admin_data = {
        "_id": ObjectId(),
        "employee_id": "00001",
        "full_name": "مدیر اصلی سیستم",
        "password_hash": hash_password("admin123!"),
        "role": "admin1",
        "status": "active",
        "phone": "09123456789",
        "email": "admin@company.com",
        "is_super_admin": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    try:
        result = admins.insert_one(admin_data)
        print("✅ Super admin created successfully!")
        print(f"   Admin ID: {result.inserted_id}")
        print(f"   Employee ID: {admin_data['employee_id']}")
        print(f"   Full Name: {admin_data['full_name']}")
        print(f"   Role: {admin_data['role']}")
        print(f"   Password: admin123!")
        print("\n⚠️  Please change the default password after first login!")
        return True
    except Exception as e:
        print(f"❌ Error creating super admin: {e}")
        return False

def create_default_admins():
    """Create default admin accounts"""
    db = get_db()
    admins = db["admins"]
    
    # Check if any admin exists
    if admins.count_documents({}) > 0:
        print("❌ Admins already exist!")
        return False
    
    # Default admins
    default_admins = [
        {
            "_id": ObjectId(),
            "employee_id": "00001",
            "full_name": "مدیر اصلی سیستم",
            "password_hash": hash_password("admin123!"),
            "role": "admin1",
            "status": "active",
            "phone": "09123456789",
            "email": "admin@company.com",
            "is_super_admin": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "employee_id": "00002",
            "full_name": "مدیر فرعی سیستم",
            "password_hash": hash_password("admin456!"),
            "role": "admin2",
            "status": "active",
            "phone": "09123456790",
            "email": "admin2@company.com",
            "is_super_admin": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    try:
        result = admins.insert_many(default_admins)
        print("✅ Default admins created successfully!")
        print(f"   Created {len(result.inserted_ids)} admins")
        print("\n📋 Admin Credentials:")
        print("   Admin 1 (Super):")
        print("     Employee ID: 00001")
        print("     Password: admin123!")
        print("   Admin 2:")
        print("     Employee ID: 00002")
        print("     Password: admin456!")
        print("\n⚠️  Please change the default passwords after first login!")
        return True
    except Exception as e:
        print(f"❌ Error creating default admins: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Employee Management System - Admin Setup")
    print("=" * 50)
    
    # Check if running in interactive mode
    import sys
    if sys.stdin.isatty():
        choice = input("Choose setup option:\n1. Create single super admin\n2. Create default admins (2 admins)\nEnter choice (1 or 2): ").strip()
    else:
        # Non-interactive mode - create single super admin by default
        choice = "1"
        print("Non-interactive mode detected. Creating single super admin...")
    
    if choice == "1":
        create_super_admin()
    elif choice == "2":
        create_default_admins()
    else:
        print("❌ Invalid choice. Please run the script again and choose 1 or 2.")
        sys.exit(1)
    
    print("\n🎉 Setup completed!")
    print("You can now start the application and login with admin credentials.")
