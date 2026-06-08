#!/usr/bin/env python3
"""DoD grader — Phase 2: multi-location portfolio."""
from _common import grader, matches


def criteria() -> dict[str, bool]:
    return {
        "location_model": matches(r"class\s+Location\b|Location\(db\.Model\)"),
        "location_route": matches(r"@app\.route\([^)]*location|/locations?\b"),
        "parameterized_fetch": (
            matches(r"get_weather\([^)]*lat")
            or matches(r"location\.(lat|latitude|station|lon|longitude)")
            or matches(r"def\s+get_weather\(\s*\w")
        ),
        "per_location_ui": matches(r"location", (".html",), subdir="templates"),
        "tests_exist": matches(r"location", (".py",), subdir="tests"),
    }


if __name__ == "__main__":
    grader("p2-multiloc", criteria)
