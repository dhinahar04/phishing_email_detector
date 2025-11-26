# macOS Quick Reference Card

**One-page reference for running the Phishing Email Detection System on macOS.**

---

## 🚀 First Time Setup (Do Once)

```bash
# 1. Install Homebrew (if needed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# 3. Install pgAdmin (optional GUI)
brew install --cask pgadmin4

# 4. Create database
createdb phishing_detector

# 5. Create tables
cd ~/path/to/phishing-detector
psql -U postgres -d phishing_detector -f database/schema.sql

# 6. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 7. Configure database connection
# Edit backend/app.py line ~51:
# db = Database(db_url='postgresql://postgres:YOUR_PASSWORD@localhost/phishing_detector')

# 8. Train ML model (takes 2-5 minutes)
python ml/phishing_ml_model.py
```

---

## 💻 Daily Usage (Every Time)

```bash
# Terminal 1: Start Backend
cd ~/path/to/phishing-detector
source venv/bin/activate
python backend/app.py
# Wait for: "🤖 ML MODEL LOADED"
# Keep this terminal open

# Terminal 2 or Browser: Open Frontend
open frontend/index.html
# Or run: python3 -m http.server 8000 (from frontend/)
```

---

## 📊 Database Quick Access

### Using pgAdmin GUI
```bash
# Open pgAdmin
open -a pgAdmin\ 4

# Connect to: localhost:5432
# Database: phishing_detector
# User: postgres
```

### Using Terminal
```bash
# Connect to database
psql -U postgres -d phishing_detector

# List tables
\dt

# View data
SELECT COUNT(*) FROM emails;
SELECT COUNT(*) FROM iocs;
SELECT * FROM ml_predictions ORDER BY created_at DESC LIMIT 5;

# Exit
\q
```

---

## 🧪 Test Commands

```bash
# Upload test email
cd data/test_emails
# Then upload phishing_paypal.eml via web interface

# Check database
psql -U postgres -d phishing_detector -c "SELECT COUNT(*) FROM emails;"

# View logs
tail -f backend/app.log  # If logging enabled
```

---

## 🛠️ Common Issues & Fixes

### PostgreSQL Not Running
```bash
brew services list
brew services start postgresql@15
```

### Port 5000 In Use
```bash
lsof -i :5000
kill -9 <PID>
```

### Database Connection Error
```bash
# Check password in backend/app.py line 51
# Verify PostgreSQL is running
psql -U postgres -l
```

### Module Not Found
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Model Not Found
```bash
python ml/phishing_ml_model.py
```

---

## 📁 Important Paths

```
~/path/to/phishing-detector/
├── backend/app.py              # Backend server
├── frontend/index.html         # Web interface
├── ml/phishing_ml_model.py       # Train model
├── database/schema.sql         # Database schema
├── models/simple_ml_model.pkl  # Trained model
├── data/test_emails/           # Test samples
└── requirements.txt            # Dependencies
```

---

## 🔗 Quick Links

- **Full Setup:** [MACOS_SETUP_COMPLETE.md](MACOS_SETUP_COMPLETE.md)
- **Quick Start:** [QUICK_START.md](QUICK_START.md)
- **All Docs:** [docs/INDEX.md](docs/INDEX.md)

---

## ✅ Health Check

```bash
# 1. PostgreSQL running?
brew services list | grep postgresql
# Expected: postgresql@15  started

# 2. Database exists?
psql -U postgres -l | grep phishing_detector
# Expected: phishing_detector

# 3. Tables exist?
psql -U postgres -d phishing_detector -c "\dt"
# Expected: 4 tables

# 4. Model exists?
ls -lh models/simple_ml_model.pkl
# Expected: ~8-10 MB file

# 5. Virtual environment works?
source venv/bin/activate && python -c "import flask; print('✓')"
# Expected: ✓
```

---

## 🎯 Demo Day Checklist

```bash
# Before presentation:
□ brew services start postgresql@15
□ cd ~/path/to/phishing-detector
□ source venv/bin/activate
□ python backend/app.py
   └─ Wait for "ML MODEL LOADED"
□ open frontend/index.html
□ Have data/test_emails/phishing_paypal.eml ready

# During demo:
□ Upload phishing_paypal.eml
□ Show: Phishing detected
□ Show: IOCs extracted
□ Show: Dashboard statistics
□ Show: Database (pgAdmin or terminal)
```

---

*Quick reference for macOS users*
