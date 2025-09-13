#!/usr/bin/env python3
"""
Test script to demonstrate proper authentication flow for checklist endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_checklist_authentication():
    print("🔐 Testing Checklist Authentication Flow...\n")
    
    # Step 1: Create first admin (if not exists)
    print("1️⃣ Creating first admin user...")
    admin_data = {
        "employee_id": 100,
        "full_name": "Admin User",
        "role": "admin1",
        "status": "active",
        "password_hash": "admin123"  # This will be hashed by the service
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/employees/first-admin",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            admin_result = response.json()
            print(f"✅ Admin created successfully!")
            print(f"   👤 Name: {admin_result['full_name']}")
            print(f"   🔑 Token: {admin_result['access_token'][:50]}...")
            admin_token = admin_result['access_token']
        elif response.status_code == 400:
            print("ℹ️  Admin already exists, proceeding to login...")
            admin_token = None
        else:
            print(f"❌ Error creating admin: {response.text}")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Step 2: Login if admin creation didn't return token
    if not admin_token:
        print("\n2️⃣ Logging in with admin credentials...")
        login_data = {
            "employee_id": 100,
            "password": "admin123"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                login_result = response.json()
                print(f"✅ Login successful!")
                print(f"   👤 Role: {login_result['role']}")
                print(f"   🔑 Token: {login_result['access_token'][:50]}...")
                admin_token = login_result['access_token']
            else:
                print(f"❌ Login error: {response.text}")
                return
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return
    
    # Step 3: Test checklist creation with proper authentication
    print("\n3️⃣ Testing checklist creation with authentication...")
    checklist_data = {
        "title": "Test Checklist",
        "description": "This is a test checklist",
        "task_id": "task_123",
        "items": [
            {"name": "Item 1", "completed": False},
            {"name": "Item 2", "completed": False}
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/checklists/",
            json=checklist_data,
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 201:
            checklist_result = response.json()
            print(f"✅ Checklist created successfully!")
            print(f"   📋 Title: {checklist_result['title']}")
            print(f"   🆔 ID: {checklist_result['id']}")
        else:
            print(f"❌ Checklist creation error: {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Step 4: Test without authentication (should fail)
    print("\n4️⃣ Testing checklist creation without authentication (should fail)...")
    try:
        response = requests.post(
            f"{BASE_URL}/checklists/",
            json=checklist_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 401:
            print("✅ Correctly rejected - 401 Unauthorized")
        else:
            print(f"❌ Unexpected response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    print("\n🎉 Authentication flow test completed!")

if __name__ == "__main__":
    test_checklist_authentication()
