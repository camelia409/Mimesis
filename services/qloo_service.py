import os
import requests
import logging
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Qloo API Configuration
QLOO_API_BASE = "https://hackathon.api.qloo.com"
API_KEY = os.getenv("QLOO_API_KEY")
if not API_KEY:
    logger.error("Qloo API key not found in environment variables.")
    raise ValueError("Qloo API key is missing. Please check your .env file.")

HEADERS = {
    "X-API-KEY": API_KEY,  # Fixed: Changed from "X-Api-Key" to "X-API-KEY"
    "Content-Type": "application/json"
}

# Enhanced Entity Mapping (static mappings)
ENTITY_MAPPING = {
    # Music Artists
    "ar rahman": "urn:entity:artist:AR_Rahman",
    "a.r. rahman": "urn:entity:artist:AR_Rahman",
    "ravi shankar": "urn:entity:artist:Ravi_Shankar",
    "sza": "urn:entity:artist:SZA",
    "aphex twin": "urn:entity:artist:Aphex_Twin",
    "arijit singh": "urn:entity:artist:Arijit_Singh",
    "beyoncé": "urn:entity:artist:Beyoncé",
    "taylor swift": "urn:entity:artist:Taylor_Swift",
    "bts": "urn:entity:artist:BTS",
    "blackpink": "urn:entity:artist:BLACKPINK",
    "lana del rey": "urn:entity:artist:Lana_Del_Rey",
    "the weeknd": "urn:entity:artist:The_Weeknd",
    "drake": "urn:entity:artist:Drake",
    "sitar": "urn:entity:instrument:Sitar",
    
    # Films and Cinema
    "radhe shyam": "urn:entity:movie:Radhe_Shyam",
    "enthiran": "urn:entity:movie:Enthiran",
    "kgf": "urn:entity:movie:KGF",
    "kgf chapter 2": "urn:entity:movie:KGF_Chapter_2",
    "blade runner": "urn:entity:movie:Blade_Runner",
    "blade runner 2049": "urn:entity:movie:Blade_Runner_2049",
    "matrix": "urn:entity:movie:The_Matrix",
    "dilwale dulhania le jayenge": "urn:entity:movie:Dilwale_Dulhania_Le_Jayenge",
    "dilwale": "urn:entity:movie:Dilwale_Dulhania_Le_Jayenge",
    "rrr": "urn:entity:movie:RRR",
    "bahubali": "urn:entity:movie:Baahubali",
    "inception": "urn:entity:movie:Inception",
    "interstellar": "urn:entity:movie:Interstellar",
    "70s bollywood": "urn:entity:movie:1970s_Bollywood",
    "bollywood": "urn:entity:movie:Bollywood",
    
    # People
    "aishwarya rai": "urn:entity:person:Aishwarya_Rai",
    "rajinikanth": "urn:entity:person:Rajinikanth",
    "amitabh bachchan": "urn:entity:person:Amitabh_Bachchan",
    
    # Cultural Elements
    "chess": "urn:entity:game:Chess",
    "20s cinema": "urn:entity:movie:1920s_Cinema",
    "vintage": "urn:entity:style:Vintage",
    "japanese architecture": "urn:entity:style:Japanese_Architecture",
    "zen": "urn:entity:style:Zen",
    "minimalist": "urn:entity:style:Minimalist",
    "bohemian": "urn:entity:style:Bohemian",
    "classic": "urn:entity:style:Classic",
    "modern": "urn:entity:style:Modern",
    "traditional": "urn:entity:style:Traditional",
    "contemporary": "urn:entity:style:Contemporary",
    "avant-garde": "urn:entity:style:Avant_Garde",
    
    # Games
    "red dead redemption": "urn:entity:video_game:Red_Dead_Redemption",
    "red dead": "urn:entity:video_game:Red_Dead_Redemption",
    "cyberpunk 2077": "urn:entity:video_game:Cyberpunk_2077",
    "the witcher": "urn:entity:video_game:The_Witcher",
    
    # Cultural Regions
    "indian": "urn:entity:style:Indian_Culture",
    "japanese": "urn:entity:style:Japanese_Culture",
    "korean": "urn:entity:style:Korean_Culture",
    "chinese": "urn:entity:style:Chinese_Culture",
    "western": "urn:entity:style:Western_Culture",
    "eastern": "urn:entity:style:Eastern_Culture",
    "african": "urn:entity:style:African_Culture",
    "latin": "urn:entity:style:Latin_Culture",
    "middle eastern": "urn:entity:style:Middle_Eastern_Culture",
    
    # Fashion Styles
    "streetwear": "urn:entity:style:Streetwear",
    "high fashion": "urn:entity:style:High_Fashion",
    "casual": "urn:entity:style:Casual_Fashion",
    "formal": "urn:entity:style:Formal_Fashion",
    "sustainable": "urn:entity:style:Sustainable_Fashion",
    "thrift": "urn:entity:style:Thrift_Fashion",
    "luxury": "urn:entity:style:Luxury_Fashion"
}

