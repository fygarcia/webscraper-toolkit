"""
WebDriver controller for browser automation.

Manages WebDriver lifecycle, initialization, and core browser operations.
"""

import os
import time
import socket
import multiprocessing
import threading
import random
import tempfile
import logging
from typing import Optional
from pathlib import Path

import undetected_chromedriver as uc
from selenium.webdriver.remote.webdriver import WebDriver

from toolkit.core.browser.config import BrowserConfig, StealthConfig
from toolkit.core.browser.window import WindowManager
from toolkit.core.browser.proxy import ProxyManager

# Enhanced features imports
try:
    from selenium_stealth import stealth
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False

try:
    from fake_useragent import UserAgent
    FAKE_USERAGENT_AVAILABLE = True
except ImportError:
    FAKE_USERAGENT_AVAILABLE = False


class WebDriverController:
    """
    Manages WebDriver lifecycle and core browser operations.
    
    Provides browser initialization, configuration management, and
    resource cleanup for web scraping automation.
    """
    
    # Class-level variables for ChromeDriver management
    _chromedriver_download_lock = None
    _chromedriver_initialized = False
    _cache_dir = None
    _dns_resolved = False
    
    def __init__(self, config: BrowserConfig):
        """
        Initialize WebDriverController.
        
        Args:
            config: BrowserConfig instance with browser settings
        """
        self.config = config
        self.driver: Optional[WebDriver] = None
        self.current_user_agent: Optional[str] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize window and proxy managers
        self.window_manager = WindowManager()
        self.proxy_manager = ProxyManager(config.proxy) if config.proxy else None
        
        # Initialize class-level variables
        self._initialize_class_variables()
        
        # Process-specific user data directory (will be set during start)
        self._user_data_dir: Optional[Path] = None
    
    @classmethod
    def _initialize_class_variables(cls):
        """Initialize class-level variables for ChromeDriver management."""
        if cls._chromedriver_download_lock is None:
            cls._chromedriver_download_lock = multiprocessing.Lock()
        
        if cls._cache_dir is None:
            cache_dir = Path.cwd() / 'chrome_cache'
            cache_dir.mkdir(exist_ok=True)
            cls._cache_dir = cache_dir
    
    def _pre_resolve_chromedriver_hosts(self):
        """Pre-resolve ChromeDriver hostnames to reduce DNS lookup time."""
        if WebDriverController._dns_resolved:
            return
        
        hosts = [
            'chromedriver.storage.googleapis.com',
            'storage.googleapis.com',
            'www.googleapis.com'
        ]
        
        self.logger.debug("Pre-resolving ChromeDriver hostnames...")
        for host in hosts:
            try:
                socket.gethostbyname(host)
            except socket.gaierror:
                pass
        
        WebDriverController._dns_resolved = True
        self.logger.debug("DNS pre-resolution completed")
    
    def _detect_environment_proxy(self) -> bool:
        """Detect proxy settings from environment variables."""
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
        
        for var in proxy_vars:
            if os.environ.get(var):
                self.logger.debug(f"Detected proxy setting: {var}")
                return True
        
        return False
    
    def _get_user_agent(self) -> str:
        """Generate or get user agent string."""
        if self.config.user_agent:
            if self.config.user_agent == "auto" or self.config.user_agent.lower() == "auto":
                # Auto-generate random user agent
                if FAKE_USERAGENT_AVAILABLE:
                    try:
                        ua = UserAgent()
                        return ua.random
                    except Exception as e:
                        self.logger.warning(f"Failed to generate random user agent: {e}")
                
                # Fallback to default
                return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            else:
                # Use provided user agent
                return self.config.user_agent
        
        # Default user agent
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    def _apply_stealth_mode(self):
        """Apply stealth mode using selenium-stealth."""
        if not self.config.stealth or not self.config.stealth.enabled:
            return
        
        if not STEALTH_AVAILABLE:
            self.logger.warning("selenium-stealth not available, skipping stealth mode")
            return
        
        try:
            stealth_config = self.config.stealth
            stealth(
                self.driver,
                languages=stealth_config.languages or ["en-US", "en"],
                vendor=stealth_config.vendor,
                platform=stealth_config.platform,
                webgl_vendor=stealth_config.webgl_vendor,
                renderer=stealth_config.renderer,
                fix_hairline=stealth_config.fix_hairline
            )
            self.logger.info("Stealth mode applied successfully")
        except Exception as e:
            self.logger.error(f"Failed to apply stealth mode: {e}")
    
    def _verify_driver_health(self) -> bool:
        """Verify that the driver is responsive and healthy."""
        if not self.driver:
            return False
        
        try:
            self.driver.execute_script('return "ok"')
            return True
        except Exception as e:
            self.logger.warning(f"Driver health check failed: {e}")
            return False
    
    def start(self, headless: Optional[bool] = None) -> WebDriver:
        """
        Initialize and start the browser.
        
        Args:
            headless: Override headless setting from config
            
        Returns:
            WebDriver instance
            
        Raises:
            Exception: If browser initialization fails
        """
        headless = headless if headless is not None else self.config.headless
        
        self.logger.info("Starting browser...")
        
        # Phase 1: Network optimizations
        self._pre_resolve_chromedriver_hosts()
        self._detect_environment_proxy()
        
        # Phase 2: ChromeDriver management
        if not WebDriverController._chromedriver_initialized:
            with WebDriverController._chromedriver_download_lock:
                if not WebDriverController._chromedriver_initialized:
                    try:
                        self.logger.debug("Pre-downloading ChromeDriver...")
                        patcher = uc.Patcher()
                        patcher.auto()
                        WebDriverController._chromedriver_initialized = True
                        self.logger.debug("ChromeDriver pre-download completed")
                    except Exception as e:
                        self.logger.warning(f"ChromeDriver pre-install failed: {e}")
        
        # Phase 3: Setup user data directory
        if self.config.user_data_dir:
            self._user_data_dir = Path(self.config.user_data_dir)
        else:
            # Create process-specific directory
            process_id = os.getpid()
            thread_id = threading.get_ident()
            random_port = random.randint(9222, 9999)
            temp_dir = Path(tempfile.gettempdir())
            self._user_data_dir = temp_dir / f"chrome_scraper_{process_id}_{thread_id}_{random_port}"
            self._user_data_dir.mkdir(parents=True, exist_ok=True)
        
        random_port = random.randint(9222, 9999)
        
        # Phase 4: Initialize WebDriver with retry logic
        retry = 0
        max_retries = 7
        base_delay = 1
        
        while retry <= max_retries:
            try:
                self.logger.debug(f"Initializing driver (attempt {retry + 1}/{max_retries + 1})...")
                
                if retry > 0:
                    delay = base_delay + random.uniform(0, 1)
                    time.sleep(delay)
                
                # Create ChromeOptions
                options = uc.ChromeOptions()
                options.headless = headless
                
                # Essential stability options
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-web-security")
                options.add_argument("--disable-features=VizDisplayCompositor")
                
                # Anti-detection options
                options.add_argument("--disable-blink-features=AutomationControlled")
                
                # User agent
                user_agent = self._get_user_agent()
                self.current_user_agent = user_agent
                options.add_argument(f"user-agent={user_agent}")
                
                # Proxy settings
                if self.proxy_manager and self.proxy_manager.is_enabled():
                    proxy_args = self.proxy_manager.get_proxy_arguments()
                    for arg in proxy_args:
                        options.add_argument(arg)
                
                # User data directory and debugging port
                options.add_argument(f"--user-data-dir={self._user_data_dir}")
                options.add_argument(f"--remote-debugging-port={random_port}")
                
                # Additional isolation options
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--disable-features=TranslateUI")
                options.add_argument("--disable-ipc-flooding-protection")
                options.add_argument("--disable-logging")
                options.add_argument("--disable-default-apps")
                options.add_argument("--disable-sync")
                options.add_argument("--disable-translate")
                options.add_argument("--disable-background-networking")
                options.add_argument("--disable-component-update")
                options.add_argument("--disable-domain-reliability")
                
                # Preferences
                prefs = {
                    "credentials_enable_service": False,
                    "profile.password_manager_enabled": False,
                    "translate": {"enabled": False},
                    "profile.default_content_setting_values": {
                        "notifications": 2,
                        "geolocation": 2,
                        "media_stream": 2,
                    }
                }
                options.add_experimental_option("prefs", prefs)
                
                # Initialize Chrome driver
                self.driver = uc.Chrome(
                    options=options,
                    use_subprocess=True,
                    no_sandbox=True,
                    suppress_welcome=True
                )
                
                # Setup window manager
                self.window_manager.set_driver(self.driver)
                
                # Apply stealth mode if configured
                self._apply_stealth_mode()
                
                # Set window size
                self.driver.set_window_size(*self.config.window_size)
                
                # Verify health
                if self._verify_driver_health():
                    self.logger.info("Browser started successfully")
                else:
                    self.logger.warning("Browser started but health check failed")
                
                break
                
            except Exception as e:
                retry += 1
                error_msg = str(e).lower()
                self.logger.warning(f"Browser initialization failed (attempt {retry}/{max_retries + 1}): {e}")
                
                if any(keyword in error_msg for keyword in [
                    "eof", "connection", "port", "address already in use",
                    "chrome", "driver", "browser", "initialization", "timeout"
                ]):
                    base_delay *= 2
                
                if retry > max_retries:
                    self.logger.error("Maximum retries exceeded")
                    raise Exception(f"Failed to start browser after {max_retries} retries: {e}")
        
        return self.driver
    
    def stop(self):
        """Stop browser and clean up resources."""
        if self.driver:
            try:
                # Check if driver is responsive
                _ = self.driver.current_url
                self.driver.quit()
                self.logger.info("Browser closed gracefully")
            except Exception as e:
                self.logger.warning(f"Browser was already closed or unresponsive: {e}")
            finally:
                self.driver = None
        
        # Cleanup user data directory if we created it
        if self._user_data_dir and self._user_data_dir.exists():
            try:
                import shutil
                shutil.rmtree(self._user_data_dir, ignore_errors=True)
                self.logger.debug(f"Cleaned up user data directory: {self._user_data_dir}")
            except Exception as e:
                self.logger.warning(f"Failed to cleanup user data directory: {e}")
    
    def is_active(self) -> bool:
        """
        Check if browser is running and responsive.
        
        Returns:
            True if browser is active, False otherwise
        """
        if not self.driver:
            return False
        
        try:
            _ = self.driver.current_url
            return True
        except Exception:
            return False
    
    def get_driver(self) -> Optional[WebDriver]:
        """
        Get the active WebDriver instance.
        
        Returns:
            WebDriver instance or None if not started
        """
        return self.driver
    
    def get_current_user_agent(self) -> Optional[str]:
        """
        Get the current user agent string.
        
        Returns:
            User agent string or None
        """
        return self.current_user_agent

