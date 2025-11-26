"""
Email Parser Module
Parses .eml and .txt email files and extracts metadata
"""
import email
from email import policy
from email.parser import BytesParser
from typing import Dict, Any, List
import os
import base64
import quopri

class EmailParser:
    def __init__(self):
        pass

    def parse_email_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse an email file (.eml or .txt format)

        Args:
            file_path: Path to the email file

        Returns:
            Dictionary containing parsed email data
        """
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)

        email_data = {
            'sender': self._extract_sender(msg),
            'recipients': self._extract_recipients(msg),
            'subject': msg.get('subject', ''),
            'date': msg.get('date', ''),
            'message_id': msg.get('message-id', ''),
            'headers': self._extract_headers(msg),
            'body': self._extract_body(msg),
            'attachments': self._extract_attachments(msg, file_path)
        }

        return email_data

    def _extract_sender(self, msg) -> str:
        """Extract sender email address"""
        from_header = msg.get('from', '')
        if '<' in from_header and '>' in from_header:
            # Extract email from "Name <email@domain.com>" format
            start = from_header.find('<') + 1
            end = from_header.find('>')
            return from_header[start:end]
        return from_header

    def _extract_recipients(self, msg) -> List[str]:
        """Extract recipient email addresses"""
        recipients = []
        for header in ['to', 'cc', 'bcc']:
            value = msg.get(header, '')
            if value:
                recipients.extend([r.strip() for r in value.split(',')])
        return recipients

    def _extract_headers(self, msg) -> Dict[str, str]:
        """Extract all email headers"""
        headers = {}
        for key, value in msg.items():
            headers[key] = value
        return headers

    def _extract_body(self, msg) -> str:
        """
        Extract email body (both plain text and HTML)

        Args:
            msg: Email message object

        Returns:
            Email body text
        """
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                # Extract text content
                if content_type == "text/plain":
                    try:
                        body += part.get_content() + "\n"
                    except:
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body += payload.decode('utf-8', errors='ignore') + "\n"
                        except:
                            pass

                elif content_type == "text/html":
                    try:
                        html_content = part.get_content()
                        # Simple HTML tag removal
                        body += self._strip_html(html_content) + "\n"
                    except:
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                html_content = payload.decode('utf-8', errors='ignore')
                                body += self._strip_html(html_content) + "\n"
                        except:
                            pass
        else:
            # Not multipart
            try:
                body = msg.get_content()
            except:
                try:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                except:
                    body = str(msg.get_payload())

        return body.strip()

    def _strip_html(self, html: str) -> str:
        """
        Remove HTML tags from text

        Args:
            html: HTML content

        Returns:
            Plain text
        """
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_attachments(self, msg, email_file_path: str) -> List[Dict[str, Any]]:
        """
        Extract attachment metadata

        Args:
            msg: Email message object
            email_file_path: Path to the email file

        Returns:
            List of attachment metadata dictionaries
        """
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition"))

                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        # Get file size
                        payload = part.get_payload(decode=True)
                        file_size = len(payload) if payload else 0

                        # Compute hash
                        file_hash = ""
                        if payload:
                            import hashlib
                            file_hash = hashlib.md5(payload).hexdigest()

                        attachments.append({
                            'filename': filename,
                            'size': file_size,
                            'content_type': part.get_content_type(),
                            'md5_hash': file_hash
                        })

        return attachments

    def extract_features(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features for machine learning

        Args:
            email_data: Parsed email data

        Returns:
            Dictionary of features
        """
        body = email_data.get('body', '')
        subject = email_data.get('subject', '')
        sender = email_data.get('sender', '')

        features = {
            'email_length': len(body),
            'num_links': body.count('http://') + body.count('https://'),
            'num_attachments': len(email_data.get('attachments', [])),
            'has_urgency_words': self._has_urgency_words(body + ' ' + subject),
            'subject_length': len(subject),
            'sender_domain': sender.split('@')[-1] if '@' in sender else '',
            'num_recipients': len(email_data.get('recipients', [])),
            'has_external_links': self._has_external_links(body),
            'has_suspicious_keywords': self._has_suspicious_keywords(body + ' ' + subject)
        }

        return features

    def _has_urgency_words(self, text: str) -> bool:
        """Check for urgency words commonly used in phishing"""
        urgency_words = [
            'urgent', 'immediately', 'action required', 'verify', 'suspend',
            'limited time', 'act now', 'confirm', 'expires', 'update'
        ]
        text_lower = text.lower()
        return any(word in text_lower for word in urgency_words)

    def _has_external_links(self, text: str) -> bool:
        """Check for external links"""
        return 'http://' in text or 'https://' in text

    def _has_suspicious_keywords(self, text: str) -> bool:
        """Check for suspicious keywords"""
        suspicious_keywords = [
            'password', 'credit card', 'social security', 'bank account',
            'verify account', 'click here', 'winner', 'prize', 'lottery'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in suspicious_keywords)
