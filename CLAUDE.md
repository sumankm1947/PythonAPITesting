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
- `utils/api_client.py` — `APIClient` class; thin wrapper around `requests.Session`; handles base URL concatenation, default headers, and per-method request/response logging
- `utils/data_loader.py` — `load_schema(name)` helper; reads a JSON schema from `data/schemas/<name>.json` (path anchored to project root via `pathlib`, UTF-8)
- `tests/test_jsonplaceholder.py` — main test suite (`TestPlaceholder`); full CRUD coverage (GET, POST, PUT, PATCH, DELETE) using `api_client_jsonplaceholder` fixture; `test_get_post` also validates the response body against a JSON schema via `jsonschema.validate`
- `tests/test_demo.py` — legacy test suite (`TestDemo`); uses `base_url_jsonplaceholder` and `api_session` fixtures directly
- `conftest.py` — shared fixtures: `api_client_jsonplaceholder` (function-scoped `APIClient` with teardown), `base_url_jsonplaceholder`, `api_session` (session-scoped, kept for legacy tests), `logging.basicConfig`
- `config/config.py` — loads `.env` via `python-dotenv`, exposes `API_ENDPOINT_JSONPLACEHOLDER`
- `data/schemas/` — JSON Schema files used for response-structure validation (e.g. `post_jsonplaceholder.json`)
- `report/` — auto-generated HTML + JSON reports from `pytest-html-reporter`

**pytest.ini** applies `-vs -rf --strict-markers --html-report=./report --title='PYTEST REPORT'` to every run automatically, and registers the custom markers `smoke` and `regression`.

**CI/CD:** `.github/workflows/pytest.yml` runs on push/PR to `main` — sets up Python 3.10, installs deps, runs pytest, and uploads `report/` as a GitHub Actions artifact.

**Test target:** `https://jsonplaceholder.typicode.com` (public fake REST API).

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
