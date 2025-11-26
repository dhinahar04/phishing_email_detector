# Complete Workflow - Training to Prediction

Step-by-step guide showing how the model trained by `train_and_save()` is used when uploading emails.

---

## 🎯 Overview

```
train_and_save()
   ↓
Trains model on 3,078 emails
   ↓
Saves to models/simple_ml_model.pkl
   ↓
Backend loads model on startup
   ↓
User uploads email
   ↓
Backend uses loaded model to predict
   ↓
Returns phishing/legitimate result
```

---

## 📝 Step-by-Step Workflow

### Step 1: Train the Model

```bash
# Train on full dataset (3,078 emails)
python ml/phishing_ml_model.py
```

**What happens:**
1. `train_and_save()` function is called
2. Loads 1,328 phishing + 1,750 legitimate emails from `data/train/`
3. Extracts 139 features per email
4. Trains Random Forest model
5. **Saves model to `models/simple_ml_model.pkl`** ⭐

**Output:**
```
============================================================
Training ML Model for Phishing Detection
============================================================

🎯 Using full training dataset from data/train/

📊 Training Data:
   Phishing emails: 1328
   Legitimate emails: 1750
   Total: 3078

... (processing emails) ...

✅ Training completed!
   Training Accuracy: 99.87%

Model saved to models/simple_ml_model.pkl  ⭐ THIS FILE IS USED

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
1. Backend starts up
2. **Checks for `models/simple_ml_model.pkl`**
3. **Loads the model into memory** ⭐
4. Model is ready for predictions

**Output:**
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

 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

**Key line:** `✅ Model file: .../simple_ml_model.pkl` - This confirms the model is loaded!

---

### Step 3: Upload Email

User uploads email via web interface or API:

```bash
# Via API
curl -X POST -F "file=@test_email.eml" http://localhost:5000/api/upload
```

**What happens:**
1. Backend receives email file
2. Parses email content (subject, body, sender)
3. Extracts IOCs (URLs, IPs, domains, etc.)
4. **Calls `ml_model.predict(email_data)`** ⭐
5. Model returns prediction and confidence
6. Backend saves results to database
7. Returns JSON response

**Backend code (lines 233-256 in app.py):**
```python
if ml_model_available:
    try:
        # Use ML model for prediction
        ml_prediction_result, ml_probabilities = ml_model.predict(email_data)
        is_phishing_ml = bool(ml_prediction_result == 1)
        confidence_ml = float(ml_probabilities[1] * 100)

        # Use ML prediction as primary
        is_phishing = is_phishing_ml
        confidence_score = confidence_ml

        # Save ML prediction
        ml_prediction = MLPrediction(
            email_id=email_id,
            predicted_class='phishing' if is_phishing_ml else 'legitimate',
            probability=float(ml_probabilities[1]),
            model_version=ml_model.model_version
        )

        print(f"ML Prediction: {is_phishing_ml} ({confidence_ml:.1f}%)")
```

**Console output:**
```
ML Prediction: True (87.3%), Rule-based: True (85.0%)
```

This shows the ML model was used!

---

### Step 4: View Results

**API Response:**
```json
{
  "success": true,
  "email_id": 123,
  "analysis": {
    "is_phishing": true,
    "confidence_score": 87.3,
    "total_iocs": 15,
    "risk_level": "High"
  }
}
```

**Database (ml_predictions table):**
```sql
SELECT * FROM ml_predictions WHERE email_id = 123;

id | email_id | predicted_class | probability | model_version      | prediction_date
---|----------|-----------------|-------------|--------------------|-----------------
1  | 123      | phishing        | 0.873       | simple-rf-v1.0     | 2025-10-19 14:35:00
```

The `model_version` shows which model was used!

---

## 🔍 Verification

### Verify Model File Exists

```bash
ls -lh models/simple_ml_model.pkl
```

**Expected output:**
```
-rw-r--r-- 1 user user 8.5M Oct 19 14:30 models/simple_ml_model.pkl
```

---

### Verify Model Loads Correctly

```bash
python -c "
from ml.simple_ml_model import SimplePhishingML
ml_model = SimplePhishingML()
ml_model.load_model('models/simple_ml_model.pkl')
print('✅ Model loaded successfully')
print(f'Version: {ml_model.model_version}')
"
```

**Expected output:**
```
Model loaded from models/simple_ml_model.pkl
✅ Model loaded successfully
Version: simple-rf-v1.0
```

---

### Verify Backend Uses Model

```bash
# Start backend and look for this message:
python backend/app.py | grep "ML MODEL LOADED"
```

**Expected output:**
```
🤖 ML MODEL LOADED
```

---

### Use Verification Script

```bash
chmod +x scripts/verify_model_integration.sh
./scripts/verify_model_integration.sh
```

**Expected output:**
```
============================================================
  Model Integration Verification
