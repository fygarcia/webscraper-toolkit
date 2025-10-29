"""
Utility functions and validators for handlers.
"""

import re
from typing import Optional
from urllib.parse import urlparse


class URLValidator:
    """URL validation utilities."""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Check if string is a valid URL.
        
        Args:
            url: URL string to validate
            
        Returns:
            True if valid URL
        """
        if not url or not isinstance(url, str):
            return False
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def is_external_url(url: str, base_domain: str) -> bool:
        """
        Check if URL is external to base domain.
        
        Args:
            url: URL to check
            base_domain: Base domain (e.g., 'example.com')
            
        Returns:
            True if URL is external
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc != '' and base_domain not in parsed.netloc
        except Exception:
            return False
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalize URL by removing query parameters and fragments.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        try:
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        except Exception:
            return url


class NameValidator:
    """Name validation and normalization utilities."""
    
    @staticmethod
    def is_valid_name(name: str, min_length: int = 1, max_length: int = 200) -> bool:
        """
        Check if name is valid.
        
        Args:
            name: Name to validate
            min_length: Minimum length
            max_length: Maximum length
            
        Returns:
            True if valid name
        """
        if not name or not isinstance(name, str):
            return False
        
        name = name.strip()
        return min_length <= len(name) <= max_length
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize name by cleaning whitespace and special characters.
        
        Args:
            name: Name to normalize
            
        Returns:
            Normalized name
        """
        if not name:
            return ""
        
        # Strip whitespace
        name = name.strip()
        
        # Replace multiple spaces with single space
        name = re.sub(r'\s+', ' ', name)
        
        return name
    
    @staticmethod
    def clean_name(name: str) -> str:
        """
        Clean name by removing special characters and normalizing.
        
        Args:
            name: Name to clean
            
        Returns:
            Cleaned name (lowercase, alphanumeric + spaces)
        """
        if not name:
            return ""
        
        # Normalize first
        name = NameValidator.normalize_name(name)
        
        # Remove special characters (keep alphanumeric and spaces)
        name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        
        # Convert to lowercase
        name = name.lower()
        
        # Remove extra spaces
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name

