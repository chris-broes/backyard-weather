#!/usr/bin/env python3
"""python_weather demo measurement harness.

Two arms (`baseline` vs `droid`), many samples per arm. Each run is a JSON
record under demo/results/runs/. Timing/turns are operator-triggered; quality,
security, coverage and Definition-of-Done are auto-collected. `aggregate`
computes per-arm summary statistics and a head-to-head verdict so the
hypothesis (Droid is faster / more complete) can be validated across samples.

Usage (one-shot):
  python demo/measure.py snapshot-base
  python demo/measure.py start --arm droid --task task-a
  python demo/measure.py turn                 # log a human intervention
  python demo/measure.py stop
  python demo/measure.py collect              # auto-metrics for current run
  python demo/measure.py aggregate            # summary + verdict

Usage (interactive, avoids retyping the python path):
  python demo/measure.py shell                # or just `python demo/measure.py`
  measure[@branch]> start --arm droid --task task-a
  measure[...]> stop
  measure[...]> collect --skip-audit
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import statistics
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "demo" / "results"
RUNS = RESULTS / "runs"
CURRENT = RESULTS / ".current"
BASE_SNAPSHOT = RESULTS / ".base_metrics.json"
DOD_DIR = Path(__file__).resolve().parent / "dod"
PY = sys.executable

# Lower-is-better metrics; everything else treats higher as better.
LOWER_IS_BETTER = {
    "duration_sec",
    "ci_green_sec",
    "human_turns",
    "flake8_findings",
    "bandit_total",
    "pip_audit_vulns",
    "codeql_alerts",
    "review_total",
    "review_blocking",
}


# --------------------------------------------------------------------------- io
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_dirs() -> None:
    RUNS.mkdir(parents=True, exist_ok=True)


def _run_path(run_id: str) -> Path:
    return RUNS / f"{run_id}.json"


def _load_run(run_id: str) -> dict[str, Any]:
    return json.loads(_run_path(run_id).read_text(encoding="utf-8"))


def _save_run(rec: dict[str, Any]) -> None:
    _run_path(rec["run_id"]).write_text(json.dumps(rec, indent=2), encoding="utf-8")


def _current_run_id() -> Optional[str]:
    if CURRENT.exists():
        rid = CURRENT.read_text(encoding="utf-8").strip()
        return rid or None
    return None


def _latest_run_id() -> Optional[str]:
    runs = sorted(RUNS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return runs[0].stem if runs else None


def _resolve_run_id(arg: Optional[str]) -> str:
    rid = arg or _current_run_id() or _latest_run_id()
    if not rid:
        sys.exit("No run specified and none found. Use --run or `start` first.")
    if not _run_path(rid).exists():
        sys.exit(f"Run '{rid}' not found under {RUNS}.")
    return rid


def _next_run_id(arm: str, task: str) -> str:
    n = 1 + sum(
        1 for p in RUNS.glob(f"{arm}_{task}_*.json") if p.is_file()
    )
    return f"{arm}_{task}_{n:02d}"


# ------------------------------------------------------------------ collectors
def _sh(cmd: list[str], timeout: int = 240) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd, cwd=str(REPO), capture_output=True, text=True, timeout=timeout
        )
        return p.returncode, p.stdout, p.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return 127, "", str(exc)


def _collect_pytest_cov() -> tuple[Optional[int], Optional[float]]:
    """Return (tests_total, coverage_percent). None on failure."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        cov_json = tmp.name
    try:
        _sh([
            PY, "-m", "pytest", "-q",
            "--cov=.", f"--cov-report=json:{cov_json}",
            "--cov-config=/dev/null",
        ])
        coverage = None
        try:
            data = json.loads(Path(cov_json).read_text(encoding="utf-8"))
            coverage = round(float(data["totals"]["percent_covered"]), 2)
        except (OSError, KeyError, ValueError):
            coverage = None
    finally:
        try:
            os.unlink(cov_json)
        except OSError:
            pass

    rc, out, _ = _sh([PY, "-m", "pytest", "--collect-only", "-q"])
    tests_total = None
    if rc in (0, 1):
        tests_total = sum(1 for line in out.splitlines() if "::" in line)
        if tests_total == 0:
            for line in out.splitlines():
                if "tests collected" in line or "test collected" in line:
                    tests_total = int(line.strip().split()[0])
                    break
    return tests_total, coverage


