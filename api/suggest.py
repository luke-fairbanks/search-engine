from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from mongo_search import MongoSearchEngine

app = Flask(__name__)
CORS(app)

# Get MongoDB URI from environment
MONGODB_URI = os.environ.get('MONGODB_URI', '')
mongo_search_engine = None

if MONGODB_URI:
    try:
        mongo_search_engine = MongoSearchEngine(MONGODB_URI)
    except Exception as e:
        print(f"MongoDB connection failed: {e}")

@app.route('/api/suggest')
def suggest():
    """Get search suggestions"""
    query = request.args.get('q', '').strip().lower()
    limit = int(request.args.get('limit', 8))
    
    if not query or len(query) < 2:
        return jsonify({'suggestions': []})
    
    try:
        if mongo_search_engine:
            suggestions = mongo_search_engine.get_suggestions(query, limit)
            return jsonify({'suggestions': suggestions})
        else:
            return jsonify({'suggestions': []}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel serverless function handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
