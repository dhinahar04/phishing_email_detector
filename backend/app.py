"""
Phishing Email Detection System - Backend API
Flask application for email upload, analysis, and dashboard
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
from datetime import datetime, timedelta
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Database, Email, IOC, AnalysisLog, MLPrediction
from backend.utils.email_parser import EmailParser
from backend.utils.ioc_extractor import IOCExtractor

# Try to load ML model
try:
    from ml.phishing_ml_model import SimplePhishingML
    ml_model = SimplePhishingML()
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'simple_ml_model.pkl')

    if os.path.exists(model_path):
        ml_model.load_model(model_path)
        ml_model_available = True

        # Get model file info
        import os.path as path
        model_size = path.getsize(model_path) / (1024 * 1024)  # Size in MB
        model_time = datetime.fromtimestamp(path.getmtime(model_path))

        print("\n" + "="*60)
        print("🤖 ML MODEL LOADED")
        print("="*60)
        print(f"✅ Model file: {model_path}")
        print(f"📊 Model size: {model_size:.2f} MB")
        print(f"📅 Trained on: {model_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔖 Version: {ml_model.model_version}")
        print(f"💡 Using ML predictions for uploaded emails")
        print("="*60 + "\n")
    else:
        ml_model_available = False
        print("\n" + "="*60)
        print("⚠️  ML MODEL NOT FOUND")
        print("="*60)
        print(f"❌ Model not found at: {model_path}")
        print(f"📝 To train the model, run:")
        print(f"   python ml/phishing_ml_model.py")
        print(f"")
        print(f"💡 Currently using rule-based detection")
        print("="*60 + "\n")

except Exception as e:
    ml_model_available = False
    print("\n" + "="*60)
    print("⚠️  ML MODEL LOAD ERROR")
    print("="*60)
    print(f"❌ Error: {e}")
    print(f"📝 To train the model, run:")
    print(f"   python ml/phishing_ml_model.py")
    print(f"")
    print(f"💡 Currently using rule-based detection")
    print("="*60 + "\n")

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'uploads')
ALLOWED_EXTENSIONS = {'eml', 'txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize database with PostgreSQL
# Update with your PostgreSQL credentials
db = Database(db_url='postgresql://postgres:password@localhost/phishing_detector')
email_parser = EmailParser()
ioc_extractor = IOCExtractor()

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_phishing_simple(email_data, iocs):
    """
    Simple rule-based phishing detection
    Returns True if email is likely phishing
    """
    phishing_score = 0

    # Check for urgency words
    urgency_words = ['urgent', 'immediately', 'action required', 'verify', 'suspend',
                     'limited time', 'act now', 'expires', 'warning']

    subject = email_data.get('subject', '').lower()
    body = email_data.get('body', '').lower()
    combined_text = subject + ' ' + body

    # Score based on urgency words
    urgency_count = sum(1 for word in urgency_words if word in combined_text)
    if urgency_count >= 3:
        phishing_score += 30
    elif urgency_count >= 1:
        phishing_score += 15

    # Check for suspicious keywords
    suspicious_keywords = ['password', 'credit card', 'social security', 'bank account',
                          'verify account', 'click here', 'winner', 'prize', 'lottery',
                          'inheritance', 'suspended', 'confirm']

    suspicious_count = sum(1 for keyword in suspicious_keywords if keyword in combined_text)
    if suspicious_count >= 3:
        phishing_score += 25
    elif suspicious_count >= 1:
        phishing_score += 10

    # Check for suspicious domains in sender
    sender = email_data.get('sender', '').lower()
    suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.click']
    if any(tld in sender for tld in suspicious_tlds):
        phishing_score += 35

    # Check IOCs
    ioc_score = 0
    for ioc in iocs:
        if ioc['ioc_type'] in ['md5', 'sha1', 'sha256']:
            ioc_score += 10
        if ioc['severity'] == 'high':
            ioc_score += 15
        elif ioc['severity'] == 'medium':
            ioc_score += 8

    phishing_score += min(ioc_score, 40)  # Cap IOC contribution

    # Check for excessive links
    link_count = body.count('http://') + body.count('https://')
    if link_count > 5:
        phishing_score += 15
    elif link_count > 2:
        phishing_score += 5

    # Check for IP addresses in URLs
    ip_in_urls = any(ioc['ioc_type'] == 'ipv4' and 'http' in combined_text for ioc in iocs)
    if ip_in_urls:
        phishing_score += 20

    return phishing_score >= 50

def calculate_confidence_score(email_data, iocs):
    """
    Calculate confidence score (0-100) for phishing detection
    """
    score = 0

    # Urgency words
    urgency_words = ['urgent', 'immediately', 'action required', 'verify', 'suspend',
                     'limited time', 'act now', 'expires', 'warning']

    subject = email_data.get('subject', '').lower()
    body = email_data.get('body', '').lower()
    combined_text = subject + ' ' + body

    urgency_count = sum(1 for word in urgency_words if word in combined_text)
    score += min(urgency_count * 8, 25)

    # Suspicious keywords
    suspicious_keywords = ['password', 'credit card', 'social security', 'bank account',
                          'verify account', 'click here', 'winner', 'prize', 'lottery']

    suspicious_count = sum(1 for keyword in suspicious_keywords if keyword in combined_text)
    score += min(suspicious_count * 7, 20)

    # Suspicious sender domain
    sender = email_data.get('sender', '').lower()
    suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.click']
    if any(tld in sender for tld in suspicious_tlds):
        score += 20

    # IOC analysis
    high_severity_iocs = sum(1 for ioc in iocs if ioc['severity'] == 'high')
    medium_severity_iocs = sum(1 for ioc in iocs if ioc['severity'] == 'medium')

    score += min(high_severity_iocs * 10, 20)
    score += min(medium_severity_iocs * 5, 15)

    return min(score, 100)

def get_risk_level(is_phishing, confidence_score):
    """
    Determine risk level based on phishing detection and confidence
    """
    if is_phishing:
        if confidence_score >= 80:
            return 'Critical'
        elif confidence_score >= 60:
            return 'High'
        else:
            return 'Medium'
    else:
        if confidence_score >= 40:
            return 'Low'
        else:
            return 'Safe'

@app.route('/api/upload', methods=['POST'])
def upload_email():
    """
    Upload email file endpoint
    Accepts .eml and .txt files
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only .eml and .txt files are allowed'}), 400

    try:
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")

        # Save file
        file.save(file_path)

        # Parse email
        email_data = email_parser.parse_email_file(file_path)

        # Create database session
        session = db.get_session()

        # Store email in database
        email_record = Email(
            filename=filename,
            file_path=file_path,
            sender=email_data.get('sender', ''),
            subject=email_data.get('subject', ''),
            body=email_data.get('body', ''),
            status='analyzing'
        )
        session.add(email_record)
        session.commit()
        session.refresh(email_record)

        email_id = email_record.id

        # Create analysis log
        analysis_log = AnalysisLog(
            email_id=email_id,
            status='started'
        )
        session.add(analysis_log)
        session.commit()

        # Extract IOCs
        extracted_iocs = ioc_extractor.extract_from_email(email_data)

        # Store IOCs in database
        for ioc in extracted_iocs:
            ioc_record = IOC(
                email_id=email_id,
                ioc_type=ioc['ioc_type'],
                ioc_value=ioc['ioc_value'],
                severity=ioc['severity']
            )
            session.add(ioc_record)

        # Phishing detection - Try ML model first, fallback to rule-based
        if ml_model_available:
            try:
                # Use ML model for prediction
                ml_prediction_result, ml_probabilities = ml_model.predict(email_data)
                is_phishing_ml = bool(ml_prediction_result == 1)
                confidence_ml = float(ml_probabilities[1] * 100)  # Probability of phishing class

                # Also run rule-based for comparison
                is_phishing_rule = detect_phishing_simple(email_data, extracted_iocs)
                confidence_rule = calculate_confidence_score(email_data, extracted_iocs)

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

                print(f"ML Prediction: {is_phishing_ml} ({confidence_ml:.1f}%), Rule-based: {is_phishing_rule} ({confidence_rule:.1f}%)")

            except Exception as e:
                print(f"ML prediction failed: {e}, using rule-based")
                # Fallback to rule-based
                is_phishing = detect_phishing_simple(email_data, extracted_iocs)
                confidence_score = calculate_confidence_score(email_data, extracted_iocs)

                ml_prediction = MLPrediction(
                    email_id=email_id,
                    predicted_class='phishing' if is_phishing else 'legitimate',
                    probability=confidence_score / 100.0,
                    model_version='rule-based-v1.0'
                )
        else:
            # Use rule-based detection
            is_phishing = detect_phishing_simple(email_data, extracted_iocs)
            confidence_score = calculate_confidence_score(email_data, extracted_iocs)

            ml_prediction = MLPrediction(
                email_id=email_id,
                predicted_class='phishing' if is_phishing else 'legitimate',
                probability=confidence_score / 100.0,
                model_version='rule-based-v1.0'
            )

        # Update email record with detection results
        email_record.is_phishing = is_phishing
        email_record.confidence_score = confidence_score

        # Save prediction to database
        session.add(ml_prediction)

        # Update analysis log
        analysis_log.analysis_end = datetime.utcnow()
        analysis_log.status = 'completed'

        # Update email status
        email_record.status = 'completed'

        session.commit()

        # Prepare IOC breakdown by type
        ioc_breakdown = {}
        severity_breakdown = {'low': 0, 'medium': 0, 'high': 0}

        for ioc in extracted_iocs:
            ioc_type = ioc['ioc_type']
            severity = ioc['severity']

            if ioc_type not in ioc_breakdown:
                ioc_breakdown[ioc_type] = []
            ioc_breakdown[ioc_type].append({
                'value': ioc['ioc_value'],
                'severity': severity
            })

            severity_breakdown[severity] += 1

        session.close()

        return jsonify({
            'success': True,
            'message': 'Email uploaded and analyzed successfully',
            'email_id': email_id,
            'filename': filename,
            'sender': email_data.get('sender', ''),
            'subject': email_data.get('subject', ''),
            'analysis': {
                'is_phishing': is_phishing,
                'confidence_score': round(confidence_score, 2),
                'total_iocs': len(extracted_iocs),
                'ioc_breakdown': ioc_breakdown,
                'severity_breakdown': severity_breakdown,
                'risk_level': get_risk_level(is_phishing, confidence_score)
            }
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<int:email_id>', methods=['GET'])
def get_status(email_id):
    """
    Get analysis status for a specific email
    """
    try:
        session = db.get_session()
        email_record = session.query(Email).filter_by(id=email_id).first()

        if not email_record:
            session.close()
            return jsonify({'error': 'Email not found'}), 404

        # Get IOC count
        ioc_count = session.query(IOC).filter_by(email_id=email_id).count()

        result = {
            'email_id': email_record.id,
            'filename': email_record.filename,
            'upload_date': email_record.upload_date.isoformat(),
            'status': email_record.status,
            'is_phishing': email_record.is_phishing,
            'confidence_score': email_record.confidence_score,
            'ioc_count': ioc_count
        }

        session.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/emails', methods=['GET'])
def get_all_emails():
    """
    Get list of all uploaded emails
    """
    try:
        session = db.get_session()
        emails = session.query(Email).order_by(Email.upload_date.desc()).all()

        result = []
        for email in emails:
            ioc_count = session.query(IOC).filter_by(email_id=email.id).count()
            result.append({
                'id': email.id,
                'filename': email.filename,
                'upload_date': email.upload_date.isoformat(),
                'status': email.status,
                'sender': email.sender,
                'subject': email.subject,
                'is_phishing': email.is_phishing,
                'confidence_score': email.confidence_score,
                'ioc_count': ioc_count
            })

        session.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/summary', methods=['GET'])
def get_summary_metrics():
    """
    Get overall summary metrics for dashboard
    """
    try:
        session = db.get_session()

        # Total emails analyzed
        total_emails = session.query(Email).count()

        # Total IOCs extracted
        total_iocs = session.query(IOC).count()

        # Phishing emails detected
        phishing_count = session.query(Email).filter_by(is_phishing=True).count()

        # Emails by status
        pending = session.query(Email).filter_by(status='pending').count()
        analyzing = session.query(Email).filter_by(status='analyzing').count()
        completed = session.query(Email).filter_by(status='completed').count()

        result = {
            'total_emails': total_emails,
            'total_iocs': total_iocs,
            'phishing_detected': phishing_count,
            'legitimate_emails': total_emails - phishing_count,
            'status_breakdown': {
                'pending': pending,
                'analyzing': analyzing,
                'completed': completed
            }
        }

        session.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/timeline', methods=['GET'])
def get_timeline_metrics():
    """
    Get time-series data for charts (last 30 days)
    """
    try:
        session = db.get_session()

        # Get emails from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        emails = session.query(Email).filter(
            Email.upload_date >= thirty_days_ago
        ).order_by(Email.upload_date).all()

        # Group by date
        timeline = {}
        for email in emails:
            date_key = email.upload_date.strftime('%Y-%m-%d')
            if date_key not in timeline:
                timeline[date_key] = {
                    'date': date_key,
                    'total': 0,
                    'phishing': 0,
                    'legitimate': 0
                }
            timeline[date_key]['total'] += 1
            if email.is_phishing:
                timeline[date_key]['phishing'] += 1
            else:
                timeline[date_key]['legitimate'] += 1

        result = list(timeline.values())

        session.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/ioc-distribution', methods=['GET'])
def get_ioc_distribution():
    """
    Get IOC type distribution for pie chart
    """
    try:
        session = db.get_session()

        # Count by IOC type
        from sqlalchemy import func
        ioc_counts = session.query(
            IOC.ioc_type,
            func.count(IOC.id).label('count')
        ).group_by(IOC.ioc_type).all()

        result = [
            {'type': ioc_type, 'count': count}
            for ioc_type, count in ioc_counts
        ]

        session.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/iocs', methods=['GET'])
def get_iocs():
    """
    Get all IOCs with filtering options
    Query parameters:
    - type: Filter by IOC type
    - search: Search in IOC values
    - email_id: Filter by email ID
    - page: Page number (default 1)
    - per_page: Items per page (default 50)
    """
    try:
        session = db.get_session()

        # Get query parameters
        ioc_type = request.args.get('type')
        search = request.args.get('search')
        email_id = request.args.get('email_id')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))

        # Build query
        query = session.query(IOC)

        if ioc_type:
            query = query.filter(IOC.ioc_type == ioc_type)
        if search:
            query = query.filter(IOC.ioc_value.ilike(f'%{search}%'))
        if email_id:
            query = query.filter(IOC.email_id == int(email_id))

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * per_page
        iocs = query.order_by(IOC.detection_date.desc()).offset(offset).limit(per_page).all()

        result = {
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
            'items': [
                {
                    'id': ioc.id,
                    'email_id': ioc.email_id,
                    'type': ioc.ioc_type,
                    'value': ioc.ioc_value,
                    'severity': ioc.severity,
                    'detection_date': ioc.detection_date.isoformat()
                }
                for ioc in iocs
            ]
        }

        session.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/iocs/<int:ioc_id>', methods=['GET'])
def get_ioc_details(ioc_id):
    """
    Get details for a specific IOC
    """
    try:
        session = db.get_session()
        ioc = session.query(IOC).filter_by(id=ioc_id).first()

        if not ioc:
            session.close()
            return jsonify({'error': 'IOC not found'}), 404

        # Get associated email
        email = session.query(Email).filter_by(id=ioc.email_id).first()

        result = {
            'id': ioc.id,
            'type': ioc.ioc_type,
            'value': ioc.ioc_value,
            'severity': ioc.severity,
            'detection_date': ioc.detection_date.isoformat(),
            'email': {
                'id': email.id,
                'filename': email.filename,
                'sender': email.sender,
                'subject': email.subject
            } if email else None
        }

        session.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Create tables if they don't exist
    db.create_tables()
    app.run(debug=True, host='0.0.0.0', port=5001)
