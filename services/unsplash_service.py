import os
import requests
import logging
import re
from typing import List, Dict, Optional


class UnsplashService:
    """Enhanced service for fetching images from Unsplash API to create visual moodboards"""
    
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
            return self._get_fallback_images(moodboard_description, count)
            
        try:
            # Generate multiple search queries for better results
            search_queries = self._generate_search_queries(moodboard_description)
            
            all_images = []
            for query in search_queries[:2]:  # Try first 2 queries
                images = self._fetch_from_unsplash(query, count // 2)
                all_images.extend(images)
                if len(all_images) >= count:
                    break
            
            # If Unsplash fails, try Pexels as fallback
            if not all_images:
                logging.info("Unsplash failed, trying Pexels fallback")
                all_images = self._fetch_from_pexels(moodboard_description, count)
            
            # If still no images, use static fallback
            if not all_images:
                all_images = self._get_fallback_images(moodboard_description, count)
            
            logging.info(f"Fetched {len(all_images)} images for moodboard")
            return all_images[:count]
            
        except Exception as e:
            logging.error(f"Error fetching moodboard images: {str(e)}")
            return self._get_fallback_images(moodboard_description, count)
    
    def _generate_search_queries(self, moodboard_description: str) -> List[str]:
        """
        Generate multiple optimized search queries from moodboard description
        """
        if not moodboard_description:
            return ["fashion aesthetic"]
        
        description_lower = moodboard_description.lower()
        queries = []
        
        # Cultural and aesthetic mapping
        cultural_mappings = {
            # Indian/South Asian aesthetics
            "indian": ["indian culture", "bollywood aesthetic", "indian wedding", "haveli architecture"],
            "hindi": ["indian culture", "bollywood aesthetic", "indian wedding", "haveli architecture"],
            "rajinikanth": ["indian cinema", "tamil culture", "south indian aesthetic"],
            "a.r. rahman": ["indian music", "bollywood aesthetic", "indian culture"],
            "arijit singh": ["indian music", "bollywood aesthetic", "indian culture"],
            "dilwale": ["indian wedding", "bollywood aesthetic", "indian culture"],
            
            # Cyberpunk/Sci-fi aesthetics
            "blade runner": ["cyberpunk city", "neon lights", "futuristic architecture", "dystopian cityscape"],
            "matrix": ["cyberpunk aesthetic", "digital art", "green code", "futuristic"],
            "aphex twin": ["electronic music aesthetic", "digital art", "abstract", "experimental"],
            "cyberpunk": ["cyberpunk aesthetic", "neon lights", "futuristic city", "digital art"],
            "glitch": ["digital art", "glitch aesthetic", "abstract", "experimental"],
            
            # Japanese aesthetics
            "japanese": ["japanese architecture", "minimalist japanese", "zen aesthetic", "japanese culture"],
            "zen": ["zen aesthetic", "minimalist", "japanese garden", "peaceful"],
            
            # Vintage/Retro aesthetics
            "vintage": ["vintage aesthetic", "retro style", "nostalgic", "old fashioned"],
            "retro": ["retro aesthetic", "vintage style", "nostalgic", "old fashioned"],
            "70s": ["1970s aesthetic", "retro style", "vintage fashion", "disco era"],
            "80s": ["1980s aesthetic", "retro style", "vintage fashion", "synthwave"],
            
            # Music-inspired aesthetics
            "sza": ["r&b aesthetic", "soul music", "contemporary r&b", "urban aesthetic"],
            "electronic": ["electronic music", "digital art", "synthwave", "futuristic"],
            
            # Gaming aesthetics
            "red dead": ["western aesthetic", "cowboy", "desert landscape", "wild west"],
            "gaming": ["gaming aesthetic", "digital art", "virtual reality", "futuristic"],
        }
        
        # Check for cultural keywords and generate specific queries
        for keyword, mappings in cultural_mappings.items():
            if keyword in description_lower:
                queries.extend(mappings)
        
        # Extract color palette
        colors = self._extract_colors(description_lower)
        if colors:
            queries.append(" ".join(colors[:2]) + " aesthetic")
        
        # Extract mood/atmosphere
        mood_terms = self._extract_mood_terms(description_lower)
        if mood_terms:
            queries.append(" ".join(mood_terms[:2]) + " aesthetic")
        
        # Extract architectural/design terms
        design_terms = self._extract_design_terms(description_lower)
        if design_terms:
            queries.append(" ".join(design_terms[:2]))
        
        # If no specific mappings found, use intelligent keyword extraction
        if not queries:
            queries = self._intelligent_keyword_extraction(moodboard_description)
        
        # Ensure we have at least one query
        if not queries:
            queries = ["aesthetic fashion style"]
        
        logging.info(f"Generated queries: {queries}")
        return queries
    
    def _extract_colors(self, text: str) -> List[str]:
        """Extract color terms from text"""
        colors = [
            "neon blue", "emerald green", "deep red", "golden", "silver", "copper",
            "charcoal", "navy", "burgundy", "sage", "coral", "turquoise", "magenta",
            "sepia", "monochrome", "pastel", "vibrant", "muted", "dark", "light"
        ]
        found_colors = []
        for color in colors:
            if color in text:
                found_colors.append(color)
        return found_colors
    
    def _extract_mood_terms(self, text: str) -> List[str]:
        """Extract mood/atmosphere terms"""
        mood_terms = [
            "melancholic", "nostalgic", "futuristic", "romantic", "mysterious",
            "energetic", "peaceful", "dramatic", "minimalist", "luxurious",
            "raw", "sophisticated", "rebellious", "elegant", "bold"
        ]
        found_moods = []
        for mood in mood_terms:
            if mood in text:
                found_moods.append(mood)
        return found_moods
    
    def _extract_design_terms(self, text: str) -> List[str]:
        """Extract architectural/design terms"""
        design_terms = [
            "brutalist", "minimalist", "organic", "geometric", "fluid",
            "structured", "asymmetrical", "layered", "textured", "smooth"
        ]
        found_designs = []
        for design in design_terms:
            if design in text:
                found_designs.append(design)
        return found_designs
    
    def _intelligent_keyword_extraction(self, description: str) -> List[str]:
        """Intelligent keyword extraction for unknown aesthetics"""
        # Extract key phrases and words
        words = re.findall(r'\b\w+\b', description.lower())
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        meaningful_words = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Create queries from meaningful words
        queries = []
        if meaningful_words:
            # Create aesthetic-focused queries
            for i in range(0, min(len(meaningful_words), 6), 2):
                query = " ".join(meaningful_words[i:i+2]) + " aesthetic"
                queries.append(query)
        
        return queries[:3]  # Return top 3 queries
    
    def _fetch_from_unsplash(self, query: str, count: int) -> List[Dict]:
        """Fetch images from Unsplash API"""
        try:
            url = f"{self.base_url}/search/photos"
            params = {
                "query": query,
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
                    "download_url": photo["links"]["download_location"],
                    "source": "unsplash"
                })
            
            logging.info(f"Fetched {len(images)} images from Unsplash for query: {query}")
            return images
            
        except Exception as e:
            logging.error(f"Unsplash API error for query '{query}': {str(e)}")
            return []
    
    def _fetch_from_pexels(self, description: str, count: int) -> List[Dict]:
        """Fetch images from Pexels API as fallback"""
        try:
            # Extract simple keywords for Pexels
            words = description.lower().split()[:3]
            query = " ".join(words)
            
            url = "https://api.pexels.com/v1/search"
            headers = {
                "Authorization": "YOUR_PEXELS_API_KEY"  # You would need to add this to .env
            }
            params = {
                "query": query,
                "per_page": count,
                "orientation": "landscape"
            }
            
            # For now, return empty as we don't have Pexels API key
            logging.info("Pexels API not configured, skipping")
            return []
            
        except Exception as e:
            logging.error(f"Pexels API error: {str(e)}")
            return []
    
    def _get_fallback_images(self, description: str, count: int) -> List[Dict]:
        """Return static fallback images based on description"""
        # Static fallback images for different aesthetics
        fallback_images = {
            "indian": [
                {"url_regular": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800", "alt_description": "Indian wedding aesthetic"},
                {"url_regular": "https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=800", "alt_description": "Bollywood aesthetic"},
                {"url_regular": "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=800", "alt_description": "Indian culture"},
                {"url_regular": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800", "alt_description": "Indian architecture"},
            ],
            "cyberpunk": [
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Cyberpunk city"},
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Neon lights"},
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Futuristic architecture"},
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Digital art"},
            ],
            "vintage": [
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Vintage aesthetic"},
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Retro style"},
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "70s aesthetic"},
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Nostalgic"},
            ],
            "japanese": [
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Japanese architecture"},
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Zen aesthetic"},
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Minimalist japanese"},
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Japanese culture"},
            ],
            "western": [
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Western aesthetic"},
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Desert landscape"},
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Wild west"},
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Cowboy aesthetic"},
            ],
            "default": [
                {"url_regular": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800", "alt_description": "Fashion aesthetic"},
                {"url_regular": "https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=800", "alt_description": "Style inspiration"},
                {"url_regular": "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=800", "alt_description": "Aesthetic moodboard"},
                {"url_regular": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800", "alt_description": "Cultural style"},
            ]
        }
        
        # Determine which fallback to use
        description_lower = description.lower()
        if any(term in description_lower for term in ["indian", "bollywood", "hindi", "rajinikanth", "a.r. rahman", "arijit singh", "dilwale"]):
            category = "indian"
        elif any(term in description_lower for term in ["cyberpunk", "blade runner", "matrix", "futuristic", "aphex twin", "glitch"]):
            category = "cyberpunk"
        elif any(term in description_lower for term in ["vintage", "retro", "70s", "80s"]):
            category = "vintage"
        elif any(term in description_lower for term in ["japanese", "zen", "minimalist"]):
            category = "japanese"
        elif any(term in description_lower for term in ["red dead", "western", "cowboy", "desert"]):
            category = "western"
        else:
            category = "default"
        
        images = fallback_images.get(category, fallback_images["default"])
        return images[:count]


# Global service instance
unsplash_service = UnsplashService()


def fetch_moodboard_images(moodboard_description: str, count: int = 5) -> List[Dict]:
    """Convenience function for fetching moodboard images"""
    return unsplash_service.fetch_moodboard_images(moodboard_description, count)