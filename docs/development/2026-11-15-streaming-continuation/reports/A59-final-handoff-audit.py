#!/usr/bin/env python3
"""Read-only final follow-up for existing A59; no additional worker credit.

Writes only a new A59 receipt; a prior observation is never overwritten.
The text/link checks support an independent reading, not product acceptance.
"""
from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unicodedata
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[4]
SESSION = Path("docs/development/2026-11-15-streaming-continuation")
BASE = "2f57723d9ec806fe8f721c317ef8c1a38d63b532"
DOCUMENTS = [
    "AGENTS.md", "README.md", "docs/PLAN.md", "docs/PROJECT_GUIDE.md",
    "docs/STATUS.md", "docs/NEXT_STEPS.md", "docs/PRODUCT_HANDOFF.md",
    "docs/CAUSAL_CONTACT_GRID_GUIDE.md", "docs/CAUSAL_CONTACT_GRID_RESULTS.md",
    "docs/DEVELOPMENT_LOG.md", str(SESSION / "README.md"),
    str(SESSION / "CHECKPOINT.md"),
]
PROPOSALS = [
    "research/CONTACT_GRID_CONVERSION_NEXT.md",
    "research/CAUSAL_CONTACT_AUDIO_NEXT.md",
    "research/CAUSAL_CONTACT_CAPACITY_NEXT.md",
    "design/WHOLE_WINDOW_REFERENCE_NEXT.md",
    "design/REFERENCE_MATERIAL_TYPE_NEXT.md",
    "design/NATIVE_ACCESSIBILITY_JOURNEY_NEXT.md",
]
REVIEWS = [
    "reviews/CONTACT_GRID_CONVERSION_NEXT_REVIEW.md",
    "reviews/CAUSAL_CONTACT_AUDIO_NEXT_REVIEW.md",
    "reviews/CAUSAL_CONTACT_CAPACITY_NEXT_REVIEW.md",
    "reviews/REFERENCE_MATERIAL_NEXT_REVIEW.md",
    "reviews/NATIVE_ACCESSIBILITY_JOURNEY_NEXT_REVIEW.md",
]


DOCUMENTS.append("docs/STREAMING_CONTINUATION_CLOSURE.md")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def headings(text: str) -> set[str]:
    result: set[str] = set()
    counts: dict[str, int] = {}
    fenced = False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        if fenced:
            continue
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        title = re.sub(r"!?\[([^\]]+)\]\([^)]*\)", r"\1", match[1])
        title = re.sub(r"<[^>]*>", "", title).lower()
        slug = "".join(c for c in title if c in "-_ " or c.isspace()
                       or unicodedata.category(c)[0] in "LN")
        slug = re.sub(r"\s", "-", slug.strip())
        number = counts.get(slug, 0)
        counts[slug] = number + 1
        result.add(slug + (f"-{number}" if number else ""))
    result.update(re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)', text))
    return result


def section(text: str, start: str, end: str | None = None) -> str:
    value = text[text.index(start):]
    return value[:value.index(end)] if end else value


