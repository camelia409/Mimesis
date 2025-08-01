import logging
import json
import time
import re
import requests
from datetime import datetime, date
from flask import render_template, request, jsonify, flash, redirect, url_for, session, make_response
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL
from models import User, StyleRequest, PopularCulturalInput, SystemMetrics, CulturalTrend
from services.qloo_service import get_fashion_archetypes
from services.gemini_service import generate_style_recommendations

def create_json_response(data, status_code=200, success=True, message=None):
    """Create a standardized JSON response"""
    response_data = {
        "success": success,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
        "status_code": status_code
    }
    
    if message:
        response_data["message"] = message
    
    response = make_response(jsonify(response_data), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response

def create_error_response(error_message, status_code=400, error_code=None):
    """Create a standardized error response"""
    error_data = {
        "success": False,
        "error": {
            "message": error_message,
            "code": error_code or f"ERR_{status_code}",
            "timestamp": datetime.utcnow().isoformat()
        },
        "status_code": status_code
    }
    
    response = make_response(jsonify(error_data), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response

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
    
    # Debug: Print userinfo to console
    print(f"Google OAuth Debug - Userinfo: {userinfo}")
    
    # You want to make sure their email is verified.
    # The user submitted a non-Google email address, so you cannot
    # log them in.
    if userinfo.get("email_verified"):
        unique_id = userinfo["sub"]
        users_email = userinfo["email"]
        users_name = userinfo["given_name"]
        users_picture = userinfo.get("picture", "")
        
        # Debug: Print extracted values
        print(f"Google OAuth Debug - Unique ID: {unique_id}")
        print(f"Google OAuth Debug - Email: {users_email}")
        print(f"Google OAuth Debug - Name: {users_name}")
        print(f"Google OAuth Debug - Picture URL: {users_picture}")
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
        
        # Debug: Print created user info
        print(f"Google OAuth Debug - Created new user with profile picture: {user.profile_picture}")
        
        flash('Account created successfully with Google!', 'success')
    else:
        # Update existing user's profile picture if it's different
        if user.profile_picture != users_picture:
            user.profile_picture = users_picture
            db.session.commit()
            print(f"Google OAuth Debug - Updated existing user profile picture: {user.profile_picture}")
        
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
    
    # Debug: Print user info to console
    print(f"Profile Debug - User ID: {current_user.id}")
    print(f"Profile Debug - Username: {current_user.username}")
    print(f"Profile Debug - Email: {current_user.email}")
    print(f"Profile Debug - Google ID: {current_user.google_id}")
    print(f"Profile Debug - Profile Picture: {current_user.profile_picture}")
    
    return render_template('profile.html', 
                         user=current_user, 
                         style_history=style_history,
                         recent_requests=recent_requests)

@app.route('/recommend', methods=['POST'])
@login_required
def recommend():
    """Process cultural preferences and generate personalized style recommendations"""
    start_time = time.time()
    style_request = None
    
    try:
        # Get user input
        cultural_input = request.form.get('cultural_preferences', '').strip()
        user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        
        if not cultural_input:
            flash('Please enter your cultural preferences', 'error')
            return render_template('index.html')
        
        logging.info(f"Processing cultural input: {cultural_input} for user: {current_user.username}")
        
        # Get user's style history for personalization
        user_history = current_user.get_style_history()
        history_context = ""
        if user_history:
            recent_history = user_history[-3:]  # Last 3 requests
            history_context = "\n".join([
                f"Past input: {h['input']}, Aesthetic: {h['aesthetic']}" 
                for h in recent_history
            ])
        else:
            history_context = "No prior style history."
        
        # Create style request record with minimal database time
        try:
            style_request = StyleRequest(
                cultural_input=cultural_input,
                ip_address=user_ip,
                user_id=current_user.id
            )
            db.session.add(style_request)
            db.session.commit()  # Commit immediately to get the ID
            logging.info(f"Style request created with ID: {style_request.id}")
        except Exception as e:
            logging.error(f"Error creating style request: {str(e)}")
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'error')
            return render_template('index.html')
        
        # Update popular cultural inputs in a separate transaction
        try:
            with db.session.begin():
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
        
        # Update cultural trends in a separate transaction
        try:
            with db.session.begin():
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
        except Exception as e:
            logging.error(f"Qloo API error: {str(e)}")
            qloo_response = {"archetypes": [], "error": str(e)}
        
        # Step 2: Generate personalized style recommendations using Gemini
        style_recommendations = {}
        try:
            # Create personalized context with user history and Qloo data
            personalization_context = f"""
            User: {current_user.username}
            Current Input: {cultural_input}
            User History: {history_context}
            Qloo Insights: {json.dumps(qloo_response.get('archetypes', [])[:3])}
            """
            
            style_recommendations = generate_style_recommendations(cultural_input, qloo_response)
            logging.info(f"Personalized Gemini recommendations: {style_recommendations}")
            
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
        
        # Update the style request with results in a separate transaction
        try:
            # Refresh the style request object
            style_request = StyleRequest.query.get(style_request.id)
            if style_request:
                style_request.qloo_response = json.dumps(qloo_response)
                
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
                
                # Calculate processing time
                processing_time = int((time.time() - start_time) * 1000)
                style_request.processing_time_ms = processing_time
                
                db.session.commit()
                
        except Exception as e:
            logging.error(f"Error updating style request: {str(e)}")
            db.session.rollback()
            # Continue with the response even if database update fails
        
        # Update daily metrics
        try:
            update_daily_metrics(success=style_recommendations.get("success", False), 
                               processing_time=int((time.time() - start_time) * 1000))
        except Exception as e:
            logging.warning(f"Error updating daily metrics: {str(e)}")
        
        # Check if client wants JSON response
        if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
            response_data = {
                'user_input': cultural_input,
                'qloo_data': qloo_response,
                'recommendations': style_recommendations,
                'request_id': style_request.id if style_request else 0,
                'processing_time_ms': int((time.time() - start_time) * 1000),
                'user_history': user_history
            }
            return create_json_response(response_data, 200, True, 'Personalized style recommendations generated successfully')
        
        return render_template('results.html', 
                             user_input=cultural_input,
                             qloo_data=qloo_response,
                             recommendations=style_recommendations,
                             request_id=style_request.id if style_request else 0,
                             user_history=user_history)
    
    except Exception as e:
        logging.error(f"Unexpected error in recommend route: {str(e)}")
        
        # Try to save error state if we have a style request
        if style_request:
            try:
                style_request = StyleRequest.query.get(style_request.id)
                if style_request:
                    style_request.error_message = str(e)
                    style_request.processing_time_ms = int((time.time() - start_time) * 1000)
                    db.session.commit()
            except Exception as commit_error:
                logging.error(f"Error saving error state: {str(commit_error)}")
                db.session.rollback()
        
        # Return error response
        error_recommendations = {
            "success": False,
            "error": f"An unexpected error occurred: {str(e)}",
            "aesthetic_name": "Error",
            "brands": [],
            "outfit": "Unable to generate outfit suggestions due to an error.",
            "moodboard": "Unable to generate moodboard due to an error."
        }
        
        return render_template('results.html', 
                             user_input=cultural_input,
                             qloo_data={"archetypes": [], "error": str(e)},
                             recommendations=error_recommendations,
                             request_id=style_request.id if style_request else 0,
                             user_history=[])



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





@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback for a style request"""
    try:
        request_id = request.form.get('request_id')
        rating = request.form.get('rating')
        feedback_text = request.form.get('feedback', '').strip()
        
        if not request_id:
            return create_error_response('Request ID required', 400, 'MISSING_REQUEST_ID')
            
        style_request = StyleRequest.query.get(request_id)
        if not style_request:
            return create_error_response('Request not found', 404, 'REQUEST_NOT_FOUND')
            
        if rating:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    style_request.user_rating = rating
                else:
                    return create_error_response('Rating must be between 1 and 5', 400, 'INVALID_RATING')
            except ValueError:
                return create_error_response('Invalid rating format', 400, 'INVALID_RATING_FORMAT')
                
        if feedback_text:
            style_request.user_feedback = feedback_text
            
        db.session.commit()
        
        response_data = {
            'request_id': request_id,
            'rating': rating,
            'feedback_length': len(feedback_text) if feedback_text else 0
        }
        
        return create_json_response(response_data, 200, True, 'Thank you for your feedback!')
        
    except Exception as e:
        logging.error(f"Error submitting feedback: {str(e)}")
        return create_error_response('Unable to submit feedback', 500, 'FEEDBACK_ERROR')


@app.route('/popular')
def popular_inputs():
    """Show popular cultural combinations"""
    try:
        # Debug: Check database connection
        print("Popular Debug: Attempting to fetch popular inputs...")
        
        # Check if table exists and has data
        popular_count = PopularCulturalInput.query.count()
        print(f"Popular Debug: Found {popular_count} popular inputs in database")
        
        # If no data exists, create some sample data
        if popular_count == 0:
            print("Popular Debug: No data found, creating sample data...")
            sample_data = [
                PopularCulturalInput(
                    cultural_input="AR Rahman, Radhe Shyam, Chess, 20s cinema, vintage",
                    request_count=5,
                    last_requested=datetime.utcnow(),
                    avg_rating=4.5
                ),
                PopularCulturalInput(
                    cultural_input="Bollywood, classical music, street art, sustainable fashion",
                    request_count=3,
                    last_requested=datetime.utcnow(),
                    avg_rating=4.2
                ),
                PopularCulturalInput(
                    cultural_input="Jazz, vintage photography, French cinema, minimalist design",
                    request_count=2,
                    last_requested=datetime.utcnow(),
                    avg_rating=4.0
                )
            ]
            
            for item in sample_data:
                db.session.add(item)
            db.session.commit()
            print("Popular Debug: Sample data created successfully")
        
        popular = PopularCulturalInput.query.order_by(
            PopularCulturalInput.request_count.desc()
        ).limit(10).all()
        
        print(f"Popular Debug: Retrieved {len(popular)} popular inputs")
        
        # Debug: Print first few items
        for i, item in enumerate(popular[:3]):
            print(f"Popular Debug: Item {i+1} - Input: {item.cultural_input}, Count: {item.request_count}")
        
        # Check if client wants JSON response
        if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
            popular_data = []
            for item in popular:
                popular_data.append({
                    'cultural_input': item.cultural_input,
                    'request_count': item.request_count,
                    'last_requested': item.last_requested.isoformat() if item.last_requested else None,
                    'avg_rating': float(item.avg_rating) if item.avg_rating else None
                })
            
            response_data = {
                'popular_inputs': popular_data,
                'total_count': len(popular_data)
            }
            return create_json_response(response_data, 200, True, 'Popular inputs retrieved successfully')
        
        return render_template('popular.html', popular_inputs=popular)
    except Exception as e:
        logging.error(f"Error fetching popular inputs: {str(e)}")
        print(f"Popular Debug: Exception occurred - {str(e)}")
        # Return empty list but don't crash
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
        
        # Check if client wants JSON response
        if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
            # Convert metrics to JSON-serializable format
            metrics_data = []
            for metric in metrics:
                metrics_data.append({
                    'date': metric.date.isoformat(),
                    'total_requests': metric.total_requests,
                    'successful_requests': metric.successful_requests,
                    'failed_requests': metric.failed_requests,
                    'success_rate': round((metric.successful_requests / metric.total_requests * 100) if metric.total_requests > 0 else 0, 1),
                    'avg_processing_time_ms': metric.avg_processing_time_ms,
                    'chat_messages': metric.chat_messages,
                    'unique_ips': metric.unique_ips
                })
            
            # Convert cultural trends to JSON-serializable format
            trends_data = []
            for trend in cultural_trends:
                trends_data.append({
                    'cultural_element': trend.cultural_element,
                    'mention_count': trend.mention_count,
                    'last_mentioned': trend.last_mentioned.isoformat() if trend.last_mentioned else None
                })
            
            response_data = {
                'summary_stats': summary_stats,
                'metrics': metrics_data,
                'cultural_trends': trends_data,
                'data_period': '7 days'
            }
            return create_json_response(response_data, 200, True, 'Analytics data retrieved successfully')
        
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
    if request.headers.get('Accept') == 'application/json' or request.path.startswith('/api/'):
        return create_error_response('Resource not found', 404, 'NOT_FOUND')
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logging.error(f"Internal server error: {str(error)}")
    if request.headers.get('Accept') == 'application/json' or request.path.startswith('/api/'):
        return create_error_response('Internal server error', 500, 'INTERNAL_ERROR')
    flash('An internal error occurred. Please try again.', 'error')
    return render_template('index.html'), 500
