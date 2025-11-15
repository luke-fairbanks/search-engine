#!/bin/bash
# MongoDB Configuration
# Set your MongoDB connection string here

# For local MongoDB:
export MONGODB_URI="mongodb://localhost:27017/"

# For MongoDB Atlas or remote MongoDB, replace with your connection string:
# export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/crawler_db?retryWrites=true&w=majority"

# Enable MongoDB by default
export USE_MONGODB="true"

# Optional: Set data directory for file-based fallback
export DATA_DIR="./data"

echo "MongoDB URI: $MONGODB_URI"
echo "Use MongoDB: $USE_MONGODB"
