#!/usr/bin/env python3
"""Inspect retained hosted bytes only; never build, test, install, or load a plugin."""
import datetime
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import struct
import sys
import tarfile
import xml.etree.ElementTree as ET
import zipfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[4]
SOURCE = "d2ed03b94114e35d0caa65968d11afe896a5e9f5"
TREE = "45f3f2bc1bc844061be7d1303b13b10bfaba9938"
RUN = 44034656821
FAMILIES = {
    "linux": (133874509035, "ubuntu-24.04-X64", "Linux", "X64", "ELF64", "x86_64"),
    "windows": (133874509343, "windows-2022-X64", "Windows", "X64", "PE32+", "x86_64"),
    "mac_arm": (133874509381, "macos-15-ARM64", "macOS", "ARM64", "Mach-O64", "arm64"),
    "mac_intel": (133874509387, "macos-15-intel-X64", "macOS", "X64", "Mach-O64", "x86_64"),
}
COMMON = {"test_native_install", "hammond_vst3_validator", "test_native_controller",
          "test_native_abi", "test_native_behavior", "test_native_automation",
          "test_native_concurrency"}
EXPECTED_TIMEOUTS = {"test_native_install": 240, "hammond_vst3_validator": 180,
                     "test_native_controller": 300, "test_native_abi": 180,
                     "test_native_behavior": 180, "test_native_automation": 180,
                     "test_native_concurrency": 240, "test_native_realtime": 180}


