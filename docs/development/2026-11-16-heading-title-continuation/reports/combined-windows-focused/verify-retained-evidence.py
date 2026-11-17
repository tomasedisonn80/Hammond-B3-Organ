#!/usr/bin/env python3
"""Read-only verification of retained focused evidence; no native/test execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zlib

SOURCE = "54859886268ce83c36f359c43327f7c72a77ae82"
TREE = "f5f8f037af301f8b1ff5b9b4a00ff5581647667a"
WORKFLOW = "41f617f77514a8091f49ab98737a0ca3c4505b4e"
ap = argparse.ArgumentParser()
ap.add_argument("--repo", type=Path, required=True)
ap.add_argument("--artifacts", type=Path, required=True)
args = ap.parse_args()
r, p = args.repo.resolve(), args.artifacts.resolve()
s = r / "docs/development/2026-11-16-heading-title-continuation/reports"


def read(name):
    return json.loads((p / name).read_bytes())


def sha(data):
    return hashlib.sha256(data).hexdigest()


pro, post, comp = (read(name) for name in (
    "provenance.json", "source-verification-after.json", "fixture-compile-and-executable-identities.json"))
assert pro["source_commit"] == post["source_commit"] == SOURCE
assert pro["source_tree"] == post["source_tree"] == TREE
assert pro["workflow_commit"] == post["workflow_commit"] == WORKFLOW
assert post["changed_source_inputs"] == post["changed_fixture_executables"] == []
assert post["original_ctest_exit"] == "0"
for name, expected in pro["source_sha256"].items():
    assert sha(subprocess.check_output(["git", "show", SOURCE + ":" + name], cwd=r)) == expected, name
assert len(pro["source_sha256"]) == post["checked_inputs"] == 566
for name, rows in comp["actual_msvc_commands"].items():
    assert rows
    for row in rows:
        assert re.findall(r"(?:^|\s)(/W[0-4])(?=\s|$)", row["command"], re.I)[-1].upper() == "/W4"
        assert re.findall(r"(?:^|\s)(/WX-?)(?=\s|$)", row["command"], re.I)[-1].upper() == "/WX"
assert len(comp["actual_msvc_commands"]) == 3
tests = []
for test in ET.parse(p / "ctest.xml").getroot().findall("testcase"):
    assert test.attrib["status"] == "run" and test.find("failure") is None and test.find("skipped") is None
    tests.append(dict(name=test.attrib["name"], seconds=float(test.attrib["time"])))
expected_tests = {"python_test_capture_standalone_interface", "python_test_compare_header_material",
    "python_test_compare_performance_plate", "test_standalone_footage_typography_raster",
    "test_standalone_title_density", "test_standalone_header_material", "test_standalone_performance_plate",
    "test_standalone_performance_plate_numerical", "test_standalone_header_statistics"}
assert len(tests) == 9 and {test["name"] for test in tests} == expected_tests
log = (p / "ctest.log").read_text()
for count in (45, 32, 64):
    assert re.search(r"Ran " + str(count) + r" tests", log)
captures = {}
for stem, target in (("title-case0", "test_standalone_footage_typography_raster"),
                     ("header-case46", "test_standalone_header_material")):
    record = read(stem + "-capture.json")
    raw = (p / (stem + "-header.bin")).read_bytes()
    assert len(raw) == record["raw_header_bytes"] and sha(raw) == record["raw_header_sha256"]
    assert record["strict_differences"] == record["capture_errors"] == []
    assert record["returncode"] == record["stderr_bytes"] == 0
    assert record["unchanged_protocol_parser"] == "passed"
    assert record["executable_sha256"] == comp["executables"][target]["sha256"]
    captures[stem] = record
report, retention = read("p1-numerical/report.json"), read("p1-output-retention.json")
assert report["passed"] and report["failures"] == [] and report["checks_evaluated"] == 191
assert retention["retention_complete"] and retention["errors"] == [] and retention["extra_native_invocations"] == 0
assert report["after_canonical"]["numerical_screens"]["passed"] == 62
assert report["after_canonical"]["numerical_screens"]["failed"] == 0
fixture = comp["executables"]["test_standalone_performance_plate"]
assert all(report["inputs"]["after_executable"][key] == fixture[key] for key in ("bytes", "sha256"))
tool = r / "tools/compare_performance_plate.py"
assert sha(tool.read_bytes()) == pro["source_sha256"]["tools/compare_performance_plate.py"]
spec = importlib.util.spec_from_file_location("retained_p1_verifier", tool)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def decode(directory, command, channel):
    item = command[channel]
    packed = (directory / item["path"]).read_bytes()
    assert len(packed) == item["bytes"] and sha(packed) == item["sha256"]
    cap = module.MAX_STDERR if channel == "stderr" else module.MAX_HEADER if command["name"] == "after-list" else module.MAX_STREAM
    decoder = zlib.decompressobj()
    raw = decoder.decompress(packed, cap + 1)
    assert len(raw) <= cap and decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
    assert len(raw) == item["raw_bytes"] and sha(raw) == item["raw_sha256"]
    return raw


streams = {}
for command in report["commands"]:
    assert command["exit_code"] == 0 and command["errors"] == []
    assert not decode(p / "p1-numerical", command, "stderr")
    streams[command["name"]] = decode(p / "p1-numerical", command, "stdout")
assert set(streams) == {"after-list", "after-00"}
module.validate_inventory(streams["after-list"], module.scenarios())
header, rgba = module.parse_frame(streams["after-00"], 0)
linux = s / "console-integration/final-p1-numerical-retained"
linux_report = json.loads((linux / "report.json").read_bytes())
linux_streams = {command["name"]: decode(linux, command, "stdout") for command in linux_report["commands"]}
module.validate_inventory(linux_streams["after-list"], module.scenarios())
assert streams["after-00"] == linux_streams["after-00"]
assert streams["after-list"] == linux_streams["after-list"][:-1] + b"\r\n"
assert linux_streams["after-list"].endswith(b"\n") and not linux_streams["after-list"].endswith(b"\r\n")
assert module.equal(module.strict_json(streams["after-list"]), module.strict_json(linux_streams["after-list"]))
result = dict(schema=1, source_commit=SOURCE, source_tree=TREE, workflow_commit=WORKFLOW,
    run_id=44036732040, job_id=133881292377, attempt=1, focused_conclusion="success",
    ctests=tests, ctest_total_seconds=76.52, python_method_counts=dict(capture=45, header=32, P1=64),
    source_inputs_independently_compared_to_git=566, source_after=post,
    actual_msvc_three_fixtures_W4_WX_verified=True, executables=comp["executables"],
    supplemental_captures=captures,
    p1=dict(checks=191, failed_checks=0, screens_passed=62,
        fixture_source_admission=report["fixture_source_admission"],
        retained_original_streams_bounded_decoded_and_verified=True,
        complete_34_case_inventory_valid=True, canonical_stream_bytes=len(streams["after-00"]),
        canonical_stream_sha256=sha(streams["after-00"]), canonical_rgba_sha256=sha(rgba),
        Linux_final_consumer_full_canonical_stream_byte_identical=True,
        Linux_Windows_complete_typed_inventories_equal=True,
        raw_inventory_bytes_equal=False,
        inventory_difference="Only the sole trailing LF becomes CRLF on Windows; both unchanged strict validators pass.",
        inventory_identities={side: dict(bytes=len(payload), sha256=sha(payload)) for side, payload in
            (("Linux", linux_streams["after-list"]), ("Windows", streams["after-list"]))},
        no_extra_P1_native_execution=True),
    artifact_id=14308285378, artifact_all_members_verified=41,
    closure_of_A52_focused_condition=True,
    admitted_for_guarded_main_update_if_prior_jobs_terminal_and_expected_ref_matches=True,
    scope="Closes only the reviewed focused Windows condition using actual complete source-bound evidence. Original failures remain. The full16-family new-main matrix is still required. No whole-interface1:1, device, physical calibration or release-completion claim.")
output = s / "combined-windows-focused/candidate-qualified.json"
with output.open("x") as stream:
    json.dump(result, stream, indent=2)
    stream.write("\n")
print(json.dumps(dict(qualification="pass", source=SOURCE, ctests=len(tests),
    compared_source_inputs=566, P1_full_canonical_stream_equal=True,
    inventory_raw_bytes_equal=False, inventory_typed_content_equal=True, P1screens=62)))
