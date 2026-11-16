#!/usr/bin/env python3
"""Read-only, bounded documentary audit; print a receipt without running tests."""

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[4]
SESSION = Path("docs/development/2026-11-15-streaming-continuation")
SHARED = [Path("docs") / name for name in (
    "PLAN.md", "PROJECT_GUIDE.md", "STATUS.md", "NEXT_STEPS.md")]
PROPOSALS = [
    "docs/research/CONTACT_GRID_CONVERSION_NEXT.md",
    "docs/research/CAUSAL_CONTACT_AUDIO_NEXT.md",
    "docs/research/CAUSAL_CONTACT_CAPACITY_NEXT.md",
    "docs/design/WHOLE_WINDOW_REFERENCE_NEXT.md",
    "docs/design/REFERENCE_MATERIAL_TYPE_NEXT.md",
    "docs/design/NATIVE_ACCESSIBILITY_JOURNEY_NEXT.md",
]
REVIEWS = [
    "docs/reviews/CONTACT_GRID_CONVERSION_NEXT_REVIEW.md",
    "docs/reviews/CAUSAL_CONTACT_AUDIO_NEXT_REVIEW.md",
    "docs/reviews/CAUSAL_CONTACT_CAPACITY_NEXT_REVIEW.md",
    "docs/reviews/REFERENCE_MATERIAL_NEXT_REVIEW.md",
    "docs/reviews/NATIVE_ACCESSIBILITY_JOURNEY_NEXT_REVIEW.md",
]
OWNERS = [
    "2026-11-15-execution-continuation", "2026-11-15-audio-continuation",
    "2026-11-15-playable-continuation", "2026-11-15-next-phase",
    "2026-11-15-fidelity-continuation", "2026-11-14-waveform-continuation",
]
SELF_REVIEW = Path("docs/reviews/STREAMING_FULL_PLAN_COVERAGE_REVIEW.md")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads((ROOT / path).read_text())


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def identity(path):
    path = Path(path)
    data = (ROOT / path).read_bytes()
    return {"path": str(path), "bytes": len(data), "sha256": digest(data)}


def local_links(path):
    text = (ROOT / path).read_text()
    checked, missing = [], []
    for match in re.finditer(r"\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", text):
        target = match.group(1)
        if target.startswith(("http:", "https:", "mailto:", "data:")):
            continue
        filename = unquote(target.split("#", 1)[0])
        if not filename:
            continue
        resolved = (ROOT / path.parent / filename).resolve()
        checked.append(target)
        if not resolved.exists():
            missing.append(target)
    return {"local_file_links": len(checked), "missing": missing,
            "scope": "Target existence only; no external fetch or anchor semantics."}


