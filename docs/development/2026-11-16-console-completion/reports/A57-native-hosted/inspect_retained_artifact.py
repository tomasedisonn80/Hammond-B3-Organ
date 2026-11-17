"""Read only retained hosted evidence; never execute repository tests or binaries."""
import collections
import gzip
import hashlib
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

BASE = pathlib.Path(__file__).resolve().parent
POLICY = json.loads((BASE / "source-policy-preflight.json").read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inspect(job_id, artifact_id):
    path = BASE / f"job-{job_id}-review.json"
    review = json.loads(path.read_text())
    archive = BASE / f"artifact-{artifact_id}.zip"
    zip_bytes = archive.read_bytes()
    with zipfile.ZipFile(archive) as z:
        prefix = "standalone-sanitizer-logs/" if any(n.startswith("standalone-sanitizer-logs/") for n in z.namelist()) else "standalone-ci-logs/"
        sanitizer = prefix == "standalone-sanitizer-logs/"
        def read(name):
            return z.read(prefix + name)
        def obj(name):
            return json.loads(read(name))
        provenance = obj("provenance.json")
        discovered = obj("ctest-discovered.json")["tests"]
        tree = ET.fromstring(read("ctest.xml"))
        log = read("ctest.log").decode("utf-8")
        numbered = collections.defaultdict(list)
        results = {}
        for line in log.splitlines():
            match = re.match(r"^(\d+): ?(.*)$", line)
            if match:
                numbered[int(match[1])].append(match[2])
            match = re.search(r"\d+/\d+ Test\s+#(\d+):\s+(\S+)\s+\.+\s+(.+?)\s+([\d.]+) sec", line)
            if match:
                results[match[2]] = {"number": int(match[1]), "result": match[3], "seconds": float(match[4])}
        outputs = {name: "\n".join(numbered[item["number"]]) for name, item in results.items()}
        report_names = ["test_standalone_title_density", "test_standalone_header_material", "test_standalone_header_statistics", "test_standalone_performance_plate", "test_standalone_performance_plate_numerical"]
        reports = {}
        for name in report_names:
            content = outputs.get(name, "")
            candidates = []
            for match in re.finditer(r"\{", content):
                try:
                    value, end = json.JSONDecoder().raw_decode(content[match.start():])
                except ValueError:
                    continue
                if isinstance(value, dict) and any(key in value for key in ("status", "checks_evaluated", "protocol_passed")):
                    candidates.append((end, value))
            if candidates:
                reports[name] = max(candidates, key=lambda item: item[0])[1]
        names = {item["name"] for item in discovered}
        required = set(POLICY["sanitizer_test_to_target"] if sanitizer else POLICY["mandatory_platform_names"])
        methods = []
        for name, content in outputs.items():
            for line in content.splitlines():
                if re.search(r"\b(skip|skipped|not run)\b", line, re.I):
                    methods.append({"test": name, "line": line})
        tests = []
        properties = {item["name"]: {p["name"]: p["value"] for p in item.get("properties", [])} for item in discovered}
        for item in tree.iter("testcase"):
            name = item.attrib["name"]
            tests.append({"name": name, "seconds": float(item.attrib["time"]), "junit_status": item.attrib.get("status"), "failed": item.find("failure") is not None, "skipped": item.find("skipped") is not None, "ctest_result": results.get(name), "timeout_seconds": properties[name].get("TIMEOUT", 180), "timeout_source": "explicit CTest property" if "TIMEOUT" in properties[name] else "CI --timeout 180", "required": name in required, "run_serial": properties[name].get("RUN_SERIAL", False), "disabled": properties[name].get("DISABLED", False)})
        assert names == {item["name"] for item in tests} == set(results)
        assert not required - names
        assert provenance["source_commit"] == review["source_sha"]
        assert int(provenance["run_id"]) == review["job"]["run_id"]
        assert int(provenance["run_attempt"]) == review["job"]["run_attempt"]
        if sanitizer:
            assert names == required
        report_bytes = (json.dumps(reports, sort_keys=True, indent=2) + "\n").encode()
        report_path = BASE / f"job-{job_id}-numerical-reports.json.gz"
        report_path.write_bytes(gzip.compress(report_bytes, mtime=0))
        numerical = {}
        for name, report in reports.items():
            scalar = {key: value for key, value in report.items() if not isinstance(value, (list, dict))}
            if name.endswith("title_density"):
                scalar.update(evaluated_cases=len(report.get("cases", [])), resources=report.get("resources"), inventory=report.get("inventory"))
            if "numerical" in report:
                scalar["numerical"] = {key: value for key, value in report["numerical"].items() if key != "results"}
                scalar["resources"] = report.get("resources")
                scalar["identities"] = report.get("identities")
            if "candidate_screens" in report:
                scalar["candidate_screens"] = {key: value for key, value in report["candidate_screens"].items() if key != "checks"}
            numerical[name] = scalar
        review.update(status="TERMINAL_SUCCESS_LOG_AND_ARTIFACT_REVIEWED" if review["job"]["conclusion"] == "success" else "TERMINAL_FAILURE_LOG_AND_ARTIFACT_REVIEWED", artifact={"id": artifact_id, "path": archive.name, "bytes": len(zip_bytes), "sha256": digest(zip_bytes), "members": [{"path": item.filename, "bytes": item.file_size, "sha256": digest(z.read(item.filename))} for item in z.infolist()]}, provenance={key: value for key, value in provenance.items() if key not in ("dependencies", "source_files", "midi")}, ctest={"junit": tree.attrib, "discovered_count": len(names), "required_count": len(required), "missing_required": sorted(required - names), "extra_to_required": sorted(names - required), "selected_names": sorted(names), "results": tests, "method_skip_lines": methods, "summary_lines": [line for line in log.splitlines() if "tests passed" in line or "Total Test time (real)" in line], "disabled_names": [name for name, p in properties.items() if p.get("DISABLED", False)], "sanitizer_environment_overrides": {name: [v for v in p.get("ENVIRONMENT", []) if v.split("=", 1)[0] in ("ASAN_OPTIONS", "UBSAN_OPTIONS", "LSAN_OPTIONS")] for name, p in properties.items() if any(v.split("=", 1)[0] in ("ASAN_OPTIONS", "UBSAN_OPTIONS", "LSAN_OPTIONS") for v in p.get("ENVIRONMENT", []))}}, numerical=numerical, numerical_reports={"path": report_path.name, "decoded_bytes": len(report_bytes), "decoded_sha256": digest(report_bytes)}, library_suite_outputs={name: output for name, output in outputs.items() if name.startswith("test_standalone_library_")}, lifecycle_and_boundary_outputs={name: output for name, output in outputs.items() if name in ("test_standalone_native_calibration", "test_standalone_replay_paint_boundary", "test_standalone_semantic_paint_boundary")}, skipped_steps=[step for step in review["job"]["steps"] if step["conclusion"] == "skipped"])
        if not sanitizer:
            installed, staged = obj("installed-inventory.json"), obj("staged-inventory.json")
            review["package"] = {"installed_payload_files": len(installed["payload"]["files"]), "installed_executable": next(item for item in installed["payload"]["files"] if item["path"].startswith("bin/")), "staged_top_level_keys": list(staged), "midi": {key: value for key, value in provenance.get("midi", {}).items() if key != "capabilities"}, "relocated_smoke": obj("relocated-smoke.json"), "sdl_backends": obj("sdl-backends.json")}
        else:
            review["instrumentation"] = obj("instrumentation.json")
        path.write_text(json.dumps(review, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"job": job_id, "status": review["status"], "tests": len(tests), "required": len(required), "skips": methods, "numerical": {name: {key: value for key, value in report.items() if key in ("status", "checks", "checks_evaluated", "failed_checks", "cases", "main_cases", "evaluated_cases", "candidate_screens")} for name, report in numerical.items()}, "junit": tree.attrib}))


if __name__ == "__main__":
    inspect(int(sys.argv[1]), int(sys.argv[2]))
