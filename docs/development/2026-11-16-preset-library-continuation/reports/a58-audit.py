#!/usr/bin/env python3
"""A58 bounded read-only recovery audit; writes only its assigned report files."""
from __future__ import annotations
import collections
import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[4]
SESSION = REPO / "docs/development/2026-11-16-preset-library-continuation"
REPORTS = SESSION / "reports"
SOURCE = "cc6be852d616ec5887485e3fccc39ddb1db22006"
TREE = "201e38b05901fa30e3d053b9c245829818a5b52e"
BASE = "54df95fe343d417dd89bb7a91f85e4f51c08dfe7"
FIRST = "20739f6280b95e567e84615d5c5aee443fc3b93d"
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1")

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_json(path):
    return json.loads(path.read_text())

def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, env=ENV, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

def file_record(path, expected=None):
    path = Path(path)
    if not path.is_file():
        return {"path": str(path), "exists": False}
    raw = path.read_bytes()
    out = {"path": str(path), "bytes": len(raw), "sha256": sha(raw)}
    if expected is not None:
        out["matches_receipt"] = out["sha256"] == expected
    return out

def usage(path):
    count = apparent = allocated = 0
    for directory, dirs, files in os.walk(path, followlinks=False):
        dirs[:] = [d for d in dirs if not (Path(directory) / d).is_symlink()]
        for name in files:
            item = Path(directory) / name
            if item.is_symlink():
                continue
            stat = item.stat()
            count += 1
            apparent += stat.st_size
            allocated += stat.st_blocks * 512
    return {"files": count, "apparent_file_bytes": apparent,
            "allocated_file_bytes": allocated}

