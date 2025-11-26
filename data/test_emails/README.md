# Test Email Samples

This directory contains test email samples for demonstrating the phishing detection system.

## Phishing Emails

### 1. phishing_paypal.eml
**Type:** PayPal phishing scam
**Characteristics:**
- Urgent subject line demanding immediate action
- Suspicious sender domain (.tk TLD)
- Multiple phishing indicators:
  - Requests for personal information (SSN, credit card, password)
  - IP address in URLs
  - Suspicious domains and shortened URLs
  - Threats of account suspension
  - Multiple urgency words
- Contains file hashes (MD5, SHA256)
- IP addresses: 185.220.101.45, 192.168.50.123

**Expected Result:** ⚠️ PHISHING - High confidence

---

### 2. phishing_bank.eml
**Type:** Banking fraud attempt
**Characteristics:**
- Security alert with fake login attempt
- Suspicious TLD (.xyz)
- IP addresses from suspicious locations
- Requests for sensitive banking information
- Urgency tactics (2-hour deadline)
- Multiple malicious links

**Expected Result:** ⚠️ PHISHING - High confidence

---

### 3. phishing_prize.eml
**Type:** Lottery/Prize scam
**Characteristics:**
- Excessive exclamation marks and urgency
- Promise of large sum of money ($5 million)
- Requests for processing fee (advance fee fraud)
- International phone numbers (Nigeria)
- Bitcoin payment request
- Suspicious .click TLD
- Multiple RED FLAGS

**Expected Result:** ⚠️ PHISHING - Critical risk

---

### 4. phishing_microsoft.eml
**Type:** Microsoft account phishing
**Characteristics:**
- Fake security alert
- Suspicious domain (.top TLD)
- IP addresses in URLs
- Account compromise scare tactics
- Shortened URL (tinyurl)
- 24-hour deadline threat

**Expected Result:** ⚠️ PHISHING - High confidence

---

## Legitimate Emails

### 1. legitimate_github.eml
**Type:** GitHub notification
**Characteristics:**
- Authentic GitHub.com domain
- Professional formatting
- Clear unsubscribe link
- No urgency tactics
- No requests for personal information
- Standard notification content

**Expected Result:** ✅ LEGITIMATE - Safe

---

### 2. legitimate_amazon.eml
**Type:** Order shipment notification
**Characteristics:**
- Official Amazon.com domain
- Standard shipping notification
- Tracking number provided
- No requests for payment or personal info
- Professional formatting
- Clear notification-only disclaimer

**Expected Result:** ✅ LEGITIMATE - Safe

---

### 3. legitimate_newsletter.eml
**Type:** Tech blog newsletter
**Characteristics:**
- Legitimate tech blog domain
- Educational content
- Clear unsubscribe option
- No personal information requests
- Professional formatting
- Standard marketing content

**Expected Result:** ✅ LEGITIMATE - Safe

---

### 4. legitimate_work.eml
**Type:** Internal work email
**Characteristics:**
- Company domain email
- Meeting invite and project update
- No external links to suspicious sites
- Professional business communication
- Standard work-related content

**Expected Result:** ✅ LEGITIMATE - Safe

---

## IOC Summary

### Phishing Emails Contain:
- **Suspicious TLDs:** .tk, .ml, .ga, .cf, .gq, .xyz, .top, .click
- **IP Addresses:** 185.220.101.45, 192.168.50.123, 203.45.67.89, 45.142.212.100, 103.224.182.245, 10.20.30.40
- **Suspicious Domains:** paypal-verify.tk, secure-banking.xyz, lottery-winner.click, microsoft-verify.top
- **File Hashes:** MD5, SHA1, SHA256 hashes
- **Shortened URLs:** bit.ly, tinyurl
- **Foreign Phone Numbers:** Nigeria, UK
- **Bitcoin Addresses**

### Legitimate Emails Contain:
- **Trusted Domains:** github.com, amazon.com, company domains
- **Standard Links:** Official website links only
- **No Suspicious TLDs**
- **No Personal Info Requests**

---

## Testing Instructions

1. **Upload Phishing Emails:**
   - Should show red alert with "PHISHING EMAIL DETECTED"
   - High confidence score (60-100%)
   - Risk level: High or Critical
   - Multiple IOCs extracted
   - Severity breakdown displayed

2. **Upload Legitimate Emails:**
   - Should show green alert with "Legitimate Email"
   - Lower confidence score (0-40%)
   - Risk level: Safe or Low
   - Few or no IOCs
   - Safe status indicated

## Demo Flow

For presentations, upload in this order:

1. **legitimate_amazon.eml** - Show safe email (baseline)
2. **phishing_paypal.eml** - Show obvious phishing
3. **phishing_prize.eml** - Show extreme phishing (lottery scam)
4. **legitimate_github.eml** - Show another safe email
5. **phishing_microsoft.eml** - Show sophisticated phishing
6. **legitimate_newsletter.eml** - Show marketing email (legitimate)

This demonstrates the system's ability to distinguish between phishing and legitimate emails across various scenarios.

---

## Notes for Development

- These emails are for testing purposes only
- Contains intentionally suspicious content
- Use for demonstration and validation
- Add more samples as needed for comprehensive testing
- All malicious URLs and IPs are examples (not real threats)
