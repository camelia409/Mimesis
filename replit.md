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
- **Database**: PostgreSQL with SQLAlchemy ORM for data persistence
- **Structure**: Modular design with separate service layers for external API integrations
- **Entry Points**: 
  - `main.py` - Application entry point
  - `app.py` - Flask app configuration with database setup
  - `routes.py` - HTTP route handlers with database integration
  - `models.py` - SQLAlchemy database models

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
2. **POST /recommend** - Processes cultural input, stores in database, and returns style recommendations
3. **POST /chat** - Interactive AI stylist chat feature
4. **POST /feedback** - User feedback and rating system for style recommendations
5. **GET /popular** - Display popular cultural input combinations

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
3. **User Feedback System**: Star rating and text feedback for style recommendations
4. **Interactive Chat**: AI stylist chat for follow-up style questions
5. **Loading States**: User feedback during API processing
6. **Error Handling**: Graceful degradation when APIs fail

## Data Flow

1. **User Input**: Cultural preferences entered via web form
2. **Database Storage**: Request stored with user IP and cultural input
3. **Qloo Processing**: Cultural entities mapped to fashion archetypes (with error handling)
4. **Gemini Generation**: AI creates personalized style recommendations
5. **Database Update**: Complete results stored including processing time and success status
6. **Response Rendering**: Results displayed with aesthetic name, brands, outfits, and moodboard
7. **User Feedback**: Optional star rating and comments stored for continuous improvement
8. **Analytics Tracking**: Popular inputs and system metrics updated for insights

### Database Schema
```python
# StyleRequest - Core style generation requests
{
    "id": int,
    "cultural_input": str,
    "ip_address": str,
    "aesthetic_name": str,
    "brands": str,  # JSON array
    "outfit_description": str,
    "moodboard_description": str,
    "qloo_response": str,  # JSON
    "gemini_response": str,  # JSON
    "success": bool,
    "processing_time_ms": int,
    "user_rating": int,  # 1-5 stars
    "user_feedback": str,
    "created_at": datetime
}

# PopularCulturalInput - Analytics
{
    "cultural_input": str,
    "request_count": int,
    "last_requested": datetime,
    "avg_rating": float
}

# SystemMetrics - Daily performance tracking
{
    "date": date,
    "total_requests": int,
    "successful_requests": int,
    "avg_processing_time_ms": int,
    "qloo_api_calls": int,
    "gemini_api_calls": int,
    "unique_ips": int,
    "chat_messages": int,
    "user_ratings_submitted": int
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