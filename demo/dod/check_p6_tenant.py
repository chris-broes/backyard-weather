#!/usr/bin/env python3
"""DoD grader — Phase 6: multi-tenant accounts & data isolation."""
from _common import grader, matches


def criteria() -> dict[str, bool]:
    return {
        "user_model": matches(r"class\s+(User|Account)\b"),
        "auth": matches(r"login_required|flask_login|login_user|check_password"),
        "tenant_scope": matches(r"account_id|user_id\s*=\s*db\.Column|owner_id|tenant_id"),
        "password_hash": matches(r"generate_password_hash|bcrypt|werkzeug\.security|pbkdf2"),
        "tests_exist": matches(
            r"login|account|tenant|isolation|unauthor", (".py",), subdir="tests"
        ),
    }


if __name__ == "__main__":
    grader("p6-tenant", criteria)
