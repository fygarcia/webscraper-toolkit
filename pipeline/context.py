"""
Pipeline context for sharing state across pipeline stages.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone


class PipelineContext:
    """
    Context object passed through pipeline stages.
    
    Provides shared state and configuration for pipeline execution.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize PipelineContext.
        
        Args:
            session_id: Optional session ID for tracking
        """
        self.session_id = session_id
        self.start_time = datetime.now(timezone.utc)
        self.data: Dict[str, Any] = {}
        self.stats: Dict[str, Any] = {}
    
    def set(self, key: str, value: Any):
        """
        Set a value in context.
        
        Args:
            key: Key for the value
            value: Value to store
        """
        self.data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from context.
        
        Args:
            key: Key to retrieve
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        return self.data.get(key, default)
    
    def increment_stat(self, stat_name: str, amount: int = 1):
        """
        Increment a statistic.
        
        Args:
            stat_name: Name of the statistic
            amount: Amount to increment by
        """
        self.stats[stat_name] = self.stats.get(stat_name, 0) + amount
    
    def get_stat(self, stat_name: str, default: int = 0) -> int:
        """
        Get a statistic value.
        
        Args:
            stat_name: Name of the statistic
            default: Default value if stat not found
            
        Returns:
            Statistic value
        """
        return self.stats.get(stat_name, default)
    
    def get_duration(self) -> float:
        """
        Get pipeline execution duration in seconds.
        
        Returns:
            Duration in seconds
        """
        duration = datetime.now(timezone.utc) - self.start_time
        return duration.total_seconds()

