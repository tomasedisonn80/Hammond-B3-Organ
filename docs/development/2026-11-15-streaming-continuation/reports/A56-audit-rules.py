#!/usr/bin/env python3
"""Read-only source checks; writes only the assigned A56 receipt.

This supports a human guidance review. It cannot prove retained dispatches,
chronology/concurrency, implementation correctness, live publication or fidelity.
Run from the repository root with python3 -B and this file's repository path.
"""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[4]
SESSION = Path("docs/development/2026-11-15-streaming-continuation")
BASE = "4aac394cde4da40906b615573a8779aee2d9a37a"
ARCHIVE = Path("docs/development/agent-guidance-history-2026-11-15.txt")
CHECKER = SESSION / "reports/check_streaming_session.py"
ENV = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, env=ENV)


def identity(data):
    return {"bytes": len(data), "sha256": sha256(data)}


def headings(text):
    return {
        re.sub(r"[^\w\- ]", "", line.lstrip("#").strip().lower()).replace(" ", "-")
        for line in text.splitlines() if re.match(r"^#{1,6} ", line)
    }


def links(path, data):
    rows = []
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", data.decode("utf-8")):
        if re.match(r"^[a-z]+:", target):
            continue
        name, separator, fragment = target.partition("#")
        resolved = (ROOT / path).parent / name if name else ROOT / path
        exists = resolved.is_file()
        anchor = not separator or (exists and fragment in headings(resolved.read_text()))
        rows.append({"target": target, "file_exists": exists, "fragment_exists": anchor})
    return rows


