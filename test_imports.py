#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    try:
        print("Testing imports...")
        
        from services.token import create_token, verify_stored_token, deactivate_token
        print("✓ Token service imports successful")
        
        from services.auth import get_current_user, require_roles
        print("✓ Auth service imports successful")
        
        from backend.main import app
        print("✓ Main app import successful")
        
        print("All imports successful!")
        return True
        
    except Exception as e:
        print(f"Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()
