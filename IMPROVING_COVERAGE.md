# 🎯 Improving Search Coverage

## The Problem

When searching for "for loop", you expect to see `https://wiki.python.org/moin/ForLoop`, but it's not in the results.

**Root Cause**: The page was never crawled! This is a **coverage problem**, not a ranking problem.

## Why ForLoop Wasn't Crawled

1. **Breadth-First Crawling**: The crawler starts at one seed URL and follows links
2. **Limited Discovery**: Only 500 pages were crawled starting from BeginnersGuide
3. **No Direct Link**: If BeginnersGuide doesn't link to ForLoop (or links through many hops), it won't be found
4. **Early Termination**: The crawler stopped after 500 pages

## Solutions

### Option 1: Crawl Specific Pages (Recommended)

Add important pages as seed URLs:

```bash
# Create a more comprehensive crawl
python3 mini_search.py crawl \
  --start https://wiki.python.org/moin/BeginnersGuide \
  --max-pages 100 \
  --out ./data_wiki \
  --verbose

# Add ForLoop specifically
python3 mini_search.py crawl \
  --start https://wiki.python.org/moin/ForLoop \
  --max-pages 50 \
  --out ./data_wiki \
  --verbose

# Add other important topics
python3 mini_search.py crawl \
  --start https://wiki.python.org/moin/WhileLoop \
  --max-pages 50 \
  --out ./data_wiki \
  --verbose

# Rebuild index
python3 mini_search.py build --data ./data_wiki
```

### Option 2: Increase Max Pages

Crawl more pages to improve coverage:

```bash
python3 mini_search.py crawl \
  --start https://wiki.python.org/moin/BeginnersGuide \
  --max-pages 2000 \
  --out ./data_wiki \
  --verbose \
  --scope domain

python3 mini_search.py build --data ./data_wiki
```

### Option 3: Use Multiple Seed URLs

Modify `mini_search.py` to support multiple seed URLs:

```python
# In mini_search.py, modify crawl():
def crawl(start_urls: list[str], max_pages: int, ...):
    # Initialize queue with multiple seeds
    for url in start_urls:
        q.put(url)
    # Rest of crawl logic...
```

Then crawl from multiple starting points:

```bash
python3 mini_search.py crawl \
  --start https://wiki.python.org/moin/BeginnersGuide \
  --start https://wiki.python.org/moin/SimplePrograms \
  --start https://wiki.python.org/moin/ForLoop \
  --max-pages 1000 \
  --out ./data_wiki
```

### Option 4: Sitemap-Based Crawling (Best for Wiki)

Most wikis have a sitemap or "All Pages" list. Use it!

```python
# Enhanced crawler that uses wiki's page list
def crawl_wiki_all_pages(base_url: str, max_pages: int, out_dir: str):
    # Fetch wiki's AllPages
    all_pages_url = f"{base_url}/AllPages"
    # Parse all page links
    # Crawl each page directly
    ...
```

### Option 5: Manual Page List

Create a list of important pages to crawl:

```python
# important_pages.txt
https://wiki.python.org/moin/ForLoop
https://wiki.python.org/moin/WhileLoop
https://wiki.python.org/moin/FunctionDefinition
https://wiki.python.org/moin/ClassDefinition
https://wiki.python.org/moin/Lists
https://wiki.python.org/moin/Dictionaries
https://wiki.python.org/moin/Strings
https://wiki.python.org/moin/FileHandling
```

Then crawl them:

```bash
while read url; do
  python3 mini_search.py crawl --start "$url" --max-pages 10 --out ./data_wiki --verbose
done < important_pages.txt

python3 mini_search.py build --data ./data_wiki
```

## Quick Fix for Your Specific Case

To get ForLoop page now:

```bash
# Crawl ForLoop specifically
python3 mini_search.py crawl \
  --start https://wiki.python.org/moin/ForLoop \
  --max-pages 50 \
  --out ./data_wiki \
  --verbose

# Rebuild index (this will include all previous pages + new ones)
python3 mini_search.py build --data ./data_wiki

# Restart server
DATA_DIR=./data_wiki PORT=5001 python3 server.py
```

## Understanding the Current Results

Let's see what's actually being returned for "for loop":

1. **Glossary** - Contains definitions including "for loop"
2. **timeit** - Shows examples with for loops
3. **PythonSpeed/PerformanceTips** - Discusses for loop performance
4. **More Control Flow Tools** - Tutorial section about for loops

These are all relevant! They just don't include the specific ForLoop wiki page because it wasn't crawled.

## Improving Coverage Strategy

### 1. Analyze Coverage
```bash
# See what was crawled
cd data_wiki/pages
cat crawl_meta.json
# Check domains
grep -o '"url": "[^"]*' *.json | cut -d'"' -f4 | cut -d'/' -f3 | sort | uniq -c
```

### 2. Identify Gaps
- Missing important topics?
- Too much from one site (docs.python.org)?
- Too little from wiki?

### 3. Target Crawling
```bash
# Crawl only wiki pages
python3 mini_search.py crawl \
  --start https://wiki.python.org/moin/ \
  --max-pages 1000 \
  --out ./data_wiki_only \
  --verbose \
  --scope host  # Only wiki.python.org
```

### 4. Merge Indexes
You could build separate indexes and query both, or merge the data directories.

## Alternative: Better Starting Point

Instead of BeginnersGuide, start from a more comprehensive page:

```bash
# Start from the main page or category page
python3 mini_search.py crawl \
  --start https://wiki.python.org/moin/FrontPage \
  --max-pages 1000 \
  --out ./data_wiki \
  --verbose
```

Or start from a category that has more links:

```bash
python3 mini_search.py crawl \
  --start https://wiki.python.org/moin/CategoryTutorial \
  --max-pages 1000 \
  --out ./data_wiki \
  --verbose
```

## The Real Issue: Web Crawling is Hard

This highlights a fundamental challenge with web search:

1. **Coverage vs. Quality**: Do you want many pages or carefully selected ones?
2. **Depth vs. Breadth**: Follow many links (breadth) or deep topics (depth)?
3. **Freshness**: How often do you re-crawl?
4. **Storage**: More pages = more storage
5. **Quality**: Not all pages are worth indexing

## Recommendation

For your use case, I recommend:

```bash
# 1. Create a curated list of important pages
cat > wiki_topics.txt << EOF
https://wiki.python.org/moin/ForLoop
https://wiki.python.org/moin/WhileLoop
https://wiki.python.org/moin/FunctionDefinitions
https://wiki.python.org/moin/SimplePrograms
https://wiki.python.org/moin/BeginnersGuide
https://wiki.python.org/moin/PythonBooks
https://wiki.python.org/moin/WebFrameworks
EOF

# 2. Crawl each topic
while read url; do
  echo "Crawling: $url"
  python3 mini_search.py crawl --start "$url" --max-pages 20 --out ./data_wiki --verbose
done < wiki_topics.txt

# 3. Rebuild
python3 mini_search.py build --data ./data_wiki

# 4. Restart
DATA_DIR=./data_wiki PORT=5001 python3 server.py
```

This gives you **targeted coverage** of important topics rather than random walk through links.

## Try It Now!

```bash
# Quick test: Crawl ForLoop
python3 mini_search.py crawl \
  --start https://wiki.python.org/moin/ForLoop \
  --max-pages 10 \
  --out ./data_wiki \
  --verbose

# Rebuild
python3 mini_search.py build --data ./data_wiki

# Test search
curl -s "http://localhost:5001/api/search?q=for+loop&k=5" | python3 -m json.tool
```

Now you should see ForLoop in the results! 🎉
