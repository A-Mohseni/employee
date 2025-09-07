#!/usr/bin/env python3

import asyncio
import sys
import os
from datetime import datetime, date

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """Test that all modules can be imported successfully"""
    print("🔍 Testing imports...")
    
    try:
        from app.core.config import settings
        print("✅ Config imported successfully")
        
        from app.core.security import create_access_token, get_password_hash, verify_password
        print("✅ Security module imported successfully")
        
        from app.core.auth import get_current_user, require_admin
        print("✅ Auth module imported successfully")
        
        from app.db.database import connect_to_mongo, close_mongo_connection
        print("✅ Database module imported successfully")
        
        from app.models.user import User, UserCreate, UserRole
        print("✅ User models imported successfully")
        
        from app.models.leave_request import LeaveRequest, LeaveRequestCreate, LeaveStatus
        print("✅ Leave request models imported successfully")
        
        from app.models.daily_report import DailyReport, DailyReportCreate
        print("✅ Daily report models imported successfully")
        
        from app.models.shopping_list import ShoppingList, ShoppingListCreate
        print("✅ Shopping list models imported successfully")
        
        from app.models.dashboard import DashboardResponse
        print("✅ Dashboard models imported successfully")
        
        from app.services.user_service import create_user, get_user_by_id
        print("✅ User service imported successfully")
        
        from app.services.leave_request_service import create_leave_request
        print("✅ Leave request service imported successfully")
        
        from app.services.daily_report_service import create_daily_report
        print("✅ Daily report service imported successfully")
        
        from app.services.shopping_list_service import create_shopping_list
        print("✅ Shopping list service imported successfully")
        
        from app.services.dashboard_service import get_dashboard_data
        print("✅ Dashboard service imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from app.db.database import connect_to_mongo, close_mongo_connection
        
        await connect_to_mongo()
        print("✅ Database connection successful")
        
        await close_mongo_connection()
        print("✅ Database connection closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

async def test_model_validation():
    """Test Pydantic model validation"""
    print("\n🔍 Testing model validation...")
    
    try:
        from app.models.user import UserCreate, UserRole
        from app.models.leave_request import LeaveRequestCreate
        from app.models.daily_report import DailyReportCreate
        from app.models.shopping_list import ShoppingListCreate, ShoppingItem
        
        # Test UserCreate
        user_data = UserCreate(
            name="Test User",
            email="test@example.com",
            role=UserRole.EMPLOYEE,
            department="IT",
            password="password123"
        )
        print("✅ UserCreate validation successful")
        
        # Test LeaveRequestCreate
        leave_data = LeaveRequestCreate(
            start_date=date.today(),
            end_date=date.today(),
            reason="Test leave request"
        )
        print("✅ LeaveRequestCreate validation successful")
        
        # Test DailyReportCreate
        report_data = DailyReportCreate(
            content="This is a test daily report content."
        )
        print("✅ DailyReportCreate validation successful")
        
        # Test ShoppingListCreate
        shopping_data = ShoppingListCreate(
            items=[
                ShoppingItem(name="Item 1", quantity=2),
                ShoppingItem(name="Item 2", quantity=1)
            ]
        )
        print("✅ ShoppingListCreate validation successful")
        
        print("🎉 All model validations successful!")
        return True
        
    except Exception as e:
        print(f"❌ Model validation error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_security_functions():
    """Test security functions"""
    print("\n🔍 Testing security functions...")
    
    try:
        from app.core.security import get_password_hash, verify_password, create_access_token
        
        # Test password hashing
        password = "testpassword123"
        hashed = get_password_hash(password)
        print("✅ Password hashing successful")
        
        # Test password verification
        is_valid = verify_password(password, hashed)
        if is_valid:
            print("✅ Password verification successful")
        else:
            print("❌ Password verification failed")
            return False
        
        # Test JWT token creation
        token_data = {"user_id": "test123", "role": "employee"}
        token = create_access_token(token_data)
        print("✅ JWT token creation successful")
        
        print("🎉 All security functions working!")
        return True
        
    except Exception as e:
        print(f"❌ Security function error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Employee Management System Setup Test\n")
    
    tests = [
        test_imports(),
        test_database_connection(),
        test_model_validation(),
        test_security_functions()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    print("\n" + "="*50)
    print("📊 Test Results Summary:")
    print("="*50)
    
    test_names = [
        "Import Tests",
        "Database Connection",
        "Model Validation", 
        "Security Functions"
    ]
    
    all_passed = True
    for i, (name, result) in enumerate(zip(test_names, results)):
        if isinstance(result, Exception):
            print(f"❌ {name}: Failed with exception")
            all_passed = False
        elif result:
            print(f"✅ {name}: Passed")
        else:
            print(f"❌ {name}: Failed")
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All tests passed! The system is ready to use.")
        print("\n📝 Next steps:")
        print("1. Create a .env file with your configuration")
        print("2. Start MongoDB")
        print("3. Run: python -m uvicorn app.main:app --reload")
        print("4. Visit: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
