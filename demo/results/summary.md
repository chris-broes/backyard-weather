# Measurement summary

Baseline runs: 5  |  Droid runs: 5
Model: claude-opus-4.8  (same model, both arms)

| Metric | Baseline (mean) | Droid (mean) | Δ | Better |
|---|---|---|---|---|
| duration_sec | 402.2 | 401.4 | -0.8 | droid |
| human_turns | 0.0 | 0.0 | +0.0 | tie |
| ci_green_sec | — | — | — | — |
| dod_score | 1.0 | 1.0 | +0.0 | tie |
| tests_total | 14.2 | 29.6 | +15.4 | droid |
| tests_added | 11.2 | 26.6 | +15.4 | droid |
| tests_per_min | 2.91 | 5.67 | +2.76 | droid |
| coverage_pct | 78.32 | 84.72 | +6.4 | droid |
| coverage_delta | 10.53 | 16.93 | +6.4 | droid |
| coverage_per_min | 2.56 | 3.98 | +1.42 | droid |
| flake8_findings | 5.2 | 4.2 | -1.0 | droid |
| bandit_total | 0.0 | 0.0 | +0.0 | tie |
| pip_audit_vulns | — | — | — | — |
| codeql_alerts | — | — | — | — |
| review_total | 5.0 | 3.0 | -2.0 | droid |
| review_blocking | 0.0 | 0.0 | +0.0 | tie |
| pr_changed_files | — | — | — | — |

## Hypothesis check
- Speed: **Droid** faster by 0.2% on mean time-to-done (baseline n=5, droid n=5).
- Completeness: mean DoD score baseline=1.0 vs droid=1.0.

_Limitations: single repo, small N, one operator. Directional, reproducible._
