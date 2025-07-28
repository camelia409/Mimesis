import logging
import json
import time
import re
import requests
from datetime import datetime, date
from flask import render_template, request, jsonify, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL
from models import User, StyleRequest, ChatMessage, PopularCulturalInput, SystemMetrics, CulturalTrend
from services.qloo_service import get_fashion_archetypes
from services.gemini_service import generate_style_recommendations, chat_with_stylist

def is_valid_email(email):
    """Validate email format using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_google_provider_cfg():
    """Get Google OAuth provider configuration"""
    # Use hardcoded endpoints directly since discovery URL is unreliable
    return {
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://www.googleapis.com/oauth2/v3/userinfo"
    }

@app.route('/')
def index():
    """Main page with cultural preference input form"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username:
            flash('Username is required', 'error')
            return render_template('register.html')
        
        if not email:
            flash('Email is required', 'error')
            return render_template('register.html')
        
        if not is_valid_email(email):
            flash('Please enter a valid email address', 'error')
            return render_template('register.html')
        
        if not password:
            flash('Password is required', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        # Check if username already exists
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already exists. Please choose another.', 'error')
            return render_template('register.html')
        
        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered. Please use a different email or login.', 'error')
            return render_template('register.html')
        
        # Create new user
        new_user = User(username=username, email=email, style_history="[]")
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # Log in the new user
        login_user(new_user)
        flash('Registration successful! Welcome to Mimesis.', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email:
            flash('Email is required', 'error')
            return render_template('login.html')
        
        if not password:
            flash('Password is required', 'error')
            return render_template('login.html')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Welcome back!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/google-login')
def google_login():
    """Initiate Google OAuth login"""
    if not GOOGLE_CLIENT_ID:
        flash('Google OAuth is not configured. Please use email/password login.', 'error')
        return redirect(url_for('login'))
    
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    if not google_provider_cfg:
        print(f"Google OAuth discovery failed. URL: {GOOGLE_DISCOVERY_URL}")
        flash('Unable to connect to Google OAuth service. Please try again later.', 'error')
        return redirect(url_for('login'))
    
    print(f"Google OAuth provider config: {google_provider_cfg}")
    
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    # For local development, use localhost
    redirect_uri = "http://localhost:5000/google-login/callback"
    
    request_uri = requests.Request(
        "GET",
        authorization_endpoint,
        params={
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
        }
    ).prepare().url
    
    return redirect(request_uri)

@app.route('/google-login/callback')
def google_callback():
    """Handle Google OAuth callback"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        flash('Google OAuth is not configured.', 'error')
        return redirect(url_for('login'))
    
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    print(f"Google OAuth callback received with code: {code[:10]}..." if code else "No code received")
    
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    if not google_provider_cfg:
        flash('Unable to connect to Google OAuth service.', 'error')
        return redirect(url_for('login'))
    
    token_endpoint = google_provider_cfg["token_endpoint"]
    
    # Prepare and send a request to get tokens
    token_response = requests.post(
        token_endpoint,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://localhost:5000/google-login/callback",
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    
    # Parse the tokens!
    if token_response.status_code != 200:
        print(f"Token exchange failed: {token_response.status_code} - {token_response.text}")
        flash('Google OAuth token exchange failed. Please try again.', 'error')
        return redirect(url_for('login'))
    
    tokens = token_response.json()
    if 'access_token' not in tokens:
        print(f"Token response missing access_token: {tokens}")
        flash('Google OAuth response invalid. Please try again.', 'error')
        return redirect(url_for('login'))
    
    # Get user information from Google
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    userinfo_response = requests.get(
        userinfo_endpoint,
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    
    if userinfo_response.status_code != 200:
        print(f"Userinfo request failed: {userinfo_response.status_code} - {userinfo_response.text}")
        flash('Failed to get user information from Google. Please try again.', 'error')
        return redirect(url_for('login'))
    
    userinfo = userinfo_response.json()
    
    # You want to make sure their email is verified.
    # The user submitted a non-Google email address, so you cannot
    # log them in.
    if userinfo.get("email_verified"):
        unique_id = userinfo["sub"]
        users_email = userinfo["email"]
        users_name = userinfo["given_name"]
        users_picture = userinfo.get("picture", "")
    else:
        flash("User email not available or not verified by Google.", "error")
        return redirect(url_for('login'))
    
    # Check if user exists
    user = User.query.filter_by(google_id=unique_id).first()
    
    if not user:
        # Check if email already exists
        existing_user = User.query.filter_by(email=users_email).first()
        if existing_user:
            flash('An account with this email already exists. Please login with email/password.', 'error')
            return redirect(url_for('login'))
        
        # Create new user
        user = User(
            username=users_name,
            email=users_email,
            google_id=unique_id,
            profile_picture=users_picture,
            style_history="[]"
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully with Google!', 'success')
    else:
        flash('Welcome back!', 'success')
    
    # Begin user session by logging the user in
    login_user(user)
    
    # Send user back to homepage
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """User profile with style history"""
    style_history = current_user.get_style_history()
    recent_requests = StyleRequest.query.filter_by(user_id=current_user.id).order_by(StyleRequest.created_at.desc()).limit(5).all()
    
    return render_template('profile.html', 
                         user=current_user, 
                         style_history=style_history,
                         recent_requests=recent_requests)

@app.route('/recommend', methods=['POST'])
@login_required
def recommend():
    """Process cultural preferences and generate style recommendations"""
    start_time = time.time()
    style_request = None
    
    try:
        # Get user input
        cultural_input = request.form.get('cultural_preferences', '').strip()
        user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        
        if not cultural_input:
            flash('Please enter your cultural preferences', 'error')
            return render_template('index.html')
        
        logging.info(f"Processing cultural input: {cultural_input}")
        
        # Create style request record
        style_request = StyleRequest(
            cultural_input=cultural_input,
            ip_address=user_ip,
            user_id=current_user.id
        )
        db.session.add(style_request)
        db.session.flush()  # Get the ID without committing
        
        # Update popular cultural inputs
        try:
            popular_input = PopularCulturalInput.query.filter_by(cultural_input=cultural_input).first()
            if popular_input:
                popular_input.increment_count()
            else:
                popular_input = PopularCulturalInput(
                    cultural_input=cultural_input,
                    request_count=1,
                    last_requested=datetime.utcnow()
                )
                db.session.add(popular_input)
        except Exception as e:
            logging.warning(f"Error updating popular inputs: {str(e)}")
        
        # Update cultural trends
        try:
            for item in cultural_input.split(','):
                element = item.strip()
                if element:
                    trend = CulturalTrend.query.filter_by(cultural_element=element).first()
                    if trend:
                        trend.increment_count()
                    else:
                        trend = CulturalTrend(cultural_element=element)
                        db.session.add(trend)
        except Exception as e:
            logging.warning(f"Error updating cultural trends: {str(e)}")
        
        # Step 1: Get fashion archetypes from Qloo API
        qloo_response = {"archetypes": [], "error": None}
        try:
            qloo_response = get_fashion_archetypes(cultural_input)
            logging.info(f"Qloo response: {qloo_response}")
            style_request.qloo_response = json.dumps(qloo_response)
        except Exception as e:
            logging.error(f"Qloo API error: {str(e)}")
            qloo_response = {"archetypes": [], "error": str(e)}
            style_request.qloo_response = json.dumps(qloo_response)
        
        # Step 2: Generate style recommendations using Gemini
        style_recommendations = {}
        try:
            style_recommendations = generate_style_recommendations(cultural_input, qloo_response)
            logging.info(f"Gemini recommendations: {style_recommendations}")
            
            # Store successful results
            if style_recommendations.get("success", False):
                style_request.aesthetic_name = style_recommendations.get("aesthetic_name")
                style_request.brands = json.dumps(style_recommendations.get("brands", []))
                style_request.outfit_description = style_recommendations.get("outfit")
                style_request.moodboard_description = style_recommendations.get("moodboard")
                style_request.success = True
                
                # Add to user's style history
                current_user.add_to_history(cultural_input, style_recommendations.get("aesthetic_name"))
            else:
                style_request.error_message = style_recommendations.get("error", "Unknown error")
                
            style_request.gemini_response = json.dumps(style_recommendations)
            
        except Exception as e:
            logging.error(f"Gemini API error: {str(e)}")
            style_recommendations = {
                "aesthetic_name": "Error generating recommendations",
                "brands": [],
                "outfit": "Unable to generate outfit suggestions",
                "moodboard": "Unable to generate moodboard",
                "error": str(e),
                "success": False
            }
            style_request.error_message = str(e)
            style_request.gemini_response = json.dumps(style_recommendations)
        
        # Calculate processing time and save
        processing_time = int((time.time() - start_time) * 1000)
        style_request.processing_time_ms = processing_time
        
        try:
            db.session.commit()
            logging.info(f"Style request saved with ID: {style_request.id}")
        except Exception as e:
            logging.error(f"Database commit error: {str(e)}")
            db.session.rollback()
        
        # Update daily metrics
        update_daily_metrics(success=style_request.success, processing_time=processing_time)
        
        return render_template('results.html', 
                             user_input=cultural_input,
                             qloo_data=qloo_response,
                             recommendations=style_recommendations,
                             request_id=style_request.id)
    
    except Exception as e:
        logging.error(f"Unexpected error in recommend route: {str(e)}")
        if style_request:
            style_request.error_message = str(e)
            try:
                db.session.commit()
            except:
                db.session.rollback()
        
        flash('An unexpected error occurred. Please try again.', 'error')
        return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Enhanced AI stylist chat with context-aware conversations"""
    try:
        user_message = request.form.get('chat_input', '').strip()
        style_request_id = request.form.get('style_request_id')
        
        if not user_message:
            return jsonify({'error': 'Please enter a message'})
        
        # Get style request for context
        context = ""
        style_request = None
        if style_request_id:
            style_request = StyleRequest.query.get(style_request_id)
            if style_request:
                context = f"Cultural Input: {style_request.cultural_input}\n"
                context += f"Aesthetic: {style_request.aesthetic_name}\n"
                context += f"Style: {style_request.outfit_description}\n"
                
                # Get previous messages for this style request
                prev_messages = ChatMessage.query.filter_by(
                    style_request_id=style_request_id
                ).order_by(ChatMessage.created_at.desc()).limit(3).all()
                
                if prev_messages:
                    context += "\nRecent conversation:\n"
                    for msg in reversed(prev_messages):
                        context += f"User: {msg.user_message}\nAI: {msg.ai_response}\n"
        
        # Generate chat response using Gemini with full context
        chat_response = chat_with_stylist(user_message, context)
        
        # Store the chat message in database
        if style_request_id and style_request:
            chat_message = ChatMessage(
                style_request_id=style_request_id,
                user_message=user_message,
                ai_response=chat_response,
                context=context[:1000]  # Limit context storage
            )
            db.session.add(chat_message)
            db.session.commit()
            
            # Update chat message count in daily metrics
            update_chat_metrics()
        
        return jsonify({
            'response': chat_response,
            'status': 'success'
        })
    
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        return jsonify({
            'error': 'I\'m having trouble responding right now. Please try again!',
            'status': 'error'
        })

def update_daily_metrics(success=True, processing_time=None):
    """Update daily system metrics"""
    try:
        today = date.today()
        metrics = SystemMetrics.query.filter_by(date=today).first()
        
        if not metrics:
            metrics = SystemMetrics(
                date=today,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                qloo_api_calls=0,
                gemini_api_calls=0,
                unique_ips=0,
                chat_messages=0,
                user_ratings_submitted=0
            )
            db.session.add(metrics)
        
        metrics.total_requests += 1
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
            
        if processing_time:
            # Update average processing time
            total_successful = metrics.successful_requests
            if total_successful > 1:
                current_avg = metrics.avg_processing_time_ms or 0
                metrics.avg_processing_time_ms = int((current_avg * (total_successful - 1) + processing_time) / total_successful)
            else:
                metrics.avg_processing_time_ms = processing_time
        
        metrics.gemini_api_calls += 1  # We always call Gemini
        metrics.qloo_api_calls += 1    # We always try to call Qloo
        metrics.updated_at = datetime.utcnow()
        
        db.session.commit()
    except Exception as e:
        logging.error(f"Error updating daily metrics: {str(e)}")
        db.session.rollback()


def update_chat_metrics():
    """Update chat message count in daily metrics"""
    try:
        today = date.today()
        metrics = SystemMetrics.query.filter_by(date=today).first()
        
        if metrics:
            metrics.chat_messages += 1
            metrics.updated_at = datetime.utcnow()
            db.session.commit()
    except Exception as e:
        logging.error(f"Error updating chat metrics: {str(e)}")
        db.session.rollback()


@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback for a style request"""
    try:
        request_id = request.form.get('request_id')
        rating = request.form.get('rating')
        feedback_text = request.form.get('feedback', '').strip()
        
        if not request_id:
            return jsonify({'error': 'Request ID required'}), 400
            
        style_request = StyleRequest.query.get(request_id)
        if not style_request:
            return jsonify({'error': 'Request not found'}), 404
            
        if rating:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    style_request.user_rating = rating
            except ValueError:
                pass
                
        if feedback_text:
            style_request.user_feedback = feedback_text
            
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Thank you for your feedback!'})
        
    except Exception as e:
        logging.error(f"Error submitting feedback: {str(e)}")
        return jsonify({'error': 'Unable to submit feedback'}), 500


@app.route('/popular')
def popular_inputs():
    """Show popular cultural combinations"""
    try:
        popular = PopularCulturalInput.query.order_by(
            PopularCulturalInput.request_count.desc()
        ).limit(10).all()
        
        return render_template('popular.html', popular_inputs=popular)
    except Exception as e:
        logging.error(f"Error fetching popular inputs: {str(e)}")
        return render_template('popular.html', popular_inputs=[])


@app.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard showing trends and performance metrics"""
    try:
        # Get popular cultural inputs
        popular_inputs = PopularCulturalInput.query.order_by(
            PopularCulturalInput.request_count.desc()
        ).limit(10).all()
        
        # Get cultural trend analysis
        cultural_trends = CulturalTrend.query.order_by(
            CulturalTrend.mention_count.desc()
        ).limit(15).all()
        
        # Get recent system metrics
        metrics = SystemMetrics.query.order_by(
            SystemMetrics.date.desc()
        ).limit(7).all()
        
        # Calculate summary stats
        total_requests = sum(m.total_requests for m in metrics)
        total_successful = sum(m.successful_requests for m in metrics)
        success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0
        
        avg_processing_time = sum(m.avg_processing_time_ms or 0 for m in metrics) / len(metrics) if metrics else 0
        
        summary_stats = {
            'total_requests': total_requests,
            'success_rate': round(success_rate, 1),
            'avg_processing_time': round(avg_processing_time),
            'total_chat_messages': sum(m.chat_messages for m in metrics),
            'unique_users': sum(m.unique_ips for m in metrics)
        }
        
        return render_template('analytics.html', 
                             popular_inputs=popular_inputs,
                             cultural_trends=cultural_trends,
                             metrics=metrics,
                             summary_stats=summary_stats)
    except Exception as e:
        logging.error(f"Error fetching analytics: {str(e)}")
        return render_template('analytics.html', 
                             popular_inputs=[],
                             cultural_trends=[],
                             metrics=metrics,
                             summary_stats={})


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logging.error(f"Internal server error: {str(error)}")
    flash('An internal error occurred. Please try again.', 'error')
    return render_template('index.html'), 500
