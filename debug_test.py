#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

def test_simple():
    print("Testing simple requests...")
    
    # Test basic endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"GET / - Status: {response.status_code}, Response: {response.json()}")
    except Exception as e:
        print(f"GET / - Error: {e}")
    
    # Test auth login
    try:
        data = {"employee_id": "100", "password": "admin123"}
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        print(f"POST /auth/login - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"POST /auth/login - Error: {e}")
    
    # Test employees list
    try:
        response = requests.get(f"{BASE_URL}/employees/list")
        print(f"GET /employees/list - Status: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"Found {len(users)} users")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"GET /employees/list - Error: {e}")

if __name__ == "__main__":
    test_simple()
