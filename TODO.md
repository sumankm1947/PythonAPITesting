# API Framework TODO

## Phase 1 — Foundation
- [x] `config/config.py` — base URLs for all 3 APIs, reads from `.env` via `python-dotenv`
- [x] `conftest.py` — shared fixtures: `base_url_jsonplaceholder`, reusable `api_session` (session-scoped), logging setup
- [x] `utils/api_client.py` — thin wrapper around `requests` (handles headers, base URL, logging)

## Phase 2 — Test Quality
- [x] `data/` — JSON test data files (`data/schemas/`, `data/booking_payload.json`)
- [ ] `@pytest.mark.parametrize` — data-driven tests using the data files
- [x] Schema validation — `jsonschema` to assert response structure (`utils/data_loader.py` loads schemas from `data/schemas/`; applied to `test_get_post`)
- [x] Pytest markers — `@pytest.mark.smoke`, `@pytest.mark.regression`

## Phase 3 — Auth + Multi-API
- [x] Decision: use Restful-Booker over ReqRes (ReqRes token isn't enforced + now needs an API key; Restful-Booker actually rejects unauthenticated mutations)
- [x] Restful-Booker auth fixtures in `conftest.py` — `restful_booker_token` (session-scoped login → token), `api_session_restfulbooker` (authenticated `APIClient`), `created_booking` + `booking_payload` (setup fixtures)
- [x] `auth` marker registered in `pytest.ini`; `APIClient` extended to accept custom `headers`
- [x] Create booking test + negative-auth test (DELETE without token → `403`)
- [ ] Positive auth path — update/delete *with* token (note: Restful-Booker `DELETE` returns `201`)
- [ ] Full create → update → delete chain
