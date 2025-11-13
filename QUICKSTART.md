# 🚀 Quick Start Guide

## Current Status

✅ **Backend Server**: Running on http://localhost:5001
✅ **Frontend Dev Server**: Running on http://localhost:3000
✅ **Search Index**: Built with 2000 pages indexed

## Access Your Search Engine

Open your browser to: **http://localhost:3000**

## API Endpoints

### Search
```
GET http://localhost:5001/api/search?q=python&k=10
```

Parameters:
- `q`: Search query (required)
- `alpha`: BM25 weight floor (default: 0.2)
- `beta`: PageRank weight (default: 0.8)
- `k`: Number of results (default: 10)

### Stats
```
GET http://localhost:5001/api/stats
```

## Testing the API

Try these example queries:

```bash
# Search for Python
curl "http://localhost:5001/api/search?q=python&k=5"

# Search for modules
curl "http://localhost:5001/api/search?q=modules&k=10"

# Get index statistics
curl "http://localhost:5001/api/stats"
```

## Project Structure

```
search-engine/
├── mini_search.py          # Core search engine (crawl, index, search)
├── server.py               # Flask REST API server
├── requirements.txt        # Python dependencies
├── data/                   # Search index and crawled pages
│   ├── index.json         # Inverted index
│   ├── pagerank.json      # PageRank scores
│   ├── postings.jsonl     # Term postings
│   └── pages/             # Raw crawled pages
└── frontend/              # React TypeScript UI
    ├── package.json
    ├── src/
    │   ├── App.tsx
    │   ├── components/
    │   │   ├── SearchPage.tsx
    │   │   ├── SearchBox.tsx
    │   │   └── SearchResults.tsx
    │   ├── services/
    │   │   └── api.ts
    │   └── types/
    │       └── SearchTypes.ts
    └── public/
```

## Features

### Backend
- **BM25 Ranking**: Industry-standard text relevance
- **PageRank**: Link analysis for authority scoring
- **Hybrid Ranking**: Combines BM25 and PageRank
- **REST API**: Clean JSON endpoints
- **CORS Support**: Works with React dev server

### Frontend
- **React 18** with TypeScript
- **Material-UI (MUI)**: Modern components
- **Tailwind CSS**: Utility-first styling
- **Responsive Design**: Works on mobile and desktop
- **Real-time Search**: Instant results as you type
- **Loading States**: Skeleton loaders
- **Error Handling**: User-friendly error messages

## Development Commands

### Backend (Terminal 1)
```bash
# Start Flask server
PORT=5001 python3 server.py

# Or with custom data directory
DATA_DIR=./data PORT=5001 python3 server.py
```

### Frontend (Terminal 2)
```bash
cd frontend
npm start
```

### Build for Production
```bash
# Build React app
cd frontend
npm run build

# Serve everything from Flask
cd ..
python3 server.py
# Visit http://localhost:5001
```

## Crawling More Data

To add more pages to your index:

```bash
# Crawl additional site
python3 mini_search.py crawl \
  --start https://example.com \
  --max-pages 500 \
  --out ./data \
  --verbose

# Rebuild index
python3 mini_search.py build --data ./data

# Restart server to load new index
```

## Customization

### Adjust Search Parameters
Edit `frontend/src/services/api.ts` to change default alpha/beta values:
```typescript
search: async (query: string, alpha: number = 0.2, beta: number = 0.8, k: number = 10)
```

### Change Theme
Edit `frontend/src/App.tsx` to customize colors:
```typescript
const theme = createTheme({
  palette: {
    mode: 'light', // or 'dark'
    primary: {
      main: '#1976d2', // Change primary color
    },
  },
});
```

### Modify Ranking
Edit `mini_search.py` BM25 parameters:
```python
def bm25_scores(..., k1: float = 1.2, b: float = 0.75):
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5001
lsof -ti:5001 | xargs kill -9

# Or use different port
PORT=5002 python3 server.py
```

### React Not Connecting to API
- Check that `proxy` in `frontend/package.json` matches server port
- Restart both servers after changing proxy

### No Results Found
- Make sure index is built: `ls data/index.json`
- Check server logs for errors
- Verify data directory: `DATA_DIR=./data python3 server.py`

## Next Steps

1. **Try searching!** Open http://localhost:3000 and search for topics
2. **Crawl more sites** to expand your index
3. **Customize the UI** with your own branding
4. **Deploy to production** (Heroku, AWS, etc.)
5. **Add features**: autocomplete, filters, faceted search

## Stop Servers

```bash
# Stop Flask server (Terminal 1)
Ctrl+C

# Stop React dev server (Terminal 2)
Ctrl+C
```

Enjoy your search engine! 🔍✨
