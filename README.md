# Mimesis - Cultural Style Intelligence Engine

Mimesis is a privacy-first web application that transforms your cultural preferences into personalized fashion aesthetics. Built for the Qloo LLM Hackathon, it leverages Qloo's Taste AI™ and Google's Gemini API to create unique style identities without requiring body metrics or personal data.

## 🌟 Features

- **Cultural Input Processing**: Enter music, movies, games, books, or any cultural influences
- **Privacy-First Design**: No body measurements, income data, or personal information required
- **AI-Powered Recommendations**: 
  - Unique aesthetic names (e.g., "Neo-Noir Luxe", "Digital Femme Fatale")
  - Curated brand suggestions across all budgets (luxury, indie, thrift, DIY)
  - Detailed outfit descriptions
  - Rich moodboard themes
- **Global Inclusivity**: Recommendations span diverse cultures and markets
- **Sustainable Focus**: Emphasis on thrift, vintage, and eco-friendly options
- **Interactive AI Stylist**: Chat feature for additional style questions

## 🚀 Live Demo

Visit the live application: [Mimesis on Replit](https://mimesis.your-username.repl.co)

## 🛠 Technology Stack

- **Backend**: Flask 2.3.3, Python 3.9+
- **APIs**: 
  - Qloo Taste AI™ for cultural mapping
  - Google Gemini 2.5 Flash for style generation
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Hosting**: Replit cloud platform

## 📋 Prerequisites

- Python 3.9+
- Qloo API Key
- Google Gemini API Key
- Internet connection for CDN resources

## ⚡ Quick Start on Replit

1. **Create New Repl**:
   - Go to [replit.com](https://replit.com)
   - Create a new Python Repl named "Mimesis"

2. **Upload Code**:
   - Copy all files from this repository to your Repl

3. **Set Environment Variables**:
   In Replit's Secrets panel, add:
   ```
   QLOO_API_KEY=your_qloo_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   SESSION_SECRET=your_session_secret_here
   ```

4. **Install Dependencies**:
   ```bash
   pip install flask requests google-genai
   ```

5. **Run the Application**:
   ```bash
   python main.py
   ```

6. **Access the App**:
   - Click the "Open in new tab" button in Replit
   - Your app will be available at `https://mimesis.your-username.repl.co`

## 🏗 Local Development

1. **Clone Repository**:
   ```bash
   git clone https://github.com/yourusername/mimesis.git
   cd mimesis
   ```

2. **Set Environment Variables**:
   ```bash
   export QLOO_API_KEY="your_qloo_api_key"
   export GEMINI_API_KEY="your_gemini_api_key"
   export SESSION_SECRET="your_session_secret"
   