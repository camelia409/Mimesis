import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()


class Base(DeclarativeBase):
    pass


# Create database instance
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure the database
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    # Fallback for development
    database_url = "sqlite:///mimesis.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the database extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid_configuration"

# Debug: Print Google OAuth configuration status
print("Google OAuth Configuration:")
print(f"GOOGLE_CLIENT_ID: {'✓ Set' if GOOGLE_CLIENT_ID else '✗ Not set'}")
print(f"GOOGLE_CLIENT_SECRET: {'✓ Set' if GOOGLE_CLIENT_SECRET else '✗ Not set'}")

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Configure logging
logging.basicConfig(level=logging.DEBUG)

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    logging.info("Database tables created successfully")

# Import routes after app creation to avoid circular imports
from routes import *

print("QLOO_API_KEY loaded:", os.environ.get("QLOO_API_KEY"))


