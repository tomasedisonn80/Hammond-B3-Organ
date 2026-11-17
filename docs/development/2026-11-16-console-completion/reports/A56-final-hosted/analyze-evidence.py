"""Read retained hosted evidence only; never launch product tests or executables."""
from pathlib import Path
import gzip
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile

BASE = Path(__file__).resolve().parent
SOURCE = "523c1979334b0fbb624ce120128a0b8ada078383"
EXPECTED_METHODS = {
    "python_test_capture_standalone_interface": 45,
    "python_test_compare_header_material": 41,
    "python_test_compare_performance_plate": 71,
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(name, value):
    destination = BASE / name
    assert not destination.exists(), destination
    destination.write_text(json.dumps(value, indent=2) + "\n")


def unittest_summary(output):
    found = re.search(r"Ran (\d+) tests? in ([0-9.]+)s", output)
    if not found:
        return None
    ok = re.search(r"(?m)^OK(?: \(skipped=(\d+)\))?\s*$", output)
    return {
        "methods": int(found[1]),
        "seconds": float(found[2]),
        "result": "OK" if ok else "NON_OK",
        "skipped_methods": int(ok[1] or 0) if ok else None,
    }


def review_logs():
    summaries = []
    pattern = re.compile(r"(?m)^.*?\s(\d+)/(\d+)\s+Test\s+#(\d+):\s+(\S+)\s+\.+\s+(.*?)\s+([0-9.]+)\s+sec")
    for path in sorted(BASE.glob("job-*.log.gz")):
        output = path.name.replace(".log.gz", ".review.json")
        if (BASE / output).exists():
            continue
        raw = gzip.decompress(path.read_bytes())
        receipt = json.loads(path.with_name(path.name.replace(".log.gz", ".log.receipt.json")).read_text())
        assert len(raw) == receipt["raw_bytes"] and digest(raw) == receipt["raw_sha256"]
        text = raw.decode("utf-8")
        records = [{"ordinal": int(m[1]), "total": int(m[2]), "test_id": int(m[3]), "name": m[4], "result": m[5], "seconds": float(m[6])} for m in pattern.finditer(text)]
        source_lines = [line for line in text.splitlines() if re.search(r"Z\s+" + SOURCE + r"\s*$", line)]
        summary = {
            "job_id": receipt["job_id"], "source": SOURCE,
            "source_recorded_as_standalone_line": bool(source_lines),
            "source_lines": source_lines, "log": receipt,
            "ctest": {"records": records, "count": len(records), "unique_names": len({x["name"] for x in records}), "passed": sum(x["result"] == "Passed" for x in records), "nonpassed": [x for x in records if x["result"] != "Passed"], "wall_seconds": [float(x) for x in re.findall(r"Total Test time \(real\) =\s*([0-9.]+) sec", text)]},
            "error_annotations": [line for line in text.splitlines() if "##[error]" in line],
            "decisive_lines": [line for line in text.splitlines() if re.search(r"tests passed|tests failed|Total Test time|The unfiltered .*includes all|Ran \d+ tests|^.*Z OK(?: |$)|Process completed with exit code|Artifact .* successfully|Artifact download URL", line)],
            "strict_sanitizer_environment_lines": [line for line in text.splitlines() if any(x in line for x in ("ASAN_OPTIONS: detect_leaks=1:halt_on_error=1", "UBSAN_OPTIONS: print_stacktrace=1:halt_on_error=1", "LSAN_OPTIONS: exitcode=23"))],
            "instrumented_build_lines": [line for line in text.splitlines() if "-fsanitize=address,undefined" in line and any(x in line for x in ("Engine.cpp", "LibraryModel.cpp", "library_model.cpp", "test_standalone_library_model", "test_standalone_library"))],
        }
        save(output, summary)
        summaries.append({"job_id": summary["job_id"], "source_recorded": bool(source_lines), "ctests": len(records), "passed": summary["ctest"]["passed"], "nonpassed": summary["ctest"]["nonpassed"], "wall_seconds": summary["ctest"]["wall_seconds"], "errors": len(summary["error_annotations"])})
    return summaries


def review_artifacts():
    summaries = []
    for path in sorted(BASE.glob("artifact-*.zip")):
        output = path.name.replace(".zip", ".review.json")
        if (BASE / output).exists():
            continue
        receipt = json.loads(path.with_suffix(".receipt.json").read_text())
        raw = path.read_bytes()
        assert digest(raw) == receipt["archive_sha256"] and len(raw) == receipt["archive_bytes"]
        review = {"artifact_id": receipt["artifact_id"], "source": SOURCE, "receipt": path.with_suffix(".receipt.json").name, "name": receipt["name"], "archive_digest_verified": True}
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            entries = [{"path": info.filename, "bytes": info.file_size, "compressed_bytes": info.compress_size, "sha256": digest(archive.read(info))} for info in archive.infolist()]
            review["entries"] = entries
            names = archive.namelist()
            source_names = [name for name in names if name.endswith("/source-revision.txt")]
            review["source_revision_records"] = {name: archive.read(name).decode().strip() for name in source_names}
            assert source_names and all(value == SOURCE for value in review["source_revision_records"].values())
            if "ci-logs/ctest.xml" in names:
                junit = ET.fromstring(archive.read("ci-logs/ctest.xml"))
                tests = junit.findall(".//testcase")
                records = [{**test.attrib, "failure": test.find("failure") is not None, "error": test.find("error") is not None, "skipped": test.find("skipped") is not None} for test in tests]
                review["junit"] = {"attributes": junit.attrib, "records": records, "record_count": len(records), "unique_names": len({x["name"] for x in records}), "nonpassing": [x for x in records if x["failure"] or x["error"] or x["skipped"] or x.get("status") != "run"]}
                discovered = json.loads(archive.read("ci-logs/ctest-discovered.json"))["tests"]
                review["discovered_ctests"] = [{"name": test["name"], "command": test.get("command"), "disabled": any(prop["name"] == "DISABLED" and prop["value"] for prop in test.get("properties", []))} for test in discovered]
                review["discovery_matches_executed_names"] = {x["name"] for x in discovered} == {x["name"] for x in records}
                last_name = next(name for name in names if name.endswith("/Testing/Temporary/LastTest.log"))
                last_text = archive.read(last_name).decode("utf-8")
                internal = []
                selected = []
                for test in tests:
                    text = test.findtext("system-out") or ""
                    parsed = unittest_summary(text)
                    if parsed:
                        internal.append({"name": test.attrib["name"], **parsed})
                    if test.attrib["name"] in EXPECTED_METHODS:
                        assert parsed
                        section = re.search(r"Testing: " + re.escape(test.attrib["name"]) + r"\r?\n.*?\r?\nCommand: ([^\n]+)", last_text, re.S)
                        selected.append({"name": test.attrib["name"], **parsed, "expected_source_methods": EXPECTED_METHODS[test.attrib["name"]], "count_matches_exact_source": parsed["methods"] == EXPECTED_METHODS[test.attrib["name"]], "execution_command": section[1] if section else None, "system_out": text})
                review["internal_unittest_summaries"] = internal
                review["requested_method_suites"] = selected
                review["requested_method_suites_all_present"] = {x["name"] for x in selected} == set(EXPECTED_METHODS)
                review["standard_library_apron"] = {name: unittest_summary(archive.read(name).decode()) for name in names if name in ("ci-logs/apron-art-stdlib.log", "ci-logs/apron-raster-stdlib.log")}
            review["additional_qualification_paths"] = [name for name in names if name.endswith("/qualification.json")]
        save(output, review)
        summaries.append({"artifact_id": review["artifact_id"], "name": review["name"], "entries": len(entries), "junit": review.get("junit", {}).get("attributes"), "methods": [{key: value for key, value in x.items() if key not in ("system_out", "execution_command")} for x in review.get("requested_method_suites", [])]})
    return summaries


if __name__ == "__main__":
    print(json.dumps({"logs": review_logs(), "artifacts": review_artifacts()}, indent=2))