def main():
    started = datetime.now(timezone.utc).isoformat()
    index = Path(git("rev-parse", "--git-path", "index").decode().strip())
    index = index if index.is_absolute() else ROOT / index
    index_before = identity(index.read_bytes())
    head_before = git("rev-parse", "HEAD").decode().strip()
    paths = [
        Path("AGENTS.md"), Path("docs/PLAN.md"), ARCHIVE, CHECKER,
        Path("README.md"), Path("docs/STATUS.md"), Path("docs/NEXT_STEPS.md"),
        Path("docs/PROJECT_GUIDE.md"), Path("docs/PRODUCT_HANDOFF.md"),
        Path("docs/DEVELOPMENT_LOG.md"), SESSION / "README.md", SESSION / "SCOPE.md",
        SESSION / "CHECKPOINT.md", SESSION / "reports/atlas-reading-coverage.json",
        SESSION / "notes/A12.md", SESSION / "notes/A44.md",
        Path("docs/reviews/STREAMING_PUBLICATION_ADMISSION.md"),
        Path("docs/reviews/STREAMING_INITIAL_HOSTED_ADMISSION.md"),
        Path("docs/reviews/STREAMING_FULL_PLAN_COVERAGE_REVIEW.md"),
        SESSION / "reports/implementation-publication.json",
        SESSION / "reports/repair-publication.json",
    ]
    snapshots = {str(p): (ROOT / p).read_bytes() for p in paths}
    parent = git("show", BASE + ":AGENTS.md")
    archive = snapshots[str(ARCHIVE)]
    prefix = archive[:-len(parent)]
    archive_checks = {
        "archive": identity(archive), "archive_lines": len(archive.splitlines()),
        "expected_archive_hash_matches": sha256(archive) == "027c7a2a2dd9e27092d338a3b1fa3d36d730195b616711eecfa4310eebabfd41",
        "parent_commit": BASE,
        "parent_agents_blob": git("rev-parse", BASE + ":AGENTS.md").decode().strip(),
        "parent_agents": identity(parent), "prefix": identity(prefix),
        "complete_parent_is_exact_suffix": archive.endswith(parent),
        "expected_lengths_match": (len(archive), len(prefix), len(parent)) == (44307, 1180, 43127),
        "prefix_is_session_preface": prefix.startswith(b"# Current streaming/material continuation"),
        "limit": "The preserved pre-reorganization working file includes a session preface; it is not identical to the parent AGENTS blob alone.",
    }
    pdf = ROOT / "Hammond_B3_Leslie_Research_Atlas_500pp.pdf"
    coverage = json.loads(snapshots[str(SESSION / "reports/atlas-reading-coverage.json")])
    pages, reader_notes = [], []
    for reader in coverage["readers"]:
        pages.extend(range(reader["first_page"], reader["last_page"] + 1))
        data = (ROOT / reader["note"]).read_bytes()
        reader_notes.append({"agent": reader["agent"], "path": reader["note"],
                             **identity(data), "recorded_hash_matches": sha256(data) == reader["note_sha256"]})
    pdf_identity = identity(pdf.read_bytes())
    reading_checks = {
        "pdf": pdf_identity,
        "pdf_hash_matches_receipt": pdf_identity["sha256"] == coverage["pdf_sha256"],
        "six_distinct_recorded_readers": len({r["agent"] for r in coverage["readers"]}) == 6,
        "ranges_cover_1_to_500_once": sorted(pages) == list(range(1, 501)),
        "reader_notes": reader_notes,
        "limit": "Checks retained ranges and note/PDF identities, not actual reading, extract bytes or underlying cited sources. A56 does not claim another 500-page reading.",
    }
    link_results = {str(p): links(p, snapshots[str(p)]) for p in (Path("AGENTS.md"), Path("docs/PLAN.md"))}
    process = subprocess.run([sys.executable, "-B", str(CHECKER), "--repo", "."],
                             cwd=ROOT, env=ENV, text=True, capture_output=True, check=False)
    progress = json.loads(process.stdout)
    changed = [p for p, data in snapshots.items() if (ROOT / p).read_bytes() != data]
    index_after = identity(index.read_bytes())
    report = {
        "schema": "b3-a56-future-rules-audit-v1", "reviewer": "/root/w10_a56",
        "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
        "cwd": str(ROOT), "python": sys.version,
        "local_git": {"head_before": head_before, "head_after": git("rev-parse", "HEAD").decode().strip(),
                      "head_tree": git("rev-parse", "HEAD^{tree}").decode().strip(),
                      "cached_origin_main": git("rev-parse", "refs/remotes/origin/main").decode().strip(),
                      "fresh_remote_query": False, "index_before": index_before, "index_after": index_after,
                      "index_unchanged_during_audit": index_before == index_after},
        "source_snapshots": {p: identity(data) for p, data in snapshots.items()},
        "source_changes_during_audit": changed,
        "archive_checks": archive_checks, "reading_checks": reading_checks,
        "operative_link_checks": link_results,
        "progress_checker": {"command": f"{sys.executable} -B {CHECKER} --repo .",
                             "returncode": process.returncode, "stderr": process.stderr, "result": progress},
        "strict_closure_executed": False,
        "limits": ["Human obligations crosswalk is in STREAMING_FUTURE_AGENT_RULES_REVIEW.md.",
                   "This is a per-file snapshot and narrow document/record integrity check, not a product source freeze or broad test run.",
                   "No build, CTest, UI capture, live remote query, staging, commit, push or ref update occurs here.",
                   "Historical archive link syntax retains repository-root meaning and is not interpreted relative to its archive directory."],
    }
    report["checks_passed"] = (
        all(archive_checks[k] for k in ("expected_archive_hash_matches", "complete_parent_is_exact_suffix", "expected_lengths_match", "prefix_is_session_preface"))
        and all(reading_checks[k] for k in ("pdf_hash_matches_receipt", "six_distinct_recorded_readers", "ranges_cover_1_to_500_once"))
        and all(r["recorded_hash_matches"] for r in reader_notes)
        and all(r["file_exists"] and r["fragment_exists"] for rows in link_results.values() for r in rows)
        and process.returncode == 0 and progress["valid"] and not changed
        and head_before == report["local_git"]["head_after"] and index_before == index_after
    )
    output = ROOT / SESSION / "reports/A56-rules-audit.json"
    if output.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        output = output.with_name(f"A56-rules-audit-{stamp}.json")
    with output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"receipt": str(output.relative_to(ROOT)), **identity(output.read_bytes()),
                      "checks_passed": report["checks_passed"], "counts": progress.get("counts"),
                      "links": {p: len(rows) for p, rows in link_results.items()},
                      "link_failures": [r for rows in link_results.values() for r in rows if not (r["file_exists"] and r["fragment_exists"])],
                      "source_changes_during_audit": changed}, indent=2))
    return 0 if report["checks_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
