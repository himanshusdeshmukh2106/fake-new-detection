#!/bin/bash
# Render Build Script
# This runs during deployment to set up the environment

echo "🔧 Installing Python dependencies..."
pip install -r requirements.txt

echo "📦 Downloading spaCy English model..."
python -m spacy download en_core_web_sm

echo "🔧 Installing Playwright browsers..."
playwright install chromium

echo "✅ Build completed successfully!"