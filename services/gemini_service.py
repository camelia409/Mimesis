import json
import logging
import os
from typing import Dict, Any
from google import genai
from google.genai import types
from pydantic import BaseModel

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "AIzaSyA2JL7kXFhurNWZqh__DHRghXFxUiEtW-0"))

class StyleRecommendations(BaseModel):
    aesthetic_name: str
    brands: list[str]
    outfit: str
    moodboard: str

def generate_style_recommendations(cultural_input: str, qloo_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use Gemini API to generate aesthetic names, brands, outfits, and moodboards
    """
    try:
        # Prepare context from Qloo data
        archetypes_context = ""
        if qloo_data.get("success") and qloo_data.get("archetypes"):
            archetypes_context = f"Fashion archetypes identified: {', '.join(qloo_data['archetypes'])}"
        
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
- outfit: Detailed outfit description with specific pieces, colors, and styling
- moodboard: Rich description of colors, textures, themes, and visual elements"""

        user_prompt = f"""Cultural preferences: {cultural_input}

{archetypes_context}

Generate personalized fashion recommendations that capture the essence of these cultural influences. Be creative, inclusive, and consider sustainability."""

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
                data = json.loads(raw_json)
                return {
                    "success": True,
                    "aesthetic_name": data.get("aesthetic_name", "Unique Cultural Aesthetic"),
                    "brands": data.get("brands", []),
                    "outfit": data.get("outfit", "Custom outfit based on your cultural vibe"),
                    "moodboard": data.get("moodboard", "Personalized moodboard reflecting your cultural style"),
                    "raw_response": data
                }
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse Gemini JSON response: {e}")
                return {
                    "success": False,
                    "error": "Invalid response format from AI",
                    "aesthetic_name": "Error",
                    "brands": [],
                    "outfit": "Unable to generate recommendations",
                    "moodboard": "Unable to generate moodboard"
                }
        else:
            raise ValueError("Empty response from Gemini model")

    except Exception as e:
        logging.error(f"Gemini API error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "aesthetic_name": "Error generating aesthetic",
            "brands": [],
            "outfit": "Unable to generate outfit suggestions",
            "moodboard": "Unable to generate moodboard"
        }

def chat_with_stylist(user_message: str, context: str = "") -> str:
    """
    Optional AI stylist chat feature for additional style questions
    """
    try:
        system_prompt = """You are Mimesis, a friendly AI stylist specializing in cultural style intelligence. Help users with fashion questions while maintaining your focus on:
- Cultural identity-based styling
- Inclusive, budget-conscious recommendations
- Sustainable fashion choices
- Global brand diversity
- Creative, personalized advice

Keep responses conversational, helpful, and under 200 words."""

        full_prompt = f"Context: {context}\n\nUser question: {user_message}"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=full_prompt)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=300
            ),
        )

        return response.text if response.text else "I'm having trouble responding right now. Please try again!"

    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        return "I'm having trouble responding right now. Please try again!"
