import os
import requests
import logging
from typing import Dict, List, Any

QLOO_API_BASE = "https://hackathon.api.qloo.com"
QLOO_API_KEY = os.environ.get("QLOO_API_KEY")
HEADERS = {"X-Api-Key": QLOO_API_KEY}

# Manual entity mapping for common inputs that might not be found
ENTITY_MAPPING = {
    "ar rahman": "urn:entity:artist:AR_Rahman",
    "a.r. rahman": "urn:entity:artist:AR_Rahman", 
    "radhe shyam": "urn:entity:movie:Radhe_Shyam",
    "rajinikanth": "urn:entity:person:Rajinikanth",
    "enthiran": "urn:entity:movie:Enthiran",
    "kgf": "urn:entity:movie:KGF",
    "kgf chapter 2": "urn:entity:movie:KGF_Chapter_2",
    "sza": "urn:entity:artist:SZA",
    "aphex twin": "urn:entity:artist:Aphex_Twin",
    "blade runner": "urn:entity:movie:Blade_Runner",
    "blade runner 2049": "urn:entity:movie:Blade_Runner_2049",
    "matrix": "urn:entity:movie:The_Matrix",
    "chess": "urn:entity:game:Chess",
    "20s cinema": "urn:entity:movie:1920s_Cinema",
    "vintage": "urn:entity:style:Vintage",
    "dilwale dulhania le jayenge": "urn:entity:movie:Dilwale_Dulhania_Le_Jayenge",
    "dilwale": "urn:entity:movie:Dilwale_Dulhania_Le_Jayenge",
    "arijit singh": "urn:entity:artist:Arijit_Singh",
    "japanese architecture": "urn:entity:style:Japanese_Architecture",
    "zen": "urn:entity:style:Zen",
    "red dead redemption": "urn:entity:video_game:Red_Dead_Redemption",
    "red dead": "urn:entity:video_game:Red_Dead_Redemption"
}

ENTITY_TYPES = [
    "urn:entity:movie",
    "urn:entity:artist", 
    "urn:entity:person",
    "urn:entity:book",
    "urn:entity:brand",
    "urn:entity:tv_show",
    "urn:entity:video_game",
    "urn:entity:place",
    "urn:entity:destination",
    "urn:entity:podcast"
]

def get_entity_id(entity_name: str) -> str:
    """Search Qloo for an entity and return its ID (or None if not found)"""
    entity_lower = entity_name.lower().strip()
    
    # Check manual mapping first
    if entity_lower in ENTITY_MAPPING:
        logging.info(f"Found manual mapping for '{entity_name}': {ENTITY_MAPPING[entity_lower]}")
        return ENTITY_MAPPING[entity_lower]
    
    try:
        # Use correct search endpoint
        resp = requests.get(
            f"{QLOO_API_BASE}/search",
            params={
                "query": entity_name,
                "types": ["urn:entity:artist", "urn:entity:movie", "urn:entity:person", "urn:entity:book", "urn:entity:video_game"]
            },
            headers=HEADERS,
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        
        # Parse the correct response structure
        results = data.get("results", {})
        entities = results.get("entities", [])
        
        if entities:
            entity_id = entities[0].get("entity_id")
            logging.info(f"Found Qloo entity for '{entity_name}': {entity_id}")
            return entity_id
        
        logging.warning(f"No Qloo entity found for: {entity_name}")
        return None
        
    except Exception as e:
        logging.error(f"Qloo entity search failed for '{entity_name}': {e}")
        return None

def get_fashion_archetypes(cultural_input: str) -> Dict[str, Any]:
    """
    Use Qloo Insights API to map cultural preferences to fashion archetypes
    """
    if not QLOO_API_KEY:
        logging.error("Qloo API key not found")
        return {"success": False, "error": "Qloo API key not found", "archetypes": [], "entities_processed": []}

    # Parse cultural inputs into entities
    entities = [entity.strip() for entity in cultural_input.split(',') if entity.strip()]
    entity_ids = []
    entities_processed = []
    
    logging.info(f"Processing cultural input: {cultural_input}")
    logging.info(f"Parsed entities: {entities}")
    
    for entity in entities:
        eid = get_entity_id(entity)
        if eid:
            entity_ids.append(eid)
            entities_processed.append(entity)
            logging.info(f"Successfully mapped '{entity}' to entity ID: {eid}")
        else:
            logging.warning(f"No Qloo entity found for: {entity}")

    if not entity_ids:
        logging.error("No Qloo entities found for any input")
        # Return fallback data to allow Gemini to still work
        return {
            "success": True,  # Mark as success to allow Gemini to proceed
            "archetypes": ["Cultural Fusion", "Global Aesthetic", "Personal Style"],
            "raw_response": {"fallback": True, "message": "Using fallback archetypes"},
            "entities_processed": entities_processed,
            "fallback": True
        }

    logging.info(f"Found entity IDs: {entity_ids}")

    # Try each entity type until we get a valid response
    for entity_type in ENTITY_TYPES:
        try:
            params = {
                "filter.type": entity_type,
                "signal.interests.entities": ",".join(entity_ids)
            }
            
            logging.info(f"Trying Qloo insights with params: {params}")
            
            resp = requests.get(
                f"{QLOO_API_BASE}/v2/insights/",
                params=params,
                headers=HEADERS,
                timeout=15
            )
            
            if resp.status_code == 200:
                data = resp.json()
                logging.info(f"Qloo insights response: {data}")
                
                # Try to extract recommendations/archetypes
                archetypes = []
                if "recommendations" in data:
                    archetypes = [rec.get("name", "") for rec in data["recommendations"]]
                elif "insights" in data:
                    archetypes = [ins.get("name", "") for ins in data["insights"]]
                elif "results" in data:
                    results = data["results"]
                    if "entities" in results:
                        archetypes = [ent.get("name", "") for ent in results["entities"]]
                
                if archetypes:
                    logging.info(f"Found archetypes: {archetypes}")
                    return {
                        "success": True,
                        "archetypes": archetypes,
                        "raw_response": data,
                        "entities_processed": entities_processed
                    }
            elif resp.status_code == 404:
                logging.info(f"404 for entity type {entity_type}, trying next...")
                continue  # Try next entity type
            else:
                logging.error(f"Qloo API error: {resp.status_code} - {resp.text}")
        except Exception as e:
            logging.error(f"Qloo Insights API error for type {entity_type}: {e}")
            continue
    
    # If all entity types fail, return fallback data
    logging.warning("All Qloo entity types failed, using fallback data")
    return {
        "success": True,  # Mark as success to allow Gemini to proceed
        "archetypes": ["Cultural Fusion", "Global Aesthetic", "Personal Style"],
        "raw_response": {"fallback": True, "message": "Using fallback archetypes"},
        "entities_processed": entities_processed,
        "fallback": True
    }
