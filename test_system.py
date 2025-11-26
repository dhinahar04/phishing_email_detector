"""
Test script for Phishing Email Detection System
Run this to verify all components are working correctly
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_email_parser():
    """Test email parsing functionality"""
    print("\n" + "="*60)
    print("Testing Email Parser")
    print("="*60)

    try:
        from backend.utils.email_parser import EmailParser

        parser = EmailParser()

        # Test with sample phishing email
        sample_file = 'data/sample_phishing.eml'
        if os.path.exists(sample_file):
            print(f"\nParsing: {sample_file}")
            email_data = parser.parse_email_file(sample_file)

            print(f"  ✓ Sender: {email_data.get('sender')}")
            print(f"  ✓ Subject: {email_data.get('subject')}")
            print(f"  ✓ Body length: {len(email_data.get('body', ''))} characters")
            print(f"  ✓ Attachments: {len(email_data.get('attachments', []))}")

            # Test feature extraction
            features = parser.extract_features(email_data)
            print(f"  ✓ Features extracted: {len(features)}")

            print("\n✓ Email Parser Test PASSED")
            return True
        else:
            print(f"  ✗ Sample file not found: {sample_file}")
            return False

    except Exception as e:
        print(f"\n✗ Email Parser Test FAILED: {e}")
        return False

def test_ioc_extractor():
    """Test IOC extraction functionality"""
    print("\n" + "="*60)
    print("Testing IOC Extractor")
    print("="*60)

    try:
        from backend.utils.ioc_extractor import IOCExtractor

        extractor = IOCExtractor()

        # Test text with various IOCs
        test_text = """
        Contact us at admin@example.com or visit http://example.com
        IP address: 192.168.1.1
        Suspicious link: http://malicious.tk/phishing
        MD5 hash: 5d41402abc4b2a76b9719d911017c592
        """

        print("\nExtracting IOCs from test text...")
        iocs = extractor.extract_iocs(test_text)

        for ioc_type, values in iocs.items():
            print(f"  ✓ {ioc_type}: {len(values)} found")
            for value in values:
                print(f"    - {value}")

        # Test with email data
        from backend.utils.email_parser import EmailParser
        parser = EmailParser()

        sample_file = 'data/sample_phishing.eml'
        if os.path.exists(sample_file):
            email_data = parser.parse_email_file(sample_file)
            ioc_list = extractor.extract_from_email(email_data)

            print(f"\n  ✓ Total IOCs from sample email: {len(ioc_list)}")
            for ioc in ioc_list[:5]:  # Show first 5
                print(f"    - {ioc['ioc_type']}: {ioc['ioc_value']} ({ioc['severity']})")

        print("\n✓ IOC Extractor Test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ IOC Extractor Test FAILED: {e}")
        return False

def test_feature_extraction():
    """Test ML feature extraction"""
    print("\n" + "="*60)
    print("Testing Feature Extraction")
    print("="*60)

    try:
        from ml.feature_extraction import FeatureExtractor
        from backend.utils.email_parser import EmailParser

        feature_extractor = FeatureExtractor()
        parser = EmailParser()

        # Test with sample email
        sample_file = 'data/sample_phishing.eml'
        if os.path.exists(sample_file):
            print(f"\nExtracting features from: {sample_file}")
            email_data = parser.parse_email_file(sample_file)

            features = feature_extractor.extract_all_features(email_data)

            print(f"  ✓ Total features extracted: {len(features)}")
            print("\n  Sample features:")
            for i, (name, value) in enumerate(list(features.items())[:10]):
                print(f"    - {name}: {value}")

            # Get feature vector
            feature_vector = feature_extractor.get_feature_vector(email_data)
            print(f"\n  ✓ Feature vector shape: {feature_vector.shape}")

            print("\n✓ Feature Extraction Test PASSED")
            return True
        else:
            print(f"  ✗ Sample file not found: {sample_file}")
            return False

    except Exception as e:
        print(f"\n✗ Feature Extraction Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_models():
    """Test database models"""
    print("\n" + "="*60)
    print("Testing Database Models")
    print("="*60)

    try:
        from database.models import Database, Email, IOC

        print("\n  ✓ Database models imported successfully")

        # Test creating database instance (without connecting)
        db = Database(db_url='postgresql://localhost/test_db')
        print("  ✓ Database instance created")

        # Test model structure
        print("\n  Email model fields:")
        for column in Email.__table__.columns:
            print(f"    - {column.name}: {column.type}")

        print("\n  IOC model fields:")
        for column in IOC.__table__.columns:
            print(f"    - {column.name}: {column.type}")

        print("\n✓ Database Models Test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Database Models Test FAILED: {e}")
        return False

def test_api_imports():
    """Test API imports"""
    print("\n" + "="*60)
    print("Testing API Imports")
    print("="*60)

    try:
        # Test Flask app imports
        print("\nImporting Flask app...")
        import backend.app as app
        print("  ✓ Flask app imported")

        # Check if app is created
        if hasattr(app, 'app'):
            print("  ✓ Flask app instance created")
        else:
            print("  ✗ Flask app instance not found")
            return False

        print("\n✓ API Imports Test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ API Imports Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("  PHISHING EMAIL DETECTION SYSTEM - TEST SUITE")
    print("="*70)

    results = {
        'Email Parser': test_email_parser(),
        'IOC Extractor': test_ioc_extractor(),
        'Feature Extraction': test_feature_extraction(),
        'Database Models': test_database_models(),
        'API Imports': test_api_imports()
    }

    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {test_name}: {status}")

    print("\n" + "-"*70)
    print(f"  Total: {passed}/{total} tests passed")
    print("="*70)

    if passed == total:
        print("\n  🎉 All tests passed! System is ready to use.")
        return True
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed. Please review errors above.")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
