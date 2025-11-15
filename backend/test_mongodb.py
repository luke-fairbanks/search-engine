#!/usr/bin/env python3
"""
Test MongoDB search engine connection and basic functionality
"""

import sys
import os

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("Testing MongoDB connection...")

    mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    print(f"  URI: {mongo_uri}")

    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("  ✓ Connection successful")

        # Check database
        db = client.crawler_db
        collection = db.crawled_pages
        count = collection.count_documents({})
        print(f"  ✓ Found {count} documents in crawled_pages collection")

        client.close()
        return True
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return False

def test_mongo_search_engine():
    """Test MongoSearchEngine class"""
    print("\nTesting MongoSearchEngine...")

    try:
        from mongo_search import MongoSearchEngine

        mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
        engine = MongoSearchEngine(mongo_uri)
        print("  ✓ MongoSearchEngine initialized")

        # Get stats
        stats = engine.get_stats()
        print(f"  ✓ Stats: {stats['total_docs']} docs, {stats['vocab_size']} terms")

        # Try a simple search (only if we have data)
        if stats['total_docs'] > 0:
            results = engine.search("test", k=5)
            print(f"  ✓ Search returned {len(results)} results")
        else:
            print("  ⚠ No documents to search (crawl some pages first)")

        engine.close()
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test that all required packages are installed"""
    print("\nTesting Python packages...")

    packages = [
        'flask',
        'flask_cors',
        'pymongo',
        'motor',
        'flask_sock',
        'aiohttp',
        'bs4'
    ]

    all_ok = True
    for package in packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            all_ok = False

    return all_ok

def main():
    print("=" * 50)
    print("MongoDB Integration Test")
    print("=" * 50)
    print()

    # Test imports
    if not test_imports():
        print("\n❌ Some packages are missing")
        print("Run: pip install -r requirements.txt")
        return False

    # Test MongoDB connection
    if not test_mongodb_connection():
        print("\n❌ MongoDB connection failed")
        print("Make sure MongoDB is running or check your MONGODB_URI")
        return False

    # Test search engine
    if not test_mongo_search_engine():
        print("\n❌ MongoSearchEngine test failed")
        return False

    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    print("=" * 50)
    print("\nYou're ready to use MongoDB with your search engine!")
    print("Start the server with: ./start.sh")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
