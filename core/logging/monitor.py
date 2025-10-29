"""
Performance monitoring and metrics tracking.
"""

import time
import logging
from typing import Dict, Any, Optional
from contextlib import contextmanager
from datetime import datetime, timezone


class PerformanceMonitor:
    """
    Monitors performance metrics during scraping operations.
    
    Tracks timing, success/failure rates, and custom metrics.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize PerformanceMonitor.
        
        Args:
            logger: Optional logger for performance logs
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.metrics: Dict[str, Any] = {}
        self.timings: Dict[str, list] = {}
        self.counters: Dict[str, int] = {}
    
    @contextmanager
    def time_operation(self, operation_name: str):
        """
        Context manager for timing operations.
        
        Args:
            operation_name: Name of the operation to time
            
        Example:
            with monitor.time_operation("download"):
                download_file(url)
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            if operation_name not in self.timings:
                self.timings[operation_name] = []
            self.timings[operation_name].append(duration)
            self.logger.debug(f"Operation '{operation_name}' took {duration:.2f}s")
    
    def record_timing(self, operation_name: str, duration: float):
        """
        Record a timing measurement.
        
        Args:
            operation_name: Name of the operation
            duration: Duration in seconds
        """
        if operation_name not in self.timings:
            self.timings[operation_name] = []
        self.timings[operation_name].append(duration)
    
    def increment_counter(self, counter_name: str, amount: int = 1):
        """
        Increment a counter.
        
        Args:
            counter_name: Name of the counter
            amount: Amount to increment by
        """
        self.counters[counter_name] = self.counters.get(counter_name, 0) + amount
    
    def set_metric(self, metric_name: str, value: Any):
        """
        Set a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        self.metrics[metric_name] = value
    
    def get_metric(self, metric_name: str, default: Any = None) -> Any:
        """
        Get a metric value.
        
        Args:
            metric_name: Name of the metric
            default: Default value if metric not found
            
        Returns:
            Metric value
        """
        return self.metrics.get(metric_name, default)
    
    def get_timing_stats(self, operation_name: str) -> Dict[str, float]:
        """
        Get statistics for a timed operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Dictionary with min, max, mean, total, count
        """
        if operation_name not in self.timings or not self.timings[operation_name]:
            return {}
        
        timings = self.timings[operation_name]
        return {
            'count': len(timings),
            'total': sum(timings),
            'mean': sum(timings) / len(timings),
            'min': min(timings),
            'max': max(timings)
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get complete performance summary.
        
        Returns:
            Dictionary with all metrics, timings, and counters
        """
        timing_summaries = {
            name: self.get_timing_stats(name)
            for name in self.timings.keys()
        }
        
        return {
            'metrics': self.metrics.copy(),
            'timings': timing_summaries,
            'counters': self.counters.copy()
        }
    
    def reset(self):
        """Reset all metrics, timings, and counters."""
        self.metrics.clear()
        self.timings.clear()
        self.counters.clear()
        self.logger.debug("Performance monitor reset")

