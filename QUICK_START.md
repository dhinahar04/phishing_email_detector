# Quick Start Guide

Simple guide to get your phishing email detector running.

---

## 🚀 3 Simple Steps

### Step 1: Train the Model (One-time)

```bash
python ml/phishing_ml_model.py
```

**What happens:**
- Trains on 3,078 emails (1,328 phishing + 1,750 legitimate)
- Takes 2-5 minutes
- Saves model to `models/simple_ml_model.pkl`
- Shows ~99.8% accuracy

**Output you'll see:**
```
============================================================
Training ML Model for Phishing Detection
============================================================

📊 Training Data:
   Phishing emails: 1328
   Legitimate emails: 1750
   Total: 3078

... (processing emails) ...

✅ Training completed!
   Training Accuracy: 99.87%

============================================================
✅ Model trained and saved successfully!
============================================================
```

---

### Step 2: Start the Backend

```bash
python backend/app.py
```

**What happens:**
- Loads your trained model
- Starts API server on port 5000
- Ready to accept email uploads

**Output you'll see:**
```
============================================================
🤖 ML MODEL LOADED
============================================================
✅ Model file: models/simple_ml_model.pkl
📊 Model size: 8.45 MB
📅 Trained on: 2025-10-19 14:30:00
💡 Using ML predictions for uploaded emails
============================================================

 * Running on http://127.0.0.1:5000
```

---

### Step 3: Open the Dashboard

**Option A: Direct (Simplest)**
```bash
# Just double-click this file:
frontend/index.html
```

**Option B: Local Server (Better)**
```bash
# In a new terminal:
cd frontend
python -m http.server 8000

# Then open browser to:
http://localhost:8000
```

---

## ✅ That's It!

Now you can:
1. Upload emails via the web interface
2. See phishing detection results
3. View IOCs extracted
4. Check dashboard statistics

---

## 🧪 Test It

Upload a test email:
- Click "Upload Email" tab
- Select `data/test_emails/phishing_paypal.eml`
- Click "Analyze Email"
- See result: **PHISHING** detected with IOCs listed

---

## 📊 What You Get

### Dashboard Shows:
- Total emails processed
- Phishing emails detected
- Total IOCs extracted
- IOC distribution chart
- Recent emails list

### For Each Email:
- Phishing/Legitimate classification
- Confidence score (0-100%)
- Risk level (Safe/Low/Medium/High/Critical)
- All extracted IOCs (URLs, IPs, domains, emails, hashes)
- Severity breakdown

---

## 🔧 Troubleshooting

### Backend Error: "Model not found"
```bash
# Train the model first:
python ml/phishing_ml_model.py
```

### Backend Error: Database connection
```bash
# Check backend/app.py line 51
# Update PostgreSQL password or use SQLite:
db = Database()  # For SQLite (no setup needed)
```

### Frontend: Can't connect to backend
```bash
# Make sure backend is running:
python backend/app.py

# Check it's on port 5000
```

---

## 📝 For macOS Users

Use the automated scripts:

```bash
# One-time setup
chmod +x scripts/mac_*.sh
./scripts/mac_setup.sh

# Run application
./scripts/mac_run.sh

# Test
./scripts/mac_test.sh
```

See: [docs/setup/MAC_INSTALL.md](docs/setup/MAC_INSTALL.md)

---

## 📚 More Documentation

- **Complete docs:** [docs/INDEX.md](docs/INDEX.md)
- **Windows guide:** [docs/setup/WINDOWS_INSTALL.md](docs/setup/WINDOWS_INSTALL.md)
- **macOS guide:** [docs/setup/MAC_INSTALL.md](docs/setup/MAC_INSTALL.md)
- **Training guide:** [docs/ml/TRAINING_DATA_GUIDE.md](docs/ml/TRAINING_DATA_GUIDE.md)
- **ML explained:** [docs/ml/ML_EXPLAINED_SIMPLE.md](docs/ml/ML_EXPLAINED_SIMPLE.md)

---

## 🎓 For Your Demo

**Show this sequence:**

1. **Training** (1 minute)
   ```bash
   python ml/phishing_ml_model.py
   ```
   Point out: 3,078 emails, 99.8% accuracy

2. **Backend** (30 seconds)
   ```bash
   python backend/app.py
   ```
   Point out: "ML MODEL LOADED" message

3. **Upload** (1 minute)
   - Open frontend
   - Upload `phishing_paypal.eml`
   - Show: Phishing detected, 85% confidence, IOCs listed

4. **Dashboard** (1 minute)
   - Show statistics
   - Show IOC chart
   - Show emails list

**Total demo time: 3-4 minutes**

---

## 🎯 Key Features to Highlight

1. **Large Dataset:** Trained on 3,078 real emails
2. **High Accuracy:** 99.8% on training data
3. **ML-Powered:** Random Forest with 139 features
4. **IOC Extraction:** Automatic URL, IP, domain detection
5. **Real-time:** Instant predictions on upload
6. **Production-Ready:** Complete web application

---

*Everything you need is ready to go!*
*Just train → start → upload → demo!*
