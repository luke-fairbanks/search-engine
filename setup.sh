#!/bin/bash

# Quick start script for Mini Search Engine

echo "🚀 Starting Mini Search Engine Setup..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip3 install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo ""
echo "1. If you haven't crawled yet, run:"
echo "   python3 mini_search.py crawl --start https://docs.python.org/3/ --max-pages 100 --out ./data --verbose"
echo ""
echo "2. Build the search index:"
echo "   python3 mini_search.py build --data ./data"
echo ""
echo "3. Start the backend server (in one terminal):"
echo "   python3 server.py"
echo ""
echo "4. Start the frontend dev server (in another terminal):"
echo "   cd frontend && npm start"
echo ""
echo "5. Open your browser to http://localhost:3000"
echo ""
