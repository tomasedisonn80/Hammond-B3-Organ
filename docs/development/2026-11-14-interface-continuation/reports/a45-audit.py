#!/usr/bin/env python3
"""Bounded, read-only documentation/source audit; no builds or test execution."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unicodedata
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[4]
SESSION = "docs/development/2026-11-14-interface-continuation"
GUIDES = (
    "STANDALONE_INSTALL.md", "STANDALONE_APP.md", "STANDALONE_MODEL.md",
    "MIDI_UI_RUNBOOK.md", "PRESET_RUNBOOK.md", "INTERFACE_RUNBOOK.md",
)
DOCUMENTS = [
    "README.md", "AGENTS.md", "docs/PLAN.md", "docs/STATUS.md",
    "docs/NEXT_STEPS.md", "docs/PROJECT_GUIDE.md",
    "docs/INTERFACE_CONTINUATION_SCOPE.md", "docs/INTERFACE_WORKSPACE_CONTRACT.md",
    "docs/INTERFACE_GEOMETRY_CONTRACT.md", "docs/INTERFACE_INSPECTION_CONTRACT.md",
    "docs/PRESET_SELECTION_CONTRACT.md", "docs/PRESET_STATE_PARAMETER_CONTRACT.md",
    "docs/PARAMETERS.md", "docs/PARAMETER_BRIDGE.md", "docs/CONTROL_STATE_FORMAT.md",
    *["docs/" + name for name in GUIDES],
    SESSION + "/README.md", SESSION + "/CHECKPOINT.md",
    "examples/demos/standalone-interface-preview-v1/README.md",
    "docs/reviews/INTERFACE_REFERENCE_COMPARISON.md",
]
SOURCE = [
    "include/hammond/ParameterBridge.h", "src/ParameterBridge.cpp",
    "data/parameter-registry.json", "src/ControlState.cpp", "src/ControlStateIO.cpp",
    "apps/standalone/UiModel.h", "apps/standalone/UiModel.cpp",
    "apps/standalone/main.cpp", "apps/standalone/MidiInput.cpp",
    "apps/standalone/InspectionModel.cpp", "cmake/InstallStandalone.cmake",
    "apps/standalone/native_tests/test_standalone_install.py",
    ".github/workflows/standalone.yml", "tests/test_parameters.py",
    "tools/chapel_controls.py", "docs/design/atlas-reference.json",
    "examples/demos/standalone-interface-preview-v1/provenance.json",
    "examples/demos/standalone-interface-preview-v1/manifest.json",
    SESSION + "/assignments.json",
    *[SESSION + "/reports/" + name for name in (
        "publication-4.json", "platform-repair-hosted.json", "a34-result.json",
        "a36-status-clarity.json", "a37-final-operator-flow.json",
        "a39-ci-inventory.json", "a40-result.json", "root-guide-freshness.json",
        "a45-proposed-guide-edits.json",
    )],
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def headings(path):
    result = set()
    seen = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        name = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", match[1])
        name = name.lower().replace(" ", "-")
        name = "".join(c for c in name if c in "-_" or unicodedata.category(c)[0] in "LN")
        nth = seen.get(name, 0)
        seen[name] = nth + 1
        result.add(name if nth == 0 else f"{name}-{nth}")
    return result


def scan_links():
    counts = {"local": 0, "repository_url_mapped_locally": 0, "other_external_unchecked": 0}
    bad = []
    installed_bad = []
    fragments = 0
    relative_installed = 0
    for document in DOCUMENTS:
        path = ROOT / document
        source = path.read_text(encoding="utf-8")
        for match in re.finditer(r"!?\[[^\]\n]*\]\(([^)]+)\)", source):
            raw = match[1].strip().strip("<>")
            url = urlsplit(raw)
            kind = "local"
            if url.scheme:
                prefix = "/tomasedisonn80/Hammond-B3-Organ/"
                if url.netloc == "github.com" and url.path.startswith(prefix):
                    relative = url.path[len(prefix):]
                    if relative.startswith(("blob/main/", "tree/main/")):
                        target = ROOT / unquote(relative.split("/", 2)[2])
                        kind = "repository_url_mapped_locally"
                    else:
                        counts["other_external_unchecked"] += 1
                        continue
                else:
                    counts["other_external_unchecked"] += 1
                    continue
            else:
                target = path.parent / unquote(url.path) if url.path else path
                if path.name in GUIDES and url.path:
                    relative_installed += 1
                    if url.path not in (*GUIDES, "THIRD_PARTY_NOTICES.md"):
                        installed_bad.append({"source": document, "target": raw})
            counts[kind] += 1
            record = {"source": document, "line": source.count("\n", 0, match.start()) + 1, "target": raw}
            if not target.exists():
                bad.append({**record, "reason": "missing local target"})
            elif url.fragment and target.suffix.lower() == ".md":
                fragments += 1
                if unquote(url.fragment) not in headings(target):
                    bad.append({**record, "reason": "heading fragment not found by bounded heading scan"})
    return {"counts": counts, "markdown_fragments_checked": fragments, "issues": bad,
            "installed_relative_links_checked": relative_installed, "installed_relative_issues": installed_bad,
            "limits": "Inline Markdown links and ATX headings in listed documents only; repository URLs resolved locally, no external HTTP validation."}


def inventory():
    install = (ROOT / "cmake/InstallStandalone.cmake").read_text()
    native_test = (ROOT / "apps/standalone/native_tests/test_standalone_install.py").read_text()
    workflow = (ROOT / ".github/workflows/standalone.yml").read_text()
    return {name: {
        "cmake": f"/docs/{name}\"" in install,
        "install_acceptance": f'"{name}": Path("docs/{name}")' in native_test,
        "hosted_inventory": f'metadata + "{name}": repo / "docs/{name}"' in workflow,
    } for name in GUIDES}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    paths = sorted(set(DOCUMENTS + SOURCE))
    before = {p: digest(ROOT / p) for p in paths}
    registry = json.loads((ROOT / "data/parameter-registry.json").read_text())
    records = sorted(registry["parameters"], key=lambda row: row["id"])
    old = [record for record in records if record["id"] < 20480]
    old_digest = hashlib.sha256(json.dumps(old, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()
    result = {
        "schema": 1, "assignment": 45, "agent": "/root/w08_a45_documentation_freshness",
        "head": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}"),
        "fetched_origin_main": git("rev-parse", "origin/main"),
        "documents": DOCUMENTS, "input_sha256": before,
        "links": scan_links(), "installed_guide_wiring": inventory(),
        "parameter_source_inspection": {"current_count": len(records), "legacy_count": len(old),
            "legacy_complete_records_sha256": old_digest,
            "frozen_legacy_digest_matches": old_digest == "13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad",
            "appended_ids": [record["id"] for record in records if record["id"] >= 20480]},
        "executed_scope": "Only source/data identity, bounded links, package wiring and syntax inspection. No build, CTest, native run, external browsing or physical qualification.",
    }
    result["changed_during_audit"] = [p for p in paths if digest(ROOT / p) != before[p]]
    output = ROOT / args.output
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"report": args.output, "documents": len(DOCUMENTS), "inputs": len(paths),
                      "links": result["links"], "parameter": result["parameter_source_inspection"],
                      "changed_during_audit": result["changed_during_audit"]}, indent=2))


if __name__ == "__main__":
    main()
