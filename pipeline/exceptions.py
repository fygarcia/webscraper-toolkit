"""
Pipeline exceptions.
"""


class PipelineError(Exception):
    """Base exception for pipeline-related errors."""
    pass


class DropItem(Exception):
    """
    Exception raised to drop an item from processing.
    
    This is a control flow exception, not an error.
    When raised in a pipeline stage, the item will be skipped.
    """
    pass

