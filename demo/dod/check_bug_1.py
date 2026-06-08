#!/usr/bin/env python3
"""DoD grader — seeded-bug triage & fix (support workflow).

Unlike the structural graders, this one is behavioral: it confirms a regression
test exists and now passes, and that the suite is green (no regression). The seed
(buggy code + failing regression test) is described in the phase spec.
"""
from __future__ import annotations

import subprocess
import sys

from _common import REPO, emit, source_files

PY = sys.executable


def _regression_paths() -> list[str]:
    paths = []
    for p in source_files((".py",), subdir="tests"):
        name = p.name.lower()
        if "regression" in name or "bug" in name:
            paths.append(str(p))
    return paths


def _pytest_ok(args: list[str]) -> bool:
    try:
        r = subprocess.run(
            [PY, "-m", "pytest", "-q", *args],
            cwd=str(REPO), capture_output=True, text=True, timeout=240,
        )
        return r.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def criteria() -> dict[str, bool]:
    reg = _regression_paths()
    return {
        "regression_test_present": bool(reg),
        "regression_test_passes": bool(reg) and _pytest_ok(reg),
        "suite_green": _pytest_ok([]),
    }


if __name__ == "__main__":
    sys.exit(emit("bug-1", criteria()))
