#!/usr/bin/env python3
"""
Test script to verify the standardized API response format
"""

import requests
import json
import sys
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5000"  # Change this to your server URL
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def print_test_header(test_name):
    """Print a formatted test header"""
    print(f"\n{'='*60}")
    print(f"TESTING: {test_name}")
    print(f"{'='*60}")

def print_response(response, test_name):
    """Print formatted response for testing"""
    print(f"\n{test_name} Response:")
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'Not set')}")
    print(f"Response Body:")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
        
        # Validate response format
        if 'success' in data:
            print(f"✅ Success field present: {data['success']}")
        else:
            print("❌ Missing 'success' field")
            
        if 'timestamp' in data:
            print(f"✅ Timestamp present: {data['timestamp']}")
        else:
            print("❌ Missing 'timestamp' field")
            
        if data.get('success'):
            if 'data' in data:
                print("✅ Success response has 'data' field")
            else:
                print("❌ Success response missing 'data' field")
        else:
            if 'error' in data:
                print("✅ Error response has 'error' field")
                if 'message' in data['error'] and 'code' in data['error']:
                    print("✅ Error has both message and code")
                else:
                    print("❌ Error missing message or code")
            else:
                print("❌ Error response missing 'error' field")
                
    except json.JSONDecodeError:
        print("❌ Response is not valid JSON")
        print(response.text)

def test_popular_inputs():
    """Test the popular inputs endpoint with JSON format"""
    print_test_header("Popular Inputs (JSON Format)")
    
    # Test with Accept header
    response1 = requests.get(f"{BASE_URL}/popular", 
                           headers={'Accept': 'application/json'})
    print_response(response1, "With Accept Header")
    
    # Test with format parameter
    response2 = requests.get(f"{BASE_URL}/popular?format=json")
    print_response(response2, "With Format Parameter")
    
    # Test without JSON format (should return HTML)
    response3 = requests.get(f"{BASE_URL}/popular")
    print(f"\nHTML Response Status: {response3.status_code}")
    print(f"Content-Type: {response3.headers.get('Content-Type', 'Not set')}")
    if 'text/html' in response3.headers.get('Content-Type', ''):
        print("✅ HTML response correctly returned")
    else:
        print("❌ Expected HTML response")

def test_analytics():
    """Test the analytics endpoint with JSON format"""
    print_test_header("Analytics (JSON Format)")
    
    # Test with Accept header
    response = requests.get(f"{BASE_URL}/analytics", 
                          headers={'Accept': 'application/json'})
    print_response(response, "Analytics JSON Response")

def test_chat_endpoint():
    """Test the chat endpoint with standardized response format"""
    print_test_header("Chat Endpoint")
    
    # Test with missing message
    response1 = requests.post(f"{BASE_URL}/chat", 
                            data={'style_request_id': '123'})
    print_response(response1, "Missing Message Error")
    
    # Test with valid message
    response2 = requests.post(f"{BASE_URL}/chat", 
                            data={
                                'chat_input': 'What shoes would work with this style?',
                                'style_request_id': '123'
                            })
    print_response(response2, "Valid Chat Request")

def test_feedback_endpoint():
    """Test the feedback endpoint with standardized response format"""
    print_test_header("Feedback Endpoint")
    
    # Test with missing request ID
    response1 = requests.post(f"{BASE_URL}/feedback", 
                            data={'rating': '5', 'feedback': 'Great!'})
    print_response(response1, "Missing Request ID Error")
    
    # Test with invalid rating
    response2 = requests.post(f"{BASE_URL}/feedback", 
                            data={'request_id': '123', 'rating': '6', 'feedback': 'Great!'})
    print_response(response2, "Invalid Rating Error")
    
    # Test with valid feedback
    response3 = requests.post(f"{BASE_URL}/feedback", 
                            data={'request_id': '123', 'rating': '5', 'feedback': 'Great recommendations!'})
    print_response(response3, "Valid Feedback")

def test_error_handlers():
    """Test error handlers return standardized format"""
    print_test_header("Error Handlers")
    
    # Test 404 error
    response1 = requests.get(f"{BASE_URL}/nonexistent-endpoint", 
                           headers={'Accept': 'application/json'})
    print_response(response1, "404 Error")

def test_recommendations_json():
    """Test the recommendations endpoint with JSON format"""
    print_test_header("Recommendations (JSON Format)")
    
    # Note: This would require authentication and a valid session
    # For testing purposes, we'll just check the endpoint structure
    print("Note: Recommendations endpoint requires authentication")
    print("To test this endpoint, you need to:")
    print("1. Register/login first")
    print("2. Send POST request with cultural_preferences")
    print("3. Include Accept: application/json header")

def run_all_tests():
    """Run all tests"""
    print("🧪 MIMESIS API RESPONSE FORMAT TESTING")
    print(f"Testing against: {BASE_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    try:
        test_popular_inputs()
        test_analytics()
        test_chat_endpoint()
        test_feedback_endpoint()
        test_error_handlers()
        test_recommendations_json()
        
        print(f"\n{'='*60}")
        print("✅ ALL TESTS COMPLETED")
        print(f"{'='*60}")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Could not connect to {BASE_URL}")
        print("Make sure the Flask server is running with: python app.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests() 