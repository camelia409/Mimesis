# Mimesis - AI-Powered Cultural Style Intelligence Engine

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-green.svg)](https://flask.palletsprojects.com)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0+-38B2AC.svg)](https://tailwindcss.com)
[![Responsive](https://img.shields.io/badge/Responsive-Design-purple.svg)](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
[![PWA](https://img.shields.io/badge/PWA-Ready-orange.svg)](https://web.dev/progressive-web-apps/)

Mimesis is a **privacy-first, fully responsive** web application that transforms your cultural preferences into personalized fashion aesthetics. Built for the Qloo LLM Hackathon, it leverages **Qloo's Taste AI™** and **Google's Gemini API** to create unique style identities without requiring body metrics or personal data.

## 🌟 Key Features

### 🎨 **Core Functionality**
- **Cultural Input Processing**: Enter music, movies, games, books, or any cultural influences
- **Privacy-First Design**: No body measurements, income data, or personal information required
- **AI-Powered Recommendations**: 
  - Unique aesthetic names (e.g., "Neo-Noir Luxe", "Digital Femme Fatale", "Cultural Fusion Aesthetic")
  - Curated brand suggestions across all budgets (luxury, indie, thrift, DIY)
  - Detailed outfit descriptions with cultural context
  - Rich moodboard themes and styling guidance
- **Global Inclusivity**: Recommendations span diverse cultures and markets
- **Sustainable Focus**: Emphasis on thrift, vintage, and eco-friendly options

### 📱 **Responsive Design**
- **Mobile-First Approach**: Optimized for smartphones (320px - 768px)
- **Tablet Support**: Perfect layout for tablets (768px - 1024px)
- **Desktop Experience**: Rich content display for large screens (1024px+)
- **Touch-Optimized**: 44px minimum touch targets, mobile-friendly interactions
- **Progressive Web App (PWA)**: Installable mobile app with offline support
- **Cross-Platform**: Works seamlessly on iOS, Android, Windows, macOS, Linux

### 🤖 **AI-Powered Features**
- **Personalized Recommendations**: Deep cultural analysis for tailored style suggestions
- **Dynamic Aesthetic Generation**: Context-aware style identities based on cultural inputs
- **Brand Intelligence**: Smart brand matching using Qloo's cultural taste analysis
- **Style Context Understanding**: AI that understands cultural nuances and preferences

### 📊 **Analytics & Monitoring**
- **User Feedback System**: Star ratings and detailed feedback collection
- **Performance Tracking**: Real-time system metrics and API usage monitoring
- **Popular Trends**: View trending cultural combinations and their style outcomes
- **Analytics Dashboard**: Comprehensive insights into user engagement and system performance

### 🔐 **User Management**
- **User Authentication**: Email/password and Google OAuth integration
- **Style History**: Personalized user profiles with style request history
- **Session Management**: Secure user sessions with configurable secrets
- **Profile Management**: User preferences and style journey tracking

## 🏗 Architecture

### Backend Structure
```
Mimesis/
├── app.py                 # Flask application configuration
├── main.py               # Application entry point
├── routes.py             # API endpoints and route handlers
├── models.py             # Database models and schemas
├── services/             # External API integrations
│   ├── qloo_service.py   # Qloo Taste AI™ integration
│   └── gemini_service.py # Google Gemini API integration
├── templates/            # HTML templates (responsive)
├── static/               # CSS, JS, and static assets
│   ├── css/
│   │   └── styles.css    # Responsive CSS with mobile-first design
│   └── js/
│       └── scripts.js    # Responsive JavaScript with touch support
└── instance/             # Database and instance files
```

### Database Models
- **User**: User authentication and profile data
- **StyleRequest**: Stores user inputs and generated recommendations
- **PopularCulturalInput**: Tracks trending cultural combinations
- **CulturalTrend**: Cultural trend analysis and insights
- **SystemMetrics**: Performance and usage analytics

## 🛠 Technology Stack

### Backend
- **Framework**: Flask 3.1.1 (Python web framework)
- **Database**: SQLite (lightweight, file-based database)
- **ORM**: SQLAlchemy 2.0+ with Flask-SQLAlchemy
- **API Integration**: 
  - **Qloo Taste AI™** for cultural mapping and fashion archetypes
  - **Google Gemini 2.5 Flash** for style generation and personalization
- **Authentication**: Flask-Login with Google OAuth support
- **Session Management**: Secure session handling with configurable secrets

### Frontend
- **Styling**: Tailwind CSS (via CDN) with custom responsive utilities
- **JavaScript**: Vanilla JS with modern ES6+ features and touch support
- **Templates**: Jinja2 templating engine with responsive layouts
- **Responsive Design**: Mobile-first approach with progressive enhancement
- **PWA Features**: Service worker, manifest, and install prompts

### Development & Deployment
- **Package Management**: uv (modern Python package manager)
- **Environment Management**: python-dotenv
- **Production Server**: Gunicorn
- **Database**: SQLite (simple, reliable, no additional setup required)

## 📋 Prerequisites

- **Python 3.11+**
- **Qloo API Key** (for cultural taste analysis)
- **Google Gemini API Key** (for style generation)
- **Internet connection** for CDN resources

## 🚀 Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/mimesis.git
cd mimesis
```

### 2. Install Dependencies

**Using uv (Recommended):**
```bash
uv sync
```

**Using pip:**
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the project root:
```env
# API Keys
QLOO_API_KEY=your_qloo_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Application Settings
SESSION_SECRET=your_session_secret_here
DATABASE_URL=sqlite:///mimesis.db
```

### 4. Database Setup
The application will automatically create the database and tables on first run:
```bash
python main.py
```

### 5. Run the Application
```bash
python main.py
```

The application will be available at `http://localhost:5000`

## 📱 Responsive Design Features

### **Mobile Experience (320px - 768px)**
- **Touch-Optimized Interface**: Large touch targets (44px minimum)
- **Readable Typography**: Optimized font sizes for mobile screens
- **Stacked Layouts**: Single-column layouts for easy navigation
- **Mobile-First Navigation**: Intuitive mobile navigation patterns
- **Touch Gestures**: Native mobile interactions and feedback

### **Tablet Experience (768px - 1024px)**
- **Balanced Layouts**: Two-column grids for optimal content display
- **Enhanced Typography**: Larger text sizes for tablet readability
- **Touch & Mouse Support**: Hybrid interaction patterns
- **Optimized Spacing**: Comfortable padding and margins

### **Desktop Experience (1024px+)**
- **Rich Content Display**: Three-column grids and detailed layouts
- **Hover Effects**: Enhanced interactive feedback
- **Large Typography**: Elegant text scaling for large screens
- **Professional Layout**: Optimal use of screen real estate

### **Accessibility Features**
- **WCAG 2.1 AA Compliance**: Color contrast and text scaling
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Semantic HTML and ARIA labels
- **Reduced Motion**: Respects user motion preferences
- **Zoom Support**: Up to 500% zoom without breaking layout

## 🔧 API Integrations

### Qloo Taste AI™
- **Purpose**: Cultural preference analysis and fashion archetype mapping
- **Endpoint**: `/recommend` (POST)
- **Input**: Cultural preferences text
- **Output**: Fashion archetypes, cultural insights, and style categories
- **Features**: 
  - Cultural trend analysis
  - Fashion archetype identification
  - Brand affinity mapping
  - Cultural significance understanding

### Google Gemini API
- **Purpose**: Style recommendation generation and personalization
- **Endpoints**: Style generation in `/recommend`
- **Features**: 
  - Aesthetic naming with cultural context
  - Personalized brand suggestions
  - Detailed outfit descriptions
  - Rich moodboard themes
  - Cultural styling guidance

## 📡 API Response Format

All API endpoints follow a standardized response format for consistency and better error handling.

### Success Response Format
```json
{
  "success": true,
  "data": {
    "aesthetic_name": "Cultural Fusion Aesthetic",
    "brands": ["Brand 1", "Brand 2", "Brand 3"],
    "outfit": "Detailed outfit description...",
    "moodboard": "Rich moodboard description...",
    "cultural_insights": {...}
  },
  "message": "Style recommendations generated successfully",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "status_code": 200
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "message": "Human-readable error message",
    "code": "ERROR_CODE",
    "timestamp": "2024-01-15T10:30:00.000Z"
  },
  "status_code": 400
}
```

### Available Endpoints
- `POST /recommend` - Get personalized style recommendations (requires auth)
- `POST /feedback` - Submit feedback and ratings
- `GET /popular` - Get popular cultural inputs
- `GET /analytics` - Get analytics data
- `GET /` - Home page with responsive design
- `GET /login` - User authentication
- `GET /register` - User registration

## 📊 Analytics & Monitoring

### Available Metrics
- **Daily Request Tracking**: Total, successful, and failed requests
- **Performance Monitoring**: Average processing times and response metrics
- **API Usage**: Qloo and Gemini API call counts and success rates
- **User Engagement**: Unique users, feedback ratings, session data
- **Popular Trends**: Most requested cultural combinations and their outcomes
- **System Health**: Database performance and error tracking

### Analytics Dashboard
Access analytics at `/analytics` to view:
- Real-time system performance metrics
- Popular cultural inputs and trends
- User engagement statistics
- API usage patterns and efficiency
- Error rates and system health

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production Deployment
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### Environment Variables for Production
```env
SESSION_SECRET=your_secure_session_secret
QLOO_API_KEY=your_qloo_api_key
GEMINI_API_KEY=your_gemini_api_key
FLASK_ENV=production
```

### PWA Deployment
The application is PWA-ready with:
- **Service Worker**: Offline functionality and caching
- **Web App Manifest**: App-like installation experience
- **Responsive Design**: Works on all devices and screen sizes
- **Touch Support**: Native mobile interactions

## 🔒 Privacy & Security

- **No Personal Data Collection**: No body measurements, income, or personal information required
- **Anonymous Analytics**: Uses IP addresses for analytics only (no personal tracking)
- **Secure Sessions**: Configurable session secrets with secure cookie handling
- **API Key Protection**: Environment variable-based configuration
- **Database Security**: SQL injection protection via SQLAlchemy ORM
- **HTTPS Ready**: Secure communication protocols supported
- **Data Minimization**: Only collects necessary data for functionality

## 🎯 Recent Improvements

### **Responsive Design Implementation**
- ✅ **Mobile-First Design**: Complete responsive overhaul
- ✅ **Touch Optimization**: Enhanced mobile interactions
- ✅ **Cross-Platform Support**: Works on all devices
- ✅ **PWA Features**: Installable mobile app experience

### **AI & Personalization Enhancements**
- ✅ **Deep Cultural Analysis**: Enhanced cultural input processing
- ✅ **Personalized Recommendations**: Context-aware style suggestions
- ✅ **Brand Intelligence**: Smart brand matching using cultural insights
- ✅ **Error Handling**: Robust error management and fallbacks

### **User Experience Improvements**
- ✅ **Star Rating System**: Interactive feedback collection
- ✅ **Enhanced UI/UX**: Modern, accessible interface design
- ✅ **Performance Optimization**: Fast loading and smooth interactions
- ✅ **Accessibility**: WCAG 2.1 AA compliance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow mobile-first responsive design principles
- Ensure accessibility compliance (WCAG 2.1 AA)
- Test on multiple devices and screen sizes
- Maintain consistent code style and documentation

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Qloo**: For providing the Taste AI™ API for cultural preference analysis
- **Google**: For the Gemini API enabling advanced AI-powered style recommendations
- **Flask Community**: For the excellent web framework
- **Tailwind CSS**: For the utility-first CSS framework
- **Open Source Community**: For the tools and libraries that make this possible

## 📞 Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Check the documentation
- Contact the development team

## 🌟 Live Demo

Experience Mimesis in action:
- **Responsive Design**: Works perfectly on mobile, tablet, and desktop
- **AI-Powered Recommendations**: Get personalized style suggestions
- **Cultural Intelligence**: See how your cultural preferences influence style
- **PWA Experience**: Install as a mobile app

---

**Built with ❤️ for the Qloo LLM Hackathon**

*Transform your cultural identity into style with AI-powered intelligence.*