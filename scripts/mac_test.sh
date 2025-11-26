#!/bin/bash

#############################################
# macOS Test Script
# Phishing Email Detection System
#############################################

echo "================================================"
echo "  Phishing Email Detection System"
echo "  Automated Testing Script"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

print_header() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Check if script is run from project root
if [ ! -f "backend/app.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if test emails exist
if [ ! -d "data/test_emails" ]; then
    print_error "Test emails directory not found: data/test_emails"
    exit 1
fi

# Check if backend is running
if ! lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    print_error "Backend server is not running on port 5000"
    echo ""
    print_info "Please start the backend first:"
    echo "  ${BLUE}./scripts/mac_run.sh${NC}"
    echo ""
    echo "  Or manually:"
    echo "  ${BLUE}source venv/bin/activate${NC}"
    echo "  ${BLUE}python3 backend/app.py${NC}"
    echo ""
    exit 1
fi

print_success "Backend server is running"
echo ""

# Check if curl is available
if ! command -v curl &> /dev/null; then
    print_error "curl is not installed"
    exit 1
fi

# Test API connection
print_header "Testing API Connection"
echo ""

response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/stats)

if [ "$response" = "200" ]; then
    print_success "API is responding (HTTP $response)"
else
    print_error "API is not responding properly (HTTP $response)"
    exit 1
fi

echo ""

# Get initial stats
print_header "Initial Database Statistics"
echo ""

stats=$(curl -s http://localhost:5000/api/stats)
echo "$stats" | python3 -m json.tool 2>/dev/null || echo "$stats"

echo ""
sleep 1

# Upload phishing emails
print_header "Uploading Phishing Test Emails"
echo ""

phishing_emails=(
    "data/test_emails/phishing_paypal.eml"
    "data/test_emails/phishing_bank.eml"
    "data/test_emails/phishing_prize.eml"
    "data/test_emails/phishing_microsoft.eml"
)

for email_file in "${phishing_emails[@]}"; do
    if [ -f "$email_file" ]; then
        filename=$(basename "$email_file")
        print_info "Uploading: $filename"

        response=$(curl -s -X POST -F "email=@$email_file" http://localhost:5000/api/upload)

        # Parse response
        is_phishing=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('analysis', {}).get('is_phishing', False))" 2>/dev/null)
        confidence=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('analysis', {}).get('confidence_score', 0))" 2>/dev/null)
        ioc_count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('analysis', {}).get('iocs', [])))" 2>/dev/null)

        if [ "$is_phishing" = "True" ]; then
            print_success "Detected as PHISHING (${confidence}% confidence, ${ioc_count} IOCs)"
        else
            print_warning "Detected as LEGITIMATE (${confidence}% confidence)"
        fi

        sleep 0.5
    else
        print_warning "File not found: $email_file"
    fi
done

echo ""
sleep 1

# Upload legitimate emails
print_header "Uploading Legitimate Test Emails"
echo ""

legitimate_emails=(
    "data/test_emails/legitimate_amazon.eml"
    "data/test_emails/legitimate_github.eml"
    "data/test_emails/legitimate_newsletter.eml"
    "data/test_emails/legitimate_work.eml"
)

for email_file in "${legitimate_emails[@]}"; do
    if [ -f "$email_file" ]; then
        filename=$(basename "$email_file")
        print_info "Uploading: $filename"

        response=$(curl -s -X POST -F "email=@$email_file" http://localhost:5000/api/upload)

        # Parse response
        is_phishing=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('analysis', {}).get('is_phishing', False))" 2>/dev/null)
        confidence=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('analysis', {}).get('confidence_score', 0))" 2>/dev/null)
        ioc_count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('analysis', {}).get('iocs', [])))" 2>/dev/null)

        if [ "$is_phishing" = "False" ] || [ "$is_phishing" = "" ]; then
            print_success "Detected as LEGITIMATE (${confidence}% confidence, ${ioc_count} IOCs)"
        else
            print_warning "Detected as PHISHING (${confidence}% confidence)"
        fi

        sleep 0.5
    else
        print_warning "File not found: $email_file"
    fi
done

echo ""
sleep 1

# Get final stats
print_header "Final Database Statistics"
echo ""

stats=$(curl -s http://localhost:5000/api/stats)
echo "$stats" | python3 -m json.tool 2>/dev/null || echo "$stats"

echo ""

# Get emails list
print_header "Recent Processed Emails"
echo ""

emails=$(curl -s "http://localhost:5000/api/emails?limit=5")
echo "$emails" | python3 -m json.tool 2>/dev/null || echo "$emails"

echo ""

# Summary
print_header "Test Summary"
echo ""

total_emails=$(echo "$stats" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_emails', 0))" 2>/dev/null)
total_iocs=$(echo "$stats" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_iocs', 0))" 2>/dev/null)
phishing_count=$(echo "$stats" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('phishing_count', 0))" 2>/dev/null)

echo "  Total Emails Processed: ${CYAN}${total_emails}${NC}"
echo "  Phishing Emails Detected: ${RED}${phishing_count}${NC}"
echo "  Total IOCs Extracted: ${YELLOW}${total_iocs}${NC}"

echo ""
print_success "Testing completed!"
echo ""
print_info "Next steps:"
echo ""
echo "  1. Open the dashboard in your browser:"
echo "     ${BLUE}open frontend/index.html${NC}"
echo ""
echo "  2. View the data in the dashboard:"
echo "     - Check the statistics cards"
echo "     - View IOC distribution chart"
echo "     - Browse emails list"
echo "     - Explore IOCs tab"
echo ""
echo "  3. Check the database directly:"
echo "     ${BLUE}sqlite3 phishing_detector.db${NC}"
echo "     ${BLUE}sqlite> SELECT * FROM emails;${NC}"
echo ""
echo "================================================"
