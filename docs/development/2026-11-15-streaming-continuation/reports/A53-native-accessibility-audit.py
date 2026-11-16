#!/usr/bin/env python3
"""Read-only source/evidence audit; writes only the selected JSON report.

No compilation, native executable, OS session, device or product test is run.
Source markers support the accompanying review; they are not behavior tests.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess


REVIEWED = "2f57723d9ec806fe8f721c317ef8c1a38d63b532"
PREVIOUS = "af2b74760ee195c9497b314a1a29172f5238dd44"
SESSION = "docs/development/2026-11-15-streaming-continuation"
OLD_SESSION = "docs/development/2026-11-14-reference-refinement"
REVIEW = "docs/reviews/NATIVE_ACCESSIBILITY_JOURNEY_NEXT_REVIEW.md"
NOTE = f"{SESSION}/notes/A53.md"
SCRIPT = f"{SESSION}/reports/A53-native-accessibility-audit.py"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output.resolve()
    checks: list[dict] = []

    def git(*arguments: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(repo), *arguments])

    def read(path: str) -> bytes:
        return (repo / path).read_bytes()

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    def identity(path: str) -> dict:
        data = read(path)
        return {"bytes": len(data), "sha256": sha(data)}

    head = git("rev-parse", "HEAD").decode().strip()
    tree = git("rev-parse", "HEAD^{tree}").decode().strip()
    check("reviewed_source_commit_resolves",
          git("rev-parse", f"{REVIEWED}^{{commit}}").decode().strip() == REVIEWED,
          {"reviewed_commit": REVIEWED, "observed_head": head, "observed_tree": tree,
           "interpretation": "Later unrelated documentation commits are permitted; reviewed source bytes are checked separately."})
    subtree_ids = {}
    for path in ("apps/standalone", "examples/demos/upper-rack-material-v1"):
        previous = git("rev-parse", f"{PREVIOUS}:{path}").decode().strip()
        reviewed = git("rev-parse", f"{REVIEWED}:{path}").decode().strip()
        changes = git("diff", "--name-only", REVIEWED, "--", path).decode().splitlines()
        untracked = git("ls-files", "--others", "--exclude-standard", "--", path).decode().splitlines()
        subtree_ids[path] = {"previous": previous, "reviewed": reviewed,
                             "worktree_changes": changes, "untracked": untracked}
        check(f"unchanged_subtree:{path}", previous == reviewed and not changes and not untracked,
              subtree_ids[path])

    a42_path = f"{SESSION}/reports/A42-source-audit.json"
    a42 = json.loads(read(a42_path))
    sources = {}
    for path, old in a42["source_identities"].items():
        data = read(path)
        sources[path] = {**identity(path), "matches_a42": sha(data) == old["sha256"],
                         "matches_reviewed_git_blob": data == git("show", f"{REVIEWED}:{path}")}
    focused_test = "apps/standalone/tests/test_standalone_percussion_reference.cpp"
    for path in (focused_test, "apps/standalone/AudioDevice.cpp", "apps/standalone/Session.cpp"):
        sources[path] = {**identity(path), "matches_reviewed_git_blob":
                         read(path) == git("show", f"{REVIEWED}:{path}")}
    check("selected_source_bindings", all(v["matches_reviewed_git_blob"] and v.get("matches_a42", True)
                                         for v in sources.values()), {"files": len(sources)})

    gallery_path = "examples/demos/upper-rack-material-v1/inputs/source-qualification.json"
    gallery = json.loads(read(gallery_path))
    gallery_matches = {p: sha(read(p)) == expected for p, expected in gallery["source_sha256"].items()}
    check("ten_original_gallery_source_bindings", len(gallery_matches) == 10 and all(gallery_matches.values()),
          gallery_matches)

    production_paths = sorted(p for p in (repo / "apps/standalone").iterdir()
                              if p.suffix in (".cpp", ".h") or p.name == "CMakeLists.txt")
    searches = {}
    patterns = {
        "native_provider": r"AT-SPI|atspi|\batk\b|UIAutomation|UIA_|NSAccessibility|IAccessible|accessibility",
        "reduced_motion_preference": r"reduced[ _-]?motion|prefers[ _-]?reduced|reduce[ _-]?motion",
        "numeric_text_input": r"SDL_TEXTINPUT|SDL_TEXTEDITING|SDL_StartTextInput|SDL_StopTextInput",
    }
    for name, pattern in patterns.items():
        hits = []
        for path in production_paths:
            for number, line in enumerate(path.read_text().splitlines(), 1):
                if re.search(pattern, line, re.IGNORECASE):
                    hits.append({"path": str(path.relative_to(repo)), "line": number, "text": line})
        searches[name] = {"pattern": pattern, "files": len(production_paths), "hits": hits}
        check(f"bounded_absence:{name}", not hits,
              "Top-level standalone production source and target file only; no OS observation inferred.")

    model = read("apps/standalone/UiModel.cpp").decode()
    header = read("apps/standalone/UiModel.h").decode()
    app = read("apps/standalone/main.cpp").decode()
    test = read(focused_test).decode()
    resize_body = model.split("bool UiModel::resize(", 1)[1].split("bool UiModel::set_workspace(", 1)[0]
    presentation_body = model.split("bool UiModel::set_presentation(", 1)[1].split("UiActions UiModel::activate(", 1)[0]
    check("focus_id_retention_source", "UiControlId focus{};" in header and
          all("view_.focus =" not in body and "focus_control(" not in body and
              "layout_ = candidate;" in body for body in (resize_body, presentation_body)) and
          "if (order[index] == view.focus)" in model,
          "Read with manual branch/control-flow review; resize and presentation preserve ID and Tab searches by ID.")
    check("percussion_order_and_parameter_source",
          "percussion_order{0, 2, 3, 1}" in model and
          "parameter = 12288U + control.index" in model and
          "UiControlKind::Percussion, Manual::Upper, DrawbarBank::A, static_cast<std::uint8_t>(index)" in model,
          {"wide_indices": [0, 2, 3, 1], "compact_flat_indices": [0, 1, 2, 3],
           "one_based_tab_positions": [57, 58, 59, 60]})
    check("existing_focused_reflow_test_source", all(s in test for s in (
          "void tab_cycle_and_semantic_reflow()", "for (const auto index : kReferenceOrder)",
          "UiPoint{1399, 820}", "UiPoint{1400, 819}", "UiPoint{1400, 820}",
          "CHECK(model.view().focus == id && model.view().controls == controls);",
          "CHECK(tap(model, UiKey::Tab, true).count == 0 && model.view().focus == id);")),
          "Existing model coverage inspected; not executed by A53.")
    check("focus_inventory_source", all(s in header for s in (
          "kUiCommonControlCount = 10;", "kUiMaxControls = 68;")) and
          "kUiMaxControls + kManualCount + 1" in model,
          {"ordinary_play": 68, "common": 10, "roving_groups": 3,
           "play_tab_stops": 71, "playing_keys": [61, 61, 25], "presets": 24})
    check("modal_source_inventory", all(s in app for s in (
          "return overlay_ == ViewOverlay::Midi ? 11U : 6U;",
          "modal_focus_ = overlay == ViewOverlay::Help ? 5U : 0U;",
          "ui_.set_text_entry_active(true);", "ui_.set_text_entry_active(false);")),
          "Manual early-return review establishes Help's one effective Close; text-entry flag is suppression.")
    check("ordinary_exit_not_generic_error_count_gate", "return fatal_failure_ || midi_startup_failed_ || midi_shutdown_failed_ ||" in app,
          "Manual run() review: generic error_count_ is part of replay health, not the ordinary exit predicate.")

    qualification_path = f"{SESSION}/reports/final-coherent-qualification.json"
    qualification = json.loads(read(qualification_path))
    log_info = qualification["logs"]["final-coherent-ctest"]
    log_path = f"{SESSION}/reports/{log_info['path']}"
    log_bytes = gzip.decompress(read(log_path))
    test_lines = [line for line in log_bytes.decode().splitlines() if "test_standalone_percussion_reference" in line]
    check("historical_focused_test_log", sha(log_bytes) == log_info["raw_sha256"] and
          any("Passed" in line for line in test_lines), test_lines)
    inventory_info = qualification["source_inventory"]
    inventory_path = f"{SESSION}/reports/{inventory_info['path']}"
    inventory_bytes = gzip.decompress(read(inventory_path))
    inventory = json.loads(inventory_bytes)
    required_qualified_paths = ["apps/standalone/UiModel.h", "apps/standalone/UiModel.cpp", focused_test]
    check("historical_qualification_binds_reviewed_model_and_test",
          sha(inventory_bytes) == inventory_info["raw_sha256"] and
          all(inventory[p] == sha(read(p)) for p in required_qualified_paths), required_qualified_paths)

    old_diag_path = f"{OLD_SESSION}/reports/desktop-acceptance.json"
    old_review_path = f"{OLD_SESSION}/reports/root-desktop-acceptance-review.json"
    old_source_path = f"{OLD_SESSION}/reports/root-desktop-acceptance-source.json"
    old = json.loads(read(old_diag_path))
    old_review = json.loads(read(old_review_path))
    old_obs = old["presentation"]["observations"]
    check("retained_x11_original_diagnostic_hash", sha(read(old_diag_path)) == old_review["diagnostics_sha256"],
          identity(old_diag_path))
    check("retained_x11_review_and_source_hashes",
          sha(read(old_review_path)) == "ff6b371a6b3e796c758551c9ec53101015097d7af364760b69724a60f275255a" and
          sha(read(old_source_path)) == "6e6970c797fd6f55bc736e9a5486a72f1739d4f44a0d779d39eae4b24e9dff74",
          "Matches immutable identities in the prior independent review.")
    old_summary = {
        "binary_sha256_from_original_review": old_review["binary_sha256"],
        "video_driver": old["runtime"]["video_driver"], "renderer": old["runtime"]["renderer"],
        "audio_driver": old["audio"]["driver"], "observations": len(old_obs),
        "observations_truncated": old["presentation"]["observations_truncated"],
        "keyboard_pedal_widths": [old_obs[i]["window_width"] for i in (9, 10)],
        "keyboard_pedal_counts": [old_obs[i]["held_targets"]["pedals"] for i in (9, 10, 11)],
        "pointer_upper_counts": [old_obs[i]["held_targets"]["upper"] for i in (13, 14, 15, 16)],
        "final_capture": old_obs[-1]["pointer_capture"], "session": old["session"],
        "callbacks": old["audio"]["callback_count"], "recorded_actions": old_review["actions"],
    }
    check("retained_x11_scope_and_unknown_discard", len(old_obs) == 19 and
          not old_summary["observations_truncated"] and old_summary["keyboard_pedal_counts"] == [1, 1, 0] and
          old_summary["pointer_upper_counts"] == [1, 0, 1, 0] and
          old["session"]["discarded_commands"] == 1 and
          not old["session"]["running_after_shutdown"] and not old["session"]["held_after_shutdown"],
          "Source-bound old observations only; no new native input or inferred discarded-command identity.")

    owned = {p: identity(p) for p in (REVIEW, NOTE, SCRIPT)}
    check("note_at_most_2000_bytes", owned[NOTE]["bytes"] <= 2000, owned[NOTE])
    links = []
    original_report = (repo / SESSION / "reports/A53-native-accessibility-audit.json").resolve()
    for path in (REVIEW, NOTE):
        data = read(path)
        text = data.decode("utf-8")
        check(f"markdown_format:{path}", data.endswith(b"\n") and not data.endswith(b"\n\n") and
              b"\r" not in data and all(line == line.rstrip() for line in text.splitlines()),
              "UTF-8, one final newline, no CR or trailing whitespace.")
        for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (repo / Path(path).parent / target.split("#", 1)[0]).resolve()
            exists = resolved.is_file() or (resolved == output and resolved == original_report)
            links.append({"from": path, "target": target, "exists": exists})
    check("owned_markdown_local_links", all(link["exists"] for link in links), {"links": len(links)})

    evidence_paths = ["AGENTS.md", "docs/PLAN.md", "docs/REFERENCE_REFINEMENT_DESKTOP.md",
                      "docs/INTERFACE_WORKSPACE_CONTRACT.md", "docs/design/NATIVE_ACCESSIBILITY_JOURNEY_NEXT.md",
                      "docs/reviews/REFERENCE_REFINEMENT_NATIVE_INPUT.md", a42_path, gallery_path,
                      qualification_path, log_path, inventory_path, old_diag_path, old_review_path, old_source_path]
    report = {
        "schema_version": 1, "worker": "/root/w09_a53", "wave": 9,
        "recorded_utc": datetime.now(timezone.utc).isoformat(), "cwd": str(repo),
        "kind": "independent-source-retained-evidence-and-owned-document-audit",
        "reviewed_commit": REVIEWED, "previous_proposal_commit": PREVIOUS,
        "observed_head": head, "observed_tree": tree, "subtree_identities": subtree_ids,
        "source_identities": sources, "evidence_identities": {p: identity(p) for p in evidence_paths},
        "source_searches": searches, "retained_x11_summary": old_summary,
        "owned_outputs": owned, "local_links": links, "checks": checks,
        "status": "pass" if all(c["passed"] for c in checks) else "fail",
        "acceptance": "Source/evidence bindings and document integrity only; native journeys remain unexecuted.",
        "review_disposition": "Admit A42 bounded journey plan with operator corrections and bridge prerequisites; no focus-transfer defect established.",
        "executed": {"git_reads_and_hashes": True, "source_and_json_inspection": True,
                     "historical_log_read": True, "native_execution": False, "build": False,
                     "product_tests": False, "os_browser_cua_or_devices": False},
        "limitations": [
            "Absence searches supplement manually reviewed source/link composition; they are not a native tree inspection.",
            "Historical CTest and X11 outputs qualify their original source/configuration, not a new A53 execution.",
            "No repaired hosted CI result is asserted.",
            "No implementation, screen-reader, real display/device, callback deadline or physical-fidelity acceptance.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": report["status"], "checks": len(checks),
                      "failed": [c["name"] for c in checks if not c["passed"]],
                      "note_bytes": owned[NOTE]["bytes"], "note_sha256": owned[NOTE]["sha256"],
                      "output": str(output)}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
