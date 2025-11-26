"""
Setup script for Phishing Email Detection System
Run this script to set up the database and verify installation
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if all required packages are installed"""
    print("Checking dependencies...")
    required_packages = [
        'flask',
        'sqlalchemy',
        'psycopg2',
        'sklearn',
        'numpy',
        'pandas'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)

    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("\nAll dependencies installed!")
    return True

def setup_database():
    """Create database tables"""
    print("\nSetting up database...")
    try:
        from database.models import Database

        # Get database URL from user
        db_url = input("Enter PostgreSQL database URL [postgresql://postgres:password@localhost/phishing_detector]: ").strip()
        if not db_url:
            db_url = 'postgresql://postgres:password@localhost/phishing_detector'

        # Initialize database
        db = Database(db_url=db_url)
        db.create_tables()

        print("  ✓ Database tables created successfully!")
        return True

    except Exception as e:
        print(f"  ✗ Error setting up database: {e}")
        print("\nMake sure PostgreSQL is running and the database exists.")
        print("Create database with: CREATE DATABASE phishing_detector;")
        return False

def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    directories = [
        'data/uploads',
        'models',
        'logs'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ {directory}")

    # Create .gitkeep for uploads directory
    with open('data/uploads/.gitkeep', 'w') as f:
        f.write('')

    print("\nDirectories created!")
    return True

def test_installation():
    """Test if the installation is working"""
    print("\nTesting installation...")

    try:
        # Test imports
        from backend.utils.email_parser import EmailParser
        from backend.utils.ioc_extractor import IOCExtractor
        from ml.feature_extraction import FeatureExtractor

        print("  ✓ Email parser")
        print("  ✓ IOC extractor")
        print("  ✓ Feature extractor")

        print("\nInstallation test passed!")
        return True

    except Exception as e:
        print(f"  ✗ Error testing installation: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("  Phishing Email Detection System - Setup")
    print("=" * 60)

    # Check dependencies
    if not check_dependencies():
        print("\nSetup failed: Missing dependencies")
        sys.exit(1)

    # Create directories
    if not create_directories():
        print("\nSetup failed: Could not create directories")
        sys.exit(1)

    # Setup database
    print("\nDo you want to set up the database now? (y/n): ", end='')
    if input().lower() == 'y':
        if not setup_database():
            print("\nWarning: Database setup failed")
            print("You can set it up later by running this script again")

    # Test installation
    if not test_installation():
        print("\nSetup failed: Installation test failed")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  Setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update .env file with your database credentials")
    print("2. Start the backend: python backend/app.py")
    print("3. Open frontend/index.html in a browser")
    print("\nFor more information, see README.md")

if __name__ == '__main__':
    main()