def identity(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def write_original(destination, raw):
    destination.parent.mkdir(parents=True, exist_ok=True)
    compressed = gzip.compress(raw, mtime=0)
    destination.write_bytes(compressed)
    assert gzip.decompress(destination.read_bytes()) == raw
    return {"path": destination.relative_to(ROOT).as_posix(),
            "original": identity(raw), "compressed": identity(compressed)}


def json_record(lines):
    rows = [json.loads(line) for line in lines if line.startswith("{")]
    assert len(rows) == 1, "Expected one complete JSON result"
    return rows[0]


def inspect_native_header(raw):
    if raw[:4] == b"\x7fELF":
        assert raw[4:6] == b"\x02\x01"
        kind, cpu = struct.unpack_from("<HH", raw, 16)
        assert kind == 3
        return {"format": "ELF64", "architecture": {62: "x86_64", 183: "arm64"}[cpu],
                "machine": cpu, "module_kind": "ET_DYN", "byte_order": "little"}
    if raw[:4] == b"\xcf\xfa\xed\xfe":
        cpu = struct.unpack_from("<I", raw, 4)[0]
        kind = struct.unpack_from("<I", raw, 12)[0]
        assert kind in (6, 8)
        return {"format": "Mach-O64", "architecture": {0x01000007: "x86_64", 0x0100000C: "arm64"}[cpu],
                "cpu_type": cpu, "file_type": kind, "byte_order": "little"}
    assert raw[:2] == b"MZ"
    offset = struct.unpack_from("<I", raw, 0x3C)[0]
    assert raw[offset:offset + 4] == b"PE\0\0"
    cpu = struct.unpack_from("<H", raw, offset + 4)[0]
    assert struct.unpack_from("<H", raw, offset + 24)[0] == 0x20B
    assert struct.unpack_from("<H", raw, offset + 22)[0] & 0x2000
    return {"format": "PE32+", "architecture": {0x8664: "x86_64", 0xAA64: "arm64"}[cpu],
            "machine": cpu, "optional_header_magic": "0x20b", "dll": True}


def inspect(family, metadata):
    job_id, token, runner_os, runner_arch, expected_format, expected_arch = FAMILIES[family]
    job = next(j for j in metadata["jobs"] if j["id"] == job_id)
    assert job["head_sha"] == SOURCE and job["run_id"] == RUN and job["run_attempt"] == 1
    assert job["status"] == "completed" and job["conclusion"] == "success"
    assert job["runner_id"] and job["runner_name"]
    required_steps = {
        "Record actual source and runner provenance",
        "Explicitly acquire and verify the locked external SDK",
        "Build the bundle and every native test input",
        "Validate the actual module and run the native tests",
        "Inventory and archive the validated native bundle",
        "Retain complete source, dependency, build and test diagnostics",
        "Retain the qualified bundle and byte inventory",
    }
    selected = [s for s in job["steps"] if s["name"] in required_steps]
    assert len(selected) == len(required_steps) and all(s["conclusion"] == "success" for s in selected)
    archives = {}
    for kind in ("diagnostics", "bundle"):
        expected_name = f"native-vst3-{token}-release-{kind}-{SOURCE}-1"
        meta = next(a for a in metadata["artifacts"] if a["name"] == expected_name)
        assert meta["workflow_run"]["head_sha"] == SOURCE and meta["workflow_run"]["id"] == RUN
        assert not meta["expired"]
        path = BASE / f'artifact-{meta["id"]}.zip'
        raw = path.read_bytes()
        assert len(raw) == meta["size_in_bytes"]
        assert "sha256:" + identity(raw)["sha256"] == meta["digest"]
        archives[kind] = {"metadata": meta, "raw": raw, "path": path.relative_to(ROOT).as_posix()}
    with zipfile.ZipFile(io.BytesIO(archives["diagnostics"]["raw"])) as archive:
        members = archive.infolist()
        assert len(members) == len({m.filename for m in members})
        assert len(members) <= 64 and sum(m.file_size for m in members) < 10_000_000
        raw = {m.filename: archive.read(m) for m in members}
    provenance = json.loads(raw["native-ci-logs/provenance.json"])
    assert provenance["source_commit"] == SOURCE and provenance["source_tree"] == TREE
    assert provenance["run_id"] == str(RUN) and provenance["run_attempt"] == "1"
    assert provenance["runner_os"] == runner_os and provenance["runner_arch"] == runner_arch
    assert provenance["configuration"] == "Release"
    lock_bytes = (ROOT / "data/dependencies/vst3-sdk-lock.json").read_bytes()
    assert raw["native-ci-logs/vst3-sdk-lock.json"] == lock_bytes
    lock = json.loads(lock_bytes)
    expected_checkouts = [{"path": ".", "commit": lock["commit"]}] + [
        {"path": item["path"], "commit": item["commit"]} for item in lock["required_submodules"]]
    acquisition = json_record(raw["native-ci-logs/sdk-acquisition.log"].decode().splitlines())
    verification = json_record(raw["native-ci-logs/sdk-verification.log"].decode().splitlines())
    for record in (acquisition, verification):
        assert record["verified_checkouts"] == expected_checkouts
        assert record["primary_licenses_verified"] == 5 and record["embedded_json_verified"] is True
    assert acquisition["network_used"] is True and verification["network_used"] is False
    ctest = raw["native-ci-logs/ctest.log"].decode()
    complete_log_path = BASE / f"job-{job_id}.log.gz"
    complete_log_bytes = gzip.decompress(complete_log_path.read_bytes())
    complete_log = complete_log_bytes.decode("utf-8-sig")
    assert SOURCE in complete_log
    job_lines = [re.sub(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+Z ?", "", s)
                 for s in complete_log.splitlines()]
    ctest_lines = ctest.splitlines()
    start_positions = [i for i, line in enumerate(job_lines) if line == ctest_lines[0]]
    assert any(job_lines[start:start + len(ctest_lines)] == ctest_lines for start in start_positions), "Job and diagnostic CTest streams differ"
    xml = ET.fromstring(raw["native-ci-logs/ctest.xml"])
    expected = COMMON | ({"test_native_realtime"} if family == "linux" else set())
    cases = xml.findall("testcase")
    assert len(cases) == len(expected) and {c.get("name") for c in cases} == expected
    assert int(xml.get("tests")) == len(cases)
    assert all(int(xml.get(k, "0")) == 0 for k in ("failures", "errors", "skipped", "disabled"))
    assert all(c.get("status") == "run" and all(c.find(t) is None for t in ("failure", "error", "skipped")) for c in cases)
    starts = re.findall(r"(?m)^\s*Start (\d+): (\S+)\s*$", ctest)
    assert len(starts) == len(expected) and {n for _, n in starts} == expected
    blocks = {name: re.findall(r"(?m)^" + number + r": ?(.*)$", ctest) for number, name in starts}
    passing = re.findall(r"(?m)^\s*\d+/\d+ Test #\d+:\s+(\S+).*?Passed\s+([0-9.]+) sec\s*$", ctest)
    assert len(passing) == len(expected) and {name for name, _ in passing} == expected
    assert re.search(r"100% tests passed(?:, 0 tests failed)? out of " + str(len(expected)), ctest)
    timeout_records = {name: int(next(s.rsplit(":", 1)[1] for s in lines if s.startswith("Test timeout computed to be:")))
                       for name, lines in blocks.items()}
    assert all(timeout_records[name] == EXPECTED_TIMEOUTS[name] for name in expected)
    validator = "\n".join(blocks["hammond_vst3_validator"])
    command = next(s for s in blocks["hammond_vst3_validator"] if s.startswith("Test command:"))
    assert "validator" in command and "HammondB3.vst3" in command
    assert "* Loading module..." in validator and "name = Hammond B3 Nominal" in validator
    assert re.findall(r"Result: (\d+) tests passed, (\d+) tests failed", validator) == [("47", "0")]
    assert "This component exports 47 parameter(s)" in validator
    class_ids = [lock["plugin_class_ids"][name]["fuid_hex"] for name in ("processor", "controller")]
    assert all(cid in validator for cid in class_ids) and validator.count("sdkVersion = VST 3.8.1") == 2
    abi = json_record(blocks["test_native_abi"])
    install = json_record(blocks["test_native_install"])
    assert abi["suite"] == "native-abi-v1" and abi["descriptors"] == 47
    assert abi["maximum_audio_error"] == 0 and abi["compared_frames"] == 229725
    assert install["suite"] == "native-install-v1" and install["relocated_abi"] == abi
    assert any(re.fullmatch(r"Ran 2 tests in [0-9.]+s", line) for line in blocks["test_native_install"])
    assert "OK" in blocks["test_native_install"]
    with zipfile.ZipFile(io.BytesIO(archives["bundle"]["raw"])) as archive:
        assert set(archive.namelist()) == {"HammondB3-Release.tar.gz", "inventory.json", "archive.sha256"}
        assert sum(m.file_size for m in archive.infolist()) < 5_000_000
        bundle_archive = archive.read("HammondB3-Release.tar.gz")
        archive_digest = archive.read("archive.sha256")
        inventory_bytes = archive.read("inventory.json")
    assert archive_digest.decode().split() == [identity(bundle_archive)["sha256"], "HammondB3-Release.tar.gz"]
    assert inventory_bytes == raw["native-ci-logs/build-inventory.json"]
    inventory = json.loads(inventory_bytes)
    assert inventory["source"]["revision"] == SOURCE and inventory["configuration"] == "Release"
    assert inventory["sdk_lock"]["sha256"] == identity(lock_bytes)["sha256"]
    assert inventory["sdk_lock"]["root_commit"] == lock["commit"]
    files = {f["path"]: f for f in inventory["files"]}
    assert len(files) == inventory["file_count"] and len(files) <= 512
    payload = {}
    with tarfile.open(fileobj=io.BytesIO(bundle_archive), mode="r:gz") as archive:
        members = archive.getmembers()
        assert len(members) <= 512 and sum(m.size for m in members) < 256 * 1024 * 1024
        for member in members:
            name = PurePosixPath(member.name)
            assert not name.is_absolute() and ".." not in name.parts and name.parts[0] == "HammondB3.vst3"
            assert member.isdir() or member.isfile()
            if member.isfile():
                relative = name.relative_to("HammondB3.vst3").as_posix()
                assert relative in files and relative not in payload and member.size <= 128 * 1024 * 1024
                data = archive.extractfile(member).read()
                assert identity(data) == {k: files[relative][k] for k in ("bytes", "sha256")}
                assert member.mode == int(files[relative]["mode_octal"], 8)
                payload[relative] = data
    assert set(payload) == set(files) and sum(map(len, payload.values())) == inventory["total_bytes"]
    assert install["payload_files"] == len(payload)
    assert install["bundle_sha256"] == {name: identity(data)["sha256"] for name, data in payload.items()}
    module = inventory["module"]
    header = inspect_native_header(payload[module["path"]])
    assert module["format"] == header["format"] == expected_format
    assert module["architectures"] == [header["architecture"]] == [expected_arch]
    moduleinfo = payload["Contents/Resources/moduleinfo.json"]
    assert all(cid.encode() in moduleinfo for cid in class_ids)
    assert identity(payload["Contents/Resources/VST3_SDK_LICENSE.txt"])["sha256"] == lock["license"]["sha256"]
    assert payload["Contents/Resources/THIRD_PARTY_NOTICES.md"] == (ROOT / "THIRD_PARTY_NOTICES.md").read_bytes()
    realtime = None
    if family == "linux":
        rt = blocks["test_native_realtime"]
        rows = [line.split() for line in rt if re.match(r"^(enabled|preset|dense|maximum|carry|output-shape|rejected|setProcessing) \d", line)]
        assert len(rows) == 8 and all(len(row) == 11 for row in rows)
        assert all(int(row[7]) == 0 and int(row[8]) == 0 for row in rows)
        assert sum(int(row[1]) + int(row[2]) for row in rows) == 193
        calibrations = [s for s in rt if s.startswith("module calibration ")]
        assert len(calibrations) == 2 and all("create new=1 delete=0; release new=0 delete=1 refs=0" in s for s in calibrations)
        scope = next(s for s in rt if s.startswith("Scope:"))
        assert scope == "Scope: Linux calling-thread global C++ new/delete; timings are observations, not device deadlines."
        realtime = {"regions": 193, "processing_paths_cpp_new_delete_zero": True,
                    "calibrations": calibrations, "rows": rows,
                    "summary": next(s for s in rt if s.startswith("regions=")), "scope": scope}
    warnings = {}
    for name in ("configure.log", "build.log"):
        lines = raw["native-ci-logs/" + name].decode().splitlines()
        warnings[name] = [s for s in lines if re.search(
            r"(?i)(?:^|\s)(?:warning(?:\s+[A-Z]\d+)?:|error(?:\s+[A-Z]\d+)?:|fatal error:)"
            r"|^CMake (?:Warning|Error)|Failed to|not supported|not found|no valid", s)]
    configure_text = raw["native-ci-logs/configure.log"].decode()
    build_text = raw["native-ci-logs/build.log"].decode()
    selftest_lines = [s for s in build_text.splitlines() if re.search(r"selftest|Executed \d+ Tests|Failed \d+ Tests", s)]
    compiler_lines = [s for s in configure_text.splitlines() if "compiler identification" in s]
    signing_lines = [s for s in (configure_text + "\n" + build_text).splitlines()
                     if re.search(r"codesign|code.sign|signature", s, re.I)]
    feature_probes = [s for s in configure_text.splitlines()
                      if re.search(r"Performing Test|Looking for|Found Threads|pthread", s)]
    diagnostic_lines = [line for line in blocks["hammond_vst3_validator"] if re.search(r"ERROR|Failed to teardown|not supported|No .*interface|no units|no programs|not export|No snapshots|could be better", line)]
    retained = []
    for name in ("provenance.json", "toolchain.log", "sdk-verification.log", "ctest.log", "ctest.xml", "build-inventory.json"):
        retained.append(write_original(BASE / family / (name + ".gz"), raw["native-ci-logs/" + name]))
    retained += [write_original(BASE / family / "archive.sha256.gz", archive_digest),
                 write_original(BASE / family / "moduleinfo.json.gz", moduleinfo)]
    result = {
        "family": family, "observed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source_commit": SOURCE, "source_tree": TREE, "run_id": RUN, "run_attempt": 1,
        "job": job, "provenance": provenance,
        "complete_job_log": {"path": complete_log_path.relative_to(ROOT).as_posix(),
                             "decoded_utf8": identity(complete_log_bytes),
                             "gzip": identity(complete_log_path.read_bytes()),
                             "complete_ctest_lines_equal_diagnostic": True},
        "artifact_metadata": {kind: {"metadata": value["metadata"], "retained_path": value["path"],
                                     "verified_bytes": identity(value["raw"])} for kind, value in archives.items()},
        "sdk": {"lock": identity(lock_bytes), "root_commit": lock["commit"],
                "acquisition": acquisition, "verification": verification,
                "build_selftest_lines_separate_from_module_validator": selftest_lines},
        "toolchain": {"toolchain_log": raw["native-ci-logs/toolchain.log"].decode(),
                      "compiler_identification": compiler_lines, "configure_feature_probes": feature_probes,
                      "sdk_signing_lines": signing_lines},
        "ctest": {"tests": len(cases), "failures": 0, "errors": 0, "skips": 0,
                  "xml_cases": [c.attrib for c in cases], "passing_rows": passing,
                  "timeout_seconds": timeout_records,
                  "total_time_line": next(s for s in ctest.splitlines() if s.startswith("Total Test time"))},
        "validator": {"actual_module_command": command, "passed": 47, "failed": 0,
                      "parameter_count": 47, "class_ids": class_ids,
                      "teardown_diagnostics": validator.count("Failed to teardown test!"),
                      "unsupported_rate_errors": len(re.findall(r"^ERROR:.*samplerate", validator, re.M)),
                      "unsupported_float64_messages": validator.count("64bit Audio Processing not supported."),
                      "diagnostic_lines": diagnostic_lines},
        "abi": abi, "install": install,
        "native_summaries": {name: [s for s in lines if s.startswith(("native-", "native behavior", "native automation:"))]
                             for name, lines in blocks.items() if name not in ("test_native_install", "test_native_abi")},
        "linux_realtime": realtime, "configure_build_diagnostic_lines": warnings,
        "bundle": {"archive": identity(bundle_archive), "inventory": inventory, "native_header": header,
                   "tar_inventory_install_bytes_equal": True, "archive_digest_matches": True,
                   "moduleinfo_policy": "Original opaque SDK metadata retained; no strict-JSON or editor claim."},
        "extracted_originals": retained,
        "scope": "Read-only inspection of observed hosted originals. No local build, test, native execution, install, CI retry, or Git/remote mutation. No DAW, device, signature, accessibility, release, deadline, physical-fidelity, or whole-interface 1:1 acceptance.",
    }
    (BASE / family / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    return {"family": family, "job": job_id, "tests": len(cases), "validator": result["validator"],
            "abi": abi, "module": module, "file_count": len(files), "total_bytes": inventory["total_bytes"],
            "configure_build_diagnostic_lines": warnings}


if __name__ == "__main__":
    metadata = json.loads((BASE / "observed-metadata.json").read_text())
    print(json.dumps([inspect(family, metadata) for family in sys.argv[1:]], indent=2))
