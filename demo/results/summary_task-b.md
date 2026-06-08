# Measurement summary — task-b

Baseline runs: 3  |  Droid runs: 3
Model: claude-opus-4.8  (same model, both arms)

| Metric | Baseline (mean) | Droid (mean) | Δ | Better |
|---|---|---|---|---|
| duration_sec | 514.33 | 494.0 | -20.33 | droid |
| human_turns | 0.0 | 0.0 | +0.0 | tie |
| ci_green_sec | — | — | — | — |
| dod_score | 1.0 | 1.0 | +0.0 | tie |
| tests_total | 16.67 | 39.0 | +22.33 | droid |
| tests_added | 13.67 | 36.0 | +22.33 | droid |
| tests_per_min | 1.79 | 4.4 | +2.61 | droid |
| coverage_pct | 80.89 | 88.84 | +7.95 | droid |
| coverage_delta | 13.1 | 21.05 | +7.95 | droid |
| coverage_per_min | 1.76 | 2.57 | +0.81 | droid |
| flake8_findings | 1.0 | 0.0 | -1.0 | droid |
| bandit_total | 0.0 | 0.0 | +0.0 | tie |
| pip_audit_vulns | — | — | — | — |
| codeql_alerts | — | — | — | — |
| review_total | 5.0 | 3.0 | -2.0 | droid |
| review_blocking | 0.0 | 0.0 | +0.0 | tie |
| pr_changed_files | — | — | — | — |

## Hypothesis check
- Speed: **Droid** faster by 4.0% on mean time-to-done (baseline n=3, droid n=3).
- Completeness: mean DoD score baseline=1.0 vs droid=1.0.

_Limitations: single repo, small N, one operator. Directional, reproducible._
