import json
import logging
import os
from typing import Dict, Any
from google import genai
from google.genai import types
from pydantic import BaseModel
import re

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "AIzaSyA2JL7kXFhurNWZqh__DHRghXFxUiEtW-0"))

class StyleRecommendations(BaseModel):
    aesthetic_name: str
    brands: list[str]
    outfit: str
    moodboard: str

def extract_largest_json(text):
    # Find all JSON objects in the text
    matches = list(re.finditer(r'\{(?:[^{}]|(?R))*\}', text, re.DOTALL))
    for match in reversed(matches):  # Try largest/last match first
        try:
            return json.loads(match.group(0))
        except Exception:
            continue
    # Try to fix common truncation (add closing braces)
    open_braces = text.count('{')
    close_braces = text.count('}')
    if open_braces > close_braces:
        fixed = text + '}' * (open_braces - close_braces)
        try:
            return json.loads(fixed)
        except Exception:
            pass
    return None

def generate_style_recommendations(cultural_input: str, qloo_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use Gemini API to generate aesthetic names, brands, outfits, and moodboards
    """
    try:
        # Prepare context from Qloo data
        archetypes_context = ""
        if qloo_data.get("success") and qloo_data.get("archetypes"):
            archetypes_context = f"Fashion archetypes identified: {', '.join(qloo_data['archetypes'])}"
        elif qloo_data.get("fallback"):
            archetypes_context = "Cultural fusion aesthetic with global influences"
        else:
            archetypes_context = "Personal cultural style identity"
        
        system_prompt = """You are Mimesis, an expert cultural style intelligence engine. Your role is to translate cultural preferences into unique, inclusive fashion aesthetics.

Key principles:
- Focus on cultural identity, not body type or income
- Provide recommendations across all budgets (luxury, indie, thrift, DIY)
- Include global and diverse brand suggestions
- Emphasize sustainability and inclusivity
- Create vivid, creative aesthetic names

Respond with a JSON object containing:
- aesthetic_name: A unique, creative style identity (e.g., "Neo-Noir Luxe", "Digital Femme Fatale")
- brands: Array of 6 brand suggestions mixing luxury, indie, thrift, and DIY options from diverse global markets. IMPORTANT: Include 1 Instagram boutique handle (e.g., @SeoulVibesStudio, @TokyoStreetFashion, @BerlinVintageFinds)
- outfit: Detailed outfit description with specific pieces, colors, styling, and cultural context. Include layering suggestions, accessories, and how each element connects to the cultural influences.
- moodboard: Rich, evocative description of the aesthetic world. Include specific colors, textures, architectural elements, cultural motifs, lighting, atmosphere, and visual themes. Make it vivid enough that someone could use this description to create a moodboard or find inspiration. Include cultural references, historical periods, artistic movements, and sensory details."""

        user_prompt = f"""Cultural preferences: {cultural_input}

{archetypes_context}

Generate personalized fashion recommendations that capture the essence of these cultural influences. Be creative, inclusive, and consider sustainability. If no specific archetypes are provided, create a unique aesthetic based on the cultural input."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=user_prompt)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=StyleRecommendations,
                temperature=0.8,  # Higher creativity
                max_output_tokens=2048
            ),
        )

        raw_json = response.text
        logging.info(f"Gemini raw response: {raw_json}")

        if raw_json:
            try:
                data = extract_largest_json(raw_json)
                if data:
                    return {
                        "success": True,
                        "aesthetic_name": data.get("aesthetic_name", "Unique Cultural Aesthetic"),
                        "brands": data.get("brands", []),
                        "outfit": data.get("outfit", "Custom outfit based on your cultural vibe"),
                        "moodboard": data.get("moodboard", "Personalized moodboard reflecting your cultural style"),
                        "raw_response": data
                    }
                else:
                    logging.error(f"Failed to extract valid JSON from Gemini response. Raw: {raw_json}")
                    return generate_fallback_recommendations(cultural_input, qloo_data)
            except Exception as e:
                logging.error(f"Failed to robustly parse Gemini JSON response: {e}\nRaw: {raw_json}")
                return generate_fallback_recommendations(cultural_input, qloo_data)
        else:
            logging.warning("Empty response from Gemini, using fallback")
            return generate_fallback_recommendations(cultural_input, qloo_data)

    except Exception as e:
        logging.error(f"Gemini API error: {str(e)}")
        return generate_fallback_recommendations(cultural_input, qloo_data)

