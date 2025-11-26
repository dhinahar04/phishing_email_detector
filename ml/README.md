# Machine Learning Module

ML components for phishing email detection with automatic retraining support.

## Files

### Core ML Files

**phishing_ml_model.py**
- Main ML model (Random Forest classifier)
- Trains on test emails or custom data
- Saves/loads models from disk
- Used by backend for predictions

**feature_extraction.py**
- Extracts 30+ numerical features from emails
- Text statistics, URL analysis, keyword detection
- Used by training and prediction

**train_model.py**
- Advanced training framework
- For larger datasets
- Cross-validation, multiple models
- Production-ready training

**auto_retrain.py** ⭐ **NEW!**
- Automatic model retraining
- Scheduled retraining (hourly/daily/weekly)
- Uses database emails for training
- Backs up old models

## Quick Start

### Initial Training (One-Time)

```bash
# Train on test emails
python ml/phishing_ml_model.py
```

**Output:**
```
Training on 8 emails (4 phishing, 4 legitimate)
Training completed! Accuracy: 100.0%
Model saved to models/simple_ml_model.pkl
```

### Automatic Retraining (Production)

```bash
# Check if retraining needed
python ml/auto_retrain.py

# Schedule daily retraining at 2 AM
python ml/auto_retrain.py --schedule daily --time 02:00

# Force retrain even if not enough data
python ml/auto_retrain.py --force
```

## Usage Patterns

### Pattern 1: College Project (Fixed Test Data)

```bash
# Train once
python ml/phishing_ml_model.py

# Start backend (loads model)
python backend/app.py

# Upload emails → Predictions use trained model
# NO retraining needed
```

### Pattern 2: Production (Growing Dataset)

```bash
# Initial training
python ml/phishing_ml_model.py

# Start backend
python backend/app.py

# Start retraining scheduler (separate terminal)
python ml/auto_retrain.py --schedule daily

# Users upload emails + provide feedback
# Model retrains automatically
# Restart backend to load new model
```

### Pattern 3: Manual Retraining

```bash
# Upload many emails via web interface

# Manually retrain when ready
python ml/auto_retrain.py --force

# Restart backend
python backend/app.py
```

## How Models Are Used

### Training Flow

```
1. phishing_ml_model.py
   ↓
2. Reads test emails or database
   ↓
3. Extracts features (feature_extraction.py)
   ↓
4. Trains Random Forest
   ↓
5. Saves to models/simple_ml_model.pkl
```

### Prediction Flow

```
1. User uploads email to backend
   ↓
2. Backend parses email
   ↓
3. Loads saved model (simple_ml_model.pkl)
   ↓
4. Extracts features (feature_extraction.py)
   ↓
5. Model predicts: phishing or legitimate
   ↓
6. Returns confidence score
```

### Automatic Retraining Flow

```
1. Scheduler triggers (daily/weekly)
   ↓
2. auto_retrain.py checks database
   ↓
3. If enough new data: retrain
   ├─ Backs up old model
   ├─ Trains on all database emails
   └─ Saves new model
   ↓
4. Backend restart loads new model
   ↓
5. Improved predictions!
```

## Command Reference

### Initial Training

```bash
# Train on test emails
python ml/phishing_ml_model.py

# Advanced training (larger datasets)
python ml/train_model.py
```

### Automatic Retraining

```bash
# One-time check and retrain
python ml/auto_retrain.py

# Force retraining
python ml/auto_retrain.py --force

# Schedule daily at 2 AM
python ml/auto_retrain.py --schedule daily --time 02:00

# Schedule hourly
python ml/auto_retrain.py --schedule hourly

# Schedule weekly (Monday at 3 AM)
python ml/auto_retrain.py --schedule weekly --time 03:00

# Set minimum emails threshold
python ml/auto_retrain.py --min-emails 20

# With PostgreSQL
python ml/auto_retrain.py --db-url "postgresql://postgres:password@localhost/phishing_detector"
```

### Testing

```bash
# Test feature extraction
python -c "from ml.feature_extraction import FeatureExtractor; \
           fe = FeatureExtractor(); \
           print(fe.extract_text_features('Test email body'))"

# Test model loading
python -c "from ml.simple_ml_model import SimplePhishingML; \
           ml = SimplePhishingML(); \
           ml.load_model('models/simple_ml_model.pkl'); \
           print('Model loaded successfully')"
```

## Configuration

### Retraining Parameters

Edit in `auto_retrain.py` or pass as arguments:

- `min_new_emails` - Minimum emails needed (default: 10)
- `schedule` - Retraining frequency (hourly/daily/weekly)
- `time` - Time to run for daily/weekly (default: 02:00)

