import requests
import json
from utils.password_hash import hash_password

BASE_URL = "http://localhost:8001"

def test_api_workflow():
    print("🚀 Starting API tests...\n")
    
    print("1️⃣ Login with existing admin:")
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
            print(f"✅ Login successful: {login_result['role']}")
            print(f"🔑 New token: {login_result['access_token']}")
            current_token = login_result['access_token']
        else:
            print(f"❌ Login error: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    print("\n" + "="*50 + "\n")
    
    print("2️⃣ Get all users:")
    
    try:
        response = requests.get(
            f"{BASE_URL}/employees/",
            headers={"Authorization": f"Bearer {current_token}"}
        )
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Number of users: {len(users)}")
            for user in users:
                print(f"   👤 {user['full_name']} - {user['role']}")
        else:
            print(f"❌ Error getting users: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    print("3️⃣ Create new user:")
    new_user_data = {
        "employee_id": 101,
        "full_name": "New Employee",
        "role": "employee",
        "status": "active",
        "password_hash": hash_password("user123")
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/employees/",
            json=new_user_data,
            headers={
                "Authorization": f"Bearer {current_token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 201:
            new_user_result = response.json()
            print(f"✅ New user created: {new_user_result['full_name']}")
            print(f"🔑 User token: {new_user_result['access_token']}")
        else:
            print(f"❌ Error creating user: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    print("4️⃣ Test JWT verification:")
    
    try:
        from utils.jwt import verify_token, TokenError
        
        result = verify_token(current_token)
        if isinstance(result, TokenError):
            print(f"❌ Token error: {result.value}")
        else:
            print(f"✅ Token is valid")
            print(f"   👤 User ID: {result.get('user_id')}")
            print(f"   🎭 Role: {result.get('role')}")
            print(f"   ⏰ Expires: {result.get('exp')}")
            
    except Exception as e:
        print(f"❌ JWT test error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    print("5️⃣ Logout:")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/logout",
            headers={"Authorization": f"Bearer {current_token}"}
        )
        
        if response.status_code == 200:
            print("✅ Logout successful")
        else:
            print(f"❌ Logout error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    print("\n🎉 API tests completed!")

if __name__ == "__main__":
    test_api_workflow()
