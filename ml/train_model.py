"""
Machine Learning Model Training Script
Trains a Random Forest classifier for phishing email detection
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.feature_extraction import FeatureExtractor
from backend.utils.email_parser import EmailParser

class PhishingDetector:
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.rf_model = None
        self.nb_model = None
        self.tfidf_vectorizer = None
        self.feature_names = None

    def prepare_data(self, email_files: list, labels: list):
        """
        Prepare training data from email files

        Args:
            email_files: List of paths to email files
            labels: List of labels (1 for phishing, 0 for legitimate)

        Returns:
            Feature matrix and labels
        """
        parser = EmailParser()
        feature_vectors = []
        text_data = []

        for email_file in email_files:
            try:
                # Parse email
                email_data = parser.parse_email_file(email_file)

                # Extract features
                features = self.feature_extractor.extract_all_features(email_data)
                feature_vector = [features[key] for key in sorted(features.keys())]
                feature_vectors.append(feature_vector)

                # Get text for TF-IDF
                subject = email_data.get('subject', '')
                body = email_data.get('body', '')
                text_data.append(subject + ' ' + body)

            except Exception as e:
                print(f"Error processing {email_file}: {e}")
                continue

        # Store feature names
        if feature_vectors:
            sample_features = self.feature_extractor.extract_all_features(
                parser.parse_email_file(email_files[0])
            )
            self.feature_names = sorted(sample_features.keys())

        X_features = np.array(feature_vectors)
        y = np.array(labels[:len(feature_vectors)])

        return X_features, y, text_data

    def train_random_forest(self, X_train, y_train):
        """
        Train Random Forest classifier

        Args:
            X_train: Training features
            y_train: Training labels

        Returns:
            Trained model
        """
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X_train, y_train)
        return self.rf_model

    def train_naive_bayes(self, text_data, y_train):
        """
        Train Naive Bayes classifier with TF-IDF features

        Args:
            text_data: List of email texts
            y_train: Training labels

        Returns:
            Trained model
        """
        # Create TF-IDF features
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        X_tfidf = self.tfidf_vectorizer.fit_transform(text_data)

        # Train Naive Bayes
        self.nb_model = MultinomialNB(alpha=0.1)
        self.nb_model.fit(X_tfidf, y_train)

        return self.nb_model

    def evaluate_model(self, model, X_test, y_test, model_name="Model"):
        """
        Evaluate model performance

        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            model_name: Name of the model

        Returns:
            Dictionary of metrics
        """
        y_pred = model.predict(X_test)

        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }

        print(f"\n{model_name} Performance:")
        print(f"Accuracy: {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall: {metrics['recall']:.4f}")
        print(f"F1-Score: {metrics['f1_score']:.4f}")
        print(f"Confusion Matrix:\n{metrics['confusion_matrix']}")

        return metrics

    def cross_validate(self, X, y, cv=5):
        """
        Perform cross-validation

        Args:
            X: Features
            y: Labels
            cv: Number of folds

        Returns:
            Cross-validation scores
        """
        if self.rf_model is None:
            self.rf_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )

        scores = cross_val_score(self.rf_model, X, y, cv=cv, scoring='accuracy')

        print(f"\nCross-Validation Scores: {scores}")
        print(f"Mean Accuracy: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")

        return scores

    def predict(self, email_data: dict):
        """
        Predict if an email is phishing

        Args:
            email_data: Parsed email data

        Returns:
            Prediction (1 for phishing, 0 for legitimate) and probability
        """
        if self.rf_model is None:
            raise ValueError("Model not trained. Please train the model first.")

        # Extract features
        features = self.feature_extractor.extract_all_features(email_data)
        feature_vector = np.array([features[key] for key in sorted(features.keys())])
        feature_vector = feature_vector.reshape(1, -1)

        # Predict
        prediction = self.rf_model.predict(feature_vector)[0]
        probability = self.rf_model.predict_proba(feature_vector)[0]

        return prediction, probability

    def save_model(self, model_path='models/phishing_detector.pkl'):
        """
        Save trained model to disk

        Args:
            model_path: Path to save the model
        """
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        model_data = {
            'rf_model': self.rf_model,
            'nb_model': self.nb_model,
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'feature_names': self.feature_names
        }

        joblib.dump(model_data, model_path)
        print(f"\nModel saved to {model_path}")

    def load_model(self, model_path='models/phishing_detector.pkl'):
        """
        Load trained model from disk

        Args:
            model_path: Path to the saved model
        """
        model_data = joblib.load(model_path)
        self.rf_model = model_data['rf_model']
        self.nb_model = model_data.get('nb_model')
        self.tfidf_vectorizer = model_data.get('tfidf_vectorizer')
        self.feature_names = model_data['feature_names']
        print(f"\nModel loaded from {model_path}")

    def get_feature_importance(self, top_n=10):
        """
        Get top N most important features

        Args:
            top_n: Number of top features to return

        Returns:
            List of (feature_name, importance) tuples
        """
        if self.rf_model is None or self.feature_names is None:
            raise ValueError("Model not trained or feature names not available")

        importances = self.rf_model.feature_importances_
        feature_importance = list(zip(self.feature_names, importances))
        feature_importance.sort(key=lambda x: x[1], reverse=True)

        print(f"\nTop {top_n} Most Important Features:")
        for i, (feature, importance) in enumerate(feature_importance[:top_n], 1):
            print(f"{i}. {feature}: {importance:.4f}")

        return feature_importance[:top_n]


def main():
    """
    Main training function
    This is a template - you'll need to provide your own dataset
    """
    print("Phishing Email Detection - Model Training")
    print("=" * 50)

    # Initialize detector
    detector = PhishingDetector()

    # TODO: Load your dataset here
    # For demonstration, this shows the expected format
    print("\nNote: This is a template. You need to provide your own dataset.")
    print("Expected format:")
    print("- email_files: List of paths to .eml files")
    print("- labels: List of labels (1 for phishing, 0 for legitimate)")
    print("\nExample:")
    print("email_files = ['data/phishing/email1.eml', 'data/legitimate/email2.eml', ...]")
    print("labels = [1, 0, ...]")

    # Example structure (commented out - replace with your data):
    """
    # Prepare data
    email_files = [...]  # Your email files
    labels = [...]  # Your labels

    X, y, text_data = detector.prepare_data(email_files, labels)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )

    text_train, text_test = train_test_split(
        text_data, test_size=0.15, random_state=42, stratify=y
    )

    # Train Random Forest
    print("\nTraining Random Forest Classifier...")
    detector.train_random_forest(X_train, y_train)
    detector.evaluate_model(detector.rf_model, X_test, y_test, "Random Forest")

    # Train Naive Bayes
    print("\nTraining Naive Bayes Classifier...")
    detector.train_naive_bayes(text_train, y_train)
    X_test_tfidf = detector.tfidf_vectorizer.transform(text_test)
    detector.evaluate_model(detector.nb_model, X_test_tfidf, y_test, "Naive Bayes")

    # Cross-validation
    print("\nPerforming Cross-Validation...")
    detector.cross_validate(X, y)

    # Feature importance
    detector.get_feature_importance()

    # Save model
    detector.save_model('models/phishing_detector.pkl')
    """

if __name__ == '__main__':
    main()
