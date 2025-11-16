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

def handler(event, context):
    """Vercel serverless function handler"""
    query = event.get('queryStringParameters', {}).get('q', '').strip()
    if not query:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': '{"error": "Query parameter q is required"}'
        }

    alpha = float(event.get('queryStringParameters', {}).get('alpha', 0.2))
    beta = float(event.get('queryStringParameters', {}).get('beta', 0.8))
    k = int(event.get('queryStringParameters', {}).get('k', 10))

    try:
        if mongo_search_engine:
            results = mongo_search_engine.search(query, alpha, beta, k)
        else:
            return {
                'statusCode': 503,
                'headers': {'Content-Type': 'application/json'},
                'body': '{"error": "Search engine not available"}'
            }

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
        
        import json
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response)
        }
    except Exception as e:
        import json
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
