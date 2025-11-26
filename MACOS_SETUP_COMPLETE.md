# Complete macOS Setup Guide - Step by Step

**Everything you need to run the Phishing Email Detection System on macOS from scratch.**

---

## 📋 Table of Contents

1. [Prerequisites Check](#step-1-prerequisites-check)
2. [Install Python](#step-2-install-python)
3. [Install PostgreSQL](#step-3-install-postgresql)
4. [Setup Project](#step-4-setup-project)
5. [Create Database](#step-5-create-database-in-pgadmin)
6. [Create Tables](#step-6-create-database-tables)
7. [Setup Python Environment](#step-7-setup-python-environment)
8. [Configure Application](#step-8-configure-application)
9. [Train ML Model](#step-9-train-ml-model)
10. [Run Application](#step-10-run-application)
11. [Test System](#step-11-test-system)

---

## Step 1: Prerequisites Check

Open Terminal (Applications → Utilities → Terminal) and check what you have:

```bash
# Check Python version
python3 --version

# Check if Homebrew is installed
brew --version

# Check if PostgreSQL is installed
psql --version
```

**Expected results:**
- Python 3.8 or later ✅
- Homebrew installed ✅
- PostgreSQL (we'll install if missing)

---

## Step 2: Install Python

### Check Python Version

```bash
python3 --version
```

### If Python is Missing or Too Old

**Download from official website:**
1. Go to https://www.python.org/downloads/macos/
2. Download Python 3.11 or 3.12 (latest stable)
3. Open the downloaded `.pkg` file
4. Follow installation wizard
5. Verify installation:
   ```bash
   python3 --version
   ```

---

## Step 3: Install PostgreSQL

### Option A: Using Homebrew (Recommended)

**Install Homebrew first (if not installed):**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Install PostgreSQL:**
```bash
# Install PostgreSQL 15
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Verify it's running
brew services list | grep postgresql
```

**Expected output:**
```
postgresql@15  started
```

---

### Option B: Using Postgres.app (GUI Alternative)

1. Download from https://postgresapp.com/
2. Drag Postgres.app to Applications
3. Open Postgres.app
4. Click "Initialize" to create a new server
5. Server will start automatically

---

### Install pgAdmin (GUI Tool)

**Download and install:**
```bash
brew install --cask pgadmin4
```

**Or download from:** https://www.pgadmin.org/download/pgadmin-4-macos/

**Open pgAdmin:**
```bash
# From Applications folder
open -a pgAdmin\ 4

# Or from terminal
open /Applications/pgAdmin\ 4.app
```

---

## Step 4: Setup Project

### Navigate to Project Directory

```bash
# Example - adjust path to your location
cd ~/Documents/phishing-detector

# Or if downloaded
cd ~/Downloads/phishing-detector

# Verify you're in the right place
ls -la
```

**You should see:**
- `backend/` folder
- `frontend/` folder
- `ml/` folder
- `requirements.txt` file
- `README.md` file

---

## Step 5: Create Database in pgAdmin

### 5.1 Open pgAdmin

```bash
open -a pgAdmin\ 4
```

### 5.2 Connect to PostgreSQL Server

1. **First time setup:**
   - pgAdmin will ask for a master password
   - Set a password you'll remember (e.g., `admin123`)
   - This is just for pgAdmin, not PostgreSQL

2. **Add Server (if not already added):**
   - Click: Servers → Right-click → Create → Server
   - **General Tab:**
     - Name: `Local PostgreSQL`
   - **Connection Tab:**
     - Host: `localhost`
     - Port: `5432`
     - Maintenance database: `postgres`
     - Username: `postgres`
     - Password: `password` (or leave empty for default)
   - Click **Save**

### 5.3 Create Database

**In pgAdmin:**

1. **Expand server:** Servers → Local PostgreSQL
2. **Right-click on "Databases"** → Create → Database
3. **General Tab:**
   - Database: `phishing_detector`
   - Owner: `postgres`
4. **Click "Save"**

**You should see:** `phishing_detector` database in the list ✅

---

### Alternative: Create Database via Terminal

```bash
# Connect to PostgreSQL
psql postgres

# You'll see a prompt like: postgres=#

# Create database
CREATE DATABASE phishing_detector;

# Verify it was created
\l

# You should see phishing_detector in the list

# Exit
\q
```

---

## Step 6: Create Database Tables

### 6.1 Get the SQL Script

**Open the schema file location:**
```bash
cd ~/Documents/phishing-detector/database
ls -la schema.sql
```

### 6.2 Run SQL Script in pgAdmin

**Method 1: Using Query Tool**

1. **Open Query Tool:**
   - In pgAdmin, click on `phishing_detector` database
   - Click: Tools → Query Tool (or press F5)

2. **Open SQL file:**
   - Click: File → Open
   - Navigate to: `phishing-detector/database/schema.sql`
   - Click Open

3. **Execute the script:**
   - Click the ▶️ (Execute) button
   - Or press F5

4. **Verify success:**
   - You should see: "Query returned successfully"
   - Check Messages tab for any errors

**Method 2: Using Terminal**

```bash
# Navigate to project
cd ~/Documents/phishing-detector

# Run schema script
psql -U postgres -d phishing_detector -f database/schema.sql

# You should see:
# CREATE TABLE
# CREATE TABLE
# CREATE TABLE
# CREATE TABLE
# CREATE INDEX
```

### 6.3 Verify Tables Created

**In pgAdmin:**
1. Right-click `phishing_detector` database → Refresh
2. Expand: Schemas → public → Tables
3. **You should see 4 tables:**
   - ✅ emails
   - ✅ iocs
   - ✅ analysis_logs
   - ✅ ml_predictions

**Or in Terminal:**
```bash
# Connect to database
psql -U postgres -d phishing_detector

# List tables
\dt

# You should see:
#  Schema |      Name       | Type  |  Owner
# --------+-----------------+-------+----------
#  public | analysis_logs   | table | postgres
#  public | emails          | table | postgres
#  public | iocs            | table | postgres
#  public | ml_predictions  | table | postgres

# Exit
\q
```

✅ **Tables created successfully!**

---

## Step 7: Setup Python Environment

### 7.1 Navigate to Project

```bash
cd ~/Documents/phishing-detector
```

### 7.2 Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Verify it was created
ls -la venv/
```

**You should see:** `venv/` folder with `bin/`, `lib/`, etc.

### 7.3 Activate Virtual Environment

```bash
# Activate
source venv/bin/activate

# Your prompt should change to show (venv)
# Example: (venv) user@macbook phishing-detector %
```

✅ **Virtual environment activated!**

### 7.4 Upgrade pip

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Verify pip version
pip --version
```

### 7.5 Install Requirements

```bash
# Install all dependencies
pip install -r requirements.txt

# This will take 2-3 minutes
# You'll see packages being installed:
# - Flask
# - scikit-learn
# - pandas
# - numpy
# - psycopg2-binary
# - etc.
```

**Verify installation:**
```bash
# Check installed packages
pip list

# You should see:
# Flask          3.0.0
# numpy          1.24.0
# pandas         2.0.0
# scikit-learn   1.3.0
# psycopg2-binary 2.9.0
# ... and more
```

✅ **All packages installed!**

---

## Step 8: Configure Application

### 8.1 Update Database Connection

**Open backend/app.py in a text editor:**

```bash
# Using nano
nano backend/app.py

# Or using VS Code
code backend/app.py

# Or using TextEdit
open -a TextEdit backend/app.py
```

### 8.2 Find Database Configuration Line

**Look for line ~51:**
```python
db = Database(db_url='postgresql://postgres:password@localhost/phishing_detector')
```

### 8.3 Update Password

**Change to your PostgreSQL password:**
```python
# If you didn't set a password, try empty or 'postgres'
db = Database(db_url='postgresql://postgres:postgres@localhost/phishing_detector')

# Or if you set a different password:
db = Database(db_url='postgresql://postgres:YOUR_PASSWORD@localhost/phishing_detector')
```

### 8.4 Save and Close

- **nano:** Press `Ctrl+O`, Enter, then `Ctrl+X`
- **VS Code:** Press `Cmd+S`
- **TextEdit:** Press `Cmd+S`

---

## Step 9: Train ML Model

### 9.1 Ensure Virtual Environment is Active

```bash
# Check if (venv) shows in prompt
# If not:
source venv/bin/activate
```

### 9.2 Train the Model

```bash
# Train on full dataset (3,078 emails)
python ml/phishing_ml_model.py
```

**What you'll see:**
```
============================================================
Training ML Model for Phishing Detection
============================================================

🎯 Using full training dataset from data/train/

📊 Training Data:
   Phishing emails: 1328
   Legitimate emails: 1750
   Total: 3078

🔄 Processing emails...

   Processing 1328 phishing emails...
      Processed 100/1328 phishing emails...
      Processed 200/1328 phishing emails...
      ... (continues) ...
      Processed 1300/1328 phishing emails...
   ✅ Processed 1328 phishing emails (0 errors)

   Processing 1750 legitimate emails...
      Processed 100/1750 legitimate emails...
      ... (continues) ...
   ✅ Processed 1750 legitimate emails (0 errors)

🎓 Training model on 3078 emails...
   Phishing: 1328, Legitimate: 1750

   Fitting TF-IDF vectorizer...
   Feature matrix shape: (3078, 139)
   Training Random Forest (50 trees)...

✅ Training completed!
   Training Accuracy: 99.87%

============================================================
✅ Model trained and saved successfully!
   Training Accuracy: 99.87%
   Model Location: models/simple_ml_model.pkl
============================================================

💡 To use this model:
   python backend/app.py
============================================================
```

**Training time:** 2-5 minutes

**Verify model file:**
```bash
ls -lh models/simple_ml_model.pkl

# You should see:
# -rw-r--r--  1 user  staff   8.5M Oct 19 14:30 models/simple_ml_model.pkl
```

✅ **Model trained successfully!**

---

## Step 10: Run Application

### 10.1 Start Backend (Terminal 1)

```bash
# Make sure you're in project directory
cd ~/Documents/phishing-detector

# Activate virtual environment
source venv/bin/activate

# Start backend
python backend/app.py
```

**Expected output:**
```
============================================================
🤖 ML MODEL LOADED
============================================================
✅ Model file: /path/to/models/simple_ml_model.pkl
📊 Model size: 8.45 MB
📅 Trained on: 2025-10-19 14:30:00
🔖 Version: simple-rf-v1.0
💡 Using ML predictions for uploaded emails
============================================================

📊 Database initialized

 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.10:5000
Press CTRL+C to quit
```

✅ **Backend running on port 5000!**

**Keep this terminal open!**

---

### 10.2 Open Frontend

**Option A: Direct (Simplest)**

```bash
# In a new terminal tab (Cmd+T)
cd ~/Documents/phishing-detector
open frontend/index.html
```

**Your default browser will open showing the dashboard!**

---

**Option B: Local Server (Better for Development)**

```bash
# Open new terminal tab (Cmd+T)
cd ~/Documents/phishing-detector/frontend

# Start HTTP server
python3 -m http.server 8000
```

**Then open browser:**
```
http://localhost:8000
```

✅ **Frontend is now accessible!**

---

## Step 11: Test System

### 11.1 Upload Test Email

1. **Open the dashboard** (http://localhost:8000 or frontend/index.html)
2. **Click "Upload Email" tab**
3. **Click "Choose File"**
4. **Navigate to:** `data/test_emails/phishing_paypal.eml`
5. **Click "Analyze Email"**

### 11.2 Expected Results

**You should see:**
```
✅ Email Analysis Complete

Status: PHISHING DETECTED
Confidence: 87.3%
Risk Level: High

IOCs Extracted: 15
├─ URLs: 8
├─ Domains: 3
├─ IP Addresses: 2
├─ Email Addresses: 2
└─ File Hashes: 0

Severity Distribution:
├─ High: 5
├─ Medium: 7
└─ Low: 3

⚠️ Warning: Multiple suspicious indicators detected
```

### 11.3 Check Backend Terminal

**In the backend terminal, you should see:**
```
127.0.0.1 - - [19/Oct/2025 14:35:00] "POST /api/upload HTTP/1.1" 200 -
ML Prediction: True (87.3%), Rule-based: True (85.0%)
IOCs extracted: 15
```

### 11.4 Check Database in pgAdmin

**In pgAdmin:**

1. **Open Query Tool** on `phishing_detector` database
2. **Run these queries:**

```sql
-- Check emails table
SELECT COUNT(*) FROM emails;
-- Should show: 1

-- Check IOCs table
SELECT COUNT(*) FROM iocs;
-- Should show: 15

-- Check ML predictions
SELECT * FROM ml_predictions;
-- Should show your prediction

-- View email details
SELECT
    filename,
    is_phishing,
    confidence_score,
    sender,
    subject
FROM emails
ORDER BY upload_date DESC
LIMIT 5;
```

✅ **System is working correctly!**

---

## 🎉 Success Checklist

- ✅ Python 3.8+ installed
- ✅ PostgreSQL installed and running
- ✅ Database `phishing_detector` created
- ✅ Tables created (emails, iocs, analysis_logs, ml_predictions)
- ✅ Virtual environment created and activated
- ✅ All packages installed
- ✅ Database connection configured
- ✅ ML model trained (99.87% accuracy)
- ✅ Backend running on port 5000
- ✅ Frontend accessible
- ✅ Test email analyzed successfully
- ✅ Data saved to database

**Everything is working! 🚀**

---

## 📝 Daily Usage (After Setup)

**Every time you want to run the application:**

```bash
# Terminal 1: Backend
cd ~/Documents/phishing-detector
source venv/bin/activate
python backend/app.py

# Terminal 2: Frontend (optional)
cd ~/Documents/phishing-detector/frontend
python3 -m http.server 8000

# Or just open:
open frontend/index.html
```

---

## 🛑 Stopping the Application

```bash
# In each terminal:
Press Ctrl+C

# Deactivate virtual environment:
deactivate
```

---

## 🔧 Troubleshooting

### Issue 1: PostgreSQL Not Starting

```bash
# Check status
brew services list

# If stopped, start it
brew services start postgresql@15

# Check it's running
ps aux | grep postgres
```

---

### Issue 2: Database Connection Error

**Error:** `connection to server at "localhost" failed`

**Solution:**
```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Try connecting manually
psql -U postgres -d phishing_detector

# If password error, update backend/app.py with correct password
```

---

### Issue 3: Port 5000 Already in Use

```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or change port in backend/app.py (last line):
# app.run(debug=True, host='0.0.0.0', port=5001)
```

---

### Issue 4: Module Not Found

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt

# Check what's installed
pip list
```

---

### Issue 5: Permission Denied

```bash
# Fix permissions
chmod +x scripts/*.sh

# Or run with bash explicitly
bash scripts/mac_setup.sh
```

---

## 📚 Additional Resources

### Quick Scripts (Automated)

After initial setup, you can use these scripts:

```bash
# Make scripts executable
chmod +x scripts/mac_*.sh

# Run everything
./scripts/mac_setup.sh      # One-time setup
./scripts/mac_run.sh         # Start backend
./scripts/mac_test.sh        # Run tests
```

### Documentation

- **Full docs:** [docs/INDEX.md](docs/INDEX.md)
- **ML guide:** [docs/ml/TRAINING_DATA_GUIDE.md](docs/ml/TRAINING_DATA_GUIDE.md)
- **Testing:** [docs/guides/TESTING_GUIDE.md](docs/guides/TESTING_GUIDE.md)

---

## 🎓 For Your College Project Demo

### Pre-Demo Checklist

**Day before presentation:**
```bash
# 1. Start PostgreSQL
brew services start postgresql@15

# 2. Verify database exists
psql -U postgres -l | grep phishing_detector

# 3. Check model exists
ls -lh models/simple_ml_model.pkl

# 4. Quick test
source venv/bin/activate
python backend/app.py
# (Check for "ML MODEL LOADED")
```

**On demo day:**
```bash
# Terminal 1
cd ~/Documents/phishing-detector
source venv/bin/activate
python backend/app.py

# Terminal 2
open frontend/index.html

# Upload test email and show results
```

---

## 🎯 Summary

**Complete setup:**
1. ✅ Install Python 3
2. ✅ Install PostgreSQL
3. ✅ Install pgAdmin
4. ✅ Create database `phishing_detector`
5. ✅ Run `schema.sql` to create tables
6. ✅ Create virtual environment
7. ✅ Install requirements
8. ✅ Configure database connection
9. ✅ Train ML model
10. ✅ Run backend
11. ✅ Open frontend
12. ✅ Test with sample email

**You're all set! 🎉**

---

*Last Updated: 2025-10-19*
*For macOS 10.15 (Catalina) or later*
