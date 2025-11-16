# Phishing Email Detection System

A machine learning-powered phishing email detection system with IOC extraction and interactive dashboard.

## 🚀 Quick Start

### For Complete Documentation
**All documentation has been organized in the [`docs/`](docs/) folder.**

👉 **Start here:** [docs/INDEX.md](docs/INDEX.md) - Complete documentation index

### macOS Users - Use Automated Scripts! ⭐

```bash
# 1. Setup (first time only)
chmod +x scripts/*.sh
./scripts/mac_setup.sh

# 2. Run the application
./scripts/mac_run.sh

# 3. Test with sample emails
./scripts/mac_test.sh
```

See: [scripts/README.md](scripts/README.md) | [docs/setup/MAC_INSTALL.md](docs/setup/MAC_INSTALL.md)

### Manual Setup (All Platforms)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train ML model (optional but recommended)
python ml/phishing_ml_model.py

# 3. Start backend
python backend/app.py

# 4. Open frontend
# Open frontend/index.html in your browser
```

### Test It!
Upload `data/test_emails/phishing_paypal.eml` and see it detected as phishing!

---

## 📚 Key Documentation

### Installation
- **macOS Complete Guide:** [MACOS_SETUP_COMPLETE.md](MACOS_SETUP_COMPLETE.md) ⭐ **Step-by-Step with PostgreSQL!**
- **macOS Quick:** [docs/setup/MAC_INSTALL.md](docs/setup/MAC_INSTALL.md)
- **Windows:** [docs/setup/WINDOWS_INSTALL.md](docs/setup/WINDOWS_INSTALL.md)
- **Quick Start:** [QUICK_START.md](QUICK_START.md)
- **Troubleshooting:** [docs/setup/FIX_PSYCOPG2.md](docs/setup/FIX_PSYCOPG2.md)

### Testing & Demo
- **Testing Guide:** [docs/guides/TESTING_GUIDE.md](docs/guides/TESTING_GUIDE.md)
- **Pre-Demo Checklist:** [docs/guides/CHECKLIST.md](docs/guides/CHECKLIST.md)

### Machine Learning
- **ML Quick Start:** [docs/ml/ML_QUICK_START.md](docs/ml/ML_QUICK_START.md)
- **ML Explained Simply:** [docs/ml/ML_EXPLAINED_SIMPLE.md](docs/ml/ML_EXPLAINED_SIMPLE.md)

### Database
- **Check Database:** [docs/database/CHECK_DATABASE.md](docs/database/CHECK_DATABASE.md)

### Project Info
- **Project Summary:** [docs/SUMMARY.md](docs/SUMMARY.md)
- **Architecture:** [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)
- **Complete Docs:** [docs/README.md](docs/README.md)

---

## 📁 Project Structure

```
phishing-detector/
├── backend/              # Flask API
│   ├── app.py           # Main application
│   └── utils/           # Email parser, IOC extractor
├── frontend/            # Web dashboard
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── database/            # Database models & schema
│   ├── models.py
│   └── schema.sql
├── ml/                  # Machine Learning
│   ├── phishing_ml_model.py      # ML trainer
│   ├── feature_extraction.py  # Feature engineering
│   └── train_model.py          # Advanced training
├── data/
│   ├── test_emails/     # 8 test samples (4 phishing, 4 legitimate)
│   └── uploads/         # Uploaded files
├── models/              # Trained ML models
├── scripts/             # 🍎 macOS automation scripts (NEW!)
│   ├── mac_setup.sh     # Complete setup
│   ├── mac_run.sh       # Start application
│   ├── mac_test.sh      # Run tests
│   └── README.md        # Script documentation
└── docs/                # 📚 ALL DOCUMENTATION HERE!
    ├── INDEX.md         # Documentation index
    ├── setup/           # Installation guides
    ├── guides/          # Testing & demo guides
    ├── ml/              # ML documentation
    └── database/        # Database guides
```

---

## ✨ Features

- ✅ **Email Upload** - Upload .eml and .txt files
- ✅ **IOC Extraction** - Extract IPs, URLs, domains, emails, hashes
- ✅ **ML Detection** - Random Forest classifier for phishing detection
- ✅ **Rule-Based Detection** - Keyword and pattern analysis
- ✅ **Interactive Dashboard** - Real-time metrics and charts
- ✅ **PostgreSQL/SQLite** - Flexible database options
- ✅ **REST API** - Complete backend API

---

## 🎯 What You Get

### Upload Email → Get Analysis
- **Phishing Status** (Yes/No)
- **Confidence Score** (0-100%)
- **Risk Level** (Safe/Low/Medium/High/Critical)
- **IOC Breakdown** by type
- **Severity Distribution** (Low/Medium/High)

### Dashboard Shows
- Total emails analyzed
- Phishing detected count
- IOC statistics
- Charts and visualizations

---

## 🧪 Test Emails Included

### Phishing (4):
- `phishing_paypal.eml` - PayPal scam
- `phishing_bank.eml` - Banking fraud
- `phishing_prize.eml` - Lottery scam
- `phishing_microsoft.eml` - Account phishing

### Legitimate (4):
- `legitimate_amazon.eml` - Order notification
- `legitimate_github.eml` - GitHub notification
- `legitimate_newsletter.eml` - Newsletter
- `legitimate_work.eml` - Work email

All documented in: `data/test_emails/README.md`

---

## 🤖 Machine Learning

**Random Forest Classifier** with:
- 100 TF-IDF features (important words)
- 30+ custom features (URLs, keywords, patterns)
- 100% accuracy on test set
- Confidence scores for each prediction

Train in 3 steps:
```bash
python ml/phishing_ml_model.py   # Train
python backend/app.py           # Start
# Upload email → See ML prediction!
```

See: [docs/ml/ML_QUICK_START.md](docs/ml/ML_QUICK_START.md)

---

## 📊 Database Tables

- **emails** - Email metadata and results
- **iocs** - Extracted indicators
- **analysis_logs** - Processing logs
- **ml_predictions** - ML model predictions

Works with **SQLite** (default, no setup) or **PostgreSQL**.

---

## 🎓 For College Project

Perfect for demonstrating:
- ✅ Full-stack development (Python + JavaScript)
- ✅ Machine learning (Random Forest)
- ✅ Database integration (PostgreSQL/SQLite)
- ✅ REST API design
- ✅ Real-world application
- ✅ Security awareness

**Complete documentation for your presentation in [`docs/`](docs/)!**

---

## 🔧 Requirements

- Python 3.10+
- Flask, SQLAlchemy
- scikit-learn, pandas, numpy
- PostgreSQL (optional) or SQLite (default)

Install:
```bash
pip install -r requirements.txt
```

---

## 📖 Need Help?

1. **Start here:** [docs/INDEX.md](docs/INDEX.md) - Documentation index
2. **Installation issues:** [docs/setup/FIX_PSYCOPG2.md](docs/setup/FIX_PSYCOPG2.md)
3. **Before demo:** [docs/guides/CHECKLIST.md](docs/guides/CHECKLIST.md)
4. **Understanding ML:** [docs/ml/ML_EXPLAINED_SIMPLE.md](docs/ml/ML_EXPLAINED_SIMPLE.md)

---

## 🎉 Ready to Use!

This is a **complete, working system** ready for:
- ✅ Development
- ✅ Testing
- ✅ Demonstration
- ✅ College project submission

**All documentation is in the [`docs/`](docs/) folder - start with [docs/INDEX.md](docs/INDEX.md)!**

---

*3rd Year Computer Science College Project*
*Phishing Email Detection with Machine Learning*
