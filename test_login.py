import requests
import json

BASE_URL = "http://localhost:8001"

def test_login():
    print("🔐 Testing login...\n")
    
    test_credentials = [
        {"employee_id": 100, "password": "admin123"},
        {"employee_id": 100, "password": "password"},
        {"employee_id": 100, "password": "123456"},
        {"employee_id": 1, "password": "admin123"},
        {"employee_id": 101, "password": "user123"}
    ]
    
    for i, creds in enumerate(test_credentials, 1):
        print(f"Test {i}: employee_id={creds['employee_id']}, password={creds['password']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json=creds,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Login successful!")
                print(f"   👤 Role: {result['role']}")
                print(f"   🔑 Token: {result['access_token'][:50]}...")
                print(f"   🆔 User ID: {result['user_id']}")
                return result['access_token']
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
        
        print("-" * 30)
    
    return None

if __name__ == "__main__":
    token = test_login()
    if token:
        print(f"\n🎉 Login successful! Token: {token}")
    else:
        print("\n❌ No successful login found.")
