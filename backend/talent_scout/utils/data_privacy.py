"""
Data Privacy and GDPR Compliance Utilities

This module provides utilities for handling candidate data in compliance
with data privacy regulations including GDPR, CCPA, and similar standards.

Key Features:
- Data anonymization for testing/demo environments
- PII (Personally Identifiable Information) masking
- Data retention policies
- Audit logging for data access
"""

import hashlib
import random
import string
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class DataPrivacyManager:
    """
    Manager for handling data privacy and GDPR compliance.
    
    Use this class to:
    - Anonymize candidate data for testing
    - Mask PII in logs and exports
    - Track data retention
    - Implement right to erasure (GDPR Article 17)
    """
    
    # Simulated data for testing/demo
    DEMO_FIRST_NAMES = [
        "Alex", "Jordan", "Taylor", "Casey", "Morgan", 
        "Riley", "Avery", "Quinn", "Cameron", "Skylar"
    ]
    
    DEMO_LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones",
        "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"
    ]
    
    DEMO_LOCATIONS = [
        "New York, NY", "San Francisco, CA", "Austin, TX",
        "Chicago, IL", "Seattle, WA", "Boston, MA",
        "Denver, CO", "Portland, OR", "Atlanta, GA"
    ]
    
    DEMO_TECH_STACKS = [
        ["Python", "Django", "PostgreSQL"],
        ["JavaScript", "React", "Node.js"],
        ["Java", "Spring Boot", "MySQL"],
        ["TypeScript", "Angular", "MongoDB"],
        ["Go", "Docker", "Kubernetes"],
        ["Ruby", "Rails", "Redis"],
    ]
    
    @staticmethod
    def generate_demo_email(first_name: str, last_name: str) -> str:
        """Generate a demo email address"""
        random_num = random.randint(100, 999)
        return f"{first_name.lower()}.{last_name.lower()}{random_num}@example.com"
    
    @staticmethod
    def generate_demo_phone() -> str:
        """Generate a demo phone number (US format)"""
        area_code = random.randint(200, 999)
        exchange = random.randint(200, 999)
        line = random.randint(1000, 9999)
        return f"+1 ({area_code}) {exchange}-{line}"
    
    @staticmethod
    def anonymize_session_data(session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize session data for demo/testing purposes.
        
        This replaces real PII with simulated data while maintaining
        data structure and realistic patterns.
        
        Args:
            session_data: Dictionary containing session information
            
        Returns:
            Anonymized session data dictionary
        """
        anonymized = session_data.copy()
        
        # Generate consistent fake data based on session ID hash
        if 'session_id' in anonymized:
            seed = int(hashlib.md5(str(anonymized['session_id']).encode()).hexdigest()[:8], 16)
            random.seed(seed)
        
        # Anonymize personal information
        if 'full_name' in anonymized and anonymized['full_name']:
            first = random.choice(DataPrivacyManager.DEMO_FIRST_NAMES)
            last = random.choice(DataPrivacyManager.DEMO_LAST_NAMES)
            anonymized['full_name'] = f"{first} {last}"
            anonymized['email'] = DataPrivacyManager.generate_demo_email(first, last)
        
        if 'phone' in anonymized and anonymized['phone']:
            anonymized['phone'] = DataPrivacyManager.generate_demo_phone()
        
        if 'location' in anonymized and anonymized['location']:
            anonymized['location'] = random.choice(DataPrivacyManager.DEMO_LOCATIONS)
        
        # Anonymize IP address
        if 'ip_address' in anonymized and anonymized['ip_address']:
            anonymized['ip_address'] = f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"
        
        # Keep tech stack realistic but randomize if empty
        if 'tech_stack' in anonymized:
            if not anonymized['tech_stack'] or len(anonymized['tech_stack']) == 0:
                anonymized['tech_stack'] = random.choice(DataPrivacyManager.DEMO_TECH_STACKS)
        
        return anonymized
    
    @staticmethod
    def mask_pii(text: str, mask_char: str = "*") -> str:
        """
        Mask PII in text for logging/display purposes.
        
        Replaces email addresses, phone numbers, and potential names
        with masked characters.
        
        Args:
            text: Text to mask
            mask_char: Character to use for masking
            
        Returns:
            Masked text
        """
        import re
        
        # Mask email addresses
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            lambda m: m.group(0)[:3] + mask_char * (len(m.group(0)) - 6) + m.group(0)[-3:],
            text
        )
        
        # Mask phone numbers
        text = re.sub(
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            mask_char * 12,
            text
        )
        
        return text
    
    @staticmethod
    def log_data_access(session_id: str, access_type: str, user: Optional[str] = None):
        """
        Log data access for GDPR audit trail.
        
        Args:
            session_id: Session identifier
            access_type: Type of access (read, update, delete, export)
            user: User who accessed the data
        """
        logger.info(
            f"DATA_ACCESS | Session: {session_id} | Type: {access_type} | "
            f"User: {user or 'anonymous'} | Timestamp: {datetime.now().isoformat()}"
        )
    
    @staticmethod
    def should_delete_session(session_created_at: datetime) -> bool:
        """
        Check if session should be deleted based on retention policy.
        
        Default retention: 90 days for inactive sessions
        
        Args:
            session_created_at: When the session was created
            
        Returns:
            True if session should be deleted
        """
        retention_days = getattr(settings, 'SESSION_RETENTION_DAYS', 90)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        return session_created_at < cutoff_date
    
    @staticmethod
    def anonymize_for_export(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare data for export with privacy protection.
        
        Removes sensitive fields and anonymizes PII for compliance
        with data export requests (GDPR Article 20).
        
        Args:
            data: Data to export
            
        Returns:
            Anonymized export data
        """
        # Remove internal metadata
        export_data = {
            k: v for k, v in data.items()
            if k not in ['ip_address', 'user_agent', 'sentiment_score']
        }
        
        # Anonymize PII if in demo mode
        if getattr(settings, 'DEMO_MODE', False):
            export_data = DataPrivacyManager.anonymize_session_data(export_data)
        
        return export_data


def ensure_gdpr_compliance():
    """
    Utility function to ensure GDPR compliance settings are configured.
    
    Call this during application startup to verify privacy settings.
    """
    required_settings = [
        'SESSION_RETENTION_DAYS',
        'DEMO_MODE',
    ]
    
    missing_settings = [
        setting for setting in required_settings
        if not hasattr(settings, setting)
    ]
    
    if missing_settings:
        logger.warning(
            f"Missing GDPR compliance settings: {', '.join(missing_settings)}. "
            "Using default values."
        )
    
    logger.info(
        f"GDPR Compliance Mode: {'DEMO' if getattr(settings, 'DEMO_MODE', False) else 'PRODUCTION'}"
    )
