"""
Content type definitions for file downloads.
"""

from enum import Enum


class ContentType(Enum):
    """
    Enum for different content types that can be downloaded.
    
    Generic content types applicable to any scraping project.
    """
    IMAGE = "images"
    THUMBNAIL = "thumbnails"
    VIDEO = "videos"
    DOCUMENT = "documents"
    AUDIO = "audio"
    ARCHIVE = "archives"
    OTHER = "other"

