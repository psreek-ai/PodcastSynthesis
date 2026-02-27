#!/bin/bash
set -e

echo "🎙️ Welcome to AI Podcast Engine 2.0"
echo "======================================"

echo "📦 Installing Backend Dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate || source venv/Scripts/activate
pip install -r requirements.txt
cd ..

echo "📦 Installing Frontend Dependencies..."
cd frontend
npm install
cd ..

echo "✅ Environment setup complete!"
echo ""
echo "To start the application:"
echo "1. Terminal 1 (Backend): cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "2. Terminal 2 (Frontend): cd frontend && npm run dev"
