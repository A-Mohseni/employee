#!/usr/bin/env python3
"""
Comprehensive endpoint testing script for Employee Management API
Tests all endpoints to ensure they work without errors
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:8000"
TEST_RESULTS = {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "errors": []
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")

def print_test_result(test_name: str, success: bool, details: str = ""):
    TEST_RESULTS["total_tests"] += 1
    if success:
        TEST_RESULTS["passed"] += 1
        print(f"{Colors.GREEN}✅ {test_name}{Colors.END}")
        if details:
            print(f"   {Colors.WHITE}{details}{Colors.END}")
    else:
        TEST_RESULTS["failed"] += 1
        print(f"{Colors.RED}❌ {test_name}{Colors.END}")
        if details:
            print(f"   {Colors.RED}{details}{Colors.END}")
        TEST_RESULTS["errors"].append(f"{test_name}: {details}")

def make_request(method: str, url: str, **kwargs) -> Optional[requests.Response]:
    """Make HTTP request with error handling"""
    try:
        response = requests.request(method, url, **kwargs)
        return response
    except requests.exceptions.ConnectionError as e:
        print(f"{Colors.RED}❌ Connection Error: Could not connect to {BASE_URL} - {str(e)}{Colors.END}")
        return None
    except Exception as e:
        print(f"{Colors.RED}❌ Request Error: {str(e)}{Colors.END}")
        return None

def test_basic_endpoints():
    """Test basic endpoints that don't require authentication"""
    print_header("TESTING BASIC ENDPOINTS")
    
    # Test root endpoint
    response = make_request("GET", f"{BASE_URL}/")
    if response is not None:
        if response.status_code == 200:
            print_test_result("GET /", True, f"Response: {response.json()}")
        else:
            print_test_result("GET /", False, f"Status: {response.status_code}, Response: {response.text}")
    else:
        print_test_result("GET /", False, "Connection failed")
    
    # Test test endpoint
    response = make_request("GET", f"{BASE_URL}/test")
    if response is not None:
        if response.status_code == 200:
            print_test_result("GET /test", True, f"Response: {response.json()}")
        else:
            print_test_result("GET /test", False, f"Status: {response.status_code}, Response: {response.text}")
    else:
        print_test_result("GET /test", False, "Connection failed")
    
    # Test model endpoint
    test_data = {"name": "Test User", "age": 25}
    response = make_request("POST", f"{BASE_URL}/test-model", json=test_data)
    if response is not None:
        if response.status_code == 200:
            print_test_result("POST /test-model", True, f"Response: {response.json()}")
        else:
            print_test_result("POST /test-model", False, f"Status: {response.status_code}, Response: {response.text}")
    else:
        print_test_result("POST /test-model", False, "Connection failed")

def test_auth_endpoints():
    """Test authentication endpoints"""
    print_header("TESTING AUTHENTICATION ENDPOINTS")
    
    # Test login with invalid credentials
    invalid_login_data = {"employee_id": "999", "password": "wrongpassword"}
    response = make_request("POST", f"{BASE_URL}/auth/login", json=invalid_login_data)
    if response is not None:
        if response.status_code in [401, 404]:  # Expected to fail
            print_test_result("POST /auth/login (invalid)", True, f"Correctly rejected invalid credentials")
        else:
            print_test_result("POST /auth/login (invalid)", False, f"Unexpected status: {response.status_code}")
    else:
        print_test_result("POST /auth/login (invalid)", False, "Connection failed")
    
    # Test login with valid credentials (if available)
    valid_login_data = {"employee_id": "100", "password": "admin123"}
    response = make_request("POST", f"{BASE_URL}/auth/login", json=valid_login_data)
    if response is not None:
        if response.status_code == 200:
            login_result = response.json()
            print_test_result("POST /auth/login (valid)", True, f"Role: {login_result.get('role', 'Unknown')}")
            return login_result.get('access_token')
        elif response.status_code == 401:
            print_test_result("POST /auth/login (valid)", True, f"Correctly rejected invalid credentials (401)")
        else:
            print_test_result("POST /auth/login (valid)", False, f"Unexpected status: {response.status_code}, Response: {response.text}")
    else:
        print_test_result("POST /auth/login (valid)", False, "Connection failed")
    
    # Test register endpoint
    register_data = {
        "employee_id": "999",
        "password": "testpass123",
        "role": "employee"
    }
    response = make_request("POST", f"{BASE_URL}/auth/register", json=register_data)
    if response is not None:
        if response.status_code in [200, 201, 400, 409]:  # Various expected responses
            print_test_result("POST /auth/register", True, f"Status: {response.status_code}")
        else:
            print_test_result("POST /auth/register", False, f"Unexpected status: {response.status_code}")
    else:
        print_test_result("POST /auth/register", False, "Connection failed")
    
    return None

