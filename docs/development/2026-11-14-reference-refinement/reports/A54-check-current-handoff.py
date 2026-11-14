#!/usr/bin/env python3
"""Read-only scoped documentation/source audit; never build, test or run the app."""

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": sha(data)}


def heading_ids(text):
    counts = {}
    result = set()
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        value = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", match.group(1))
        value = re.sub(r"<[^>]*>", "", value).lower()
        value = re.sub(r"[^\w\- ]", "", value).replace(" ", "-")
        count = counts.get(value, 0)
        counts[value] = count + 1
        result.add(value if count == 0 else f"{value}-{count}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("{}\n")
    session = "docs/development/2026-11-14-reference-refinement/"
    reports = repo / session / "reports"
    baseline = json.loads((reports / "A54-current-baseline.json").read_text())
    commit = "0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b"
    tree = "f8144b771cda1264a8788f8297f5bfec999f4a08"
    gallery_binary = "01fe78a55b7a9bc72228dafe175f5a8eb48481c063f217606474d4dff682320f"
    checks = []

    def check(name, condition, detail=None):
        item = {"name": name, "passed": bool(condition)}
        if detail is not None:
            item["detail"] = detail
        checks.append(item)

    def git(*arguments):
        return subprocess.check_output(["git", *arguments], cwd=repo)

    check("published Git tree", git("rev-parse", commit + "^{tree}").decode().strip() == tree)
    scopes = {}
    current = {
        "docs/STATUS.md": "## Current reference refinement and nominal propagation qualification",
        "docs/NEXT_STEPS.md": "## Current reference-refinement closure and shared continuation",
    }
    for rel, entry in baseline["documents"].items():
        data = (repo / rel).read_bytes()
        text = data.decode()
        if rel in current:
            prefix = data[:entry["protected_prefix_bytes"]]
            check(rel + " protected concurrent prefix", sha(prefix) == entry["protected_prefix_sha256"])
            marker = entry["historical_suffix_marker"]
            suffix = marker + text.split(marker, 1)[1]
            check(rel + " historical suffix", sha(suffix.encode()) == entry["historical_suffix_sha256"])
            scopes[rel] = current[rel] + text.split(current[rel], 1)[1].split(marker, 1)[0]
        elif rel.endswith("DEVELOPMENT_LOG.md"):
            marker = entry["historical_body_start"]
            body = marker + text.split(marker, 1)[1]
            check(rel + " every prior dated entry", sha(body.encode()) == entry["historical_body_sha256"])
            scopes[rel] = text.split(marker, 1)[0]
        else:
            scopes[rel] = text
    note = session + "notes/A54-current-handoff-status.md"
    scopes[note] = (repo / note).read_text()
    word_count = len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b", scopes[note]))
    check("substantive assigned note", word_count >= 300, {"words_including_headings": word_count})

    links = []
    for rel, body in scopes.items():
        for match in re.finditer(r"!?\[[^]\n]*\]\(([^)\n]+)\)", body):
            raw = match.group(1).split(' "', 1)[0].strip("<>")
            parsed = urlsplit(raw)
            if parsed.scheme or parsed.netloc:
                continue
            target = ((repo / rel).parent / unquote(parsed.path)).resolve() if parsed.path else repo / rel
            exists = target.exists()
            anchor_ok = not parsed.fragment
            if parsed.fragment and exists and target.suffix.lower() == ".md":
                anchor_ok = unquote(parsed.fragment) in heading_ids(target.read_text())
            elif parsed.fragment and exists:
                anchor_ok = True
            item = {"document": rel, "target": raw, "exists": exists, "anchor_checked": bool(parsed.fragment)}
            links.append(item)
            check("local link " + rel + " -> " + raw, exists and anchor_ok)

    a49 = json.loads((reports / "A49-coherent-final-build.json").read_text())
    q49 = a49["qualification"]
    check("A49 exact one full execution", a49["full_suite_executions"] == 1 and a49["result_counts"] == {"ctest_not_run": 0, "discovered": 157, "executed": 157, "failed": 0, "passed": 157})
    check("A49 timings", round(a49["build"]["seconds"], 3) == 11.381 and a49["ctest_reported_seconds"] == 146.97)
    check("A49 source and freeze counts", (q49["product_test_commit"], q49["published_tree"], q49["repository_files"], q49["markdown_files"], q49["product_test_inputs"], q49["dependency_files"]) == (commit, tree, 2625, 912, 368, 1758))
    check("A49 retained freeze result", q49["freeze"]["all_records_unchanged"] and q49["freeze"]["all_dependency_records_unchanged"] and q49["freeze"]["postbuild_execution_inputs_unchanged_during_tests"])
    a50 = json.loads((reports / "A50-final-gallery-admission.json").read_text())
    check("A50 admission and source", (a50["status"], a50["checks"], a50["qualified_commit"], a50["qualified_tree"], a50["build"]["executable"]["sha256"]) == ("passed", 611, commit, tree, gallery_binary))
    gallery = repo / a50["gallery"]["path"]
    for name in ["manifest", "provenance", "readme"]:
        filename = {"manifest": "manifest.json", "provenance": "provenance.json", "readme": "README.md"}[name]
        check("v4 " + filename + " matches A50", identity(gallery / filename) == a50["gallery"][name])
    a51 = json.loads((reports / "A51-native-input-evidence.json").read_text())
    check("A51 exact audit limits", (a51["checks_total"], a51["checks_passed"], a51["source_comparison"]["inventory_paths"], a51["source_comparison"]["unchanged_paths"]) == (33, 33, 161, 159) and not a51["current_v4"]["new_native_os_input_run_by_A51"])

    selected_sources = [
        "CMakeLists.txt", "apps/standalone/CMakeLists.txt", "apps/standalone/InstrumentView.cpp",
        "apps/standalone/main.cpp", "apps/standalone/UiModel.cpp", "apps/standalone/Session.cpp",
        "src/Engine.cpp", "src/ControlStateIO.cpp", "data/parameter-registry.json",
        "cmake/InstallStandalone.cmake", "cmake/InstallHammondTools.cmake", "cmake/InstallCaptureTools.cmake",
        "tools/acquire_sdl2.py", "tools/acquire_rtmidi.py", "tools/check_refinement_session.py",
        "data/dependencies/sdl2-lock.json", "data/dependencies/rtmidi-lock.json",
    ]
    source_identities = {}
    for rel in selected_sources:
        local = (repo / rel).read_bytes()
        published = git("show", commit + ":" + rel)
        source_identities[rel] = identity(repo / rel)
        check("selected source matches published " + rel, local == published)

    setups = {}
    for directory, midi, x11, binary_sha in [
        ("build-native", "OFF", False, q49["native_executable_sha256"]),
        ("build-desktop", "ON", True, gallery_binary),
    ]:
        root = repo.parent / directory
        cache_text = (root / "CMakeCache.txt").read_text()
        cache = dict(re.findall(r"^([^#/:\r\n][^:=\r\n]*):[^=\r\n]+=(.*)$", cache_text, re.M))
        config = (root / "_sdl2/include-config-release/SDL2/SDL_config.h").read_text()
        effective_x11 = "#define SDL_VIDEO_DRIVER_X11 1" in config
        effective_alsa = "#define SDL_AUDIO_DRIVER_ALSA 1" in config
        executable = root / "apps/standalone/hammond_standalone"
        keys = ["CMAKE_BUILD_TYPE", "BUILD_TESTING", "HAMMOND_BUILD_STANDALONE", "HAMMOND_ENABLE_MIDI", "HAMMOND_BUILD_VST3", "HAMMOND_ENABLE_SANITIZERS", "SDL_X11", "SDL_ALSA"]
        setups[directory] = {"cache": {key: cache[key] for key in keys}, "effective_x11": effective_x11, "effective_sdl_alsa": effective_alsa, "executable": identity(executable)}
        check(directory + " existing configuration", cache["CMAKE_BUILD_TYPE"] == "Release" and cache["HAMMOND_ENABLE_MIDI"] == midi and cache["BUILD_TESTING"] == "ON" and cache["HAMMOND_BUILD_STANDALONE"] == "ON" and cache["HAMMOND_BUILD_VST3"] == "OFF" and cache["HAMMOND_ENABLE_SANITIZERS"] == "OFF" and effective_x11 == x11 and not effective_alsa)
        check(directory + " unchanged named executable", sha(executable.read_bytes()) == binary_sha)

    handoff = scopes["docs/REFERENCE_REFINEMENT_HANDOFF.md"]
    for text in ["15 files with MIDI disabled; 19 with MIDI enabled", "23 files:", "57 files:"]:
        check("component inventory " + text, text in handoff)
    check("CaptureTools source fixes 57-file inventory", "exactly 57 files" in (repo / "cmake/InstallCaptureTools.cmake").read_text())
    check("documented CMake options exist", all("option(" + option in (repo / "CMakeLists.txt").read_text() for option in ["HAMMOND_BUILD_STANDALONE", "HAMMOND_ENABLE_MIDI", "HAMMOND_BUILD_VST3"]))
    check("focused standalone build target exists", "add_custom_target(hammond_standalone_test_inputs" in (repo / "apps/standalone/CMakeLists.txt").read_text())
    check("required integrity gate exists in completed A49 discovery", "python_test_repository_integrity" in a49["discovered_names"])
    shared_files = list(baseline["documents"])
    diff = subprocess.run(["git", "diff", "--check", "--", *shared_files], cwd=repo, text=True, capture_output=True)
    check("owned shared documentation git diff --check", diff.returncode == 0, {"exit": diff.returncode, "stdout": diff.stdout, "stderr": diff.stderr})

    evidence_names = ["A43-hosted-fixture-closure.json", "A44-hosted-sanitizer-audit.json", "A49-coherent-final-build.json", "A50-final-gallery-admission.json", "A51-native-input-evidence.json", "coherent-result.json", "root-windows-2e.log", "root-header-publication.json"]
    failures = [item for item in checks if not item["passed"]]
    result = {
        "schema": 1, "worker": "/root/w09_a54_current_handoff_status", "observed_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Scoped current documentation/link/source/cache/report inspection; no build, CTest, native app, install, desktop, final strict checker, network refresh or publication.",
        "command": ["python3", "-B", session + "reports/A54-check-current-handoff.py", "--repo", str(repo), "--output", str(output)],
        "source": {"commit": commit, "tree": tree, "observed_local_head": git("rev-parse", "HEAD").decode().strip(), "cached_origin_main": git("rev-parse", "origin/main").decode().strip(), "new_remote_observation": False},
        "status": "passed" if not failures else "failed", "checks_total": len(checks), "checks_passed": len(checks) - len(failures), "checks": checks, "failures": failures,
        "local_links_checked": len(links), "links": links,
        "owned_documents": {rel: identity(repo / rel) for rel in scopes},
        "checker_identity": identity(Path(__file__).resolve()),
        "protected_history_baseline": identity(reports / "A54-current-baseline.json"),
        "evidence_identities": {name: identity(reports / name) for name in evidence_names},
        "selected_published_source_identities": source_identities, "existing_build_inspection": setups,
        "component_counts": {"Standalone_MIDI_OFF": 15, "Standalone_MIDI_ON": 19, "OfflineTools": 23, "CaptureTools": 57},
        "current_hosted_boundary": "Twelve successful 0881 job statuses are root's live-checkpoint/task observation, not an independent primary-log audit by A54; A56 owns that later exact-source audit.",
        "audit_setup_history": {"initial_failure": "The first scoped audit's cache-key regex crossed line breaks and raised KeyError for CMAKE_BUILD_TYPE. Restricting the matcher to one line corrected the audit; no product source, build or test was involved.", "tool_returned_trace": identity(reports / "A54-initial-audit-error.log")},
        "final_gates_not_run": ["actual strict sixty-record checker", "affected full repository-integrity suite", "expected-head publication and final-head CI"],
        "limits": ["Selected source matches do not establish a new full build, clean worktree or hermetic environment.", "All linked prior execution results remain their authors' exact-source evidence.", "The 22:30 resource and 54-dispatched/51-accepted counts are snapshots; the live manifest/checkpoint own later changes.", "R4 belongs to the separate waveform owner; R5/R6, scanner G5, device/accessibility/deadline/physical gates and literal 1:1 equality remain open."]
    }
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": result["status"], "checks_total": len(checks), "checks_passed": result["checks_passed"], "links": len(links), "failures": failures, "output": str(output)}, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
