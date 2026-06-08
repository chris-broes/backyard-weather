# Measurement summary — task-a

Baseline runs: 1  |  Droid runs: 1

| Metric | Baseline (mean) | Droid (mean) | Δ | Better |
|---|---|---|---|---|
| duration_sec | 403.0 | 484.0 | +81.0 | baseline |
| human_turns | 0.0 | 0.0 | +0.0 | tie |
| ci_green_sec | — | — | — | — |
| dod_score | 1.0 | 1.0 | +0.0 | tie |
| tests_total | 9.0 | 19.0 | +10.0 | droid |
| tests_added | 6.0 | 16.0 | +10.0 | droid |
| tests_per_min | 0.89 | 1.98 | +1.09 | droid |
| coverage_pct | 74.03 | 82.15 | +8.12 | droid |
| coverage_delta | 6.24 | 14.36 | +8.12 | droid |
| coverage_per_min | 0.93 | 1.78 | +0.85 | droid |
| flake8_findings | 2.0 | 0.0 | -2.0 | droid |
| bandit_total | 0.0 | 0.0 | +0.0 | tie |
| pip_audit_vulns | — | — | — | — |
| codeql_alerts | — | — | — | — |
| review_total | — | — | — | — |
| review_blocking | — | — | — | — |
| pr_changed_files | — | — | — | — |

## Hypothesis check
- Speed: **Baseline** faster by 20.1% on mean time-to-done (baseline n=1, droid n=1).
- Completeness: mean DoD score baseline=1.0 vs droid=1.0.

_Limitations: single repo, small N, one operator. Directional, reproducible._
