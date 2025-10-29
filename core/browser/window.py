"""
Window and tab management utilities for WebDriver.
"""

import logging
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchWindowException


class WindowManager:
    """
    Manages browser window and tab operations.
    
    Provides utilities for window switching, closing extra windows,
    and maintaining window state.
    """
    
    def __init__(self, driver: Optional[WebDriver] = None):
        """
        Initialize WindowManager.
        
        Args:
            driver: Optional WebDriver instance. Can be set later via set_driver().
        """
        self.driver: Optional[WebDriver] = None
        self.original_handle: Optional[str] = None
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
        if driver and driver.window_handles:
            self.original_handle = driver.window_handles[0]
    
    def get_original_handle(self) -> Optional[str]:
        """
        Get the original window handle.
        
        Returns:
            Original window handle or None if not set
        """
        return self.original_handle
    
    def ensure_active(self) -> bool:
        """
        Ensure the original window is active.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            self.logger.warning("No driver available for window management")
            return False
        
        try:
            if self.original_handle and self.original_handle in self.driver.window_handles:
                self.driver.switch_to.window(self.original_handle)
                return True
            elif self.driver.window_handles:
                # Original window is gone, use first available
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.original_handle = self.driver.window_handles[0]
                return True
            else:
                self.logger.error("No windows available")
                return False
        except NoSuchWindowException as e:
            self.logger.error(f"Window no longer exists: {e}")
            return False
    
    def close_extra_windows(self) -> int:
        """
        Close all windows except the original one.
        
        Returns:
            Number of windows closed
        """
        if not self.driver:
            self.logger.warning("No driver available")
            return 0
        
        if not self.original_handle:
            return 0
        
        closed_count = 0
        try:
            current_handles = self.driver.window_handles
            
            for handle in current_handles:
                if handle != self.original_handle:
                    try:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                        closed_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to close window {handle}: {e}")
            
            # Switch back to original window
            self.ensure_active()
            
            if closed_count > 0:
                self.logger.info(f"Closed {closed_count} extra window(s)")
            
        except Exception as e:
            self.logger.error(f"Error closing extra windows: {e}")
        
        return closed_count
    
    def get_window_count(self) -> int:
        """
        Get the number of open windows/tabs.
        
        Returns:
            Number of windows, or 0 if driver not available
        """
        if not self.driver:
            return 0
        
        try:
            return len(self.driver.window_handles)
        except Exception:
            return 0
    
    def is_original_window_active(self) -> bool:
        """
        Check if the original window is currently active.
        
        Returns:
            True if original window is active, False otherwise
        """
        if not self.driver or not self.original_handle:
            return False
        
        try:
            return self.driver.current_window_handle == self.original_handle
        except Exception:
            return False
