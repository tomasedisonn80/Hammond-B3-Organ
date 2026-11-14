#!/usr/bin/env python3
"""Read-only publication inventory; this does not run either final gate."""
import argparse
import collections
import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


def digest(data):
    return hashlib.sha256(data).hexdigest()


def identity(data):
    return {"bytes": len(data), "sha256": digest(data)}


def aggregate(records):
    return digest(json.dumps(records, sort_keys=True, separators=(",", ":")).encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    session = "docs/development/2026-11-14-reference-refinement"
    reports = session + "/reports/"
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    observed = {}

    def git(*arguments):
        return subprocess.check_output(["git", "--no-optional-locks", *arguments], cwd=repo)

    def read(path):
        data = (repo / path).read_bytes()
        observed[path] = identity(data)
        return data

    def load(path):
        return json.loads(read(path))

    def compare_records(records, prefix=""):
        checked, errors = {}, []
        for path, expected in records.items():
            full = prefix + path
            current = identity(read(full))
            checked[full] = current
            if current != {k: expected[k] for k in ("bytes", "sha256")}:
                errors.append(full)
        return {"count": len(checked), "inventory_sha256": aggregate(checked), "mismatches": errors}

    head = git("rev-parse", "HEAD").decode().strip()
    tree = git("rev-parse", "HEAD^{tree}").decode().strip()
    cached = git("rev-parse", "origin/main").decode().strip()
    status_before = git("status", "--porcelain=v1", "--untracked-files=all")
    staged = git("diff", "--cached", "--name-status").decode()
    head_paths = {}
    for entry in git("ls-tree", "-rz", "HEAD").split(b"\0"):
        if entry:
            metadata, raw_path = entry.split(b"\t", 1)
            mode, kind, oid = metadata.decode().split()
            head_paths[raw_path.decode()] = {"mode": mode, "kind": kind, "blob": oid}
    changed = git("diff", "--name-only", "-z", "HEAD").decode().split("\0")
    untracked = git("ls-files", "--others", "--exclude-standard", "-z").decode().split("\0")
    candidate_paths = sorted(set(changed + untracked) - {""})
    manifest_path = session + "/assignments.json"
    manifest = load(manifest_path)
    assignments = {row["id"]: row for row in manifest["assignments"]}

    def category(path):
        if path.startswith(".github/"):
            return "workflow"
        if path.startswith("examples/demos/standalone-interface-preview-v4/"):
            return "v4_gallery"
        if path.startswith(session + "/"):
            return "refinement_records"
        if path.endswith(".md") and (path.startswith("docs/") or path in ("AGENTS.md", "README.md")):
            return "documentation"
        return "unclassified"

    inventory = {}
    binary = []
    generated = []
    absent = []
    for path in candidate_paths:
        if not (repo / path).is_file():
            absent.append(path)
            continue
        data = read(path)
        record = {**identity(data), "category": category(path), "tracked_at_head": path in head_paths}
        worker_match = re.search(r"/(A\d{2})-", path)
        if worker_match:
            worker = worker_match.group(1)
            record.update(worker=worker, recorded_state=assignments.get(worker, {}).get("status", "absent"))
        inventory[path] = record
        if b"\0" in data[:4096] or data.startswith((b"\x89PNG", b"\x1f\x8b")):
            binary.append({"path": path, **identity(data), "kind": "png" if data.startswith(b"\x89PNG") else "gzip" if data.startswith(b"\x1f\x8b") else "other"})
        if re.search(r"(?:^|/)(?:build[^/]*|CMakeFiles)/|(?:\.bmp|\.o|\.obj|\.a|\.so|\.dll|\.exe|\.wav|\.zip|\.raw|\.pcm|\.pyc)$|(?:^|/)(?:CMakeCache\.txt|build\.ninja|cmake_install\.cmake)$", path):
            generated.append(path)

    note_rows = []
    for row in manifest["assignments"]:
        record = {k: row[k] for k in ("id", "wave", "agent", "status")}
        if row["status"] == "accepted":
            data = read(row["note"])
            record.update(path=row["note"], **identity(data), declared_sha256=row["note_sha256"], hash_matches=digest(data) == row["note_sha256"])
        note_rows.append(record)

    a56_source = load(reports + "A56-source-comparison.json")
    product = compare_records(a56_source["identities"])
    product["source_commit"] = a56_source["source_commit"]
    product["source_tree"] = a56_source["source_tree"]
    product["published_blob_mismatches"] = []
    for path in a56_source["identities"]:
        data = read(path)
        oid = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if oid != head_paths[path]["blob"]:
            product["published_blob_mismatches"].append(path)

    protected_groups = {
        "historical_session_records": [p for p in head_paths if p.startswith("docs/development/") and not p.startswith(session + "/")],
        "published_refinement_notes_reports": [p for p in head_paths if p.startswith((session + "/notes/", reports))],
        "published_example_gallery_evidence": [p for p in head_paths if p.startswith("examples/")],
        "original_reference": ["Hammond_B3_Leslie_Research_Atlas_500pp.pdf", "docs/design/atlas-cover-reference.jpg", "docs/design/atlas-reference.json", "docs/research/source-manifest.json"],
    }
    preserved = {}
    for name, paths in protected_groups.items():
        records, errors = {}, []
        for path in paths:
            data = read(path)
            records[path] = identity(data)
            oid = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            if oid != head_paths[path]["blob"]:
                errors.append(path)
        preserved[name] = {"count": len(records), "bytes": sum(r["bytes"] for r in records.values()), "inventory_sha256": aggregate(records), "published_blob_mismatches": errors}

    a49 = load(reports + "A49-coherent-final-build.json")
    a49_manifest = load(reports + "A49-artifact-manifest.json")
    a49_check = compare_records(a49_manifest["files"], reports)
    compressed = []
    for name, record in a49["snapshots"].items():
        data = read(reports + record["stored_file"])
        raw = gzip.decompress(data)
        compressed.append({"snapshot": name, "path": reports + record["stored_file"], "compressed_identity_matches": len(data) == record["compressed_bytes"] and digest(data) == record["compressed_sha256"], "expanded_identity_matches": len(raw) == record["bytes"] and digest(raw) == record["sha256"], "expanded_bytes": len(raw)})
    a50 = load(reports + "A50-final-gallery-admission.json")
    a56 = load(reports + "A56-published-header-hosted-audit.json")
    a58 = load(reports + "A58-review-baseline.json")
    evidence = {
        "A49_original_artifact_bundle": a49_check,
        "A49_compressed_inputs": compressed,
        "A50_retained_records": compare_records(a50["retained_evidence"]),
        "A56_historical_failure_and_cancelled_records": compare_records(a56["historical_records_observed"], reports),
        "A56_retained_records": compare_records(a56["retained_files"], reports),
        "A58_protected_evidence": compare_records(a58["protected_evidence"]),
    }
    gallery_path = "examples/demos/standalone-interface-preview-v4/"
    gallery_manifest = load(gallery_path + "manifest.json")
    gallery_check = compare_records(gallery_manifest["files"], gallery_path)
    gallery_files = {p.relative_to(repo).as_posix(): identity(read(p.relative_to(repo).as_posix())) for p in sorted((repo / gallery_path).rglob("*")) if p.is_file()}
    gallery = {"payload": gallery_check, "file_count": len(gallery_files), "bytes": sum(v["bytes"] for v in gallery_files.values()), "all_files_inventory_sha256": aggregate(gallery_files), "matches_A50_count_and_bytes": len(gallery_files) == a50["gallery"]["files"] and sum(v["bytes"] for v in gallery_files.values()) == a50["gallery"]["bytes"], "metadata_identities": compare_records({gallery_path + key + "." + ("md" if key == "readme" else "json"): a50["gallery"][key] for key in ("manifest", "provenance")})}
    gallery["readme_identity_matches_A50"] = identity(read(gallery_path + "README.md")) == a50["gallery"]["readme"]

    historical_sections = []
    a48 = load(reports + "A48-instructions-baseline.json")
    data = read("AGENTS.md"); tail = data[data.index(a48["historical_boundary"].encode()):]
    historical_sections.append({"path": "AGENTS.md", "scope": "historical instructions", "sha256": digest(tail), "matches": digest(tail) == a48["historical_suffix_sha256"]})
    a54 = load(reports + "A54-current-baseline.json")
    for path, record in a54["documents"].items():
        data = read(path)
        if "protected_prefix_bytes" in record:
            prefix = data[:record["protected_prefix_bytes"]]
            historical_sections.append({"path": path, "scope": "concurrent waveform prefix", "sha256": digest(prefix), "matches": digest(prefix) == record["protected_prefix_sha256"]})
        marker = record.get("historical_suffix_marker", record.get("historical_body_start"))
        if marker:
            tail = data[data.index(marker.encode()):]
            expected = record.get("historical_suffix_sha256", record.get("historical_body_sha256"))
            historical_sections.append({"path": path, "scope": "dated historical body", "sha256": digest(tail), "matches": digest(tail) == expected})
    for path, record, scope in [("README.md", a58["readme_waveform_prefix"], "concurrent waveform prefix")]:
        data = read(path)[:record["bytes"]]
        historical_sections.append({"path": path, "scope": scope, "sha256": digest(data), "matches": digest(data) == record["sha256"]})
    data = read("docs/RELEASE_READINESS.md")
    tail = data[data.index(b"## Historical standalone/scanner assessment"):]
    historical_sections.append({"path": "docs/RELEASE_READINESS.md", "scope": "dated historical assessments", "sha256": digest(tail), "matches": identity(tail) == a58["release_historical_suffix"]})

    workflow_path = ".github/workflows/ci.yml"
    workflow = read(workflow_path)
    published_workflow = git("show", "HEAD:" + workflow_path)
    insertion = b"      - name: Verify the completed refinement session\n        if: runner.os == 'Linux'\n        run: |\n          set -o pipefail\n          python tools/check_refinement_session.py --repo . --json | tee ci-logs/refinement-session-completion.json\n\n"
    workflow_check = {"six_line_addition_only": workflow.count(insertion) == 1 and workflow.replace(insertion, b"", 1) == published_workflow, "working": identity(workflow), "published": identity(published_workflow), "other_workflows_unchanged": all(read(p) == git("show", "HEAD:" + p) for p in head_paths if p.startswith(".github/workflows/") and p != workflow_path)}

    storage = {}
    for relative in (".", "../build-native", "../build-desktop", "../SDL2", "../rtmidi", "../native-sysroot", "../build-tools"):
        path = (repo / relative).resolve()
        if path.is_dir():
            result = subprocess.check_output(["du", "-sb", str(path)]).decode().split("\t", 1)
            storage[relative] = {"path": str(path), "apparent_bytes": int(result[0]), "ownership": "session repository" if relative == "." else "existing shared input/build; not a Git candidate"}
    ignored = [p for p in git("ls-files", "--others", "--ignored", "--exclude-standard", "-z").decode().split("\0") if p]
    ignored_info = {"files": len(ignored), "bytes": sum((repo / p).stat().st_size for p in ignored), "all_python_bytecode": all(p.endswith(".pyc") for p in ignored)}
    groups = collections.defaultdict(list)
    for record in binary:
        groups[record["sha256"]].append(record["path"])
    stability = [p for p, expected in observed.items() if not (repo / p).is_file() or identity((repo / p).read_bytes()) != expected]
    status_after = git("status", "--porcelain=v1", "--untracked-files=all")
    accounting = {"manifest": {"path": manifest_path, **observed[manifest_path]}, "recorded": len(note_rows), "distinct_agents": len({r["agent"] for r in note_rows}), "counts": dict(collections.Counter(r["status"] for r in note_rows)), "running": [r["id"] for r in note_rows if r["status"] != "accepted"], "accepted_note_hash_mismatches": [r["id"] for r in note_rows if r.get("hash_matches") is False], "rows": note_rows, "strict_checker_executed": False, "external_dispatch_or_acceptance_truth_attested": False}
    result = {"schema": "A59-publication-preflight-v1", "worker": "/root/w10_a59_publication_preflight", "started_utc": started, "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "repository": str(repo), "scope": "Static read-only inventory and retained evidence comparison; no build, CTest, checker, Git/index/ref mutation, cleanup or network observation.", "source": {"head": head, "tree": tree, "cached_origin_main": cached, "fresh_remote_query": False, "staged_name_status": staged, "no_staged_changes": staged == "", "tracked_head_paths": len(head_paths), "index_still_matches_HEAD": git("diff", "--cached", "--name-status") == b""}, "candidate": {"tracked_changed": len([p for p in candidate_paths if p in head_paths]), "untracked": len([p for p in candidate_paths if p not in head_paths]), "files": len(inventory), "bytes": sum(r["bytes"] for r in inventory.values()), "category_counts": dict(collections.Counter(r["category"] for r in inventory.values())), "inventory_sha256": aggregate(inventory), "paths": inventory, "missing_or_nonregular": absent, "unclassified": [p for p,r in inventory.items() if r["category"] == "unclassified"], "generated_build_or_raw_candidates": generated, "snapshot_output_excluded": str(Path(args.output).resolve()) not in [str(repo / p) for p in candidate_paths]}, "product": product, "workflow": workflow_check, "accounting": accounting, "preserved_published_evidence": preserved, "original_evidence": evidence, "historical_and_concurrent_document_sections": historical_sections, "gallery": gallery, "binary_inventory": {"files": len(binary), "bytes": sum(r["bytes"] for r in binary), "unique_hashes": len(groups), "duplicate_groups": [v for v in groups.values() if len(v) > 1], "paths": binary, "object_preparation_is_publication": False}, "storage": {"directories": storage, "disk_free_bytes": shutil.disk_usage(repo).free, "ignored": ignored_info, "other_session_directory_visited": False}, "stability": {"observed_input_files": len(observed), "changed_during_snapshot": stability, "git_status_unchanged_during_snapshot": status_before == status_after, "head_unchanged": git("rev-parse", "HEAD").decode().strip() == head, "atomic_freeze_claimed": False}, "limits": ["The manifest records root's declarations; this script cannot authenticate collaboration dispatch or substantive acceptance.", "No final documentation-integrity or strict-session gate is run here; root must execute both after final records are accepted.", "The output is written after the inventory and cannot hash itself. Later worker/root edits require candidate reconciliation.", "Cached origin/main and historical receipts do not substitute for a fresh expected-head observation immediately before publication.", "Existing hosted 0881 execution excludes the additive completion step and final closure records."]}
    output = Path(args.output).resolve()
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "source": result["source"], "candidate_files": len(inventory), "category_counts": result["candidate"]["category_counts"], "accounting_counts": accounting["counts"], "product_mismatches": product["mismatches"], "binary_files": len(binary), "binary_bytes": result["binary_inventory"]["bytes"], "changed_during_snapshot": stability}, indent=2))


if __name__ == "__main__":
    main()
