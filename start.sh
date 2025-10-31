#!/bin/bash

# GraphRAG Explorer - Quick Start Script
# This script helps you get started with GraphRAG Explorer

set -e

echo "🚀 GraphRAG Explorer - Quick Start"
echo "===================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Backend .env file not found. Creating from template..."
    cp backend/.env.example backend/.env
    echo ""
    echo "📝 Please edit backend/.env and add your OpenAI API key:"
    echo "   OPENAI_API_KEY=your_key_here"
    echo ""
    echo "Press Enter after you've added your API key..."
    read -r
fi

# Start Docker containers
echo "🐳 Starting Docker containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ GraphRAG Explorer is running!"
    echo ""
    echo "📍 Access the application:"
    echo "   Frontend:       http://localhost:3000"
    echo "   Backend API:    http://localhost:8000"
    echo "   API Docs:       http://localhost:8000/docs"
    echo "   Neo4j Browser:  http://localhost:7474"
    echo "                   (username: neo4j, password: password)"
    echo ""
    echo "📖 Next steps:"
    echo "   1. Open http://localhost:3000 in your browser"
    echo "   2. Upload a document (try data/example_document.txt)"
    echo "   3. View the knowledge graph"
    echo "   4. Ask questions and compare RAG approaches"
    echo ""
    echo "🛑 To stop the application, run: docker-compose down"
    echo ""
else
    echo "❌ Failed to start services. Check logs with: docker-compose logs"
    exit 1
fi
