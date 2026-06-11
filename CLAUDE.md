# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working Mode

**This is a learning project — act as a teacher/guide, not an implementer.** The user (Suman) is learning API automation and writes the code himself. Do NOT write or edit code files unless explicitly asked. Instead:
- Explain concepts, trade-offs, and the "why" behind approaches.
- Point to what to change and where (file + general direction), then let the user implement it.
- Review the user's code after he writes it; suggest improvements aligned with standards.
- When asked to "check" something, review the existing implementation for correctness — don't rewrite it.

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
- `utils/api_client.py` — `APIClient` class; thin wrapper around `requests.Session`; handles base URL concatenation, per-method request/response logging, and an optional `headers` arg on construction (defaults to JSON `Content-Type`; used to inject the auth `Cookie` for Restful-Booker)
- `utils/data_loader.py` — `load_schema(name)` helper; reads a JSON schema from `data/schemas/<name>.json` (path anchored to project root via `pathlib`, UTF-8)
- `tests/test_jsonplaceholder.py` — JSONPlaceholder suite (`TestPlaceholder`); full CRUD coverage (GET, POST, PUT, PATCH, DELETE) using `api_client_jsonplaceholder` fixture; `test_get_post` also validates the response body against a JSON schema via `jsonschema.validate`
- `tests/test_restfulbooker.py` — Restful-Booker suite (`TestRestfulBooker`); token-auth tests — create booking, `PATCH` partial update (`test_patch_partial_update`), `DELETE` with token (`test_delete_booking`, asserts `201`), and a negative `DELETE`-without-token test asserting `403`. Together the create/patch/delete tests cover the full authenticated CRUD chain
- `tests/test_demo.py` — legacy test suite (`TestDemo`); uses `base_url_jsonplaceholder` and `api_session` fixtures directly
- `conftest.py` — shared fixtures: `api_client_jsonplaceholder` (function-scoped `APIClient` with teardown); Restful-Booker auth chain — `restful_booker_token` (session-scoped login → token), `api_session_restfulbooker` (authenticated `APIClient` with `Cookie: token=...`), `created_booking` (setup fixture returning a fresh `bookingid`), `booking_payload` (loads `data/booking_payload.json`); plus `base_url_jsonplaceholder`, `api_session` (legacy), `logging.basicConfig`
- `config/config.py` — loads `.env` via `python-dotenv`, exposes `API_ENDPOINT_JSONPLACEHOLDER` and `API_ENDPOINT_RESTFULBOOKER`
- `data/schemas/` — JSON Schema files used for response-structure validation (e.g. `post_jsonplaceholder.json`)
- `data/booking_payload.json` — shared Restful-Booker create-booking request body (sourced by both the create test and the `created_booking` fixture)
- `report/` — auto-generated HTML + JSON reports from `pytest-html-reporter`

**pytest.ini** applies `-vs -rf --strict-markers --html-report=./report --title='PYTEST REPORT'` to every run automatically, and registers the custom markers `smoke`, `regression`, and `auth`.

**CI/CD:** `.github/workflows/pytest.yml` runs on push/PR to `main` — sets up Python 3.10, installs deps, runs pytest, and uploads `report/` as a GitHub Actions artifact.

**Test targets:** `https://jsonplaceholder.typicode.com` (public fake REST API, no auth) and `https://restful-booker.herokuapp.com` (token-authenticated booking API).

## Learning Notes

Personal study notes for the concepts implemented in this framework. Kept here intentionally as living documentation.

### Guiding principle: tests must fail *loudly*

The single most important rule running through everything below: **a test should fail loudly when something is wrong, never pass quietly.** The worst possible outcome in test automation is a *green test that actually verified nothing* — it gives false confidence and hides real regressions. Every design choice below (raising on missing schemas, `--strict-markers`, explicit encoding) exists to favour a loud, obvious failure over a silent, misleading pass.

### JSON Schema validation (`jsonschema`)

**The problem it solves.** Asserting specific values (`response.json()["id"] == 1`) only confirms *this one record* looks right. It misses a whole class of contract regressions: a field renamed (`userId` → `user_id`), a type changing (`id` becoming the string `"1"`), a field disappearing, or an unexpected `null`. Checking every field's type by hand on every test is verbose and brittle.

