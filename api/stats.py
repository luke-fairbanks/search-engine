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
    try:
        if mongo_search_engine:
            stats_data = mongo_search_engine.get_stats()
            stats_data['source'] = 'mongodb'
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(stats_data)
            }
        else:
            return {
                'statusCode': 503,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Search engine not available'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
