#!/usr/bin/env python3
"""
Diagnostic tool to check data sources and help troubleshoot
"""

import os
import sys
from pathlib import Path

def check_env():
    """Check environment configuration"""
    print("=" * 60)
    print("🔧 Environment Configuration")
    print("=" * 60)

    try:
        from load_env import load_env
        load_env()
    except:
        pass

    mongodb_uri = os.environ.get('MONGODB_URI', 'NOT SET')
    use_mongodb = os.environ.get('USE_MONGODB', 'NOT SET')
    data_dir = os.environ.get('DATA_DIR', './data')

    print(f"MONGODB_URI: {mongodb_uri[:50]}..." if len(mongodb_uri) > 50 else f"MONGODB_URI: {mongodb_uri}")
    print(f"USE_MONGODB: {use_mongodb}")
    print(f"DATA_DIR: {data_dir}")
    print()

def check_mongodb():
    """Check MongoDB connection and data"""
    print("=" * 60)
    print("🗄️  MongoDB Status")
    print("=" * 60)

    try:
        from load_env import load_env
        load_env()
    except:
        pass

    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')

    try:
        from mongo_search import MongoSearchEngine
        engine = MongoSearchEngine(mongodb_uri)
        stats = engine.get_stats()

        print(f"✓ Connection: SUCCESS")
        print(f"  Documents: {stats['total_docs']}")
        print(f"  Vocabulary: {stats['vocab_size']} terms")
        print(f"  Avg doc length: {stats['avg_doc_length']:.1f}")

        if stats['total_docs'] == 0:
            print()
            print("⚠️  WARNING: No documents in MongoDB!")
            print("   To add data, you need to:")
            print("   1. Start the app: ./start.sh")
            print("   2. Go to Crawler page")
            print("   3. Toggle ON 'Save to MongoDB'")
            print("   4. Crawl some pages")
        else:
            print()
            print("✅ MongoDB has data and is ready to use!")

        engine.close()
        return stats['total_docs'] > 0

    except Exception as e:
        print(f"✗ Connection: FAILED")
        print(f"  Error: {e}")
        return False

def check_file_data():
    """Check file-based data"""
    print()
    print("=" * 60)
    print("📁 File-Based Data Status")
    print("=" * 60)

    data_dirs = ['./data', './data_wiki', '../data', '../data_wiki']
    found_data = False

    for data_dir in data_dirs:
        index_file = Path(data_dir) / 'index.json'
        pages_dir = Path(data_dir) / 'pages'

        if index_file.exists():
            print(f"✓ Found: {data_dir}/")

            if pages_dir.exists():
                page_files = list(pages_dir.glob('*.json'))
                print(f"  Index: ✓")
                print(f"  Pages: {len(page_files)}")
                found_data = True
            else:
                print(f"  Index: ✓")
                print(f"  Pages: ✗ (missing pages directory)")

    if not found_data:
        print("✗ No file-based data found")
        print("  This is OK if you're using MongoDB")

    return found_data

def show_recommendations(has_mongo_data, has_file_data):
    """Show recommendations based on current state"""
    print()
    print("=" * 60)
    print("💡 Recommendations")
    print("=" * 60)

    if has_mongo_data:
        print("✅ You're all set! MongoDB has data.")
        print("   Searches will use MongoDB by default.")
        print()
        print("   Start the app: ./start.sh")

    elif has_file_data and not has_mongo_data:
        print("⚠️  You have file-based data but no MongoDB data.")
        print()
        print("   Option 1: Import files to MongoDB")
        print("   → python import_to_mongo.py")
        print()
        print("   Option 2: Crawl new pages with MongoDB enabled")
        print("   → ./start.sh")
        print("   → Go to Crawler → Toggle ON 'Save to MongoDB'")
        print()
        print("   Option 3: Disable MongoDB to use files")
        print("   → Edit backend/.env and set: USE_MONGODB=false")

    else:
        print("⚠️  No data found in MongoDB or files.")
        print()
        print("   You need to crawl some pages:")
        print("   1. Start the app: ./start.sh")
        print("   2. Open: http://localhost:3000")
        print("   3. Go to Crawler page (hamburger menu)")
        print("   4. Toggle ON 'Save to MongoDB'")
        print("   5. Enter a URL and start crawling")

def main():
    print()
    print("╔════════════════════════════════════════════════════════╗")
    print("║          Search Engine Diagnostics                    ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()

    check_env()
    has_mongo_data = check_mongodb()
    has_file_data = check_file_data()
    show_recommendations(has_mongo_data, has_file_data)

    print()
    print("=" * 60)
    print()

if __name__ == '__main__':
    main()