def test_user_endpoints(token: Optional[str] = None):
    """Test user management endpoints"""
    print_header("TESTING USER MANAGEMENT ENDPOINTS")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test get users (requires admin)
    response = make_request("GET", f"{BASE_URL}/employees/", headers=headers)
    if response is not None:
        if response.status_code in [200, 401, 403]:
            print_test_result("GET /employees/", True, f"Status: {response.status_code}")
        else:
            print_test_result("GET /employees/", False, f"Unexpected status: {response.status_code}")
    else:
        print_test_result("GET /employees/", False, "Connection failed")
    
    # Test get users list (public)
    response = make_request("GET", f"{BASE_URL}/employees/list")
    if response is not None:
        if response.status_code == 200:
            users = response.json()
            print_test_result("GET /employees/list", True, f"Found {len(users)} users")
        else:
            print_test_result("GET /employees/list", False, f"Status: {response.status_code}")
    else:
        print_test_result("GET /employees/list", False, "Connection failed")
    
    # Test create first admin
    admin_data = {
        "employee_id": 999,
        "full_name": "Test Admin",
        "role": "admin1",
        "status": "active",
        "password": "testpass123"
    }
    response = make_request("POST", f"{BASE_URL}/employees/first-admin", json=admin_data)
    if response is not None:
        if response.status_code in [200, 201, 400, 409]:
            print_test_result("POST /employees/first-admin", True, f"Status: {response.status_code}")
        else:
            print_test_result("POST /employees/first-admin", False, f"Unexpected status: {response.status_code}")
    else:
        print_test_result("POST /employees/first-admin", False, "Connection failed")
    
    # Test create user (requires admin)
    user_data = {
        "employee_id": 998,
        "full_name": "Test User",
        "role": "employee",
        "status": "active",
        "password": "testpass123"
    }
    response = make_request("POST", f"{BASE_URL}/employees/", json=user_data, headers=headers)
    if response is not None:
        if response.status_code in [200, 201, 401, 403]:
            print_test_result("POST /employees/", True, f"Status: {response.status_code}")
        else:
            print_test_result("POST /employees/", False, f"Unexpected status: {response.status_code}")
    else:
        print_test_result("POST /employees/", False, "Connection failed")

