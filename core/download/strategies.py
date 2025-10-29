"""
Download strategy implementations.

Provides different strategies for downloading files (HTTP, FTP, etc.)
"""

import logging
import requests
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path
from toolkit.core.download.config import DownloadConfig


class DownloadStrategy(ABC):
    """
    Abstract base class for download strategies.
    
    Strategy pattern for different download methods.
    """
    
    def __init__(self, config: DownloadConfig):
        """
        Initialize download strategy.
        
        Args:
            config: DownloadConfig instance
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def download(self, url: str, destination: Path, session: Optional[requests.Session] = None) -> bool:
        """
        Download a file from URL to destination.
        
        Args:
            url: URL to download from
            destination: Path to save file
            session: Optional requests Session
            
        Returns:
            True if successful, False otherwise
        """
        pass


class HTTPDownloadStrategy(DownloadStrategy):
    """
    HTTP/HTTPS download strategy using requests library.
    """
    
    def download(self, url: str, destination: Path, session: Optional[requests.Session] = None) -> bool:
        """
        Download file via HTTP/HTTPS.
        
        Args:
            url: URL to download from
            destination: Path to save file
            session: Optional requests Session
            
        Returns:
            True if successful, False otherwise
        """
        if not url or not isinstance(url, str):
            self.logger.error("URL must be a non-empty string")
            return False
        
        destination = Path(destination)
        
        try:
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.debug(f"Downloading: {url}")
            
            # Prepare headers
            headers = {
                'User-Agent': self.config.user_agent,
                'Accept': '*/*'
            }
            
            # Make request
            if session:
                response = session.get(
                    url, 
                    headers=headers, 
                    stream=True, 
                    timeout=self.config.timeout,
                    verify=self.config.verify_ssl
                )
            else:
                response = requests.get(
                    url,
                    headers=headers,
                    stream=True,
                    timeout=self.config.timeout,
                    verify=self.config.verify_ssl
                )
            
            response.raise_for_status()
            
            # Check available disk space
            content_length = response.headers.get('content-length')
            if content_length:
                required_space = int(content_length)
                available_space = self._get_available_space(destination.parent)
                if available_space < required_space:
                    self.logger.error(
                        f"Insufficient disk space. Required: {required_space}, "
                        f"Available: {available_space}"
                    )
                    return False
            
            # Download file
            with open(destination, "wb") as f:
                for chunk in response.iter_content(chunk_size=self.config.chunk_size):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
            
            self.logger.info(f"Successfully downloaded {url} to {destination}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return False
        except OSError as e:
            self.logger.error(f"Failed to save file to {destination}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error downloading {url}: {e}")
            return False
    
    def _get_available_space(self, path: Path) -> int:
        """
        Get available disk space in bytes.
        
        Args:
            path: Path to check disk space for
            
        Returns:
            Available space in bytes, or float('inf') if unable to determine
        """
        try:
            import os
            statvfs = os.statvfs(str(path))
            return statvfs.f_frsize * statvfs.f_bavail
        except (OSError, AttributeError):
            # Windows doesn't have statvfs
            try:
                import shutil
                total, used, free = shutil.disk_usage(str(path))
                return free
            except Exception:
                # Fallback: assume we have enough space
                return float('inf')

