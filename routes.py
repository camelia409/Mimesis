import logging
import json
import time
from datetime import datetime, date
from flask import render_template, request, jsonify, flash
from app import app, db
from models import StyleRequest, ChatMessage, PopularCulturalInput, SystemMetrics
from services.qloo_service import get_fashion_archetypes
from services.gemini_service import generate_style_recommendations, chat_with_stylist

@app.route('/')
def index():
    """Main page with cultural preference input form"""
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
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
            ip_address=user_ip
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
    """Optional AI stylist chat feature"""
    try:
        user_message = request.form.get('message', '').strip()
        context = request.form.get('context', '')
        
        if not user_message:
            return jsonify({'error': 'Please enter a message'})
        
        # Generate chat response using Gemini
        chat_response = chat_with_stylist(user_message, context)
        
        return jsonify({
            'response': chat_response,
            'status': 'success'
        })
    
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        return jsonify({
            'error': 'Unable to process your message. Please try again.',
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
