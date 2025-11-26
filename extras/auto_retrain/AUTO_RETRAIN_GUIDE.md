# Automatic Model Retraining Guide

Complete guide for setting up and using automatic ML model retraining with scheduled processes.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [Quick Start](#quick-start)
4. [Configuration Options](#configuration-options)
5. [Scheduling Methods](#scheduling-methods)
6. [User Feedback System](#user-feedback-system)
7. [Monitoring & Logs](#monitoring--logs)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The automatic retraining system allows your ML model to improve over time by:
1. **Collecting feedback** from users about prediction accuracy
2. **Retraining the model** on confirmed data from the database
3. **Running on a schedule** (hourly, daily, weekly)
4. **Backing up old models** before creating new ones

### When to Use Automatic Retraining

✅ **Good for:**
- Production systems with real users
- Systems that process many emails over time
- When you want the model to adapt to new phishing patterns

❌ **NOT needed for:**
- College project demos with fixed test data
- Initial development/testing
- Small datasets (<20 emails)

---

## How It Works

### Data Flow

```
1. User uploads email
   ↓
2. System makes prediction
   ↓
3. User provides feedback (optional)
   ├─ "Correct" → Confirmed data
   └─ "Wrong" → Corrected data
   ↓
4. Data stored in database with labels
   ↓
5. Scheduled retraining runs
   ├─ Checks if enough new data (default: 10 emails)
   ├─ Backs up current model
   ├─ Trains new model on all database data
   └─ Saves new model
   ↓
6. Backend restarts and loads new model
   ↓
7. Improved predictions!
```

### Retraining Triggers

The system retrains when:
- ✅ Minimum new emails threshold reached (default: 10)
- ✅ Scheduled time arrives (e.g., daily at 2 AM)
- ✅ Manual trigger via command

The system does NOT retrain if:
- ❌ Less than 10 new emails since last training
- ❌ Less than 4 total emails in database
- ❌ Less than 2 of each class (phishing/legitimate)

---

## Quick Start

### Step 1: Install Dependencies

```bash
# Install the schedule package (added to requirements.txt)
pip install schedule
```

### Step 2: One-Time Manual Retraining

Test the retraining system manually:

```bash
# Check if retraining is needed
python ml/auto_retrain.py

# Force retraining even if not enough data
python ml/auto_retrain.py --force
```

### Step 3: Run Scheduled Retraining

```bash
# Daily retraining at 2 AM
python ml/auto_retrain.py --schedule daily --time 02:00

# Hourly checks
python ml/auto_retrain.py --schedule hourly

# Weekly on Monday at 3 AM
python ml/auto_retrain.py --schedule weekly --time 03:00
```

### Step 4: Set Up as Background Service (Optional)

See [Scheduling Methods](#scheduling-methods) below for systemd/launchd setup.

---

## Configuration Options

### Command Line Arguments

```bash
python ml/auto_retrain.py [OPTIONS]
```

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--schedule` | Schedule type | None (run once) | `daily`, `hourly`, `weekly` |
| `--time` | Time to run (HH:MM) | `02:00` | `03:30` |
| `--min-emails` | Minimum new emails needed | `10` | `20` |
| `--force` | Force retraining | False | `--force` |
| `--db-url` | Database URL | SQLite default | `postgresql://...` |

### Examples

**Check once and exit:**
```bash
python ml/auto_retrain.py
```

**Force retrain with only 5 emails:**
```bash
python ml/auto_retrain.py --force --min-emails 5
```

**Daily at midnight:**
```bash
python ml/auto_retrain.py --schedule daily --time 00:00
```

**Hourly with PostgreSQL:**
```bash
python ml/auto_retrain.py \
    --schedule hourly \
    --db-url "postgresql://postgres:password@localhost/phishing_detector"
```

---

## Scheduling Methods

### Method 1: Simple Background Process (Development)

**Linux/macOS:**
```bash
# Run in background
nohup python ml/auto_retrain.py --schedule daily > logs/retrain.log 2>&1 &

# Check if running
ps aux | grep auto_retrain

# Stop
pkill -f auto_retrain.py
```

**macOS with script:**
```bash
# Use the provided wrapper script
chmod +x scripts/retrain_service.sh
./scripts/retrain_service.sh &
```

---

### Method 2: Systemd Service (Linux Production)

**Step 1: Edit service file**

Edit `scripts/phishing-retrain.service`:
```ini
[Service]
User=YOUR_USERNAME
WorkingDirectory=/path/to/phishing-detector
Environment="PATH=/path/to/phishing-detector/venv/bin"
ExecStart=/path/to/phishing-detector/venv/bin/python3 /path/to/phishing-detector/ml/auto_retrain.py --schedule daily --time 02:00
```

**Step 2: Install and enable**

```bash
# Copy service file
sudo cp scripts/phishing-retrain.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable (start on boot)
sudo systemctl enable phishing-retrain

# Start now
sudo systemctl start phishing-retrain

# Check status
sudo systemctl status phishing-retrain

# View logs
sudo journalctl -u phishing-retrain -f
```

**Step 3: Manage service**

```bash
# Stop
sudo systemctl stop phishing-retrain

# Restart
sudo systemctl restart phishing-retrain

# Disable (don't start on boot)
sudo systemctl disable phishing-retrain
```

---

### Method 3: LaunchAgent (macOS Production)

**Step 1: Edit plist file**

Edit `scripts/com.phishing.retrain.plist`:
```xml
<key>ProgramArguments</key>
<array>
    <string>/path/to/phishing-detector/scripts/retrain_service.sh</string>
</array>

<key>WorkingDirectory</key>
<string>/path/to/phishing-detector</string>

<key>StandardOutPath</key>
<string>/Users/YOUR_USERNAME/Library/Logs/phishing-retrain.log</string>
```

**Step 2: Install and load**

```bash
# Copy to LaunchAgents
cp scripts/com.phishing.retrain.plist ~/Library/LaunchAgents/

# Load (start now)
launchctl load ~/Library/LaunchAgents/com.phishing.retrain.plist

# Check if loaded
launchctl list | grep phishing

# View logs
tail -f ~/Library/Logs/phishing-retrain.log
```

**Step 3: Manage agent**

```bash
# Unload (stop)
launchctl unload ~/Library/LaunchAgents/com.phishing.retrain.plist

# Remove
rm ~/Library/LaunchAgents/com.phishing.retrain.plist
launchctl remove com.phishing.retrain
```

---

### Method 4: Cron (Unix/Linux/macOS)

**Step 1: Create wrapper script**

Create `scripts/cron_retrain.sh`:
```bash
#!/bin/bash
cd /path/to/phishing-detector
source venv/bin/activate
python3 ml/auto_retrain.py >> logs/cron_retrain.log 2>&1
```

**Step 2: Make executable**
```bash
chmod +x scripts/cron_retrain.sh
```

**Step 3: Add to crontab**
```bash
# Edit crontab
crontab -e

# Daily at 2 AM
0 2 * * * /path/to/phishing-detector/scripts/cron_retrain.sh

# Every 6 hours
0 */6 * * * /path/to/phishing-detector/scripts/cron_retrain.sh

# Weekly on Sunday at 3 AM
0 3 * * 0 /path/to/phishing-detector/scripts/cron_retrain.sh
```

**View cron logs:**
```bash
tail -f logs/cron_retrain.log
```

---

## User Feedback System

### How Feedback Works

When users upload emails, they can provide feedback:
1. **Confirmed** - Prediction was correct
2. **Corrected** - Prediction was wrong

This feedback is used to:
- ✅ Improve training data quality
- ✅ Track model accuracy
- ✅ Identify problematic patterns

### Providing Feedback via API

```bash
# Confirm prediction was correct
curl -X POST http://localhost:5000/api/feedback/123 \
  -H "Content-Type: application/json" \
  -d '{"is_correct": true, "actual_class": "phishing"}'

# Correct a wrong prediction
curl -X POST http://localhost:5000/api/feedback/123 \
  -H "Content-Type: application/json" \
  -d '{"is_correct": false, "actual_class": "legitimate"}'
```

### Viewing Feedback Stats

```bash
curl http://localhost:5000/api/feedback/stats
```

**Response:**
```json
{
  "total_emails": 50,
  "with_feedback": 25,
  "without_feedback": 25,
  "confirmed": 22,
  "corrected": 3,
  "accuracy": 88.0
}
```

### Database Schema

Feedback is stored in the `emails` table:

| Column | Type | Description |
|--------|------|-------------|
| `user_feedback` | VARCHAR(20) | 'confirmed', 'corrected', or NULL |
| `user_confirmed_class` | BOOLEAN | User's confirmed classification |
| `feedback_date` | TIMESTAMP | When feedback was provided |

---

## Monitoring & Logs

### Retraining Output

When retraining runs, you'll see:

```
============================================================
🔄 AUTOMATIC MODEL RETRAINING
============================================================

📋 Check: 15 new emails since last training

------------------------------------------------------------
📊 Preparing training data from 30 emails...
   📧 Phishing emails: 15
   ✉️  Legitimate emails: 15

------------------------------------------------------------
📦 Backing up current model...
✅ Backed up model to: models/backups/model_backup_20251019_020015.pkl

------------------------------------------------------------
🎓 Training new model...
   Training samples: 30
Training on 30 emails (15 phishing, 15 legitimate)
Training completed! Accuracy: 96.7%

💾 Saving new model...

============================================================
✅ MODEL RETRAINING COMPLETED SUCCESSFULLY!
============================================================

📁 Model saved to: models/simple_ml_model.pkl
📅 Training date: 2025-10-19 02:00:15
📊 Training samples: 30

⚠️  NOTE: Restart the backend to load the new model:
   python backend/app.py
```

### Log Files

Logs are saved to:
- `logs/retrain_service.log` - Main service log
- `logs/cron_retrain.log` - Cron job log
- System logs (journalctl, launchctl)

### View Logs

```bash
# Tail service log
tail -f logs/retrain_service.log

# Systemd logs (Linux)
sudo journalctl -u phishing-retrain -f

# LaunchAgent logs (macOS)
tail -f ~/Library/Logs/phishing-retrain.log

# Cron logs
tail -f logs/cron_retrain.log
```

---

## Troubleshooting

### Issue 1: "Insufficient data" Error

**Error:**
```
❌ Insufficient data: 3 emails (minimum 4 needed)
```

**Solution:**
- Upload more emails to the database
- Use `--min-emails 2` to lower threshold
- Use `--force` to try anyway (not recommended)

---

### Issue 2: "Unbalanced dataset" Warning

**Error:**
```
⚠️  Warning: Unbalanced dataset (need at least 2 of each class)
❌ Not enough phishing examples
```

**Solution:**
- Ensure you have at least 2 phishing AND 2 legitimate emails
- Check `user_confirmed_class` values in database
- Upload and label more diverse emails

---

### Issue 3: Schedule Not Running

**Check if service is running:**

```bash
# Systemd
sudo systemctl status phishing-retrain

# LaunchAgent
launchctl list | grep phishing

# Cron
crontab -l
```

**Check logs:**
```bash
# Look for errors in logs
tail -50 logs/retrain_service.log
```

**Common causes:**
- Wrong file paths in service/plist files
- Virtual environment not activated
- Permissions issues
- Service not enabled

---

### Issue 4: Model Not Loading After Retrain

**Symptom:**
Backend still uses old model after retraining.

**Solution:**
```bash
# Restart the backend
# Press Ctrl+C in backend terminal, then:
python backend/app.py

# Or if running as service:
sudo systemctl restart phishing-backend
```

**Note:** Backend loads model only on startup, not automatically.

---

### Issue 5: Database Connection Error

**Error:**
```
sqlalchemy.exc.OperationalError: connection failed
```

**Solution:**
```bash
# For PostgreSQL, provide DB URL:
python ml/auto_retrain.py \
    --db-url "postgresql://postgres:YOUR_PASSWORD@localhost/phishing_detector"

# For SQLite, no URL needed (default)
python ml/auto_retrain.py
```

---

## Best Practices

### 1. Start Small

```bash
# Test manually first
python ml/auto_retrain.py --force

# Then schedule daily
python ml/auto_retrain.py --schedule daily
```

### 2. Monitor Initially

- Check logs after first few retraining runs
- Verify model accuracy is improving
- Check that backend loads new model

### 3. Set Appropriate Thresholds

```bash
# Production: Higher threshold
python ml/auto_retrain.py --min-emails 50 --schedule weekly

# Development: Lower threshold
python ml/auto_retrain.py --min-emails 5 --schedule daily
```

### 4. Keep Backups

- Automatic backups saved to `models/backups/`
- Don't delete these!
- Can rollback if new model performs poorly

### 5. Restart Backend After Retraining

```bash
# Option 1: Manual
Ctrl+C in backend terminal
python backend/app.py

# Option 2: Automated (systemd)
sudo systemctl restart phishing-backend
```

---

## Performance Impact

| Aspect | Impact |
|--------|--------|
| **Training Time** | 5-10 seconds for <100 emails |
| **CPU Usage** | High during training, low otherwise |
| **Memory** | ~200MB during training |
| **Disk Space** | ~1MB per model backup |
| **Backend Downtime** | 0 (model loads on startup) |

---

## Summary

### For College Projects (Demo)

❌ **DON'T USE** automatic retraining:
- Fixed test dataset
- Manual training is fine
- Adds unnecessary complexity

### For Production Systems

✅ **DO USE** automatic retraining:
- Real user data
- Model improves over time
- Schedule weekly/daily

### Quick Command Reference

```bash
# One-time retrain
python ml/auto_retrain.py --force

# Daily at 2 AM
python ml/auto_retrain.py --schedule daily --time 02:00

# Check retrain status
tail -f logs/retrain_service.log

# Restart backend
python backend/app.py
```

---

## Related Documentation

- [ML_TRAINING_FAQ.md](ML_TRAINING_FAQ.md) - FAQ about training
- [ML_QUICK_START.md](ML_QUICK_START.md) - Initial model training
- [ML_EXPLAINED_SIMPLE.md](ML_EXPLAINED_SIMPLE.md) - How ML works

---

*Last Updated: 2025-10-19*
