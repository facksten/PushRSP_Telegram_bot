#!/bin/bash

# PushTutor Setup Script

echo "🤖 PushTutor Setup"
echo "=================="

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
major_version=$(echo $python_version | cut -d. -f1)
minor_version=$(echo $python_version | cut -d. -f2)

if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 9 ]); then
    echo "❌ Python 3.9+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env created"
fi

# Create logs directory
mkdir -p logs

# Initialize database
echo ""
echo "💾 Initializing database..."
python -c "from database import db_manager; db_manager.create_tables()" 2>/dev/null || echo "⚠️  Database already exists or error occurred"

# Make run script executable
chmod +x run.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Configure .env file with your credentials"
echo "   2. Run: ./run.sh"
echo ""
echo "🔑 Required credentials:"
echo "   - For Userbot: TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE"
echo "   - For Bot API: BOT_TOKEN"
echo "   - For LLM: At least one of GEMINI_API_KEY, OPENAI_API_KEY, OPENROUTER_API_KEY"
echo ""
