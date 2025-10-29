"""
Repository pattern and Unit of Work for database operations.
"""

import logging
from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc

from toolkit.core.database.models import ModelBase

T = TypeVar('T', bound=ModelBase)


class Repository(Generic[T]):
    """
    Generic repository pattern for database operations.
    
    Provides CRUD operations for any model type.
    """
    
    def __init__(self, session: Session, model_class: Type[T]):
        """
        Initialize Repository.
        
        Args:
            session: SQLAlchemy Session
            model_class: SQLAlchemy model class
        """
        self.session = session
        self.model_class = model_class
        self.logger = logging.getLogger(f"{self.__class__.__name__}[{model_class.__name__}]")
    
    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity instance or None
        """
        return self.session.query(self.model_class).filter_by(id=entity_id).first()
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0, order_by: Optional[str] = None) -> List[T]:
        """
        Get all entities.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Column name to order by (with '-' prefix for descending)
            
        Returns:
            List of entity instances
        """
        query = self.session.query(self.model_class)
        
        if order_by:
            if order_by.startswith('-'):
                # Descending order
                column = getattr(self.model_class, order_by[1:])
                query = query.order_by(desc(column))
            else:
                # Ascending order
                column = getattr(self.model_class, order_by)
                query = query.order_by(column)
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def find_by(self, **filters: Any) -> List[T]:
        """
        Find entities by filters.
        
        Args:
            **filters: Filter criteria (e.g., name="John", age=30)
            
        Returns:
            List of matching entity instances
        """
        return self.session.query(self.model_class).filter_by(**filters).all()
    
    def find_one_by(self, **filters: Any) -> Optional[T]:
        """
        Find one entity by filters.
        
        Args:
            **filters: Filter criteria
            
        Returns:
            Entity instance or None
        """
        return self.session.query(self.model_class).filter_by(**filters).first()
    
    def add(self, entity: T) -> T:
        """
        Add a new entity.
        
        Args:
            entity: Entity instance to add
            
        Returns:
            Added entity instance
        """
        self.session.add(entity)
        return entity
    
    def update(self, entity: T) -> T:
        """
        Update an entity.
        
        Args:
            entity: Entity instance to update
            
        Returns:
            Updated entity instance
        """
        self.session.merge(entity)
        return entity
    
    def delete(self, entity: T) -> None:
        """
        Delete an entity.
        
        Args:
            entity: Entity instance to delete
        """
        self.session.delete(entity)
    
    def delete_by_id(self, entity_id: Any) -> bool:
        """
        Delete entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            True if deleted, False if not found
        """
        entity = self.get_by_id(entity_id)
        if entity:
            self.delete(entity)
            return True
        return False
    
    def count(self, **filters: Any) -> int:
        """
        Count entities matching filters.
        
        Args:
            **filters: Filter criteria
            
        Returns:
            Count of matching entities
        """
        query = self.session.query(self.model_class)
        if filters:
            query = query.filter_by(**filters)
        return query.count()
    
    def exists(self, **filters: Any) -> bool:
        """
        Check if entity exists.
        
        Args:
            **filters: Filter criteria
            
        Returns:
            True if exists, False otherwise
        """
        return self.count(**filters) > 0


class UnitOfWork:
    """
    Unit of Work pattern for transaction management.
    
    Manages transactions and provides repositories with session management.
    """
    
    def __init__(self, session: Session):
        """
        Initialize UnitOfWork.
        
        Args:
            session: SQLAlchemy Session
        """
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)
        self._repositories: Dict[Type[T], Repository[T]] = {}
    
    def get_repository(self, model_class: Type[T]) -> Repository[T]:
        """
        Get or create repository for a model class.
        
        Args:
            model_class: SQLAlchemy model class
            
        Returns:
            Repository instance for the model
        """
        if model_class not in self._repositories:
            self._repositories[model_class] = Repository(self.session, model_class)
        return self._repositories[model_class]
    
    def commit(self):
        """Commit the current transaction."""
        try:
            self.session.commit()
            self.logger.debug("Transaction committed")
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Transaction failed, rolled back: {e}")
            raise
    
    def rollback(self):
        """Rollback the current transaction."""
        self.session.rollback()
        self.logger.debug("Transaction rolled back")
    
    def flush(self):
        """Flush pending changes to database without committing."""
        self.session.flush()
    
    def close(self):
        """Close the session."""
        self.session.close()
        self.logger.debug("Session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic commit/rollback."""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()

