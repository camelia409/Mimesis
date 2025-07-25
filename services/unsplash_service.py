import os
import requests
import logging
from typing import List, Dict


class UnsplashService:
    """Service for fetching images from Unsplash API to create visual moodboards"""
    
    def __init__(self):
        self.access_key = os.environ.get("UNSPLASH_ACCESS_KEY")
        self.base_url = "https://api.unsplash.com"
        
    def fetch_moodboard_images(self, moodboard_description: str, count: int = 5) -> List[Dict]:
        """
        Fetch images from Unsplash that match the moodboard theme
        
        Args:
            moodboard_description: Description of the aesthetic/moodboard
            count: Number of images to fetch (max 30 per request)
            
        Returns:
            List of image data with URLs and metadata
        """
        if not self.access_key:
            logging.warning("Unsplash API key not found")
            return []
            
        try:
            # Extract key visual terms from moodboard description
            search_query = self._extract_search_terms(moodboard_description)
            
            url = f"{self.base_url}/search/photos"
            params = {
                "query": search_query,
                "client_id": self.access_key,
                "per_page": min(count, 30),
                "orientation": "landscape",
                "order_by": "relevant"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            images = []
            
            for photo in data.get("results", []):
                images.append({
                    "id": photo["id"],
                    "url_small": photo["urls"]["small"],
                    "url_regular": photo["urls"]["regular"],
                    "alt_description": photo.get("alt_description", "Moodboard image"),
                    "photographer": photo["user"]["name"],
                    "photographer_url": photo["user"]["links"]["html"],
                    "download_url": photo["links"]["download_location"]
                })
            
            logging.info(f"Fetched {len(images)} images for query: {search_query}")
            return images
            
        except requests.RequestException as e:
            logging.error(f"Unsplash API error: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Error fetching moodboard images: {str(e)}")
            return []
    
    def _extract_search_terms(self, moodboard_description: str) -> str:
        """
        Extract the most relevant visual search terms from moodboard description
        
        Args:
            moodboard_description: Full moodboard description
            
        Returns:
            Optimized search query for Unsplash
        """
        if not moodboard_description:
            return "fashion aesthetic"
            
        # Common visual keywords to prioritize
        visual_keywords = [
            "neon", "vintage", "retro", "minimalist", "grunge", "bohemian", "gothic",
            "cyberpunk", "steampunk", "industrial", "desert", "urban", "nature",
            "noir", "pastel", "monochrome", "colorful", "dark", "light", "sunset",
            "city", "landscape", "texture", "fabric", "leather", "denim", "silk",
            "gold", "silver", "copper", "metallic", "geometric", "organic", "fluid"
        ]
        
        description_lower = moodboard_description.lower()
        found_keywords = []
        
        # Extract color terms
        colors = ["blue", "red", "green", "yellow", "orange", "purple", "pink", "black", "white", "gray", "grey", "brown", "beige", "navy", "emerald", "turquoise", "magenta", "coral", "sage", "indigo", "sepia"]
        for color in colors:
            if color in description_lower:
                found_keywords.append(color)
        
        # Extract visual style keywords
        for keyword in visual_keywords:
            if keyword in description_lower:
                found_keywords.append(keyword)
        
        # Take first few sentences and extract key terms
        sentences = moodboard_description.split('.')[0:2]
        key_terms = []
        
        for sentence in sentences:
            words = sentence.split()
            for word in words[:10]:  # First 10 words of each sentence
                word_clean = word.strip('.,!?"()[]').lower()
                if len(word_clean) > 3 and word_clean not in ['this', 'that', 'with', 'from', 'they', 'them', 'their', 'have', 'been', 'were', 'would', 'could', 'should']:
                    key_terms.append(word_clean)
        
        # Combine found keywords and key terms
        all_terms = found_keywords + key_terms[:3]  # Limit to prevent too broad search
        
        if all_terms:
            search_query = " ".join(all_terms[:4])  # Use top 4 terms
        else:
            # Fallback to first significant words
            words = moodboard_description.split()[:5]
            search_query = " ".join(word.strip('.,!?"()[]') for word in words)
        
        # Ensure we have a reasonable search query
        if len(search_query.strip()) < 3:
            search_query = "aesthetic fashion style"
            
        logging.info(f"Generated search query: '{search_query}' from description: '{moodboard_description[:100]}...'")
        return search_query


# Global service instance
unsplash_service = UnsplashService()


def fetch_moodboard_images(moodboard_description: str, count: int = 5) -> List[Dict]:
    """Convenience function for fetching moodboard images"""
    return unsplash_service.fetch_moodboard_images(moodboard_description, count)