def main():
    coverage = read_json(SESSION / "reports/atlas-reading-coverage.json")
    index = read_json("docs/research/chapter-index.json")
    ledger = read_json(SESSION / "assignments.json")
    raw = (ROOT / "../atlas.txt").read_text()
    pages = raw.split("\f")
    pdf = identity("Hammond_B3_Leslie_Research_Atlas_500pp.pdf")
    reader_results, all_pages = [], []
    for reader in coverage["readers"]:
        first, last = reader["first_page"], reader["last_page"]
        page_numbers = list(range(first, last + 1))
        all_pages.extend(page_numbers)
        extract = Path(f"../atlas-{first:03d}-{last:03d}.txt")
        data = (ROOT / extract).read_bytes()
        rebuilt = "".join(f"\n=== PDF PAGE {n} ===\n" + pages[n - 1]
                          for n in page_numbers).encode()
        note = identity(reader["note"])
        matches = [a for a in ledger["assignments"]
                   if a["agent"] == reader["agent"]]
        reader_results.append({
            "agent": reader["agent"], "first_page": first, "last_page": last,
            "extract": identity(extract), "note": note,
            "extract_matches_receipt": len(data) == reader["extract_bytes"]
                and digest(data) == reader["extract_sha256"],
            "page_markers_match": [int(n) for n in re.findall(
                r"^=== PDF PAGE (\d+) ===$", data.decode(), re.M)] == page_numbers,
            "extract_reconstructs_from_raw_pages": data == rebuilt,
            "note_matches_receipt": note["sha256"] == reader["note_sha256"],
            "accepted_ledger_binding": len(matches) == 1
                and matches[0]["status"] == "accepted"
                and matches[0]["note_sha256"] == reader["note_sha256"],
        })
    chapters = index["chapters"]
    chapter_pages = [p for c in chapters
                     for p in range(c["start_page"], c["end_page"] + 1)]
    chapter_checks = {
        "count": len(chapters),
        "numbers_1_to_80": [c["number"] for c in chapters] == list(range(1, 81)),
        "six_pages_each": all(c["end_page"] - c["start_page"] == 5 for c in chapters),
        "contiguous_pages_13_to_492": chapter_pages == list(range(13, 493)),
        "front_chapters_directory_cover_500": [p for s in index["sections"]
            for p in range(s["start_page"], s["end_page"] + 1)] == list(range(1, 501)),
        "chapter_start_markers_match_extract": all(re.search(
            rf"CHAPTER\s+{c['chapter_id']}\b", pages[c["start_page"] - 1])
            is not None for c in chapters),
        "ten_research_waves": len(index["research_waves"]) == 10,
        "all_original_review_note_targets_exist": all(
            (ROOT / "docs/research" / c["review_note"]).exists() for c in chapters),
        "source_identity_matches_pdf": index["source"]["sha256"] == pdf["sha256"]
            and index["source"]["bytes"] == pdf["bytes"],
    }
    payload = read_json(SESSION / "reports/A30-compatibility.json")[
        "contact_reference_component"]["install_rules_and_payload_sha256"]
    changed = [{"path": path, "old_sha256": old, "current_sha256": identity(path)["sha256"]}
               for path, old in payload.items() if identity(path)["sha256"] != old]
    source_inputs = [Path("AGENTS.md"), Path("README.md"), *SHARED,
        Path("docs/PRODUCT_HANDOFF.md"), Path("docs/DEVELOPMENT_LOG.md"),
        Path("docs/research/chapter-index.json"), SESSION / "README.md",
        SESSION / "SCOPE.md", SESSION / "CHECKPOINT.md", SESSION / "assignments.json",
        SESSION / "reports/atlas-reading-coverage.json",
        SESSION / "reports/implementation-publication.json",
        SESSION / "reports/repair-publication.json", SESSION / "reports/A30-compatibility.json",
        Path("docs/reviews/CONTACT_REFERENCE_WINDOWS_REPAIR_ADMISSION.md"),
        Path("docs/reviews/STREAMING_INITIAL_HOSTED_ADMISSION.md"),
        *(Path(p) for p in PROPOSALS + REVIEWS),
        *(Path("docs/development") / name / "CHECKPOINT.md" for name in OWNERS),
        SELF_REVIEW, Path(__file__).resolve().relative_to(ROOT)]
    source_before = [identity(p) for p in source_inputs]
    shared_text = {str(p): (ROOT / p).read_text() for p in SHARED}
    record = {
        "schema_version": 1,
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "reviewer": "/root/w09_a54", "cwd": str(ROOT),
        "command": "python3 -B docs/development/2026-11-15-streaming-continuation/reports/A54-plan-coverage.py",
        "python": sys.version, "platform": platform.platform(),
        "scope": {"focused_pdf_pages_reread": [5, *range(445, 457), *range(481, 493)],
                  "new_whole_500_page_reading_claim": False,
                  "runtime_build_broad_tests_native_ui_remote_queries": False,
                  "external_dispatch_attestation": False},
        "git": {"head": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}"),
                "cached_origin_main": git("rev-parse", "refs/remotes/origin/main"),
                "staged_paths_at_observation": git("diff", "--cached", "--name-only").splitlines()},
        "pdf": {**pdf, "matches_coverage": pdf["sha256"] == coverage["pdf_sha256"]},
        "raw_extract": {**identity("../atlas.txt"), "pages": len(pages) - 1,
                        "terminal_part_empty": not pages[-1]},
        "readers": reader_results,
        "coverage": {"complete_disjoint_1_to_500": all_pages == list(range(1, 501)),
                     "six_unique_readers": len(set(r["agent"] for r in reader_results)) == 6},
        "chapter_index": chapter_checks,
        "plan_milestone_rows": re.findall(r"^\| \*\*(M\d) —", shared_text["docs/PLAN.md"], re.M),
        "owner_recovery_routes": {name: {doc: f"{name}/CHECKPOINT.md" in text
                                        for doc, text in shared_text.items()}
                                  for name in OWNERS},
        "new_proposal_routes": {p: {doc: Path(p).name in text
                                     for doc, text in shared_text.items()} for p in PROPOSALS},
        "new_review_routes": {p: {doc: Path(p).name in text
                                   for doc, text in shared_text.items()} for p in REVIEWS},
        "next_steps_has_streaming_strict_command":
            "check_streaming_session.py --repo . --strict" in shared_text["docs/NEXT_STEPS.md"],
        "local_link_checks": {str(p): local_links(p) for p in [*SHARED, SELF_REVIEW]},
        "historical_A30_payload_comparison": {
            "inventory_including_install_rules": len(payload),
            "payload_names": len(payload) - 1, "changed": changed,
            "unchanged_including_install_rules": len(payload) - len(changed),
            "scope": "Hash comparison only; old numerical/runtime reports are not rebound."},
        "ledger_snapshot": {"records": len(ledger["assignments"]),
                            "statuses": dict(Counter(a["status"] for a in ledger["assignments"])),
                            "required_workers": ledger["requested_workers"],
                            "closure_claim": False},
        "source_inputs": source_before,
        "source_inputs_stable_during_audit": source_before == [identity(p) for p in source_inputs],
        "manual_findings": ["A54-F1 published-source freshness", "A54-F2 Windows grid evidence",
                            "A54-F3 changed installed I/O identity", "A54-F4 new proposal/review routes",
                            "A54-F5 matching strict-check command and historical result link"],
        "disposition": "Complete-plan coverage retained; root final-document corrections remain. No product completion claim.",
    }
    print(json.dumps(record, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
