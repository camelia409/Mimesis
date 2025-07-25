import os
import requests
import logging
from typing import Dict, List, Any

def get_fashion_archetypes(cultural_input: str) -> Dict[str, Any]:
    """
    Query Qloo Taste AI API to map cultural preferences to fashion archetypes
    """
    api_key = os.environ.get("QLOO_API_KEY", "CvVdTX4-BEHocC3z1A9VCakIfYFSeSlXtXtY-4SKijo")
    
    if not api_key:
        raise Exception("Qloo API key not found in environment variables")
    
    # Parse cultural inputs into entities
    entities = [entity.strip() for entity in cultural_input.split(',') if entity.strip()]
    
    # Qloo API endpoint (verify actual endpoint in Qloo documentation)
    url = "https://api.qloo.com/v1/recommendations"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "entities": entities,
        "domain": "fashion",
        "count": 10  # Number of recommendations to return
    }
    
    try:
        logging.info(f"Sending request to Qloo API: {payload}")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract fashion archetypes from response
            archetypes = []
            if 'recommendations' in data:
                archetypes = [rec.get('name', '') for rec in data['recommendations']]
            
            return {
                "success": True,
                "archetypes": archetypes,
                "raw_response": data,
                "entities_processed": entities
            }
        else:
            logging.error(f"Qloo API error: {response.status_code} - {response.text}")
            return {
                "success": False,
                "error": f"API returned status {response.status_code}",
                "archetypes": [],
                "entities_processed": entities
            }
    
    except requests.exceptions.Timeout:
        logging.error("Qloo API request timed out")
        return {
            "success": False,
            "error": "Request timed out",
            "archetypes": [],
            "entities_processed": entities
        }
    
    except requests.exceptions.ConnectionError:
        logging.error("Failed to connect to Qloo API")
        return {
            "success": False,
            "error": "Unable to connect to Qloo API",
            "archetypes": [],
            "entities_processed": entities
        }
    
    except Exception as e:
        logging.error(f"Unexpected error in Qloo API call: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "archetypes": [],
            "entities_processed": entities
        }