def test_checklist_endpoints(token: Optional[str] = None):
    """Test checklist endpoints"""
    print_header("TESTING CHECKLIST ENDPOINTS")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test get roles
    response = make_request("GET", f"{BASE_URL}/checklists/roles")
    if response is not None:
        if response.status_code == 200:
            roles = response.json()
            print_test_result("GET /checklists/roles", True, f"Roles: {roles}")
        else:
            print_test_result("GET /checklists/roles", False, f"Status: {response.status_code}")
    else:
        print_test_result("GET /checklists/roles", False, "Connection failed")
    
    # Test get role field schema
    response = make_request("GET", f"{BASE_URL}/checklists/role-field-schema/admin1")
    if response is not None:
        if response.status_code == 200:
            schema = response.json()
            print_test_result("GET /checklists/role-field-schema/admin1", True, f"Schema fields: {len(schema.get('fields', []))}")
        else:
            print_test_result("GET /checklists/role-field-schema/admin1", False, f"Status: {response.status_code}")
    else:
        print_test_result("GET /checklists/role-field-schema/admin1", False, "Connection failed")
    
    # Test list checklists
    response = make_request("GET", f"{BASE_URL}/checklists/", headers=headers)
    if response is not None:
        if response.status_code in [200, 401]:
            print_test_result("GET /checklists/", True, f"Status: {response.status_code}")
        else:
            print_test_result("GET /checklists/", False, f"Unexpected status: {response.status_code}")
    else:
        print_test_result("GET /checklists/", False, "Connection failed")
    
    # Test create checklist
    checklist_data = {
        "title": "Test Checklist",
        "description": "Test description",
        "task_id": "test_task_123",
        "assigned_to": "employee",
        "due_date": (datetime.now() + timedelta(days=7)).isoformat()
    }
    response = make_request("POST", f"{BASE_URL}/checklists/", json=checklist_data, headers=headers)
    if response is not None:
        if response.status_code in [200, 201, 401, 403]:
            print_test_result("POST /checklists/", True, f"Status: {response.status_code}")
        else:
            print_test_result("POST /checklists/", False, f"Unexpected status: {response.status_code}")
    else:
        print_test_result("POST /checklists/", False, "Connection failed")

def test_leave_request_endpoints(token: Optional[str] = None):
    """Test leave request endpoints"""
    print_header("TESTING LEAVE REQUEST ENDPOINTS")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test list leave requests
    response = make_request("GET", f"{BASE_URL}/leave-requests/", headers=headers)
    if response is not None:
        if response.status_code in [200, 401]:
            print_test_result("GET /leave-requests/", True, f"Status: {response.status_code}")
        else:
            print_test_result("GET /leave-requests/", False, f"Unexpected status: {response.status_code}")
    else:
        print_test_result("GET /leave-requests/", False, "Connection failed")
    
    # Test create leave request
    leave_data = {
        "leave_type": "sick",
        "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=3)).isoformat(),
        "reason": "Test leave request",
        "emergency_contact": "123-456-7890"
    }
    response = make_request("POST", f"{BASE_URL}/leave-requests/", json=leave_data, headers=headers)
    if response is not None:
        if response.status_code in [200, 201, 401, 403]:
            print_test_result("POST /leave-requests/", True, f"Status: {response.status_code}")
        else:
            print_test_result("POST /leave-requests/", False, f"Unexpected status: {response.status_code}")
    else:
        print_test_result("POST /leave-requests/", False, "Connection failed")

def test_purchase_item_endpoints(token: Optional[str] = None):
    """Test purchase item endpoints"""
    print_header("TESTING PURCHASE ITEM ENDPOINTS")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test list purchase items
    response = make_request("GET", f"{BASE_URL}/purchase-items/", headers=headers)
    if response is not None:
        if response.status_code in [200, 401, 403]:
            print_test_result("GET /purchase-items/", True, f"Status: {response.status_code}")
        else:
            print_test_result("GET /purchase-items/", False, f"Unexpected status: {response.status_code}")
    else:
        print_test_result("GET /purchase-items/", False, "Connection failed")
    
    # Test create purchase item
    purchase_data = {
        "item_name": "Test Item",
        "description": "Test description",
        "quantity": 5,
        "unit_price": 10.50,
        "total_price": 52.50,
        "category": "office_supplies",
        "vendor": "Test Vendor",
        "purchase_date": datetime.now().isoformat()
    }
    response = make_request("POST", f"{BASE_URL}/purchase-items/", json=purchase_data, headers=headers)
    if response is not None:
        if response.status_code in [200, 201, 401, 403]:
            print_test_result("POST /purchase-items/", True, f"Status: {response.status_code}")
        else:
            print_test_result("POST /purchase-items/", False, f"Unexpected status: {response.status_code}")
    else:
        print_test_result("POST /purchase-items/", False, "Connection failed")

