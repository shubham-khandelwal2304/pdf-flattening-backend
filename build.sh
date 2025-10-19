#!/bin/bash
# Build script for Render deployment

echo "Installing system dependencies..."
apt-get update
apt-get install -y build-essential

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"
