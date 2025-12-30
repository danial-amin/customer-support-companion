#!/bin/bash

# Setup script for Customer Support AI

echo "🚀 Setting up Customer Support AI..."

# Check if .env exists
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "📝 Creating .env file from .env.example..."
        cp .env.example .env
        # Generate a secure SECRET_KEY
        if command -v openssl &> /dev/null; then
            SECRET_KEY=$(openssl rand -hex 32)
            # Replace the placeholder SECRET_KEY
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
            else
                # Linux
                sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
            fi
        fi
        echo "✅ .env file created from .env.example"
        echo "⚠️  Please update .env file with your API keys!"
    else
        echo "❌ .env.example not found. Please create it first."
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Run: docker-compose up -d"
echo "3. Access frontend at http://localhost:3003 (or 3000/3001 if available)"
echo "4. Access backend API docs at http://localhost:8000/docs"
echo ""
echo "✨ Setup complete!"

