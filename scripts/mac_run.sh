#!/bin/bash

#############################################
# macOS Run Script
# Phishing Email Detection System
#############################################

echo "================================================"
echo "  Phishing Email Detection System"
echo "  Starting Application..."
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

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if script is run from project root
if [ ! -f "backend/app.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found!"
    print_info "Please run setup first: ./scripts/mac_setup.sh"
    exit 1
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi

print_success "Virtual environment activated"
echo ""

# Check if ML model exists
if [ ! -f "models/simple_ml_model.pkl" ]; then
    print_error "ML model not found!"
    print_info "Training model now..."
    python3 ml/phishing_ml_model.py

    if [ $? -ne 0 ]; then
        print_error "Failed to train ML model"
        print_info "Continuing without ML model (will use rule-based detection)"
    else
        print_success "ML model trained successfully"
    fi
    echo ""
fi

# Check if port 5000 is already in use
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    print_error "Port 5000 is already in use!"
    echo ""
    print_info "To find and kill the process using port 5000:"
    echo "  lsof -i :5000"
    echo "  kill -9 <PID>"
    echo ""
    print_info "Or run the backend on a different port by editing backend/app.py"
    exit 1
fi

# Start backend server
print_success "Starting backend server..."
echo ""
print_info "Backend API will be available at: ${BLUE}http://localhost:5000${NC}"
print_info "Frontend can be accessed at: ${BLUE}frontend/index.html${NC}"
echo ""
print_info "To open frontend automatically:"
echo "  ${BLUE}open frontend/index.html${NC}"
echo ""
print_info "Or run a local server for frontend:"
echo "  ${BLUE}cd frontend && python3 -m http.server 8000${NC}"
echo "  Then open: ${BLUE}http://localhost:8000${NC}"
echo ""
echo "================================================"
print_success "Server is starting..."
echo "================================================"
echo ""
print_info "Press Ctrl+C to stop the server"
echo ""

# Run backend
python3 backend/app.py
