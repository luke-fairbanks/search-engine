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

@app.route('/api/stats')
def stats():
    """Get index statistics"""
    try:
        if mongo_search_engine:
            stats_data = mongo_search_engine.get_stats()
            stats_data['source'] = 'mongodb'
            return jsonify(stats_data)
        else:
            return jsonify({'error': 'Search engine not available'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel serverless function handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