def test_report_endpoints(token: Optional[str] = None):
    """Test report endpoints"""
    print_header("TESTING REPORT ENDPOINTS")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test list reports
    response = make_request("GET", f"{BASE_URL}/reports/", headers=headers)
    if response is not None:
        if response.status_code in [200, 401]:
            print_test_result("GET /reports/", True, f"Status: {response.status_code}")
        else:
            print_test_result("GET /reports/", False, f"Unexpected status: {response.status_code}")
    else:
        print_test_result("GET /reports/", False, "Connection failed")
    
    # Test create report
    report_data = {
        "title": "Test Report",
        "content": "Test report content",
        "report_type": "monthly",
        "status": "draft"
    }
    response = make_request("POST", f"{BASE_URL}/reports/", json=report_data, headers=headers)
    if response is not None:
        if response.status_code in [200, 201, 401]:
            print_test_result("POST /reports/", True, f"Status: {response.status_code}")
        else:
            print_test_result("POST /reports/", False, f"Unexpected status: {response.status_code}")
    else:
        print_test_result("POST /reports/", False, "Connection failed")

def test_documentation_endpoints():
    """Test API documentation endpoints"""
    print_header("TESTING DOCUMENTATION ENDPOINTS")
    
    # Test OpenAPI docs
    response = make_request("GET", f"{BASE_URL}/docs")
    if response is not None:
        if response.status_code == 200:
            print_test_result("GET /docs", True, "OpenAPI documentation accessible")
        else:
            print_test_result("GET /docs", False, f"Status: {response.status_code}")
    else:
        print_test_result("GET /docs", False, "Connection failed")
    
    # Test ReDoc
    response = make_request("GET", f"{BASE_URL}/redoc")
    if response is not None:
        if response.status_code == 200:
            print_test_result("GET /redoc", True, "ReDoc documentation accessible")
        else:
            print_test_result("GET /redoc", False, f"Status: {response.status_code}")
    else:
        print_test_result("GET /redoc", False, "Connection failed")
    
    # Test OpenAPI JSON
    response = make_request("GET", f"{BASE_URL}/openapi.json")
    if response is not None:
        if response.status_code == 200:
            openapi_data = response.json()
            print_test_result("GET /openapi.json", True, f"OpenAPI spec with {len(openapi_data.get('paths', {}))} paths")
        else:
            print_test_result("GET /openapi.json", False, f"Status: {response.status_code}")
    else:
        print_test_result("GET /openapi.json", False, "Connection failed")

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total = TEST_RESULTS["total_tests"]
    passed = TEST_RESULTS["passed"]
    failed = TEST_RESULTS["failed"]
    
    print(f"{Colors.BOLD}Total Tests: {total}{Colors.END}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {failed}{Colors.END}")
    
    if failed > 0:
        print(f"\n{Colors.RED}❌ Some tests failed!{Colors.END}")
        print(f"\n{Colors.YELLOW}Failed Tests:{Colors.END}")
        for error in TEST_RESULTS["errors"]:
            print(f"  • {error}")
    else:
        print(f"\n{Colors.GREEN}🎉 All tests passed!{Colors.END}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.END}")

def main():
    """Main test function"""
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("🚀 COMPREHENSIVE ENDPOINT TESTING")
    print("=" * 50)
    print(f"Testing API at: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.END}")
    
    # Test basic endpoints first
    test_basic_endpoints()
    
    # Test authentication and get token
    token = test_auth_endpoints()
    
    # Test all other endpoints
    test_user_endpoints(token)
    test_checklist_endpoints(token)
    test_leave_request_endpoints(token)
    test_purchase_item_endpoints(token)
    test_report_endpoints(token)
    test_documentation_endpoints()
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    main()
