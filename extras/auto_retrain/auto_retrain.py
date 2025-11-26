"""
Automatic Model Retraining Module

This module handles automatic retraining of the ML model based on:
1. Emails uploaded and analyzed in the database
2. Extracted IOCs (Indicators of Compromise) from emails
3. Scheduled intervals (daily, weekly, etc.)
4. Minimum data threshold (retrain when enough new data)

The model learns from:
- Email content (subject, body, sender)
- IOC patterns (URLs, IPs, domains, file hashes)
- Phishing classification from rule-based/ML detection

Usage:
    # Manual trigger
    python ml/auto_retrain.py

    # With scheduler (run in background)
    python ml/auto_retrain.py --schedule daily
"""

import os
import sys
import time
import schedule
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Database, Email, IOC
from ml.phishing_ml_model import SimplePhishingML
from backend.utils.email_parser import EmailParser
from ml.feature_extraction import FeatureExtractor


class AutoRetrainer:
    """Handles automatic model retraining using database emails and extracted IOCs"""

    def __init__(self, db_url=None, min_new_emails=10):
        """
        Initialize auto-retrainer

        Args:
            db_url: Database connection URL (None = SQLite default)
            min_new_emails: Minimum new emails needed before retraining
        """
        self.db = Database(db_url)
        self.ml_model = SimplePhishingML()
        self.email_parser = EmailParser()
        self.feature_extractor = FeatureExtractor()
        self.min_new_emails = min_new_emails

        # Model storage
        self.model_dir = Path(__file__).parent.parent / 'models'
        self.model_dir.mkdir(exist_ok=True)
        self.model_path = self.model_dir / 'simple_ml_model.pkl'
        self.backup_dir = self.model_dir / 'backups'
        self.backup_dir.mkdir(exist_ok=True)

    def check_if_retraining_needed(self):
        """
        Check if retraining is needed based on:
        - Number of new emails since last training
        - Total emails with IOCs in database

        Returns:
            tuple: (bool, str) - (should_retrain, reason)
        """
        session = self.db.Session()

        try:
            # Get last model training time from file modification
            if self.model_path.exists():
                last_train_time = datetime.fromtimestamp(self.model_path.stat().st_mtime)
            else:
                return True, "No existing model found"

            # Count emails uploaded since last training
            new_emails = session.query(Email).filter(
                Email.upload_date > last_train_time
            ).count()

            if new_emails >= self.min_new_emails:
                return True, f"{new_emails} new emails since last training"

            # Count emails with user feedback (has_user_feedback column)
            # Note: This requires adding a new column to track feedback
            # For now, we'll retrain based on total emails
            total_emails = session.query(Email).count()

            if total_emails >= self.min_new_emails:
                return True, f"Sufficient data: {total_emails} emails"

            return False, f"Not enough new data ({new_emails} new, {self.min_new_emails} needed)"

        finally:
            session.close()

    def backup_current_model(self):
        """Backup current model before retraining"""
        if not self.model_path.exists():
            print("⚠️  No existing model to backup")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f'model_backup_{timestamp}.pkl'

        import shutil
        shutil.copy2(self.model_path, backup_path)
        print(f"✅ Backed up model to: {backup_path}")

        return backup_path

    def prepare_training_data(self):
        """
        Prepare training data from database with IOCs

        Returns:
            tuple: (emails_data, labels) or None if insufficient data
        """
        session = self.db.Session()

        try:
            # Get all emails from database
            emails = session.query(Email).all()

            if len(emails) < 4:
                print(f"❌ Insufficient data: {len(emails)} emails (minimum 4 needed)")
                return None

            print(f"📊 Preparing training data from {len(emails)} emails...")

            emails_data = []
            labels = []

            for email in emails:
                # Get IOCs for this email
                iocs = session.query(IOC).filter_by(email_id=email.id).all()

                # Build IOC summary for features
                ioc_counts = {}
                for ioc in iocs:
                    ioc_type = ioc.ioc_type
                    if ioc_type not in ioc_counts:
                        ioc_counts[ioc_type] = 0
                    ioc_counts[ioc_type] += 1

                # Prepare email data dictionary with IOCs
                email_data = {
                    'subject': email.subject or '',
                    'sender': email.sender or '',
                    'body': email.body or '',
                    'full_text': f"{email.subject or ''} {email.body or ''}",
                    # Add IOC information
                    'ioc_count': len(iocs),
                    'has_ipv4': ioc_counts.get('ipv4', 0) > 0,
                    'has_url': ioc_counts.get('url', 0) > 0,
                    'has_email': ioc_counts.get('email', 0) > 0,
                    'has_hash': (ioc_counts.get('md5', 0) + ioc_counts.get('sha256', 0)) > 0,
                    'ipv4_count': ioc_counts.get('ipv4', 0),
                    'url_count': ioc_counts.get('url', 0),
                    'email_count': ioc_counts.get('email', 0),
                    'domain_count': ioc_counts.get('domain', 0),
                }

                emails_data.append(email_data)

                # Use the is_phishing label from database
                # 1 = phishing, 0 = legitimate
                labels.append(1 if email.is_phishing else 0)

            # Check label distribution
            phishing_count = sum(labels)
            legitimate_count = len(labels) - phishing_count

            print(f"   📧 Phishing emails: {phishing_count}")
            print(f"   ✉️  Legitimate emails: {legitimate_count}")

            # Calculate IOC statistics
            total_iocs = sum(ed.get('ioc_count', 0) for ed in emails_data)
            avg_iocs_phishing = sum(ed.get('ioc_count', 0) for i, ed in enumerate(emails_data) if labels[i] == 1) / max(phishing_count, 1)
            avg_iocs_legit = sum(ed.get('ioc_count', 0) for i, ed in enumerate(emails_data) if labels[i] == 0) / max(legitimate_count, 1)

            print(f"   🔍 Total IOCs extracted: {total_iocs}")
            print(f"   📊 Avg IOCs (phishing): {avg_iocs_phishing:.1f}")
            print(f"   📊 Avg IOCs (legitimate): {avg_iocs_legit:.1f}")

            # Need at least 2 of each class
            if phishing_count < 2 or legitimate_count < 2:
                print("⚠️  Warning: Unbalanced dataset (need at least 2 of each class)")
                if phishing_count < 2:
                    print("   ❌ Not enough phishing examples")
                if legitimate_count < 2:
                    print("   ❌ Not enough legitimate examples")
                return None

            return emails_data, labels

        finally:
            session.close()

    def retrain_model(self, force=False):
        """
        Retrain the ML model with data from database

        Args:
            force: Force retraining even if not needed

        Returns:
            bool: True if retraining was successful
        """
        print("\n" + "="*60)
        print("🔄 AUTOMATIC MODEL RETRAINING")
        print("="*60 + "\n")

        # Check if retraining is needed
        if not force:
            should_retrain, reason = self.check_if_retraining_needed()
            print(f"📋 Check: {reason}")

            if not should_retrain:
                print("✅ Retraining not needed at this time")
                return False
        else:
            print("⚡ Force retraining requested")

        print("\n" + "-"*60)

        # Prepare training data
        training_data = self.prepare_training_data()
        if training_data is None:
            print("❌ Cannot retrain: Insufficient or invalid data")
            return False

        emails_data, labels = training_data

        print("\n" + "-"*60)

        # Backup current model
        print("\n📦 Backing up current model...")
        self.backup_current_model()

        print("\n" + "-"*60)

        # Train new model
        print("\n🎓 Training new model...")
        print(f"   Training samples: {len(emails_data)}")

        try:
            # Create new model instance
            self.ml_model = SimplePhishingML()

            # Train on database emails
            success = self.ml_model.train_on_custom_data(emails_data, labels)

            if not success:
                print("❌ Training failed")
                return False

            # Save new model
            print("\n💾 Saving new model...")
            self.ml_model.save_model(str(self.model_path))

            print("\n" + "="*60)
            print("✅ MODEL RETRAINING COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"\n📁 Model saved to: {self.model_path}")
            print(f"📅 Training date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📊 Training samples: {len(emails_data)}")
            print("\n⚠️  NOTE: Restart the backend to load the new model:")
            print("   python backend/app.py")
            print("\n")

            return True

        except Exception as e:
            print(f"\n❌ Error during training: {e}")
            import traceback
            traceback.print_exc()
            return False

    def schedule_retraining(self, interval='daily', time_str='02:00'):
        """
        Schedule automatic retraining

        Args:
            interval: 'daily', 'weekly', or 'hourly'
            time_str: Time to run (HH:MM) for daily/weekly
        """
        print("\n" + "="*60)
        print("⏰ SCHEDULED RETRAINING ENABLED")
        print("="*60 + "\n")

        print(f"📅 Interval: {interval}")
        if interval in ['daily', 'weekly']:
            print(f"🕐 Time: {time_str}")
        print(f"📊 Minimum emails for retraining: {self.min_new_emails}")
        print("\n" + "-"*60 + "\n")

        # Schedule based on interval
        if interval == 'hourly':
            schedule.every().hour.do(self.retrain_model)
            print("✅ Scheduled: Every hour")

        elif interval == 'daily':
            schedule.every().day.at(time_str).do(self.retrain_model)
            print(f"✅ Scheduled: Every day at {time_str}")

        elif interval == 'weekly':
            schedule.every().monday.at(time_str).do(self.retrain_model)
            print(f"✅ Scheduled: Every Monday at {time_str}")

        print("\n🔄 Scheduler is running... (Press Ctrl+C to stop)")
        print("-"*60 + "\n")

        # Run scheduler loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            print("\n\n⏹️  Scheduler stopped by user")
            print("="*60 + "\n")


def main():
    """Main entry point for auto-retrain script"""
    parser = argparse.ArgumentParser(
        description='Automatic ML Model Retraining',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check and retrain if needed (one-time)
  python ml/auto_retrain.py

  # Force retraining even if not needed
  python ml/auto_retrain.py --force

  # Schedule daily retraining at 2 AM
  python ml/auto_retrain.py --schedule daily --time 02:00

  # Schedule hourly checks
  python ml/auto_retrain.py --schedule hourly

  # Schedule weekly (Monday at 3 AM)
  python ml/auto_retrain.py --schedule weekly --time 03:00

  # Set minimum emails threshold
  python ml/auto_retrain.py --min-emails 20
        """
    )

    parser.add_argument(
        '--schedule',
        choices=['hourly', 'daily', 'weekly'],
        help='Schedule automatic retraining'
    )

    parser.add_argument(
        '--time',
        default='02:00',
        help='Time to run (HH:MM) for daily/weekly schedules (default: 02:00)'
    )

    parser.add_argument(
        '--min-emails',
        type=int,
        default=10,
        help='Minimum new emails needed for retraining (default: 10)'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force retraining even if not needed'
    )

    parser.add_argument(
        '--db-url',
        help='Database URL (default: SQLite)'
    )

    args = parser.parse_args()

    # Create retrainer instance
    retrainer = AutoRetrainer(
        db_url=args.db_url,
        min_new_emails=args.min_emails
    )

    # Schedule or run once
    if args.schedule:
        retrainer.schedule_retraining(
            interval=args.schedule,
            time_str=args.time
        )
    else:
        # One-time retraining
        retrainer.retrain_model(force=args.force)


if __name__ == '__main__':
    main()
