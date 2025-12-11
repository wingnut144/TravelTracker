#!/bin/bash

# Travel Tracker - GitHub Deployment Script
# This script pulls the latest code from GitHub and redeploys

set -e

echo "========================================="
echo "  Travel Tracker - GitHub Deployment"
echo "========================================="
echo ""

# Configuration
GITHUB_REPO="YOUR_USERNAME/travel-tracker"
BRANCH="main"
COMPOSE_FILE="docker-compose-github.yml"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📥 Pulling latest changes from GitHub...${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create .env file with your configuration."
    echo "You can copy from .env.example:"
    echo "  cp .env.example .env"
    exit 1
fi

echo -e "${GREEN}✅ .env file found${NC}"
echo ""

# Stop existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f $COMPOSE_FILE down

# Remove old images to force rebuild from GitHub
echo -e "${YELLOW}🗑️  Removing old images...${NC}"
docker rmi traveltracker-web:latest traveltracker-scheduler:latest 2>/dev/null || true

# Pull and rebuild from GitHub
echo -e "${YELLOW}🔨 Building from GitHub (${GITHUB_REPO}#${BRANCH})...${NC}"
docker-compose -f $COMPOSE_FILE build --no-cache

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful!${NC}"
echo ""

# Start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
docker-compose -f $COMPOSE_FILE up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to start services!${NC}"
    exit 1
fi

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Run database migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
docker-compose -f $COMPOSE_FILE exec -T web flask db upgrade

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✅ Deployment Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "📍 Application is running at: http://localhost:5000"
echo ""
echo "📊 View logs:"
echo "   docker-compose -f $COMPOSE_FILE logs -f web"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose -f $COMPOSE_FILE down"
echo ""
echo "🔄 To deploy updates in the future:"
echo "   ./deploy-github.sh"
echo ""
