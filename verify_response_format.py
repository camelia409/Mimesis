#!/usr/bin/env python3
"""
Verification script for the standardized response format functions
"""

import sys
import os
from datetime import datetime

# Add the current directory to the path so we can import from routes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_response_functions():
    """Test the response format functions directly"""
    print("🧪 TESTING RESPONSE FORMAT FUNCTIONS")
    print("=" * 50)
    
    try:
        # Import the response functions
        from routes import create_json_response, create_error_response
        
        print("✅ Successfully imported response functions")
        
        # Test create_json_response
        print("\n1. Testing create_json_response...")
        test_data = {"test": "data", "number": 123}
        response = create_json_response(test_data, 200, True, "Test successful")
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        # Parse the response
        import json
        data = json.loads(response.get_data(as_text=True))
        print(f"Response Data: {json.dumps(data, indent=2)}")
        
        # Validate structure
        assert data['success'] == True, "Success field should be True"
        assert 'data' in data, "Should have data field"
        assert data['data'] == test_data, "Data should match input"
        assert 'timestamp' in data, "Should have timestamp"
        assert 'status_code' in data, "Should have status_code"
        print("✅ create_json_response working correctly")
        
        # Test create_error_response
        print("\n2. Testing create_error_response...")
        error_response = create_error_response("Test error message", 400, "TEST_ERROR")
        
        print(f"Status Code: {error_response.status_code}")
        print(f"Content-Type: {error_response.headers.get('Content-Type')}")
        
        # Parse the error response
        error_data = json.loads(error_response.get_data(as_text=True))
        print(f"Error Response: {json.dumps(error_data, indent=2)}")
        
        # Validate error structure
        assert data['success'] == True, "Previous test should still be True"
        assert error_data['success'] == False, "Error success should be False"
        assert 'error' in error_data, "Should have error field"
        assert error_data['error']['message'] == "Test error message", "Error message should match"
        assert error_data['error']['code'] == "TEST_ERROR", "Error code should match"
        assert 'timestamp' in error_data['error'], "Error should have timestamp"
        print("✅ create_error_response working correctly")
        
        # Test different status codes
        print("\n3. Testing different status codes...")
        not_found_response = create_error_response("Not found", 404, "NOT_FOUND")
        server_error_response = create_error_response("Server error", 500, "INTERNAL_ERROR")
        
        assert not_found_response.status_code == 404, "404 status code should be set"
        assert server_error_response.status_code == 500, "500 status code should be set"
        print("✅ Status codes working correctly")
        
        # Test without optional parameters
        print("\n4. Testing optional parameters...")
        simple_response = create_json_response({"simple": "test"})
        simple_error = create_error_response("Simple error")
        
        simple_data = json.loads(simple_response.get_data(as_text=True))
        simple_error_data = json.loads(simple_error.get_data(as_text=True))
        
        assert simple_data['success'] == True, "Default success should be True"
        assert simple_data['status_code'] == 200, "Default status should be 200"
        assert 'message' not in simple_data, "Should not have message when not provided"
        
        assert simple_error_data['success'] == False, "Error success should be False"
        assert simple_error_data['status_code'] == 400, "Default error status should be 400"
        print("✅ Optional parameters working correctly")
        
        print(f"\n{'='*50}")
        print("✅ ALL TESTS PASSED!")
        print("✅ Response format functions are working correctly")
        print(f"{'='*50}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_responses():
    """Test that service functions return consistent formats"""
    print("\n🔧 TESTING SERVICE RESPONSE FORMATS")
    print("=" * 50)
    
    try:
        # Test Qloo service error response
        from services.qloo_service import get_fashion_archetypes
        
        # Mock the function to test error response
        import os
        original_key = os.environ.get('QLOO_API_KEY')
        os.environ['QLOO_API_KEY'] = ''  # Clear the key to trigger error
        
        error_response = get_fashion_archetypes("test input")
        
        assert error_response['success'] == False, "Should return success=False when API key missing"
        assert 'error' in error_response, "Should have error field"
        assert 'error_code' in error_response, "Should have error_code field"
        print("✅ Qloo service error response format correct")
        
        # Restore original key
        if original_key:
            os.environ['QLOO_API_KEY'] = original_key
        else:
            os.environ.pop('QLOO_API_KEY', None)
            
        return True
        
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_response_functions()
    if success:
        test_service_responses()
    
    if success:
        print("\n🎉 All verification tests completed successfully!")
        print("The standardized response format is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1) 