# Enhanced Cultural Insights (static mappings)
CULTURAL_INSIGHTS = {
    "ar rahman": {
        "aesthetic": "Sophisticated fusion of classical Indian and contemporary music",
        "style_keywords": ["elegant", "cultural fusion", "sophisticated", "traditional", "contemporary"],
        "color_palette": ["deep reds", "gold", "navy", "cream", "sage green"],
        "fabrics": ["silk", "cotton", "linen", "embroidery", "traditional textiles"],
        "cultural_elements": ["classical music", "Indian culture", "cinematic grandeur", "cultural sophistication"]
    },
    "ravi shankar": {
        "aesthetic": "Timeless Indian classical music with spiritual depth and cultural richness",
        "style_keywords": ["spiritual", "classical", "timeless", "cultural", "sophisticated"],
        "color_palette": ["deep oranges", "gold", "saffron", "cream", "earth tones"],
        "fabrics": ["silk", "cotton", "traditional textiles", "handwoven fabrics", "natural materials"],
        "cultural_elements": ["classical Indian music", "spiritual culture", "traditional aesthetics", "cultural heritage"]
    },
    "aishwarya rai": {
        "aesthetic": "Timeless Indian beauty with global sophistication and cultural elegance",
        "style_keywords": ["elegant", "timeless", "sophisticated", "cultural", "global"],
        "color_palette": ["deep reds", "gold", "emerald", "navy", "cream"],
        "fabrics": ["silk", "satin", "embroidery", "luxury fabrics", "traditional textiles"],
        "cultural_elements": ["Indian beauty", "global sophistication", "cultural elegance", "timeless style"]
    },
    "sitar": {
        "aesthetic": "Classical Indian instrument with spiritual resonance and cultural depth",
        "style_keywords": ["spiritual", "classical", "cultural", "traditional", "harmonious"],
        "color_palette": ["deep browns", "gold", "cream", "sage", "earth tones"],
        "fabrics": ["natural materials", "traditional textiles", "handcrafted fabrics", "organic materials"],
        "cultural_elements": ["classical Indian music", "spiritual culture", "traditional craftsmanship", "cultural heritage"]
    },
    "70s bollywood": {
        "aesthetic": "Vintage Bollywood glamour with retro charm and cultural vibrancy",
        "style_keywords": ["vintage", "glamorous", "retro", "vibrant", "cultural"],
        "color_palette": ["bright colors", "gold", "silver", "vibrant hues", "metallic accents"],
        "fabrics": ["silk", "sequins", "velvet", "satin", "traditional textiles"],
        "cultural_elements": ["Bollywood culture", "retro glamour", "cultural vibrancy", "vintage aesthetics"]
    },
    "sza": {
        "aesthetic": "Contemporary R&B with urban sophistication and modern femininity",
        "style_keywords": ["urban", "contemporary", "sophisticated", "modern", "feminine"],
        "color_palette": ["blacks", "whites", "neutrals", "pastels", "metallics"],
        "fabrics": ["silk", "satin", "leather", "denim", "luxury fabrics"],
        "cultural_elements": ["R&B culture", "urban lifestyle", "contemporary fashion", "modern femininity"]
    },
    "blade runner": {
        "aesthetic": "Cyberpunk noir with futuristic urban dystopia",
        "style_keywords": ["futuristic", "urban", "noir", "cyberpunk", "dystopian"],
        "color_palette": ["neon colors", "blacks", "grays", "electric blues", "purples"],
        "fabrics": ["leather", "vinyl", "metallic", "synthetic", "tech fabrics"],
        "cultural_elements": ["cyberpunk culture", "futuristic aesthetics", "urban noir", "technological influence"]
    },
    "vintage": {
        "aesthetic": "Timeless elegance with retro charm and classic sophistication",
        "style_keywords": ["timeless", "elegant", "classic", "retro", "sophisticated"],
        "color_palette": ["earth tones", "pastels", "jewel tones", "neutrals", "warm colors"],
        "fabrics": ["wool", "silk", "cotton", "tweed", "vintage textiles"],
        "cultural_elements": ["vintage culture", "classic aesthetics", "timeless style", "retro charm"]
    },
    "zen": {
        "aesthetic": "Minimalist philosophy with natural materials and peaceful aesthetics",
        "style_keywords": ["minimalist", "peaceful", "natural", "simple", "harmonious"],
        "color_palette": ["whites", "beiges", "grays", "earth tones", "soft neutrals"],
        "fabrics": ["linen", "cotton", "natural fibers", "organic materials", "simple textures"],
        "cultural_elements": ["Zen philosophy", "minimalist culture", "natural aesthetics", "peaceful living"]
    }
}

