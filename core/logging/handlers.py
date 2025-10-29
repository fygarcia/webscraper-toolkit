"""
Custom logging handlers and formatters.
"""

import logging
from logging import handlers
from datetime import datetime, timezone
from typing import Optional, Any
from toolkit.core.logging.session import SessionTracker


class UTCFormatter(logging.Formatter):
    """
    Custom formatter that converts timestamps to UTC.
    
    Useful for distributed systems where consistent timezone handling is important.
    """
    
    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        """
        Format time in UTC.
        
        Args:
            record: Log record
            datefmt: Optional date format string
            
        Returns:
            Formatted UTC timestamp string
        """
        ct = datetime.fromtimestamp(record.created, tz=timezone.utc)
        if datefmt:
            return ct.strftime(datefmt)
        else:
            return ct.strftime('%Y-%m-%d %H:%M:%S UTC')


class DatabaseHandler(logging.Handler):
    """
    Custom handler for logging to database.
    
    Requires a database session/connection to be provided. The database
    should have a logs table with appropriate schema.
    """
    
    def __init__(self, db_session, table_name: str = "logs"):
        """
        Initialize DatabaseHandler.
        
        Args:
            db_session: Database session (SQLAlchemy Session or similar)
            table_name: Name of the logs table
        """
        super().__init__()
        self.db_session = db_session
        self.table_name = table_name
    
    def emit(self, record: logging.LogRecord):
        """
        Emit a log record to the database.
        
        Args:
            record: Log record to emit
        """
        try:
            # Get context from record
            context = getattr(record, 'context', {})
            session_id = context.get('session_id') or getattr(record, 'session_id', None)
            entity_id = context.get('entity_id') or getattr(record, 'entity_id', None)
            
            # Create log entry (this assumes a Log model exists)
            # Users should provide their own Log model or adapter
            log_entry = {
                'level': record.levelname,
                'message': self.format(record),
                'source': record.name,
                'session_id': session_id,
                'entity_id': entity_id,
                'timestamp': datetime.now(timezone.utc)
            }
            
            # Insert into database
            # This is a generic interface - users must implement their own
            # Log model or provide a custom emit method
            self._insert_log(log_entry)
            
        except Exception:
            # Don't let logging errors break the application
            self.handleError(record)
    
    def _insert_log(self, log_entry: dict):
        """
        Insert log entry into database.
        
        This is a placeholder - users should override or provide their own
        Log model implementation.
        
        Args:
            log_entry: Dictionary with log entry data
        """
        # Generic implementation - can be overridden by users
        # For SQLAlchemy, users would do:
        # log_record = Log(**log_entry)
        # self.db_session.add(log_record)
        # self.db_session.commit()
        pass

