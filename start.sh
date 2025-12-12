#!/bin/bash

# Travel Tracker Startup Script
# This script helps you quickly set up and run the Travel Tracker application

echo "========================================="
echo "  Travel Tracker - Setup Script"
echo "========================================="
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

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Update SECRET_KEY in .env file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    fi
    
    echo "✅ .env file created with random SECRET_KEY"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file to add your API keys and OAuth credentials"
    echo "   - Google OAuth (for Gmail integration)"
    echo "   - Microsoft OAuth (for Outlook integration)"
    echo "   - Airline API keys (optional)"
    echo "   - Immich API details (optional)"
    echo "   - Google Maps API key (optional)"
    echo ""
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🏗️  Building Docker images..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "✅ Build successful!"
echo ""
echo "🚀 Starting services..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start services. Please check the error messages above."
    exit 1
fi

echo ""
echo "⏳ Waiting for database to be ready..."
sleep 10

echo ""
echo "🗄️  Running database migrations..."
docker-compose exec -T web flask db upgrade

if [ $? -ne 0 ]; then
    echo "⚠️  Database migration failed. This might be normal on first run."
    echo "   Initializing database..."
    docker-compose exec -T web flask init-db
fi

echo ""
echo "========================================="
echo "  ✅ Travel Tracker is now running!"
echo "========================================="
echo ""
echo "📍 Access the application at: http://localhost:5000"
echo ""
echo "👤 Create an admin user:"
echo "   docker-compose exec web flask create-admin"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f web"
echo ""
echo "🛑 Stop the application:"
echo "   docker-compose down"
echo ""
echo "🔄 Restart the application:"
echo "   docker-compose restart"
echo ""
echo "📖 For more information, see README.md"
echo ""
echo "========================================="
echo ""

# Open browser (optional)
read -p "Would you like to open the application in your browser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open http://localhost:5000
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open http://localhost:5000 2>/dev/null || echo "Please open http://localhost:5000 in your browser"
    else
        echo "Please open http://localhost:5000 in your browser"
    fi
fi

echo ""
echo "Happy travels! 🌍✈️"
