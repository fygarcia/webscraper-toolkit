"""
Proxy management for browser automation.
"""

import logging
import os
from typing import Optional, Dict
from toolkit.core.browser.config import ProxyConfig


class ProxyManager:
    """
    Manages proxy configuration and setup for browser automation.
    
    Supports HTTP, SOCKS5, and Tor proxies.
    """
    
    def __init__(self, config: Optional[ProxyConfig] = None):
        """
        Initialize ProxyManager.
        
        Args:
            config: ProxyConfig instance with proxy settings
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.proxies: Optional[Dict[str, str]] = None
        
        if config and config.enabled:
            self._setup_proxies()
    
    def _setup_proxies(self):
        """Setup proxy configuration from config."""
        if not self.config or not self.config.enabled:
            return
        
        if self.config.type.lower() == "tor":
            self.proxies = {
                'http': 'socks5h://127.0.0.1:9150',
                'https': 'socks5h://127.0.0.1:9150'
            }
            self.logger.info("Tor proxy configured")
        elif self.config.type.lower() == "http":
            self.proxies = {
                'http': f"http://{self.config.address}",
                'https': f"https://{self.config.address}"
            }
            if self.config.username and self.config.password:
                self.proxies['http'] = f"http://{self.config.username}:{self.config.password}@{self.config.address}"
                self.proxies['https'] = f"https://{self.config.username}:{self.config.password}@{self.config.address}"
            self.logger.info(f"HTTP proxy configured: {self.config.address}")
        elif self.config.type.lower() == "socks5":
            self.proxies = {
                'http': f"socks5://{self.config.address}",
                'https': f"socks5://{self.config.address}"
            }
            self.logger.info(f"SOCKS5 proxy configured: {self.config.address}")
        else:
            self.logger.warning(f"Unknown proxy type: {self.config.type}")
    
    def get_proxy_arguments(self) -> list[str]:
        """
        Get Chrome arguments for proxy configuration.
        
        Returns:
            List of Chrome arguments for proxy setup
        """
        if not self.config or not self.config.enabled or not self.proxies:
            return []
        
        # For Chrome, we use --proxy-server argument
        # Use the HTTP proxy URL for Chrome argument
        proxy_url = self.proxies.get('http', '')
        
        if proxy_url.startswith('socks5'):
            # Convert socks5:// to socks5:// for Chrome
            proxy_server = proxy_url.replace('socks5h://', 'socks5://').replace('socks5://', 'socks5://')
            return [f'--proxy-server={proxy_server}']
        elif proxy_url.startswith('http'):
            return [f'--proxy-server={proxy_url}']
        else:
            return []
    
    def get_requests_proxies(self) -> Optional[Dict[str, str]]:
        """
        Get proxies dict for requests library.
        
        Returns:
            Dict with http/https proxy URLs or None
        """
        return self.proxies
    
    def detect_environment_proxy(self) -> bool:
        """
        Detect proxy settings from environment variables.
        
        Returns:
            True if proxy settings found in environment
        """
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
        
        for var in proxy_vars:
            if os.environ.get(var):
                self.logger.info(f"Detected proxy setting: {var}={os.environ.get(var)}")
                return True
        
        return False
    
    def is_enabled(self) -> bool:
        """
        Check if proxy is enabled.
        
        Returns:
            True if proxy is enabled and configured
        """
        return self.config is not None and self.config.enabled and self.proxies is not None

