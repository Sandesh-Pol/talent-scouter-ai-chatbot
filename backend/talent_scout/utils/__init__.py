"""
Utility modules for TalentScout application.
"""

from .data_privacy import DataPrivacyManager, ensure_gdpr_compliance

__all__ = ['DataPrivacyManager', 'ensure_gdpr_compliance']
