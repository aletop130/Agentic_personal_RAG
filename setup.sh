#!/bin/bash

echo "🚀 Agentic RAG - Quick Start"
echo "================================"
echo ""

echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.12+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 12 ]); then
    echo "❌ Python version $PYTHON_VERSION is not supported. Python 3.12+ is required for Regolo AI."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected (3.12+ required)"

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ All prerequisites found!"
echo ""

echo "📦 Setting up backend..."
cd backend

if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit backend/.env and add your REGOLO_API_KEY!"
    echo "   Get your API key from: https://dashboard.regolo.ai"
    echo ""
    echo "   Then run: ./setup.sh again"
    exit 0
fi

echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies."
    exit 1
fi

echo "✅ Backend dependencies installed!"
echo ""

echo "🐳 Starting Qdrant..."
cd ../docker/qdrant
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start Qdrant."
    exit 1
fi

echo "✅ Qdrant started on ports 7333 (HTTP) and 7334 (gRPC)"
echo ""

cd ../..

echo "🎉 Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit backend/.env and add your REGOLO_API_KEY"
echo "   2. Start the backend:"
echo "      cd backend"
echo "      python -m app.main"
echo "   3. Open frontend/index.html in your browser"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
