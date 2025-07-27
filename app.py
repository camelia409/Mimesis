import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
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

# Configure logging
logging.basicConfig(level=logging.DEBUG)

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    logging.info("Database tables created successfully")

# Import routes after app creation to avoid circular imports
from routes import *

import os
print("QLOO_API_KEY loaded:", os.environ.get("QLOO_API_KEY"))


