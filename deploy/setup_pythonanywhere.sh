#!/bin/bash
# Setup script for PythonAnywhere deployment

echo "DeepRead Studio - PythonAnywhere Setup"
echo "======================================"

# Create virtual environment
echo "Creating virtual environment..."
python3.10 -m venv ~/deepread-venv

# Activate virtual environment
source ~/deepread-venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
cd ~/DeepReadStudio
pip install -r backend/requirements.txt

# Create necessary directories
mkdir -p backend/uploads
mkdir -p data

# Initialize database
echo "Initializing database..."
cd backend
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Create admin user
echo "Creating admin user..."
flask create-admin

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure your .env file with API keys"
echo "2. Update the WSGI configuration in PythonAnywhere web tab"
echo "3. Set the source code directory to: /home/YOUR_USERNAME/DeepReadStudio/backend"
echo "4. Set the virtualenv path to: /home/YOUR_USERNAME/deepread-venv"
echo "5. Reload the web app"
