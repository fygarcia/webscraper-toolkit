"""
Logging configuration classes.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class HandlerConfig:
    """Configuration for a logging handler."""
    
    type: str  # "console", "file", "database"
    level: LogLevel = LogLevel.INFO
    enabled: bool = True
    
    # File handler specific
    file_path: Optional[Path] = None
    file_mode: str = "a"
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5
    
    # Database handler specific
    db_connection_string: Optional[str] = None
    table_name: str = "logs"


@dataclass
class LogConfig:
    """Complete logging configuration."""
    
    logger_name: str = "scraper"
    level: LogLevel = LogLevel.INFO
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers: List[HandlerConfig] = field(default_factory=list)
    session_id: Optional[str] = None
    enable_context: bool = True  # Enable context variables (session_id, etc.)

