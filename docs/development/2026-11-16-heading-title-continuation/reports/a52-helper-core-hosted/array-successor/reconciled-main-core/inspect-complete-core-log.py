#!/usr/bin/env python3
"""Inspect already acquired complete Core logs; never execute project tools."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re

SOURCE = "523c1979334b0fbb624ce120128a0b8ada078383"
RUN = 44043394024
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("job_id", type=int)
args = parser.parse_args()
directory = Path(__file__).resolve().parent
requirements = json.loads((directory / "requirements.json").read_bytes())
meta = json.loads((directory / f"job-{args.job_id}-metadata.json").read_bytes())
archive = directory / f"job-{args.job_id}-complete.log.gz"
packed = archive.read_bytes()
decoded = gzip.decompress(packed)
assert len(decoded) <= 16 * 1024**2, "Complete decoded job exceeds review storage bound"
raw_lines = decoded.decode("utf-8").splitlines()
ansi = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
lines = [ansi.sub("", re.sub(r"^\d{4}-\d\d-\d\dT[0-9:.]+Z\s?", "", line)) for line in raw_lines]
rows = []
pattern = re.compile(r"^\s*(\d+)/(\d+)\s+Test\s+#(\d+):\s+(\S+)\s+\.{2,}\s*(.*)$")
for number, text in enumerate(lines, 1):
    match = pattern.match(text)
    if match:
        rows.append(dict(line=number, ordinal=int(match[1]), total=int(match[2]),
                         test_number=int(match[3]), name=match[4], result=match[5]))
def matching(predicate, maximum=None):
    result = [{"line": i + 1, "text": line} for i, line in enumerate(lines) if predicate(line)]
    return result if maximum is None else result[:maximum]
def json_lines():
    for i, line in enumerate(lines):
        if not line.startswith("{"):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            yield i + 1, value
waveforms = [{"line": i, **value} for i, value in json_lines()
             if value.get("mode") == "full" and "qualification_json" in value]
unicode = [{"line": i, **value} for i, value in json_lines()
           if value.get("schema") == "hammond-starter-generator-v1"]
source_rows = matching(lambda t: t == SOURCE)
names = {r["name"] for r in rows}
is_r4 = "R4 waveform" in meta["job"]["name"]
is_sanitizer = "ASan" in meta["job"]["name"]
required = requirements["required_registration_apron_tests"] + requirements["additional_source_affected_tests"]
artifact = None
artifact_digests = matching(lambda t: "SHA256 digest of uploaded artifact is " in t)
for i, line in enumerate(lines, 1):
    match = re.search(r"Artifact (.+) has been successfully uploaded! Final size is (\d+) bytes\. Artifact ID is (\d+)", line)
    if match:
        artifact = {"name": match[1], "bytes": int(match[2]), "id": int(match[3]), "line": i}
if artifact is not None and artifact_digests:
    artifact["sha256"] = artifact_digests[-1]["text"].rsplit(" ", 1)[-1]
compile_flags = matching(lambda t: "-fsanitize=address,undefined" in t and " -c " in t and " -o " in t, 4)
support_flags = matching(lambda t: "-fsanitize=address,undefined" in t and "LibraryModel.cpp" in t and " -c " in t, 2)
link_flags = matching(lambda t: "-fsanitize=address,undefined" in t and " -o " in t and " -c " not in t and "libhammond_core.a" in t, 3)
policy = matching(lambda t: any(name + ":" in t for name in ("ASAN_OPTIONS", "UBSAN_OPTIONS", "LSAN_OPTIONS")))
executed_policy = []
for i, line in enumerate(lines):
    if "##[group]Run ctest --preset sanitizers --parallel" in line:
        end = next((j for j in range(i + 1, min(i + 100, len(lines))) if "##[endgroup]" in lines[j]), min(i + 100, len(lines)))
        executed_policy = [{"line": j + 1, "text": lines[j]} for j in range(i, end)
                           if any(name + ":" in lines[j] for name in ("ASAN_OPTIONS", "UBSAN_OPTIONS", "LSAN_OPTIONS"))]
issues = []
if not source_rows:
    issues.append("Exact source revision stdout not located")
if not is_r4:
    if len(rows) != 209 or len(names) != 209 or any(row["total"] != 209 for row in rows):
        issues.append("Actual unique CTest outcome inventory is not exactly 209")
    if any(not row["result"].startswith("Passed") for row in rows):
        issues.append("One or more actual CTest outcomes did not pass")
    if set(required) - names:
        issues.append("Missing required registration/apron or source-affected CTest outcomes")
    if not any(re.fullmatch(r"100% tests passed(?:, 0 tests failed)? out of 209", line) for line in lines):
        issues.append("Final complete 209-test pass summary not located")
else:
    if len(waveforms) != 1 or waveforms[0].get("status") != "pass" or waveforms[0].get("failures") != []:
        issues.append("A single successful full R4 summary with empty failures not located")
    if not any(re.fullmatch(r"Ran 14 tests in .+s", line) for line in lines) or "OK" not in lines:
        issues.append("Complete 14-method R4 admission self-test result not located")
if is_sanitizer:
    for name, value in requirements["sanitizer_job_environment"].items():
        if not any((name + ": " + value) in item["text"] for item in executed_policy):
            issues.append("Missing actual CTest step policy " + name)
    if not compile_flags or not support_flags or not link_flags:
        issues.append("Actual core/support GNU instrumentation compile or link evidence incomplete")
if "Windows MSVC" in meta["job"]["name"]:
    file_events = [row for row in unicode if row.get("event") == "file"]
    complete = [row for row in unicode if row.get("event") == "summary" and row.get("status") == "Complete"]
    refusals = [row for row in unicode if row.get("status") == "ProtectedPath"]
    if len(file_events) != 24 or len(complete) != 1 or complete[0].get("committed_count") != 24 or len(refusals) != 1:
        issues.append("Actual Windows Unicode generator completion/refusal evidence incomplete")
report = {
    "schema": 1, "job_id": args.job_id, "source_commit": SOURCE, "run_id": RUN, "attempt": 1,
    "job": meta["job"],
    "complete_log": {"path": str(archive), "decoded_bytes": len(decoded), "decoded_lines": len(lines),
                     "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
                     "compressed_bytes": len(packed), "compressed_sha256": hashlib.sha256(packed).hexdigest(),
                     "round_trip_verified": True},
    "source_revision_stdout": source_rows,
    "toolchain": matching(lambda t: bool(re.match(r"^(cmake version|ctest version|Python \d|g\+\+ |-- The (CXX|C) compiler identification|Microsoft .*Compiler Version)", t)), 16),
    "architecture": matching(lambda t: t in ("x86_64", "arm64", "AMD64", "aarch64") or t.startswith(("Linux-", "macOS-", "Windows-")), 8),
    "python_install_architecture": matching(lambda t: "pythonLocation:" in t, 2),
    "ctest_outcomes": rows, "unique_ctest_count": len(names),
    "required_missing": sorted(set(required) - names) if not is_r4 else [],
    "summary_lines": matching(lambda t: bool(re.search(r"100% tests passed|tests failed out of|Total Test time \(real\)|^Ran \d+ tests|^OK(?: \(|$)|^FAILED", t))),
    "invocations": matching(lambda t: t.startswith(("ctest --preset ", "python tests/test_rotary_waveform_acceptance.py", "cmake --build build-waveform --target check_rotary_waveform_full"))),
    "instrumentation_compile_examples": compile_flags, "instrumented_library_model_compile": support_flags,
    "instrumentation_link_examples": link_flags, "executed_ctest_sanitizer_environment": executed_policy,
    "sanitizer_policy_lines": policy,
    "sanitizer_exception_scope": ("Source-declared intentional quarantine test disables leak detection only for test_standalone_midi_backend_quarantine; all other tests inherit the strict job policy. Its per-test environment is not printed by non-verbose CTest." if is_sanitizer else None),
    "optional_skip_lines": matching(lambda t: ("skipped" in t.lower() and ("pillow" in t.lower() or "numpy" in t.lower() or re.search(r"skipped=\d+", t.lower())))),
    "reported_error_lines": matching(lambda t: bool(re.search(r"##\[error\]|ERROR: AddressSanitizer|runtime error:|SUMMARY: (?:AddressSanitizer|UndefinedBehaviorSanitizer)|\*\*\*(?:Failed|Timeout)|The following tests FAILED", t)), 40),
    "full_r4_results": waveforms,
    "windows_unicode_generator_records": unicode,
    "uploaded_artifact": artifact,
    "artifact_bodies_independently_downloaded": False,
    "inspection_issues": issues,
}
path = directory / f"job-{args.job_id}-summary-v2.json"
assert not path.exists(), "Frozen per-job summary already exists"
path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
print(json.dumps({"job_id": args.job_id, "name": meta["job"]["name"], "conclusion": meta["job"]["conclusion"],
                  "ctest_count": len(rows), "all_ctest_results_pass": all(row["result"].startswith("Passed") for row in rows),
                  "summary_lines": report["summary_lines"], "toolchain": report["toolchain"],
                  "architecture": report["architecture"], "full_r4_results": waveforms,
                  "inspection_issues": issues, "artifact": artifact, "decoded_bytes": len(decoded),
                  "compressed_bytes": len(packed), "summary_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}))
