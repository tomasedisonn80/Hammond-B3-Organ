#!/usr/bin/env python3
"""Read retained evidence and the two owned documents; do not execute product gates."""
import argparse
import hashlib
import json
import platform
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    session = Path("docs/development/2026-11-14-reference-refinement")
    reports = repo / session / "reports"
    published = "0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b"
    tree = "f8144b771cda1264a8788f8297f5bfec999f4a08"
    checks = []

    def digest(data):
        return hashlib.sha256(data).hexdigest()

    def identity(path):
        data = path.read_bytes()
        return {"bytes": len(data), "sha256": digest(data)}

    def read_report(name):
        return json.loads((reports / name).read_text())

    def check(name, passed, detail=None):
        record = {"name": name, "passed": bool(passed)}
        if detail is not None:
            record["detail"] = detail
        checks.append(record)

    def git(*command):
        return subprocess.check_output(["git", *command], cwd=repo)

    baseline = read_report("A58-review-baseline.json")
    a49 = read_report("A49-coherent-final-build.json")
    a50 = read_report("A50-final-gallery-admission.json")
    a51 = read_report("A51-native-input-evidence.json")
    a54 = read_report("A54-current-handoff-status.json")
    a55 = read_report("A55-strict-ci-gate.json")
    a56 = read_report("A56-published-header-hosted-audit.json")
    source_comparison = read_report("A56-source-comparison.json")
    readme = (repo / "README.md").read_text()
    release = (repo / "docs/RELEASE_READINESS.md").read_text()
    marker = "## Historical standalone/scanner assessment"
    current, historical = release.split(marker, 1)
    historical = marker + historical
    check("published Git tree", git("rev-parse", published + "^{tree}").decode().strip() == tree)
    check("complete historical release suffix unchanged", identity_bytes(historical.encode()) == baseline["release_historical_suffix"])
    prefix = readme.split("\n\nA C++20", 1)[0].encode()
    check("README waveform prefix unchanged", identity_bytes(prefix) == baseline["readme_waveform_prefix"])
    stripped = readme
    additions = []
    for start in ("[A50's independent final gallery admission]", "[A51's independent native-input review]", "For the accepted `0881d1f4` product source,"):
        paragraphs = [p for p in readme.split("\n\n") if p.startswith(start)]
        check("one README addition: " + start, len(paragraphs) == 1)
        if len(paragraphs) == 1:
            block = paragraphs[0] + "\n\n"
            stripped = stripped.replace(block, "", 1)
            additions.append({"text": paragraphs[0], **identity_bytes(block.encode())})
    check("all original A47 README bytes preserved", identity_bytes(stripped.encode()) == baseline["readme_before"])
    for group in ("protected_evidence", "retained_asset_and_inventory_inputs"):
        for name, before in baseline[group].items():
            check("unchanged " + name, identity(repo / name) == before)

    links = []
    note = session / "notes/A58-release-evidence-closure.md"
    documents = {"README.md": readme, "docs/RELEASE_READINESS.md": current, str(note): (repo / note).read_text()}
    for document, content in documents.items():
        for raw in re.findall(r"!?\[[^\]\n]*\]\(([^\s)]+)\)", content):
            parsed = urlsplit(raw)
            if parsed.scheme or parsed.netloc:
                continue
            path = ((repo / document).parent / unquote(parsed.path)).resolve() if parsed.path else repo / document
            exists = path.exists()
            links.append({"document": document, "target": raw, "exists": exists})
            check("local link " + document + " -> " + raw, exists)
    check("note has at least 300 narrative words", len(re.sub(r"```.*?```", "", documents[str(note)], flags=re.S).split()) >= 300)

    check("A49 one complete local run", a49["outcome"] == "passed" and a49["full_suite_executions"] == 1 and a49["result_counts"] == {"ctest_not_run": 0, "discovered": 157, "executed": 157, "failed": 0, "passed": 157})
    check("A49 published-source freeze", a49["qualification"]["product_test_commit"] == published and a49["qualification"]["published_tree"] == tree and a49["qualification"]["product_test_inputs"] == 368 and a49["qualification"]["repository_files"] == 2625 and a49["qualification"]["markdown_files"] == 912 and a49["qualification"]["freeze"]["all_records_unchanged"])
    check("A49 exact recorded timings", a49["ctest_reported_seconds"] == 146.97 and round(a49["build"]["seconds"], 3) == 11.381)
    check("A49 capture binary distinction", a49["qualification"]["configuration"]["HAMMOND_ENABLE_MIDI"] == "OFF" and a49["qualification"]["native_executable_sha256"] != a50["build"]["executable"]["sha256"])
    check("A50 final admission", a50["status"] == "passed" and a50["checks"] == 611 and a50["failures"] == [] and len(a50["cases"]) == 8 and a50["gallery"]["files"] == 41 and a50["qualified_commit"] == published and a50["qualified_tree"] == tree)
    check("A50 gallery manifest identity", identity(repo / a50["gallery"]["path"] / "manifest.json") == a50["gallery"]["manifest"])
    check("A50 gallery provenance identity", identity(repo / a50["gallery"]["path"] / "provenance.json") == a50["gallery"]["provenance"])
    check("A51 bounded old-executable review", a51["checks_passed"] == a51["checks_total"] == 33 and a51["source_comparison"]["unchanged_paths"] == 159 and a51["source_comparison"]["inventory_paths"] == 161 and not a51["current_v4"]["new_native_os_input_run_by_A51"])
    check("A54 prior handoff audit retained", a54["status"] == "passed" and a54["checks_passed"] == 126 and a54["source"]["commit"] == published)
    check("A55 focused wiring result retained", a55["result"] == "passed_focused_local_wiring_checks" and a55["check_count"] == 16)
    check("A56 exact published identity", a56["tested_source"]["commit"] == published and a56["tested_source"]["tree"] == tree)
    check("A56 all twelve completed jobs", len(a56["jobs"]) == 12 and all(j["head_sha"] == published and j["source_tree_from_run"] == tree and j["status"] == "completed" and j["conclusion"] == "success" for j in a56["jobs"]))
    expected = {
        "Release (macOS AppleClang)": 138, "Release (Linux GCC)": 138,
        "Release (Windows MSVC)": 138, "Linux GCC ASan + UBSan + leaks": 138,
        "Native standalone (Linux GCC ASan + UBSan + leaks)": 16,
        "Native standalone (macOS AppleClang, MIDI ON)": 41,
        "Native standalone (Windows MSVC x64, MIDI ON)": 41,
        "Native standalone (Linux GCC, MIDI OFF)": 41,
        "Native standalone (Linux GCC, MIDI ON)": 41,
        "Native VST3 (Linux GCC)": 8, "Native VST3 (macOS AppleClang)": 7,
        "Native VST3 (Windows MSVC x64)": 7,
    }
    for job in a56["jobs"]:
        result = job["ctest"]
        check("A56 count " + job["name"], result["passed"] == result["total"] == expected[job["name"]] and result["failed"] == 0 and result["ordinal_sequence_complete"])
    materials = [j["material_acceptance"] for j in a56["jobs"] if "material_acceptance" in j]
    check("A56 all five material results", len(materials) == 5 and all(m["checks"] == 1071 and m["legacy_checks"] == 901 and m["header_checks"] == 170 and m["failures"] == 0 for m in materials))
    validators = [j["sdk_validator"] for j in a56["jobs"] if "sdk_validator" in j]
    check("A56 all three SDK validators", len(validators) == 3 and all(v["passed"] == 47 and v["failed"] == 0 for v in validators))
    exception = a56["core_sanitizer_policy"]["existing_exception"]
    check("A56 named existing quarantine-only leak exception", exception["test"] == "test_standalone_midi_backend_quarantine" and exception["override"] == "ASAN_OPTIONS=detect_leaks=0:halt_on_error=1" and not exception["in_native_sixteen"] and not exception["new_exception"])
    check("A56 native sanitizer sixteen retained", len(a56["native_sanitizer_policy"]["required_tests"]) == 16 and a56["core_sanitizer_policy"]["required_gates_inherit_leak_policy"])
    check("A56 future strict step not inherited", next(j for j in a56["jobs"] if j["name"] == "Release (Linux GCC)")["strict_current_refinement_session_step_executed"] is False and a56["source_comparison"]["workflows"][".github/workflows/ci.yml"]["working_equals_tested"] is False)
    check("A56 bounded source comparison", source_comparison["selected_count"] == 365 and source_comparison["all_selected_working_bytes_equal_published"] and "Documentation" in source_comparison["exclusions"])
    check("A55 current workflow bytes match A56 comparison", identity(repo / ".github/workflows/ci.yml")["sha256"] == source_comparison["workflow_comparison"][".github/workflows/ci.yml"]["working_sha256"])
    changed = set(git("diff", "--name-only", published, "--").decode().splitlines())
    changed.update(git("ls-files", "--others", "--exclude-standard").decode().splitlines())
    outside = sorted(name for name in changed if name not in {"README.md", "AGENTS.md", ".github/workflows/ci.yml"} and not name.startswith(("docs/", "examples/demos/standalone-interface-preview-v4/")))
    check("closure candidate remains documentation/gallery/reports and A55", not outside, {"changed_paths": len(changed), "outside_scope": outside})
    for name, declared in a56["retained_files"].items():
        check("A56 retained file " + name, identity(reports / name) == declared)
    excerpts = (reports / "A56-primary-log-excerpts.txt").read_text()
    check("Windows nonfatal warning and successful relocated payload retained", "Invalid escape sequence \\h" in excerpts and "Verified 19 installed files, MIDI WinMM, relocated help/dummy smoke, and the archived bytes." in excerpts and "Windows CMake path-escape warning" in current)

    selected = ["apps/standalone/InstrumentView.cpp", "apps/standalone/CMakeLists.txt", "apps/standalone/main.cpp", "apps/standalone/UiModel.cpp", "apps/standalone/Session.cpp", "src/Engine.cpp", "src/ControlStateIO.cpp", "data/parameter-registry.json", "cmake/InstallStandalone.cmake", "cmake/InstallHammondTools.cmake", "cmake/InstallCaptureTools.cmake"]
    selected += list(baseline["retained_asset_and_inventory_inputs"])
    for name in selected:
        check("published bytes " + name, (repo / name).read_bytes() == git("show", published + ":" + name))
    fonts = json.loads((repo / "assets/standalone/fonts/source-manifest.json").read_text())
    for record in fonts["fonts"] + [fonts["license"]]:
        check("declared font/notice identity " + record["file"], identity(repo / "assets/standalone/fonts" / record["file"])["sha256"] == record["sha256"])
    atlas = json.loads((repo / "assets/standalone/fonts/atlas-manifest.json").read_text())
    check("generated glyph identity", identity(repo / atlas["header"]["file"])["sha256"] == atlas["header"]["sha256"])
    art = json.loads((repo / "assets/standalone/reference/manifest.json").read_text())
    for record in art["assets"]:
        check("declared decorative crop " + record["file"], identity(repo / "assets/standalone/reference" / record["file"])["sha256"] == record["sha256"])
    check("declared reference JPEG ancestry", identity(repo / art["source"]["file"])["sha256"] == art["source"]["sha256"])
    check("declared original atlas identity", identity(repo / art["source"]["pdf"])["sha256"] == art["source"]["pdf_sha256"])
    for wording in ("Literal whole-interface 1:1 equality remains unmet", "G5 same-hertz failure", "R4 discrete parity", "R5 audible", "R6 runtime/Engine integration", "Engine remains dry", "47 sound", "B3CONTROLS4", "readers 1–3", "signing/notarization", "assistive-technology", "callback deadlines", "DAW", "final hosted run is future"):
        check("current boundary " + wording, wording in current)
    for stale in ("A46 owns the pending fresh v4 gallery", "Hosted qualification at this new header head remains pending"):
        check("obsolete current claim removed: " + stale, stale not in current)
    whitespace = subprocess.run(["git", "diff", "--check", "--", "README.md", "docs/RELEASE_READINESS.md"], cwd=repo, capture_output=True, text=True)
    check("owned shared-document diff check", whitespace.returncode == 0, {"exit": whitespace.returncode, "stdout": whitespace.stdout, "stderr": whitespace.stderr})
    evidence_names = ["A45-release-readiness.json", "A49-coherent-final-build.json", "A50-final-gallery-admission.json", "A51-native-input-evidence.json", "A54-current-handoff-status.json", "A55-strict-ci-gate.json", "A56-published-header-hosted-audit.json", "A56-source-comparison.json", "A56-primary-log-excerpts.txt"]
    failures = [c for c in checks if not c["passed"]]
    result = {
        "schema": "a58-release-evidence-closure-v1", "worker": "/root/w10_a58_release_evidence_closure", "wave": 10,
        "observed_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
        "cwd": str(repo), "source_commit": published, "source_tree": tree,
        "observed_local_head": git("rev-parse", "HEAD").decode().strip(),
        "scope": "Focused retained-report, link, source-byte, asset-provenance and owned-document consistency checks. No build, CTest, native process, image generation, remote access, publication or actual completion checker.",
        "status": "passed" if not failures else "failed", "checks_total": len(checks), "checks_passed": len(checks) - len(failures),
        "checks": checks, "failures": failures, "links": links, "local_link_occurrences": len(links),
        "owned_documents": {name: identity(repo / name) for name in documents},
        "readme_additions": additions, "baseline": identity(reports / "A58-review-baseline.json"),
        "auditor": identity(Path(__file__)), "evidence": {name: identity(reports / name) for name in evidence_names},
        "initial_audit": {"file": "A58-initial-document-check.json", **identity(reports / "A58-initial-document-check.json"), "classification": "346/347 initial document checks; the audit output link was absent before its first creation. No product execution or repair."},
        "limits": ["A56 primary logs supply hosted execution claims; this worker independently reads their retained evidence without making a fresh hosted observation.", "A49 freezes earlier documentation; the final candidate and A55 step need their own final integrity/completion/hosted results.", "The previous X11 binary and accepted dummy-driver v4 endpoints remain distinct scopes.", "R4 remains with its separate owner; product, physical, display/device/DAW, accessibility, deadline, signing and existing rights gates remain open."],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks_passed": result["checks_passed"], "checks_total": len(checks), "local_link_occurrences": len(links), "failures": failures}, indent=2))
    return bool(failures)


def identity_bytes(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


if __name__ == "__main__":
    raise SystemExit(main())
