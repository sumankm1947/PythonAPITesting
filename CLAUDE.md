# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run a single test file
pytest tests/test_demo.py

# Run a single test by name
pytest tests/test_demo.py::TestDemo::test_get_post

# Run with explicit verbose output
pytest -vs
```

Reports are auto-generated to `./report/` on every run (configured in `pytest.ini`).

## Architecture

A **pytest-based REST API automation framework** built with Python + `requests`.

**Request flow:** Tests → `api_client_jsonplaceholder` fixture (`APIClient`) → `requests.Session` → external API → assertions on response status + JSON body.

**Key files:**
- `utils/api_client.py` — `APIClient` class; thin wrapper around `requests.Session`; handles base URL concatenation, default headers, and per-method request/response logging
- `tests/test_jsonplaceholder.py` — main test suite (`TestPlaceholder`); full CRUD coverage (GET, POST, PUT, PATCH, DELETE) using `api_client_jsonplaceholder` fixture
- `tests/test_demo.py` — legacy test suite (`TestDemo`); uses `base_url_jsonplaceholder` and `api_session` fixtures directly
- `conftest.py` — shared fixtures: `api_client_jsonplaceholder` (function-scoped `APIClient` with teardown), `base_url_jsonplaceholder`, `api_session` (session-scoped, kept for legacy tests), `logging.basicConfig`
- `config/config.py` — loads `.env` via `python-dotenv`, exposes `API_ENDPOINT_JSONPLACEHOLDER`
- `data/` — placeholder for external test data files (not yet implemented)
- `report/` — auto-generated HTML + JSON reports from `pytest-html-reporter`

**pytest.ini** applies `-vs -rf --html-report=./report --title='PYTEST REPORT'` to every run automatically.

**CI/CD:** `.github/workflows/pytest.yml` runs on push/PR to `main` — sets up Python 3.10, installs deps, runs pytest, and uploads `report/` as a GitHub Actions artifact.

**Test target:** `https://jsonplaceholder.typicode.com` (public fake REST API).
