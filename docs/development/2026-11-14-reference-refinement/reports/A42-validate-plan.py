#!/usr/bin/env python3
"""A42 documentary source/link/arithmetic receipt; never runs native code/tests."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata


ROOT = Path(__file__).resolve().parents[4]
SESSION = Path("docs/development/2026-11-14-reference-refinement")
PLAN = Path("docs/ROTARY_RENDERER_IMPLEMENTATION_PLAN.md")
NOTE = SESSION / "notes/A42-rotary-renderer-next-plan.md"
REPORT = SESSION / "reports/A42-rotary-renderer-plan.json"
BASELINE = "f9c11a498ecd88886349415205fc5dccc627033e"
INCOMING = "26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8"
PROTECTED = (
    "include/hammond/RotaryTypes.h",
    "include/hammond/RotaryMotion.h",
    "include/hammond/RotaryPropagation.h",
    "src/RotaryMotion.cpp",
    "src/RotaryPropagation.cpp",
    "docs/ROTARY_NUMERICAL_CONTRACT.md",
    "docs/ROTARY_PROPAGATION_CONTRACT.md",
)
INPUTS = PROTECTED + (
    "AGENTS.md",
    "docs/PLAN.md",
    "docs/REFERENCE_REFINEMENT_SCOPE.md",
    str(SESSION / "CHECKPOINT.md"),
    str(SESSION / "assignments.json"),
    "docs/ROTARY_MOTION.md",
    "docs/ROTARY_PROPAGATION.md",
    str(SESSION / "notes/A30-rotary-docs-handoff.md"),
    "docs/ROTARY_RENDERER_PLAN.md",
    "docs/development/2026-11-14-waveform-continuation/README.md",
    "docs/development/2026-11-14-waveform-continuation/CHECKPOINT.md",
    "tests/test_rotary_motion_acceptance.py",
    "tests/test_rotary_propagation_acceptance.py",
    "tools/rotary_reference.py",
)


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def identity(path: Path | str) -> dict:
    data = (ROOT / path).read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def heading_fragments(path: Path) -> set[str]:
    found: set[str] = set()
    counts: dict[str, int] = {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*$", path.read_text(), re.M):
        plain = heading.replace("`", "").replace("*", "").lower()
        slug = "".join(c for c in plain if c in " -_" or unicodedata.category(c)[0] in "LN")
        slug = slug.replace(" ", "-")
        prior = counts.get(slug, 0)
        counts[slug] = prior + 1
        found.add(slug if prior == 0 else f"{slug}-{prior}")
    return found


def main() -> int:
    errors: list[str] = []
    checks: list[dict] = []
    for doc in (PLAN, NOTE):
        path = ROOT / doc
        body = path.read_text()
        words = len(body.split())
        if doc == NOTE and words > 700:
            errors.append(f"Note exceeds 700 words: {words}")
        if not body.endswith("\n") or body.endswith("\n\n"):
            errors.append(f"Noncanonical final newline: {doc}")
        for number, line in enumerate(body.splitlines(), 1):
            if line != line.rstrip() or "\t" in line:
                errors.append(f"Whitespace at {doc}:{number}")
        for link in re.findall(r"\]\(([^)]+)\)", body):
            if "://" in link or link.startswith("mailto:"):
                continue
            target, _, fragment = link.partition("#")
            resolved = (path.parent / target).resolve() if target else path
            # The report is emitted below; inspect all other links directly.
            exists = resolved == (ROOT / REPORT).resolve() or resolved.is_file()
            fragment_ok = not fragment or (exists and fragment in heading_fragments(resolved))
            checks.append({"from": str(doc), "target": link,
                           "exists": exists, "fragment_valid": fragment_ok})
            if not exists or not fragment_ok:
                errors.append(f"Invalid local link: {doc} -> {link}")
    unchanged = {}
    for path in PROTECTED:
        same = git("show", f"{BASELINE}:{path}") == (ROOT / path).read_bytes()
        unchanged[path] = same
        if not same:
            errors.append(f"Protected source changed from baseline: {path}")
    same_brief = git("show", f"{INCOMING}:docs/ROTARY_RENDERER_PLAN.md") == (ROOT / "docs/ROTARY_RENDERER_PLAN.md").read_bytes()
    if not same_brief:
        errors.append("Concurrent brief changed from its inspected incoming commit")
    rates = (44100, 48000, 96000, 192000)
    capacities = []
    for rate in rates:
        delay = Fraction(rate * 20, 300)
        ceiling = -(-delay.numerator // delay.denominator)
        row = {"sample_rate": rate, "maximum_delay_frames": str(delay),
               "capacity_frames": ceiling + 6, "flush_frames": ceiling + 4,
               "epoch_frames": 86400 * rate}
        capacities.append(row)
        if ceiling + 6 > 16384:
            errors.append(f"History cap exceeded at {rate}")
    margin_m = Fraction(1, 2**43)
    margin_frames = margin_m * Fraction(192000, 300)
    arithmetic = {
        "basis": "Frozen admission limits; documentary arithmetic only",
        "capacities": capacities,
        "maximum_bracket_margin_m_exact": str(margin_m),
        "maximum_bracket_margin_frames_exact": str(margin_frames),
        "maximum_bracket_margin_frames": float(margin_frames),
        "maximum_path_evaluations_per_call": 4 * 4096 * 48,
        "maximum_tap_reads_per_call": 16 * 4096,
        "maximum_journal_cell_entries": 2 * 4096,
        "maximum_output_scratch_doubles": 2 * 4096,
        "static_grid_cells": 65 * 512,
        "low_band_grid_cells": 65 * 103,
        "ordered_stopped_rate_pairs": 4 * 4,
    }
    result = {
        "schema_version": 1,
        "assignment": "A42",
        "agent": "/root/w07_a42_rotary_renderer_next_plan",
        "session": "2026-11-14-reference-refinement",
        "result_scope": "Proposed independent R4 engineering review; no native/runtime acceptance",
        "initial_product_head": BASELINE,
        "initial_product_tree": "39ac16b12526143eee4136e4cc4a534b71013660",
        "observed_head_at_validation": git("rev-parse", "HEAD").decode().strip(),
        "observed_tree_at_validation": git("rev-parse", "HEAD^{tree}").decode().strip(),
        "observed_origin_main_at_validation": git("rev-parse", "refs/remotes/origin/main").decode().strip(),
        "concurrent_brief_commit": INCOMING,
        "concurrent_brief_matches_incoming": same_brief,
        "inputs": {path: identity(path) for path in INPUTS},
        "artifacts": {str(path): {**identity(path), "words": len((ROOT / path).read_text().split())}
                      for path in (PLAN, NOTE, Path(__file__).relative_to(ROOT))},
        "protected_sources_match_initial_product": unchanged,
        "document_validation": {"passed": not errors, "local_links_checked": len(checks),
                                "links": checks, "errors": errors},
        "documentary_arithmetic": arithmetic,
        "validation_command": "python3 " + str(Path(__file__).relative_to(ROOT)),
        "working_directory": str(ROOT),
        "python_version": sys.version.split()[0],
        "other_executed_checks": ["read-only file inventory and source reads", "git status --short",
                                  "git rev-parse HEAD HEAD^{tree} refs/remotes/origin/main",
                                  "git diff f9c11a4 -- five native rotary files and two frozen contracts"],
        "not_run": ["configure/build", "native tests", "numerical acceptance", "sanitizers",
                    "allocation probe", "device/host integration", "commit/push"],
    }
    (ROOT / REPORT).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"passed": not errors, "links_checked": len(checks),
                      "note_words": result["artifacts"][str(NOTE)]["words"],
                      "plan_words": result["artifacts"][str(PLAN)]["words"],
                      "protected_unchanged": all(unchanged.values()), "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