def generate_fallback_recommendations(cultural_input: str, qloo_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate fallback recommendations when Gemini fails"""
    try:
        # Create a simple fallback response based on cultural input
        cultural_terms = cultural_input.lower().split(',')
        
        # Extract key themes
        themes = []
        if any('indian' in term or 'bollywood' in term or 'rahman' in term for term in cultural_terms):
            themes.append('Indian')
        if any('cyberpunk' in term or 'futuristic' in term or 'matrix' in term for term in cultural_terms):
            themes.append('Cyberpunk')
        if any('vintage' in term or 'retro' in term for term in cultural_terms):
            themes.append('Vintage')
        if any('japanese' in term or 'zen' in term for term in cultural_terms):
            themes.append('Japanese')
        if any('western' in term or 'cowboy' in term for term in cultural_terms):
            themes.append('Western')
        
        if not themes:
            themes = ['Cultural Fusion']
        
        aesthetic_name = f"{' '.join(themes)} Aesthetic"
        
        # Generate fallback content
        fallback_brands = [
            "Global Fashion Collective",
            "Sustainable Style Hub", 
            "Vintage Revival",
            "Cultural Fusion Boutique",
            "@GlobalStyleFinds",
            "DIY Fashion Studio"
        ]
        
        fallback_outfit = f"A {themes[0].lower()} inspired ensemble featuring cultural elements, sustainable materials, and global influences. The outfit combines traditional and contemporary pieces to create a unique personal style that celebrates your cultural background."
        
        fallback_moodboard = f"A rich tapestry of {', '.join(themes).lower()} influences, featuring warm earth tones, cultural motifs, and sustainable materials. The aesthetic blends traditional craftsmanship with modern sensibilities, creating a unique fusion that honors diverse cultural heritage while embracing contemporary style."
        
        return {
            "success": True,
            "aesthetic_name": aesthetic_name,
            "brands": fallback_brands,
            "outfit": fallback_outfit,
            "moodboard": fallback_moodboard,
            "fallback": True
        }
        
    except Exception as e:
        logging.error(f"Fallback generation failed: {e}")
        return {
            "success": True,
            "aesthetic_name": "Cultural Style Identity",
            "brands": ["Global Fashion", "Sustainable Style", "Cultural Fusion", "Vintage Finds", "@StyleCollective", "DIY Studio"],
            "outfit": "A personalized ensemble that reflects your cultural influences and personal style preferences.",
            "moodboard": "A rich blend of cultural elements, colors, and textures that capture the essence of your unique style identity.",
            "fallback": True
        }

def chat_with_stylist(user_message: str, context: str = "") -> str:
    """
    Enhanced AI stylist chat feature for additional style questions
    """
    try:
        # Enhanced system prompt for better responses
        system_prompt = """You are Mimesis, a friendly and knowledgeable AI stylist specializing in cultural style intelligence. Your role is to help users with fashion questions while maintaining focus on:

- Cultural identity-based styling and personal expression
- Inclusive, budget-conscious recommendations (luxury to thrift)
- Sustainable fashion choices and eco-friendly options
- Global brand diversity and cultural fusion
- Creative, personalized advice for unique style identities

Guidelines:
- Keep responses conversational, helpful, and under 200 words
- Provide specific, actionable advice
- Include cultural context when relevant
- Suggest sustainable alternatives when possible
- Be encouraging and supportive of personal style exploration

Remember: You're helping someone discover their unique aesthetic identity through cultural influences."""

        # Create a more detailed prompt with context
        if context:
            full_prompt = f"""Context about the user's style identity:
{context}

User's current question: {user_message}

Please provide personalized advice based on their style context."""
        else:
            full_prompt = f"""User question: {user_message}

Please provide helpful fashion advice focusing on cultural style intelligence and personal expression."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=full_prompt)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.8,
                max_output_tokens=400
            ),
        )

        if response.text and response.text.strip():
            return response.text.strip()
        else:
            return generate_chat_fallback_response(user_message)

    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        return generate_chat_fallback_response(user_message)

def generate_chat_fallback_response(user_message: str) -> str:
    """Generate helpful fallback responses for chat when Gemini fails"""
    try:
        message_lower = user_message.lower()
        
        # Provide context-aware fallback responses
        if any(word in message_lower for word in ['accessor', 'jewelry', 'bag', 'shoes']):
            return "For accessories, I'd recommend focusing on pieces that complement your cultural aesthetic. Consider sustainable jewelry brands, vintage finds, or handmade pieces that reflect your personal style. Mix high and low - a statement piece with everyday basics always works!"
        
        elif any(word in message_lower for word in ['makeup', 'beauty', 'cosmetic']):
            return "Your makeup should enhance your natural beauty and complement your cultural aesthetic. Look for brands that celebrate diverse beauty standards. Consider sustainable beauty options and techniques that work with your skin type and lifestyle."
        
        elif any(word in message_lower for word in ['sustain', 'eco', 'green', 'ethical']):
            return "Great question! Sustainable fashion is all about conscious choices. Look for thrift stores, vintage shops, and brands with transparent supply chains. Consider upcycling, clothing swaps, and investing in quality pieces that last. Every small choice makes a difference!"
        
        elif any(word in message_lower for word in ['occasion', 'event', 'party', 'work']):
            return "For special occasions, think about how your cultural influences can shine through. Mix traditional elements with contemporary pieces, or use accessories to add cultural flair to classic silhouettes. Confidence is your best accessory!"
        
        elif any(word in message_lower for word in ['budget', 'cheap', 'afford', 'price']):
            return "Style doesn't have to break the bank! Thrift stores, vintage markets, and online resale platforms are treasure troves. Mix high-street basics with unique vintage finds. Remember, personal style is about creativity, not cost."
        
        else:
            return "I'd love to help you with your style question! Consider how your cultural influences can guide your choices - whether it's through colors, textures, silhouettes, or accessories. What specific aspect of your style are you looking to explore?"
            
    except Exception as e:
        logging.error(f"Fallback chat response generation failed: {e}")
        return "I'm here to help with your style questions! Feel free to ask about accessories, sustainable options, makeup, or any other fashion advice. Your unique cultural background is a great source of style inspiration."
