#!/bin/bash

#############################################
# Retraining Service Wrapper
# Runs the auto-retrain scheduler as a service
#############################################

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/retrain_service.log"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

# Create log directory
mkdir -p "$LOG_DIR"

print_info "========================================="
print_info "Starting Retraining Service"
print_info "========================================="
print_info "Project: $PROJECT_DIR"
print_info "Log: $LOG_FILE"
print_info ""

# Check virtual environment
if [ ! -d "$VENV_DIR" ]; then
    print_error "Virtual environment not found: $VENV_DIR"
    print_error "Run setup first: ./scripts/mac_setup.sh"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"
print_success "Virtual environment activated"

# Default: Run daily at 2 AM
SCHEDULE="${RETRAIN_SCHEDULE:-daily}"
TIME="${RETRAIN_TIME:-02:00}"
MIN_EMAILS="${RETRAIN_MIN_EMAILS:-10}"

print_info "Configuration:"
print_info "  Schedule: $SCHEDULE"
print_info "  Time: $TIME"
print_info "  Minimum emails: $MIN_EMAILS"
print_info ""

# Run the auto-retrain scheduler
cd "$PROJECT_DIR"

print_success "Starting scheduler..."
python3 ml/auto_retrain.py \
    --schedule "$SCHEDULE" \
    --time "$TIME" \
    --min-emails "$MIN_EMAILS" \
    2>&1 | tee -a "$LOG_FILE"
