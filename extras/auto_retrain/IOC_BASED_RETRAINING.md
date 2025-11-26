# IOC-Based Automatic Retraining

How the automatic retraining system uses extracted IOCs (Indicators of Compromise) to improve the ML model.

---

## 🎯 Overview

Instead of relying on user feedback, the system automatically retrains using:
1. **Email content** - Subject, body, sender
2. **Extracted IOCs** - URLs, IPs, domains, file hashes
3. **Automatic labels** - Phishing classification from rule-based/ML detection

This is **more practical** because:
- ✅ No user interaction required
- ✅ IOCs are extracted automatically
- ✅ Works immediately with uploaded emails
- ✅ Real indicators of malicious content

---

## 📊 What Are IOCs?

**IOCs (Indicators of Compromise)** are artifacts extracted from emails that indicate potential malicious activity:

| IOC Type | Example | Why It Matters |
|----------|---------|----------------|
| **IPv4** | 192.168.1.1 | Direct IP connections bypass DNS, suspicious |
| **URL** | http://evil.tk/phish | Links to malicious sites |
| **Domain** | badsite.tk | Suspicious domains (.tk, .xyz, etc.) |
| **Email** | scam@phisher.com | Contact addresses in phishing emails |
| **MD5/SHA256** | a1b2c3d... | File hashes of malicious attachments |

---

## 🔄 How It Works

### 1. Email Upload & Analysis

```
User uploads email
   ↓
Backend analyzes email
   ├─ Parses content
   ├─ Extracts IOCs automatically
   └─ Makes phishing prediction
   ↓
Saves to database:
   ├─ Email content
   ├─ IOCs (separate table)
   └─ Phishing classification
```

### 2. IOC Features Extracted

When retraining, the system adds **9 IOC-based features** to each email:

```python
'ioc_total_count': 15,        # Total IOCs found
'has_ipv4_ioc': True,         # Contains IP addresses?
'has_url_ioc': True,          # Contains URLs?
'has_email_ioc': True,        # Contains email addresses?
'has_hash_ioc': False,        # Contains file hashes?
'ipv4_ioc_count': 2,          # Number of IPs
'url_ioc_count': 8,           # Number of URLs
'email_ioc_count': 3,         # Number of emails
'domain_ioc_count': 5         # Number of domains
```

### 3. Training Data Preparation

```python
for email in database:
    # Get email content
    email_data = {
        'subject': email.subject,
        'body': email.body,
        'sender': email.sender
    }

    # Get IOCs from database
    iocs = get_iocs_for_email(email.id)

    # Add IOC features
    email_data['ioc_count'] = len(iocs)
    email_data['ipv4_count'] = count_by_type(iocs, 'ipv4')
    email_data['url_count'] = count_by_type(iocs, 'url')
    # ... more IOC features

    # Use automatic label
    label = 1 if email.is_phishing else 0

    training_data.append((email_data, label))
```

### 4. Model Training

```
Training Features = Text Features (100) + Custom Features (30) + IOC Features (9)
                  = 139 total features

Model learns patterns like:
- "High URL count + suspicious TLDs = likely phishing"
- "Many IPs + urgency words = high risk"
- "No IOCs + known sender = legitimate"
```

---

## 📈 IOC Statistics During Retraining

When retraining runs, you see IOC statistics:

```
📊 Preparing training data from 50 emails...
   📧 Phishing emails: 25
   ✉️  Legitimate emails: 25
   🔍 Total IOCs extracted: 347
   📊 Avg IOCs (phishing): 18.3
   📊 Avg IOCs (legitimate): 9.1
```

This shows:
- Phishing emails have **2x more IOCs** on average
- Model learns this pattern automatically
- No manual labeling required

---

## 🎓 Examples

### Example 1: Phishing Email with Many IOCs

**Email Content:**
```
Subject: URGENT! Account Suspended
From: security@badbank.tk
Body: Click http://192.168.1.100/verify to restore access...
```

**Extracted IOCs:**
- 1 suspicious domain (.tk)
- 1 URL
- 1 IPv4 address
- 1 email address

**IOC Features:**
```python
{
    'ioc_total_count': 4,
    'has_ipv4_ioc': True,    # Red flag!
    'has_url_ioc': True,
    'has_email_ioc': True,
    'ipv4_ioc_count': 1,
    'url_ioc_count': 1,
}
```

**ML learns:** "Emails with IPs in URLs + .tk domain = phishing"

---

### Example 2: Legitimate Email with Few IOCs

**Email Content:**
```
Subject: Your Amazon Order #12345
From: auto-confirm@amazon.com
Body: Your order has shipped. Track at amazon.com/orders
```

**Extracted IOCs:**
- 1 legitimate domain (amazon.com)
- 1 URL
- 1 email address

**IOC Features:**
```python
{
    'ioc_total_count': 3,
    'has_ipv4_ioc': False,    # Good sign
    'has_url_ioc': True,
    'has_email_ioc': True,
    'ipv4_ioc_count': 0,      # No direct IPs
    'url_ioc_count': 1,
}
```

**ML learns:** "Legitimate domains + no IPs + low IOC count = safe"

---

## 🚀 Retraining Process

### Step 1: Trigger Retraining

```bash
# Manual
python ml/auto_retrain.py --force

# Scheduled (daily at 2 AM)
python ml/auto_retrain.py --schedule daily --time 02:00
```

### Step 2: System Fetches Data

