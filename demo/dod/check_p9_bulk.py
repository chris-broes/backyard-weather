#!/usr/bin/env python3
"""DoD grader — Phase 9: bulk CSV scoring + underwriter report export."""
from _common import grader, matches


def criteria() -> dict[str, bool]:
    return {
        "upload_route": matches(r"@app\.route\([^)]*(upload|bulk|import|csv)"),
        "csv_processing": matches(r"import\s+csv|csv\.reader|csv\.DictReader|read_csv"),
        "export": matches(
            r"send_file|Content-Disposition|attachment|make_response[^)]*csv|\.pdf"
        ),
        "validation": matches(r"abort\(400|allowed_file|secure_filename"),
        "tests_exist": matches(r"csv|upload|bulk", (".py",), subdir="tests"),
    }


if __name__ == "__main__":
    grader("p9-bulk", criteria)
