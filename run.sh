#!/bin/bash

# PushTutor Run Script

echo "🤖 Starting PushTutor Bot..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating from template..."
    cp .env.example .env
    echo "✅ .env created. Please configure it before running."
    exit 1
fi

# Create logs directory
mkdir -p logs

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
fi

# Run the bot
echo "🚀 Launching PushTutor..."
python main.py
