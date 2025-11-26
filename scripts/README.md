# macOS Scripts

Automated scripts for setting up and running the Phishing Email Detection System on macOS.

## Available Scripts

### 1. mac_setup.sh
**Purpose**: Complete setup and installation

**What it does**:
- Checks Python installation (requires 3.8+)
- Creates virtual environment
- Installs all dependencies
- Trains ML model
- Sets up database (SQLite or PostgreSQL)

**Usage**:
```bash
chmod +x scripts/mac_setup.sh
./scripts/mac_setup.sh
```

**First time setup**: Run this first!

---

### 2. mac_run.sh
**Purpose**: Start the backend server

**What it does**:
- Activates virtual environment
- Checks for ML model
- Starts Flask backend on port 5000
- Provides instructions for opening frontend

**Usage**:
```bash
chmod +x scripts/mac_run.sh
./scripts/mac_run.sh
```

**Note**: Keep this terminal window open while using the application

---

### 3. mac_test.sh
**Purpose**: Automated testing with sample emails

**What it does**:
- Verifies backend is running
- Uploads all 8 test emails (4 phishing, 4 legitimate)
- Displays detection results
- Shows database statistics

**Usage**:
```bash
# Start backend first (in another terminal)
./scripts/mac_run.sh

# Then run tests
chmod +x scripts/mac_test.sh
./scripts/mac_test.sh
```

**Output**: Shows pass/fail for each test email with confidence scores

---

### 4. mac_open_frontend.sh
**Purpose**: Open the web dashboard

**What it does**:
- Checks if backend is running
- Opens frontend in browser
- Optionally starts HTTP server for frontend

**Usage**:
```bash
chmod +x scripts/mac_open_frontend.sh
./scripts/mac_open_frontend.sh
```

**Options**:
1. Open HTML directly (quickest)
2. Start HTTP server on port 8000 (better for development)
3. Both

---

### 5. mac_check_db.sh
**Purpose**: Verify database contents

**What it does**:
- Detects database type (SQLite/PostgreSQL)
- Shows table statistics
- Displays recent emails
- Shows IOC distribution
- Provides SQL commands for manual inspection

**Usage**:
```bash
chmod +x scripts/mac_check_db.sh
./scripts/mac_check_db.sh
```

**Use when**: You want to verify data is being saved correctly

---

## Quick Start Workflow

### First Time Setup
```bash
# 1. Make all scripts executable
chmod +x scripts/*.sh

# 2. Run setup
./scripts/mac_setup.sh
```

### Daily Usage
```bash
# Terminal 1: Start backend
./scripts/mac_run.sh

# Terminal 2: Open frontend (optional)
./scripts/mac_open_frontend.sh

# Or just open directly
open frontend/index.html
```

### Testing
```bash
# With backend running:
./scripts/mac_test.sh
```

### Check Database
```bash
./scripts/mac_check_db.sh
```

---

## Troubleshooting

### "Permission denied" error
```bash
chmod +x scripts/*.sh
```

### "Backend not running" error
Make sure you've started the backend in another terminal:
```bash
./scripts/mac_run.sh
```

### "Python not found" error
Install Python 3.8 or later from https://www.python.org/downloads/macos/

### "Port already in use" error
```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>
```

### Virtual environment issues
```bash
# Remove old venv
rm -rf venv

# Run setup again
./scripts/mac_setup.sh
```

---

## Script Requirements

- **macOS**: 10.15 (Catalina) or later
- **Python**: 3.8 or later
- **Bash**: 3.2+ (pre-installed on macOS)
- **Internet**: Required for initial dependency installation

---

## Manual Setup (Without Scripts)

If you prefer manual setup, see [docs/setup/MAC_INSTALL.md](../docs/setup/MAC_INSTALL.md)

---

## Getting Help

- Full macOS guide: [docs/setup/MAC_INSTALL.md](../docs/setup/MAC_INSTALL.md)
- All documentation: [docs/INDEX.md](../docs/INDEX.md)
- Testing guide: [docs/guides/TESTING_GUIDE.md](../docs/guides/TESTING_GUIDE.md)
