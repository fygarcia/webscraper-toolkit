"""
Database configuration classes.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """Configuration for database connections."""
    
    connection_string: str
    echo: bool = False
    pool_pre_ping: bool = True
    pool_size: int = 5
    max_overflow: int = 10
    connect_args: Optional[dict] = None
    
    def __post_init__(self):
        """Set default connect_args for SQLite if not provided."""
        if self.connect_args is None and "sqlite" in self.connection_string.lower():
            self.connect_args = {"check_same_thread": False}
