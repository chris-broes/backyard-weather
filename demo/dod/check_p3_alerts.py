#!/usr/bin/env python3
"""DoD grader — Phase 3: severe-weather (NWS) alerts integration."""
from _common import grader, matches


def criteria() -> dict[str, bool]:
    return {
        "alerts_api": matches(r"weather\.gov/alerts|/alerts/active"),
        "alerts_in_scoring": matches(r"\balert"),
        "alerts_event_fields": matches(r"messageType|\"event\"|NWSheadline|effective\b|expires\b"),
        "alerts_ui": matches(r"alert", (".html",), subdir="templates"),
        "tests_exist": matches(r"alert", (".py",), subdir="tests"),
    }


if __name__ == "__main__":
    grader("p3-alerts", criteria)
