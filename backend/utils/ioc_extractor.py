"""
IOC (Indicators of Compromise) Extractor Module
Extracts IP addresses, URLs, domains, email addresses, and file hashes from email content
"""
import re
import hashlib
from typing import List, Dict, Any

class IOCExtractor:
    def __init__(self):
        # Regular expressions for different IOC types
        self.patterns = {
            'ipv4': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
            'url': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'domain': r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b',
            'md5': r'\b[a-fA-F0-9]{32}\b',
            'sha1': r'\b[a-fA-F0-9]{40}\b',
            'sha256': r'\b[a-fA-F0-9]{64}\b'
        }

    def extract_iocs(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all IOCs from the given text

        Args:
            text: Email content (headers + body)

        Returns:
            Dictionary with IOC types as keys and lists of extracted values
        """
        iocs = {}

        for ioc_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            # Remove duplicates while preserving order
            unique_matches = list(dict.fromkeys(matches))
            if unique_matches:
                iocs[ioc_type] = unique_matches

        return iocs

    def extract_from_email(self, email_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract IOCs from email data structure

        Args:
            email_data: Dictionary containing email fields (sender, subject, body, headers)

        Returns:
            List of IOC dictionaries with type, value, and severity
        """
        # Combine all email content for IOC extraction
        combined_text = ""

        if 'sender' in email_data:
            combined_text += email_data['sender'] + "\n"
        if 'subject' in email_data:
            combined_text += email_data['subject'] + "\n"
        if 'body' in email_data:
            combined_text += email_data['body'] + "\n"
        if 'headers' in email_data:
            combined_text += str(email_data['headers']) + "\n"

        # Extract IOCs
        extracted_iocs = self.extract_iocs(combined_text)

        # Format as list of dictionaries
        ioc_list = []
        for ioc_type, values in extracted_iocs.items():
            for value in values:
                ioc_list.append({
                    'ioc_type': ioc_type,
                    'ioc_value': value,
                    'severity': self._determine_severity(ioc_type, value)
                })

        return ioc_list

    def _determine_severity(self, ioc_type: str, value: str) -> str:
        """
        Determine severity level based on IOC type and value

        Args:
            ioc_type: Type of IOC
            value: IOC value

        Returns:
            Severity level (low, medium, high)
        """
        # Simple heuristics for severity determination
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top']

        if ioc_type in ['md5', 'sha1', 'sha256']:
            return 'high'
        elif ioc_type == 'ipv4':
            return 'medium'
        elif ioc_type == 'url':
            if any(tld in value.lower() for tld in suspicious_tlds):
                return 'high'
            return 'medium'
        elif ioc_type == 'domain':
            if any(tld in value.lower() for tld in suspicious_tlds):
                return 'high'
            return 'low'
        else:
            return 'low'

    def defang_url(self, url: str) -> str:
        """
        Defang URLs by replacing http:// with hxxp:// and . with [.]

        Args:
            url: URL to defang

        Returns:
            Defanged URL
        """
        defanged = url.replace('http://', 'hxxp://')
        defanged = defanged.replace('https://', 'hxxps://')
        defanged = defanged.replace('.', '[.]')
        return defanged

    def compute_file_hash(self, file_path: str, algorithm: str = 'sha256') -> str:
        """
        Compute hash of a file

        Args:
            file_path: Path to the file
            algorithm: Hash algorithm (md5, sha1, sha256)

        Returns:
            Hex digest of the file hash
        """
        hash_func = getattr(hashlib, algorithm)()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)

        return hash_func.hexdigest()
