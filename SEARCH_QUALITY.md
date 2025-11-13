# 🔍 Search Quality Analysis

## The Problem

You're seeing "Global Module Index" for almost every result because:

### 1. Site Structure Issue (docs.python.org)
- **Boilerplate text**: Every page has identical navigation like:
  ```
  "Global module index All modules and libraries
   General index All functions, classes, and terms
   Glossary Terms explained"
  ```
- **Duplicate content**: Multiple Python versions (3.1, 3.10, 3.11, 3.12, 3.14) with same pages
- **Index pages**: Many pages are just lists/tables with minimal unique content
- **Navigation-heavy**: More navigation than actual content on many pages

### 2. Algorithm Behavior (BM25)
BM25 works by:
- **Term Frequency (TF)**: How often a term appears in a document
- **Document Frequency (DF)**: How many documents contain the term
- **IDF = log((N - DF) / DF)**: Inverse document frequency

When almost every document contains "global module index", these terms:
- ✅ Have high TF (appear in the text)
- ❌ Have high DF (appear in 1000+ documents)
- ❌ Have low IDF (not discriminative)
- **Result**: Documents with boilerplate rank similarly

## Evidence

Checking your data:
```bash
grep -l "Global Module Index" data/pages/*.json | wc -l
# Result: 1000+ files contain this phrase
```

Sample pages:
- File 0: "3.14.0 Documentation" (version index)
- File 1: "3.10.19 Documentation" (version index)
- File 182: "Global Module Index — Python v3.1.5" (module list)
- File 500: "Copyright — Python 3.10.19" (boilerplate page)

**Too many duplicate/boilerplate pages!**

## Solutions

### ✅ Recommended: Scrape wiki.python.org

**Why wiki.python.org is better:**
- 📝 **Article-style content**: Tutorials, guides, explanations
- 🎯 **Unique content**: Each page has distinct information
- 📚 **Diverse topics**: BeginnersGuide, PythonBooks, WebFrameworks, Testing, etc.
- 🚫 **Less boilerplate**: Minimal navigation duplication
- 🔤 **Better for search**: More natural language, varied vocabulary

**Example wiki pages:**
- `wiki.python.org/moin/BeginnersGuide`
- `wiki.python.org/moin/PythonBooks`
- `wiki.python.org/moin/WebFrameworks`
- `wiki.python.org/moin/Testing`
- `wiki.python.org/moin/UsefulModules`

### Quick Start (Recommended)

```bash
# Crawl Python Wiki (better content)
./crawl_wiki.sh

# After crawling, restart server with new data
DATA_DIR=./data_wiki PORT=5001 python3 server.py
```

### Alternative: Improve Current Crawler

If you want to stick with docs.python.org, we can improve the crawler:

**1. Filter boilerplate text**
```python
# In mini_search.py, modify LinkAndTextExtractor
def handle_starttag(self, tag, attrs):
    # Skip common navigation elements
    if tag in ("script", "style", "noscript", "nav", "footer"):
        self._skip_stack.append(tag)
    # Skip elements with nav-related classes
    attrs_dict = dict(attrs)
    classes = attrs_dict.get("class", "").lower()
    if any(x in classes for x in ["navigation", "sidebar", "footer", "breadcrumb"]):
        self._skip_stack.append(tag)
```

**2. Skip index pages**
```python
# In crawl(), after fetching:
if any(x in url.lower() for x in ['/genindex.html', '/modindex.html', '/py-modindex.html']):
    if verbose:
        print(f"[skip] index page: {url}")
    continue
```

**3. Title boost**
Give more weight to title terms in BM25:
```python
# In build()
title_tokens = tokenize(title) * 3  # Triple weight for title
toks = title_tokens + tokenize(text)
```

## Recommendation

**For best results: Crawl wiki.python.org**

It will give you:
- ✅ Better variety in search results
- ✅ More natural language content
- ✅ Less duplicate pages
- ✅ More useful for actual searches

**Run this:**
```bash
./crawl_wiki.sh
```

Then restart your server:
```bash
# Stop current server (Ctrl+C)
# Start with wiki data
DATA_DIR=./data_wiki PORT=5001 python3 server.py
```

## Comparison

### docs.python.org
- ✅ Good for: API reference, technical specs
- ❌ Bad for: Search diversity, unique content
- ❌ Has: Tons of duplicate navigation, multiple versions

### wiki.python.org
- ✅ Good for: Tutorials, guides, explanations, diversity
- ✅ Has: Unique articles, less boilerplate
- ❌ May have: Fewer pages (but higher quality)

## Try It!

```bash
# Option 1: Wiki (recommended)
./crawl_wiki.sh

# Option 2: Different docs site
python3 mini_search.py crawl \
  --start https://realpython.com \
  --max-pages 300 \
  --out ./data_realpython \
  --verbose

# Option 3: Mix of sites
# Crawl multiple sites into same data directory
```

**Bottom line**: The "Global Module Index" problem is due to docs.python.org's structure. Wiki will give much better results! 🎯