def _collect_flake8() -> Optional[int]:
    rc, out, err = _sh([
        PY, "-m", "flake8", ".", "--count",
        "--max-line-length=127", "--extend-exclude=.venv,migrations,demo",
    ])
    if rc == 127:
        return None
    tail = (out + err).strip().splitlines()
    for line in reversed(tail):
        line = line.strip()
        if line.isdigit():
            return int(line)
    return 0


def _collect_bandit() -> Optional[dict[str, int]]:
    rc, out, _ = _sh([
        PY, "-m", "bandit", "-r", ".", "-f", "json",
        "-x", "./.venv,./tests,./migrations,./demo",
    ])
    if rc == 127 or not out.strip():
        return None
    try:
        data = json.loads(out)
    except ValueError:
        return None
    sev = {"high": 0, "medium": 0, "low": 0}
    for r in data.get("results", []):
        s = str(r.get("issue_severity", "")).lower()
        if s in sev:
            sev[s] += 1
    sev["total"] = sev["high"] + sev["medium"] + sev["low"]
    return sev


def _collect_pip_audit(timeout: int = 120) -> Optional[int]:
    rc, out, _ = _sh([PY, "-m", "pip_audit", "-f", "json"], timeout=timeout)
    if rc == 127 or not out.strip():
        return None
    try:
        data = json.loads(out)
    except ValueError:
        return None
    deps = data.get("dependencies", data) if isinstance(data, dict) else data
    if isinstance(deps, list):
        return sum(len(d.get("vulns", [])) for d in deps)
    return None


def _collect_dod(task: Optional[str]) -> Optional[dict[str, Any]]:
    if not task:
        return None
    safe = task.replace("-", "_")
    checker = DOD_DIR / f"check_{safe}.py"
    if not checker.exists():
        return None
    rc, out, _ = _sh([PY, str(checker)])
    try:
        return json.loads(out)
    except ValueError:
        return None


