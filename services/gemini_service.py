import json
import logging
import os
from typing import Dict, Any, List
import google.generativeai as genai
from google.generativeai import types
from pydantic import BaseModel
import re

def format_sentences_with_breaks(text: str) -> str:
    """Format text to ensure each sentence starts on a new line after a full stop"""
    # Split text into sections
    sections = text.split('\n\n')
    formatted_sections = []
    
    for section in sections:
        if section.strip():
            # Split into lines
            lines = section.split('\n')
            formatted_lines = []
            
            for line in lines:
                if line.strip() and not line.strip().isupper():  # Not a header
                    # Split sentences and add line breaks
                    sentences = re.split(r'(?<=[.!?])\s+', line)
                    formatted_sentences = []
                    for sentence in sentences:
                        if sentence.strip():
                            formatted_sentences.append(sentence.strip())
                    
                    if formatted_sentences:
                        formatted_lines.append('\n'.join(formatted_sentences))
                else:
                    formatted_lines.append(line)
            
            formatted_sections.append('\n'.join(formatted_lines))
    
    return '\n\n'.join(formatted_sections)

# Initialize Gemini client lazily to avoid SSL issues
client = None

def get_gemini_client():
    """Get Gemini client with lazy initialization"""
    global client
    if client is None:
        try:
            # Configure the API key
            genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "AIzaSyA2JL7kXFhurNWZqh__DHRghXFxUiEtW-0"))
            # Get the model
            client = genai.GenerativeModel('gemini-1.5-pro')
        except Exception as e:
            logging.error(f"Failed to initialize Gemini client: {e}")
            # Return None if client initialization fails
            return None
    return client

class StyleRecommendations(BaseModel):
    aesthetic_name: str
    brands: list[str]
    outfit: str
    moodboard: str

def extract_largest_json(text):
    """Extract the largest JSON object from text, with improved error handling."""
    if not text:
        return None
    
    logging.info(f"Attempting to extract JSON from text of length: {len(text)}")
    logging.info(f"Text starts with: {text[:100]}...")
    
    # First, try to extract JSON from markdown code blocks
    markdown_patterns = [
        r'```json\s*(\{.*?\})\s*```',  # JSON in markdown code blocks
        r'```\s*(\{.*?\})\s*```',      # JSON in generic code blocks
        r'`(\{.*?\})`',                # JSON in inline code
    ]
    
    for i, pattern in enumerate(markdown_patterns):
        try:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                json_str = match.group(1) if len(match.groups()) > 0 else match.group(0)
                logging.info(f"Found JSON in markdown pattern {i}: {json_str[:100]}...")
                try:
                    parsed = json.loads(json_str)
                    if isinstance(parsed, dict) and len(parsed) > 0:
                        logging.info(f"Successfully parsed JSON from markdown pattern {i}")
                        return parsed
                except json.JSONDecodeError as e:
                    logging.error(f"JSON decode error in markdown pattern {i}: {e}")
                    continue
        except Exception as e:
            logging.error(f"Error in markdown pattern {i}: {e}")
            continue
    
    # If no markdown JSON found, try to find JSON objects with different patterns
    json_patterns = [
        r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Basic JSON object
        r'\{.*?\}',  # Simple JSON object
        r'\{[^}]*"aesthetic_name"[^}]*\}',  # JSON with aesthetic_name
        r'\{[^}]*"brands"[^}]*\}',  # JSON with brands
    ]
    
    largest_json = None
    max_length = 0
    
    for i, pattern in enumerate(json_patterns):
        try:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                json_str = match.group()
                if len(json_str) > max_length:
                    logging.info(f"Found potential JSON with pattern {i}: {json_str[:100]}...")
                    try:
                        # Try to parse as JSON
                        parsed = json.loads(json_str)
                        if isinstance(parsed, dict) and len(parsed) > 0:
                            largest_json = parsed
                            max_length = len(json_str)
                            logging.info(f"Successfully parsed JSON with pattern {i}")
                    except json.JSONDecodeError as e:
                        logging.error(f"JSON decode error in pattern {i}: {e}")
                        continue
        except Exception as e:
            logging.error(f"Error in JSON pattern {i}: {e}")
            continue
    
    # If no JSON found, try to extract from the entire text
    if largest_json is None:
        try:
            # Try to parse the entire text as JSON
            parsed = json.loads(text.strip())
            if isinstance(parsed, dict):
                logging.info("Successfully parsed entire text as JSON")
                largest_json = parsed
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse entire text as JSON: {e}")
    
    if largest_json:
        logging.info(f"Successfully extracted JSON with {len(largest_json)} fields")
    else:
        logging.error("Failed to extract any JSON from the text")
    
    return largest_json

