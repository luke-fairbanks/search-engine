#!/bin/bash

# Start the backend search server

echo "🚀 Starting search server..."
echo ""

DATA_DIR=./data_wiki PORT=5001 python3 server.py
