"""
Browser session management for web scraping.

Provides session state management, cookie handling, and requests.Session integration.
"""

import logging
import requests
from typing import Optional
from pathlib import Path
from selenium.webdriver.remote.webdriver import WebDriver

from toolkit.core.browser.controller import WebDriverController
from toolkit.core.browser.cookies import CookieManager


class BrowserSession:
    """
    Manages browser session state and cookies.
    
    Provides high-level session management including cookie persistence
    and integration with requests library for downloads.
    """
    
    def __init__(self, controller: WebDriverController):
        """
        Initialize BrowserSession.
        
        Args:
            controller: WebDriverController instance
        """
        self.controller = controller
        self.cookie_manager = CookieManager()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Update cookie manager when driver becomes available
        if controller.driver:
            self.cookie_manager.set_driver(controller.driver)
    
    def save_cookies(self, filepath: Path):
        """
        Save current session cookies to file.
        
        Args:
            filepath: Path to save cookies JSON file
        """
        if not self.controller.driver:
            self.logger.warning("Browser not started, cannot save cookies")
            return
        
        self.cookie_manager.set_driver(self.controller.driver)
        self.cookie_manager.save_cookies(filepath)
    
    def load_cookies(self, filepath: Path, domain: str):
        """
        Load cookies from file into browser session.
        
        Args:
            filepath: Path to cookies JSON file
            domain: Domain to navigate to before loading cookies
        """
        if not self.controller.driver:
            self.logger.warning("Browser not started, cannot load cookies")
            return
        
        self.cookie_manager.set_driver(self.controller.driver)
        self.cookie_manager.load_cookies(filepath, domain)
    
    def get_requests_session(self) -> requests.Session:
        """
        Get requests.Session with browser cookies and user agent.
        
        Returns:
            requests.Session configured with browser cookies
        """
        if not self.controller.driver:
            raise Exception("Browser is not started. Cannot get session.")
        
        session = requests.Session()
        
        # Get cookies from Selenium
        selenium_cookies = self.controller.driver.get_cookies()
        
        # Convert Selenium cookies to requests-compatible format
        for cookie in selenium_cookies:
            session.cookies.set(
                cookie['name'], 
                cookie['value'], 
                domain=cookie.get('domain')
            )
        
        # Set user-agent consistent with browser
        user_agent = self.controller.get_current_user_agent()
        if user_agent:
            session.headers.update({"User-Agent": user_agent})
        
        # Add proxy support if enabled
        if self.controller.proxy_manager and self.controller.proxy_manager.is_enabled():
            proxies = self.controller.proxy_manager.get_requests_proxies()
            if proxies:
                session.proxies.update(proxies)
        
        return session
    
    def get_cookies(self) -> list[dict]:
        """
        Get all cookies from current browser session.
        
        Returns:
            List of cookie dictionaries
        """
        if not self.controller.driver:
            return []
        
        return self.controller.driver.get_cookies()
    
    def delete_all_cookies(self):
        """Delete all cookies from current browser session."""
        if not self.controller.driver:
            return
        
        self.controller.driver.delete_all_cookies()
        self.logger.info("Deleted all cookies from session")

