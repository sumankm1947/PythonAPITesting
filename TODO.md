# API Framework TODO

## Phase 1 — Foundation
- [ ] `config/config.py` — base URLs for all 3 APIs, reads from `.env` via `python-dotenv`
- [ ] `conftest.py` — shared fixtures: `base_url`, reusable `requests.Session`, setup/teardown
- [ ] `utils/api_client.py` — thin wrapper around `requests` (handles headers, base URL, logging)

## Phase 2 — Test Quality
- [ ] `data/` — JSON test data files
- [ ] `@pytest.mark.parametrize` — data-driven tests using the data files
- [ ] Schema validation — `jsonschema` to assert response structure
- [ ] Pytest markers — `@pytest.mark.smoke`, `@pytest.mark.regression`

## Phase 3 — Auth + Multi-API
- [ ] ReqRes API — login endpoint for token; add `auth` fixture in `conftest.py`
- [ ] Restful-Booker API — token-based auth, full CRUD workflow (create → update → delete)
