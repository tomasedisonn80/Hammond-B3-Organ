#!/usr/bin/env python3
"""Audit retained connector-decoded logs; never build, execute tests or mutate Git."""
import argparse
import datetime
import hashlib
import json
import pathlib
import re
import subprocess

HEAD = "0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b"
TREE = "f8144b771cda1264a8788f8297f5bfec999f4a08"
PARENT = "26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8"
WORKER = "/root/w10_a56_published_header_hosted_audit"
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
STAMP = re.compile(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z ")
RESULT = re.compile(r"^\s*(\d+)/(\d+) Test\s+#(\d+):\s+(\S+)\s+.*?\b(Passed)\s+(\d+(?:\.\d+)?)\s+sec")
ROTARY = ["test_rotary_motion", "test_rotary_propagation",
          "test_rotary_propagation_allocation", "python_test_rotary_motion_acceptance",
          "python_test_rotary_propagation_acceptance", "python_test_rotary_profile",
          "python_test_rotary_reference"]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=pathlib.Path)
    parser.add_argument("--cache", required=True, type=pathlib.Path)
    args = parser.parse_args()
    repo, cache = args.repo.resolve(), args.cache.resolve()
    out = repo / "docs/development/2026-11-14-reference-refinement/reports"
    git = lambda *argv: subprocess.check_output(["git", "-C", str(repo), *argv])
    blob = lambda path, ref=HEAD: git("show", ref + ":" + path)
    meta = json.loads((cache / "metadata.json").read_bytes())
    observed = datetime.datetime.now(datetime.timezone.utc).isoformat()
    assert git("rev-parse", HEAD + "^{tree}").decode().strip() == TREE
    assert git("rev-parse", HEAD + "^").decode().strip() == PARENT
    source_workflow = blob(".github/workflows/standalone.yml").decode()
    native_required = re.search(r"HAMMOND_SANITIZER_TARGETS: >-\n(.*?)    steps:",
                                source_workflow, re.S).group(1).split()
    assert len(native_required) == len(set(native_required)) == 16
    assert "test_standalone_midi_backend_quarantine" not in native_required
    full_results = {}
    report = {
        "schema_version": 1, "assignment": "A56", "worker": WORKER,
        "audit_utc": observed, "outcome": "PASS for the exact published header source; named core leak exception retained",
        "tested_source": {"commit": HEAD, "tree": TREE, "parent": PARENT},
        "retrieval": {"metadata_fetched_at": meta["fetched_at"],
            "method": "Connected GitHub GET workflow metadata, job steps and github_fetch_workflow_job_logs for each of twelve jobs.",
            "log_identity": "SHA-256 of exact connector-decoded text encoded as UTF-8, preserving BOM and original line endings; not original ZIP or binary payload bytes.",
            "excerpt_normalization": "Numbered original lines; ANSI escapes removed and line endings normalized to LF. Intervening lines omitted.",
            "full_logs": "Scratch cache only; bounded excerpts retained in this repository.",
            "artifact_payloads_downloaded": False, "remote_mutations": False,
            "product_build_or_tests_executed_by_auditor": False},
        "runs": [], "jobs": [],
    }
    extracts = ["A56 exact published-header primary log extracts",
                "source=" + HEAD + " tree=" + TREE,
                report["retrieval"]["excerpt_normalization"],
                report["retrieval"]["log_identity"], ""]
    for item in meta["runs"]:
        run = item["run"]
        assert run["head_sha"] == HEAD and run["head_commit"]["tree_id"] == TREE
        assert run["status"] == "completed" and run["conclusion"] == "success" and run["run_attempt"] == 1
        report["runs"].append({key: run[key] for key in
                               ("id", "name", "path", "head_sha", "event", "run_attempt",
                                "status", "conclusion", "created_at", "updated_at", "html_url")})
        for job in item["jobs"]:
            jid = job["id"]
            assert job["status"] == "completed" and job["conclusion"] == "success"
            raw = (cache / f"{jid}.log").read_bytes()
            decoded = raw.decode("utf-8")
            lines = [ANSI.sub("", s) for s in decoded.splitlines()]
            body = [STAMP.sub("", s) for s in lines]
            keep = set(range(min(21, len(lines))))
            def retain(index, before=0, after=0):
                keep.update(range(max(0, index-before), min(len(lines), index+after+1)))
            identity_lines = [i for i, text in enumerate(body) if text.strip("'") == HEAD]
            assert identity_lines, (jid, "missing actual checkout identity")
            for i in identity_lines: retain(i)
            results = []
            for i, text in enumerate(body):
                m = RESULT.match(text)
                if m:
                    results.append({"ordinal": int(m[1]), "total": int(m[2]), "test_id": int(m[3]),
                                    "name": m[4], "status": m[5], "seconds": float(m[6]), "line": i+1})
                    retain(i)
            totals = [(i, int(m[1])) for i, text in enumerate(body)
                      if (m := re.fullmatch(r"100% tests passed(?:, 0 tests failed)? out of (\d+)", text))]
            times = [(i, float(m[1])) for i, text in enumerate(body)
                     if (m := re.fullmatch(r"Total Test time \(real\) =\s*([\d.]+) sec", text))]
            assert len(totals) == len(times) == 1, (jid, totals, times)
            total = totals[0][1]
            assert len(results) == len({r["test_id"] for r in results}) == len({r["name"] for r in results}) == total
            assert {r["ordinal"] for r in results} == set(range(1, total+1))
            assert {r["total"] for r in results} == {total}
            retain(totals[0][0]); retain(times[0][0])
            full_results[jid] = results
            toolchain = {}
            for field, pattern in {
                "cmake": r"^cmake version (.+)$", "ctest": r"^ctest version (.+)$",
                "python": r"^Python (.+)$", "cxx": r"^-- The CXX compiler identification is (.+)$",
                "c": r"^-- The C compiler identification is (.+)$", "runner_image": r"^Image: (.+)$",
            }.items():
                matches = [(i, m[1]) for i, text in enumerate(body) if (m := re.match(pattern, text))]
                if matches:
                    toolchain[field] = matches[0][1]; retain(matches[0][0])
            toolchain["runner_image_version"] = next(body[i+1].removeprefix("Version: ") for i,t in enumerate(body) if t.startswith("Image: "))
            if "Windows" in job["name"]:
                m = re.search(r"MSVC[\\/]+([\d.]+)[\\/]+bin", decoded)
                assert m; toolchain["msvc_toolset_directory"] = m[1]
            warnings = []
            for i, text in enumerate(body):
                if re.search(r"\bwarning:|\bWarning\b|\bwarning C\d", text) and not re.search(r"\d+ Warning\(s\)", text):
                    warnings.append({"line": i+1, "text": text})
                    retain(i, after=17 if "CMake Warning (dev)" in text else (6 if "CMake" in text else 0))
                if re.search(r"Warning\(s\)|Error\(s\)|^-- Pinned .* verified:|^Verified \d+ installed files", text):
                    retain(i)
            job_result = {
                "run_id": run["id"], "job_id": jid, "name": job["name"],
                "url": run["html_url"] + "/job/" + str(jid),
                "head_sha": HEAD, "source_tree_from_run": TREE,
                "status": job["status"], "conclusion": job["conclusion"], "steps": job["steps"],
                "log": {"sha256_utf8": digest(raw), "bytes_utf8": len(raw), "decoded_characters": len(decoded),
                        "lines": len(lines), "checkout_identity_lines": [i+1 for i in identity_lines]},
                "ctest": {"passed": total, "failed": 0, "total": total, "seconds": times[0][1],
                          "unique_test_ids": total, "unique_test_names": total, "ordinal_sequence_complete": True,
                          "summary_line": totals[0][0]+1, "duration_line": times[0][0]+1},
                "toolchain": toolchain, "warnings": warnings,
            }
            if run["id"] == 43646527300:
                assert total == 138
                names = {r["name"]: r for r in results}
                job_result["required_rotary_results"] = [names[name] for name in ROTARY]
                job_result["refinement_checker_regression"] = names["python_test_refinement_session"]
                job_result["quarantine_result"] = names["test_standalone_midi_backend_quarantine"]
                for i, text in enumerate(body):
                    if (text.startswith("##[group]Run cmake") or text.startswith("##[group]Run ctest")):
                        retain(i, after=4)
                if jid == 132605474816:
                    assert any(s["name"] == "Verify the completed interface session" and s["conclusion"] == "success" for s in job["steps"])
                    assert not any("refinement session" in s["name"] for s in job["steps"])
                    job_result["strict_current_refinement_session_step_executed"] = False
            elif run["id"] == 43646527323:
                assert total == (16 if jid == 132605474865 else 41)
                names = {r["name"]: r for r in results}
                assert set(native_required) <= set(names)
                if jid == 132605474865: assert set(names) == set(native_required)
                job_result["required_native_results"] = [names[name] for name in native_required]
                material = [(i, json.loads(text[text.index("{"):])) for i,text in enumerate(body)
                            if re.match(r'^\d+: \{"checks":1071,', text)]
                assert len(material) == 1
                mi, m = material[0]
                assert (m["checks"], m["failures"], m["legacy_checks"], m["header_checks"], m["frames"]) == (1071, 0, 901, 170, 88)
                retain(mi)
                job_result["material_acceptance"] = {k: m[k] for k in ["checks", "failures", "legacy_checks", "header_checks", "frames", "state_checks", "clip_frames", "backend"]}
                job_result["material_acceptance"]["line"] = mi+1
                for key, token in [("layout_acceptance", "Independent reference layout: 78 layouts"),
                                   ("pending_acknowledged_acceptance", "Native inspection rendering harness: 6 frames")]:
                    matched = [(i,text) for i,text in enumerate(body) if token in text]
                    assert len(matched) == 1; i,text = matched[0]
                    retain(i); job_result[key] = {"line": i+1, "text": text}
                installed = [(i,text) for i,text in enumerate(body) if re.match(r"^Verified \d+ installed files",text)]
                if jid != 132605474865:
                    assert len(installed) == 1
                    job_result["relocated_payload"] = {"line": installed[0][0]+1, "text": installed[0][1],
                                                       "scope": "Hosted guard execution and primary output; no downloaded package reinspection by A56."}
                for i,text in enumerate(body):
                    if re.match(r"^Discovered (?:exactly 16 built interface gates|41 standalone tests)", text): retain(i)
            else:
                assert total == (8 if jid == 132605474498 else 7)
                validator = [(i,text) for i,text in enumerate(body) if re.match(r"^\d+: Result: 47 tests passed, 0 tests failed$", text)]
                assert len(validator) == 1
                retain(validator[0][0]); job_result["sdk_validator"] = {"passed": 47, "failed": 0, "line": validator[0][0]+1}
            if jid in (132605474865, 132605474892):
                policy = {"ASAN_OPTIONS": "detect_leaks=1:halt_on_error=1",
                          "UBSAN_OPTIONS": "print_stacktrace=1:halt_on_error=1", "LSAN_OPTIONS": "exitcode=23"}
                job_result["sanitizer_job_defaults"] = policy
                for key,value in policy.items():
                    found = [i for i,text in enumerate(body) if text.strip() == key+": "+value]
                    assert found; retain(found[0])
                if jid == 132605474892:
                    proof = {}
                    for src in ("src/RotaryMotion.cpp", "src/RotaryPropagation.cpp",
                                "tests/test_rotary_motion.cpp", "tests/test_rotary_propagation.cpp",
                                "tests/test_rotary_propagation_allocation.cpp",
                                "tests/probes/rotary_motion_probe.cpp", "tests/probes/rotary_propagation_probe.cpp"):
                        found = [i for i,text in enumerate(body) if src in text and "-fsanitize=address,undefined" in text and " -c " in text]
                        assert found, src; retain(found[0]); proof[src] = found[0]+1
                    job_result["instrumented_required_cpp_compile_lines"] = proof
                else:
                    for name in ("Require instrumented SDL C and project C++ objects and linked runtimes",
                                 "Discover exactly sixteen gates and run with leak checking",
                                 "Reverify source and locked SDL2 after acceptance"):
                        assert any(s["name"] == name and s["conclusion"] == "success" for s in job["steps"])
                    for i,text in enumerate(body):
                        if any(token in text for token in ("Missing instrumented build inputs:", "Missing built test command:",
                                "Disabled required gate:", "assert set(counts) == expected", "assert len(names) == len(set(names)) == 16",
                                'assert "__asan_" in symbols', 'assert "libasan.so" in runtimes',
                                'assert "-fsanitize=address,undefined" in shlex.split',
                                'assert {"-fsanitize=address,undefined", "-fno-omit-frame-pointer"}',
                                "overrides = properties.get(", "assert not any(value.startswith((", "for value in overrides)",
                                "sanitizer_limits =", '"test_standalone_scaled_view": 360', '"test_standalone_preset_raster": 300',
                                '"test_standalone_inspection_raster": 60', '"test_standalone_material_acceptance": 60',
                                "--show-only=json-v1", "ctest --test-dir build-standalone-sanitizers -C Release -V")):
                            retain(i)
            job_result["log"]["retained_excerpt_lines"] = len(keep)
            job_result["log"]["excerpt_file"] = "A56-primary-log-excerpts.txt"
            extracts.extend(["", f"=== Job {jid} | run {run['id']} | {job['name']} ===",
                             f"head={HEAD} conclusion=success sha256_utf8={digest(raw)} bytes_utf8={len(raw)}",
                             "Selected numbered lines; intervening lines are omitted."])
            extracts.extend(f"{i+1}: {lines[i]}" for i in sorted(keep))
            report["jobs"].append(job_result)
    assert len(report["runs"]) == 3 and len(report["jobs"]) == 12
    assert len({frozenset(r["name"] for r in full_results[j]) for j in [132605474588,132605474816,132605474823,132605474892]}) == 1
    assert len({frozenset(r["name"] for r in full_results[j]) for j in [132605475094,132605475118,132605475127,132605475146]}) == 1

    # Compare a precisely named source set; documentation and future workflow do not inherit CI identity.
    all_paths = git("ls-tree", "-r", "--name-only", HEAD).decode().splitlines()
    prefixes = ("apps/", "assets/", "cmake/", "data/", "include/", "plugins/", "src/", "tests/", "tools/")
    root_files = {"CMakeLists.txt", "CMakePresets.json", "Makefile", ".gitattributes", ".gitignore"}
    selected = sorted(p for p in all_paths if p.startswith(prefixes) or p in root_files)
    assert len(selected) == 365
    identities = {}
    for path in selected:
        published, current = blob(path), (repo/path).read_bytes()
        assert published == current, path
        identities[path] = {"bytes": len(published), "sha256": digest(published), "working_equals_published": True}
    workflow_compare = {}
    for path in (".github/workflows/ci.yml", ".github/workflows/standalone.yml", ".github/workflows/native-vst3.yml"):
        a,b = blob(path), (repo/path).read_bytes()
        workflow_compare[path] = {"tested_sha256": digest(a), "working_sha256": digest(b), "working_equals_tested": a == b}
    compare = {"schema_version": 1, "worker": WORKER, "observed_utc": observed, "source_commit": HEAD, "source_tree": TREE,
        "selection": "All published files below apps, assets, cmake, data, include, plugins, src, tests and tools; plus CMakeLists.txt, CMakePresets.json, Makefile, .gitattributes and .gitignore when present.",
        "selected_count": len(selected), "all_selected_working_bytes_equal_published": True,
        "exclusions": "The .github workflows are compared separately. Documentation, session records, reports and gallery files are excluded; no complete-worktree, final candidate, frozen Markdown or final CI equality is claimed.",
        "identities": identities, "workflow_comparison": workflow_compare}
    special = sorted(set(json.loads((out/"A44-hosted-sanitizer-audit.json").read_bytes())["tested_source"]["audited_inputs"]) |
                     {"data/dependencies/rtmidi-lock.json", "data/dependencies/vst3-sdk-lock.json", "tests/test_refinement_session.py", "tools/check_refinement_session.py"})
    report["selected_source_hashes"] = {p: {"published_sha256": digest(blob(p)), "working_sha256": digest((repo/p).read_bytes())} for p in special}
    assert report["selected_source_hashes"]["tests/test_rotary_propagation_allocation.cpp"]["published_sha256"] == "022845759fe2e604ad4c8003dc0acf4e2b693d79933da86e25a0ac8e0f9f39d7"
    contracts = ["docs/ROTARY_NUMERICAL_CONTRACT.md", "docs/ROTARY_PROPAGATION_CONTRACT.md"]
    assert all(blob(p) == blob(p,PARENT) == (repo/p).read_bytes() for p in contracts)
    cmake = blob("CMakeLists.txt").decode()
    appcmake = blob("apps/standalone/CMakeLists.txt").decode()
    assert appcmake.count('ENVIRONMENT "ASAN_OPTIONS=detect_leaks=0:halt_on_error=1"') == 1
    assert "set_tests_properties(test_standalone_midi_backend_quarantine PROPERTIES" in appcmake
    assert '"HAMMOND_ROTARY_MOTION_PROBE_EXECUTABLE=$<TARGET_FILE:hammond_rotary_motion_probe>"' in cmake
    assert '"HAMMOND_ROTARY_PROPAGATION_PROBE_EXECUTABLE=$<TARGET_FILE:hammond_rotary_propagation_probe>"' in cmake
    assert "ASAN_OPTIONS" not in cmake and appcmake.count("ASAN_OPTIONS") == 1
    for path in ("tests/test_rotary_motion_acceptance.py", "tests/test_rotary_propagation_acceptance.py"):
        text = blob(path).decode()
        assert "raise RuntimeError" in text
        assert not any(name in text for name in ("ASAN_OPTIONS", "UBSAN_OPTIONS", "LSAN_OPTIONS"))
    prior_audit = json.loads((out/"A44-hosted-sanitizer-audit.json").read_bytes())
    numeric_paths = [p for p in prior_audit["tested_source"]["audited_inputs"]
                     if p.startswith(("include/hammond/Rotary", "src/Rotary", "tests/probes/rotary", "tests/test_rotary"))
                     or p in contracts + ["tools/rotary_reference.py", "tests/TestSupport.h"]]
    report["prior_numerical_inputs"] = {p: {
        "published_sha256": digest(blob(p)),
        "equals_A44_tested_input": digest(blob(p)) == prior_audit["tested_source"]["audited_inputs"][p]["tested_sha256"],
        "equals_26ff_parent_bytes": blob(p) == blob(p,PARENT)} for p in numeric_paths}
    assert all(v["equals_A44_tested_input"] and v["equals_26ff_parent_bytes"] for v in report["prior_numerical_inputs"].values())
    assert "check_refinement_session.py" not in blob(".github/workflows/ci.yml").decode()
    report["source_comparison"] = {"report": "A56-source-comparison.json", "selected_count": len(selected),
        "all_selected_working_bytes_equal_published": True, "workflows": workflow_compare,
        "boundary": compare["exclusions"],
        "future_strict_gate": "A55 adds Linux-only strict current-session checker in the unpublished ci.yml candidate. The 0881 logs execute the refinement checker regression test and historical interface strict checker, not that future refinement sixty-record step."}
    report["native_sanitizer_policy"] = {"required_tests": native_required,
        "guards_observed_success": ["Instrumented objects for all sixteen targets plus SDL2-static, hammond_core, hammond_standalone_support and hammond_standalone_drawing; objects exist and are nonempty.",
            "ASan/UBSan references in four static archives; all sixteen executable link flags and ldd runtime dependencies required.",
            "Exactly sixteen unique discovered built commands; disabled tests and ASan/UBSan/LSan environment overrides rejected; --no-tests=error.",
            "Exact existing raster timeouts 180/360/300 seconds and inspection/material timeouts 60/60 seconds."],
        "scope": "Source and successful primary guard steps inspected; no artifact instrumentation.json or binaries downloaded. Selected project C++ and pinned SDL C are instrumented; system libraries are not rebuilt. Dummy surfaces do not qualify real devices."}
    report["core_sanitizer_policy"] = {
        "required_rotary_gates": ROTARY, "required_gates_inherit_leak_policy": True,
        "existing_exception": {"test": "test_standalone_midi_backend_quarantine", "source": "apps/standalone/CMakeLists.txt",
            "override": "ASAN_OPTIONS=detect_leaks=0:halt_on_error=1", "in_native_sixteen": False,
            "reason": "Injected failed-close tests intentionally retain callback contexts until process exit; normal destruction and required rotary/native gates retain leak checks.", "new_exception": False},
        "boundary": "138/138 is not an exception-free leak-detection claim. Passing core stdout is suppressed; detailed allocation workload remains earlier A27/A38 evidence for the exact unchanged repaired source. No original Windows stack trace is inferred."}
    historical = ["A27-r3-summary.json", "A27-r3-sanitizer-environment.json", "A27-r3-sanitizer-pty.json",
                  "A38-windows-allocation-repair.json", "root-windows-2e.log", "A43-hosted-fixture-closure.json",
                  "A43-f9c-windows-release-decoded.log", "A44-hosted-sanitizer-audit.json"]
    report["historical_records_observed"] = {name: {"bytes": (out/name).stat().st_size, "sha256": digest((out/name).read_bytes())} for name in historical}
    original = json.loads((out/"A38-windows-allocation-repair.json").read_bytes())["hosted_original"]
    assert report["historical_records_observed"]["root-windows-2e.log"]["sha256"] == original["log_sha256"]
    assert report["historical_records_observed"]["root-windows-2e.log"]["bytes"] == original["log_bytes"]
    report["history_preserved"] = [
        "A27 original complete local sanitizer remains failed/environment-blocked at LSan thread-attach EPERM, including PTY exit 134 and its stricter one-off policy.",
        "2e161dc Windows remains 135/136 with allocation SEGFAULT at 0.02 seconds.",
        "f9c11a4 remains six successful jobs and six cancellations; Windows allocation passed before cancellation of its 69/137 partial suite.",
        "26ff2fbe remains a separate passing pre-header 137-core/901-material result under A43/A44."]
    report["limitations"] = [
        "This result qualifies only source 0881d1f4 and the named unchanged current inputs. Final documentation, workflow, sixty-record completion and later publication CI need their own observations.",
        "Native tests and relocated smoke use dummy SDL audio/video; compiled platform backends are not physical audio/MIDI/display or DAW tests.",
        "SDK validator and package guard success are bounded hosted execution evidence; A56 did not download or independently inspect executable/package payloads.",
        "Literal 1:1 visual equality, accessibility, deadline, signing and physical fidelity remain unestablished. R4, R5, R6/Engine and scanner G5 remain separate gates."]
    report["validation"] = {"all_twelve_checkout_logs_match_source": True, "all_three_run_trees_match": True,
        "all_twelve_unique_full_test_counts_match_summaries": True,
        "all_four_core_test_name_sets_identical": True, "all_four_native_release_test_name_sets_identical": True,
        "all_five_native_material_results_1071_equals_901_plus_170": True,
        "all_three_validator_results_47_pass_0_fail": True, "original_2e_log_matches_A38_identity": True,
        "no_product_tests_run_by_A56": True}
    (out/"A56-primary-log-excerpts.txt").write_text("\n".join(extracts)+"\n", encoding="utf-8")
    (out/"A56-source-comparison.json").write_text(json.dumps(compare,sort_keys=True,indent=2)+"\n", encoding="utf-8")
    report["retained_files"] = {name: {"bytes": (out/name).stat().st_size, "sha256": digest((out/name).read_bytes())}
        for name in ["A56-primary-log-excerpts.txt", "A56-source-comparison.json", pathlib.Path(__file__).name]}
    (out/"A56-published-header-hosted-audit.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"outcome": report["outcome"], "jobs": len(report["jobs"]),
          "ctest_total_across_jobs": sum(j["ctest"]["total"] for j in report["jobs"]),
          "compared_source_inputs":len(selected), "report": str(out/"A56-published-header-hosted-audit.json"),
          "retained_files": report["retained_files"]},indent=2))


if __name__ == "__main__":
    main()
