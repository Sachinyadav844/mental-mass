#!/bin/bash
# MentalMass Backend Setup Script

echo "=========================================="
echo "MentalMass Backend Setup"
echo "=========================================="

# Check if we're in the backend directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
FLASK_ENV=development
DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
JWT_SECRET_KEY=mentalmass_secret_key_2024_production
EOF
    echo "✅ .env created"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create data directory
mkdir -p data
mkdir -p logs

# Initialize database
echo "💾 Initializing database..."
python << EOF
from database import init_db
try:
    init_db()
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"❌ Database initialization error: {e}")
    exit(1)
EOF

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the backend server, run:"
echo "  python app.py"
echo ""
echo "Server will be available at:"
echo "  http://localhost:5000"
echo ""
echo "API Documentation:"
echo "  See BACKEND_COMPLETE.md for full API reference"
echo ""
