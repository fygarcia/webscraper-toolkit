"""
Download management module for web scraping.

Provides file downloading, path management, and download strategies.
"""

from toolkit.core.download.downloader import FileDownloader
from toolkit.core.download.path_manager import StoragePathManager
from toolkit.core.download.strategies import DownloadStrategy, HTTPDownloadStrategy
from toolkit.core.download.config import DownloadConfig, RetryPolicy
from toolkit.core.download.types import ContentType

__all__ = [
    'FileDownloader',
    'StoragePathManager',
    'DownloadStrategy',
    'HTTPDownloadStrategy',
    'DownloadConfig',
    'RetryPolicy',
    'ContentType',
]