def main():
    result = {
        "schema": "a58-final-record-recovery-v1", "worker": "A58",
        "agent": "/root/w10_a58", "wave": 10,
        "observed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cwd": str(REPO),
        "scope": "Read-only Git/filesystem/hash inspection and matching progress checker; no external dispatch proof, build, suite, render, capture, cleanup, staging or publication.",
    }
    index_before = sha((REPO / ".git/index").read_bytes())
    ledger_raw = (SESSION / "assignments.json").read_bytes()
    ledger = json.loads(ledger_raw)
    workers = ledger["workers"]
    accepted = [w for w in workers if w["status"] == "accepted"]
    note_hashes = {}
    note_mismatches = []
    root_review_missing = []
    owned_invalid = []
    accepted_owned_missing = []
    owned_count = 0
    active_paths = {}
    for worker in workers:
        if worker["status"] == "accepted":
            note = SESSION / "notes" / (worker["id"] + ".md")
            digest = sha(note.read_bytes()) if note.is_file() else None
            note_hashes[worker["id"]] = digest
            if digest != worker.get("note_sha256"):
                note_mismatches.append(worker["id"])
            if not worker.get("acceptance", "").strip():
                root_review_missing.append(worker["id"])
        for name in worker["owned_paths"]:
            owned_count += 1
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name:
                owned_invalid.append({"worker": worker["id"], "path": name})
                continue
            anchor = SESSION if path.parts[0] in ("notes", "reports") else REPO
            matched = list(anchor.glob(name))
            if any(not p.resolve().is_relative_to(REPO) for p in matched):
                owned_invalid.append({"worker": worker["id"], "path": name,
                                      "reason": "Resolved match leaves the owned repository."})
            if worker["status"] == "accepted" and not matched:
                accepted_owned_missing.append({"worker": worker["id"], "path": name})
            if worker["status"] != "accepted":
                active_paths.setdefault(worker["id"], []).append(str(anchor / name))
    waves = dict(sorted(collections.Counter(w["wave"] for w in workers).items()))
    accepted_waves = dict(sorted(collections.Counter(w["wave"] for w in accepted).items()))
    result["ledger"] = {
        "sha256": sha(ledger_raw), "records": len(workers), "accepted": len(accepted),
        "statuses": dict(collections.Counter(w["status"] for w in workers)),
        "distinct_worker_ids": len({w["id"] for w in workers}),
        "distinct_agent_identities": len({w["agent"] for w in workers}),
        "waves_recorded": waves, "waves_accepted": accepted_waves,
        "invalid_wave_ids": [w["id"] for w in workers if w["wave"] != (int(w["id"][1:]) - 1) // 6 + 1],
        "all_accepted_note_sha256": note_hashes, "note_mismatches": note_mismatches,
        "root_acceptance_missing": root_review_missing,
        "owned_path_count": owned_count, "owned_path_invalid": owned_invalid,
        "accepted_owned_path_missing": accepted_owned_missing,
        "active_exclusive_paths": active_paths,
        "interpretation": "These are actual-ledger records, not independent authentication of external dispatch. Planned/follow-up/historical workers are not added.",
    }
    command = ["python3", "-B", str((SESSION / "check_session.py").relative_to(REPO))]
    progress = subprocess.run(command, cwd=REPO, env=ENV, text=True, capture_output=True)
    (REPORTS / "a58-ledger-progress.json").write_text(progress.stdout)
    result["checker"] = {"command": command, "exit_code": progress.returncode,
                         "stderr": progress.stderr, "result": json.loads(progress.stdout),
                         "strict_executed": False,
                         "strict_owner": "Root after every real final note is accepted and rehashed."}

    coverage = read_json(REPORTS / "atlas-reading-coverage.json")
    extract_pages = (REPO.parent / "tmp/pdfs/atlas.txt").read_bytes().split(b"\f")
    pages = []
    reader_results = []
    worker_map = {w["id"]: w for w in workers}
    for reader in coverage["readers"]:
        pages.extend(range(reader["first_page"], reader["last_page"] + 1))
        digest = sha((SESSION / "notes" / (reader["worker"] + ".md")).read_bytes())
        extract_range = b"\f".join(extract_pages[reader["first_page"] - 1:reader["last_page"]])
        reader_results.append({"worker": reader["worker"], "agent": reader["agent"],
            "first_page": reader["first_page"], "last_page": reader["last_page"],
            "pages": reader["pages"], "note_sha256": digest,
            "note_matches_coverage_and_ledger": digest == reader["note_sha256"] == worker_map[reader["worker"]]["note_sha256"],
            "extract_without_final_formfeed_matches": sha(extract_range) == reader["text_sha256_without_final_formfeed"],
            "extract_with_final_formfeed_matches": sha(extract_range + b"\f") == reader["text_sha256_with_final_formfeed"],
            "agent_matches_ledger": reader["agent"] == worker_map[reader["worker"]]["agent"]})
    result["atlas"] = {"receipt": file_record(REPORTS / "atlas-reading-coverage.json"),
        "ranges_exactly_once_1_through_500": sorted(pages) == list(range(1, 501)),
        "readers": reader_results,
        "pdf": file_record(REPO / "Hammond_B3_Leslie_Research_Atlas_500pp.pdf", coverage["pdf_sha256"]),
        "full_extract": file_record(REPO.parent / "tmp/pdfs/atlas.txt", coverage["full_extract_sha256"]),
        "limit": "Checks retained range and note identities; does not claim this worker reread 500 pages or verified every cited external source."}

    changed = git("diff", "--name-only", SOURCE, "--", ".").decode().splitlines()
    staged = git("diff", "--cached", "--name-only").decode().splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard").decode().splitlines()
    production_prefixes = ("src/", "include/", "plugins/", "apps/", "tools/", "tests/", "cmake/", ".github/workflows/", "data/", "assets/", "examples/")
    production_changes = [p for p in changed + untracked if p.startswith(production_prefixes) or p in ("CMakeLists.txt", "CMakePresets.json")]
    preserved_groups = {}
    for group, prefix in (("core_headers", "include"), ("core_sources", "src"), ("plugins", "plugins"), ("preexisting_data", "data")):
        names = git("ls-tree", "-r", "--name-only", BASE, "--", prefix).decode().splitlines()
        mismatches = [p for p in names if not (REPO / p).is_file() or (REPO / p).read_bytes() != git("show", BASE + ":" + p)]
        preserved_groups[group] = {"files": len(names), "mismatches": mismatches}
    delta = git("diff", "--name-only", BASE, "HEAD").decode().splitlines()
    inspected = sorted(set(delta + untracked))
    compiled = []
    generated = []
    for name in inspected:
        path = REPO / name
        if not path.is_file():
            continue
        with path.open("rb") as handle:
            magic = handle.read(8)
        if magic.startswith((b"\x7fELF", b"MZ", b"!<arch>\n", b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf")):
            compiled.append(name)
        if "__pycache__" in path.parts or path.suffix in (".pyc", ".o", ".obj", ".b64") or path.name in ("CMakeCache.txt", "build.ninja"):
            generated.append(name)
    cache_paths = []
    for directory, dirs, files in os.walk(REPO, followlinks=False):
        dirs[:] = [d for d in dirs if d != ".git" and not (Path(directory) / d).is_symlink()]
        for name in dirs:
            if name == "__pycache__": cache_paths.append(str((Path(directory) / name).relative_to(REPO)))
        for name in files:
            if name == "CMakeCache.txt" or name == "build.ninja" or name.endswith((".pyc", ".o", ".obj")):
                cache_paths.append(str((Path(directory) / name).relative_to(REPO)))
    result["source"] = {"head": git("rev-parse", "HEAD").decode().strip(),
        "head_tree": git("rev-parse", "HEAD^{tree}").decode().strip(),
        "expected_source": SOURCE, "expected_tree": TREE,
        "published_commit_parent": git("show", "-s", "--format=%P", SOURCE).decode().strip(),
        "authored_local_tree": git("rev-parse", "503ed724^{tree}").decode().strip(),
        "cached_origin_main": git("rev-parse", "origin/main").decode().strip(),
        "fresh_remote_query_performed": False,
        "followup_publication_receipt": file_record(REPORTS / "followup-publication.json"),
        "tracked_overlay_paths": changed, "staged_paths": staged,
        "untracked_path_count": len(untracked), "production_build_workflow_test_data_changes_since_source": production_changes,
        "preserved_from_session_base": preserved_groups,
        "delta_and_untracked_files_inspected": len(inspected),
        "compiled_magic_paths": compiled, "accidental_generated_paths": generated,
        "checkout_build_cache_object_paths": cache_paths,
        "index_sha256_before": index_before}
    result["source"]["retained_other_owner_sources"] = {
        name: (REPO / name).read_bytes() == git("show", BASE + ":" + name)
        for name in ("apps/standalone/main.cpp", "apps/standalone/UiModel.cpp", "apps/standalone/UiModel.h")}
    ignored_cache_files = []
    archival_cache_files = []
    for name in cache_paths:
        path = REPO / name
        if not path.is_file():
            continue
        tracked = bool(git("ls-files", "--", name).strip())
        ignored = subprocess.run(["git", "check-ignore", "--", name], cwd=REPO,
            env=ENV, capture_output=True).returncode == 0
        entry = {"path": name, "bytes": path.stat().st_size, "tracked": tracked, "ignored": ignored}
        (ignored_cache_files if ignored else archival_cache_files).append(entry)
    result["source"]["ignored_python_cache_files"] = ignored_cache_files
    result["source"]["ignored_python_cache_bytes"] = sum(p["bytes"] for p in ignored_cache_files)
    result["source"]["archived_cache_evidence"] = archival_cache_files
    result["source"]["cache_interpretation"] = "Seven ignored Python cache files are existing local intermediates, not tracked deliverables. The tracked historical gallery CMakeCache snapshot is intentional evidence. No removal is performed."

    contracts = ["docs/REGISTRATION_CLI_CONTRACT.md", "docs/REGISTRATION_RENDER_CONTRACT.md", "docs/STARTER_REGISTRATION_PACK_CONTRACT.md", "docs/design/REFERENCE_APRON_CONTRACT.md"]
    frozen = []
    for name in contracts:
        raw = (REPO / name).read_bytes()
        frozen.append({"path": name, "sha256": sha(raw),
                       "same_as_first_publication": raw == git("show", FIRST + ":" + name),
                       "same_as_followup": raw == git("show", SOURCE + ":" + name)})
    a47 = read_json(REPORTS / "a47-resource-recovery.json")
    configuration = {}
    for name in ("build-native", "a38-headless"):
        cache = REPO.parent / name / "CMakeCache.txt"
        text = cache.read_text()
        values = {}
        for line in text.splitlines():
            if line and not line.startswith(("#", "//")) and "=" in line:
                left, value = line.split("=", 1)
                if ":" in left:
                    values[left.split(":", 1)[0]] = value
        expected = a47["resource"]["configuration"][name]
        configuration[name] = {"cache_sha256": sha(cache.read_bytes()),
            "cache_matches_a47": sha(cache.read_bytes()) == expected["cache_sha256"],
            "settings": {key: values.get(key) for key in expected["settings"]},
            "settings_match_a47": all(values.get(key) == value for key, value in expected["settings"].items())}
    baselines = [file_record(item["path"], item["sha256"]) for item in a47["preserved_evidence"]["baseline_items"]]
    failures = [file_record(REPO / item["path"], item["sha256"]) for item in a47["preserved_evidence"]["original_failure_records"]]
    paired = read_json(REPORTS / "apron-paired-final.json")
    fixture_paths = ["apps/standalone/native_tests/test_standalone_reference_apron_raster.cpp", "docs/design/reference-apron-fixtures.json"]
    fixtures = [file_record(REPO / p, paired["source_sha256"][p]) for p in fixture_paths]
    result["preservation"] = {"a47_receipt": file_record(REPORTS / "a47-resource-recovery.json"),
        "frozen_contracts": frozen, "seven_genuine_baseline_items": baselines,
        "original_failure_records": failures, "frozen_fixture": fixtures,
        "fixture_cases": read_json(REPO / fixture_paths[1])["case_count"],
        "paired_receipt": file_record(REPORTS / "apron-paired-final.json"),
        "paired_reported_totals": paired["totals"],
        "paired_executable_hash_checks": [file_record(v["path"], v["sha256"]) for v in paired["executables"].values()],
        "baseline_portability_limit": "Genuine baseline binaries remain local preservation files; source rebuilds are not original artifacts. Preserve before any workspace retirement."}

    gallery = REPO / "docs/design/native-gallery-preset-v1"
    manifest = read_json(gallery / "manifest.json")
    provenance = read_json(gallery / "provenance.json")
    mismatches = [name for name, expected in manifest["files"].items() if not (gallery / name).is_file() or sha((gallery / name).read_bytes()) != expected["sha256"] or (gallery / name).stat().st_size != expected["bytes"]]
    source_mismatches = [name for name, expected in provenance["source"]["files"].items() if sha(git("show", FIRST + ":" + name)) != expected["sha256"]]
    current_differences = [name for name, expected in provenance["source"]["files"].items() if sha((REPO / name).read_bytes()) != expected["sha256"]]
    result["gallery"] = {"manifest": file_record(gallery / "manifest.json"), "views": len(provenance["cases"]),
        "manifest_payloads": len(manifest["files"]), "payload_mismatches": mismatches,
        "recorded_source_files": len(provenance["source"]["files"]), "first_published_source_mismatches": source_mismatches,
        "current_source_differences_from_capture": current_differences,
        "executable": file_record(provenance["executable"]["path"], provenance["executable"]["after"]["sha256"]),
        "representative_png": file_record(gallery / "images/play-reference-1672x941.png"),
        "limit": "Hashes preserve prior actual captures; no new capture or visual acceptance is claimed."}

    integrated = read_json(REPORTS / "w07-integrated-qualification.json")
    archive_receipt = integrated["audition_delivery_repair"]
    archive_path = REPORTS / archive_receipt["archive"]
    member_expectations = {m["path"]: m for m in archive_receipt["members"]}
    member_mismatches = []
    originals_mismatched = []
    unsafe = []
    with tarfile.open(archive_path) as archive:
        members = archive.getmembers()
        payloads = {}
        for member in members:
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts or not member.isfile():
                unsafe.append(member.name)
                continue
            raw = archive.extractfile(member).read()
            payloads[member.name] = raw
            expected = member_expectations.get(member.name)
            if not expected or sha(raw) != expected["sha256"] or len(raw) != expected["bytes"]:
                member_mismatches.append(member.name)
            original = REPO / archive_receipt["original_directory"] / member.name
            if not original.is_file() or original.read_bytes() != raw:
                originals_mismatched.append(member.name)
    wavs = [name for name in payloads if name.endswith(".wav")]
    pair_names = [name for name in wavs if name.endswith("-performance.wav")]
    pairs_equal = sum(payloads[name] == payloads[name.replace("-performance.wav", "-registration.wav")] for name in pair_names)
    result["auditions"] = {"archive": file_record(archive_path, archive_receipt["archive_sha256"]),
        "members": len(members), "expected_members": archive_receipt["member_count"],
        "member_names_match": set(payloads) == set(member_expectations),
        "member_mismatches": member_mismatches, "ignored_original_mismatches": originals_mismatched,
        "unsafe_members": unsafe, "wav_count": len(wavs), "exact_whole_wav_pairs": pairs_equal,
        "original_report_sha256_matches": sha(gzip.decompress((REPORTS / archive_receipt["original_report_gzip"]).read_bytes())) == archive_receipt["original_report_sha256"],
        "integrated_original_result": integrated["full_run"], "limit": "Archive inspection only, no new audio rendering or physical/audio quality acceptance."}

    log_checks = []
    baseline_receipt = read_json(REPORTS / "baseline-qualification.json")
    for name, item in baseline_receipt["logs"].items():
        compressed = (REPORTS / name).read_bytes()
        raw = gzip.decompress(compressed)
        log_checks.append({"path": name, "compressed_match": sha(compressed) == item["compressed_sha256"],
                           "raw_match": sha(raw) == item["raw_sha256"] and len(raw) == item["raw_bytes"]})
    for item in integrated["logs"].values():
        raw = gzip.decompress((REPORTS / item["archive"]).read_bytes())
        log_checks.append({"path": item["archive"], "raw_match": sha(raw) == item["raw_sha256"] and len(raw) == item["raw_bytes"]})
    result["preservation"]["original_qualification_log_checks"] = log_checks

    navigation = ["AGENTS.md", "README.md", "docs/PLAN.md", "docs/STATUS.md", "docs/NEXT_STEPS.md", "docs/PRODUCT_HANDOFF.md", "docs/PRESET_LIBRARY_CONTINUATION_HANDOFF.md", str((SESSION / "README.md").relative_to(REPO)), str((SESSION / "CHECKPOINT.md").relative_to(REPO)), str((SESSION / "ROOT_DECISIONS.md").relative_to(REPO)), str((SESSION / "NEXT_ASSIGNMENTS.md").relative_to(REPO))]
    links = 0
    broken_links = []
    navigation_records = []
    for name in navigation:
        path = REPO / name
        text = path.read_text()
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            target_path = unquote(target.split("#", 1)[0])
            if not target_path:
                continue
            links += 1
            if not (path.parent / target_path).is_file() and not (path.parent / target_path).is_dir():
                broken_links.append({"source": name, "target": target})
        current_text = text[:text.find("## Preserved dated") if "## Preserved dated" in text else len(text)]
        navigation_records.append({"path": name, "sha256": sha(path.read_bytes()),
            "exact_source_present": SOURCE in current_text, "exact_tree_present": TREE in current_text})
    result["recovery"] = {"navigation": navigation_records, "local_link_targets_checked": links,
        "missing_local_link_targets": broken_links,
        "current_count_lines": {
            name: [{"line": n, "text": line} for n, line in enumerate((REPO / name).read_text().splitlines(), 1)
                   if n <= 45 and re.search(r"accepted|dispatched|running|A55|A58", line)]
            for name in ("docs/PLAN.md", "docs/STATUS.md", str((SESSION / "CHECKPOINT.md").relative_to(REPO)), str((SESSION / "NEXT_ASSIGNMENTS.md").relative_to(REPO)))},
        "early_superseded_counts": [
            {"path": "docs/PLAN.md", "observed_before_root_refresh": "48 accepted; wave 9 underway"},
            {"path": "docs/STATUS.md", "observed_before_root_refresh": "A01-A51 accepted; A52-A54 running; 54 recorded"},
            {"path": str((SESSION / "CHECKPOINT.md").relative_to(REPO)), "observed_before_root_refresh": "54 accepted; 57 recorded; A58-A60 undispatched"}],
        "scope": "All file links are checked for existence; this is not a complete Markdown fragment renderer. Historical snapshots remain historical. Exact current source is reached from README, AGENTS, PLAN, STATUS, NEXT_STEPS and focused handoff; session README routes through checkpoint."}
    milestone_pattern = rb"(?m)^\| \*\*M[0-9][^\n]*$"
    current_rows = re.findall(milestone_pattern, (REPO / "docs/PLAN.md").read_bytes())
    original_rows = re.findall(milestone_pattern, git("show", BASE + ":docs/PLAN.md"))
    result["recovery"]["milestones"] = {"current_rows": len(current_rows),
        "base_rows": len(original_rows), "byte_identical_to_base": current_rows == original_rows,
        "rows_sha256": sha(b"\n".join(current_rows))}
    stat = os.statvfs(REPO)
    build_roots = []
    for child in REPO.parent.iterdir():
        if child.is_dir() and not child.is_symlink() and (child / "CMakeCache.txt").is_file() and (child / "build.ninja").is_file():
            build_roots.append(child.name)
    result["resources"] = {"filesystem_available_bytes": stat.f_bavail * stat.f_frsize,
        "scope": "This repository and explicitly owned sibling native/headless/baseline directories only; free space is aggregate. No other workspace inspection or deletion.",
        "repository": usage(REPO),
        "owned_directories": {name: usage(REPO.parent / name) for name in ("build-native", "a38-headless", "baseline-native")},
        "top_level_live_build_roots": sorted(build_roots), "cleanup_performed": False,
        "baseline_preservation_required": True, "configuration": configuration}
    result["source"]["index_sha256_after"] = sha((REPO / ".git/index").read_bytes())
    result["source"]["index_unchanged"] = result["source"]["index_sha256_after"] == index_before
    result["ledger"]["unchanged_during_observation"] = sha((SESSION / "assignments.json").read_bytes()) == sha(ledger_raw)
    result["next_root_checks"] = [
        "Review and accept every actual A58-A60 note; rehash all sixty and run the matching checker --strict, retaining the result.",
        "Reconcile current navigation counts and exact hosted outcomes from their responsible independent reviewer; retain dated originals and failed/unrun states.",
        "Verify all accepted files and links, fresh remote source/tree/parent, guarded nonforced publication and an inspected clean own checkout.",
        "Preserve local genuine baselines and recovery manifests; root explicitly directed that the small ignored Python caches remain in place, with no cleanup required."]
    observer_failure = REPORTS / "a58-config-observer-failure.json"
    result["observer_errors"] = [file_record(observer_failure)] if observer_failure.is_file() else []
    result["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (REPORTS / "a58-record-recovery.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": len(workers), "accepted": len(accepted),
        "progress_exit": progress.returncode, "note_mismatches": note_mismatches,
        "owned_invalid": owned_invalid, "accepted_owned_missing": accepted_owned_missing,
        "production_changes": production_changes, "compiled": compiled, "cache_paths": cache_paths,
        "broken_links": broken_links, "gallery_mismatches": mismatches,
        "archive_mismatches": member_mismatches, "original_mismatches": originals_mismatched,
        "free_bytes": result["resources"]["filesystem_available_bytes"], "index_unchanged": result["source"]["index_unchanged"]}, indent=2))

if __name__ == "__main__":
    main()
