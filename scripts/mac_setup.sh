#!/bin/bash

#############################################
# macOS Setup Script
# Phishing Email Detection System
#############################################

echo "================================================"
echo "  Phishing Email Detection System - Setup"
echo "  macOS Installation Script"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if script is run from project root
if [ ! -f "backend/app.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_info "Starting setup process..."
echo ""

# Step 1: Check Python version
print_info "Step 1/7: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.8 or later"
    print_info "Visit: https://www.python.org/downloads/macos/"
    exit 1
fi

# Check Python version is 3.8+
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]; }; then
    print_error "Python 3.8 or later is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo ""

# Step 2: Create virtual environment
print_info "Step 2/7: Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi
echo ""

# Step 3: Activate virtual environment and upgrade pip
print_info "Step 3/7: Activating virtual environment..."
source venv/bin/activate

if [ $? -eq 0 ]; then
    print_success "Virtual environment activated"
else
    print_error "Failed to activate virtual environment"
    exit 1
fi

print_info "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "Pip upgraded"
echo ""

# Step 4: Install Python dependencies
print_info "Step 4/7: Installing Python dependencies..."
print_info "This may take a few minutes..."

pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    print_success "All Python dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi
echo ""

# Step 5: Create necessary directories
print_info "Step 5/7: Creating project directories..."
mkdir -p models
mkdir -p data/test_emails
mkdir -p logs

print_success "Directories created"
echo ""

# Step 6: Train ML model
print_info "Step 6/7: Training machine learning model..."
python3 ml/phishing_ml_model.py

if [ $? -eq 0 ]; then
    print_success "ML model trained and saved"
else
    print_warning "ML model training failed (you can train it manually later)"
fi
echo ""

# Step 7: Check database choice
print_info "Step 7/7: Database setup..."
echo ""
echo "Which database would you like to use?"
echo "  1) SQLite (Default - No setup required)"
echo "  2) PostgreSQL (Advanced - Requires installation)"
echo ""
read -p "Enter choice [1-2] (default: 1): " db_choice

db_choice=${db_choice:-1}

if [ "$db_choice" = "2" ]; then
    print_info "PostgreSQL selected"

    # Check if PostgreSQL is installed
    if command -v psql &> /dev/null; then
        print_success "PostgreSQL is installed"

        echo ""
        print_info "To complete PostgreSQL setup, run these commands:"
        echo ""
        echo "  # Create database"
        echo "  createdb phishing_detector"
        echo ""
        echo "  # Run schema"
        echo "  psql phishing_detector < database/schema.sql"
        echo ""
        echo "  # Update backend/app.py with your PostgreSQL password"
        echo ""
    else
        print_warning "PostgreSQL not found"
        print_info "To install PostgreSQL:"
        echo ""
        echo "  brew install postgresql@15"
        echo "  brew services start postgresql@15"
        echo ""
    fi
else
    print_success "SQLite selected (default)"
    print_info "Database will be created automatically at: phishing_detector.db"
fi

echo ""
echo "================================================"
print_success "Setup completed successfully!"
echo "================================================"
echo ""
print_info "Next steps:"
echo ""
echo "  1. Run the application:"
echo "     ${BLUE}./scripts/mac_run.sh${NC}"
echo ""
echo "  2. Or manually start:"
echo "     ${BLUE}source venv/bin/activate${NC}"
echo "     ${BLUE}python3 backend/app.py${NC}"
echo ""
echo "  3. Test with sample emails:"
echo "     ${BLUE}./scripts/mac_test.sh${NC}"
echo ""
echo "  4. Open browser to: ${BLUE}http://localhost:5000${NC}"
echo ""
print_info "For detailed instructions, see: docs/setup/MAC_INSTALL.md"
echo ""
