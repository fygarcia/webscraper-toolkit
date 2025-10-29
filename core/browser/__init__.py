"""
Browser automation module for web scraping.

Provides WebDriver management, session handling, cookie management, and proxy support.
"""

from toolkit.core.browser.controller import WebDriverController
from toolkit.core.browser.session import BrowserSession
from toolkit.core.browser.cookies import CookieManager
from toolkit.core.browser.window import WindowManager
from toolkit.core.browser.proxy import ProxyManager
from toolkit.core.browser.config import BrowserConfig, ProxyConfig, StealthConfig

__all__ = [
    'WebDriverController',
    'BrowserSession',
    'CookieManager',
    'WindowManager',
    'ProxyManager',
    'BrowserConfig',
    'ProxyConfig',
    'StealthConfig',
]
