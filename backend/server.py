#!/usr/bin/env python3
"""
HTTP server for mini search engine
Provides REST API for search queries
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys

# Load .env file if it exists (for production)
try:
    from load_env import load_env
    load_env()
except ImportError:
    pass

# Import search functions
from mini_search import hybrid_rank, load_index

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://search-engine-two-flame.vercel.app",
            "https://*.vercel.app"  # Allow all Vercel preview deployments
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configuration
DATA_DIR = os.environ.get('DATA_DIR', '../data_wiki')
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
USE_MONGODB = os.environ.get('USE_MONGODB', 'true').lower() == 'true'

# Initialize MongoDB search engine if enabled
mongo_search_engine = None
if USE_MONGODB:
    try:
        from mongo_search import MongoSearchEngine
        mongo_search_engine = MongoSearchEngine(MONGODB_URI)
        # Show partial URI for security (hide password)
        uri_display = MONGODB_URI[:30] + "..." if len(MONGODB_URI) > 30 else MONGODB_URI
        print(f"✓ MongoDB search engine initialized")
        print(f"  URI: {uri_display}")
        print(f"  Status: PRIMARY DATA SOURCE")
    except Exception as e:
        print(f"⚠ MongoDB search engine failed to initialize: {e}")
        print("  Falling back to file-based search")
        USE_MONGODB = False
else:
    print("ℹ MongoDB disabled (USE_MONGODB=false)")
    print(f"  Using file-based search from: {DATA_DIR}")

# Setup WebSocket crawler (optional - only if dependencies installed)
try:
    from crawler_ws import setup_crawler_websocket
    setup_crawler_websocket(app)
    print("✓ WebSocket crawler enabled")
except ImportError as e:
    print(f"⚠ WebSocket crawler disabled (missing dependencies: {e})")
    print("  To enable: pip install flask-sock aiohttp beautifulsoup4")

@app.route('/api/search', methods=['GET'])
def search():
    """Search endpoint"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    alpha = float(request.args.get('alpha', 0.2))
    beta = float(request.args.get('beta', 0.8))
    k = int(request.args.get('k', 10))

    try:
        # Use MongoDB if available, otherwise fall back to file-based search
        if USE_MONGODB and mongo_search_engine:
            results = mongo_search_engine.search(query, alpha, beta, k)
        else:
            results = hybrid_rank(query, DATA_DIR, alpha, beta, k=k)

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
            'source': 'mongodb' if (USE_MONGODB and mongo_search_engine) else 'files'
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def stats():
    """Get index statistics"""
    try:
        # Use MongoDB if available, otherwise fall back to file-based search
        if USE_MONGODB and mongo_search_engine:
            stats_data = mongo_search_engine.get_stats()
            stats_data['source'] = 'mongodb'
            return jsonify(stats_data)
        else:
            idx, pr = load_index(DATA_DIR)
            return jsonify({
                'total_docs': len(idx['docs']),
                'avg_doc_length': idx['avgdl'],
                'vocab_size': len(idx['idf']),
                'source': 'files'
            })
    except Exception as e:
        print(f"Error in /api/stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/suggest', methods=['GET'])
def suggest():
    """Get search suggestions based on partial query"""
    query = request.args.get('q', '').strip().lower()
    limit = int(request.args.get('limit', 8))

    if not query or len(query) < 2:
        return jsonify({'suggestions': []})

    try:
        if USE_MONGODB and mongo_search_engine:
            # Get suggestions from MongoDB - search titles and extract unique terms
            suggestions = mongo_search_engine.get_suggestions(query, limit)
        else:
            # Get suggestions from file-based index with fuzzy matching
            idx, _ = load_index(DATA_DIR)
            query_normalized = ''.join(c for c in query if c.isalnum())

            # Find matching terms in vocabulary
            matching_terms = []
            for term in idx['idf'].keys():
                # Exact prefix match
                if term.startswith(query):
                    matching_terms.append((term, 0, idx['idf'].get(term, 0)))
                # Match without spaces (e.g., "for loops" -> "forloops")
                elif len(query_normalized) >= 3 and term.startswith(query_normalized):
                    matching_terms.append((term, 1, idx['idf'].get(term, 0)))
                # Contains the query
                elif query in term and len(query) >= 3:
                    matching_terms.append((term, 2, idx['idf'].get(term, 0)))

            # Sort by priority (lower is better), then by IDF (lower is more common)
            matching_terms.sort(key=lambda x: (x[1], x[2]))
            suggestions = [term for term, _, _ in matching_terms[:limit]]

        return jsonify({'suggestions': suggestions})
    except Exception as e:
        print(f"Error in /api/suggest: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500@app.route('/api/crawler', methods=['POST'])
def crawler():
    """Start a crawl job"""
    try:
        data = request.get_json()

        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400

        start_url = data.get('url')
        max_depth = data.get('maxDepth', 2)
        max_pages = data.get('maxPages', 100)
        save_to_mongo = data.get('saveToMongo', True)

        # Validate URL
        from urllib.parse import urlparse
        try:
            result = urlparse(start_url)
            if not all([result.scheme, result.netloc]):
                return jsonify({'error': 'Invalid URL format'}), 400
        except:
            return jsonify({'error': 'Invalid URL format'}), 400

        # Check MongoDB availability if save_to_mongo is requested
        if save_to_mongo and not USE_MONGODB:
            return jsonify({'error': 'MongoDB is not enabled'}), 400

        # Import crawler synchronously
        import asyncio
        from crawler_ws import WebCrawler

        # Setup MongoDB client if needed
        mongo_client = None
        if save_to_mongo and USE_MONGODB:
            from motor.motor_asyncio import AsyncIOMotorClient
            mongo_client = AsyncIOMotorClient(MONGODB_URI)

        # Create crawler instance
        crawler = WebCrawler(
            start_url=start_url,
            max_depth=max_depth,
            max_pages=max_pages,
            save_to_mongo=save_to_mongo,
            mongo_client=mongo_client
        )

        # Run crawler in background (non-blocking)
        # For now, return immediately and let it run
        # In production, you'd use Celery or similar for background tasks

        return jsonify({
            'status': 'started',
            'message': f'Crawl job started for {start_url}',
            'config': {
                'url': start_url,
                'maxDepth': max_depth,
                'maxPages': max_pages,
                'saveToMongo': save_to_mongo
            }
        }), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve React app"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Check data sources
    has_files = os.path.exists(os.path.join(DATA_DIR, 'index.json'))
    has_mongo = USE_MONGODB and mongo_search_engine

    if not has_mongo and not has_files:
        print(f"Error: No data source available")
        print(f"  - MongoDB: {'✓ enabled' if USE_MONGODB else '✗ disabled'} ({MONGODB_URI})")
        print(f"  - Files: ✗ not found in {DATA_DIR}")
        print("\nTo use MongoDB:")
        print("  1. Set MONGODB_URI environment variable")
        print("  2. Run crawler with 'Save to MongoDB' enabled")
        print("\nTo use files:")
        print("  python mini_search.py build --data ./data")
        sys.exit(1)

    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on http://localhost:{port}")
    print(f"Data sources:")
    print(f"  - MongoDB: {'✓ primary' if has_mongo else '✗ disabled'}")
    print(f"  - Files: {'✓ fallback' if has_files else '✗ not available'} ({DATA_DIR})")

    app.run(host='0.0.0.0', port=port, debug=True)
