#!/bin/bash

#############################################
# macOS Open Frontend Script
# Opens frontend with local HTTP server
#############################################

echo "================================================"
echo "  Opening Frontend Dashboard"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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

# Check if backend is running
if ! lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    print_error "Backend server is not running on port 5000"
    echo ""
    print_info "Please start the backend first:"
    echo "  ${BLUE}./scripts/mac_run.sh${NC}"
    exit 1
fi

print_success "Backend is running"
echo ""

# Check which method to use
echo "How would you like to open the frontend?"
echo ""
echo "  1) Open HTML file directly (simplest)"
echo "  2) Start Python HTTP server on port 8000 (recommended)"
echo "  3) Both"
echo ""
read -p "Enter choice [1-3] (default: 1): " choice

choice=${choice:-1}

if [ "$choice" = "1" ] || [ "$choice" = "3" ]; then
    print_info "Opening frontend/index.html in default browser..."
    open frontend/index.html
    print_success "Frontend opened in browser"
    echo ""
fi

if [ "$choice" = "2" ] || [ "$choice" = "3" ]; then
    # Check if port 8000 is in use
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        print_error "Port 8000 is already in use!"
        print_info "Kill the process or use option 1"
        exit 1
    fi

    print_info "Starting HTTP server on port 8000..."
    cd frontend

    echo ""
    print_success "Frontend server starting..."
    print_info "Open your browser to: ${BLUE}http://localhost:8000${NC}"
    echo ""
    print_info "Press Ctrl+C to stop the server"
    echo ""

    # Auto-open browser after 1 second
    (sleep 1 && open http://localhost:8000) &

    python3 -m http.server 8000
fi
