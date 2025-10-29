"""
Database connection and session management.
"""

import logging
from typing import Optional, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session

from toolkit.core.database.config import DatabaseConfig
from toolkit.core.database.models import ModelBase


class DatabaseManager:
    """
    Manages database connections and sessions.
    
    Provides engine, session factory, and schema management.
    """
    
    def __init__(self, config: DatabaseConfig):
        """
        Initialize DatabaseManager.
        
        Args:
            config: DatabaseConfig instance
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Create engine
        self.engine = create_engine(
            config.connection_string,
            echo=config.echo,
            pool_pre_ping=config.pool_pre_ping,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            connect_args=config.connect_args or {}
        )
        
        # Create session factory
        self.session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Create scoped session factory for thread safety
        self.scoped_session_factory = scoped_session(self.session_factory)
    
    def create_session(self) -> Session:
        """
        Create a new database session.
        
        Returns:
            New Session instance
        """
        return self.session_factory()
    
    def get_session(self) -> Session:
        """
        Get a scoped session (thread-safe).
        
        Returns:
            Scoped Session instance
        """
        return self.scoped_session_factory()
    
    def get_session_generator(self) -> Generator[Session, None, None]:
        """
        Get a session generator for dependency injection.
        
        Yields:
            Session instance
            
        Example:
            for session in db_manager.get_session_generator():
                # Use session
                pass
        """
        session = self.create_session()
        try:
            yield session
        finally:
            session.close()
    
    def create_all_tables(self, base: Optional[type] = None):
        """
        Create all tables defined in models.
        
        Args:
            base: Base class for models (defaults to ModelBase)
        """
        base = base or ModelBase
        base.metadata.create_all(bind=self.engine)
        self.logger.info("Created all database tables")
    
    def drop_all_tables(self, base: Optional[type] = None):
        """
        Drop all tables defined in models.
        
        Args:
            base: Base class for models (defaults to ModelBase)
            
        Warning: This will delete all data!
        """
        base = base or ModelBase
        base.metadata.drop_all(bind=self.engine)
        self.logger.warning("Dropped all database tables")
    
    def close(self):
        """Close database connections and cleanup."""
        self.engine.dispose()
        self.logger.debug("Database connections closed")
    
    @property
    def connection_string(self) -> str:
        """Get the connection string."""
        return self.config.connection_string

