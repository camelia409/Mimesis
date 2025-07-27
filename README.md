# Mimesis - Cultural Style Intelligence Engine

Mimesis is a privacy-first web application that transforms your cultural preferences into personalized fashion aesthetics. Built for the Qloo LLM Hackathon, it leverages Qloo's Taste AI™ and Google's Gemini API to create unique style identities without requiring body metrics or personal data.

## 🌟 Features

### Core Functionality
- **Cultural Input Processing**: Enter music, movies, games, books, or any cultural influences
- **Privacy-First Design**: No body measurements, income data, or personal information required
- **AI-Powered Recommendations**: 
  - Unique aesthetic names (e.g., "Neo-Noir Luxe", "Digital Femme Fatale")
  - Curated brand suggestions across all budgets (luxury, indie, thrift, DIY)
  - Detailed outfit descriptions
  - Rich moodboard themes
- **Global Inclusivity**: Recommendations span diverse cultures and markets
- **Sustainable Focus**: Emphasis on thrift, vintage, and eco-friendly options

### Advanced Features
- **Interactive AI Stylist**: Chat feature for additional style questions and personalized advice
- **Analytics Dashboard**: Track popular cultural inputs and system performance
- **User Feedback System**: Rate and provide feedback on recommendations
- **Popular Trends**: View trending cultural combinations and their style outcomes
- **Performance Monitoring**: Real-time system metrics and API usage tracking

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
├── templates/            # HTML templates
├── static/               # CSS, JS, and static assets
└── instance/             # Database and instance files
```

### Database Models
- **StyleRequest**: Stores user inputs and generated recommendations
- **ChatMessage**: AI stylist conversation history
- **PopularCulturalInput**: Tracks trending cultural combinations
- **SystemMetrics**: Performance and usage analytics
- **User**: User preferences and session data

## 🛠 Technology Stack

### Backend
- **Framework**: Flask 3.1.1 (Python web framework)
- **Database**: SQLite (default) / PostgreSQL (optional for production)
- **ORM**: SQLAlchemy 2.0+ with Flask-SQLAlchemy
- **API Integration**: 
  - Qloo Taste AI™ for cultural mapping
  - Google Gemini 2.5 Flash for style generation

### Frontend
- **Styling**: Tailwind CSS (via CDN)
- **JavaScript**: Vanilla JS with modern ES6+ features
- **Templates**: Jinja2 templating engine
- **Responsive Design**: Mobile-first approach

### Development & Deployment
- **Package Management**: uv (modern Python package manager)
- **Environment Management**: python-dotenv
- **Production Server**: Gunicorn
- **Database**: SQLite (default) / PostgreSQL (optional, requires psycopg2-binary)

## 📋 Prerequisites

- Python 3.11+
- Qloo API Key (for cultural taste analysis)
- Google Gemini API Key (for style generation)
- Internet connection for CDN resources

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

# Optional: Production Database (PostgreSQL)
# DATABASE_URL=postgresql://user:password@localhost/mimesis
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

## 🔧 API Integrations

### Qloo Taste AI™
- **Purpose**: Cultural preference analysis and fashion archetype mapping
- **Endpoint**: `/recommend` (POST)
- **Input**: Cultural preferences text
- **Output**: Fashion archetypes and style categories

### Google Gemini API
- **Purpose**: Style recommendation generation and AI stylist chat
- **Endpoints**: 
  - Style generation in `/recommend`
  - Chat functionality in `/chat`
- **Features**: Aesthetic naming, brand suggestions, outfit descriptions, moodboards



## 📊 Analytics & Monitoring

### Available Metrics
- **Daily Request Tracking**: Total, successful, and failed requests
- **Performance Monitoring**: Average processing times
- **API Usage**: Qloo and Gemini API call counts
- **User Engagement**: Unique IPs, chat messages, ratings
- **Popular Trends**: Most requested cultural combinations

### Analytics Dashboard
Access analytics at `/analytics` to view:
- System performance metrics
- Popular cultural inputs
- User engagement statistics
- API usage patterns

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production Deployment
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app

# Using Docker (if Dockerfile is added)
docker build -t mimesis .
docker run -p 5000:5000 mimesis
```

### Environment Variables for Production
```env
DATABASE_URL=postgresql://user:password@host:port/database
SESSION_SECRET=your_secure_session_secret
QLOO_API_KEY=your_qloo_api_key
GEMINI_API_KEY=your_gemini_api_key
```

## 🔒 Privacy & Security

- **No Personal Data Collection**: No body measurements, income, or personal information required
- **Anonymous Tracking**: Uses IP addresses for analytics only
- **Secure Sessions**: Configurable session secrets
- **API Key Protection**: Environment variable-based configuration
- **Database Security**: SQL injection protection via SQLAlchemy ORM

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Qloo**: For providing the Taste AI™ API for cultural preference analysis
- **Google**: For the Gemini API enabling advanced AI-powered style recommendations
- **Flask Community**: For the excellent web framework
- **Tailwind CSS**: For the utility-first CSS framework

## 📞 Support

For questions, issues, or contributions, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for the Qloo LLM Hackathon**