def _gh_repo() -> Optional[str]:
    rc, out, _ = _sh(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"])
    return out.strip() if rc == 0 and out.strip() else None


def _collect_ci(branch: str) -> Optional[dict[str, Any]]:
    """GitHub Actions outcome + time-to-green for a branch (best-effort)."""
    rc, out, _ = _sh([
        "gh", "run", "list", "--branch", branch, "--limit", "20",
        "--json", "status,conclusion,createdAt,updatedAt,workflowName",
    ])
    if rc != 0 or not out.strip():
        return None
    try:
        runs = json.loads(out)
    except ValueError:
        return None
    conclusion = next((r.get("conclusion") for r in runs if r.get("conclusion")), None)
    green_sec = None
    for r in runs:
        if r.get("conclusion") == "success":
            try:
                start = datetime.fromisoformat(r["createdAt"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(r["updatedAt"].replace("Z", "+00:00"))
                green_sec = int((end - start).total_seconds())
                break
            except (KeyError, ValueError):
                pass
    return {"conclusion": conclusion, "green_sec": green_sec, "runs": len(runs)}


def _collect_codeql(branch: str) -> Optional[dict[str, Any]]:
    """Open code-scanning (CodeQL) alerts for a branch ref (best-effort)."""
    repo = _gh_repo()
    if not repo:
        return None
    rc, out, _ = _sh([
        "gh", "api", "--paginate",
        f"/repos/{repo}/code-scanning/alerts?ref=refs/heads/{branch}&state=open&per_page=100",
    ])
    if rc != 0 or not out.strip():
        return None
    try:
        alerts = json.loads(out)
    except ValueError:
        return None
    if not isinstance(alerts, list):
        return None
    sev = {"critical": 0, "high": 0, "medium": 0, "low": 0, "warning": 0, "note": 0, "error": 0}
    for a in alerts:
        rule = a.get("rule", {}) or {}
        level = (rule.get("security_severity_level") or rule.get("severity") or "").lower()
        if level in sev:
            sev[level] += 1
    sev["total"] = len(alerts)
    return sev


def _collect_pr(branch: str) -> Optional[dict[str, Any]]:
    """PR outcome + diff size + check rollup for a branch (best-effort)."""
    rc, out, _ = _sh([
        "gh", "pr", "view", branch, "--json",
        "number,state,reviewDecision,statusCheckRollup,additions,deletions,changedFiles",
    ])
    if rc != 0 or not out.strip():
        return None
    try:
        pr = json.loads(out)
    except ValueError:
        return None
    rollup = pr.get("statusCheckRollup") or []
    failed = sum(
        1 for c in rollup
        if str(c.get("conclusion") or c.get("state")).upper()
        in ("FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED")
    )
    return {
        "number": pr.get("number"),
        "state": pr.get("state"),
        "review_decision": pr.get("reviewDecision"),
        "additions": pr.get("additions"),
        "deletions": pr.get("deletions"),
        "changed_files": pr.get("changedFiles"),
        "checks_failed": failed,
    }


def _merge_ci_metrics(metrics: dict[str, Any], branch: str) -> None:
    ci = _collect_ci(branch)
    codeql = _collect_codeql(branch)
    pr = _collect_pr(branch)
    metrics["ci_conclusion"] = (ci or {}).get("conclusion")
    metrics["ci_green_sec"] = (ci or {}).get("green_sec")
    metrics["codeql_alerts"] = (codeql or {}).get("total")
    metrics["codeql_breakdown"] = codeql
    metrics["pr_number"] = (pr or {}).get("number")
    metrics["pr_changed_files"] = (pr or {}).get("changed_files")
    metrics["pr_additions"] = (pr or {}).get("additions")
    metrics["pr_deletions"] = (pr or {}).get("deletions")
    metrics["pr_review_decision"] = (pr or {}).get("review_decision")
    metrics["pr_checks_failed"] = (pr or {}).get("checks_failed")


# ---------------------------------------------------------------- subcommands
def cmd_snapshot_base(args: argparse.Namespace) -> None:
    _ensure_dirs()
    tests_total, coverage = _collect_pytest_cov()
    snap = {
        "captured_at": _now(),
        "tests_total": tests_total,
        "coverage_pct": coverage,
    }
    BASE_SNAPSHOT.write_text(json.dumps(snap, indent=2), encoding="utf-8")
    print(f"Base snapshot saved: tests={tests_total} coverage={coverage}%")


def _git(*args: str) -> tuple[int, str]:
    rc, out, _ = _sh(["git", *args])
    return rc, out.strip()


_SHARED_BRANCH_RE = re.compile(r"^(track-|demo-base$|main$|master$|.*-base$)")


def _preflight_warnings(intended_branch: str) -> list[str]:
    """Non-blocking checks to catch wrong-branch / dirty-tree run starts."""
    warns: list[str] = []
    rc, cur = _git("rev-parse", "--abbrev-ref", "HEAD")
    if rc == 0 and cur:
        if cur != intended_branch:
            warns.append(
                f"current git branch is '{cur}' but this run records branch "
                f"'{intended_branch}'. Are you on the right branch?"
            )
        if _SHARED_BRANCH_RE.match(cur):
            warns.append(
                f"'{cur}' looks like a shared/base branch — create a per-run branch "
                f"first (git switch -c <arm>/<task>/run-NN <track>) so work is isolated."
            )
    rc, out = _git(
        "status", "--porcelain", "--", ".",
        ":(exclude)demo", ":(exclude)AGENTS.md", ":(exclude).factory",
    )
    if rc == 0 and out:
        warns.append(
            "working tree has uncommitted product changes — runs should start from a "
            "clean branch. Dirty paths:\n    " + "\n    ".join(out.splitlines()[:8])
        )
    return warns


def cmd_start(args: argparse.Namespace) -> None:
    _ensure_dirs()
    arm, task = args.arm, args.task
    run_id = _next_run_id(arm, task)
    branch = args.branch or f"{arm}/{task}/run-{run_id.split('_')[-1]}"
    rec = {
        "run_id": run_id,
        "arm": arm,
        "task": task,
        "branch": branch,
        "base": "demo-base",
        "model": args.model,
        "operator": args.operator or os.environ.get("USER", "unknown"),
        "started_at": _now(),
        "ended_at": None,
        "duration_sec": None,
        "human_turns": 0,
        "notes": args.notes or "",
        "metrics": {},
    }
    _save_run(rec)
    CURRENT.write_text(run_id, encoding="utf-8")
    print(f"Started run {run_id} (arm={arm}, task={task}, branch={branch})")
    for w in _preflight_warnings(branch):
        print(f"\n  !! WARNING: {w}")
    print("\nLog interventions with `turn`; finish with `stop`; then `collect`.")


def cmd_turn(args: argparse.Namespace) -> None:
    rid = _resolve_run_id(args.run)
    rec = _load_run(rid)
    rec["human_turns"] = int(rec.get("human_turns", 0)) + max(1, args.n)
    _save_run(rec)
    print(f"{rid}: human_turns = {rec['human_turns']}")


def cmd_stop(args: argparse.Namespace) -> None:
    rid = _resolve_run_id(args.run)
    rec = _load_run(rid)
    rec["ended_at"] = _now()
    try:
        start = datetime.fromisoformat(rec["started_at"])
        end = datetime.fromisoformat(rec["ended_at"])
        rec["duration_sec"] = int((end - start).total_seconds())
    except (KeyError, ValueError):
        rec["duration_sec"] = None
    _save_run(rec)
    if CURRENT.exists() and _current_run_id() == rid:
        CURRENT.unlink()
    print(f"Stopped {rid}: duration = {rec['duration_sec']}s")


def cmd_collect(args: argparse.Namespace) -> None:
    rid = _resolve_run_id(args.run)
    rec = _load_run(rid)
    task = rec.get("task", args.task)

    print(f"Collecting metrics for {rid} (task={task}) ...")
    tests_total, coverage = _collect_pytest_cov()
    flake8 = _collect_flake8()
    bandit = _collect_bandit()
    pip_audit = None if args.skip_audit else _collect_pip_audit()
    dod = _collect_dod(task)

    base = {}
    if BASE_SNAPSHOT.exists():
        base = json.loads(BASE_SNAPSHOT.read_text(encoding="utf-8"))

    tests_added = (
        tests_total - base["tests_total"]
        if tests_total is not None and base.get("tests_total") is not None
        else None
    )
    coverage_delta = (
        round(coverage - base["coverage_pct"], 2)
        if coverage is not None and base.get("coverage_pct") is not None
        else None
    )

    duration = rec.get("duration_sec")

    def _per_min(value: Optional[float]) -> Optional[float]:
        if value is None or not duration or duration <= 0:
            return None
        return round(value / (duration / 60.0), 3)

    metrics: dict[str, Any] = {
        "tests_total": tests_total,
        "tests_added": tests_added,
        "coverage_pct": coverage,
        "coverage_delta": coverage_delta,
        "tests_per_min": _per_min(tests_added),
        "coverage_per_min": _per_min(coverage_delta),
        "flake8_findings": flake8,
        "bandit_total": (bandit or {}).get("total"),
        "bandit_breakdown": bandit,
        "pip_audit_vulns": pip_audit,
        "dod_status": (dod or {}).get("status"),
        "dod_score": (dod or {}).get("score"),
        "dod_detail": dod,
    }
    if args.ci_branch:
        _merge_ci_metrics(metrics, args.ci_branch)
    existing = rec.get("metrics", {})
    existing.update(metrics)
    rec["metrics"] = existing
    rec["collected_at"] = _now()
    _save_run(rec)
    print(json.dumps(metrics, indent=2))


def cmd_ci(args: argparse.Namespace) -> None:
    """Backfill CI / CodeQL / PR metrics for a run after push + PR open."""
    rid = _resolve_run_id(args.run)
    rec = _load_run(rid)
    branch = args.branch or rec.get("branch")
    if not branch:
        sys.exit("No branch on record; pass --branch.")
    metrics = rec.setdefault("metrics", {})
    _merge_ci_metrics(metrics, branch)
    rec["ci_collected_at"] = _now()
    _save_run(rec)
    keys = [
        "ci_conclusion", "ci_green_sec", "codeql_alerts",
        "pr_number", "pr_changed_files", "pr_additions",
        "pr_deletions", "pr_review_decision", "pr_checks_failed",
    ]
    print(json.dumps({k: metrics.get(k) for k in keys}, indent=2))


def cmd_review(args: argparse.Namespace) -> None:
    """Record neutral review-droid findings (REVIEW_SUMMARY) for a run."""
    rid = _resolve_run_id(args.run)
    rec = _load_run(rid)
    data = None
    if args.json:
        data = json.loads(args.json)
    elif args.from_file:
        text = Path(args.from_file).read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"REVIEW_SUMMARY\s+(\{.*\})", text)
        if m:
            data = json.loads(m.group(1))
    if not isinstance(data, dict):
        sys.exit("Provide --json '<obj>' or --from-file <file with a REVIEW_SUMMARY line>.")
    metrics = rec.setdefault("metrics", {})
    metrics["review_total"] = data.get("total")
    metrics["review_blocking"] = (data.get("critical") or 0) + (data.get("high") or 0)
    metrics["review_breakdown"] = data
    rec["reviewed_at"] = _now()
    _save_run(rec)
    print(json.dumps({k: metrics.get(k) for k in
                      ["review_total", "review_blocking", "review_breakdown"]}, indent=2))


def _summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "mean": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
        "stdev": round(statistics.pstdev(values), 2) if len(values) > 1 else 0.0,
        "min": round(min(values), 2),
        "max": round(max(values), 2),
    }


def _gather(task: Optional[str]) -> dict[str, list[dict[str, Any]]]:
    arms: dict[str, list[dict[str, Any]]] = {"baseline": [], "droid": []}
    for p in sorted(RUNS.glob("*.json")):
        rec = json.loads(p.read_text(encoding="utf-8"))
        if task and rec.get("task") != task:
            continue
        if rec.get("arm") in arms:
            arms[rec["arm"]].append(rec)
    return arms


def _metric_values(runs: list[dict[str, Any]], key: str) -> list[float]:
    out = []
    for r in runs:
        if key == "human_turns":
            v = r.get("human_turns")
        elif key == "duration_sec":
            v = r.get("duration_sec")
        else:
            v = (r.get("metrics") or {}).get(key)
        if isinstance(v, (int, float)):
            out.append(float(v))
    return out


def cmd_aggregate(args: argparse.Namespace) -> None:
    arms = _gather(args.task)
    metrics = [
        "duration_sec", "human_turns", "ci_green_sec",
        "dod_score", "tests_total", "tests_added", "tests_per_min",
        "coverage_pct", "coverage_delta", "coverage_per_min",
        "flake8_findings", "bandit_total", "pip_audit_vulns",
        "codeql_alerts", "review_total", "review_blocking", "pr_changed_files",
    ]
    lines: list[str] = []
    title = f"# Measurement summary{' — ' + args.task if args.task else ''}"
    lines.append(title)
    lines.append("")
    lines.append(f"Baseline runs: {len(arms['baseline'])}  |  Droid runs: {len(arms['droid'])}")
    models = sorted({r.get("model") for r in arms["baseline"] + arms["droid"] if r.get("model")})
    if models:
        same = "same model, both arms" if len(models) == 1 else "WARNING: models differ"
        lines.append(f"Model: {', '.join(models)}  ({same})")
    lines.append("")
    lines.append("| Metric | Baseline (mean) | Droid (mean) | Δ | Better |")
    lines.append("|---|---|---|---|---|")

    for m in metrics:
        b = _summary(_metric_values(arms["baseline"], m))
        d = _summary(_metric_values(arms["droid"], m))
        bm = b.get("mean")
        dm = d.get("mean")
        delta = winner = ""
        if isinstance(bm, (int, float)) and isinstance(dm, (int, float)):
            diff = round(dm - bm, 2)
            delta = f"{diff:+}"
            if diff == 0:
                winner = "tie"
            elif m in LOWER_IS_BETTER:
                winner = "droid" if dm < bm else "baseline"
            else:
                winner = "droid" if dm > bm else "baseline"
        lines.append(
            f"| {m} | {bm if bm is not None else '—'} "
            f"| {dm if dm is not None else '—'} | {delta or '—'} | {winner or '—'} |"
        )

    lines.append("")
    lines.append("## Hypothesis check")
    bd = _metric_values(arms["baseline"], "duration_sec")
    dd = _metric_values(arms["droid"], "duration_sec")
    if bd and dd:
        improvement = round((statistics.mean(bd) - statistics.mean(dd)) / statistics.mean(bd) * 100, 1)
        faster = "Droid" if statistics.mean(dd) < statistics.mean(bd) else "Baseline"
        lines.append(f"- Speed: **{faster}** faster by {abs(improvement)}% on mean time-to-done "
                     f"(baseline n={len(bd)}, droid n={len(dd)}).")
    else:
        lines.append("- Speed: not enough timed runs yet (need `start`/`stop` on both arms).")

    bdod = _metric_values(arms["baseline"], "dod_score")
    ddod = _metric_values(arms["droid"], "dod_score")
    if bdod and ddod:
        lines.append(f"- Completeness: mean DoD score baseline={round(statistics.mean(bdod),3)} "
                     f"vs droid={round(statistics.mean(ddod),3)}.")
    else:
        lines.append("- Completeness: collect DoD on both arms to compare.")

    lines.append("")
    lines.append("_Limitations: single repo, small N, one operator. Directional, reproducible._")

    report = "\n".join(lines)
    print(report)
    out_path = RESULTS / ("summary.md" if not args.task else f"summary_{args.task}.md")
    out_path.write_text(report + "\n", encoding="utf-8")
    print(f"\nWrote {out_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="measure", description="python_weather demo measurement harness")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("shell", help="start an interactive session (no python path per command)")
    sub.add_parser("snapshot-base", help="record base tests/coverage for deltas")

    p_start = sub.add_parser("start", help="begin a timed run")
    p_start.add_argument("--arm", required=True, choices=["baseline", "droid"])
    p_start.add_argument("--task", required=True, help="phase id, e.g. task-a, p2-multiloc")
    p_start.add_argument("--branch")
    p_start.add_argument("--model", default="claude-opus-4.8",
                         help="underlying LLM, held constant across both arms")
    p_start.add_argument("--operator")
    p_start.add_argument("--notes")

    p_turn = sub.add_parser("turn", help="log human intervention(s) on current run")
    p_turn.add_argument("--run")
    p_turn.add_argument("--n", type=int, default=1)

    p_stop = sub.add_parser("stop", help="finish current run and compute duration")
    p_stop.add_argument("--run")

    p_collect = sub.add_parser("collect", help="auto-collect quality/security/DoD metrics")
    p_collect.add_argument("--run")
    p_collect.add_argument("--task", help="override phase id (defaults to the run's task)")
    p_collect.add_argument("--ci-branch", help="also pull CI/CodeQL/PR data for this branch via gh")
    p_collect.add_argument("--skip-audit", action="store_true", help="skip pip-audit (offline)")

    p_ci = sub.add_parser("ci", help="backfill CI/CodeQL/PR metrics after push + PR open")
    p_ci.add_argument("--run")
    p_ci.add_argument("--branch", help="defaults to the run's recorded branch")

    p_review = sub.add_parser("review", help="record neutral review-droid findings for a run")
    p_review.add_argument("--run")
    p_review.add_argument("--json", help="REVIEW_SUMMARY json object, e.g. '{\"total\":3,...}'")
    p_review.add_argument("--from-file", help="file containing a REVIEW_SUMMARY line")

    p_agg = sub.add_parser("aggregate", help="summary stats + head-to-head verdict")
    p_agg.add_argument("--task", help="filter to one phase id")
    p_report = sub.add_parser("report", help="alias for aggregate")
    p_report.add_argument("--task", help="filter to one phase id")
    return parser


DISPATCH = {
    "snapshot-base": cmd_snapshot_base,
    "start": cmd_start,
    "turn": cmd_turn,
    "stop": cmd_stop,
    "collect": cmd_collect,
    "ci": cmd_ci,
    "review": cmd_review,
    "aggregate": cmd_aggregate,
    "report": cmd_aggregate,
}


def _shell_prompt() -> str:
    cur = ""
    if CURRENT.exists():
        cur = CURRENT.read_text(encoding="utf-8").strip()
    rc, branch, _ = _sh(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    branch = branch.strip() if rc == 0 else ""
    inner = " ".join(p for p in (cur, f"@{branch}" if branch else "") if p)
    return f"measure[{inner}]> " if inner else "measure> "


def interactive_shell() -> None:
    parser = build_parser()
    if not os.environ.get("SECRET_KEY"):
        os.environ["SECRET_KEY"] = "demo"
        print("(SECRET_KEY not set; using 'demo' for this session)")
    print("Interactive measurement shell. Type a command without the python path,")
    print("e.g.  start --arm droid --task task-b   |   stop   |   collect --skip-audit")
    print("`help` lists commands, `exit`/`quit` (or Ctrl-D) leaves.\n")
    while True:
        try:
            line = input(_shell_prompt()).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line in {"exit", "quit", "q"}:
            break
        if line in {"help", "?", "h"}:
            parser.print_help()
            continue
        try:
            tokens = shlex.split(line)
        except ValueError as exc:
            print(f"parse error: {exc}")
            continue
        try:
            ns = parser.parse_args(tokens)
        except SystemExit:
            continue  # argparse already reported the error / printed help
        if not ns.cmd or ns.cmd == "shell":
            continue
        try:
            DISPATCH[ns.cmd](ns)
        except SystemExit as exc:
            if exc.code not in (0, None):
                print(f"(command exited with code {exc.code})")
        except Exception as exc:  # keep the session alive on collector errors
            print(f"error: {exc}")


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.cmd or args.cmd == "shell":
        interactive_shell()
        return 0
    DISPATCH[args.cmd](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
