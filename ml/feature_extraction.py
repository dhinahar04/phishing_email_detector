"""
Feature Extraction Module for ML Model
Extracts features from email data for phishing detection
"""
import re
from typing import Dict, Any
import numpy as np

class FeatureExtractor:
    def __init__(self):
        # Keywords commonly found in phishing emails
        self.urgency_words = [
            'urgent', 'immediately', 'action required', 'verify', 'suspend',
            'limited time', 'act now', 'confirm', 'expires', 'update', 'warning'
        ]

        self.suspicious_keywords = [
            'password', 'credit card', 'social security', 'bank account',
            'verify account', 'click here', 'winner', 'prize', 'lottery',
            'inheritance', 'transfer', 'refund', 'tax', 'suspended'
        ]

        self.suspicious_tlds = [
            '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work',
            '.click', '.link', '.download', '.stream'
        ]

    def extract_text_features(self, text: str) -> Dict[str, float]:
        """
        Extract text-based features from email content

        Args:
            text: Email text (subject + body)

        Returns:
            Dictionary of features
        """
        text_lower = text.lower()

        features = {
            'length': len(text),
            'num_words': len(text.split()),
            'num_sentences': text.count('.') + text.count('!') + text.count('?'),
            'avg_word_length': np.mean([len(word) for word in text.split()]) if text.split() else 0,
            'num_exclamation': text.count('!'),
            'num_question': text.count('?'),
            'num_uppercase': sum(1 for c in text if c.isupper()),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if len(text) > 0 else 0,
        }

        return features

    def extract_url_features(self, text: str) -> Dict[str, float]:
        """
        Extract URL-related features

        Args:
            text: Email text

        Returns:
            Dictionary of URL features
        """
        # Find all URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text, re.IGNORECASE)

        features = {
            'num_links': len(urls),
            'has_shortened_url': any(
                domain in url.lower() for url in urls
                for domain in ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly']
            ) if urls else False,
            'has_suspicious_tld': any(
                tld in url.lower() for url in urls for tld in self.suspicious_tlds
            ) if urls else False,
            'has_ip_address': any(
                re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url)
                for url in urls
            ) if urls else False,
            'num_at_symbols': sum(url.count('@') for url in urls),
            'avg_url_length': np.mean([len(url) for url in urls]) if urls else 0,
            'max_url_length': max([len(url) for url in urls]) if urls else 0,
        }

        return features

    def extract_email_features(self, email_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract features from email metadata

        Args:
            email_data: Parsed email data

        Returns:
            Dictionary of email features
        """
        sender = email_data.get('sender', '')
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')

        features = {
            'subject_length': len(subject),
            'body_length': len(body),
            'sender_has_numbers': bool(re.search(r'\d', sender)),
            'num_recipients': len(email_data.get('recipients', [])),
            'has_attachments': len(email_data.get('attachments', [])) > 0,
            'num_attachments': len(email_data.get('attachments', [])),
        }

        return features

    def extract_keyword_features(self, text: str) -> Dict[str, float]:
        """
        Extract keyword-based features

        Args:
            text: Email text

        Returns:
            Dictionary of keyword features
        """
        text_lower = text.lower()

        features = {
            'num_urgency_words': sum(
                text_lower.count(word) for word in self.urgency_words
            ),
            'has_urgency_words': any(
                word in text_lower for word in self.urgency_words
            ),
            'num_suspicious_keywords': sum(
                text_lower.count(keyword) for keyword in self.suspicious_keywords
            ),
            'has_suspicious_keywords': any(
                keyword in text_lower for keyword in self.suspicious_keywords
            ),
        }

        return features

    def extract_ioc_features(self, email_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract IOC-based features (if IOC data is available)

        Args:
            email_data: Parsed email data with optional IOC counts

        Returns:
            Dictionary of IOC features
        """
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

    def extract_all_features(self, email_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract all features from email data

        Args:
            email_data: Parsed email data (with optional IOC data)

        Returns:
            Dictionary of all features
        """
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        combined_text = subject + ' ' + body

        # Extract different feature groups
        text_features = self.extract_text_features(combined_text)
        url_features = self.extract_url_features(combined_text)
        email_features = self.extract_email_features(email_data)
        keyword_features = self.extract_keyword_features(combined_text)
        ioc_features = self.extract_ioc_features(email_data)  # NEW: IOC-based features

        # Combine all features
        all_features = {
            **text_features,
            **url_features,
            **email_features,
            **keyword_features,
            **ioc_features  # NEW: Include IOC features
        }

        return all_features

    def get_feature_vector(self, email_data: Dict[str, Any]) -> np.ndarray:
        """
        Get feature vector as numpy array for ML model

        Args:
            email_data: Parsed email data

        Returns:
            Numpy array of feature values
        """
        features = self.extract_all_features(email_data)

        # Define feature order (important for model consistency)
        feature_names = sorted(features.keys())

        # Create feature vector
        feature_vector = np.array([
            float(features[name]) for name in feature_names
        ])

        return feature_vector

    def get_feature_names(self, email_data: Dict[str, Any]) -> list:
        """
        Get ordered list of feature names

        Args:
            email_data: Parsed email data

        Returns:
            List of feature names in order
        """
        features = self.extract_all_features(email_data)
        return sorted(features.keys())
