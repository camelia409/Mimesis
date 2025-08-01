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

# Configuration
app.config['SECRET_KEY'] = os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mimesis.db')

# Handle SQLite database URL for cloud platforms
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure database engine options based on database type
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
    # SQLite-specific configuration to prevent locking issues
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_size": 1,  # Single connection for SQLite
        "max_overflow": 0,  # No overflow for SQLite
        "pool_timeout": 30,
        "connect_args": {
            "timeout": 30,  # SQLite timeout
            "check_same_thread": False,  # Allow multi-threading
        }
    }
else:
    # PostgreSQL/MySQL configuration
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