# Entity Types for Insights
ENTITY_TYPES = [
    "urn:entity:movie", "urn:entity:artist", "urn:entity:person", "urn:entity:book",
    "urn:entity:brand", "urn:entity:tv_show", "urn:entity:video_game",
    "urn:entity:place", "urn:entity:destination", "urn:entity:podcast"
]

# API Helper Functions
def get_tags(search: str) -> Dict[str, Any]:
    """Fetch tags from Qloo API based on search query."""
    url = f"{QLOO_API_BASE}/v2/tags"
    params = {"filter.query": search}  # Fixed: Changed from "search" to "filter.query"
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to get tags for '{search}': {e}")
        return {"error": str(e), "success": False}

def get_insights(tag_urn: str, entity_type: str = "urn:entity:brand") -> Dict[str, Any]:
    """Fetch insights from Qloo API for a given tag URN and entity type."""
    url = f"{QLOO_API_BASE}/v2/insights"
    params = {"filter.type": entity_type, "signal.interests.tags": tag_urn}  # Fixed: Using signal.interests.tags
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to get insights for '{tag_urn}': {e}")
        return {"error": str(e), "success": False}

def get_entity_id(entity_name: str) -> str:
    """Search Qloo for an entity and return its ID (or None if not found)."""
    entity_lower = entity_name.lower().strip()
    
    # Check manual mapping first
    if entity_lower in ENTITY_MAPPING:
        logger.info(f"Found manual mapping for '{entity_name}': {ENTITY_MAPPING[entity_lower]}")
        return ENTITY_MAPPING[entity_lower]

    try:
        url = f"{QLOO_API_BASE}/search"
        params = {"query": entity_name, "types": ENTITY_TYPES}
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Handle different response structures
        entities = []
        if isinstance(data, dict):
            results = data.get("results", {})
            if isinstance(results, dict):
                entities = results.get("entities", [])
            elif isinstance(results, list):
                entities = results
        elif isinstance(data, list):
            entities = data
        
        if entities and len(entities) > 0:
            entity_id = entities[0].get("entity_id")
            logger.info(f"Found Qloo entity for '{entity_name}': {entity_id}")
            return entity_id
        
        logger.warning(f"No Qloo entity found for: {entity_name}")
        return None
    except requests.RequestException as e:
        logger.error(f"Qloo entity search failed for '{entity_name}': {e}")
        return None

