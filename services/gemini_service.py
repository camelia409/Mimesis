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

IMPORTANT: Brand recommendations must be highly personalized and diverse based on the cultural input. Consider:
- Cultural heritage and regional fashion influences
- Mix of luxury, contemporary, vintage, and sustainable brands
- Global diversity (not just Western brands)
- Instagram boutiques and independent designers
- Cultural fusion and cross-cultural influences

Respond with a JSON object containing:
- aesthetic_name: A unique, creative style identity that reflects the cultural input (e.g., "Vintage Tamil Cinematic Maestro", "Cyberpunk Zen Minimalist")
- brands: Array of 6 highly personalized brand suggestions that directly relate to the cultural input. Mix luxury, indie, thrift, and DIY options from diverse global markets. MUST include at least 1 Instagram boutique handle (e.g., @DesiCraftStudio, @TokyoStreetFashion, @BerlinVintageFinds). Brands should reflect the specific cultural themes identified.
- outfit: Detailed outfit description with specific pieces, colors, styling, and cultural context. Include layering suggestions, accessories, and how each element connects to the cultural influences.
- moodboard: Rich, evocative description of the aesthetic world. Include specific colors, textures, architectural elements, cultural motifs, lighting, atmosphere, and visual themes. Make it vivid enough that someone could use this description to create a moodboard or find inspiration. Include cultural references, historical periods, artistic movements, and sensory details."""

        user_prompt = f"""Cultural preferences: {cultural_input}

{archetypes_context}

Generate highly personalized fashion recommendations that capture the essence of these cultural influences. 

CRITICAL: The brand recommendations must be specifically tailored to the cultural input provided. Analyze the cultural elements and suggest brands that directly relate to those influences. For example:
- If Indian/Bollywood elements are mentioned, include Indian designers and South Asian fashion brands
- If Japanese/Korean elements are mentioned, include Asian fashion brands and streetwear
- If vintage/retro elements are mentioned, include vintage and heritage brands
- If cyberpunk/futuristic elements are mentioned, include avant-garde and tech fashion brands

