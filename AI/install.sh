#!/bin/bash

# Exit on any error
set -e

echo "=== KhojAI Installation Script ==="

# Check if we're on a supported platform
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# Download NLTK data
echo "Downloading NLTK data..."
python3 -c "
import nltk
print('Downloading NLTK data...')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
try:
    nltk.download('punkt_tab')
except:
    pass
print('NLTK data downloaded successfully.')
"

# Download spaCy model
echo "Downloading spaCy model..."
python3 -m spacy download en_core_web_sm

# Instructions for Ollama
echo "Checking for Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "WARNING: Ollama is not installed. Please install it manually:"
    echo "  Visit: https://ollama.ai/download"
    echo "  After installing, run: ollama pull gemma2:2b"
else
    echo "Pulling Ollama model..."
    ollama pull gemma2:2b
fi

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Set up your Google API credentials in the .env file"
echo "2. Activate the virtual environment with: source venv/bin/activate"
echo "3. Run the application with: python app.py"
echo ""