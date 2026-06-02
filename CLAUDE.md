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

**Request flow:** Tests → `requests` HTTP calls → external API → assertions on response status + JSON body.

**Key files:**
- `tests/test_demo.py` — class-based test suite (`TestDemo`); `BASE_URL` is hard-coded here
- `conftest.py` — root conftest, currently empty; intended for shared fixtures (base URL, session setup)
- `config/` — placeholder for environment/config management (not yet implemented)
- `data/` — placeholder for external test data files (not yet implemented)
- `report/` — auto-generated HTML + JSON reports from `pytest-html-reporter`

**pytest.ini** applies `-vs -rf --html-report=./report --title='PYTEST REPORT'` to every run automatically.

**CI/CD:** `.github/workflows/pytest.yml` runs on push/PR to `main` — sets up Python 3.10, installs deps, runs pytest, and uploads `report/` as a GitHub Actions artifact.

**Test target:** `https://jsonplaceholder.typicode.com` (public fake REST API).
