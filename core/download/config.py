"""
Download configuration classes.
"""

from dataclasses import dataclass


@dataclass
class RetryPolicy:
    """Retry policy configuration for downloads."""
    
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    backoff_factor: float = 1.0


@dataclass
class DownloadConfig:
    """Configuration for file downloads."""
    
    timeout: int = 30
    chunk_size: int = 8192
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    retry_policy: RetryPolicy = None
    verify_ssl: bool = True
    
    def __post_init__(self):
        """Initialize default retry policy if not provided."""
        if self.retry_policy is None:
            self.retry_policy = RetryPolicy()
