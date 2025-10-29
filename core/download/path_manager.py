"""
Storage path management for file downloads.

Provides directory organization and path normalization utilities.
"""

import logging
from pathlib import Path
from typing import Union, Optional
from toolkit.core.download.types import ContentType


class StoragePathManager:
    """
    Manages storage paths and directory structure.
    
    Provides configurable path strategies for organizing downloaded content.
    """
    
    def __init__(self, base_dir: Union[str, Path], strategy: str = "source_type"):
        """
        Initialize StoragePathManager.
        
        Args:
            base_dir: Base directory for storage
            strategy: Path organization strategy - "flat", "source_type", or "custom"
        """
        self.base_dir = Path(base_dir)
        self.strategy = strategy
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Create base directory
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def get_content_dir(self, source: str, content_type: ContentType) -> Path:
        """
        Get directory for a source and content type.
        
        Args:
            source: Source identifier (e.g., "site1")
            content_type: ContentType enum value
            
        Returns:
            Path object for the content directory (created if doesn't exist)
        """
        if not source or not isinstance(source, str):
            raise ValueError("Source must be a non-empty string")
        
        if self.strategy == "flat":
            # All files in one directory
            content_dir = self.base_dir / content_type.value
        elif self.strategy == "source_type":
            # Organized by source, then by type
            content_dir = self.base_dir / source / content_type.value
        else:
            # Default to source_type
            content_dir = self.base_dir / source / content_type.value
        
        content_dir.mkdir(parents=True, exist_ok=True)
        return content_dir
    
    def normalize_path(self, path: Union[str, Path]) -> str:
        """
        Normalize path to relative format.
        
        Args:
            path: Path to normalize (absolute or relative)
            
        Returns:
            Normalized relative path string
        """
        if not path:
            return ""
        
        path_obj = Path(path)
        
        # Handle relative paths
        if not path_obj.is_absolute():
            normalized = str(path_obj).replace('\\', '/')
            return normalized.lower()
        
        # Handle absolute paths - try to make relative to base_dir
        try:
            relative_path = path_obj.relative_to(self.base_dir)
            return str(relative_path).replace('\\', '/').lower()
        except ValueError:
            # Path is not under base_dir, return normalized absolute
            return str(path_obj).replace('\\', '/').lower()
    
    def resolve_path(self, relative_path: str) -> Path:
        """
        Resolve relative path to absolute path.
        
        Args:
            relative_path: Relative path string
            
        Returns:
            Absolute Path object
        """
        if not relative_path:
            return self.base_dir
        
        # Remove leading base_dir reference if present
        if relative_path.startswith(str(self.base_dir)):
            return Path(relative_path)
        
        return self.base_dir / relative_path.lstrip('/').lstrip('\\')

