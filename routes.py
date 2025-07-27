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
def analytics():
    """Analytics dashboard showing trends and performance metrics"""
    try:
        # Get popular cultural inputs
        popular_inputs = PopularCulturalInput.query.order_by(
            PopularCulturalInput.request_count.desc()
        ).limit(10).all()
        
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
                             metrics=metrics,
                             summary_stats=summary_stats)
    except Exception as e:
        logging.error(f"Error fetching analytics: {str(e)}")
        return render_template('analytics.html', 
                             popular_inputs=[],
                             metrics=[],
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
