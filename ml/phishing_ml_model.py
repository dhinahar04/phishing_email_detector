"""
Simple ML Model for Phishing Detection
Trains on the test emails and provides predictions
"""
import os
import sys
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.email_parser import EmailParser
from ml.feature_extraction import FeatureExtractor

class SimplePhishingML:
    def __init__(self):
        self.rf_model = None
        self.tfidf_vectorizer = None
        self.feature_extractor = FeatureExtractor()
        self.model_version = "simple-rf-v1.0"

    def train_on_training_data(self, max_samples=None):
        """
        Train on the full training dataset in data/train/

        Args:
            max_samples: Maximum samples to use (None = use all)
        """
        parser = EmailParser()

        train_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data', 'train'
        )

        phishing_dir = os.path.join(train_dir, 'phishing')
        legitimate_dir = os.path.join(train_dir, 'legitimate')

        # Check directories exist
        if not os.path.exists(phishing_dir) or not os.path.exists(legitimate_dir):
            raise FileNotFoundError(f"Training data not found in {train_dir}")

        # Get all files
        phishing_files = [f for f in os.listdir(phishing_dir) if os.path.isfile(os.path.join(phishing_dir, f))]
        legitimate_files = [f for f in os.listdir(legitimate_dir) if os.path.isfile(os.path.join(legitimate_dir, f))]

        # Limit samples if specified
        if max_samples:
            max_per_class = max_samples // 2
            phishing_files = phishing_files[:max_per_class]
            legitimate_files = legitimate_files[:max_per_class]

        print(f"\n📊 Training Data:")
        print(f"   Phishing emails: {len(phishing_files)}")
        print(f"   Legitimate emails: {len(legitimate_files)}")
        print(f"   Total: {len(phishing_files) + len(legitimate_files)}")
        print(f"\n🔄 Processing emails...")

        texts = []
        labels = []
        feature_vectors = []

        # Process phishing emails
        print(f"\n   Processing {len(phishing_files)} phishing emails...")
        processed = 0
        errors = 0

        for i, filename in enumerate(phishing_files, 1):
            filepath = os.path.join(phishing_dir, filename)
            try:
                email_data = parser.parse_email_file(filepath)
                text = email_data.get('subject', '') + ' ' + email_data.get('body', '')
                texts.append(text)
                labels.append(1)  # 1 = phishing

                features = self.feature_extractor.extract_all_features(email_data)
                feature_vector = [features[key] for key in sorted(features.keys())]
                feature_vectors.append(feature_vector)
                processed += 1

                # Progress indicator every 100 emails
                if i % 100 == 0:
                    print(f"      Processed {i}/{len(phishing_files)} phishing emails...")

            except Exception as e:
                errors += 1
                if errors <= 5:  # Only show first 5 errors
                    print(f"      ⚠️  Error in {filename}: {str(e)[:50]}")

        print(f"   ✅ Processed {processed} phishing emails ({errors} errors)")

        # Process legitimate emails
        print(f"\n   Processing {len(legitimate_files)} legitimate emails...")
        processed = 0
        errors = 0

        for i, filename in enumerate(legitimate_files, 1):
            filepath = os.path.join(legitimate_dir, filename)
            try:
                email_data = parser.parse_email_file(filepath)
                text = email_data.get('subject', '') + ' ' + email_data.get('body', '')
                texts.append(text)
                labels.append(0)  # 0 = legitimate

                features = self.feature_extractor.extract_all_features(email_data)
                feature_vector = [features[key] for key in sorted(features.keys())]
                feature_vectors.append(feature_vector)
                processed += 1

                # Progress indicator every 100 emails
                if i % 100 == 0:
                    print(f"      Processed {i}/{len(legitimate_files)} legitimate emails...")

            except Exception as e:
                errors += 1
                if errors <= 5:  # Only show first 5 errors
                    print(f"      ⚠️  Error in {filename}: {str(e)[:50]}")

        print(f"   ✅ Processed {processed} legitimate emails ({errors} errors)")

        if len(texts) < 4:
            raise ValueError("Not enough training data. Need at least 4 emails.")

        # Training
        print(f"\n🎓 Training model on {len(texts)} emails...")
        print(f"   Phishing: {sum(labels)}, Legitimate: {len(labels) - sum(labels)}")

        # Train TF-IDF model
        print(f"\n   Fitting TF-IDF vectorizer...")
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        X_tfidf = self.tfidf_vectorizer.fit_transform(texts).toarray()

        # Combine with extracted features
        X_features = np.array(feature_vectors)
        X_combined = np.hstack([X_tfidf, X_features])

        print(f"   Feature matrix shape: {X_combined.shape}")
        print(f"   Training Random Forest (50 trees)...")

        # Train Random Forest
        self.rf_model = RandomForestClassifier(
            n_estimators=50,
            max_depth=10,
            random_state=42,
            n_jobs=-1  # Use all CPU cores
        )
        self.rf_model.fit(X_combined, labels)

        # Calculate accuracy
        train_predictions = self.rf_model.predict(X_combined)
        accuracy = np.mean(train_predictions == labels)

        print(f"\n✅ Training completed!")
        print(f"   Training Accuracy: {accuracy * 100:.2f}%")

        return accuracy

    def train_on_test_emails(self):
        """Train on the small test emails (for quick testing)"""
        parser = EmailParser()

        # Define training data from our test emails
        test_emails_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data', 'test_emails'
        )

        # Phishing emails
        phishing_files = [
            'phishing_paypal.eml',
            'phishing_bank.eml',
            'phishing_prize.eml',
            'phishing_microsoft.eml'
        ]

        # Legitimate emails
        legitimate_files = [
            'legitimate_amazon.eml',
            'legitimate_github.eml',
            'legitimate_newsletter.eml',
            'legitimate_work.eml'
        ]

        texts = []
        labels = []
        feature_vectors = []

        # Process phishing emails
        for filename in phishing_files:
            filepath = os.path.join(test_emails_dir, filename)
            if os.path.exists(filepath):
                try:
                    email_data = parser.parse_email_file(filepath)
                    text = email_data.get('subject', '') + ' ' + email_data.get('body', '')
                    texts.append(text)
                    labels.append(1)  # 1 = phishing

                    # Extract features
                    features = self.feature_extractor.extract_all_features(email_data)
                    feature_vector = [features[key] for key in sorted(features.keys())]
                    feature_vectors.append(feature_vector)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

        # Process legitimate emails
        for filename in legitimate_files:
            filepath = os.path.join(test_emails_dir, filename)
            if os.path.exists(filepath):
                try:
                    email_data = parser.parse_email_file(filepath)
                    text = email_data.get('subject', '') + ' ' + email_data.get('body', '')
                    texts.append(text)
                    labels.append(0)  # 0 = legitimate

                    # Extract features
                    features = self.feature_extractor.extract_all_features(email_data)
                    feature_vector = [features[key] for key in sorted(features.keys())]
                    feature_vectors.append(feature_vector)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

        if len(texts) < 4:
            raise ValueError("Not enough training data. Need at least 4 emails.")

        print(f"Training on {len(texts)} emails ({sum(labels)} phishing, {len(labels) - sum(labels)} legitimate)")

        # Train TF-IDF model for text features
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        X_tfidf = self.tfidf_vectorizer.fit_transform(texts).toarray()

        # Combine with extracted features
        X_features = np.array(feature_vectors)
        X_combined = np.hstack([X_tfidf, X_features])

        # Train Random Forest
        self.rf_model = RandomForestClassifier(
            n_estimators=50,
            max_depth=10,
            random_state=42
        )
        self.rf_model.fit(X_combined, labels)

        # Calculate training accuracy
        train_predictions = self.rf_model.predict(X_combined)
        accuracy = np.mean(train_predictions == labels)

        print(f"Training completed! Accuracy: {accuracy * 100:.1f}%")

        return accuracy

    def train_on_custom_data(self, emails_data, labels):
        """
        Train on custom email data (e.g., from database)

        Args:
            emails_data: List of email data dictionaries with keys:
                         'subject', 'sender', 'body', 'full_text'
            labels: List of labels (1 = phishing, 0 = legitimate)

        Returns:
            bool: True if training successful
        """
        if len(emails_data) != len(labels):
            raise ValueError("Number of emails and labels must match")

        if len(emails_data) < 4:
            raise ValueError("Need at least 4 emails for training")

        # Check we have both classes
        phishing_count = sum(labels)
        legitimate_count = len(labels) - phishing_count

        if phishing_count < 2 or legitimate_count < 2:
            raise ValueError("Need at least 2 examples of each class")

        print(f"Training on {len(emails_data)} emails ({phishing_count} phishing, {legitimate_count} legitimate)")

        texts = []
        feature_vectors = []

        for email_data in emails_data:
            # Get text (prefer full_text if available)
            if 'full_text' in email_data and email_data['full_text']:
                text = email_data['full_text']
            else:
                text = email_data.get('subject', '') + ' ' + email_data.get('body', '')

            texts.append(text)

            # Extract features
            features = self.feature_extractor.extract_all_features(email_data)
            feature_vector = [features[key] for key in sorted(features.keys())]
            feature_vectors.append(feature_vector)

        # Train TF-IDF model
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        X_tfidf = self.tfidf_vectorizer.fit_transform(texts).toarray()

        # Combine with extracted features
        X_features = np.array(feature_vectors)
        X_combined = np.hstack([X_tfidf, X_features])

        # Train Random Forest
        self.rf_model = RandomForestClassifier(
            n_estimators=50,
            max_depth=10,
            random_state=42
        )
        self.rf_model.fit(X_combined, labels)

        # Calculate training accuracy
        train_predictions = self.rf_model.predict(X_combined)
        accuracy = np.mean(train_predictions == labels)

        print(f"Training completed! Accuracy: {accuracy * 100:.1f}%")

        return True

    def predict(self, email_data):
        """
        Predict if an email is phishing

        Args:
            email_data: Parsed email data dictionary

        Returns:
            prediction: 1 for phishing, 0 for legitimate
            probabilities: [prob_legitimate, prob_phishing]
        """
        if self.rf_model is None or self.tfidf_vectorizer is None:
            raise ValueError("Model not trained. Call train_on_test_emails() first.")

        # Prepare text
        text = email_data.get('subject', '') + ' ' + email_data.get('body', '')

        # TF-IDF features
        X_tfidf = self.tfidf_vectorizer.transform([text]).toarray()

        # Extract features
        features = self.feature_extractor.extract_all_features(email_data)
        feature_vector = np.array([features[key] for key in sorted(features.keys())])
        feature_vector = feature_vector.reshape(1, -1)

        # Combine features
        X_combined = np.hstack([X_tfidf, feature_vector])

        # Predict
        prediction = self.rf_model.predict(X_combined)[0]
        probabilities = self.rf_model.predict_proba(X_combined)[0]

        return prediction, probabilities

    def save_model(self, model_path='models/simple_ml_model.pkl'):
        """Save trained model to disk"""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        model_data = {
            'rf_model': self.rf_model,
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'model_version': self.model_version
        }

        joblib.dump(model_data, model_path)
        print(f"Model saved to {model_path}")

    def load_model(self, model_path='models/simple_ml_model.pkl'):
        """Load trained model from disk"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        model_data = joblib.load(model_path)
        self.rf_model = model_data['rf_model']
        self.tfidf_vectorizer = model_data['tfidf_vectorizer']
        self.model_version = model_data.get('model_version', 'unknown')

        print(f"Model loaded from {model_path}")


def train_and_save(use_full_dataset=True, max_samples=None):
    """
    Train model and save it

    Args:
        use_full_dataset: Use data/train/ if True, else use test_emails/
        max_samples: Maximum samples to use (None = use all)
    """
    print("="*60)
    print("Training ML Model for Phishing Detection")
    print("="*60)

    ml_model = SimplePhishingML()

    if use_full_dataset:
        print("\n🎯 Using full training dataset from data/train/")
        if max_samples:
            print(f"   Limited to {max_samples} samples")
        accuracy = ml_model.train_on_training_data(max_samples=max_samples)
    else:
        print("\n🎯 Using test emails from data/test_emails/")
        accuracy = ml_model.train_on_test_emails()

    # Save model
    model_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'models', 'simple_ml_model.pkl'
    )
    ml_model.save_model(model_path)

    print("\n" + "="*60)
    print(f"✅ Model trained and saved successfully!")
    print(f"   Training Accuracy: {accuracy * 100:.2f}%")
    print(f"   Model Location: {model_path}")
    print("="*60)
    print(f"\n💡 To use this model:")
    print(f"   python backend/app.py")
    print("="*60 + "\n")

    return ml_model


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Train phishing detection ML model')
    parser.add_argument(
        '--test-only',
        action='store_true',
        help='Use only test emails (8 samples) instead of full training data'
    )
    parser.add_argument(
        '--max-samples',
        type=int,
        help='Maximum number of samples to use from training data'
    )

    args = parser.parse_args()

    # Train and save the model
    train_and_save(
        use_full_dataset=not args.test_only,
        max_samples=args.max_samples
    )
