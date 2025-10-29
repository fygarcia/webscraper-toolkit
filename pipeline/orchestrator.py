"""
Pipeline orchestrator for executing multi-stage pipelines.
"""

import logging
from typing import List, Optional, Iterator, Callable
from toolkit.pipeline.base import AbstractPipeline
from toolkit.pipeline.item import ScrapedItem
from toolkit.pipeline.context import PipelineContext
from toolkit.pipeline.exceptions import DropItem, PipelineError


class PipelineOrchestrator:
    """
    Orchestrates execution of multiple pipeline stages.
    
    Manages pipeline stage execution, error handling, and statistics.
    """
    
    def __init__(self, pipelines: List[AbstractPipeline], context: Optional[PipelineContext] = None):
        """
        Initialize PipelineOrchestrator.
        
        Args:
            pipelines: List of pipeline stages to execute in order
            context: Optional PipelineContext for sharing state
        """
        self.pipelines = pipelines
        self.context = context or PipelineContext()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Set context on all pipelines
        for pipeline in self.pipelines:
            pipeline.set_context(self.context)
        
        # Statistics
        self.stats = {
            'total_items': 0,
            'processed_items': 0,
            'dropped_items': 0,
            'error_items': 0
        }
    
    def execute(self, items: Iterator[ScrapedItem]) -> List[ScrapedItem]:
        """
        Execute pipeline on a collection of items.
        
        Args:
            items: Iterator of ScrapedItem instances
            
        Returns:
            List of successfully processed items
        """
        self.logger.info(f"Starting pipeline execution with {len(self.pipelines)} stages")
        
        # Initialize all pipelines
        for pipeline in self.pipelines:
            try:
                pipeline.initialize()
            except Exception as e:
                self.logger.error(f"Error initializing pipeline {pipeline.name}: {e}")
                raise PipelineError(f"Pipeline initialization failed: {e}")
        
        processed_items = []
        
        try:
            # Process each item through all pipeline stages
            for item in items:
                self.stats['total_items'] += 1
                
                try:
                    processed_item = self._process_through_pipelines(item)
                    
                    if processed_item:
                        processed_items.append(processed_item)
                        self.stats['processed_items'] += 1
                    else:
                        self.stats['dropped_items'] += 1
                        
                except DropItem:
                    self.stats['dropped_items'] += 1
                    continue
                except Exception as e:
                    self.stats['error_items'] += 1
                    self.logger.error(f"Error processing item {item.name}: {e}", exc_info=True)
                    continue
        
        finally:
            # Finalize all pipelines
            for pipeline in self.pipelines:
                try:
                    pipeline.finalize()
                except Exception as e:
                    self.logger.warning(f"Error finalizing pipeline {pipeline.name}: {e}")
        
        self.logger.info(
            f"Pipeline execution complete. "
            f"Total: {self.stats['total_items']}, "
            f"Processed: {self.stats['processed_items']}, "
            f"Dropped: {self.stats['dropped_items']}, "
            f"Errors: {self.stats['error_items']}"
        )
        
        return processed_items
    
    def _process_through_pipelines(self, item: ScrapedItem) -> Optional[ScrapedItem]:
        """
        Process item through all pipeline stages sequentially.
        
        Args:
            item: ScrapedItem to process
            
        Returns:
            Processed ScrapedItem or None if dropped
        """
        current_item = item
        
        for pipeline in self.pipelines:
            if current_item is None:
                return None
            
            current_item = pipeline.process(current_item, self.context)
            
            if current_item is None:
                return None
        
        return current_item
    
    def get_stats(self) -> dict:
        """
        Get pipeline execution statistics.
        
        Returns:
            Dictionary with execution statistics
        """
        return self.stats.copy()
    
    def add_pipeline(self, pipeline: AbstractPipeline):
        """
        Add a pipeline stage to the orchestrator.
        
        Args:
            pipeline: AbstractPipeline instance to add
        """
        pipeline.set_context(self.context)
        self.pipelines.append(pipeline)
        self.logger.debug(f"Added pipeline stage: {pipeline.name}")
    
    def insert_pipeline(self, index: int, pipeline: AbstractPipeline):
        """
        Insert a pipeline stage at a specific position.
        
        Args:
            index: Position to insert at
            pipeline: AbstractPipeline instance to insert
        """
        pipeline.set_context(self.context)
        self.pipelines.insert(index, pipeline)
        self.logger.debug(f"Inserted pipeline stage at index {index}: {pipeline.name}")

