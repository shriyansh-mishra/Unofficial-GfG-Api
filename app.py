import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from scraper import GeeksforGeeksScraper
from utils import validate_username, is_rate_limited

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Enable CORS
CORS(app)

# Initialize scraper
scraper = GeeksforGeeksScraper()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/docs')
def documentation():
    return render_template('documentation.html')

@app.route('/api/profile', methods=['GET'])
def get_profile():
    username = request.args.get('username')
    
    if not validate_username(username):
        return jsonify({"error": "Invalid username parameter"}), 400
    
    if is_rate_limited(request.remote_addr):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
    
    try:
        profile_data = scraper.get_complete_profile(username)
        return jsonify(profile_data)
    except Exception as e:
        logger.error(f"Error scraping profile for {username}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/basic-info', methods=['GET'])
def get_basic_info():
    username = request.args.get('username')
    
    if not validate_username(username):
        return jsonify({"error": "Invalid username parameter"}), 400
    
    if is_rate_limited(request.remote_addr):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
    
    try:
        basic_info = scraper.get_basic_info(username)
        return jsonify(basic_info)
    except Exception as e:
        logger.error(f"Error scraping basic info for {username}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/coding-stats', methods=['GET'])
def get_coding_stats():
    username = request.args.get('username')
    
    if not validate_username(username):
        return jsonify({"error": "Invalid username parameter"}), 400
    
    if is_rate_limited(request.remote_addr):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
    
    try:
        coding_stats = scraper.get_coding_stats(username)
        return jsonify(coding_stats)
    except Exception as e:
        logger.error(f"Error scraping coding stats for {username}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/submission-data', methods=['GET'])
def get_submission_data():
    username = request.args.get('username')
    
    if not validate_username(username):
        return jsonify({"error": "Invalid username parameter"}), 400
    
    if is_rate_limited(request.remote_addr):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
    
    try:
        submission_data = scraper.get_submission_data(username)
        return jsonify(submission_data)
    except Exception as e:
        logger.error(f"Error scraping submission data for {username}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/difficulty-stats', methods=['GET'])
def get_difficulty_stats():
    username = request.args.get('username')
    
    if not validate_username(username):
        return jsonify({"error": "Invalid username parameter"}), 400
    
    if is_rate_limited(request.remote_addr):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
    
    try:
        difficulty_stats = scraper.get_difficulty_stats(username)
        return jsonify(difficulty_stats)
    except Exception as e:
        logger.error(f"Error scraping difficulty stats for {username}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/institution-languages', methods=['GET'])
def get_institution_languages():
    username = request.args.get('username')
    
    if not validate_username(username):
        return jsonify({"error": "Invalid username parameter"}), 400
    
    if is_rate_limited(request.remote_addr):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
    
    try:
        institution_languages = scraper.get_institution_languages(username)
        return jsonify(institution_languages)
    except Exception as e:
        logger.error(f"Error scraping institution and languages for {username}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/streak', methods=['GET'])
def get_streak():
    username = request.args.get('username')
    
    # Validate username
    if not validate_username(username):
        return jsonify({"error": "Invalid username parameter"}), 400
    
    # Check rate limiting
    if is_rate_limited(request.remote_addr):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
    
    try:
        streak_data = scraper.get_streak(username)
        return jsonify(streak_data)
    except Exception as e:
        logger.error(f"Error scraping streak for {username}: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# from app import app

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)