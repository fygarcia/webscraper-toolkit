"""
Base handler class for website-specific scrapers.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Iterator, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

from toolkit.pipeline.item import ScrapedItem


class AbstractHandler(ABC):
    """
    Abstract base class for all website handlers.
    
    Provides common browser interaction utilities and defines the handler interface
    for site-specific scrapers.
    """
    
    def __init__(self, driver: WebDriver, source_name: str):
        """
        Initialize AbstractHandler.
        
        Args:
            driver: Selenium WebDriver instance
            source_name: Source identifier (e.g., 'site1', 'scraper_name')
        """
        self.driver = driver
        self.source_name = source_name
        self.logger = logging.getLogger(f"{self.__class__.__name__}:{source_name}")
        self.cookie_accepted = False
    
    @abstractmethod
    def scrape_main_page(self) -> Iterator[ScrapedItem]:
        """
        Scrape the main page and yield ScrapedItem objects.
        
        This method must be implemented by all subclasses.
        
        Yields:
            ScrapedItem instances
        """
        raise NotImplementedError
    
    def get_url(self, url: str, wait_for_load: bool = True):
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            wait_for_load: Whether to wait for page load
        """
        try:
            self.logger.debug(f"Navigating to URL: {url}")
            self.driver.get(url)
            if wait_for_load:
                self.wait_page_load()
        except Exception as e:
            self.logger.error(f"Error navigating to URL {url}: {e}", exc_info=True)
    
    def get_soup(self) -> BeautifulSoup:
        """
        Get BeautifulSoup object for current page.
        
        Returns:
            BeautifulSoup instance
        """
        return BeautifulSoup(self.driver.page_source, 'html.parser')
    
    def is_element_xpath_present(self, element_xpath: str, timeout: int = 10) -> bool:
        """
        Check if element is present using XPath.
        
        Args:
            element_xpath: XPath selector
            timeout: Timeout in seconds
            
        Returns:
            True if element is present and clickable
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, element_xpath))
            )
            self.logger.debug(f"Element found by XPath: {element_xpath}")
            return True
        except TimeoutException:
            self.logger.debug(f"Element not found by XPath within {timeout}s: {element_xpath}")
            return False
    
    def is_element_css_present(self, element_css: str, timeout: int = 10) -> bool:
        """
        Check if element is present using CSS selector.
        
        Args:
            element_css: CSS selector
            timeout: Timeout in seconds
            
        Returns:
            True if element is present and clickable
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, element_css))
            )
            self.logger.debug(f"Element found by CSS: {element_css}")
            return True
        except TimeoutException:
            self.logger.debug(f"Element not found by CSS within {timeout}s: {element_css}")
            return False
    
    def click_element_css(self, element_css: str, timeout: int = 10) -> bool:
        """
        Find and click element using CSS selector.
        
        Args:
            element_css: CSS selector
            timeout: Timeout in seconds
            
        Returns:
            True if element was clicked successfully
        """
        if not element_css:
            self.logger.warning("No element_css provided to click_element_css.")
            return False
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, element_css))
            )
            self.logger.debug(f"Clicking element with CSS: {element_css}")
            element.click()
            return True
        except TimeoutException:
            self.logger.error(f"Could not find or click element with CSS '{element_css}' within {timeout}s.")
            return False
        except Exception as e:
            self.logger.error(f"Error clicking element with CSS '{element_css}': {e}")
            return False
    
    def wait_page_load(self, timeout: int = 30):
        """
        Wait for page to load completely.
        
        Args:
            timeout: Timeout in seconds
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
        except TimeoutException:
            self.logger.warning(f"Page load timeout after {timeout}s")
    
    def scroll_down(self, pixels: int = 500):
        """
        Scroll down the page.
        
        Args:
            pixels: Number of pixels to scroll
        """
        self.driver.execute_script(f"window.scrollBy(0, {pixels});")
        time.sleep(0.5)  # Give time for content to load
    
    def is_external_url(self, url: str, base_domain: str) -> bool:
        """
        Check if URL is external to the base domain.
        
        Args:
            url: URL to check
            base_domain: Base domain (e.g., 'example.com')
            
        Returns:
            True if URL is external
        """
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc != '' and base_domain not in parsed.netloc
    
    def save_page_html(self, filename: str):
        """
        Save current page HTML to file for debugging.
        
        Args:
            filename: Path to save HTML file
        """
        if not self.driver:
            self.logger.warning("Browser is not open. Cannot save page HTML.")
            return
        
        html_content = self.driver.page_source
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        self.logger.info(f"Saved page HTML to '{filename}'")

