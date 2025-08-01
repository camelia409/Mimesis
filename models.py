from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from flask_login import UserMixin


class User(db.Model, UserMixin):
    """User model for storing user preferences and sessions"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    google_id = db.Column(db.String(100), unique=True, nullable=True)  # Google OAuth ID
    profile_picture = db.Column(db.String(500), nullable=True)  # Profile picture URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Style history for personalization
    style_history = db.Column(db.Text, default="[]")  # JSON string of past inputs
    
    # User relationships
    style_requests = db.relationship('StyleRequest', backref='user', lazy=True)
    
    def get_style_history(self):
        """Get user's style history as a list"""
        import json
        try:
            return json.loads(self.style_history)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def add_to_history(self, cultural_input, aesthetic_name):
        """Add a new style request to user's history"""
        import json
        history = self.get_style_history()
        history.append({
            "input": cultural_input,
            "aesthetic": aesthetic_name,
            "timestamp": datetime.utcnow().isoformat()
        })
        # Keep only last 10 entries
        self.style_history = json.dumps(history[-10:])
        db.session.commit()
    
    def set_password(self, password):
        """Hash and set password"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)


class StyleRequest(db.Model):
    """Model for storing user style requests and generated recommendations"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Input data
    cultural_input = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)  # For anonymous tracking
    
    # Generated results
    aesthetic_name = db.Column(db.String(255), nullable=True)
    brands = db.Column(db.Text, nullable=True)  # JSON string of brand list
    outfit_description = db.Column(db.Text, nullable=True)
    moodboard_description = db.Column(db.Text, nullable=True)
    
    # API response data
    qloo_response = db.Column(db.Text, nullable=True)  # JSON string
    gemini_response = db.Column(db.Text, nullable=True)  # JSON string
    
    # Metadata
    success = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time_ms = db.Column(db.Integer, nullable=True)
    
    # User feedback
    user_rating = db.Column(db.Integer, nullable=True)  # 1-5 star rating
    user_feedback = db.Column(db.Text, nullable=True)


class PopularCulturalInput(db.Model):
    """Model for tracking popular cultural combinations for analytics"""
    id = db.Column(db.Integer, primary_key=True)
    cultural_input = db.Column(db.String(500), unique=True, nullable=False)
    request_count = db.Column(db.Integer, default=1)
    last_requested = db.Column(db.DateTime, default=datetime.utcnow)
    avg_rating = db.Column(db.Float, nullable=True)
    
    def increment_count(self):
        self.request_count += 1
        self.last_requested = datetime.utcnow()


class SystemMetrics(db.Model):
    """Model for tracking system performance and usage metrics"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Daily metrics
    date = db.Column(db.Date, unique=True, nullable=False)
    total_requests = db.Column(db.Integer, default=0)
    successful_requests = db.Column(db.Integer, default=0)
    failed_requests = db.Column(db.Integer, default=0)
    
    # Performance metrics
    avg_processing_time_ms = db.Column(db.Integer, nullable=True)
    qloo_api_calls = db.Column(db.Integer, default=0)
    gemini_api_calls = db.Column(db.Integer, default=0)
    
    # User engagement
    unique_ips = db.Column(db.Integer, default=0)
    user_ratings_submitted = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CulturalTrend(db.Model):
    """Model for tracking individual cultural elements and their trends"""
    id = db.Column(db.Integer, primary_key=True)
    cultural_element = db.Column(db.String(255), unique=True, nullable=False)
    mention_count = db.Column(db.Integer, default=1)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    def increment_count(self):
        self.mention_count += 1
        self.last_seen = datetime.utcnow()