# API Framework TODO

## Phase 1 — Foundation
- [x] `config/config.py` — base URLs for all 3 APIs, reads from `.env` via `python-dotenv`
- [x] `conftest.py` — shared fixtures: `base_url_jsonplaceholder`, reusable `api_session` (session-scoped), logging setup
- [x] `utils/api_client.py` — thin wrapper around `requests` (handles headers, base URL, logging)

## Phase 2 — Test Quality
- [ ] `data/` — JSON test data files
- [ ] `@pytest.mark.parametrize` — data-driven tests using the data files
- [x] Schema validation — `jsonschema` to assert response structure (`utils/data_loader.py` loads schemas from `data/schemas/`; applied to `test_get_post`)
- [x] Pytest markers — `@pytest.mark.smoke`, `@pytest.mark.regression`

## Phase 3 — Auth + Multi-API
- [ ] ReqRes API — login endpoint for token; add `auth` fixture in `conftest.py`
- [ ] Restful-Booker API — token-based auth, full CRUD workflow (create → update → delete)
