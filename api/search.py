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

@app.route('/api/search')
def search():
    """Search endpoint"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    alpha = float(request.args.get('alpha', 0.2))
    beta = float(request.args.get('beta', 0.8))
    k = int(request.args.get('k', 10))

    try:
        if mongo_search_engine:
            results = mongo_search_engine.search(query, alpha, beta, k)
        else:
            return jsonify({'error': 'Search engine not available'}), 503

        response = {
            'query': query,
            'total': len(results),
            'results': [
                {
                    'url': doc.url,
                    'title': doc.title,
                    'snippet': doc.snippet,
                    'score': float(score),
                    'length': doc.length
                }
                for doc, score in results
            ],
            'source': 'mongodb'
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel serverless function handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
