"""
Base pipeline classes and interfaces.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from toolkit.pipeline.item import ScrapedItem
from toolkit.pipeline.context import PipelineContext
from toolkit.pipeline.exceptions import DropItem


class AbstractPipeline(ABC):
    """
    Abstract base class for all pipeline stages.
    
    Pipeline stages process items sequentially, each stage transforms
    or validates items before passing them to the next stage.
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize AbstractPipeline.
        
        Args:
            name: Optional name for this pipeline stage
        """
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(self.name)
        self.context: Optional[PipelineContext] = None
    
    def set_context(self, context: PipelineContext):
        """
        Set the pipeline context.
        
        Args:
            context: PipelineContext instance
        """
        self.context = context
    
    def process(self, item: ScrapedItem, context: Optional[PipelineContext] = None) -> Optional[ScrapedItem]:
        """
        Process an item through this pipeline stage.
        
        This method wraps the abstract process_item() method with common
        error handling and logging.
        
        Args:
            item: ScrapedItem to process
            context: Optional PipelineContext (uses self.context if not provided)
            
        Returns:
            Processed ScrapedItem, None if item should be dropped, or raises DropItem
        """
        if context:
            self.set_context(context)
        
        try:
            self.logger.debug(f"Processing item: {item.name} (source: {item.source})")
            result = self.process_item(item)
            
            if result is None:
                self.logger.debug(f"Item dropped by {self.name}: {item.name}")
            else:
                self.logger.debug(f"Item processed successfully by {self.name}: {result.name}")
            
            return result
            
        except DropItem as e:
            self.logger.info(f"Item dropped by {self.name}: {item.name} - {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error processing item in {self.name}: {e}", exc_info=True)
            raise
    
    @abstractmethod
    def process_item(self, item: ScrapedItem) -> Optional[ScrapedItem]:
        """
        Process a single item through this pipeline stage.
        
        This method must be implemented by subclasses.
        
        Args:
            item: ScrapedItem to process
            
        Returns:
            Processed ScrapedItem or None if item should be dropped
            
        Raises:
            DropItem: To explicitly drop the item
        """
        raise NotImplementedError
    
    def initialize(self):
        """
        Initialize pipeline stage (called before processing starts).
        
        Override this method for initialization logic.
        """
        pass
    
    def finalize(self):
        """
        Finalize pipeline stage (called after all items are processed).
        
        Override this method for cleanup or final processing.
        """
        pass