**What JSON Schema is.** A vocabulary — written *as JSON* — for describing the **shape** of a JSON document: which fields exist, their types, and which are required. You write the contract once and validate any response against it.

```json
{
  "type": "object",
  "properties": {
    "userId": { "type": "integer" },
    "id":     { "type": "integer" },
    "title":  { "type": "string" },
    "body":   { "type": "string" }
  },
  "required": ["userId", "id", "title", "body"]
}
```

**How it's used here.** `jsonschema.validate(instance=response.json(), schema=...)` returns silently on a match and raises `ValidationError` (which fails the test, with a precise message like *"'userId' is a required property"*) on a mismatch. In `tests/test_jsonplaceholder.py`, validation is called **after** the status-code assertion — so a `404` fails as "wrong status", not as a confusing schema error about the error body.

**Value assertions vs. schema validation** — use both. Schema guards the *contract/structure*; value assertions confirm *business logic*. This is effectively **contract testing**.

**Key keywords:** `type` (`string`/`integer`/`number`/`boolean`/`object`/`array`/`null`), `properties`, `required`, `items` (schema each element of an **array** must satisfy — needed for list endpoints like `GET /posts`), `additionalProperties: false` (strict: reject any undeclared field — stricter but more brittle).

**Single object vs. array.** `/posts/1` returns an object → validate against an `object` schema. `/posts` returns a list → use `{"type": "array", "items": { <object schema> }}` so every element is checked.

### File encoding — why `encoding="utf-8"` is explicit

A file on disk is just **bytes**; an *encoding* is the rulebook mapping characters ↔ bytes. The same character maps to different bytes under different encodings (`é` is two bytes in UTF-8, one byte in Windows-1252).

`open()` **without** `encoding=` uses a **platform-dependent default**: Windows often defaults to `cp1252`, while Linux (and CI) defaults to UTF-8. That asymmetry is the bug — code behaves *differently across environments*, producing the classic "works on my machine" / "passes locally, fails in CI" trap, or mojibake/`UnicodeDecodeError` the moment a smart-quote, em-dash, accented name, or emoji appears in a data file.

**Rule:** always pass `encoding="utf-8"` explicitly when opening text files. UTF-8 is the universal standard — represents all Unicode, is ASCII-backward-compatible, and is the JSON spec default. (`utils/data_loader.py` follows this.) Related but separate: when *writing* JSON, `ensure_ascii=False` controls whether non-ASCII is escaped to `\uXXXX` vs. written raw — not needed for reading.

### `utils/data_loader.py` — robust path handling

Loading files by relative path (`open("data/schemas/x.json")`) resolves against the **current working directory** — wherever `pytest` happened to be launched — so it breaks when run from a subfolder or in CI. The fix is to anchor to the file's own location:

- `Path(__file__).resolve()` → absolute path to the module itself
- `.parent.parent` → walk up from `utils/` to the project root
- build the schema path from there (`SCHEMA_DIR / f"{schema_name}.json"`)