def main() -> None:
    moment = dt.datetime.now(dt.timezone.utc)
    index_path = Path(git("rev-parse", "--git-path", "index").decode().strip())
    if not index_path.is_absolute():
        index_path = ROOT / index_path
    index_before = sha(index_path.read_bytes())
    head_before = git("rev-parse", "HEAD", "HEAD^{tree}").decode().splitlines()
    inputs = DOCUMENTS + [str(SESSION / "assignments.json")]
    inputs += ["docs/" + x for x in PROPOSALS + REVIEWS]
    inputs += [
        "docs/reviews/STREAMING_FULL_PLAN_COVERAGE_REVIEW.md",
        "docs/reviews/STREAMING_FUTURE_AGENT_RULES_REVIEW.md",
        "docs/reviews/CONTACT_REFERENCE_WINDOWS_REPAIR_ADMISSION.md",
    ]
    inputs += [str(SESSION / "reports" / x) for x in [
        "hosted-2f57723-complete.json", "windows-core-2f57723-success.json",
        "windows-core-2f57723.log.gz", "hosted-af2b747-complete.json",
        "implementation-publication.json", "repair-publication.json",
        "windows-repair-qualification.json", "coherent-qualification.json",
        "final-coherent-qualification.json", "publication-source-qualification.json",
        "atlas-reading-coverage.json", "check_streaming_session.py", "A30-compatibility.json",
    ]]
    payload = json.loads((ROOT / SESSION / "reports/A30-compatibility.json").read_text())["contact_reference_component"]["install_rules_and_payload_sha256"]
    inputs += list(payload)
    extra_names = ["streaming-session-strict.json", "A55-final-record-audit.json",
                   "final-documentary-source-admission.json", "windows-repair-code-inputs.json.gz",
                   "A58-hosted-audit.json", "A59-integrity.json"]
    inputs += [str(SESSION / "reports" / n) for n in extra_names]
    prior_own = json.loads((ROOT / SESSION / "reports/A59-integrity.json").read_text())
    inputs += list(prior_own["files"])
    current_ledger = json.loads((ROOT / SESSION / "assignments.json").read_text())
    note_paths = {}
    for row in current_ledger["assignments"]:
        matches = [p for p in row["owned_paths"] if p.startswith(str(SESSION / "notes") + "/") and p.endswith(".md")]
        assert len(matches) == 1, (row["number"], matches)
        note_paths[row["number"]] = matches[0]
    inputs += list(note_paths.values())
    repaired_inputs = json.loads(gzip.decompress((ROOT / SESSION / "reports/windows-repair-code-inputs.json.gz").read_bytes()))
    source_admission = json.loads((ROOT / SESSION / "reports/final-documentary-source-admission.json").read_text())
    qualified_inputs = repaired_inputs | source_admission["workflows"]
    inputs += list(qualified_inputs)
    inputs = list(dict.fromkeys(inputs))
    before = {name: (ROOT / name).read_bytes() for name in inputs}
    texts = {name: before[name].decode() for name in DOCUMENTS}
    checks: list[dict] = []

    def check(name: str, ok: bool, details=None) -> None:
        checks.append({"check": name, "passed": bool(ok), "details": details})

    check("local published code identity", head_before == [BASE, "cee5fdc4b07d95185ebd9e4d1c5f236f88a787f9"], head_before)
    link_results = []
    anchor_cache: dict[Path, set[str]] = {}
    for name in DOCUMENTS:
        content = re.sub(r"(?ms)^\s*(```|~~~).*?^\s*\1\s*$", "", texts[name])
        links = re.findall(r"!?\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", content)
        bad = []
        local = 0
        for target in links:
            parts = urlsplit(target)
            if parts.scheme or parts.netloc:
                continue
            local += 1
            path = ((ROOT / name).parent / unquote(parts.path)).resolve() if parts.path else ROOT / name
            if not path.exists():
                bad.append({"target": target, "reason": "missing path"})
                continue
            if parts.fragment and path.suffix.lower() == ".md":
                if path not in anchor_cache:
                    anchor_cache[path] = headings(path.read_text())
                if unquote(parts.fragment) not in anchor_cache[path]:
                    bad.append({"target": target, "reason": "missing heading"})
        link_results.append({"file": name, "local_links": local, "failures": bad})
    check("document local paths and heading fragments", not any(x["failures"] for x in link_results), link_results)

    for name in ["docs/PLAN.md", "docs/PROJECT_GUIDE.md", "docs/STATUS.md", "docs/NEXT_STEPS.md"]:
        missing = [p for p in PROPOSALS + REVIEWS if f"]({p})" not in texts[name]]
        check("next proposal and review routes: " + name, not missing, missing)
    command = "python3 -B docs/development/2026-11-15-streaming-continuation/reports/check_streaming_session.py --repo . --strict"
    check("streaming strict command is explicit", command in texts["docs/NEXT_STEPS.md"])
    old_result = "development/2026-11-15-product-continuation/reports/product-session-strict.json"
    check("historical product result has its own route", f"]({old_result})" in texts["docs/PROJECT_GUIDE.md"])

    markers = {
        "docs/STATUS.md": "## Earlier execution continuation snapshot — 15 November 2026",
        "docs/NEXT_STEPS.md": "### Historical execution handoff — 15 November 2026",
        "docs/PRODUCT_HANDOFF.md": "## Historical product-continuation record — 15 November 2026",
    }
    for name, marker in markers.items():
        prior = git("show", f"{BASE}:{name}").decode()
        old_suffix = section(prior, marker)
        new_suffix = section(texts[name], marker)
        check("historical suffix retained: " + name, old_suffix == new_suffix,
              {"bytes": len(old_suffix.encode()), "sha256": sha(old_suffix.encode())})
    prior_log = git("show", f"{BASE}:docs/DEVELOPMENT_LOG.md").decode().partition("\n\n")[2]
    check("original development log entries retained", texts["docs/DEVELOPMENT_LOG.md"].endswith(prior_log),
          {"bytes": len(prior_log.encode()), "sha256": sha(prior_log.encode())})
    prior_plan = git("show", f"{BASE}:docs/PLAN.md").decode()
    old_plan = section(prior_plan, "## Milestones and exit evidence", "## Current ownership and source")
    new_plan = section(texts["docs/PLAN.md"], "## Milestones and exit evidence", "## Current ownership and source")
    check("complete milestones and dependency rules retained", old_plan == new_plan,
          {"sha256": sha(old_plan.encode()), "milestones": re.findall(r"\*\*(M\d) —", new_plan)})
    owner_routes = ["execution-continuation", "audio-continuation", "playable-continuation", "next-phase", "fidelity-continuation", "waveform-continuation"]
    owner_block = section(texts["docs/PLAN.md"], "## Current ownership and source", "## Current implementation design choices")
    check("separate owner recovery routes retained", all(x in owner_block for x in owner_routes), owner_routes)

    hosted = json.loads(before[str(SESSION / "reports/hosted-2f57723-complete.json")])
    jobs = [j for r in hosted["runs"] for j in r["jobs"]]
    check("retained repaired source has thirteen successful jobs", hosted["commit"] == BASE and len(jobs) == 13
          and all(r["head_sha"] == BASE and r["run_attempt"] == 1 and r["event"] == "push"
                  and r["status"] == "completed" and r["conclusion"] == "success" for r in hosted["runs"])
          and all(j["status"] == "completed" and j["conclusion"] == "success" for j in jobs))
    failure = json.loads(before[str(SESSION / "reports/hosted-af2b747-complete.json")])
    check("initial failed matrix remains distinct", failure["commit"].startswith("af2b747")
          and failure["successful_jobs"] == 12 and failure["total_jobs"] == 13)
    win = json.loads(before[str(SESSION / "reports/windows-core-2f57723-success.json")])
    raw = gzip.decompress(before[str(SESSION / "reports/windows-core-2f57723.log.gz")])
    check("retained repaired Windows log identity and totals", sha(raw) == win["decoded_log_sha256"]
          and len(raw) == win["decoded_log_bytes"] and win["commit"] == BASE
          and win["tests"] == {"passed": 185, "failed": 0, "total": 185, "wall_seconds": 291.43}
          and b"100% tests passed, 0 tests failed out of 185" in raw)
    causal = ["test_causal_contact_grid", "test_causal_contact_grid_lifecycle", "test_causal_contact_grid_resources",
              "python_test_causal_contact_grid_cli", "python_test_causal_contact_grid_differential", "python_test_causal_contact_grid_reference"]
    log = raw.decode()
    check("six causal suites and relocated install appear passed", all(re.search(r"Test\s+#\d+: " + re.escape(n) + r"\s+\.+\s+Passed", log) for n in causal + ["python_test_contact_reference_install"]))
    changed_payload = {p: {"before": h, "after": sha(before[p])} for p, h in payload.items() if sha(before[p]) != h}
    check("old package has exactly the documented one-file exception", len(payload) == 49
          and set(changed_payload) == {"tools/contact_switching_io.py"}
          and changed_payload["tools/contact_switching_io.py"]["after"] == "1281cd0726a6cf16dcc0ceea8445b4e42900ed995bb82dfea70c6dffdd104cc6",
          {"members_including_install_rule": len(payload), "changed": changed_payload})
    immutable_reports = ["coherent-qualification.json", "final-coherent-qualification.json",
                         "publication-source-qualification.json", "atlas-reading-coverage.json",
                         "A30-compatibility.json", "hosted-af2b747-complete.json", "windows-repair-qualification.json"]
    rewritten = [n for n in immutable_reports if before[str(SESSION / "reports" / n)] != git("show", f"{BASE}:{SESSION}/reports/{n}")]
    check("original source-bound reports are not rewritten", not rewritten, rewritten)

    ledger = json.loads(before[str(SESSION / "assignments.json")])
    rows = ledger["assignments"]
    accepted = sum(x["status"] == "accepted" for x in rows)
    check("ledger is a bounded snapshot", len(rows) <= 60 and accepted <= len(rows), {"recorded": len(rows), "accepted": accepted})
    count_match = re.search(r"(\d+)(?: actual workers)? dispatched / (\d+) accepted", texts[str(SESSION / "CHECKPOINT.md")])
    check("checkpoint exact live counts agree", bool(count_match) and tuple(map(int, count_match.groups())) == (len(rows), accepted), count_match.groups() if count_match else None)
    strict_path = str(SESSION / "reports/streaming-session-strict.json")
    strict = json.loads(before[strict_path])
    ledger_path = str(SESSION / "assignments.json")
    check("final strict receipt binds all sixty accepted records", len(rows) == accepted == 60
          and strict["valid"] and strict["strict_record_closure"]
          and strict["ledger"]["sha256"] == sha(before[ledger_path])
          and strict["counts"] == {"records": 60, "unique_numbers": 60, "unique_agents": 60,
                                    "accepted_numbers": 60, "verified_accepted_notes": 60}
          and len(strict["waves"]) == 10
          and all(w["recorded"] == w["accepted"] == w["verified"] == 6 for w in strict["waves"])
          and strict["external_dispatch_attested"] is False)
    note_errors = [r["number"] for r in rows if r["status"] != "accepted"
                   or sha(before[note_paths[r["number"]]]) != r["note_sha256"]]
    wave_numbers = {str(w): sorted(r["number"] for r in rows if r["wave"] == w) for w in range(1, 11)}
    check("independent note hashes and ten exact groups agree", not note_errors
          and len(set(note_paths.values())) == 60
          and all(wave_numbers[str(w)] == list(range(6*w-5, 6*w+1)) for w in range(1, 11)),
          {"note_errors": note_errors, "waves": wave_numbers})
    a55 = json.loads(before[str(SESSION / "reports/A55-final-record-audit.json")])
    check("retained A55 final audit and root strict bytes agree", a55["passed"]
          and len(a55["checks"]) == 21 and all(a55["checks"].values())
          and a55["additional_worker_credit"] == 0
          and a55["strict_result"] == strict
          and a55["strict_stdout_sha256"] == sha(before[strict_path])
          and a55["strict_stdout_bytes"] == len(before[strict_path]))
    old_a59_differences = [p for p, m in prior_own["files"].items()
                           if len(before[p]) != m["bytes"] or sha(before[p]) != m["sha256"]]
    check("all original A59 files and accepted note remain exact", not old_a59_differences
          and sha(before[str(SESSION / "reports/A59-integrity.json")]) == "ea897953d24520d335d4af0b9ee0c8e51db3d54f739353460dbd1f91d1008d42"
          and sha(before[str(SESSION / "notes/A59.md")]) == "3b9778a425ab8b9974c9d6a66bc6e40ad1ceb2e0a583ac7a38da6d65dbefa010",
          old_a59_differences)
    prior_audit = json.loads(before[str(SESSION / "reports/A59-handoff-audit-20261116T014947649010Z.json")])
    old_log_reconstructed = "# Development log\n\n" + section(texts["docs/DEVELOPMENT_LOG.md"], "## 2026-11-16 — Published code passes repaired platform matrix; final handoff review")
    check("all log entries from original A59 snapshot also remain exact",
          sha(old_log_reconstructed.encode()) == prior_audit["inputs"]["docs/DEVELOPMENT_LOG.md"]["sha256"])
    changed_code = [p for p, h in qualified_inputs.items() if sha(before[p]) != h]
    check("505 production inputs and three workflows retain repaired identities",
          len(repaired_inputs) == 505 and len(source_admission["workflows"]) == 3
          and source_admission["qualified_code_commit"] == BASE
          and source_admission["all_current_inputs_match_repaired_qualification_and_commit"]
          and sha(before[str(SESSION / "reports/windows-repair-code-inputs.json.gz")]) == source_admission["inventory_compressed_sha256"]
          and not changed_code, changed_code)
    names = list(qualified_inputs)
    objects = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT,
                             input=("\n".join(BASE + ":" + p for p in names) + "\n").encode(),
                             capture_output=True, check=True).stdout
    cursor = 0
    unequal_blobs = []
    for name in names:
        end = objects.index(b"\n", cursor)
        parts = objects[cursor:end].split()
        assert len(parts) == 3 and parts[1] == b"blob", parts
        size = int(parts[2]); cursor = end + 1
        blob = objects[cursor:cursor+size]; cursor += size
        assert objects[cursor:cursor+1] == b"\n"
        cursor += 1
        if blob != before[name]:
            unequal_blobs.append(name)
    check("all qualified current bytes match immutable repaired Git blobs",
          not unequal_blobs and cursor == len(objects), unequal_blobs)
    a58 = json.loads(before[str(SESSION / "reports/A58-hosted-audit.json")])
    recorded = a58["jobs"]
    core = [j for j in recorded if "six_causal_suites_pass" in j]
    native = [j for j in recorded if j["name"].startswith("Native standalone")]
    vst3 = [j for j in recorded if j["name"].startswith("Native VST3")]
    check("closure hosted table agrees with independently retained exact-source admission",
          a58["source_commit"] == BASE and a58["successful_jobs"] == a58["total_jobs"] == 13
          and a58["root_completion_receipt_independently_agrees"]
          and all(j["actual_recorded_revision_matches"] and j["conclusion"] == "success" for j in recorded)
          and len(core) == 4 and all(j["ctest_passed"] == j["ctest_total"] == 185 and j["six_causal_suites_pass"] for j in core)
          and len(native) == 5 and sorted(j["ctest_total"] for j in native) == [22, 53, 53, 53, 53]
          and all(j["ctest_passed"] == j["ctest_total"] for j in native)
          and all(j["upper_fixture"]["result"]["cases"] == 30 and j["upper_fixture"]["result"]["checks"] == 58876889 for j in native)
          and len(vst3) == 3 and sorted(j["ctest_total"] for j in vst3) == [7, 7, 8]
          and all(j["vst3_validator"]["passed"] == 47 and j["vst3_validator"]["failed"] == 0 for j in vst3))
    closure = texts["docs/STREAMING_CONTINUATION_CLOSURE.md"]
    listed_waves = [(int(w), int(first), int(last)) for w, first, last in re.findall(r"\| (\d+) \| A(\d+)–A(\d+) \|", closure)]
    check("closure wave table names exactly the accepted grouping", listed_waves == [(w, 6*w-5, 6*w) for w in range(1, 11)], listed_waves)
    normalized = " ".join(closure.split())
    check("closure retains scope and exact-next-action boundaries",
          "Literal whole-interface 1:1 remains unmet and unwaived" in normalized
          and "Their next implementation contracts remain unadmitted" in normalized
          and all(t in closure for t in ["Lower L1", "Wood W1", "footage T1", "S0", "N+33", "505", "2f57723", "fresh expected head", "without force"])
          and "the retained repaired-code runs stay bound to `2f57723`" in normalized)
    old_sentence = "The current streaming session remains in progress; only its own actual ledger"
    corrected = "The current streaming session has sixty accepted scoped deliveries in ten waves;"
    finding_resolved = old_sentence not in texts["docs/PLAN.md"] and corrected in texts["docs/PLAN.md"]
    check("observed final PLAN count finding is resolved", finding_resolved)
    manual_findings = [{"id": "A59-FINAL-1", "file": "docs/PLAN.md", "section": "Keeping the plan alive",
                       "observed_before_correction": old_sentence,
                       "finding": "Residual current in-progress wording contradicted the final sixty accepted records.",
                       "resolution": corrected, "resolved_in_final_snapshot": finding_resolved,
                       "historical_and_ownership_limits_retained": True}]
    changed = [p for p, data in before.items() if (ROOT / p).read_bytes() != data]
    check("all audited inputs stable during observation", not changed, changed)
    check("index and HEAD unchanged during observation", sha(index_path.read_bytes()) == index_before and git("rev-parse", "HEAD", "HEAD^{tree}").decode().splitlines() == head_before)

    result = {"schema_version": 1, "reviewer": "/root/w10_a59", "followup_of_existing_worker": 59, "additional_worker_credit": 0, "manual_findings": manual_findings, "observed_utc": moment.isoformat(),
              "cwd": str(ROOT), "scope": "Current shared handoff reading, local links, preserved history and retained source evidence; no fresh remote/hosted query, build, native execution or product acceptance.",
              "head": head_before[0], "tree": head_before[1], "index_sha256": index_before,
              "review_script_sha256": sha(Path(__file__).read_bytes()),
              "inputs": {p: {"bytes": len(b), "sha256": sha(b)} for p, b in before.items()},
              "checks": checks, "passed": all(x["passed"] for x in checks)}
    target = ROOT / SESSION / "reports/A59-final-handoff-audit.json"
    if target.exists():
        raise FileExistsError("Preserve the existing final receipt; assign a new receipt path for a further observation.")
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"receipt": str(target.relative_to(ROOT)), "passed": result["passed"],
                      "checks": len(checks), "failed": [x for x in checks if not x["passed"]]}, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
