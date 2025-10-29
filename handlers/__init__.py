"""
Handler framework for site-specific scrapers.

Provides base classes and utilities for building website-specific scrapers.
"""

from toolkit.handlers.base import AbstractHandler
from toolkit.handlers.utils import URLValidator, NameValidator

__all__ = [
    'AbstractHandler',
    'URLValidator',
    'NameValidator',
]

