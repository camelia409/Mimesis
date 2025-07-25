import os
import logging
from flask import Flask

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Import routes after app creation to avoid circular imports
from routes import *