def get_cultural_insights(entity_name: str) -> Dict[str, Any]:
    """Get detailed cultural insights for a specific entity."""
    entity_lower = entity_name.lower().strip()
    
    if entity_lower in CULTURAL_INSIGHTS:
        return CULTURAL_INSIGHTS[entity_lower]

    # Dynamic fallback based on cultural keywords
    if any(keyword in entity_lower for keyword in ["indian", "tamil", "hindi", "bollywood"]):
        return {
            "aesthetic": "Rich cultural heritage with vibrant colors and traditional elements",
            "style_keywords": ["cultural", "traditional", "vibrant", "heritage", "sophisticated"],
            "color_palette": ["deep reds", "gold", "navy", "emerald", "purple"],
            "fabrics": ["silk", "cotton", "embroidery", "traditional textiles", "luxury fabrics"],
            "cultural_elements": ["Indian culture", "traditional aesthetics", "cultural heritage", "vibrant expression"]
        }
    elif any(keyword in entity_lower for keyword in ["japanese", "zen", "tokyo"]):
        return {
            "aesthetic": "Minimalist elegance with natural materials and cultural harmony",
            "style_keywords": ["minimalist", "elegant", "natural", "harmonious", "cultural"],
            "color_palette": ["whites", "beiges", "grays", "navy", "soft neutrals"],
            "fabrics": ["linen", "cotton", "natural fibers", "simple textures", "organic materials"],
            "cultural_elements": ["Japanese culture", "minimalist philosophy", "natural aesthetics", "cultural harmony"]
        }
    elif any(keyword in entity_lower for keyword in ["western", "american", "european"]):
        return {
            "aesthetic": "Contemporary sophistication with modern urban influences",
            "style_keywords": ["contemporary", "sophisticated", "modern", "urban", "elegant"],
            "color_palette": ["neutrals", "blacks", "whites", "navy", "pastels"],
            "fabrics": ["cotton", "silk", "wool", "denim", "luxury fabrics"],
            "cultural_elements": ["Western culture", "contemporary fashion", "urban lifestyle", "modern sophistication"]
        }
    
    return {
        "aesthetic": "Personal cultural expression with contemporary relevance",
        "style_keywords": ["personal", "cultural", "contemporary", "expressive", "unique"],
        "color_palette": ["versatile colors", "personal preferences", "cultural influences"],
        "fabrics": ["quality materials", "cultural textiles", "contemporary fabrics"],
        "cultural_elements": ["personal culture", "contemporary expression", "unique identity"]
    }

