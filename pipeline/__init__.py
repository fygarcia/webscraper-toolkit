"""
Pipeline framework for web scraping workflows.

Provides ETL pipeline pattern for data processing with filtering, transformation,
and loading stages.
"""

from toolkit.pipeline.item import ScrapedItem
from toolkit.pipeline.base import AbstractPipeline, PipelineContext
from toolkit.pipeline.orchestrator import PipelineOrchestrator
from toolkit.pipeline.exceptions import DropItem, PipelineError

__all__ = [
    'ScrapedItem',
    'AbstractPipeline',
    'PipelineContext',
    'PipelineOrchestrator',
    'DropItem',
    'PipelineError',
]

