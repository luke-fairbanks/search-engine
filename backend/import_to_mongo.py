#!/usr/bin/env python3
"""
Import existing crawled data into MongoDB
"""

import json
import os
import sys
from datetime import datetime
from pymongo import MongoClient

# Load .env file if available
try:
    from load_env import load_env
    load_env()
except:
    pass

def import_to_mongodb(data_dir, mongo_uri=None):
    """Import crawled pages from JSON files into MongoDB"""

    # Use environment variable if not explicitly provided
    if mongo_uri is None:
        mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')

    print(f"🔌 Connecting to MongoDB: {mongo_uri[:50]}..." if len(mongo_uri) > 50 else f"🔌 Connecting to MongoDB: {mongo_uri}")
    try:
        client = MongoClient(mongo_uri)
        db = client.crawler_db
        collection = db.crawled_pages

        # Test connection
        client.admin.command('ping')
        print("✓ Connected to MongoDB")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        print("\nMake sure MongoDB is running:")
        print("  brew services start mongodb-community")
        sys.exit(1)

    # Load metadata
    crawl_meta_path = os.path.join(data_dir, 'crawl_meta.json')
    if not os.path.exists(crawl_meta_path):
        print(f"❌ crawl_meta.json not found in {data_dir}")
        sys.exit(1)

    with open(crawl_meta_path, 'r') as f:
        crawl_meta = json.load(f)

    start_url = crawl_meta.get('start_url', 'unknown')
    print(f"📊 Crawl source: {start_url}")
    print(f"📅 Crawled at: {crawl_meta.get('timestamp', 'unknown')}")

    # Load all pages
    pages_dir = os.path.join(data_dir, 'pages')
    if not os.path.exists(pages_dir):
        print(f"❌ pages directory not found in {data_dir}")
        sys.exit(1)

    page_files = sorted([f for f in os.listdir(pages_dir) if f.endswith('.json')])
    print(f"📄 Found {len(page_files)} pages to import")

    # Clear existing data for this crawl (optional)
    print(f"🧹 Clearing existing data for {start_url}...")
    collection.delete_many({'start_url': start_url})

    # Import pages
    documents = []
    imported = 0
    errors = 0

    print("📥 Importing pages...")
    for i, filename in enumerate(page_files):
        try:
            with open(os.path.join(pages_dir, filename), 'r') as f:
                page = json.load(f)

            # Create MongoDB document
            doc = {
                'url': page.get('url', ''),
                'title': page.get('title', 'Untitled'),
                'text': page.get('text', ''),  # Store full text content
                'snippet': page.get('snippet', '')[:500],  # Limit snippet size
                'depth': page.get('depth', 0),
                'parent_url': page.get('parent_url', None),
                'link_count': len(page.get('links', [])),
                'links': page.get('links', [])[:50],  # Store first 50 links
                'length': page.get('length', 0),
                'crawled_at': datetime.fromisoformat(crawl_meta['timestamp']) if 'timestamp' in crawl_meta else datetime.utcnow(),
                'start_url': start_url,
                'imported_at': datetime.utcnow()
            }

            documents.append(doc)
            imported += 1

            # Batch insert every 100 documents
            if len(documents) >= 100:
                collection.insert_many(documents)
                documents = []
                print(f"  ✓ Imported {imported}/{len(page_files)} pages", end='\r')

        except Exception as e:
            errors += 1
            print(f"  ⚠ Error importing {filename}: {e}")

    # Insert remaining documents
    if documents:
        collection.insert_many(documents)

    print(f"\n✅ Import complete!")
    print(f"   Imported: {imported} pages")
    print(f"   Errors: {errors}")
    print(f"   Collection: crawler_db.crawled_pages")

    # Create indexes for better performance
    print("\n🔧 Creating indexes...")
    collection.create_index('url')
    collection.create_index('start_url')
    collection.create_index('depth')
    collection.create_index('crawled_at')
    print("✓ Indexes created")

    # Print summary
    print(f"\n📊 Database summary:")
    total_docs = collection.count_documents({})
    print(f"   Total documents: {total_docs}")
    print(f"   This crawl: {imported}")

    # Group by depth
    pipeline = [
        {'$match': {'start_url': start_url}},
        {'$group': {'_id': '$depth', 'count': {'$sum': 1}}},
        {'$sort': {'_id': 1}}
    ]
    depth_counts = list(collection.aggregate(pipeline))
    print(f"\n   Pages by depth:")
    for item in depth_counts:
        print(f"     Depth {item['_id']}: {item['count']} pages")

    print(f"\n🎉 Done! You can now query the data:")
    print(f"   mongosh")
    print(f"   use crawler_db")
    print(f"   db.crawled_pages.find().limit(5)")

if __name__ == '__main__':
    import argparse

    # Get default from environment
    default_mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')

    parser = argparse.ArgumentParser(description='Import crawled data into MongoDB')
    parser.add_argument('--data-dir', default='./data_wiki', help='Data directory containing crawl_meta.json and pages/')
    parser.add_argument('--mongo-uri', default=default_mongo_uri, help=f'MongoDB connection URI (default: from MONGODB_URI env var or localhost)')

    args = parser.parse_args()

    if not os.path.exists(args.data_dir):
        print(f"❌ Data directory not found: {args.data_dir}")
        sys.exit(1)

    import_to_mongodb(args.data_dir, args.mongo_uri)
