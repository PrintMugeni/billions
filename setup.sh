#!/bin/bash

echo "🚀 Setting up Global Price Comparison Platform"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/price_comparison

# Redis Configuration
REDIS_URL=redis://localhost:6379

# GeoIP API Key (optional)
GEOIP_API_KEY=

# Admin Secret
ADMIN_SECRET=your-admin-secret-key-change-this

# Scraping Configuration
SCRAPER_TIMEOUT=30000
SCRAPER_DELAY=1.0

# Revenue Model
MARKUP_PERCENTAGE=2.0
MIN_MARKUP_AMOUNT=1.0
MAX_MARKUP_AMOUNT=5.0
EOF
    echo "✅ Created .env file"
else
    echo "✅ .env file already exists"
fi

# Create backend .env file
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend .env file..."
    cp .env backend/.env
    echo "✅ Created backend .env file"
else
    echo "✅ Backend .env file already exists"
fi

# Create frontend .env file
if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend .env file..."
    cat > frontend/.env << EOF
REACT_APP_API_URL=http://localhost:8000
EOF
    echo "✅ Created frontend .env file"
else
    echo "✅ Frontend .env file already exists"
fi

echo ""
echo "🔧 Building and starting services..."
echo "This may take a few minutes on first run..."

# Build and start services
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "🎉 Setup complete! Your application is running:"
    echo ""
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📊 Admin Dashboard: http://localhost:3000/admin"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📋 Next steps:"
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Configure your GeoIP API key in the .env file (optional)"
    echo "3. Update the ADMIN_SECRET in the .env file"
    echo "4. Customize the scrapers for your target e-commerce sites"
    echo ""
    echo "🛑 To stop the application: docker-compose down"
    echo "🔄 To restart: docker-compose up -d"
    echo "📝 To view logs: docker-compose logs -f"
else
    echo "❌ Some services failed to start. Check the logs with: docker-compose logs"
    exit 1
fi 