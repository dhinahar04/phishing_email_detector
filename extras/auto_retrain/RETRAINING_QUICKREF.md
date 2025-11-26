# Automatic Retraining - Quick Reference

One-page reference for automatic ML model retraining.

---

## 🚀 Quick Commands

```bash
# Check if retraining needed
python ml/auto_retrain.py

# Force retrain now
python ml/auto_retrain.py --force

# Daily at 2 AM
python ml/auto_retrain.py --schedule daily --time 02:00

# Hourly checks
python ml/auto_retrain.py --schedule hourly

# Weekly (Monday 3 AM)
python ml/auto_retrain.py --schedule weekly --time 03:00
```

---

## 📋 When Does It Retrain?

✅ **Retrains when:**
- 10+ new emails since last training (adjustable)
- Scheduled time arrives
- Manual trigger with `--force`

❌ **Skips when:**
- <10 new emails
- <4 total emails in database
- <2 of each class (phishing/legitimate)

---

## 🔄 Complete Workflow

```bash
# 1. Initial setup (once)
pip install schedule
python ml/phishing_ml_model.py

# 2. Start backend
python backend/app.py

# 3. Start retraining scheduler (separate terminal)
python ml/auto_retrain.py --schedule daily

# 4. Users upload emails and provide feedback
# (Automatic - happens via web interface)

# 5. Model retrains automatically at scheduled time
# (Automatic - check logs)

# 6. Restart backend to load new model
Ctrl+C in backend terminal
python backend/app.py
```

---

## 🎛️ Configuration Options

| Option | Values | Default | Example |
|--------|--------|---------|---------|
| `--schedule` | hourly, daily, weekly | none | `daily` |
| `--time` | HH:MM | 02:00 | `03:30` |
| `--min-emails` | number | 10 | `20` |
| `--force` | flag | false | `--force` |

---

## 📁 Files Created

```
models/
├── simple_ml_model.pkl          # Active model
└── backups/
    └── model_backup_*.pkl       # Old models

logs/
└── retrain_service.log          # Retraining logs
```

---

## 🔍 Check Status

```bash
# View logs
tail -f logs/retrain_service.log

# Check if service running
ps aux | grep auto_retrain

# Systemd (Linux)
sudo systemctl status phishing-retrain

# LaunchAgent (macOS)
launchctl list | grep phishing
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Insufficient data" | Upload more emails or use `--force` |
| "Unbalanced dataset" | Need 2+ of each class |
| Schedule not running | Check service status, logs |
| New model not loading | Restart backend |
| Connection error | Check database URL |

---

## 📊 User Feedback API

```bash
# Confirm prediction correct
curl -X POST http://localhost:5000/api/feedback/123 \
  -H "Content-Type: application/json" \
  -d '{"is_correct": true, "actual_class": "phishing"}'

# Correct wrong prediction
curl -X POST http://localhost:5000/api/feedback/123 \
  -H "Content-Type: application/json" \
  -d '{"is_correct": false, "actual_class": "legitimate"}'

# View feedback stats
curl http://localhost:5000/api/feedback/stats
```

---

## 🎯 Use Cases

### College Project
❌ **Don't use** - Manual training is simpler

### Production
✅ **Use** - Model improves over time

### Development
⚠️ **Optional** - Test manually first

---

## ⏰ Recommended Schedules

| Situation | Schedule | Threshold |
|-----------|----------|-----------|
| **High traffic** | Hourly | 50 emails |
| **Normal traffic** | Daily | 20 emails |
| **Low traffic** | Weekly | 10 emails |
| **Development** | Manual | 5 emails |

---

## 🔐 Production Setup

### Linux (systemd)
```bash
sudo cp scripts/phishing-retrain.service /etc/systemd/system/
sudo systemctl enable phishing-retrain
sudo systemctl start phishing-retrain
```

### macOS (LaunchAgent)
```bash
cp scripts/com.phishing.retrain.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.phishing.retrain.plist
```

### Cron (Universal)
```bash
crontab -e
# Add: 0 2 * * * /path/to/phishing-detector/scripts/cron_retrain.sh
```

---

## 📚 Full Documentation

- [AUTO_RETRAIN_GUIDE.md](AUTO_RETRAIN_GUIDE.md) - Complete guide
- [ML_TRAINING_FAQ.md](ML_TRAINING_FAQ.md) - Training FAQ
- [ml/README.md](../../ml/README.md) - ML module overview

---

## 💡 Tips

1. **Test manually first**
   ```bash
   python ml/auto_retrain.py --force
   ```

2. **Monitor logs initially**
   ```bash
   tail -f logs/retrain_service.log
   ```

3. **Restart backend after retraining**
   ```bash
   Ctrl+C → python backend/app.py
   ```

4. **Keep model backups**
   - Check `models/backups/` directory
   - Don't delete old models

5. **Adjust threshold based on usage**
   ```bash
   # More emails = higher threshold
   python ml/auto_retrain.py --min-emails 50
   ```

---

*Quick reference card - For detailed info, see AUTO_RETRAIN_GUIDE.md*
