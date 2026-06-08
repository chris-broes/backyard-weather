#!/usr/bin/env python3
"""Executable Definition-of-Done grader for Task A (risk-scoring feature).

Emits a JSON object to stdout describing per-criterion pass/fail, an overall
status (full | partial | none) and a 0..1 score. Always exits 0: this grades,
it does not gate.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _any_file_matches(pattern: str, globs: list[str]) -> bool:
    rx = re.compile(pattern, re.IGNORECASE)
    for g in globs:
        for p in REPO.glob(g):
            if p.is_file() and rx.search(_read(p)):
                return True
    return False


def _importable_scorer() -> bool:
    """A hyphen-free module exposing a callable risk-scoring function."""
    candidates = [
        REPO / "risk_scoring.py",
        REPO / "risk_scoring" / "__init__.py",
    ]
    for path in candidates:
        if not path.exists():
            continue
        spec = importlib.util.spec_from_file_location("_rs_probe", path)
        if not spec or not spec.loader:
            continue
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
        except Exception:
            continue
        for name in dir(mod):
            obj = getattr(mod, name)
            if callable(obj) and "risk" in name.lower() and "score" in name.lower():
                return True
    return False


def _scoring_behaves() -> bool:
    """The scorer returns a number and ranks a harsh day above a mild one."""
    path = REPO / "risk_scoring.py"
    if not path.exists():
        path = REPO / "risk_scoring" / "__init__.py"
    if not path.exists():
        return False
    spec = importlib.util.spec_from_file_location("_rs_probe2", path)
    if not spec or not spec.loader:
        return False
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    except Exception:
        return False
    fn = None
    for name in dir(mod):
        obj = getattr(mod, name)
        if callable(obj) and "risk" in name.lower() and "score" in name.lower():
            fn = obj
            break
    if fn is None:
        return False
    try:
        harsh = fn(-5, 90, 30)
        mild = fn(22, 45, 5)
    except Exception:
        return False
    return isinstance(harsh, (int, float)) and isinstance(mild, (int, float)) and harsh > mild


def _endpoint_or_field() -> bool:
    """A risk endpoint exists, or the model/route exposes a risk attribute."""
    app_src = _read(REPO / "app.py")
    if re.search(r"@app\.route\(\s*['\"][^'\"]*risk", app_src, re.IGNORECASE):
        return True
    if re.search(r"risk[_a-z]*\s*=\s*db\.Column", app_src, re.IGNORECASE):
        return True
    return bool(re.search(r"risk_score|risk_band|calculate_risk", app_src, re.IGNORECASE))


def _surfaced_in_ui() -> bool:
    return _any_file_matches(r"risk", ["templates/*.html"])


def _tests_exist() -> bool:
    return _any_file_matches(r"risk", ["tests/*.py"])


def main() -> int:
    criteria = {
        "importable_module": _importable_scorer(),
        "scoring_behaves": _scoring_behaves(),
        "endpoint_or_field": _endpoint_or_field(),
        "surfaced_in_ui": _surfaced_in_ui(),
        "tests_exist": _tests_exist(),
    }
    passed = sum(1 for v in criteria.values() if v)
    total = len(criteria)
    score = round(passed / total, 3) if total else 0.0
    if passed == total:
        status = "full"
    elif passed == 0:
        status = "none"
    else:
        status = "partial"
    print(json.dumps({
        "task": "task-a",
        "status": status,
        "score": score,
        "passed": passed,
        "total": total,
        "criteria": criteria,
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
