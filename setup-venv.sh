#!/bin/bash
# Quick setup script for virtual environment

echo "🔧 Setting up Python virtual environment..."

# Check if venv already exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists at ./venv"
    read -p "Delete and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
    else
        echo "Keeping existing venv. To activate: source venv/bin/activate"
        exit 0
    fi
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate it
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install selenium python-dotenv supabase

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
echo ""
echo "To test your Chrome + ChromeDriver setup:"
echo "  python3 -c 'from driver_setup import setup_driver; d = setup_driver(headless=True); d.get(\"https://google.com\"); print(\"✅ Works!\", d.title); d.quit()'"
echo ""
echo "To deactivate when done:"
echo "  deactivate"
echo ""
