#!/bin/bash
# Setup script for the web crawler with graph visualization and MongoDB

echo "🚀 Setting up Web Crawler with Graph Visualization..."

# Backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
cd frontend
npm install reactflow
cd ..

echo ""
echo "✅ Installation complete!"
echo ""
echo "🔧 Configuration:"
echo "   - MongoDB (optional): Set MONGODB_URI environment variable"
echo "     Default: mongodb://localhost:27017/"
echo ""
echo "🚀 To start:"
echo "   1. Backend:  cd backend && export DATA_DIR=../data_wiki && export PORT=5001 && python3 server.py"
echo "   2. Frontend: cd frontend && npm start"
echo ""
echo "📝 Note: If MongoDB is not installed, the crawler will work without database storage"
