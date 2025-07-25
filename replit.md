# Replit Configuration for Mimesis

## Overview

Mimesis is a cultural style intelligence engine that transforms users' cultural preferences (music, movies, games, books, etc.) into personalized fashion aesthetics. The application uses Qloo's Taste AI™ to map cultural preferences to fashion archetypes and Google's Gemini API to generate unique aesthetic names, brand recommendations, and style descriptions.

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

## System Architecture

### Backend Architecture
- **Framework**: Flask 2.3.3 with Python 3.9+
- **Structure**: Modular design with separate service layers for external API integrations
- **Entry Points**: 
  - `main.py` - Application entry point
  - `app.py` - Flask app configuration
  - `routes.py` - HTTP route handlers

### Frontend Architecture
- **Template Engine**: Jinja2 templates with HTML5
- **Styling**: Tailwind CSS (CDN) with custom CSS enhancements
- **JavaScript**: Vanilla JS for form validation and user interactions
- **Layout**: Responsive design using CSS Grid and Flexbox

### API Integration Layer
- **Qloo Service** (`services/qloo_service.py`): Handles cultural preference mapping to fashion archetypes
- **Gemini Service** (`services/gemini_service.py`): Generates style recommendations using Google's AI

## Key Components

### Core Routes
1. **GET /** - Main landing page with cultural preference input form
2. **POST /recommend** - Processes cultural input and returns style recommendations
3. **POST /chat** (planned) - Interactive AI stylist chat feature

### Service Layer
1. **Qloo Integration**:
   - Maps cultural entities to fashion archetypes
   - Handles API authentication and error responses
   - Processes comma-separated cultural inputs

2. **Gemini Integration**:
   - Generates unique aesthetic names (e.g., "Neo-Noir Luxe")
   - Creates brand recommendations across all budgets
   - Produces detailed outfit descriptions and moodboard themes
   - Uses structured JSON output with Pydantic models

### Frontend Components
1. **Input Form**: Cultural preference textarea with real-time validation
2. **Results Display**: Aesthetic identity presentation with brand suggestions
3. **Loading States**: User feedback during API processing
4. **Error Handling**: Graceful degradation when APIs fail

## Data Flow

1. **User Input**: Cultural preferences entered via web form
2. **Qloo Processing**: Cultural entities mapped to fashion archetypes
3. **Gemini Generation**: AI creates personalized style recommendations
4. **Response Rendering**: Results displayed with aesthetic name, brands, outfits, and moodboard
5. **Error Handling**: Fallback responses when external APIs fail

### Data Structure
```python
# Qloo Response
{
    "success": bool,
    "archetypes": List[str],
    "raw_response": Dict,
    "entities_processed": List[str]
}

# Gemini Response
{
    "aesthetic_name": str,
    "brands": List[str],
    "outfit": str,
    "moodboard": str
}
```

## External Dependencies

### Required APIs
1. **Qloo Taste AI™**:
   - Endpoint: `https://api.qloo.com/v1/recommendations`
   - Authentication: Bearer token
   - Purpose: Cultural preference to fashion archetype mapping

2. **Google Gemini 2.5 Flash**:
   - Model: `gemini-2.5-flash`
   - Purpose: Style recommendation generation
   - Output: Structured JSON responses

### Environment Variables
- `QLOO_API_KEY`: Qloo API authentication key
- `GEMINI_API_KEY`: Google Gemini API key
- `SESSION_SECRET`: Flask session security key

### CDN Dependencies
- Tailwind CSS: `https://cdn.tailwindcss.com`
- Font Awesome: `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css`

## Deployment Strategy

### Replit Hosting
- **Platform**: Replit cloud platform
- **Runtime**: Python 3.9+ environment
- **Port**: 5000 (Flask default)
- **Host**: 0.0.0.0 for external access

### Configuration Files
- `.replit`: Defines run command (`python main.py`)
- `replit.nix`: Specifies Python environment and dependencies
- `requirements.txt`: Python package dependencies

### Security Considerations
- Environment variables stored in Replit Secrets
- No sensitive user data collection (privacy-first design)
- Error handling prevents API key exposure
- CSRF protection via Flask session management

### Performance Optimizations
- API timeout handling (30 seconds)
- Graceful degradation when external services fail
- Client-side form validation to reduce server load
- Modular service architecture for maintainability

The application emphasizes privacy, inclusivity, and cultural intelligence while maintaining a simple, accessible user experience suitable for hackathon demonstration and future development.