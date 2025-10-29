"""
Logging manager for centralized logging configuration.
"""

import logging
import uuid
from typing import Optional, Dict, Any
from pathlib import Path

from toolkit.core.logging.config import LogConfig, LogLevel, HandlerConfig
from toolkit.core.logging.handlers import UTCFormatter, DatabaseHandler
from toolkit.core.logging.session import SessionTracker


class LoggingManager:
    """
    Manages logging configuration and loggers.
    
    Provides centralized logging setup with multiple handlers
    (console, file, database) and session tracking.
    """
    
    def __init__(self, config: LogConfig):
        """
        Initialize LoggingManager.
        
        Args:
            config: LogConfig instance with logging settings
        """
        self.config = config
        self.logger = logging.getLogger(config.logger_name)
        self.logger.setLevel(config.level.value)
        
        # Generate session ID if not provided
        self.session_id = config.session_id or str(uuid.uuid4())
        
        # Initialize session tracker if enabled
        self.session_tracker: Optional[SessionTracker] = None
        if config.enable_context:
            self.session_tracker = SessionTracker(self.session_id)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Setup configured handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup all configured logging handlers."""
        # If no handlers configured, setup default console handler
        if not self.config.handlers:
            self._setup_console_handler()
            return
        
        # Setup each configured handler
        for handler_config in self.config.handlers:
            if not handler_config.enabled:
                continue
            
            if handler_config.type == "console":
                self._setup_console_handler(handler_config)
            elif handler_config.type == "file":
                self._setup_file_handler(handler_config)
            elif handler_config.type == "database":
                self._setup_database_handler(handler_config)
    
    def _setup_console_handler(self, config: Optional[HandlerConfig] = None):
        """Setup console handler."""
        handler = logging.StreamHandler()
        handler.setLevel((config.level if config else self.config.level).value)
        formatter = UTCFormatter(self.config.format_string)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def _setup_file_handler(self, config: HandlerConfig):
        """Setup file handler with rotation."""
        if not config.file_path:
            self.logger.warning("File handler enabled but no file_path specified")
            return
        
        from logging.handlers import RotatingFileHandler
        
        file_path = Path(config.file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        handler = RotatingFileHandler(
            file_path,
            mode=config.file_mode,
            maxBytes=config.max_bytes,
            backupCount=config.backup_count
        )
        handler.setLevel(config.level.value)
        formatter = UTCFormatter(self.config.format_string)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def _setup_database_handler(self, config: HandlerConfig):
        """Setup database handler."""
        if not config.db_connection_string:
            self.logger.warning("Database handler enabled but no db_connection_string specified")
            return
        
        # Users must provide their own database session
        # This is a placeholder for the interface
        # In practice, users would pass their database session here
        handler = DatabaseHandler(None, config.table_name)
        handler.setLevel(config.level.value)
        formatter = UTCFormatter(self.config.format_string)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def get_logger(self) -> logging.Logger:
        """
        Get the configured logger instance.
        
        Returns:
            Configured logger
        """
        return self.logger
    
    def log(self, message: str, level: str = 'info', context: Optional[Dict[str, Any]] = None):
        """
        Log a message with optional context.
        
        Args:
            message: Log message
            level: Log level ('debug', 'info', 'warning', 'error', 'critical')
            context: Optional context dictionary (e.g., {'entity_id': '123'})
        """
        # Add session context
        if self.config.enable_context:
            extra = {'context': {'session_id': self.session_id}}
            if context:
                extra['context'].update(context)
        else:
            extra = {'context': context or {}}
        
        # Map level string to logging method
        level_methods = {
            'debug': self.logger.debug,
            'info': self.logger.info,
            'warning': self.logger.warning,
            'error': self.logger.error,
            'critical': self.logger.critical
        }
        
        method = level_methods.get(level.lower(), self.logger.info)
        method(message, extra=extra)
    
    def get_session_id(self) -> str:
        """
        Get the current session ID.
        
        Returns:
            Session ID string
        """
        return self.session_id
    
    @staticmethod
    def create_simple_config(
        logger_name: str = "scraper",
        level: LogLevel = LogLevel.INFO,
        log_file: Optional[Path] = None,
        session_id: Optional[str] = None
    ) -> LogConfig:
        """
        Create a simple logging configuration.
        
        Args:
            logger_name: Name of the logger
            level: Log level
            log_file: Optional file path for file logging
            session_id: Optional session ID
            
        Returns:
            LogConfig instance
        """
        handlers = [
            HandlerConfig(type="console", level=level, enabled=True)
        ]
        
        if log_file:
            handlers.append(
                HandlerConfig(
                    type="file",
                    level=level,
                    enabled=True,
                    file_path=log_file
                )
            )
        
        return LogConfig(
            logger_name=logger_name,
            level=level,
            handlers=handlers,
            session_id=session_id
        )

