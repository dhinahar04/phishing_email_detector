# Auto-Retrain Feature (Optional)

This folder contains the automatic retraining functionality that was developed but is not currently enabled in the main application.

## What's Here

- `auto_retrain.py` - Automatic model retraining script
- `AUTO_RETRAIN_GUIDE.md` - Complete guide for auto-retraining
- `IOC_BASED_RETRAINING.md` - IOC-based retraining approach
- `RETRAINING_QUICKREF.md` - Quick reference
- Service files for running scheduler

## Why It's Disabled

For a college project demo, manual training is simpler and more reliable:
- Train once: `python ml/phishing_ml_model.py`
- Model works for all demos
- No complexity during presentation

## If You Want to Enable It

1. Copy `auto_retrain.py` back to `ml/` folder
2. Run: `python ml/auto_retrain.py --help`
3. See documentation in this folder

## Current Approach (Recommended for Demo)

**Simple and reliable:**
```bash
# Train model once
python ml/phishing_ml_model.py

# Start backend (uses trained model)
python backend/app.py

# Upload emails - model makes predictions
# No automatic retraining needed
```

This is perfect for your college project!
