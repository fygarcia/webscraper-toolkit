# Personal Web Scraping Toolkit

A generic, reusable toolkit for web scraping projects. This toolkit provides browser automation, file downloads, pipeline framework, handlers, and utilities that can be copied into any new scraping project.

## Features

- **Browser Automation**: Selenium-based browser management with stealth mode and proxy support
- **File Downloads**: Robust file downloading with retry logic and path management
- **Pipeline Framework**: ETL pipeline pattern for data processing
- **Handler Framework**: Base classes for building site-specific scrapers
- **Database Utilities**: ORM helpers and repository patterns
- **Logging & Monitoring**: Centralized logging with session tracking
- **Configuration Management**: YAML/JSON-based configuration system

## Installation

Copy the `toolkit/` folder to your new project and install dependencies:

```bash
pip install -r toolkit/requirements.txt
```

## Quick Start

### Browser Automation

```python
from toolkit.core.browser import WebDriverController, BrowserConfig, BrowserSession, StealthConfig

# Configure browser
config = BrowserConfig(
    headless=True,
    user_agent="auto",  # Auto-generate random user agent
    stealth=StealthConfig(enabled=True)
)

# Start browser
controller = WebDriverController(config)
controller.start()

# Create session for cookie management
session = BrowserSession(controller)
session.save_cookies(Path("cookies.json"))

# Get driver
driver = controller.get_driver()
```

### File Downloads

```python
from toolkit.core.download import FileDownloader, DownloadConfig, StoragePathManager, ContentType

# Configure downloader
config = DownloadConfig(timeout=30, chunk_size=8192)
downloader = FileDownloader(config)

# Setup path manager
path_manager = StoragePathManager("downloads", strategy="source_type")

# Download file
content_dir = path_manager.get_content_dir("site1", ContentType.IMAGE)
destination = content_dir / "image.jpg"
success = downloader.download("https://example.com/image.jpg", destination)
```

### Pipeline Framework

```python
from toolkit.pipeline import AbstractPipeline, PipelineOrchestrator, ScrapedItem, PipelineContext
from toolkit.pipeline.exceptions import DropItem

# Create custom pipeline stage
class CustomPipeline(AbstractPipeline):
    def process_item(self, item: ScrapedItem):
        # Your processing logic
        if not item.name:
            raise DropItem("Missing name")
        # Transform item
        item.metadata['processed'] = True
        return item

# Build and execute pipeline
context = PipelineContext(session_id="session_123")
orchestrator = PipelineOrchestrator([CustomPipeline()], context=context)
processed_items = orchestrator.execute(scraped_items_iterator)
```

### Handler Framework

```python
from toolkit.handlers import AbstractHandler
from toolkit.pipeline.item import ScrapedItem

class MySiteHandler(AbstractHandler):
    def scrape_main_page(self):
        self.get_url("https://example.com/listings")
        soup = self.get_soup()
        
        for element in soup.find_all("div", class_="listing"):
            item = ScrapedItem(
                source="mysite",
                name=element.find("h2").text,
                detail_url=element.find("a")["href"]
            )
            yield item
```

## Toolkit Structure

```
toolkit/
├── core/              # Core infrastructure
│   ├── browser/      # Browser automation
│   │   ├── controller.py    # WebDriverController
│   │   ├── session.py       # BrowserSession
│   │   ├── cookies.py       # CookieManager
│   │   ├── window.py        # WindowManager
│   │   ├── proxy.py         # ProxyManager
│   │   └── config.py        # BrowserConfig, ProxyConfig, StealthConfig
│   ├── download/     # File downloads
│   │   ├── downloader.py    # FileDownloader
│   │   ├── path_manager.py  # StoragePathManager
│   │   ├── strategies.py    # DownloadStrategy, HTTPDownloadStrategy
│   │   ├── config.py        # DownloadConfig, RetryPolicy
│   │   └── types.py         # ContentType enum
│   ├── database/     # Database utilities
│   │   ├── manager.py       # DatabaseManager
│   │   ├── repository.py    # Repository, UnitOfWork
│   │   ├── models.py        # ModelBase
│   │   └── config.py        # DatabaseConfig
│   └── logging/      # Logging system
│       ├── manager.py       # LoggingManager
│       ├── handlers.py      # DatabaseHandler, UTCFormatter
│       ├── session.py       # SessionTracker
│       ├── monitor.py       # PerformanceMonitor
│       └── config.py        # LogConfig, HandlerConfig
├── pipeline/          # Pipeline framework
│   ├── base.py            # AbstractPipeline
│   ├── item.py            # ScrapedItem
│   ├── context.py         # PipelineContext
│   ├── orchestrator.py    # PipelineOrchestrator
│   └── exceptions.py      # DropItem, PipelineError
├── handlers/          # Handler framework
│   ├── base.py            # AbstractHandler
│   └── utils.py           # URLValidator, NameValidator
└── requirements.txt   # Dependencies
```

## Important API Notes

- **Logging**: `LogLevel` must be imported from `toolkit.core.logging.config`, not `toolkit.core.logging`
- **Repository Pattern**: Use `repository.add()` to create entities, not `create()`
- **UnitOfWork**: Use `uow.get_repository(ModelClass)` to get repositories
- **PerformanceMonitor**: Use `get_summary()` to retrieve statistics, not `get_statistics()`

## Testing

The toolkit includes two types of tests:

### 1. Pytest Unit Tests (`tests/` directory)

Fast, isolated unit tests using mocking to avoid actual browser launches or network calls:

```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_browser_automation.py

# Skip end-to-end tests
pytest -m "not e2e"
```

**Test Coverage:**
- `test_browser_automation.py` - Browser controller and session (with mocked WebDriver)
- `test_handler_framework.py` - Handler base class and scraping logic
- `test_pipeline_framework.py` - Pipeline orchestrator and stages
- `test_file_downloads.py` - File downloader with strategy pattern

**How they work:**
- Use pytest fixtures (`conftest.py`) for common test objects
- Mock external dependencies (browsers, network) to test logic in isolation
- Fast execution without real browser launches
- Ideal for CI/CD pipelines

### 2. Integration Test Notebook (`test.ipynb`)

Comprehensive integration tests that actually run all toolkit components:

```bash
# Open in Jupyter (notebook is in toolkit/ folder)
cd toolkit
jupyter notebook test.ipynb

# Or from project root
jupyter notebook toolkit/test.ipynb
```

**Test Coverage:**
- ✅ Browser Management - Real browser automation, sessions, cookies, windows
- ✅ Handler Framework - Scraping with real websites, utilities
- ✅ Pipeline Framework - Full pipeline execution with context
- ✅ Download Management - Real file downloads with path management
- ✅ Logging System - LoggingManager, SessionTracker, PerformanceMonitor
- ✅ Database & ORM - SQLite database operations, Repository, UnitOfWork

**How it works:**
- Runs cells sequentially to test each module
- Uses real components (browsers, databases, file system)
- Provides interactive testing and debugging
- Great for manual verification and learning the toolkit

**Running the notebook:**
1. Start Jupyter from project root: `jupyter notebook toolkit/test.ipynb`
2. Or navigate to toolkit folder: `cd toolkit && jupyter notebook test.ipynb`
3. Run cells sequentially (or "Run All")
4. Each section tests a different module with real components
5. The notebook automatically detects the project root for imports

## Documentation

See individual module docstrings for detailed API documentation.

## License

This toolkit is for personal use. Copy and modify as needed for your projects.