### Model Parameters

Edit in `phishing_ml_model.py`:

```python
# TF-IDF features
TfidfVectorizer(max_features=100, stop_words='english')

# Random Forest
RandomForestClassifier(
    n_estimators=50,    # Number of trees
    max_depth=10,       # Tree depth
    random_state=42     # Reproducibility
)
```

## File Structure

```
ml/
├── phishing_ml_model.py      # Main ML model
├── feature_extraction.py   # Feature engineering
├── train_model.py          # Advanced training
├── auto_retrain.py         # Automatic retraining ⭐ NEW!
└── README.md               # This file

models/
├── simple_ml_model.pkl     # Trained model
└── backups/                # Model backups
    └── model_backup_*.pkl

logs/
└── retrain_service.log     # Retraining logs
```

## Model Files

### simple_ml_model.pkl

Contains:
- Random Forest model (50 trees)
- TF-IDF vectorizer (100 features)
- Model version string

**Size:** ~500KB - 2MB depending on training data

**Location:** `models/simple_ml_model.pkl`

**Backed up to:** `models/backups/` before retraining

## Performance

| Metric | Value |
|--------|-------|
| **Training Time** | 5-10 seconds (8-100 emails) |
| **Prediction Time** | <0.1 seconds per email |
| **Model Size** | ~500KB - 2MB |
| **Features** | 130 total (100 TF-IDF + 30 custom) |
| **Accuracy** | 95-100% on test data |

## Troubleshooting

### "Model not found" Error

```bash
# Train the model first
python ml/phishing_ml_model.py

# Verify file exists
ls -la models/simple_ml_model.pkl
```

### "Insufficient data" Error

```bash
# Need at least 4 emails (2 phishing, 2 legitimate)
# Upload more emails or use --force

python ml/auto_retrain.py --force --min-emails 2
```

### "Module not found" Error

```bash
# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install scikit-learn numpy pandas joblib schedule
```

### Model Not Improving

- Check if you have diverse training data
- Verify user feedback is being recorded
- Ensure new emails are different from training set
- Review logs for training errors

## Best Practices

### For Development

1. Train once manually: `python ml/phishing_ml_model.py`
2. Don't use auto-retraining
3. Test with fixed dataset

### For Production

1. Initial training: `python ml/phishing_ml_model.py`
2. Enable auto-retraining: `python ml/auto_retrain.py --schedule daily`
3. Monitor logs regularly
4. Review model accuracy weekly
5. Keep model backups

### For College Projects

1. Train once with test data
2. Explain manual training in presentation
3. Mention auto-retraining as "future enhancement"
4. Demo with fixed test emails

## Documentation

- [AUTO_RETRAIN_GUIDE.md](../docs/ml/AUTO_RETRAIN_GUIDE.md) - Complete retraining guide
- [ML_TRAINING_FAQ.md](../docs/ml/ML_TRAINING_FAQ.md) - Training FAQ
- [ML_QUICK_START.md](../docs/ml/ML_QUICK_START.md) - Quick start guide
- [ML_EXPLAINED_SIMPLE.md](../docs/ml/ML_EXPLAINED_SIMPLE.md) - ML concepts explained

## Examples

### Example 1: Train and Predict

```python
from ml.simple_ml_model import SimplePhishingML

# Train
model = SimplePhishingML()
model.train_on_test_emails()
model.save_model('models/simple_ml_model.pkl')

# Predict
email_data = {
    'subject': 'Urgent: Verify your account',
    'body': 'Click here to verify...',
    'sender': 'phishing@badsite.tk'
}

prediction, probabilities = model.predict(email_data)
print(f"Phishing: {prediction == 1}")
print(f"Confidence: {probabilities[1] * 100:.1f}%")
```

### Example 2: Schedule Retraining

```python
from ml.auto_retrain import AutoRetrainer

# Create retrainer
retrainer = AutoRetrainer(min_new_emails=10)

# Schedule daily at 2 AM
retrainer.schedule_retraining(interval='daily', time_str='02:00')
```

### Example 3: Custom Training Data

```python
from ml.simple_ml_model import SimplePhishingML

# Prepare data
emails = [
    {'subject': 'Phishing', 'body': '...'},
    {'subject': 'Legitimate', 'body': '...'},
]
labels = [1, 0]  # 1=phishing, 0=legitimate

# Train
model = SimplePhishingML()
model.train_on_custom_data(emails, labels)
model.save_model('models/custom_model.pkl')
```

---

*For detailed guides, see [docs/ml/](../docs/ml/)*
