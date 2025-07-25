from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean


class User(db.Model):
    """User model for storing user preferences and sessions"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User relationships
    style_requests = db.relationship('StyleRequest', backref='user', lazy=True)


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


class ChatMessage(db.Model):
    """Model for storing AI stylist chat conversations"""
    id = db.Column(db.Integer, primary_key=True)
    style_request_id = db.Column(db.Integer, db.ForeignKey('style_request.id'), nullable=True)
    
    # Chat data
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    context = db.Column(db.Text, nullable=True)  # Style context for the chat
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    response_time_ms = db.Column(db.Integer, nullable=True)


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
    chat_messages = db.Column(db.Integer, default=0)
    user_ratings_submitted = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)