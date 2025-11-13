#!/bin/bash

# Quick fix: Crawl specific ForLoop page

echo "🔍 Crawling ForLoop page..."

python3 backend/mini_search.py crawl \
  --start https://wiki.python.org/moin/ForLoop \
  --max-pages 10 \
  --out ./data_wiki \
  --verbose

echo ""
echo "📊 Rebuilding index..."
python3 backend/mini_search.py build --data ./data_wiki

echo ""
echo "✅ Done! Restart your server with:"
echo "   DATA_DIR=./data_wiki PORT=5001 python3 backend/server.py"
echo ""
echo "Then search for 'for loop' again!"
