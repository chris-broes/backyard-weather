#!/usr/bin/env python3
"""DoD grader — Phase 7: SQLite -> Postgres + migrations.

Note: the discriminating signal is the Postgres driver; DATABASE_URL support and
the migrations dir already exist at base. Real "boots on Postgres" verification
is a manual/CI step (see spec).
"""
from _common import grader, matches, REPO


def criteria() -> dict[str, bool]:
    versions = REPO / "migrations" / "versions"
    return {
        "pg_driver": matches(r"psycopg", (".txt",)),
        "database_url_config": matches(r"DATABASE_URL", (".py",)),
        "migrations_present": versions.is_dir() and bool(list(versions.glob("*.py"))),
        "postgres_referenced": matches(
            r"postgres", (".py", ".yml", ".yaml", ".md", ".toml")
        ),
        "tests_or_docs": matches(r"postgres|psycopg", (".py", ".md"), subdir="tests")
        or matches(r"postgres", (".md",)),
    }


if __name__ == "__main__":
    grader("p7-postgres", criteria)
