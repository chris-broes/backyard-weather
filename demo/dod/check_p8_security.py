#!/usr/bin/env python3
"""DoD grader — Phase 8: security hardening pass.

Structural proxies only. The real success signal for this phase is the harness's
objective metrics: bandit_total (target 0 medium/high) and codeql_alerts (->0).
"""
from _common import grader, matches


def criteria() -> dict[str, bool]:
    return {
        "ssrf_guard": matches(r"allowed_hosts|allowlist|ALLOWED_DOMAINS|urlparse|netloc"),
        "security_headers": matches(
            r"Strict-Transport-Security|X-Content-Type-Options|X-Frame-Options|after_request"
        ),
        "csrf_or_validation": matches(r"CSRFProtect|validate_csrf|abort\(40|raise\s+ValueError"),
        "rate_limit": matches(r"rate.?limit|Limiter|RateLimit"),
        "security_tests": matches(
            r"security|ssrf|header|csrf|\b401\b|\b403\b", (".py",), subdir="tests"
        ),
    }


if __name__ == "__main__":
    grader("p8-security", criteria)
