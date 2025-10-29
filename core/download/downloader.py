"""
File downloader with retry logic and progress tracking.
"""

import logging
import time
from typing import Optional
from pathlib import Path
import requests

from toolkit.core.download.config import DownloadConfig, RetryPolicy
from toolkit.core.download.strategies import DownloadStrategy, HTTPDownloadStrategy


class FileDownloader:
    """
    Downloads files with retry logic and progress tracking.
    
    Uses strategy pattern for different download methods.
    """
    
    def __init__(self, config: DownloadConfig, strategy: Optional[DownloadStrategy] = None):
        """
        Initialize FileDownloader.
        
        Args:
            config: DownloadConfig instance
            strategy: DownloadStrategy instance (defaults to HTTPDownloadStrategy)
        """
        self.config = config
        self.strategy = strategy or HTTPDownloadStrategy(config)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def download(self, url: str, destination: Path, session: Optional[requests.Session] = None) -> bool:
        """
        Download file with automatic retries.
        
        Args:
            url: URL to download from
            destination: Path to save file
            session: Optional requests Session
            
        Returns:
            True if successful, False otherwise
        """
        retry_policy = self.config.retry_policy
        destination = Path(destination)
        
        for attempt in range(retry_policy.max_retries):
            try:
                success = self.strategy.download(url, destination, session)
                if success:
                    return True
            except Exception as e:
                self.logger.warning(f"Download attempt {attempt + 1} failed: {e}")
            
            # Calculate delay for next retry
            if attempt < retry_policy.max_retries - 1:
                delay = min(
                    retry_policy.base_delay * (retry_policy.exponential_base ** attempt),
                    retry_policy.max_delay
                )
                self.logger.info(f"Retrying in {delay:.1f}s...")
                time.sleep(delay)
        
        self.logger.error(f"Failed to download {url} after {retry_policy.max_retries} attempts")
        return False
    
    def download_stream(self, url: str, destination: Path, chunk_size: Optional[int] = None) -> bool:
        """
        Stream download for large files (uses same strategy, but explicit interface).
        
        Args:
            url: URL to download from
            destination: Path to save file
            chunk_size: Override chunk size from config
            
        Returns:
            True if successful, False otherwise
        """
        # Use the configured chunk size unless overridden
        original_chunk_size = self.config.chunk_size
        if chunk_size:
            self.config.chunk_size = chunk_size
        
        try:
            return self.download(url, destination)
        finally:
            self.config.chunk_size = original_chunk_size