def get_fashion_archetypes(cultural_input: str) -> Dict[str, Any]:
    """Map cultural preferences to fashion archetypes using Qloo Insights API."""
    if not API_KEY:
        logger.error("Qloo API key not found")
        return {
            "success": False,
            "error": "Qloo API key not found",
            "archetypes": [],
            "entities_processed": [],
            "error_code": "QLOO_API_KEY_MISSING"
        }

    entities = [entity.strip() for entity in cultural_input.split(',') if entity.strip()]
    entities_processed = []
    cultural_insights = []
    tag_urns = []

    logger.info(f"Processing cultural input: {cultural_input}")
    logger.info(f"Parsed entities: {entities}")

    # First, try to get tags for each entity
    for entity in entities:
        try:
            # Try to get tags for this entity
            tags_result = get_tags(entity)
            if tags_result.get("success") and "results" in tags_result:
                tags = tags_result["results"].get("tags", [])
                if tags:
                    # Use the first tag found
                    tag_urn = tags[0].get("id")
                    if tag_urn:
                        tag_urns.append(tag_urn)
                        entities_processed.append(entity)
                        insights = get_cultural_insights(entity)
                        cultural_insights.append({"entity": entity, "insights": insights})
                        logger.info(f"Found tag for '{entity}': {tag_urn}")
                        continue
            
            # If no tags found, try manual mapping
            eid = get_entity_id(entity)
            if eid:
                entities_processed.append(entity)
                insights = get_cultural_insights(entity)
                cultural_insights.append({"entity": entity, "insights": insights})
                logger.info(f"Successfully mapped '{entity}' to entity ID: {eid}")
            else:
                logger.warning(f"No Qloo entity or tags found for: {entity}")
                
        except Exception as e:
            logger.error(f"Error processing entity '{entity}': {e}")

    if not tag_urns and not entities_processed:
        logger.error("No Qloo entities or tags found for any input")
        return {
            "success": True,
            "archetypes": ["Cultural Fusion", "Global Aesthetic", "Personal Style"],
            "raw_response": {"fallback": True, "message": "Using fallback archetypes"},
            "entities_processed": entities_processed,
            "cultural_insights": cultural_insights,
            "fallback": True
        }

    # Try to get insights using tags first
    if tag_urns:
        logger.info(f"Found tag URNs: {tag_urns}")
        try:
            # Use the first tag for insights
            tag_urn = tag_urns[0]
            insights_result = get_insights(tag_urn, "urn:entity:brand")
            
            if insights_result.get("success") and "results" in insights_result:
                entities_data = insights_result["results"].get("entities", [])
                if entities_data:
                    archetypes = [ent.get("name", "") for ent in entities_data[:5]]  # Get first 5 brands
                    logger.info(f"Found archetypes from tags: {archetypes}")
                    return {
                        "success": True,
                        "archetypes": archetypes,
                        "raw_response": insights_result,
                        "entities_processed": entities_processed,
                        "cultural_insights": cultural_insights
                    }
        except Exception as e:
            logger.error(f"Error getting insights from tags: {e}")

    # Fallback: try entity-based approach
    logger.info("Trying entity-based approach...")
    entity_ids = []
    
    for entity in entities_processed:
        eid = get_entity_id(entity)
        if eid:
            entity_ids.append(eid)

    if not entity_ids:
        logger.warning("No entity IDs found, using enhanced fallback data")
        return {
            "success": True,
            "archetypes": ["Cultural Fusion", "Global Aesthetic", "Personal Style"],
            "raw_response": {"fallback": True, "message": "Using fallback archetypes"},
            "entities_processed": entities_processed,
            "cultural_insights": cultural_insights,
            "fallback": True
        }

    logger.info(f"Found entity IDs: {entity_ids}")
    
    # Try each entity type until we get a valid response
    for entity_type in ENTITY_TYPES:
        try:
            # Try using signal.interests.tags instead of signal.interests.entities
            # First, try to get a tag for one of the entities
            test_entity = entities_processed[0] if entities_processed else "fashion"
            tags_result = get_tags(test_entity)
            
            if tags_result.get("success") and "results" in tags_result:
                tags = tags_result["results"].get("tags", [])
                if tags:
                    tag_urn = tags[0].get("id")
                    params = {"filter.type": entity_type, "signal.interests.tags": tag_urn}
                    logger.info(f"Trying Qloo insights with params: {params}")
                    
                    response = requests.get(f"{QLOO_API_BASE}/v2/insights", headers=HEADERS, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"Qloo insights response: {data}")
                        
                        # Try to extract recommendations/archetypes
                        archetypes = []
                        if "results" in data and "entities" in data["results"]:
                            archetypes = [ent.get("name", "") for ent in data["results"]["entities"][:5]]
                        
                        if archetypes:
                            logger.info(f"Found archetypes: {archetypes}")
                            return {
                                "success": True,
                                "archetypes": archetypes,
                                "raw_response": data,
                                "entities_processed": entities_processed,
                                "cultural_insights": cultural_insights
                            }
                    elif response.status_code == 404:
                        logger.info(f"404 for entity type {entity_type}, trying next...")
                        continue  # Try next entity type
                    else:
                        logger.error(f"Qloo API error: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            logger.error(f"Qloo Insights API error for type {entity_type}: {e}")
            continue

    logger.warning("All Qloo entity types failed, using enhanced fallback data")
    return {
        "success": True,
        "archetypes": ["Cultural Fusion", "Global Aesthetic", "Personal Style"],
        "raw_response": {"fallback": True, "message": "Using fallback archetypes"},
        "entities_processed": entities_processed,
        "cultural_insights": cultural_insights,
        "fallback": True
    }

if __name__ == "__main__":
    # Test the module
    test_input = "Ravi Shankar, Aishwarya Rai, Sitar, 70s Bollywood"
    result = get_fashion_archetypes(test_input)
    logger.info(f"Test result: {result}")
