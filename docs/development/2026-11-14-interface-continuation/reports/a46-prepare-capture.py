#!/usr/bin/env python3
"""A46 preflight: qualify existing A44 native inputs, without rebuilding."""

import hashlib
import importlib.util
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
REPORTS = Path(__file__).resolve().parent
BUILD = REPO.parent / "build-native"
EXE = BUILD / "apps/standalone/hammond_standalone"
PUBLISHED = "8673713a484c40e26ac7810c7c4cbc22fa874426"
PUBLISHED_TREE = "e11bd68d6051f663631579ef235325a8775f8133"
spec = importlib.util.spec_from_file_location("capture", REPO / "tools/capture_standalone_interface.py")
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


def read(name):
    return json.loads((REPORTS / name).read_text())


def a44_digest(files):
    return hashlib.sha256("".join(f"{p}\0{v}\n" for p, v in sorted(files.items())).encode()).hexdigest()


def main():
    a44 = read("a44-midi-on-source-after-build.json")
    b44 = read("a44-build-result.json")
    f44 = read("a44-final-package-result.json")
    files = capture.inventory(capture.production_paths(REPO), REPO)
    by_sha = {name: value["sha256"] for name, value in files.items()}
    builds = capture.inventory(capture.build_paths(BUILD), BUILD)
    assert len(files) == 98 and len(builds) == 13
    assert by_sha == a44["production_sha256"]
    assert capture.identity(EXE) == b44["builds"]["midi-on"]["executable"] == f44["final_packages"]["midi-on"]["executable"]
    assert a44_digest(by_sha) == a44["production_inventory_sha256"] == f44["production_inventory_sha256"]
    assert capture.identity(REPO.parent / "a36-status-bin/hammond_standalone") == capture.identity(EXE)
    git = capture.git_identity(REPO)

    def differences(revision):
        return [name for name in files if hashlib.sha256(subprocess.check_output(
            ["git", "-C", str(REPO), "show", f"{revision}:{name}"])).hexdigest() != by_sha[name]]

    current_differences, published_differences = differences(git["head"]), differences(PUBLISHED)
    assert not current_differences and not published_differences
    supporting_reports = ["a44-midi-on-source-after-build.json", "a44-build-result.json",
                          "a44-package-refresh.json", "a44-final-package-result.json"]
    a44_builds = b44["builds"]["midi-on"]["generated_and_library_identity"]
    common = {name: value for name, value in builds.items() if name in a44_builds}
    assert all(value == a44_builds[name] for name, value in common.items())
    extra = {name: capture.identity(BUILD / name) for name in [
        "CMakeCache.txt", "apps/standalone/CMakeFiles/hammond_standalone.dir/link.txt",
        "apps/standalone/CMakeFiles/hammond_standalone_support.dir/flags.make",
        "generated/standalone-capabilities.json"]}
    before = {
        "schema": "a46-final-gallery-snapshot-v1", "assignment": 46,
        "worker": "/root/w08_a46_final_native_gallery",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(), "git": git,
        "product_source_published_commit": PUBLISHED, "product_source_published_tree": PUBLISHED_TREE,
        "production_files": files, "production_count": len(files),
        "production_a44_path_nul_sha_newline_digest": a44_digest(by_sha),
        "production_size_and_sha_inventory_sha256": capture.inventory_digest(files),
        "production_differences_from_head": current_differences,
        "production_differences_from_published_commit": published_differences,
        "production_differences_from_a44": [], "build_files": builds, "build_count": len(builds),
        "build_inventory_sha256": capture.inventory_digest(builds),
        "selected_configuration": capture.configuration(BUILD), "additional_build_identity": extra,
        "a44_build_overlap_count": len(common), "a44_build_overlap_differences": [],
        "a44_reports": {name: capture.identity(REPORTS / name) for name in supporting_reports},
        "executable": {"path": str(EXE), **capture.identity(EXE)},
        "capture_harness": capture.identity(REPO / "tools/capture_standalone_interface.py"),
        "historical_v1_manifest": capture.identity(REPO / "examples/demos/standalone-interface-preview-v1/manifest.json"),
        "tracked_changes_from_head": subprocess.check_output(
            ["git", "-C", str(REPO), "diff", "--name-only", "HEAD"], text=True).splitlines(),
        "boundary": "All 98 observed production inputs equal the named published commit and A44 source snapshot. The worktree has concurrent non-production edits. The selected 13 generated/header/profile/static-library identities and selected configuration are not a complete compiler/dependency build graph.",
    }
    capture.write_json(REPORTS / "a46-source-before.json", before)
    qualified = {
        "schema": "a46-qualified-native-gallery-source-v1", "assignment": 46,
        "worker": "/root/w08_a46_final_native_gallery",
        "binary_sha256": capture.identity(EXE)["sha256"], "binary_bytes": capture.identity(EXE)["bytes"],
        "source_sha256": {name: a44["production_sha256"][name] for name in capture.REQUIRED_QUALIFIED_SOURCES},
        "qualified_source_count": len(capture.REQUIRED_QUALIFIED_SOURCES),
        "qualification_method": "Matched current files and executable to A44 source, configured target-build and final package/relocation records; no configure, compilation or independent rebuild performed by A46. A44 MIDI-on target-build invocation was already up to date.",
        "a44_source_head": a44["head"], "a44_source_committed_tree": a44["committed_tree"],
        "capture_preflight_git": git, "production_source_is_uncommitted_overlay": False,
        "all_98_production_files_match_published_commit": PUBLISHED,
        "production_a44_path_nul_sha_newline_digest": a44_digest(by_sha),
        "production_size_and_sha_inventory_sha256": capture.inventory_digest(files),
        "build_inventory_sha256": capture.inventory_digest(builds),
        "selected_configuration": capture.configuration(BUILD),
        "supporting_reports": {name: capture.identity(REPORTS / name)
                               for name in supporting_reports + ["a46-source-before.json"]},
        "scope": "source_sha256 intentionally pins the ten harness-required renderer/model/drawing/inspection/main/reference files only. The full 98-file product observation is in a46-source-before.json and gallery provenance. Neither subset nor full observation proves the entire source/build/dependency graph or signed source-to-binary reproducibility. CMake test budgets, workflow, reports and unrelated docs are outside the rendered product inventory.",
        "source_reference": "Original cover/page 409; docs/design/atlas-cover-reference.jpg, unchanged generated concept, not a native application frame.",
    }
    capture.write_json(REPORTS / "a46-source-qualification.json", qualified)
    print(json.dumps({"head": git, "product_files": len(files), "build_files": len(builds),
                      "a44_digest": a44_digest(by_sha), "size_sha_digest": capture.inventory_digest(files),
                      "build_digest": capture.inventory_digest(builds), "binary": capture.identity(EXE),
                      "required_sources": len(capture.REQUIRED_QUALIFIED_SOURCES),
                      "a44_build_overlap": len(common), "all_checks": "passed"}, indent=2))


if __name__ == "__main__":
    main()
