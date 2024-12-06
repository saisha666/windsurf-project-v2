#!/bin/bash

echo "Starting Windsurf Project Installation (Unix/Linux)..."

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Python not found! Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Setup directories
echo "Setting up project directories..."
python3 setup_directories.py

# Initialize database
echo "Initializing database..."
python3 src/database/init_db.py

# Setup CUDA if available
python3 -c "import torch; print('CUDA Available:', torch.cuda.is_available())"

# Create necessary environment variables
echo "Setting up environment variables..."
echo "export WINDSURF_HOME=$(pwd)" >> ~/.bashrc
echo "export WINDSURF_DATA=$(pwd)/data" >> ~/.bashrc
echo "export WINDSURF_MODELS=$(pwd)/models" >> ~/.bashrc
source ~/.bashrc

# Test installation
echo "Running system tests..."
python3 -m pytest tests/

echo "Installation complete! Run 'python3 src/main.py' to start the system."