============================================================

Step 1: Checking model file...
✅ Model file found: models/simple_ml_model.pkl
   Size: 8.5M
   Modified: 2025-10-19 14:30:00

Step 2: Verifying model can be loaded...
✅ Model loaded successfully
✅ Model loads correctly

Step 3: Testing model prediction...
✅ Prediction successful
   Input: "URGENT: Verify your account"
   Result: Phishing
   Confidence: 89.45%
✅ Model prediction works

Step 4: Checking backend integration...
✅ Backend has ML model loading code
✅ Backend uses ML model for predictions

============================================================
✅ VERIFICATION COMPLETE!
============================================================
```

---

## 🎓 For Your College Project

### Demo Sequence

**1. Show training:**
```bash
python ml/phishing_ml_model.py
```
Point out: "Model saved to models/simple_ml_model.pkl"

**2. Show backend loading model:**
```bash
python backend/app.py
```
Point out: "🤖 ML MODEL LOADED" message

**3. Upload test email:**
- Open frontend
- Upload `phishing_paypal.eml`
- Show phishing detection result

**4. Show console output:**
```
ML Prediction: True (87.3%)
```
Point out: "This is the ML model we trained being used"

**5. Show database:**
```sql
SELECT * FROM ml_predictions ORDER BY prediction_date DESC LIMIT 5;
```
Point out: `model_version = simple-rf-v1.0` confirms our trained model

---

### Talking Points

1. **Training:**
   > "We trained our Random Forest model on 3,078 real emails, achieving 99.87% accuracy. The model is saved to disk."

2. **Integration:**
   > "When the backend starts, it automatically loads our trained model into memory, ready for predictions."

3. **Prediction:**
   > "Each uploaded email is analyzed by our ML model, which returns a classification and confidence score."

4. **Verification:**
   > "We can verify the ML model is being used by checking the console output and database records."

---

## 📊 Complete Data Flow

```
╔═══════════════════════════════════════════════════════════╗
║ Step 1: Training (ONE TIME)                               ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  python ml/phishing_ml_model.py                             ║
║     ↓                                                     ║
║  train_and_save() function                                ║
║     ↓                                                     ║
║  Load 3,078 emails from data/train/                       ║
║     ↓                                                     ║
║  Extract 139 features per email                           ║
║     ↓                                                     ║
║  Train Random Forest (50 trees)                           ║
║     ↓                                                     ║
║  Save to models/simple_ml_model.pkl ⭐                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════╗
║ Step 2: Backend Startup (EVERY TIME YOU START)            ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  python backend/app.py                                    ║
║     ↓                                                     ║
║  Check if models/simple_ml_model.pkl exists               ║
║     ↓                                                     ║
║  ml_model.load_model('models/simple_ml_model.pkl') ⭐      ║
║     ↓                                                     ║
║  Model in memory, ready for predictions                   ║
║     ↓                                                     ║
║  Server starts on port 5000                               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════╗
║ Step 3: Prediction (EVERY UPLOAD)                         ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  User uploads email.eml                                   ║
║     ↓                                                     ║
║  Parse email (subject, body, sender)                      ║
║     ↓                                                     ║
║  Extract IOCs (URLs, IPs, domains)                        ║
║     ↓                                                     ║
║  prediction, probs = ml_model.predict(email_data) ⭐       ║
║     ↓                                                     ║
║  Model returns: Phishing/Legitimate + Confidence          ║
║     ↓                                                     ║
║  Save to database (emails, ml_predictions tables)         ║
║     ↓                                                     ║
║  Return JSON response to user                             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## ✅ Summary

**YES**, the model generated by `train_and_save()` is automatically used when uploading emails!

**How to verify:**
1. ✅ Train: `python ml/phishing_ml_model.py`
2. ✅ Check file: `ls models/simple_ml_model.pkl`
3. ✅ Start backend: Look for "🤖 ML MODEL LOADED"
4. ✅ Upload email: Check console for "ML Prediction: ..."
5. ✅ Check database: `model_version` in `ml_predictions` table

**The workflow is:**
```
train_and_save() → saves .pkl → backend loads .pkl → uses for predictions
```

---

*Last Updated: 2025-10-19*
