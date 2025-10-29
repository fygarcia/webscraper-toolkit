"""
Cookie management for browser automation.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver


class CookieManager:
    """
    Manages cookies for browser sessions.
    
    Provides save/load functionality for persistent cookie storage.
    """
    
    def __init__(self, driver: Optional[WebDriver] = None):
        """
        Initialize CookieManager.
        
        Args:
            driver: Optional WebDriver instance. Can be set later via set_driver().
        """
        self.driver: Optional[WebDriver] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if driver:
            self.set_driver(driver)
    
    def set_driver(self, driver: WebDriver):
        """
        Set the WebDriver instance.
        
        Args:
            driver: WebDriver instance
        """
        self.driver = driver
    
    def save_cookies(self, filepath: Path):
        """
        Save cookies from current browser session to a JSON file.
        
        Args:
            filepath: Path to save cookies file
        """
        if not self.driver:
            self.logger.warning("No driver available for cookie management")
            return
        
        try:
            cookies = self.driver.get_cookies()
            
            # Ensure directory exists
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Save cookies to file
            with open(filepath, 'w') as f:
                json.dump(cookies, f, indent=2)
            
            self.logger.info(f"Saved {len(cookies)} cookies to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save cookies: {e}")
    
    def load_cookies(self, filepath: Path, domain: str):
        """
        Load cookies from JSON file into browser session.
        
        Args:
            filepath: Path to cookies JSON file
            domain: Domain to navigate to before loading cookies
        """
        if not self.driver:
            self.logger.warning("No driver available for cookie management")
            return
        
        filepath = Path(filepath)
        
        if not filepath.exists():
            self.logger.warning(f"Cookies file not found: {filepath}")
            return
        
        try:
            # Load cookies from file
            with open(filepath, 'r') as f:
                cookies = json.load(f)
            
            # Navigate to domain (required for adding cookies)
            self.logger.info(f"Navigating to {domain} to add cookies...")
            self.driver.get(domain)
            
            # Clear existing cookies
            self.driver.delete_all_cookies()
            self.logger.debug("Cleared all existing cookies")
            
            # Add cookies
            added_count = 0
            for cookie in cookies:
                try:
                    if 'name' in cookie and 'value' in cookie:
                        # Remove 'domain' field to avoid domain mismatch
                        simplified_cookie = {
                            k: v for k, v in cookie.items() 
                            if k != 'domain'
                        }
                        
                        # Filter to allowed keys only
                        allowed_keys = {
                            'name', 'value', 'path', 'secure', 
                            'httpOnly', 'sameSite', 'expiry'
                        }
                        simplified_cookie = {
                            k: v for k, v in simplified_cookie.items() 
                            if k in allowed_keys
                        }
                        
                        self.driver.add_cookie(simplified_cookie)
                        added_count += 1
                    else:
                        self.logger.warning(f"Skipping invalid cookie: {cookie}")
                except Exception as e:
                    self.logger.warning(f"Failed to add cookie {cookie.get('name', 'unknown')}: {e}")
            
            # Refresh page to apply cookies
            self.driver.refresh()
            self.logger.info(f"Loaded {added_count} cookies from {filepath}")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON from {filepath}: {e}")
        except Exception as e:
            self.logger.error(f"Error loading cookies: {e}")
    
    def get_cookies(self) -> list[dict]:
        """
        Get all cookies from current browser session.
        
        Returns:
            List of cookie dictionaries
        """
        if not self.driver:
            self.logger.warning("No driver available")
            return []
        
        try:
            return self.driver.get_cookies()
        except Exception as e:
            self.logger.error(f"Error getting cookies: {e}")
            return []
    
    def delete_all_cookies(self):
        """Delete all cookies from current browser session."""
        if not self.driver:
            self.logger.warning("No driver available")
            return
        
        try:
            self.driver.delete_all_cookies()
            self.logger.info("Deleted all cookies")
        except Exception as e:
            self.logger.error(f"Error deleting cookies: {e}")

