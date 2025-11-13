#!/usr/bin/env python3
"""
HTTP server for mini search engine
Provides REST API for search queries
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys

# Import search functions from mini_search
from mini_search import hybrid_rank, load_index

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)  # Enable CORS for React development

# Configuration
DATA_DIR = os.environ.get('DATA_DIR', './data')

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
            ]
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def stats():
    """Get index statistics"""
    try:
        idx, pr = load_index(DATA_DIR)
        return jsonify({
            'total_docs': len(idx['docs']),
            'avg_doc_length': idx['avgdl'],
            'vocab_size': len(idx['idf'])
        })
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
    if not os.path.exists(os.path.join(DATA_DIR, 'index.json')):
        print(f"Error: Index not found in {DATA_DIR}")
        print("Please run: python mini_search.py build --data ./data")
        sys.exit(1)

    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on http://localhost:{port}")
    print(f"Data directory: {DATA_DIR}")
    app.run(host='0.0.0.0', port=port, debug=True)
