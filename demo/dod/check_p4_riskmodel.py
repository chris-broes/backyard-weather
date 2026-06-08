#!/usr/bin/env python3
"""DoD grader — Phase 4: configurable risk model + new factors."""
from _common import grader, matches


def criteria() -> dict[str, bool]:
    return {
        "config_externalized": matches(
            r"RISK_WEIGHTS|WEIGHTS\s*=|risk_config|load_weights|RISK_CONFIG"
        ),
        "configurable_bands": matches(r"BANDS\b|bands\s*=|THRESHOLDS|thresholds\s*="),
        "new_factor": matches(r"precip|precipitation|uv_index|visibility|gust|alert"),
        "model_versioned": matches(r"MODEL_VERSION|RISK_VERSION|model_version"),
        "tests_exist": matches(r"weight|factor|\bband\b|precip", (".py",), subdir="tests"),
    }


if __name__ == "__main__":
    grader("p4-riskmodel", criteria)
