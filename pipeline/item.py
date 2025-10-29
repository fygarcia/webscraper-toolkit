"""
Generic scraped item data class for pipeline processing.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ScrapedItem:
    """
    Generic data class for scraped items.
    
    This is the primary data transfer object used throughout the pipeline.
    Users should extend this class or create their own dataclass for
    domain-specific fields.
    """
    # Essential identifiers
    source: str  # Source identifier (e.g., 'site1', 'scraper_name')
    name: str  # Item name/title
    detail_url: str  # URL to item detail page
    
    # Optional identifiers
    item_id: Optional[str] = None  # Unique identifier (can be set by pipeline)
    clean_name: Optional[str] = None  # Normalized name for matching
    
    # Media URLs
    thumbnail_url: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    video_urls: List[str] = field(default_factory=list)
    
    # Metadata
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)  # Generic metadata storage
    
    # Status flags
    is_active: bool = True
    is_new: bool = False
    is_available: bool = True
    
    # Local file paths (populated during processing)
    local_image_paths: List[str] = field(default_factory=list)
    local_video_paths: List[str] = field(default_factory=list)
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to the item."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)

