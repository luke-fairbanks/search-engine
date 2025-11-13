#!/bin/bash

# Crawl Python Wiki for better search results

echo "🕷️  Crawling Python Wiki..."
echo "This will give more diverse, article-style content"
echo ""

# Create new data directory for wiki
mkdir -p data_wiki

# Crawl wiki.python.org
python3 backend/mini_search.py crawl \
  --start https://wiki.python.org/moin/BeginnersGuide \
  --max-pages 500 \
  --out ./data_wiki \
  --verbose \
  --scope domain

echo ""
echo "✅ Crawl complete!"
echo ""
echo "Building search index..."
python3 backend/mini_search.py build --data ./data_wiki

echo ""
echo "🎉 Done! To use the wiki data:"
echo "   DATA_DIR=./data_wiki PORT=5001 python3 backend/server.py"
echo ""