def generate_style_recommendations(cultural_input: str, qloo_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use Gemini API to generate highly personalized aesthetic names, brands, outfits, and moodboards
    based on specific cultural inputs and Qloo insights
    """
    try:
        # Enhanced cultural analysis from user input
        cultural_elements = analyze_cultural_input(cultural_input)
        
        # Prepare detailed context from Qloo data
        qloo_context = create_detailed_qloo_context(qloo_data, cultural_elements)
        
        # Create focused personalized prompt
        personalized_prompt = create_personalized_prompt(cultural_input, cultural_elements, qloo_context)
        
        logging.info(f"Generated personalized prompt for cultural input: {cultural_input}")
        
        # Use Gemini to generate personalized recommendations
        client = get_gemini_client()
        if client is None:
            return generate_fallback_recommendations(cultural_input, qloo_data)
        
        response = client.generate_content(
            personalized_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=4000  # Increased token limit
            ),
        )
        
        if response.text:
            logging.info(f"Gemini response received: {len(response.text)} characters")
            logging.info(f"Response preview: {response.text[:200]}...")
            
            # Extract JSON response
            json_data = extract_largest_json(response.text)
            if json_data:
                # Validate the response structure
                required_fields = ["aesthetic_name", "brands", "outfit", "moodboard"]
                if all(field in json_data for field in required_fields):
                    # Validate and enhance the response
                    validated_response = validate_and_enhance_response(json_data, cultural_elements)
                    logging.info(f"Generated personalized recommendations: {validated_response.get('aesthetic_name')}")
                    return validated_response
                else:
                    logging.error(f"Missing required fields in JSON response: {list(json_data.keys())}")
                    logging.error(f"Available fields: {json_data}")
                    return generate_fallback_recommendations(cultural_input, qloo_data)
            else:
                logging.error("Failed to extract JSON from Gemini response")
                logging.error(f"Full response text: {response.text}")
                return generate_fallback_recommendations(cultural_input, qloo_data)
        else:
            logging.error("Empty response from Gemini")
            return generate_fallback_recommendations(cultural_input, qloo_data)
            
    except Exception as e:
        logging.error(f"Error in generate_style_recommendations: {str(e)}")
        return generate_fallback_recommendations(cultural_input, qloo_data)

def analyze_cultural_input(cultural_input: str) -> Dict[str, Any]:
    """
    Analyze cultural input to extract specific themes, elements, and preferences
    """
    elements = [elem.strip().lower() for elem in cultural_input.split(',') if elem.strip()]
    
    analysis = {
        "raw_elements": elements,
        "themes": [],
        "categories": {
            "music": [],
            "film": [],
            "art": [],
            "culture": [],
            "lifestyle": [],
            "fashion": [],
            "instruments": [],
            "games": [],
            "eras": []
        },
        "cultural_regions": [],
        "aesthetic_preferences": [],
        "style_keywords": [],
        "specific_elements": {},
        "color_themes": [],
        "fabric_preferences": [],
        "cultural_significance": []
    }
    
    # Enhanced cultural mappings with specific details
    music_artists = {
        "ar rahman": {
            "style": "sophisticated_fusion",
            "colors": ["deep reds", "gold", "navy", "cream"],
            "fabrics": ["silk", "cotton", "linen", "embroidery"],
            "significance": "classical Indian music fusion with contemporary elements"
        },
        "a.r. rahman": {
            "style": "sophisticated_fusion", 
            "colors": ["deep reds", "gold", "navy", "cream"],
            "fabrics": ["silk", "cotton", "linen", "embroidery"],
            "significance": "classical Indian music fusion with contemporary elements"
        },
        "sza": {
            "style": "contemporary_rnb",
            "colors": ["blacks", "whites", "neutrals", "pastels"],
            "fabrics": ["silk", "satin", "leather", "denim"],
            "significance": "urban contemporary R&B with modern femininity"
        }
    }
    
    films = {
        "radhe shyam": {
            "style": "period_drama",
            "colors": ["rich jewel tones", "gold", "deep purples"],
            "fabrics": ["velvet", "silk", "embroidery", "traditional textiles"],
            "significance": "period drama with traditional Indian aesthetics"
        },
        "blade runner": {
            "style": "cyberpunk_noir",
            "colors": ["neon colors", "blacks", "grays", "electric blues"],
            "fabrics": ["leather", "vinyl", "metallic", "synthetic"],
            "significance": "futuristic urban dystopia with noir elements"
        },
        "matrix": {
            "style": "cyberpunk_tech",
            "colors": ["blacks", "greens", "silvers", "dark grays"],
            "fabrics": ["leather", "vinyl", "tech fabrics", "synthetic"],
            "significance": "technological dystopia with sleek aesthetics"
        }
    }
    
    cultural_styles = {
        "vintage": {
            "style": "timeless_elegance",
            "colors": ["earth tones", "pastels", "jewel tones", "neutrals"],
            "fabrics": ["wool", "silk", "cotton", "tweed"],
            "significance": "classic sophistication with retro charm"
        },
        "zen": {
            "style": "minimalist_philosophy",
            "colors": ["whites", "beiges", "grays", "earth tones"],
            "fabrics": ["linen", "cotton", "natural fibers", "organic materials"],
            "significance": "minimalist philosophy with natural materials"
        },
        "minimalist": {
            "style": "clean_simplicity",
            "colors": ["whites", "blacks", "grays", "neutrals"],
            "fabrics": ["cotton", "linen", "simple textures"],
            "significance": "clean, simple, and uncluttered style"
        }
    }
    
    instruments = {
        "sitar": {
            "style": "classical_indian",
            "colors": ["deep browns", "gold", "cream", "sage"],
            "fabrics": ["natural materials", "traditional textiles", "handcrafted fabrics"],
            "significance": "classical Indian instrument with spiritual resonance"
        }
    }
    
    games = {
        "chess": {
            "style": "strategic_elegance",
            "colors": ["blacks", "whites", "gold", "deep browns"],
            "fabrics": ["wool", "silk", "structured fabrics"],
            "significance": "strategic thinking with classic elegance"
        }
    }
    
    eras = {
        "20s cinema": {
            "style": "art_deco_glamour",
            "colors": ["gold", "silver", "jewel tones", "metallics"],
            "fabrics": ["silk", "velvet", "sequins", "luxury fabrics"],
            "significance": "Art Deco glamour with cinematic sophistication"
        },
        "70s bollywood": {
            "style": "retro_glamour",
            "colors": ["bright colors", "gold", "silver", "vibrant hues"],
            "fabrics": ["silk", "sequins", "velvet", "satin"],
            "significance": "vintage Bollywood glamour with retro charm"
        }
    }
    
    for element in elements:
        # Check specific mappings first
        if element in music_artists:
            analysis["categories"]["music"].append(element)
            analysis["themes"].append("musical_influence")
            analysis["specific_elements"][element] = music_artists[element]
            analysis["color_themes"].extend(music_artists[element]["colors"])
            analysis["fabric_preferences"].extend(music_artists[element]["fabrics"])
            analysis["cultural_significance"].append(music_artists[element]["significance"])
            
        elif element in films:
            analysis["categories"]["film"].append(element)
            analysis["themes"].append("cinematic_aesthetic")
            analysis["specific_elements"][element] = films[element]
            analysis["color_themes"].extend(films[element]["colors"])
            analysis["fabric_preferences"].extend(films[element]["fabrics"])
            analysis["cultural_significance"].append(films[element]["significance"])
            
        elif element in cultural_styles:
            analysis["categories"]["culture"].append(element)
            analysis["themes"].append("cultural_style")
            analysis["specific_elements"][element] = cultural_styles[element]
            analysis["color_themes"].extend(cultural_styles[element]["colors"])
            analysis["fabric_preferences"].extend(cultural_styles[element]["fabrics"])
            analysis["cultural_significance"].append(cultural_styles[element]["significance"])
            
        elif element in instruments:
            analysis["categories"]["instruments"].append(element)
            analysis["themes"].append("musical_instrument")
            analysis["specific_elements"][element] = instruments[element]
            analysis["color_themes"].extend(instruments[element]["colors"])
            analysis["fabric_preferences"].extend(instruments[element]["fabrics"])
            analysis["cultural_significance"].append(instruments[element]["significance"])
            
        elif element in games:
            analysis["categories"]["games"].append(element)
            analysis["themes"].append("strategic_game")
            analysis["specific_elements"][element] = games[element]
            analysis["color_themes"].extend(games[element]["colors"])
            analysis["fabric_preferences"].extend(games[element]["fabrics"])
            analysis["cultural_significance"].append(games[element]["significance"])
            
        elif element in eras:
            analysis["categories"]["eras"].append(element)
            analysis["themes"].append("historical_era")
            analysis["specific_elements"][element] = eras[element]
            analysis["color_themes"].extend(eras[element]["colors"])
            analysis["fabric_preferences"].extend(eras[element]["fabrics"])
            analysis["cultural_significance"].append(eras[element]["significance"])
        
        # Extract cultural regions
        if any(region in element for region in ["indian", "tamil", "hindi", "bollywood", "ar rahman", "radhe shyam"]):
            analysis["cultural_regions"].append("south_asian")
        elif any(region in element for region in ["japanese", "zen", "tokyo"]):
            analysis["cultural_regions"].append("east_asian")
        elif any(region in element for region in ["western", "american", "european", "blade runner", "matrix"]):
            analysis["cultural_regions"].append("western")
        
        # Extract aesthetic preferences
        if element in ["vintage", "retro", "classic", "20s cinema", "70s bollywood"]:
            analysis["aesthetic_preferences"].append("timeless_elegance")
        elif element in ["modern", "contemporary", "blade runner", "matrix"]:
            analysis["aesthetic_preferences"].append("contemporary_style")
        elif element in ["minimalist", "zen"]:
            analysis["aesthetic_preferences"].append("minimalist_aesthetic")
        elif element in ["ar rahman", "sitar"]:
            analysis["aesthetic_preferences"].append("cultural_fusion")
    
    # Remove duplicates
    analysis["themes"] = list(set(analysis["themes"]))
    analysis["cultural_regions"] = list(set(analysis["cultural_regions"]))
    analysis["aesthetic_preferences"] = list(set(analysis["aesthetic_preferences"]))
    analysis["color_themes"] = list(set(analysis["color_themes"]))
    analysis["fabric_preferences"] = list(set(analysis["fabric_preferences"]))
    analysis["cultural_significance"] = list(set(analysis["cultural_significance"]))
    
    return analysis

def create_detailed_qloo_context(qloo_data: Dict[str, Any], cultural_elements: Dict[str, Any]) -> str:
    """
    Create detailed context from Qloo data for personalization
    """
    context_parts = []
    
    if qloo_data.get("success") and qloo_data.get("archetypes"):
        archetypes = qloo_data["archetypes"]
        context_parts.append(f"FASHION ARCHETYPES: {', '.join(archetypes)}")
        
        # Add specific archetype analysis
        for archetype in archetypes:
            if "vintage" in archetype.lower():
                context_parts.append("VINTAGE AESTHETIC: Classic, timeless elegance with retro influences")
            elif "modern" in archetype.lower():
                context_parts.append("MODERN AESTHETIC: Contemporary, clean lines with current trends")
            elif "cultural" in archetype.lower():
                context_parts.append("CULTURAL FUSION: Blend of traditional and contemporary elements")
            elif "minimalist" in archetype.lower():
                context_parts.append("MINIMALIST AESTHETIC: Clean, simple, and uncluttered style")
    
    if qloo_data.get("entities_processed"):
        entities = qloo_data["entities_processed"]
        context_parts.append(f"PROCESSED ENTITIES: {', '.join(entities)}")
    
    # Add cultural analysis context
    if cultural_elements["cultural_regions"]:
        regions = cultural_elements["cultural_regions"]
        context_parts.append(f"CULTURAL REGIONS: {', '.join(regions)}")
    
    if cultural_elements["aesthetic_preferences"]:
        preferences = cultural_elements["aesthetic_preferences"]
        context_parts.append(f"AESTHETIC PREFERENCES: {', '.join(preferences)}")
    
    return "\n".join(context_parts) if context_parts else "Personal cultural style identity"

def create_personalized_prompt(cultural_input: str, cultural_elements: Dict[str, Any], qloo_context: str) -> str:
    """
    Create a focused and effective personalized prompt for Gemini
    """
    
    # Extract key cultural elements for the prompt
    specific_elements = cultural_elements.get("specific_elements", {})
    color_themes = cultural_elements.get("color_themes", [])
    fabric_preferences = cultural_elements.get("fabric_preferences", [])
    
    # Build a focused cultural summary
    cultural_summary = []
    for element, details in specific_elements.items():
        cultural_summary.append(f"• {element.title()}: {details['significance']}")
    
    prompt = f"""Create personalized fashion recommendations for this cultural input: "{cultural_input}"

Cultural Elements:
{chr(10).join(cultural_summary[:3])}

Colors: {', '.join(color_themes[:3])}
Fabrics: {', '.join(fabric_preferences[:3])}

Create a unique style identity that reflects these cultural elements.

Respond with this exact JSON format:
{{
    "aesthetic_name": "Unique style name reflecting the cultural input",
    "brands": ["Brand1", "Brand2", "Brand3", "Brand4", "Brand5", "@InstagramBoutique"],
    "outfit": "CORE APPROACH\\n[One sentence]\\n\\nSTYLING PHILOSOPHY\\n[3 principles]\\n\\nPRACTICAL CONSIDERATIONS\\n[3 recommendations]\\n\\nCULTURAL INTEGRATION\\n[3 cultural elements]",
    "moodboard": "COLOR STORY\\n[3 colors with hex codes]\\n\\nTEXTURE GUIDE\\n[3 textures]\\n\\nCULTURAL ELEMENTS\\n[3 motifs]\\n\\nSTYLE APPROACH\\n[3 techniques]\\n\\nSEASONAL ADAPTATION\\n[Spring, Summer, Fall, Winter]\\n\\nPERSONAL EXPRESSION\\n[3 tips]"
}}

Be specific to the cultural input provided."""
    
    return prompt

def build_cultural_context(cultural_elements: Dict[str, Any]) -> str:
    """
    Build detailed cultural context from analyzed elements
    """
    context_parts = []
    
    # Add raw elements
    if cultural_elements.get("raw_elements"):
        elements = cultural_elements["raw_elements"]
        context_parts.append(f"CULTURAL ELEMENTS: {', '.join(elements)}")
    
    # Add themes
    if cultural_elements.get("themes"):
        themes = cultural_elements["themes"]
        context_parts.append(f"IDENTIFIED THEMES: {', '.join(themes)}")
    
    # Add categories with details
    if cultural_elements.get("categories"):
        categories = cultural_elements["categories"]
        for category, items in categories.items():
            if items:
                context_parts.append(f"{category.upper()}: {', '.join(items)}")
    
    # Add cultural regions
    if cultural_elements.get("cultural_regions"):
        regions = cultural_elements["cultural_regions"]
        context_parts.append(f"CULTURAL REGIONS: {', '.join(regions)}")
    
    # Add aesthetic preferences
    if cultural_elements.get("aesthetic_preferences"):
        preferences = cultural_elements["aesthetic_preferences"]
        context_parts.append(f"AESTHETIC PREFERENCES: {', '.join(preferences)}")
    
    # Add style keywords
    if cultural_elements.get("style_keywords"):
        keywords = cultural_elements["style_keywords"]
        context_parts.append(f"STYLE KEYWORDS: {', '.join(keywords)}")
    
    # Add cultural significance
    if cultural_elements.get("cultural_significance"):
        significance = cultural_elements["cultural_significance"]
        context_parts.append(f"CULTURAL SIGNIFICANCE: {', '.join(significance)}")
    
    # Add specific element analysis
    if cultural_elements.get("specific_elements"):
        specific_elements = cultural_elements["specific_elements"]
        context_parts.append("DETAILED ELEMENT ANALYSIS:")
        for element, details in specific_elements.items():
            context_parts.append(f"  • {element.title()}: {details['significance']}")
            context_parts.append(f"    Style: {details['style']}")
            context_parts.append(f"    Colors: {', '.join(details['colors'])}")
            context_parts.append(f"    Fabrics: {', '.join(details['fabrics'])}")
    
    return "\n".join(context_parts) if context_parts else "Personal cultural style identity"

def create_styling_guidance(cultural_elements: Dict[str, Any]) -> str:
    """
    Create specific styling guidance based on cultural elements
    """
    guidance_parts = []
    
    # Add specific styling guidance based on cultural elements
    if cultural_elements.get("specific_elements"):
        specific_elements = cultural_elements["specific_elements"]
        
        for element, details in specific_elements.items():
            element_guidance = f"STYLING FOR {element.upper()}:\n"
            
            if details["style"] == "sophisticated_fusion":
                element_guidance += "• Blend classical Indian elements with contemporary silhouettes\n"
                element_guidance += "• Use sophisticated color combinations with traditional fabrics\n"
                element_guidance += "• Incorporate cultural motifs through accessories and details\n"
                element_guidance += "• Focus on elegant layering and cultural fusion\n"
                
            elif details["style"] == "period_drama":
                element_guidance += "• Embrace romantic and dramatic aesthetics\n"
                element_guidance += "• Use rich, jewel-toned colors and luxurious fabrics\n"
                element_guidance += "• Incorporate traditional Indian elements with modern styling\n"
                element_guidance += "• Focus on statement pieces and cultural grandeur\n"
                
            elif details["style"] == "cyberpunk_noir":
                element_guidance += "• Embrace futuristic and urban aesthetics\n"
                element_guidance += "• Use dark colors with neon accents and metallic elements\n"
                element_guidance += "• Incorporate tech-inspired fabrics and structured silhouettes\n"
                element_guidance += "• Focus on sleek, modern lines with dystopian edge\n"
                
            elif details["style"] == "timeless_elegance":
                element_guidance += "• Embrace classic sophistication with retro influences\n"
                element_guidance += "• Use timeless colors and quality fabrics\n"
                element_guidance += "• Incorporate vintage elements with modern styling\n"
                element_guidance += "• Focus on enduring style and cultural heritage\n"
                
            elif details["style"] == "minimalist_philosophy":
                element_guidance += "• Embrace clean lines and natural materials\n"
                element_guidance += "• Use neutral colors and simple textures\n"
                element_guidance += "• Incorporate cultural elements through subtle details\n"
                element_guidance += "• Focus on harmony and peaceful aesthetics\n"
                
            elif details["style"] == "classical_indian":
                element_guidance += "• Honor traditional Indian craftsmanship and aesthetics\n"
                element_guidance += "• Use natural materials and traditional textiles\n"
                element_guidance += "• Incorporate cultural motifs and spiritual elements\n"
                element_guidance += "• Focus on cultural authenticity and heritage\n"
                
            elif details["style"] == "strategic_elegance":
                element_guidance += "• Embrace structured and sophisticated aesthetics\n"
                element_guidance += "• Use classic colors with strategic contrast\n"
                element_guidance += "• Incorporate elements of strategy and precision\n"
                element_guidance += "• Focus on timeless elegance with intellectual appeal\n"
                
            elif details["style"] == "art_deco_glamour":
                element_guidance += "• Embrace Art Deco sophistication and glamour\n"
                element_guidance += "• Use metallic accents and geometric patterns\n"
                element_guidance += "• Incorporate luxury fabrics and cinematic elements\n"
                element_guidance += "• Focus on dramatic elegance and vintage charm\n"
                
            guidance_parts.append(element_guidance)
    
    # Add general cultural fusion guidance
    if cultural_elements.get("cultural_regions"):
        regions = cultural_elements["cultural_regions"]
        if "south_asian" in regions:
            guidance_parts.append("SOUTH ASIAN FUSION GUIDANCE:\n")
            guidance_parts.append("• Blend traditional Indian elements with contemporary fashion\n")
            guidance_parts.append("• Use rich colors and traditional fabrics in modern silhouettes\n")
            guidance_parts.append("• Incorporate cultural motifs through accessories and details\n")
            guidance_parts.append("• Honor cultural heritage while embracing modern lifestyle\n")
    
    # Add aesthetic preference guidance
    if cultural_elements.get("aesthetic_preferences"):
        preferences = cultural_elements["aesthetic_preferences"]
        if "timeless_elegance" in preferences:
            guidance_parts.append("TIMELESS ELEGANCE GUIDANCE:\n")
            guidance_parts.append("• Focus on classic silhouettes and quality materials\n")
            guidance_parts.append("• Use enduring colors and sophisticated styling\n")
            guidance_parts.append("• Incorporate vintage elements with contemporary appeal\n")
            guidance_parts.append("• Create looks that transcend trends and seasons\n")
        
        if "cultural_fusion" in preferences:
            guidance_parts.append("CULTURAL FUSION GUIDANCE:\n")
            guidance_parts.append("• Blend multiple cultural influences harmoniously\n")
            guidance_parts.append("• Use cultural elements as accents and statement pieces\n")
            guidance_parts.append("• Honor cultural traditions while embracing modern fashion\n")
            guidance_parts.append("• Create unique combinations that tell a cultural story\n")
    
    return "\n".join(guidance_parts) if guidance_parts else "Embrace your unique cultural style identity with confidence and authenticity."

def validate_and_enhance_response(response_data: Dict[str, Any], cultural_elements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and enhance the AI response to ensure personalization
    """
    # Ensure all required fields are present
    required_fields = ["aesthetic_name", "brands", "outfit", "moodboard"]
    for field in required_fields:
        if field not in response_data:
            response_data[field] = ""
    
    # Enhance aesthetic name if it's too generic
    if response_data["aesthetic_name"] and len(response_data["aesthetic_name"]) < 20:
        # Make it more specific based on cultural elements
        enhanced_name = enhance_aesthetic_name(response_data["aesthetic_name"], cultural_elements)
        response_data["aesthetic_name"] = enhanced_name
    
    # Ensure brands are personalized
    if response_data["brands"] and len(response_data["brands"]) < 6:
        # Add more personalized brands
        additional_brands = generate_additional_brands(cultural_elements)
        response_data["brands"].extend(additional_brands[:6-len(response_data["brands"])])
    
    # Add success flag
    response_data["success"] = True
    
    return response_data

def enhance_aesthetic_name(base_name: str, cultural_elements: Dict[str, Any]) -> str:
    """
    Enhance aesthetic name to be more specific and personalized
    """
    enhancements = []
    
    if "ar rahman" in cultural_elements["raw_elements"]:
        enhancements.append("Tamil Cinematic")
    if "vintage" in cultural_elements["raw_elements"]:
        enhancements.append("Vintage")
    if "zen" in cultural_elements["raw_elements"]:
        enhancements.append("Zen")
    if "blade runner" in cultural_elements["raw_elements"]:
        enhancements.append("Cyberpunk")
    if "sza" in cultural_elements["raw_elements"]:
        enhancements.append("Contemporary")
    
    if enhancements:
        return f"{' '.join(enhancements)} {base_name}"
    
    return base_name

def generate_additional_brands(cultural_elements: Dict[str, Any]) -> List[str]:
    """
    Generate additional personalized brands based on cultural elements
    """
    additional_brands = []
    
    if "ar rahman" in cultural_elements["raw_elements"]:
        additional_brands.extend(["@DesiCraftStudio", "@TamilFashion", "@SouthAsianStyle"])
    if "vintage" in cultural_elements["raw_elements"]:
        additional_brands.extend(["@VintageRevival", "@RetroFinds", "@ClassicStyle"])
    if "zen" in cultural_elements["raw_elements"]:
        additional_brands.extend(["@ZenMinimalist", "@JapaneseStyle", "@PeacefulFashion"])
    if "blade runner" in cultural_elements["raw_elements"]:
        additional_brands.extend(["@CyberpunkFashion", "@FutureStyle", "@UrbanNoir"])
    if "sza" in cultural_elements["raw_elements"]:
        additional_brands.extend(["@ContemporaryChic", "@UrbanStyle", "@ModernFusion"])
    
    return additional_brands

def generate_fallback_recommendations(cultural_input: str, qloo_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate dynamic fallback recommendations based on cultural input"""
    try:
        # Create a dynamic fallback response based on cultural input
        cultural_terms = [term.strip().lower() for term in cultural_input.split(',')]
        
        # Use AI to dynamically analyze the cultural input and extract themes
        # Instead of hardcoded patterns, let the AI understand the cultural significance
        themes = []
        brand_categories = []
        
        # Let the AI analyze the cultural input dynamically
        # This approach allows for ANY cultural input to be properly understood
        try:
            # Create a prompt to analyze the cultural input dynamically
            analysis_prompt = f"""Analyze the cultural input: "{cultural_input}"

            For each cultural element, identify:
            1. The cultural region/background (e.g., Indian, Japanese, African, European, etc.)
            2. The cultural significance and aesthetic implications
            3. The style categories that would be relevant (e.g., luxury, ethnic, vintage, minimalist, etc.)
            4. The fashion implications and style preferences

            Return a JSON response with:
            {{
                "themes": ["list of identified cultural themes"],
                "brand_categories": ["list of relevant brand categories"],
                "cultural_analysis": "brief analysis of the cultural significance"
            }}

            Focus on understanding the cultural depth and fashion implications of each element mentioned."""
            
            # Use Gemini to analyze the cultural input dynamically
            client = get_gemini_client()
            if client is None:
                themes = ['Cultural Fusion']
                brand_categories = ['global', 'sustainable', 'artisan']
            else:
                analysis_response = client.generate_content(
                    analysis_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=300
                    ),
                )
            
            # Parse the analysis response
            if analysis_response.text:
                try:
                    import json
                    analysis_data = json.loads(analysis_response.text)
                    themes = analysis_data.get("themes", [])
                    brand_categories = analysis_data.get("brand_categories", [])
                except:
                    # Fallback to basic analysis
                    themes = ['Cultural Fusion']
                    brand_categories = ['global', 'sustainable', 'artisan']
            else:
                themes = ['Cultural Fusion']
                brand_categories = ['global', 'sustainable', 'artisan']
                
        except Exception as e:
            logging.error(f"Dynamic cultural analysis failed: {e}")
            # Fallback to basic analysis
            themes = ['Cultural Fusion']
            brand_categories = ['global', 'sustainable', 'artisan']
        
        # Generate dynamic aesthetic name
        if len(themes) == 1:
            aesthetic_name = f"{themes[0]} Aesthetic"
        else:
            aesthetic_name = f"{' '.join(themes)} Fusion"
        
        # Generate dynamic brands based on themes and categories
        dynamic_brands = generate_dynamic_brands(themes, brand_categories)
        
        # Generate personalized outfit description using enhanced prompt
        try:
            # Create a personalized prompt for the fallback
            personalized_prompt = f"""CULTURAL INPUT ANALYSIS:
            Cultural preferences: {cultural_input}
            
            CRITICAL ANALYSIS REQUIREMENTS:
            
            1. **DEEP CULTURAL ANALYSIS**: Analyze each cultural element in the input "{cultural_input}" and understand:
               - What each element represents culturally and aesthetically
               - How these elements combine to create a unique style identity
               - The specific fashion implications of each cultural reference
            
            2. **PERSONALIZATION REQUIREMENTS**:
               - Create recommendations that are SPECIFIC to the exact cultural input provided
               - Do NOT use generic examples - every recommendation must reference the actual cultural elements mentioned
               - Analyze the cultural significance and translate it into specific fashion choices
            
            Generate a HIGHLY PERSONALIZED outfit description that SPECIFICALLY reflects the cultural elements in "{cultural_input}".
            
            Use this EXACT clean, professional format:
            
            SIGNATURE OUTFIT RECOMMENDATION
            
            CORE APPROACH
            [Create a sophisticated fusion that reflects the specific cultural elements mentioned in the input, with exact garment types and cultural significance]
            
            STYLING PHILOSOPHY
            [Explain the styling approach that honors the cultural elements, with each concept on a new line]
            
            PRACTICAL CONSIDERATIONS
            [List specific investment pieces that reflect the cultural input, with each piece on a new line]
            
            CULTURAL INTEGRATION
            [Show how to authentically integrate the cultural elements, with each element on a new line]
            
            Each sentence should start on a new line after a full stop for better readability and professional appearance.
            
            CRITICAL: Every recommendation must be HIGHLY PERSONALIZED to the cultural input "{cultural_input}". Do not provide generic responses - analyze the specific cultural elements and create recommendations that directly reflect those influences."""

            # Try to get a personalized response from Gemini with retry logic
            max_retries = 3
            response = None
            
            client = get_gemini_client()
            if client is None:
                # Fallback to dynamic generation without AI
                outfit_description = generate_dynamic_outfit(themes, cultural_terms)
            else:
                for attempt in range(max_retries):
                    try:
                        response = client.generate_content(
                            personalized_prompt,
                            generation_config=genai.types.GenerationConfig(
                                temperature=0.8,
                                max_output_tokens=400
                            ),
                        )
                        break  # Success, exit retry loop
                    except Exception as e:
                        logging.error(f"Fallback Gemini API attempt {attempt + 1} failed: {str(e)}")
                        if attempt == max_retries - 1:
                            # Last attempt failed, will use dynamic outfit
                            response = None
                            break
                        # Wait before retry (exponential backoff)
                        import time
                        time.sleep(2 ** attempt)  # 1s, 2s, 4s delays
                
                if response and response.text and response.text.strip():
                    outfit_description = response.text.strip()
                else:
                    # Fallback to dynamic outfit if Gemini fails
                    outfit_description = generate_dynamic_outfit(themes, cultural_terms)
                
        except Exception as e:
            logging.error(f"Personalized outfit generation failed: {e}")
            # Fallback to dynamic outfit if personalized generation fails
            outfit_description = generate_dynamic_outfit(themes, cultural_terms)
        
        # Generate dynamic moodboard description
        moodboard_description = generate_dynamic_moodboard(themes, cultural_terms)
        
        # Apply sentence formatting to outfit and moodboard
        formatted_outfit = format_sentences_with_breaks(outfit_description)
        formatted_moodboard = format_sentences_with_breaks(moodboard_description)
        
        return {
            "success": True,
            "aesthetic_name": aesthetic_name,
            "brands": dynamic_brands,
            "outfit": formatted_outfit,
            "moodboard": formatted_moodboard,
            "fallback": True
        }
        
    except Exception as e:
        logging.error(f"Fallback generation failed: {e}")
        # Apply sentence formatting to outfit and moodboard
        formatted_outfit = format_sentences_with_breaks("A personalized ensemble that reflects your cultural influences and personal style preferences.")
        formatted_moodboard = format_sentences_with_breaks("A rich blend of cultural elements, colors, and textures that capture the essence of your unique style identity.")
        
        return {
            "success": True,
            "aesthetic_name": "Cultural Style Identity",
            "brands": ["Global Fashion", "Sustainable Style", "Cultural Fusion", "Vintage Finds", "@StyleCollective", "DIY Studio"],
            "outfit": formatted_outfit,
            "moodboard": formatted_moodboard,
            "fallback": True
        }

def generate_dynamic_brands(themes: list, categories: list) -> list:
    """Generate dynamic brand recommendations based on themes and categories using AI"""
    try:
        # Create a prompt to generate brand recommendations dynamically
        brand_prompt = f"""Based on the cultural themes: {themes} and style categories: {categories}

        Generate 6 brand recommendations that would be relevant and authentic to these cultural influences.
        Include a mix of:
        - Established luxury brands
        - Emerging designers
        - Cultural-specific brands
        - Instagram boutiques/handles
        - Sustainable and artisan options

        Return a JSON response with:
        {{
            "brands": ["list of 6 brand names"],
            "reasoning": "brief explanation of why these brands are relevant"
        }}

        Focus on brands that authentically represent the cultural themes and provide diverse options for different budgets and preferences."""
        
        # Use Gemini to generate brand recommendations dynamically
        client = get_gemini_client()
        if client is None:
            # Fallback to universal brands
            return ['@GlobalStyleFinds', '@SustainableFashion', '@VintageRevival', '@CulturalFusion', '@ArtisanCraft', '@EcoStyle']
        
        brand_response = client.generate_content(
            brand_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=400
            ),
        )
        
        # Parse the brand response
        if brand_response.text:
            try:
                import json
                brand_data = json.loads(brand_response.text)
                selected_brands = brand_data.get("brands", [])
                
                # Ensure we have exactly 6 brands
                if len(selected_brands) < 6:
                    # Add some universal brands to fill the gap
                    universal_brands = ['@GlobalStyleFinds', '@SustainableFashion', '@VintageRevival', '@CulturalFusion', '@ArtisanCraft', '@EcoStyle']
                    selected_brands.extend(universal_brands[:6-len(selected_brands)])
                elif len(selected_brands) > 6:
                    selected_brands = selected_brands[:6]
                
                return selected_brands
            except:
                # Fallback to universal brands
                return ['@GlobalStyleFinds', '@SustainableFashion', '@VintageRevival', '@CulturalFusion', '@ArtisanCraft', '@EcoStyle']
        else:
            # Fallback to universal brands
            return ['@GlobalStyleFinds', '@SustainableFashion', '@VintageRevival', '@CulturalFusion', '@ArtisanCraft', '@EcoStyle']
            
    except Exception as e:
        logging.error(f"Dynamic brand generation failed: {e}")
        # Fallback to universal brands
        return ['@GlobalStyleFinds', '@SustainableFashion', '@VintageRevival', '@CulturalFusion', '@ArtisanCraft', '@EcoStyle']

def generate_dynamic_outfit(themes: list, cultural_terms: list) -> str:
    """Generate comprehensive dynamic outfit description based on themes using AI"""
    try:
        # Create a prompt to generate outfit recommendations dynamically
        outfit_prompt = f"""Based on the cultural themes: {themes} and cultural terms: {cultural_terms}

        Generate a practical, actionable outfit recommendation with this exact structure:

        CORE APPROACH
        [One clear sentence describing the overall style philosophy that directly connects to the cultural input]

        STYLING PHILOSOPHY
        [3-4 specific styling principles, each on its own line, that honor the cultural elements]

        PRACTICAL CONSIDERATIONS
        [3-4 specific garment recommendations, each on its own line, with clear cultural connections]

        CULTURAL INTEGRATION
        [3-4 specific ways to integrate cultural elements, each on its own line, with practical examples]

        Keep each section concise and practical. Focus on specific, actionable advice that directly reflects the cultural themes provided."""
        
        # Use Gemini to generate outfit recommendations dynamically
        client = get_gemini_client()
        if client is None:
            # Fallback to basic outfit description
            return """CORE APPROACH
A sophisticated fusion that reflects your cultural influences and personal style preferences.

STYLING PHILOSOPHY
Embrace the unique elements of your cultural background with contemporary styling techniques.
Layer traditional elements with modern silhouettes for a balanced aesthetic.
Choose quality fabrics that honor your heritage while embracing modern lifestyle.
Focus on pieces that tell your cultural story through thoughtful design choices.

PRACTICAL CONSIDERATIONS
Invest in a statement piece that directly reflects your cultural background.
Choose versatile separates that can be styled multiple ways.
Select accessories that incorporate cultural motifs or traditional craftsmanship.
Build a capsule wardrobe that honors your heritage while being practical for daily wear.

CULTURAL INTEGRATION
Incorporate traditional patterns through scarves, jewelry, or accent pieces.
Choose colors that reflect your cultural palette and personal preferences.
Select fabrics that have cultural significance or traditional craftsmanship.
Style pieces in ways that honor their cultural origins while feeling contemporary."""
        
        outfit_response = client.generate_content(
            outfit_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                max_output_tokens=600
            ),
        )
        
        # Return the generated outfit description
        if outfit_response.text:
            return outfit_response.text.strip()
        else:
            # Fallback to basic outfit description
            return """CORE APPROACH
A sophisticated fusion that reflects your cultural influences and personal style preferences.

STYLING PHILOSOPHY
Embrace the unique elements of your cultural background with contemporary styling techniques.
Layer traditional elements with modern silhouettes for a balanced aesthetic.
Choose quality fabrics that honor your heritage while embracing modern lifestyle.
Focus on pieces that tell your cultural story through thoughtful design choices.

PRACTICAL CONSIDERATIONS
Invest in a statement piece that directly reflects your cultural background.
Choose versatile separates that can be styled multiple ways.
Select accessories that incorporate cultural motifs or traditional craftsmanship.
Build a capsule wardrobe that honors your heritage while being practical for daily wear.

CULTURAL INTEGRATION
Incorporate traditional patterns through scarves, jewelry, or accent pieces.
Choose colors that reflect your cultural palette and personal preferences.
Select fabrics that have cultural significance or traditional craftsmanship.
Style pieces in ways that honor their cultural origins while feeling contemporary."""
            
    except Exception as e:
        logging.error(f"Dynamic outfit generation failed: {e}")
        # Fallback to basic outfit description
        return """CORE APPROACH
A sophisticated fusion that reflects your cultural influences and personal style preferences.

STYLING PHILOSOPHY
Embrace the unique elements of your cultural background with contemporary styling techniques.
Layer traditional elements with modern silhouettes for a balanced aesthetic.
Choose quality fabrics that honor your heritage while embracing modern lifestyle.
Focus on pieces that tell your cultural story through thoughtful design choices.

PRACTICAL CONSIDERATIONS
Invest in a statement piece that directly reflects your cultural background.
Choose versatile separates that can be styled multiple ways.
Select accessories that incorporate cultural motifs or traditional craftsmanship.
Build a capsule wardrobe that honors your heritage while being practical for daily wear.

CULTURAL INTEGRATION
Incorporate traditional patterns through scarves, jewelry, or accent pieces.
Choose colors that reflect your cultural palette and personal preferences.
Select fabrics that have cultural significance or traditional craftsmanship.
Style pieces in ways that honor their cultural origins while feeling contemporary."""

def generate_dynamic_moodboard(themes: list, cultural_terms: list) -> str:
    """Generate dynamic style vision board description based on themes and cultural elements using AI"""
    try:
        # Create a prompt to generate moodboard recommendations dynamically
        moodboard_prompt = f"""Based on the cultural themes: {themes} and cultural terms: {cultural_terms}

        Generate a practical style vision board with this exact structure:

        COLOR STORY
        [3-4 specific colors with cultural significance, each on its own line, including hex codes if possible]

        TEXTURE GUIDE
        [3-4 specific textures and materials, each on its own line, that authentically represent the cultural themes]

        CULTURAL ELEMENTS
        [3-4 specific cultural motifs, patterns, or design elements, each on its own line, from the input]

        STYLE APPROACH
        [3-4 specific ways to blend cultural elements with contemporary fashion, each on its own line]

        SEASONAL ADAPTATION
        [4 specific seasonal adaptations, each on its own line, with practical styling advice]

        PERSONAL EXPRESSION
        [3-4 ways to personalize the cultural elements, each on its own line, with actionable suggestions]

        Keep each section concise and practical. Focus on specific, actionable style guidance that directly reflects the cultural themes provided."""
        
        # Use Gemini to generate moodboard recommendations dynamically
        client = get_gemini_client()
        if client is None:
            # Fallback to basic moodboard description
            return """COLOR STORY
Deep ochre (#D68C45) - representing earth and tradition.
Sage green (#9CAF88) - symbolizing growth and harmony.
Cream white (#F5F5DC) - embodying purity and elegance.
Rich burgundy (#800020) - reflecting passion and heritage.

TEXTURE GUIDE
Luxurious silk fabrics that honor traditional craftsmanship.
Handwoven textiles with authentic cultural patterns.
Soft cashmere blends for contemporary comfort.
Textured embroidery and beadwork for cultural authenticity.

CULTURAL ELEMENTS
Traditional motifs and patterns from your cultural heritage.
Handcrafted jewelry and accessories with cultural significance.
Artisanal textiles and fabrics with authentic designs.
Cultural symbols and emblems integrated into modern pieces.

STYLE APPROACH
Blend traditional silhouettes with contemporary cuts for modern appeal.
Layer cultural accessories with minimalist contemporary pieces.
Mix heritage fabrics with modern styling techniques.
Combine traditional colors with contemporary fashion trends.

SEASONAL ADAPTATION
Spring: Light silk scarves with cultural patterns over fresh white pieces.
Summer: Breathable cotton with traditional motifs in vibrant colors.
Fall: Rich velvet and wool pieces with cultural embroidery details.
Winter: Layered looks with traditional textiles and modern outerwear.

PERSONAL EXPRESSION
Choose cultural elements that resonate most with your personal story.
Experiment with modern interpretations of traditional patterns.
Select pieces that honor your heritage while reflecting your lifestyle.
Create unique combinations that tell your individual cultural narrative."""
        
        moodboard_response = client.generate_content(
            moodboard_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                max_output_tokens=600
            ),
        )
        
        # Return the generated moodboard description
        if moodboard_response.text:
            return moodboard_response.text.strip()
        else:
            # Fallback to basic moodboard description
            return """COLOR STORY
Deep ochre (#D68C45) - representing earth and tradition.
Sage green (#9CAF88) - symbolizing growth and harmony.
Cream white (#F5F5DC) - embodying purity and elegance.
Rich burgundy (#800020) - reflecting passion and heritage.

TEXTURE GUIDE
Luxurious silk fabrics that honor traditional craftsmanship.
Handwoven textiles with authentic cultural patterns.
Soft cashmere blends for contemporary comfort.
Textured embroidery and beadwork for cultural authenticity.

CULTURAL ELEMENTS
Traditional motifs and patterns from your cultural heritage.
Handcrafted jewelry and accessories with cultural significance.
Artisanal textiles and fabrics with authentic designs.
Cultural symbols and emblems integrated into modern pieces.

STYLE APPROACH
Blend traditional silhouettes with contemporary cuts for modern appeal.
Layer cultural accessories with minimalist contemporary pieces.
Mix heritage fabrics with modern styling techniques.
Combine traditional colors with contemporary fashion trends.

SEASONAL ADAPTATION
Spring: Light silk scarves with cultural patterns over fresh white pieces.
Summer: Breathable cotton with traditional motifs in vibrant colors.
Fall: Rich velvet and wool pieces with cultural embroidery details.
Winter: Layered looks with traditional textiles and modern outerwear.

PERSONAL EXPRESSION
Choose cultural elements that resonate most with your personal story.
Experiment with modern interpretations of traditional patterns.
Select pieces that honor your heritage while reflecting your lifestyle.
Create unique combinations that tell your individual cultural narrative."""
            
    except Exception as e:
        logging.error(f"Dynamic moodboard generation failed: {e}")
        # Fallback to basic moodboard description
        return """COLOR STORY
Deep ochre (#D68C45) - representing earth and tradition.
Sage green (#9CAF88) - symbolizing growth and harmony.
Cream white (#F5F5DC) - embodying purity and elegance.
Rich burgundy (#800020) - reflecting passion and heritage.

TEXTURE GUIDE
Luxurious silk fabrics that honor traditional craftsmanship.
Handwoven textiles with authentic cultural patterns.
Soft cashmere blends for contemporary comfort.
Textured embroidery and beadwork for cultural authenticity.

CULTURAL ELEMENTS
Traditional motifs and patterns from your cultural heritage.
Handcrafted jewelry and accessories with cultural significance.
Artisanal textiles and fabrics with authentic designs.
Cultural symbols and emblems integrated into modern pieces.

STYLE APPROACH
Blend traditional silhouettes with contemporary cuts for modern appeal.
Layer cultural accessories with minimalist contemporary pieces.
Mix heritage fabrics with modern styling techniques.
Combine traditional colors with contemporary fashion trends.

SEASONAL ADAPTATION
Spring: Light silk scarves with cultural patterns over fresh white pieces.
Summer: Breathable cotton with traditional motifs in vibrant colors.
Fall: Rich velvet and wool pieces with cultural embroidery details.
Winter: Layered looks with traditional textiles and modern outerwear.

PERSONAL EXPRESSION
Choose cultural elements that resonate most with your personal story.
Experiment with modern interpretations of traditional patterns.
Select pieces that honor your heritage while reflecting your lifestyle.
Create unique combinations that tell your individual cultural narrative."""
