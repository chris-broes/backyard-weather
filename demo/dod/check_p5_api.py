#!/usr/bin/env python3
"""DoD grader — Phase 5: insurer REST API + API-key auth."""
from _common import grader, matches


def criteria() -> dict[str, bool]:
    return {
        "api_route": matches(r"@app\.route\(\s*['\"]/api"),
        "api_key_auth": matches(r"api[_-]?key|X-API-Key|Authorization|abort\(401"),
        "rate_limit": matches(r"rate.?limit|Limiter|RateLimit"),
        "api_contract": matches(r"/api/v\d|Blueprint|openapi|swagger"),
        "tests_exist": matches(r"/api|api[_-]?key|x-api-key", (".py",), subdir="tests"),
    }


if __name__ == "__main__":
    grader("p5-api", criteria)
