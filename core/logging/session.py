"""
Session tracking for logging and monitoring.
"""

import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone


class SessionTracker:
    """
    Tracks session state and metadata for logging.
    
    Provides session-level context and statistics tracking.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize SessionTracker.
        
        Args:
            session_id: Optional session ID (generated if not provided)
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.start_time = datetime.now(timezone.utc)
        self.metadata: Dict[str, Any] = {}
        self.stats: Dict[str, int] = {}
    
    def add_metadata(self, key: str, value: Any):
        """
        Add metadata to session.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)
    
    def increment_stat(self, stat_name: str, amount: int = 1):
        """
        Increment a statistic counter.
        
        Args:
            stat_name: Name of the statistic
            amount: Amount to increment by
        """
        self.stats[stat_name] = self.stats.get(stat_name, 0) + amount
    
    def get_stat(self, stat_name: str, default: int = 0) -> int:
        """
        Get statistic value.
        
        Args:
            stat_name: Name of the statistic
            default: Default value if stat not found
            
        Returns:
            Statistic value
        """
        return self.stats.get(stat_name, default)
    
    def get_duration(self) -> float:
        """
        Get session duration in seconds.
        
        Returns:
            Duration in seconds
        """
        duration = datetime.now(timezone.utc) - self.start_time
        return duration.total_seconds()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get session summary.
        
        Returns:
            Dictionary with session summary
        """
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'duration_seconds': self.get_duration(),
            'metadata': self.metadata.copy(),
            'stats': self.stats.copy()
        }

