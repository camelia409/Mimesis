import logging
from flask import render_template, request, jsonify, flash
from app import app
from services.qloo_service import get_fashion_archetypes
from services.gemini_service import generate_style_recommendations, chat_with_stylist

@app.route('/')
def index():
    """Main page with cultural preference input form"""
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    """Process cultural preferences and generate style recommendations"""
    try:
        # Get user input
        cultural_input = request.form.get('cultural_preferences', '').strip()
        
        if not cultural_input:
            flash('Please enter your cultural preferences', 'error')
            return render_template('index.html')
        
        logging.info(f"Processing cultural input: {cultural_input}")
        
        # Step 1: Get fashion archetypes from Qloo API
        try:
            qloo_response = get_fashion_archetypes(cultural_input)
            logging.info(f"Qloo response: {qloo_response}")
        except Exception as e:
            logging.error(f"Qloo API error: {str(e)}")
            qloo_response = {"archetypes": [], "error": str(e)}
        
        # Step 2: Generate style recommendations using Gemini
        try:
            style_recommendations = generate_style_recommendations(cultural_input, qloo_response)
            logging.info(f"Gemini recommendations: {style_recommendations}")
        except Exception as e:
            logging.error(f"Gemini API error: {str(e)}")
            style_recommendations = {
                "aesthetic_name": "Error generating recommendations",
                "brands": [],
                "outfit": "Unable to generate outfit suggestions",
                "moodboard": "Unable to generate moodboard",
                "error": str(e)
            }
        
        return render_template('results.html', 
                             user_input=cultural_input,
                             qloo_data=qloo_response,
                             recommendations=style_recommendations)
    
    except Exception as e:
        logging.error(f"Unexpected error in recommend route: {str(e)}")
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