```
1. Get all emails from database
2. For each email:
   - Get email content
   - Get IOCs from iocs table
   - Build feature dictionary
3. Prepare labels (is_phishing column)
```

### Step 3: Model Trains

```
Training on 50 emails (25 phishing, 25 legitimate)
Features:
  - 100 TF-IDF (text patterns)
  - 30 custom (urgency, links, etc.)
  - 9 IOC-based (NEW!)
Training completed! Accuracy: 96.0%
```

### Step 4: Model Saved

```
✅ MODEL RETRAINING COMPLETED SUCCESSFULLY!
📁 Model saved to: models/simple_ml_model.pkl
📅 Training date: 2025-10-19 14:30:00
📊 Training samples: 50 (347 total IOCs)

⚠️  Restart backend to load new model
```

---

## 💡 Advantages of IOC-Based Approach

| Aspect | User Feedback | IOC-Based |
|--------|---------------|-----------|
| **User interaction** | Required | None |
| **Setup complexity** | High (UI, API, validation) | Low (automatic) |
| **Data quality** | Depends on users | Consistent |
| **Immediate use** | No (need feedback first) | Yes |
| **Scalability** | Limited by user engagement | Unlimited |
| **Accuracy** | Subjective | Objective |

---

## 📝 Database Schema

### emails table
```sql
- id
- subject
- body
- sender
- is_phishing  ← Used as label
```

### iocs table
```sql
- id
- email_id     ← Links to email
- ioc_type     ← 'ipv4', 'url', 'domain', etc.
- ioc_value    ← Actual IOC string
- severity     ← 'low', 'medium', 'high'
```

Retraining joins these tables to build training data.

---

## 🔍 Feature Comparison

**Before (Text Only):**
```
Features: 130 total
- Text length, word count
- URL count, link analysis
- Keywords, urgency words
- Sender analysis
```

**After (With IOCs):**
```
Features: 139 total
- All previous features
+ IOC total count
+ Has IPv4/URL/email/hash
+ Individual IOC type counts
```

**Result:** 7% more features, better accuracy on malicious indicators.

---

## 🎯 Practical Example

### Initial Training (8 test emails)

```bash
python ml/phishing_ml_model.py
```

**Output:**
```
Training on 8 emails (4 phishing, 4 legitimate)
Accuracy: 100%
Model saved!
```

### After 50 Real Emails Uploaded

```bash
python ml/auto_retrain.py --force
```

**Output:**
```
📊 Preparing training data from 50 emails...
   📧 Phishing emails: 27
   ✉️  Legitimate emails: 23
   🔍 Total IOCs extracted: 412
   📊 Avg IOCs (phishing): 19.7
   📊 Avg IOCs (legitimate): 8.4

🎓 Training new model...
Training on 50 emails (27 phishing, 23 legitimate)
Training completed! Accuracy: 94.0%

✅ MODEL RETRAINING COMPLETED SUCCESSFULLY!
```

### Result

Model now knows:
- Real-world phishing patterns
- Actual IOC distributions
- Better accuracy on new emails

---

## 🛠️ Implementation Details

### Code: IOC Feature Extraction

**File:** `ml/feature_extraction.py`

```python
def extract_ioc_features(self, email_data: Dict) -> Dict[str, float]:
    """Extract IOC-based features"""
    features = {
        'ioc_total_count': float(email_data.get('ioc_count', 0)),
        'has_ipv4_ioc': float(email_data.get('has_ipv4', False)),
        'has_url_ioc': float(email_data.get('has_url', False)),
        'has_email_ioc': float(email_data.get('has_email', False)),
        'has_hash_ioc': float(email_data.get('has_hash', False)),
        'ipv4_ioc_count': float(email_data.get('ipv4_count', 0)),
        'url_ioc_count': float(email_data.get('url_count', 0)),
        'email_ioc_count': float(email_data.get('email_count', 0)),
        'domain_ioc_count': float(email_data.get('domain_count', 0)),
    }
    return features
```

### Code: Preparing Training Data with IOCs

**File:** `ml/auto_retrain.py`

```python
def prepare_training_data(self):
    emails = database.get_all_emails()

    for email in emails:
        # Get IOCs from database
        iocs = database.get_iocs_for_email(email.id)

        # Count by type
        ioc_counts = count_by_type(iocs)

        # Build email data with IOC features
        email_data = {
            'subject': email.subject,
            'body': email.body,
            'ioc_count': len(iocs),
            'ipv4_count': ioc_counts.get('ipv4', 0),
            'url_count': ioc_counts.get('url', 0),
            # ... more IOC features
        }

        training_data.append(email_data)
        labels.append(1 if email.is_phishing else 0)

    return training_data, labels
```

---

## 📚 Summary

### What Changed

✅ **Removed:** User feedback requirement
✅ **Added:** Automatic IOC extraction and usage
✅ **Benefit:** Works immediately, no user interaction

### How to Use

```bash
# 1. Upload emails (IOCs extracted automatically)
curl -X POST -F "email=@test.eml" http://localhost:5000/api/upload

# 2. Retrain when ready (uses emails + IOCs)
python ml/auto_retrain.py --force

# 3. Restart backend
python backend/app.py

# 4. Better predictions!
```

### Key Points

1. IOCs are extracted automatically during email upload
2. Retraining uses both email content AND IOC patterns
3. No user feedback needed - fully automatic
4. Model learns real malicious indicators
5. Works for college projects and production

---

*Implementation: IOC-based automatic retraining*
*Date: 2025-10-19*