A missing schema file then raises `FileNotFoundError` naturally — a loud failure, consistent with the guiding principle. (An earlier version returned an empty `{}` schema for unknown names; an empty schema validates *anything*, so a typo'd name silently passed — exactly the false-positive to avoid.)

### Pytest markers (`smoke`, `regression`)

**What a marker is.** A label on a test (`@pytest.mark.smoke`). It carries no behaviour by itself — it just **tags** the test so groups can be *selected*, *skipped*, or treated differently.

**Why.** Run subsets at different cadences: `smoke` = a tiny, fast critical-path subset (run on every commit/PR for quick feedback); `regression` = the full, slower suite (run nightly / pre-release). Same code, two speeds — keeps CI fast without losing coverage. A test can carry multiple markers (stacked decorators); smoke tests are typically also tagged `regression` since smoke is a subset of the full run.

**Selecting:** `pytest -m smoke`, `pytest -m "smoke or regression"`, `pytest -m "regression and not smoke"`.

**The division of labour** (the key mental model):

| Piece | Job |
|---|---|
| `@pytest.mark.smoke` (decorator, in test file) | **Tags** the test |
| `pytest -m smoke` (CLI flag) | **Selects** tagged tests |
| `pytest.ini` `markers =` section | **Declares** the name is legit + description |

Registration in `pytest.ini` does **not** tag tests or enable selection (those work without it) — it is a *safety net and documentation*. Unregistered markers otherwise emit `PytestUnknownMarkWarning`, and a typo (`@pytest.mark.smoek`) is silently accepted as a brand-new marker, so `pytest -m smoke` would quietly skip that test — a silent coverage hole.

**`--strict-markers`** (set in `pytest.ini`) upgrades unregistered markers from a warning to a hard **error** at collection time — so a mistyped tag fails the run immediately instead of silently mis-tagging. This is the "fail loud" principle applied to markers, and is recommended for any real suite.

**Verify:** `pytest -m smoke` (runs only smoke), `pytest --markers` (lists registered markers with descriptions).

### Token authentication & the `auth` fixture chain (Restful-Booker)

**The flow.** Token auth is a two-step dance: (1) `POST /auth` with credentials → server returns a `token`; (2) send that token on every *protected* request. Restful-Booker expects it as a `Cookie: token=<token>` header (other APIs use `Authorization: Bearer <token>` — same idea, different header). Mutations (`PUT`/`DELETE`) require it; `POST /booking` (create) does not.

**Why a fixture, and why session scope.** A fixture logs in **once** and hands tests a ready token, so every test doesn't re-authenticate. `restful_booker_token` is `scope="session"` because the token stays valid for the whole run — logging in once is faster and the token is read-only shared state (safe to share). Function scope would re-login per test, slower for no benefit here.

**Two-layer design (separation of concerns):**
- `restful_booker_token` — *gets credentials*: logs in, returns the raw token string.
- `api_session_restfulbooker` — *gets an authenticated client*: depends on the token fixture, returns an `APIClient` with `Cookie: token=...` already baked into its session. Tests just call methods; the token attaches itself.

This mirrors real frameworks (separate "obtain credentials" from "build authed client") and keeps the raw token reusable for negative tests.

**The negative test is the point.** The single most valuable auth assertion is `DELETE /booking/{id}` with an **unauthenticated** client → assert **`403`**. It proves auth is actually *enforced*, not just that login returns a string. (ReqRes was rejected as a target precisely because its token isn't enforced on anything — you could never write this test.) Pair it with a positive test (same call *with* token → success) for the with/without contrast — here `test_delete_booking` (with token → `201`) is the positive twin of `test_delete_booking_withouttoken` (no token → `403`).

**Response-shape gotcha — create vs. update nest differently.** `POST /booking` wraps its result: `{"bookingid": N, "booking": {...}}`, so the create test reads `response.json()["booking"]["firstname"]`. But `PATCH /booking/{id}` returns the **updated booking object directly** at the top level: `{"firstname": ..., "lastname": ..., ...}`, so `test_patch_partial_update` reads `response.json()["firstname"]` (no `["booking"]`). Same API, two different envelopes — always check the actual response body rather than assuming one shape.

**The CRUD chain.** create (`test_post_createbooking`) → update (`test_patch_partial_update`) → delete (`test_delete_booking`) together exercise the full authenticated lifecycle, each test self-contained via the `created_booking` fixture (no cross-test ordering). A stronger variant of a mutation test adds a **follow-up read** to confirm the side effect actually persisted — PATCH then `GET` asserting the new value, DELETE then `GET` asserting `404` — "trust but verify": don't trust the mutation endpoint's own echo, confirm with an independent read.

**Setup fixtures vs. tests under test.** `created_booking` (creates a booking, returns its `bookingid`) and the create *test* both call `POST /booking` — that is **not** duplication to eliminate. The test's job is to *verify* creation (it asserts); the fixture's job is to *arrange* a precondition for delete/update (it doesn't assert). Different intent. What *is* worth de-duplicating is the request *data* — hence `data/booking_payload.json`, sourced by both. General rule: test code tolerates more duplication than production code (favour explicit, self-contained tests), but centralise shared *data*.

**Sharing state across tests — use fixtures, not class attributes.** pytest instantiates a **fresh instance of the test class for every test method**, so `self.x = ...` set in one test is gone in the next (the read silently falls back to the class attribute). A `created_booking` fixture is the correct way to pass a created id into a later test — it also removes the hidden ordering dependency (each test can run in isolation).