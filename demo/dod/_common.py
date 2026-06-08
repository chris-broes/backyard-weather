"""Shared helpers for Definition-of-Done graders.

Graders are heuristic structural checks: they confirm the *shape* of a phase's
work exists in the tree (modules, routes, fields, tests). They are intentionally
lightweight proxies — the harness's objective metrics (tests, coverage, bandit,
CodeQL, CI) carry the quality signal. Each grader prints one JSON object and
always exits 0.
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


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def source_files(exts: tuple[str, ...], subdir: str | None = None) -> list[Path]:
    base = REPO / subdir if subdir else REPO
    out: list[Path] = []
    if not base.exists():
        return out
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith(exts):
                out.append(Path(root) / f)
    return out


def matches(pattern: str, exts: tuple[str, ...] = (".py",), subdir: str | None = None) -> bool:
    rx = re.compile(pattern, re.IGNORECASE)
    return any(rx.search(read(p)) for p in source_files(exts, subdir))


def emit(task: str, criteria: dict[str, bool]) -> int:
    passed = sum(1 for v in criteria.values() if v)
    total = len(criteria)
    score = round(passed / total, 3) if total else 0.0
    status = "full" if passed == total else ("none" if passed == 0 else "partial")
    print(json.dumps({
        "task": task,
        "status": status,
        "score": score,
        "passed": passed,
        "total": total,
        "criteria": criteria,
    }))
    return 0


def grader(task: str, criteria_fn) -> None:
    """Run a criteria function (returns dict[str,bool]) and emit the result."""
    sys.exit(emit(task, criteria_fn()))
