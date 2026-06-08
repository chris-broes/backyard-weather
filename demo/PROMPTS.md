# Frozen prompt pack — identical input for both arms

Hand the **exact** prompt below to whichever agent is running the phase
(Droid or the baseline/Copilot arm). Rules that keep the comparison fair:

- Paste **verbatim**. Do not edit a prompt between the two arms.
- **Same underlying model on both arms** (Claude Opus 4.8), so the comparison
  isolates the tool/agent, not the LLM. Keep this constant across all runs.
- Start the harness clock (`measure.py start`) **immediately before** pasting.
- Don't add hints mid-run; if you must intervene, log it with `measure.py turn`.
- Acceptance criteria here mirror the frozen DoD in `PROGRAM.md`; the graders in
  `demo/dod/` are the executable contract.

Task-id ↔ prompt mapping matches the phase registry in `PROGRAM.md`.

---

## task-a — Risk-scoring core  *(already run; included for the record)*
```
Finish the weather risk-scoring capability in this Flask app. Definition of done:
- Move the scoring logic into an importable, hyphen-free module with type hints and docstrings.
- Validate inputs; handle missing/out-of-range values explicitly (no crashes).
- Compute a risk score and a human-readable band (Low/Moderate/High) for each weather entry.
- Surface the score+band in the UI (index page) AND expose it via a JSON endpoint.
- Add unit tests for the scoring bands and edge cases, plus a functional test asserting the score renders.
- pytest must pass, flake8 clean, no new security findings.
- Produce a single, reviewable change.
```

---

## task-b — NWS JSON API migration
```
Migrate the weather data pipeline from HTML scraping to the official NWS JSON API. Definition of done:
- Add a provider abstraction that fetches current conditions from api.weather.gov (JSON).
- Keep the existing HTML-scrape path as a documented fallback.
- Normalize fields to the existing model: temperature °F, pressure inHg, wind speed mph, wind direction (compass), humidity %.
- Tests must use recorded fixtures (no live network in tests); demonstrate behavior parity with the previous pipeline.
- pytest must pass, flake8 clean, no new security findings.
- Produce a single, reviewable change.
```

---

## p2-multiloc — Multi-location portfolio
```
Add multi-location portfolio support so an insurer can track many properties. Definition of done:
- Add a Location model (name plus lat/lon, or NWS zone/station).
- Provide ways to add and list locations.
- Parameterize the weather fetch by location; remove the hardcoded San Francisco lat/lon/station.
- Compute and display a risk score per location.
- Add tests covering multiple locations.
- pytest must pass, flake8 clean, no new security findings.
- Produce a single, reviewable change.
```

---

## p3-alerts — Severe-weather alerts integration
```
Integrate active NWS weather alerts into the risk score. Definition of done:
- Fetch active alerts from api.weather.gov/alerts for a location.
- Factor active alerts into the risk score with a clear, documented contribution.
- Surface alerts in the UI; parse alert event, severity, and expiry.
- Add fixture-based tests (no live network).
- pytest must pass, flake8 clean, no new security findings.
- Produce a single, reviewable change.
```

---

## p4-riskmodel — Configurable risk model + factors
```
Make the risk model configurable and extensible. Definition of done:
- Externalize scoring weights and bands to configuration (no inline magic literals).
- Add at least one new factor (e.g., precipitation, wind gust, or active alerts).
- Add a model version constant.
- Keep existing scoring behavior covered by tests; add tests for the new factor(s) and config loading.
- pytest must pass, flake8 clean, no new security findings.
- Produce a single, reviewable change.
```

---

## p5-api — Insurer REST API + API-key auth
```
Add an insurer-facing REST API. Definition of done:
- Versioned JSON endpoints under /api/v1/ that return risk data.
- API-key authentication via request header; return 401 on missing/invalid keys.
- Basic rate limiting.
- Tests for both authorized and unauthorized access.
- pytest must pass, flake8 clean, no new security findings.
- Produce a single, reviewable change.
```

---

## p6-tenant — Multi-tenant accounts & isolation
```
Add multi-tenant accounts with strict data isolation. Definition of done:
- Add a User/Account model with hashed passwords and login.
- Scope all weather/location data per account (foreign key); require auth on data routes.
- Add an isolation test proving one account cannot read another account's data.
- pytest must pass, flake8 clean, no new security findings.
- Produce a single, reviewable change.
```

---

## p7-postgres — SQLite → Postgres + migrations
```
Migrate persistence from SQLite to PostgreSQL. Definition of done:
- The app boots against Postgres via DATABASE_URL; add psycopg to requirements.
- Provide Alembic migration(s) for the current schema, with documented run steps.
- The test suite stays green (SQLite is acceptable in CI).
- Produce a single, reviewable change.
```

---

## p8-security — Security hardening pass
```
Perform a security hardening pass. Definition of done:
- Add an SSRF guard (host allowlist) so outbound weather fetches can only reach weather.gov / api.weather.gov.
- Add security headers; ensure CSRF protection is on; validate user-supplied input.
- bandit reports 0 medium/high findings (resolve or explicitly justify any remaining).
- Add security regression tests.
- pytest must pass, flake8 clean.
- Produce a single, reviewable change.
```

---

## p9-bulk — Bulk CSV scoring + report export
```
Add bulk scoring and report export for underwriters. Definition of done:
- Add an upload endpoint that scores a portfolio CSV; validate the upload (use secure_filename).
- Export results as a downloadable CSV (and/or PDF) with proper download headers.
- Add tests using a sample CSV.
- pytest must pass, flake8 clean, no new security findings.
- Produce a single, reviewable change.
```

---

## bug-1 — Seeded-bug ticket (support workflow)
```
Bug report: negative temperatures are being recorded as positive values — a reported -5°F is stored as 5.
The test tests/test_regression_bug1.py captures the expected behavior and is currently failing.
Find and fix the root cause (do not just edit the test). Definition of done:
- tests/test_regression_bug1.py passes and the full suite is green.
- The fix addresses the underlying cause, with no unrelated scope creep.
- Produce a single, reviewable change.
```
