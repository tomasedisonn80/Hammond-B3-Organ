"""Bind existing A33 local executions and original hosted failures; no native rerun."""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

REPO = Path(__file__).resolve().parents[4]
REPORTS = Path(__file__).resolve().parent


def identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def methods(data):
    return sorted(node.name for node in ast.walk(ast.parse(data))
                  if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"))


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, check=True,
                          capture_output=True).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        parser.error("report must be a fresh path")
    before = json.loads((REPORTS / "A33-before-bindings.json").read_text())
    sources, unchanged, runs = {}, {}, []
    for name, old in before["files"].items():
        path = REPO / name
        current = identity(path)
        if not name.startswith("tests/"):
            assert current == old, name
            unchanged[name] = current
            continue
        archive = REPORTS / ("A33-before-" + path.stem + ".txt")
        assert identity(archive) == old, name
        assert archive.read_bytes() == git("show", before["head"] + ":" + name), name
        old_methods, new_methods = methods(archive.read_bytes()), methods(path.read_bytes())
        assert set(old_methods) <= set(new_methods), name
        sources[name] = {"before": old, "after": current,
                         "original_test_methods_preserved": len(old_methods),
                         "current_test_methods": len(new_methods),
                         "new_test_methods": sorted(set(new_methods) - set(old_methods))}
    for suite, count in (("cli", 34), ("adversarial", 12)):
        log = REPORTS / ("A33-" + suite + "-initial-local.log")
        output = log.read_text()
        match = re.search(r"Ran (\d+) tests in ([0-9.]+)s", output)
        assert match and int(match.group(1)) == count and output.endswith("\nOK\n")
        assert " ... skipped " not in output
        runs.append({"command": "python3 -B tests/test_contact_grid_conversion_" + suite + ".py -v",
                     "exit_code": 0, "tests": count, "skips": 0,
                     "unittest_seconds": float(match.group(2)),
                     "log": str(log.relative_to(REPO)), "log_identity": identity(log)})
    policy_path = REPORTS / "A33-capability-policy.json"
    policy = json.loads(policy_path.read_text())
    assert policy["status"] == "passed"
    assert policy["source_sha256"] == sources["tests/test_contact_grid_conversion_adversarial.py"]["after"]["sha256"]
    assert policy["counts"] == {"cases": 10, "capability_skips": 2, "other_errors_retained": 8}
    assert all(case["subprocess_calls"] == 0 for case in policy["cases"])
    original_path = REPORTS / "A33-original-reproduction.json"
    original = json.loads(original_path.read_text())
    assert original["status"] == "both-original-premises-reproduced"
    assert original["log_sha256"] == identity(REPORTS / "A33-original-reproduction.log")["sha256"]
    hosted = []
    published_log_identities = json.loads((REPORTS / "wave04-hosted-log-identities.json").read_text())
    for label, job_id, passed, name in (
        ("macOS AppleClang", 133083059424, 188, "hosted-3520c96-macos-core.log"),
        ("Windows MSVC", 133083060473, 189, "hosted-3520c96-windows-core.raw.log"),
    ):
        actual = identity(REPORTS / name)
        assert all(actual[key] == published_log_identities[name][key] for key in actual)
        hosted.append({"platform": label, "run_id": 43801643469, "job_id": job_id,
                       "head": before["head"], "passed": passed, "registered": 190,
                       "log": name, "log_identity": actual})
    report = {
        "schema": 1, "worker": "/root/w06_a33", "status": "local-repair-qualified-native-rerun-pending",
        "created_utc": datetime.now(timezone.utc).isoformat(), "cwd": str(REPO),
        "original_head": before["head"], "original_tree": before["tree"],
        "observed_head_at_receipt": git("rev-parse", "HEAD").decode().strip(),
        "environment": {"platform": platform.platform(), "python": sys.version},
        "sources": sources, "unchanged_watched_production_contract_corpus": unchanged,
        "original_hosted_failures": hosted, "local_suites": runs,
        "original_reproduction": {"receipt": original_path.name, "identity": identity(original_path),
                                  "cases": original["cases"]},
        "injected_capability_policy": {"receipt": policy_path.name, "identity": identity(policy_path),
                                       "counts": policy["counts"], "seconds": policy["seconds"]},
        "scope": ["Two test files changed; all original test methods retained.",
                  "Actual local directory-alias and Unicode CLI success/refusal journeys pass.",
                  "EILSEQ is injected only in preparation-policy checks; no native macOS replay claimed.",
                  "No native Windows 8.3 replay; hosted raw log supplies the original path-prefix evidence.",
                  "No production, CMake, workflow, shared native build, commit or push by A33.",
                  "Root must publish and observe repaired exact-source macOS and Windows jobs separately."]}
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "local_passes": sum(run["tests"] for run in runs),
                      "unchanged_bindings": len(unchanged), "injected_cases": policy["counts"]["cases"]}))


if __name__ == "__main__":
    main()
