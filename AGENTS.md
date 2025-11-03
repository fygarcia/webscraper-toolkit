## Project overview

This repository hosts a generic, reusable web scraping toolkit designed to be copied into new scraping projects with minimal changes. It includes:

- **Browser automation**: Selenium controller, sessions, cookies, window, proxy, stealth mode
- **Download manager**: Robust file downloader with strategies and retry policy
- **Logging system**: Centralized logging, session tracking, performance monitor
- **Database utilities**: SQLAlchemy session/ORM base, repository and unit-of-work patterns
- **Pipeline framework**: ETL-style processing with orchestrator and shared context
- **Handler framework**: Base classes and utilities for site-specific scrapers

See `README.md` and `CREATION_SUMMARY.md` for detailed features and examples.

## Repository layout

```
core/
  browser/    # WebDriver controller, session, cookies, window, proxy, config
  download/   # Downloader, path manager, strategies, types, config
  database/   # DB manager, models base, repository, config
  logging/    # Logging manager, handlers, session tracker, performance monitor
pipeline/     # Base pipeline, context, item, orchestrator, exceptions
handlers/     # Abstract handler and utilities for site scrapers
requirements.txt
```

## Getting started (humans and agents)

- **Python version**: 3.10+
- **Install deps**:
  ```bash
  python -m venv .venv && .venv/Scripts/activate  # Windows
  pip install -r requirements.txt
  ```
- **Local run (examples)**: Use snippets in `README.md` under Quick Start to spin up browser, create handlers, and execute pipelines.
- **Where to add code**:
  - New site scraper: extend `handlers/base.py` and `handlers/utils.py`
  - New pipeline stage: add a class extending `pipeline/base.py`
  - Download/Storage behavior: add a new strategy in `core/download/strategies.py`
  - Logging/metrics: configure via `core/logging/config.py` and `core/logging/manager.py`

## Build, lint, and test

- **Lint (PEP8/type hints encouraged)**: Use `ruff`/`flake8` locally if installed; otherwise ensure code is formatted and typed.
- **Run tests** (when present):
  ```bash
  pytest -q
  ```
- **Type check** (optional):
  ```bash
  mypy .
  ```

Note: This toolkit ships without a test suite yet. When adding features, include unit tests under `tests/` using `pytest`.

## Coding conventions

- **Language**: Python, PEP8; use type hints across public APIs
- **Naming**: camelCase for functions/methods/variables, PascalCase for classes, snake_case for files/dirs, UPPER_CASE for env vars
- **Structure**: Prefer small, modular classes/functions; avoid files >300 LOC
- **Control flow**: Use guard clauses; avoid deep nesting; only catch exceptions with real handling
- **Comments**: Keep concise; only for non-obvious rationale and invariants
- **Config over constants**: Avoid hard-coded values; use configuration dataclasses or environment variables

## Scraping guidelines

- **Browser**: Use `core/browser/controller.py` (`WebDriverController`) and `BrowserSession` for cookie persistence
- **Stealth/Proxies**: Configure via `core/browser/config.py` and `core/browser/proxy.py`
- **Politeness**: Implement waits and backoffs; respect robots and rate limits where applicable
- **Parsing**: Prefer robust selectors; use `handlers/utils.py` helpers for URL and name validation
- **Downloads**: Use `core/download/downloader.py` with `StoragePathManager` for consistent paths

## Database usage

- Use `core/database/manager.py` to obtain sessions
- Extend `core/database/models.py` for ORM models
- Prefer `core/database/repository.py` and Unit of Work for transactional operations

## Logging and observability

- Configure via `core/logging/config.py` and initialize `LoggingManager`
- Use `SessionTracker` and `PerformanceMonitor` for session metrics and timing

## Security and secrets

- Do not commit credentials or cookies
- Use environment variables for secrets and endpoints; never overwrite `.env` without confirmation
- Apply least-privilege for DB connections and network access

## Contribution workflow

- Branching: feature branches off `master`
- Commits: concise, imperative, scoped to one concern
- Before PRs: run linters/tests locally; update `README.md` examples if APIs change
- Keep changes focused; avoid introducing new patterns/tech unless necessary; remove old logic if replaced

## Testing guidelines

- Write `pytest` unit tests for major functionality (handlers, pipelines, download strategies)
- Mock external services (network, browser) in tests only; never in dev/prod paths
- Ensure deterministic tests (no live web unless explicitly marked and isolated)

## For AI coding agents

- Prefer editing existing modules over creating new ones; follow current patterns
- Do not touch unrelated code; think through cross-module impacts
- When adding a feature:
  - Update or add tests
  - Update docs (this file or `README.md`) if public API changes
  - Avoid duplication; reuse utilities in `handlers/utils.py`, `pipeline/`, `core/*`
- After making code changes that affect runtime behavior, ensure any local runner or example script is restarted cleanly and that no stale browser sessions are left running

## Example development flows

- **Add a new site handler**:
  1) Create a subclass of `handlers/base.py` `AbstractHandler`
  2) Implement scraping generators that yield `pipeline/item.py` `ScrapedItem`
  3) Compose pipelines in `pipeline/orchestrator.py` and execute
  4) Use `core/download` for files and `core/logging` for observability

- **Add a new pipeline stage**:
  1) Subclass `pipeline/base.py` `AbstractPipeline`
  2) Implement `process_item`
  3) Register in `PipelineOrchestrator`

## Support and docs

- Start with `README.md` Quick Start for code snippets
- Consult `CREATION_SUMMARY.md` for the architecture map and module inventory
- Module-level docstrings include API details

## License

This toolkit is for personal use. Copy and modify as needed for your projects.