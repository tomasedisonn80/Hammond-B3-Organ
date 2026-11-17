"""Inspect retained Windows-generator and full-R4 CI artifacts; no execution."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import zipfile

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[4]
SOURCE = "523c1979334b0fbb624ce120128a0b8ada078383"
TREE = "893441fe87859b9dbad81a5d81a453f7c96030f8"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(name, report):
    path = BASE / name
    assert not path.exists(), path
    path.write_text(json.dumps(report, indent=2) + "\n")


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}, check=True, capture_output=True).stdout


def review_windows(archive, receipt):
    prefix = "ci-logs/windows-unicode-generator/"
    raw = archive.read(prefix + "qualification.json")
    q = json.loads(raw)
    assert q["source_commit"] == SOURCE and q["source_tree"] == TREE
    generated = archive.read(prefix + "generate.stdout")
    records = [json.loads(line) for line in generated.decode("utf-8").splitlines()]
    refusal = json.loads(archive.read(prefix + "protected-source.stdout"))
    expected = {}
    root = "data/registrations/starter-v1/entries"
    for path in git("ls-tree", "-r", "--name-only", SOURCE, "--", root).decode().splitlines():
        payload = git("show", SOURCE + ":" + path)
        expected[path[len(root) + 1:]] = {"bytes": len(payload), "sha256": sha(payload)}
    assert len(expected) == 24 and q["payloads"] == expected
    assert len(records) == 25
    assert all(x["event"] == "file" and x["status"] == "Saved" and x["committed"] is True for x in records[:-1])
    assert {x["file"] for x in records[:-1]} == set(expected)
    assert records[-1]["status"] == "Complete" and records[-1]["attempted_count"] == records[-1]["committed_count"] == 24
    assert records[-1]["unattempted_count"] == 0 and records[-1]["uncertain_file"] is None
    assert b"\r" not in generated and generated.endswith(b"\n")
    assert archive.read(prefix + "generate.stderr") == archive.read(prefix + "protected-source.stderr") == b""
    assert refusal == q["protected_source_refusal"] and refusal["status"] == "ProtectedPath"
    assert refusal["attempted_count"] == refusal["committed_count"] == 0 and q["source_pack_unchanged"] is True
    assert any(ord(x) > 127 for x in q["unicode_source_root"])
    model = json.loads(archive.read(prefix + "generator-target-Release.json"))
    groups = [group for group in model["compileGroups"] if group["language"] == "CXX"]
    assert groups and all("/utf-8" in {flag for fragment in group["compileCommandFragments"] for flag in fragment["fragment"].split()} for group in groups)
    assert all(q["compiled_source_definition"] in {item["define"] for item in group["defines"]} for group in groups)
    report = {"artifact_id": receipt["artifact_id"], "source": SOURCE, "qualification_path": prefix + "qualification.json", "qualification_sha256": sha(raw), "qualification": q, "actual_generation_records": len(records), "payloads_saved": 24, "all_payloads_match_exact_published_source": True, "generation_summary": records[-1], "stdout_lf_only": True, "generate_and_protected_stderr_empty": True, "source_root_contains_unicode": True, "compile_groups_all_utf8": True, "compiled_source_definition_verified": True, "commands": json.loads(archive.read(prefix + "commands.json")), "scope": q["scope"]}
    save("windows-unicode-generator-review.json", report)
    return {"kind": "windows_unicode_generator", "artifact_id": receipt["artifact_id"], "payloads": 24, "source": SOURCE, "status": "passed"}


def review_r4(archive, receipt):
    names = archive.namelist()
    qp, = [name for name in names if "/full/" in name and name.endswith("/qualification.json")]
    raw = archive.read(qp)
    q = json.loads(raw)
    parent = qp.rsplit("/", 1)[0]
    native_raw = archive.read(parent + "/native.stdout.json")
    stderr_raw = archive.read(parent + "/native.stderr.txt")
    native = json.loads(native_raw)
    for name, payload in (("stdout", native_raw), ("stderr", stderr_raw)):
        bound = q["native_process"][name]
        assert len(payload) == bound["bytes"] and sha(payload) == bound["sha256"]
    for name in ("source_before", "source_after"):
        assert q[name]["git_head"] == SOURCE and q[name]["git_tree"] == TREE and q[name]["dirty_overlay"] is False
    assert q["source_before"] == q["source_after"]
    assert q["status"] == native["status"] == "pass" and q["mode"] == native["mode"] == "full"
    assert q["completed"] is True and native["completed"] is True
    assert not q["failures"] and not native["failures"] and all(value == "pass" for value in q["groups"].values())
    assert q["native_process"]["exit_code"] == 0 and q["native_process"]["timed_out"] is False
    assert q["native_totals"] == q["native_admission"]["totals"] == native["totals"]
    assert q["native_totals"]["partition_compared_samples"] == q["native_totals"]["partition_equal_samples"]
    admission_log = archive.read("waveform-ci-logs/report-admission.log").decode()
    methods = re.search(r"Ran (\d+) tests? in ([0-9.]+)s", admission_log)
    assert methods and re.search(r"(?m)^OK\s*$", admission_log)
    report = {"artifact_id": receipt["artifact_id"], "source": SOURCE, "qualification_path": qp, "qualification_sha256": sha(raw), "status": q["status"], "mode": q["mode"], "completed": q["completed"], "started_utc": q["started_utc"], "finished_utc": q["finished_utc"], "wall_seconds": q["wall_seconds"], "failures": q["failures"], "groups": q["groups"], "native_process": q["native_process"], "native_totals": q["native_totals"], "native_admission": q["native_admission"], "native_report_totals_match_qualification": True, "original_stdout_stderr_digests_verified": True, "source_before": q["source_before"], "source_after": q["source_after"], "source_stability_verified": True, "executable_before": q["executable_before"], "executable_after": q["executable_after"], "build_before": q["build_before"], "build_after": q["build_after"], "selected_decimal_crosscheck": q["selected_decimal_crosscheck"], "retained_static_grid": q["retained_static_grid"], "report_admission_self_test_methods": int(methods[1]), "report_admission_self_test_seconds": float(methods[2]), "scope": q["scope"], "separate_gates": q["separate_gates"]}
    save("r4-full-review.json", report)
    return {"kind": "r4_full", "artifact_id": receipt["artifact_id"], "wall_seconds": q["wall_seconds"], "totals": q["native_totals"], "admission_methods": int(methods[1]), "status": "passed"}


results = []
for path in sorted(BASE.glob("artifact-*.zip")):
    receipt = json.loads(path.with_suffix(".receipt.json").read_text())
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if "ci-logs/windows-unicode-generator/qualification.json" in names and not (BASE / "windows-unicode-generator-review.json").exists():
            results.append(review_windows(archive, receipt))
        if "waveform-ci-logs/report-admission.log" in names and not (BASE / "r4-full-review.json").exists():
            results.append(review_r4(archive, receipt))
print(json.dumps(results, indent=2))
