from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from pdf_parser import PitchDeckParser
from fund_matcher import FundMatcher
from config import Config
import json

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Enable CORS for all domains on all routes
CORS(app)

# Initialize the PDF parser and fund matcher
pdf_parser = PitchDeckParser()
fund_matcher = FundMatcher()

def allowed_file(filename):
    """Check if the uploaded file is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Pitch Deck Parser API is running'
    })

@app.route('/api/upload-pitch-deck', methods=['POST'])
def upload_pitch_deck():
    """Upload and parse pitch deck PDF"""
    
    try:
        # Check if the post request has the file part
        if 'pitchDeck' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['pitchDeck']
        
        # Check if user selected a file
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Get additional form data
        company_name = request.form.get('companyName', '')
        stage = request.form.get('stage', '')
        funding_goal = request.form.get('fundingGoal', '')
        continents = request.form.get('continents', '[]')
        countries = request.form.get('countries', '[]')
        
        # Parse JSON strings
        try:
            continents = json.loads(continents) if continents else []
            countries = json.loads(countries) if countries else []
        except json.JSONDecodeError:
            continents = []
            countries = []
        
        if file and allowed_file(file.filename):
            # Secure the filename
            filename = secure_filename(file.filename)
            
            # Create a unique filename to avoid conflicts
            import uuid
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save the file
            file.save(filepath)
            
            try:
                print(f"📄 Processing PDF: {filepath}")
                print(f"📝 Form data: company={company_name}, stage={stage}, funding={funding_goal}")
                
                # Parse the PDF
                parsing_result = pdf_parser.parse_pitch_deck(filepath)
                print(f"🔍 Parsing result: {parsing_result}")
                
                # Add form data to the result
                parsing_result['form_data'] = {
                    'company_name': company_name,
                    'stage': stage,
                    'funding_goal': funding_goal,
                    'continents': continents,
                    'countries': countries
                }
                
                # Find matching funds if parsing was successful and no error
                if 'error' not in parsing_result:
                    print("🔍 Finding matching funds...")
                    try:
                        matching_funds = fund_matcher.find_matching_funds(parsing_result, top_n=10)
                        parsing_result['matching_funds'] = matching_funds
                        parsing_result['funds_processed'] = len(matching_funds)
                        print(f"✅ Found {len(matching_funds)} matching funds")
                    except Exception as e:
                        print(f"⚠️ Fund matching failed: {e}")
                        parsing_result['matching_funds'] = []
                        parsing_result['matching_error'] = str(e)
                
                # Clean up - remove the uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                return jsonify({
                    'success': True,
                    'message': 'Pitch deck analyzed successfully',
                    'data': parsing_result
                })
                
            except Exception as e:
                # Clean up file if parsing fails
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                return jsonify({
                    'error': f'Failed to parse PDF: {str(e)}'
                }), 500
                
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}'
        }), 500


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'error': 'File too large. Maximum size is 25MB.'
    }), 413

@app.errorhandler(404)
def not_found(e):
    """Handle not found error"""
    return jsonify({
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    return jsonify({
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Check if OpenAI API key is configured
    if not Config.OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY not found in environment variables!")
        print("Please set your OpenAI API key in a .env file or environment variable.")
    
    # Check if Airtable API key is configured
    if not Config.AIRTABLE_API_KEY:
        print("WARNING: AIRTABLE_API_KEY not found in environment variables!")
        print("Fund matching will not work without Airtable API key.")
        print("Get your API key from: https://airtable.com/account")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
