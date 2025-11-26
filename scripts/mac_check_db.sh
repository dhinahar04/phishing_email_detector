#!/bin/bash

#############################################
# macOS Database Check Script
# Check database contents and statistics
#############################################

echo "================================================"
echo "  Database Verification Tool"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

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

# Detect database type
if [ -f "phishing_detector.db" ]; then
    DB_TYPE="sqlite"
    DB_FILE="phishing_detector.db"
    print_success "Found SQLite database: $DB_FILE"
else
    DB_TYPE="postgresql"
    print_info "SQLite database not found, checking PostgreSQL..."

    if command -v psql &> /dev/null; then
        print_success "PostgreSQL client found"
    else
        print_error "Neither SQLite nor PostgreSQL database found"
        exit 1
    fi
fi

echo ""

# SQLite queries
if [ "$DB_TYPE" = "sqlite" ]; then
    print_header "Database Tables"
    echo ""

    sqlite3 "$DB_FILE" ".tables"

    echo ""
    print_header "Emails Table Statistics"
    echo ""

    echo "Total emails:"
    sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM emails;"

    echo ""
    echo "Phishing emails:"
    sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM emails WHERE is_phishing = 1;"

    echo ""
    echo "Legitimate emails:"
    sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM emails WHERE is_phishing = 0;"

    echo ""
    print_header "IOCs Table Statistics"
    echo ""

    echo "Total IOCs:"
    sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM iocs;"

    echo ""
    echo "IOCs by type:"
    sqlite3 "$DB_FILE" -column -header "SELECT ioc_type, COUNT(*) as count FROM iocs GROUP BY ioc_type ORDER BY count DESC;"

    echo ""
    echo "IOCs by severity:"
    sqlite3 "$DB_FILE" -column -header "SELECT severity, COUNT(*) as count FROM iocs GROUP BY severity ORDER BY count DESC;"

    echo ""
    print_header "Recent Emails (Last 5)"
    echo ""

    sqlite3 "$DB_FILE" -column -header "SELECT id, filename, sender, subject, is_phishing, confidence_score FROM emails ORDER BY upload_date DESC LIMIT 5;"

    echo ""
    print_header "ML Predictions Table"
    echo ""

    ml_count=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM ml_predictions;")
    echo "Total ML predictions: $ml_count"

    if [ "$ml_count" -gt 0 ]; then
        echo ""
        echo "Recent predictions:"
        sqlite3 "$DB_FILE" -column -header "SELECT email_id, predicted_class, ROUND(probability, 2) as prob, model_version FROM ml_predictions ORDER BY prediction_date DESC LIMIT 5;"
    fi

    echo ""
    print_header "Interactive Database Shell"
    echo ""
    print_info "To explore the database interactively, run:"
    echo "  ${BLUE}sqlite3 $DB_FILE${NC}"
    echo ""
    print_info "Useful SQL commands:"
    echo "  ${BLUE}.tables${NC}                 - List all tables"
    echo "  ${BLUE}.schema emails${NC}          - Show emails table structure"
    echo "  ${BLUE}SELECT * FROM emails;${NC}   - View all emails"
    echo "  ${BLUE}SELECT * FROM iocs;${NC}     - View all IOCs"
    echo "  ${BLUE}.quit${NC}                   - Exit"
    echo ""

# PostgreSQL queries
else
    DB_NAME="phishing_detector"

    print_header "Database Tables"
    echo ""

    psql -d "$DB_NAME" -c "\dt"

    echo ""
    print_header "Emails Table Statistics"
    echo ""

    psql -d "$DB_NAME" -c "SELECT COUNT(*) as total_emails FROM emails;"

    psql -d "$DB_NAME" -c "SELECT COUNT(*) as phishing_emails FROM emails WHERE is_phishing = true;"

    psql -d "$DB_NAME" -c "SELECT COUNT(*) as legitimate_emails FROM emails WHERE is_phishing = false;"

    echo ""
    print_header "IOCs Table Statistics"
    echo ""

    psql -d "$DB_NAME" -c "SELECT COUNT(*) as total_iocs FROM iocs;"

    echo ""
    psql -d "$DB_NAME" -c "SELECT ioc_type, COUNT(*) as count FROM iocs GROUP BY ioc_type ORDER BY count DESC;"

    echo ""
    psql -d "$DB_NAME" -c "SELECT severity, COUNT(*) as count FROM iocs GROUP BY severity ORDER BY count DESC;"

    echo ""
    print_header "Recent Emails (Last 5)"
    echo ""

    psql -d "$DB_NAME" -c "SELECT id, filename, sender, subject, is_phishing, confidence_score FROM emails ORDER BY upload_date DESC LIMIT 5;"

    echo ""
    print_header "ML Predictions Table"
    echo ""

    psql -d "$DB_NAME" -c "SELECT COUNT(*) as total_predictions FROM ml_predictions;"

    psql -d "$DB_NAME" -c "SELECT email_id, predicted_class, ROUND(probability::numeric, 2) as prob, model_version FROM ml_predictions ORDER BY prediction_date DESC LIMIT 5;"

    echo ""
    print_header "Interactive Database Shell"
    echo ""
    print_info "To explore the database interactively, run:"
    echo "  ${BLUE}psql $DB_NAME${NC}"
    echo ""
    print_info "Useful SQL commands:"
    echo "  ${BLUE}\\dt${NC}                     - List all tables"
    echo "  ${BLUE}\\d emails${NC}              - Show emails table structure"
    echo "  ${BLUE}SELECT * FROM emails;${NC}   - View all emails"
    echo "  ${BLUE}SELECT * FROM iocs;${NC}     - View all IOCs"
    echo "  ${BLUE}\\q${NC}                      - Exit"
    echo ""
fi

print_success "Database check completed!"
echo ""
