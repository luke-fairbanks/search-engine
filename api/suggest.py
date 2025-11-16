from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json

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
    query = event.get('queryStringParameters', {}).get('q', '').strip().lower()
    limit = int(event.get('queryStringParameters', {}).get('limit', 8))
    
    if not query or len(query) < 2:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'suggestions': []})
        }
    
    try:
        if mongo_search_engine:
            suggestions = mongo_search_engine.get_suggestions(query, limit)
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'suggestions': suggestions})
            }
        else:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'suggestions': []})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
