import requests
import json

BASE_URL = "http://localhost:8001"

def test_endpoints():
    print("🔍 Testing available endpoints...\n")
    
    endpoints = [
        "/docs",
        "/redoc", 
        "/openapi.json",
        "/employees/first-admin",
        "/auth/login"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    print("\n" + "="*50)
    print("📖 API Documentation:")
    print(f"Swagger UI: {BASE_URL}/docs")
    print(f"ReDoc: {BASE_URL}/redoc")

if __name__ == "__main__":
    test_endpoints()