Be creative, inclusive, and consider sustainability. Ensure brand diversity and global representation. If no specific archetypes are provided, create a unique aesthetic based on the cultural input."""

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
    """Generate dynamic fallback recommendations based on cultural input"""
    try:
        # Create a dynamic fallback response based on cultural input
        cultural_terms = [term.strip().lower() for term in cultural_input.split(',')]
        
        # Extract key themes and cultural elements
        themes = []
        brand_categories = []
        
        # Indian/South Asian influences
        if any(term in ['indian', 'bollywood', 'rahman', 'tamil', 'hindi', 'sari', 'kurta', 'south asian'] for term in cultural_terms):
            themes.append('Indian')
            brand_categories.extend(['ethnic', 'luxury', 'artisan'])
        
        # Japanese/Korean influences
        if any(term in ['japanese', 'korean', 'zen', 'minimalist', 'tokyo', 'seoul', 'kawaii', 'streetwear'] for term in cultural_terms):
            themes.append('Japanese/Korean')
            brand_categories.extend(['minimalist', 'streetwear', 'luxury'])
        
        # Western/American influences
        if any(term in ['western', 'cowboy', 'americana', 'vintage', 'retro', 'classic'] for term in cultural_terms):
            themes.append('Western')
            brand_categories.extend(['vintage', 'heritage', 'luxury'])
        
        # Cyberpunk/Futuristic influences
        if any(term in ['cyberpunk', 'futuristic', 'matrix', 'sci-fi', 'tech', 'digital'] for term in cultural_terms):
            themes.append('Cyberpunk')
            brand_categories.extend(['avant-garde', 'tech', 'streetwear'])
        
        # European influences
        if any(term in ['french', 'italian', 'european', 'paris', 'milan', 'romantic', 'elegant'] for term in cultural_terms):
            themes.append('European')
            brand_categories.extend(['luxury', 'elegant', 'heritage'])
        
        # African influences
        if any(term in ['african', 'afro', 'tribal', 'ethnic', 'wax print', 'ankara'] for term in cultural_terms):
            themes.append('African')
            brand_categories.extend(['ethnic', 'artisan', 'sustainable'])
        
        # Latin American influences
        if any(term in ['latin', 'mexican', 'brazilian', 'caribbean', 'tropical', 'vibrant'] for term in cultural_terms):
            themes.append('Latin American')
            brand_categories.extend(['vibrant', 'artisan', 'sustainable'])
        
        # Vintage/Retro influences
        if any(term in ['vintage', 'retro', '50s', '60s', '70s', '80s', '90s', 'classic'] for term in cultural_terms):
            themes.append('Vintage')
            brand_categories.extend(['vintage', 'heritage', 'sustainable'])
        
        # If no specific themes found, create a fusion aesthetic
        if not themes:
            themes = ['Cultural Fusion']
            brand_categories = ['global', 'sustainable', 'artisan']
        
        # Generate dynamic aesthetic name
        if len(themes) == 1:
            aesthetic_name = f"{themes[0]} Aesthetic"
        else:
            aesthetic_name = f"{' '.join(themes)} Fusion"
        
        # Generate dynamic brands based on themes and categories
        dynamic_brands = generate_dynamic_brands(themes, brand_categories)
        
        # Generate dynamic outfit description
        outfit_description = generate_dynamic_outfit(themes, cultural_terms)
        
        # Generate dynamic moodboard description
        moodboard_description = generate_dynamic_moodboard(themes, cultural_terms)
        
        return {
            "success": True,
            "aesthetic_name": aesthetic_name,
            "brands": dynamic_brands,
            "outfit": outfit_description,
            "moodboard": moodboard_description,
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

def generate_dynamic_brands(themes: list, categories: list) -> list:
    """Generate dynamic brand recommendations based on themes and categories"""
    brand_database = {
        'indian': {
            'luxury': ['Anita Dongre', 'Sabyasachi', 'Manish Malhotra'],
            'ethnic': ['Fabindia', 'Biba', 'W for Woman'],
            'artisan': ['@DesiCraftStudio', '@EthnicVibes', '@HandloomHub'],
            'sustainable': ['@EcoEthnic', '@GreenSaree', '@SustainableSilk']
        },
        'japanese/korean': {
            'minimalist': ['Uniqlo', 'Muji', 'COS'],
            'streetwear': ['BAPE', 'Comme des Garçons', 'Off-White'],
            'luxury': ['Issey Miyake', 'Yohji Yamamoto', 'Sacai'],
            'kawaii': ['@KawaiiFashion', '@TokyoStyle', '@SeoulVibes']
        },
        'western': {
            'vintage': ['Levi\'s Vintage', 'Carhartt', 'Filson'],
            'heritage': ['Ralph Lauren', 'Tommy Hilfiger', 'Brooks Brothers'],
            'luxury': ['Ralph Lauren Purple Label', 'Tom Ford', 'Saint Laurent'],
            'sustainable': ['@VintageWestern', '@HeritageStyle', '@CowboyChic']
        },
        'cyberpunk': {
            'avant-garde': ['Rick Owens', 'Balenciaga', 'Vetements'],
            'tech': ['@CyberFashion', '@TechWear', '@DigitalStyle'],
            'streetwear': ['Off-White', 'Supreme', 'Palace'],
            'luxury': ['@NeoFuturist', '@DigitalLuxe', '@TechCouture']
        },
        'european': {
            'luxury': ['Chanel', 'Dior', 'Hermès'],
            'elegant': ['Celine', 'Bottega Veneta', 'Loewe'],
            'heritage': ['Burberry', 'Aquascutums', 'Barbour'],
            'sustainable': ['@ParisianChic', '@MilanStyle', '@EuropeanElegance']
        },
        'african': {
            'ethnic': ['@AfricanPrints', '@WaxPrintStyle', '@AnkaraFashion'],
            'artisan': ['@HandmadeAfrica', '@TribalCraft', '@AfricanArtisan'],
            'sustainable': ['@EcoAfrica', '@SustainableWax', '@GreenAnkara'],
            'luxury': ['@LuxeAfrica', '@AfricanCouture', '@TribalLuxe']
        },
        'latin american': {
            'vibrant': ['@LatinVibes', '@TropicalStyle', '@CaribbeanChic'],
            'artisan': ['@HandmadeLatina', '@ArtisanCraft', '@LatinCraft'],
            'sustainable': ['@EcoLatina', '@GreenTropical', '@SustainableVibes'],
            'luxury': ['@LuxeLatina', '@LatinCouture', '@TropicalLuxe']
        },
        'vintage': {
            'vintage': ['@VintageFinds', '@RetroStyle', '@ClassicVintage'],
            'heritage': ['@HeritageStyle', '@TimelessFashion', '@ClassicChic'],
            'sustainable': ['@EcoVintage', '@GreenRetro', '@SustainableClassic'],
            'luxury': ['@VintageLuxe', '@RetroCouture', '@ClassicLuxe']
        },
        'cultural fusion': {
            'global': ['@GlobalStyle', '@FusionFashion', '@CulturalMix'],
            'sustainable': ['@EcoFusion', '@GreenGlobal', '@SustainableMix'],
            'artisan': ['@HandmadeGlobal', '@ArtisanFusion', '@CraftMix']
        }
    }
    
    selected_brands = []
    
    # Select brands based on themes and categories
    for theme in themes:
        theme_lower = theme.lower()
        if theme_lower in brand_database:
            for category in categories:
                if category in brand_database[theme_lower]:
                    # Add 1-2 brands from each category
                    brands = brand_database[theme_lower][category]
                    selected_brands.extend(brands[:2])
    
    # Ensure we have exactly 6 brands
    if len(selected_brands) < 6:
        # Add some universal brands
        universal_brands = ['@GlobalStyleFinds', '@SustainableFashion', '@VintageRevival', '@CulturalFusion', '@ArtisanCraft', '@EcoStyle']
        selected_brands.extend(universal_brands[:6-len(selected_brands)])
    elif len(selected_brands) > 6:
        selected_brands = selected_brands[:6]
    
    return selected_brands

def generate_dynamic_outfit(themes: list, cultural_terms: list) -> str:
    """Generate dynamic outfit description based on themes"""
    outfit_templates = {
        'indian': "A fusion of traditional Indian elegance with contemporary flair. Think silk kurtas paired with modern denim, statement jewelry that bridges heritage and current trends, and footwear that combines comfort with cultural authenticity. Layer with a lightweight dupatta or scarf for added dimension.",
        'japanese/korean': "Clean lines and minimalist sophistication define this aesthetic. Structured blazers over crisp white shirts, wide-leg trousers with precise tailoring, and accessories that emphasize quality over quantity. Footwear balances comfort with sleek design, while layering creates depth without clutter.",
        'western': "Heritage meets modern sensibility with denim jackets, vintage-inspired shirts, and boots that tell a story. Mix classic silhouettes with contemporary details, add leather accessories for authenticity, and layer with timeless pieces that transcend seasons.",
        'cyberpunk': "Futuristic streetwear with avant-garde elements. Oversized silhouettes, technical fabrics, and bold accessories create a look that's both edgy and sophisticated. Mix high-tech materials with streetwear staples, and add statement pieces that push boundaries.",
        'european': "Timeless elegance with contemporary refinement. Structured coats, tailored separates, and quality accessories that speak to heritage and craftsmanship. Focus on fit, fabric, and details that elevate everyday pieces to luxury status.",
        'african': "Vibrant prints and bold colors celebrate cultural heritage. Mix traditional wax prints with modern silhouettes, add statement jewelry that honors craftsmanship, and layer with pieces that tell stories of tradition and innovation.",
        'latin american': "Tropical vibes meet urban sophistication. Bright colors, flowing fabrics, and accessories that celebrate cultural heritage. Mix traditional elements with contemporary pieces, and add touches that reflect the warmth and vibrancy of Latin culture.",
        'vintage': "Timeless pieces with retro charm. Mix eras thoughtfully, layer vintage finds with modern basics, and accessorize with pieces that have character and history. Focus on quality over quantity and pieces that tell a story."
    }
    
    # Select primary theme for outfit
    primary_theme = themes[0].lower() if themes else 'cultural fusion'
    
    if primary_theme in outfit_templates:
        return outfit_templates[primary_theme]
    else:
        return "A personalized ensemble that reflects your cultural influences and personal style preferences, combining traditional elements with contemporary pieces to create a unique aesthetic that celebrates your heritage while embracing modern sensibilities."

def generate_dynamic_moodboard(themes: list, cultural_terms: list) -> str:
    """Generate dynamic moodboard description based on themes"""
    moodboard_templates = {
        'indian': "Rich jewel tones and warm earth colors create a palette of deep burgundies, golden yellows, and emerald greens. Textures range from smooth silk to intricate embroidery, while architectural elements draw from Mughal palaces and modern Indian cities. Cultural motifs include paisleys, mandalas, and geometric patterns, all bathed in warm, golden lighting that evokes the magic of Indian cinema and traditional celebrations.",
        'japanese/korean': "Clean, minimalist aesthetics with a focus on natural materials and neutral tones. Think soft grays, warm whites, and subtle earth tones. Textures emphasize natural fibers, smooth surfaces, and precise craftsmanship. Architectural elements reflect Zen principles and modern urban design, while cultural motifs include cherry blossoms, geometric patterns, and calligraphic elements. Lighting is soft and natural, creating a sense of calm sophistication.",
        'western': "Warm, earthy tones dominate with rich browns, deep blues, and natural leather colors. Textures include worn denim, soft suede, and aged leather, while architectural elements draw from rustic barns and modern ranches. Cultural motifs feature stars, horses, and geometric patterns, all illuminated by warm, golden hour lighting that creates a sense of nostalgia and authenticity.",
        'cyberpunk': "High contrast aesthetics with neon colors against dark backgrounds. Electric blues, hot pinks, and metallic silvers create a futuristic palette. Textures range from sleek metallic surfaces to distressed fabrics, while architectural elements reflect urban decay and high-tech environments. Cultural motifs include digital glitches, circuit patterns, and neon signs, all bathed in artificial lighting that creates a sense of otherworldly atmosphere.",
        'european': "Sophisticated neutrals and rich jewel tones create a palette of deep navies, warm creams, and elegant grays. Textures emphasize quality fabrics, fine tailoring, and luxurious materials. Architectural elements draw from classical European design and modern urban sophistication. Cultural motifs include fleur-de-lis, geometric patterns, and artistic elements, all illuminated by soft, elegant lighting that creates a sense of timeless beauty.",
        'african': "Vibrant, bold colors with rich earth tones and bright accents. Think deep oranges, bright yellows, and rich greens. Textures include wax prints, handwoven fabrics, and natural materials. Architectural elements draw from traditional African design and modern urban centers. Cultural motifs feature tribal patterns, animal prints, and geometric designs, all bathed in warm, natural lighting that celebrates cultural heritage.",
        'latin american': "Warm, tropical colors with bright accents and rich earth tones. Vibrant oranges, deep blues, and bright greens create a lively palette. Textures include flowing fabrics, handcrafted elements, and natural materials. Architectural elements reflect colonial heritage and modern Latin American cities. Cultural motifs include floral patterns, geometric designs, and traditional symbols, all illuminated by warm, tropical lighting that creates a sense of warmth and celebration.",
        'vintage': "Muted, nostalgic colors with warm undertones and subtle patinas. Soft pastels, warm browns, and faded jewel tones create a timeless palette. Textures include aged fabrics, worn leather, and vintage materials. Architectural elements draw from various historical periods and classic design. Cultural motifs include retro patterns, vintage graphics, and timeless symbols, all bathed in soft, nostalgic lighting that creates a sense of history and charm."
    }
    
    # Select primary theme for moodboard
    primary_theme = themes[0].lower() if themes else 'cultural fusion'
    
    if primary_theme in moodboard_templates:
        return moodboard_templates[primary_theme]
    else:
        return "A rich blend of cultural elements, colors, and textures that capture the essence of your unique style identity. The aesthetic combines traditional influences with contemporary sensibilities, creating a visual world that celebrates diversity and personal expression."

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
