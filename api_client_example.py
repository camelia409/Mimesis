#!/usr/bin/env python3
"""
Example API client for Mimesis using the new standardized response format
"""

import requests
import json
from typing import Dict, Any, Optional

class MimesisAPIClient:
    """Client for interacting with the Mimesis API"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request and handle the standardized response format"""
        url = f"{self.base_url}{endpoint}"
        
        # Always request JSON responses
        headers = kwargs.get('headers', {})
        headers['Accept'] = 'application/json'
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            data = response.json()
            
            # Validate response format
            if 'success' not in data:
                raise ValueError("Response missing 'success' field")
                
            if data['success']:
                if 'data' not in data:
                    raise ValueError("Success response missing 'data' field")
                return data
            else:
                if 'error' not in data:
                    raise ValueError("Error response missing 'error' field")
                error_msg = data['error'].get('message', 'Unknown error')
                error_code = data['error'].get('code', 'UNKNOWN')
                raise Exception(f"{error_code}: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response")
    
    def get_popular_inputs(self) -> Dict[str, Any]:
        """Get popular cultural inputs"""
        return self._make_request('GET', '/popular')
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics data"""
        return self._make_request('GET', '/analytics')
    
    def chat_with_stylist(self, message: str, style_request_id: Optional[str] = None) -> Dict[str, Any]:
        """Chat with the AI stylist"""
        data = {'chat_input': message}
        if style_request_id:
            data['style_request_id'] = style_request_id
            
        return self._make_request('POST', '/chat', data=data)
    
    def submit_feedback(self, request_id: str, rating: Optional[int] = None, feedback: Optional[str] = None) -> Dict[str, Any]:
        """Submit feedback for a style request"""
        data = {'request_id': request_id}
        if rating is not None:
            data['rating'] = str(rating)
        if feedback:
            data['feedback'] = feedback
            
        return self._make_request('POST', '/feedback', data=data)
    
    def get_style_recommendations(self, cultural_preferences: str) -> Dict[str, Any]:
        """Get style recommendations (requires authentication)"""
        data = {'cultural_preferences': cultural_preferences}
        return self._make_request('POST', '/recommend', data=data)

def example_usage():
    """Example usage of the Mimesis API client"""
    client = MimesisAPIClient()
    
    print("🎨 Mimesis API Client Example")
    print("=" * 50)
    
    try:
        # Get popular inputs
        print("\n1. Getting popular cultural inputs...")
        popular_response = client.get_popular_inputs()
        popular_inputs = popular_response['data']['popular_inputs']
        print(f"Found {len(popular_inputs)} popular inputs")
        for i, item in enumerate(popular_inputs[:3], 1):
            print(f"  {i}. {item['cultural_input']} (used {item['request_count']} times)")
        
        # Chat with stylist
        print("\n2. Chatting with AI stylist...")
        chat_response = client.chat_with_stylist("What shoes would work with a vintage aesthetic?")
        ai_response = chat_response['data']['response']
        print(f"AI Stylist: {ai_response}")
        
        # Submit feedback
        print("\n3. Submitting feedback...")
        feedback_response = client.submit_feedback(
            request_id="123", 
            rating=5, 
            feedback="Great recommendations!"
        )
        print(f"Feedback submitted successfully: {feedback_response['message']}")
        
        # Get analytics
        print("\n4. Getting analytics...")
        analytics_response = client.get_analytics()
        summary = analytics_response['data']['summary_stats']
        print(f"Total requests: {summary['total_requests']}")
        print(f"Success rate: {summary['success_rate']}%")
        print(f"Average processing time: {summary['avg_processing_time']}ms")
        
        print("\n✅ All API calls completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def advanced_usage():
    """Advanced usage examples"""
    client = MimesisAPIClient()
    
    print("\n🔧 Advanced Usage Examples")
    print("=" * 50)
    
    # Example: Error handling
    print("\n1. Error handling example...")
    try:
        # This should fail with missing message
        client.chat_with_stylist("")
    except Exception as e:
        print(f"Expected error caught: {str(e)}")
    
    # Example: Working with response data
    print("\n2. Working with response data...")
    try:
        response = client.get_popular_inputs()
        
        # Access nested data
        data = response['data']
        popular_inputs = data['popular_inputs']
        total_count = data['total_count']
        
        # Process the data
        print(f"Total popular inputs: {total_count}")
        
        # Find highest rated input
        if popular_inputs:
            highest_rated = max(popular_inputs, 
                              key=lambda x: x.get('avg_rating', 0) or 0)
            print(f"Highest rated: {highest_rated['cultural_input']} "
                  f"(rating: {highest_rated.get('avg_rating', 'N/A')})")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    example_usage()
    advanced_usage() 