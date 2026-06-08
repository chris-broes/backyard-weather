#!/usr/bin/env python3
"""Executable Definition-of-Done grader for Task B (NWS API migration).

Emits a JSON object to stdout (per-criterion pass/fail, overall status, 0..1
score). Always exits 0: this grades, it does not gate.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXCLUDE_DIRS = {
    ".venv", "venv", ".git", "migrations", "__pycache__", "demo",
    ".pytest_cache", "instance", "node_modules", ".github",
}


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _source_files(exts: tuple[str, ...], subdir: str | None = None) -> list[Path]:
    base = REPO / subdir if subdir else REPO
    out: list[Path] = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith(exts):
                out.append(Path(root) / f)
    return out


def _matches(pattern: str, exts: tuple[str, ...], subdir: str | None = None) -> bool:
    rx = re.compile(pattern, re.IGNORECASE)
    return any(rx.search(_read(p)) for p in _source_files(exts, subdir))


def main() -> int:
    criteria = {
        # Uses the official NWS JSON API instead of HTML scraping.
        "uses_nws_api": _matches(r"api\.weather\.gov", (".py",)),
        # JSON parsing path present (response.json / requests for the API).
        "json_pipeline": _matches(
            r"\.json\(\)|requests\.get\([^)]*api\.weather\.gov", (".py",)
        ),
        # Legacy HTML scrape retained as a documented fallback.
        "fallback_retained": _matches(r"BeautifulSoup", (".py",)),
        # Tests exercise the new provider using recorded fixtures, not live network.
        "fixture_tests": (
            _matches(r"api\.weather\.gov", (".py",), subdir="tests")
            or bool(list((REPO / "tests").glob("**/*.json")))
            or (REPO / "tests" / "fixtures").is_dir()
        ),
        # Normalized fields preserved on the model path.
        "fields_normalized": _matches(
            r"temperature.*pressure|wind_speed|humidity", (".py",)
        ),
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
        "task": "task-b",
        "status": status,
        "score": score,
        "passed": passed,
        "total": total,
        "criteria": criteria,
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
