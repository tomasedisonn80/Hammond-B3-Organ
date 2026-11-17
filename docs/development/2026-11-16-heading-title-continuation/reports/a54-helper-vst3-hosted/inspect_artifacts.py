#!/usr/bin/env python3
"""A54 read-only artifact inspection; never loads or executes a native module.

Inputs are eight downloaded, hash-identified ZIPs plus exact workflow metadata.
Outputs are new evidence in this directory. Raw artifact text stays in ZIP/gzip.
"""
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import struct
import subprocess
import tarfile
import xml.etree.ElementTree as ET
import zipfile


BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[4]
SOURCE = "6287055a111dc4e2747564da3d48edc9b65e2e3e"
TREE = "c96fe07c4241f5afe423306945508a114506f0c2"
PARENT = "03c70c103a4a0dd72b323529416b909c19a4e139"
RUN = 44026516616
FAMILIES = {
    "linux": (133848046935, "ubuntu-24.04-X64", "Linux", "X64", "ELF64", "x86_64"),
    "mac_arm": (133848046857, "macos-15-ARM64", "macOS", "ARM64", "Mach-O64", "arm64"),
    "mac_intel": (133848046789, "macos-15-intel-X64", "macOS", "X64", "Mach-O64", "x86_64"),
    "windows": (133848046537, "windows-2022-X64", "Windows", "X64", "PE32+", "x86_64"),
}
COMMON = {"test_native_install", "hammond_vst3_validator", "test_native_controller",
          "test_native_abi", "test_native_behavior", "test_native_automation",
          "test_native_concurrency"}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(raw):
    return {"bytes": len(raw), "sha256": digest(raw)}


def json_line(text):
    objects = [json.loads(line) for line in text.splitlines() if line.startswith("{")]
    assert len(objects) == 1
    return objects[0]


def parse_sdk_moduleinfo(raw):
    # SDK metadata permits trailing commas. Remove only tokens outside strings.
    text = raw.decode("utf-8")
    output, quoted, escaped = [], False, False
    for index, char in enumerate(text):
        if quoted:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
            output.append(char)
        elif char == "," and text[index + 1:].lstrip().startswith(("}", "]")):
            continue
        else:
            output.append(char)
    return json.loads("".join(output))


def inspect_header(raw):
    if raw.startswith(b"\x7fELF"):
        assert raw[4] == 2 and raw[5] == 1
        machine = struct.unpack_from("<H", raw, 18)[0]
        assert struct.unpack_from("<H", raw, 16)[0] == 3
        return {"format": "ELF64", "architecture": {62: "x86_64", 183: "arm64"}[machine],
                "machine_code": machine, "byte_order": "little", "module_type": "ET_DYN"}
    if raw.startswith(b"\xcf\xfa\xed\xfe"):
        cpu = struct.unpack_from("<I", raw, 4)[0]
        kind = struct.unpack_from("<I", raw, 12)[0]
        assert kind in (6, 8)
        return {"format": "Mach-O64", "architecture": {0x01000007: "x86_64", 0x0100000C: "arm64"}[cpu],
                "cpu_type": cpu, "file_type": kind, "byte_order": "little"}
    assert raw.startswith(b"MZ")
    offset = struct.unpack_from("<I", raw, 0x3C)[0]
    assert raw[offset:offset + 4] == b"PE\x00\x00"
    machine = struct.unpack_from("<H", raw, offset + 4)[0]
    assert struct.unpack_from("<H", raw, offset + 24)[0] == 0x20B
    assert struct.unpack_from("<H", raw, offset + 22)[0] & 0x2000
    return {"format": "PE32+", "architecture": {0x8664: "x86_64", 0xAA64: "arm64"}[machine],
            "machine_code": machine, "optional_header_magic": "0x20b", "dll_characteristic": True}


def inspect_family(family, metadata, lock, lock_raw):
    job_id, token, runner_os, runner_arch, expected_format, expected_arch = FAMILIES[family]
    job = next(j for j in metadata["jobs"] if j["id"] == job_id)
    assert job["head_sha"] == SOURCE and job["run_attempt"] == 1
    assert job["status"] == "completed" and job["conclusion"] == "success"
    assert job["runner_id"] and job["runner_name"]
    required_steps = [s for s in job["steps"] if s["name"] in {
        "Record actual source and runner provenance", "Explicitly acquire and verify the locked external SDK",
        "Build the bundle and every native test input", "Validate the actual module and run the native tests",
        "Inventory and archive the validated native bundle",
        "Retain complete source, dependency, build and test diagnostics",
        "Retain the qualified bundle and byte inventory"}]
    assert len(required_steps) == 7 and all(s["conclusion"] == "success" for s in required_steps)
    artifacts = {}
    for kind in ("diagnostics", "bundle"):
        expected_name = f"native-vst3-{token}-release-{kind}-{SOURCE}-1"
        a = next(a for a in metadata["artifacts"] if a["name"] == expected_name)
        raw = (BASE / f'artifact-{a["id"]}.zip').read_bytes()
        assert len(raw) == a["size_in_bytes"] and digest(raw) == a["digest"].split(":")[1]
        assert not a["expired"] and a["workflow_run"]["id"] == RUN
        assert a["workflow_run"]["head_sha"] == SOURCE
        artifacts[kind] = (a, raw)

    with zipfile.ZipFile(io.BytesIO(artifacts["diagnostics"][1])) as diagnostic:
        assert len(diagnostic.namelist()) == len(set(diagnostic.namelist()))
        assert sum(x.file_size for x in diagnostic.infolist()) < 5_000_000
        raw = {name: diagnostic.read(name) for name in diagnostic.namelist()}
    provenance = json.loads(raw["native-ci-logs/provenance.json"])
    assert provenance["source_commit"] == SOURCE and provenance["source_tree"] == TREE
    assert provenance["run_id"] == str(RUN) and provenance["run_attempt"] == "1"
    assert provenance["runner_os"] == runner_os and provenance["runner_arch"] == runner_arch
    assert provenance["configuration"] == "Release"
    assert raw["native-ci-logs/vst3-sdk-lock.json"] == lock_raw
    acquisition = json_line(raw["native-ci-logs/sdk-acquisition.log"].decode())
    verification = json_line(raw["native-ci-logs/sdk-verification.log"].decode())
    expected_checkouts = [{"path": ".", "commit": lock["commit"]}] + [
        {"path": entry["path"], "commit": entry["commit"]} for entry in lock["required_submodules"]]
    for record in (acquisition, verification):
        assert record["verified_checkouts"] == expected_checkouts
        assert record["primary_licenses_verified"] == 5 and record["embedded_json_verified"] is True
    assert acquisition["network_used"] is True and verification["network_used"] is False

    ctest_raw, xml_raw = raw["native-ci-logs/ctest.log"], raw["native-ci-logs/ctest.xml"]
    ctest = ctest_raw.decode()
    suite = ET.fromstring(xml_raw)
    expected_tests = COMMON | ({"test_native_realtime"} if family == "linux" else set())
    cases = suite.findall("testcase")
    assert len(cases) == len(expected_tests) and {c.attrib["name"] for c in cases} == expected_tests
    assert int(suite.attrib["tests"]) == len(cases)
    assert all(int(suite.attrib.get(k, 0)) == 0 for k in ("failures", "disabled", "skipped", "errors"))
    for case in cases:
        assert case.get("status") == "run"
        assert case.find("failure") is None and case.find("skipped") is None and case.find("error") is None
    starts = re.findall(r"(?m)^\s*Start (\d+): (\S+)\s*$", ctest)
    assert {name for _, name in starts} == expected_tests and len(starts) == len(expected_tests)
    blocks = {name: re.findall(r"(?m)^" + number + r": ?(.*)$", ctest) for number, name in starts}
    passing_rows = re.findall(r"(?m)^\s*\d+/\d+ Test #\d+:\s+(\S+).*?Passed\s+([0-9.]+) sec\s*$", ctest)
    assert {name for name, _ in passing_rows} == expected_tests and len(passing_rows) == len(expected_tests)
    # Runner CTest releases print either wording; explicit JUnit zero counts
    # and the complete individual passing rows are required above in both cases.
    assert re.search(r"100% tests passed(?:, 0 tests failed)? out of " + str(len(expected_tests)), ctest)
    validator_lines = blocks["hammond_vst3_validator"]
    validator = "\n".join(validator_lines)
    validator_command = next(line for line in validator_lines if line.startswith("Test command:"))
    assert "validator" in validator_command and "HammondB3.vst3" in validator_command
    assert "* Loading module..." in validator and "name = Hammond B3 Nominal" in validator
    assert re.findall(r"Result: (\d+) tests passed, (\d+) tests failed", validator) == [("47", "0")]
    class_ids = [lock["plugin_class_ids"][name]["fuid_hex"] for name in ("processor", "controller")]
    assert all(cid in validator for cid in class_ids) and validator.count("sdkVersion = VST 3.8.1") == 2
    abi = json_line("\n".join(blocks["test_native_abi"]))
    install = json_line("\n".join(blocks["test_native_install"]))
    assert abi["suite"] == "native-abi-v1" and abi["descriptors"] == 47 and abi["assertions"] == 701642
    assert abi["maximum_audio_error"] == 0 and abi["compared_frames"] == 229725
    assert install["suite"] == "native-install-v1" and install["relocated_abi"] == abi
    install_text = "\n".join(blocks["test_native_install"])
    assert len(re.findall(r"Ran 2 tests in [0-9.]+s", install_text)) == 1
    assert re.search(r"(?m)^OK\s*$", install_text)

    with zipfile.ZipFile(io.BytesIO(artifacts["bundle"][1])) as package:
        assert set(package.namelist()) == {"archive.sha256", "inventory.json", "HammondB3-Release.tar.gz"}
        assert sum(x.file_size for x in package.infolist()) < 2_000_000
        archive = package.read("HammondB3-Release.tar.gz")
        archive_digest = package.read("archive.sha256")
        inventory_raw = package.read("inventory.json")
    assert archive_digest.decode().split() == [digest(archive), "HammondB3-Release.tar.gz"]
    assert inventory_raw == raw["native-ci-logs/build-inventory.json"]
    inventory = json.loads(inventory_raw)
    assert inventory["source"]["revision"] == SOURCE and inventory["configuration"] == "Release"
    assert inventory["sdk_lock"]["sha256"] == digest(lock_raw)
    assert inventory["sdk_lock"]["root_commit"] == lock["commit"]
    files = {entry["path"]: entry for entry in inventory["files"]}
    assert len(files) == inventory["file_count"] == (4 if family == "linux" else 6)
    payload = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        members = tar.getmembers()
        assert len(members) <= 32 and sum(m.size for m in members) < 5_000_000
        for member in members:
            name = PurePosixPath(member.name)
            assert not name.is_absolute() and ".." not in name.parts and name.parts[0] == "HammondB3.vst3"
            assert member.isdir() or member.isfile()
            if member.isfile():
                relative = name.relative_to("HammondB3.vst3").as_posix()
                assert relative in files and relative not in payload
                data = tar.extractfile(member).read()
                record = files[relative]
                assert len(data) == record["bytes"] and digest(data) == record["sha256"]
                assert member.mode == int(record["mode_octal"], 8)
                payload[relative] = data
    assert set(payload) == set(files) and sum(map(len, payload.values())) == inventory["total_bytes"]
    assert install["payload_files"] == len(payload)
    assert install["bundle_sha256"] == {name: digest(data) for name, data in payload.items()}
    module = inventory["module"]
    assert module["format"] == expected_format and module["architectures"] == [expected_arch]
    header = inspect_header(payload[module["path"]])
    assert header["format"] == expected_format and header["architecture"] == expected_arch
    moduleinfo_raw = payload["Contents/Resources/moduleinfo.json"]
    moduleinfo = parse_sdk_moduleinfo(moduleinfo_raw)
    assert len(moduleinfo["Classes"]) == 2 and {c["CID"] for c in moduleinfo["Classes"]} == set(class_ids)
    assert all(c["SDKVersion"] == "VST 3.8.1" for c in moduleinfo["Classes"])
    assert digest(payload["Contents/Resources/VST3_SDK_LICENSE.txt"]) == lock["license"]["sha256"]
    assert payload["Contents/Resources/THIRD_PARTY_NOTICES.md"] == (ROOT / "THIRD_PARTY_NOTICES.md").read_bytes()

    realtime = None
    if family == "linux":
        rt = blocks["test_native_realtime"]
        rows = [line.split() for line in rt if re.match(r"^(enabled|preset|dense|maximum|carry|output-shape|rejected|setProcessing) \d", line)]
        assert len(rows) == 8 and all(len(row) == 11 for row in rows)
        assert all(int(row[7]) == 0 and int(row[8]) == 0 for row in rows)
        assert sum(int(row[1]) + int(row[2]) for row in rows) == 193
        summary = next(line for line in rt if line.startswith("regions="))
        assert "regions=193 overload_calibration=12/12" in summary and "assertions=8945157" in summary
        calibrations = [line for line in rt if line.startswith("module calibration ")]
        assert len(calibrations) == 2 and all("create new=1 delete=0; release new=0 delete=1 refs=0" in line for line in calibrations)
        scope = next(line for line in rt if line.startswith("Scope:"))
        assert scope == "Scope: Linux calling-thread global C++ new/delete; timings are observations, not device deadlines."
        realtime = {"regions": 193, "overload_calibration": "12/12", "assertions": 8945157,
                    "processing_paths_cpp_new_delete_zero": True, "positive_calibration": calibrations,
                    "rows": rows, "summary": summary, "scope": scope,
                    "complete_output": [line for line in rt if not line.startswith(("Test command:", "Working Directory:", "Test timeout"))]}
    old = json.loads((BASE.parent / "a54-vst3-hosted" / family / "validation.json").read_text())
    previous = json.loads((BASE.parent / "a54-repair-vst3-hosted" / family / "validation.json").read_text())
    old_diag_id = old["artifact_ids"]["diagnostics"]
    with zipfile.ZipFile(BASE.parent / "a54-vst3-hosted" / f"artifact-{old_diag_id}.zip") as prior:
        old_ctest = prior.read("native-ci-logs/ctest.log").decode()
    messages = {"teardown_message": "Failed to teardown test!", "unsupported_64_bit_message": "64bit Audio Processing not supported."}
    diagnostic_messages = {key: {"text": phrase, "current_count": validator.count(phrase),
                                 "original_complete_ctest_count": old_ctest.count(phrase)}
                           for key, phrase in messages.items()}
    for key, item in diagnostic_messages.items():
        item["previous_03c70c1_count"] = previous["actual_module_validator"]["diagnostic_messages"][key]["current_count"]
    assert all(item["current_count"] == item["original_complete_ctest_count"] == item["previous_03c70c1_count"] for item in diagnostic_messages.values())
    compiler_lines = [line for line in raw["native-ci-logs/configure.log"].decode().splitlines()
                      if "compiler identification" in line or "Found Python3:" in line]
    elapsed = float(re.search(r"Total Test time \(real\) =\s*([0-9.]+) sec", ctest).group(1))
    report = {
        "family": family, "job": job, "source": SOURCE, "tree": TREE, "provenance": provenance,
        "sdk_lock": identity(lock_raw), "sdk_version": lock["version"], "sdk_tag": lock["tag"],
        "sdk_acquisition": acquisition, "sdk_verification": verification,
        "artifacts": {kind: {"id": a[0]["id"], "name": a[0]["name"], **identity(a[1])} for kind, a in artifacts.items()},
        "ctest_log": identity(ctest_raw), "ctest_xml": identity(xml_raw),
        "ctest_count": len(cases), "ctest_failures": 0, "ctest_skipped": 0, "ctest_disabled": 0,
        "ctest_total_seconds": elapsed,
        "tests": [{"name": c.get("name"), "seconds": float(c.get("time")), "status": c.get("status"),
                   "command": next(line for line in blocks[c.get("name")] if line.startswith("Test command:")),
                   "computed_timeout": next(line for line in blocks[c.get("name")] if line.startswith("Test timeout"))} for c in cases],
        "actual_module_validator": {"passed": 47, "failed": 0, "sdk_version": "3.8.1", "command": validator_command,
                                    "actual_module_loaded": True, "class_ids": class_ids, "not_sdk_selftest_substitution": True,
                                    "diagnostic_messages": diagnostic_messages, "warning_free_claim": False},
        "native_abi": abi, "native_install": install, "install_methods_executed": 2,
        "install_methods": ["test_install_move_and_load", "test_preflight_rejects_incomplete_bundle_without_mutating_prefix"],
        "relocated_abi_equals_direct_abi": True,
        "native_summaries": [line for block in blocks.values() for line in block if line.startswith(("native-controller", "native behavior", "native automation", "native-concurrency"))],
        "linux_realtime": realtime, "compiler_identification": compiler_lines,
        "bundle_inventory": inventory, "bundle_inventory_bytes": identity(inventory_raw),
        "archive": identity(archive), "archive_digest_file": identity(archive_digest),
        "all_archive_payload_bytes_sizes_modes_match_inventory": True,
        "build_and_staged_inventory_bytes_identical": True,
        "independently_parsed_module_header": header, "module_bytes": identity(payload[module["path"]]),
        "moduleinfo": identity(moduleinfo_raw), "moduleinfo_classes": moduleinfo["Classes"],
        "unchanged_from_original_run": {"native_abi_summary": abi == old["native_abi"],
                                       "module_metadata_bytes": identity(moduleinfo_raw) == old["moduleinfo"],
                                       "module_binary_sha256": files[module["path"]]["sha256"] == old["native_install"]["bundle_sha256"][module["path"]],
                                       "validator_diagnostic_message_counts": True},
        "unchanged_from_03c70c1_run": {"native_abi_summary": abi == previous["native_abi"],
                                         "module_metadata_bytes": identity(moduleinfo_raw) == previous["moduleinfo"],
                                         "module_binary_sha256": files[module["path"]]["sha256"] == previous["module_bytes"]["sha256"],
                                         "validator_diagnostic_message_counts": True},
        "scope_limits": ["SDK/native workflow qualification of this exact source only.",
                         "No all-DAW, physical MIDI/audio device, hardware deadline, calibrated instrument, signing/notarization or whole-UI 1:1 claim.",
                         "Complete CTest log, rather than possibly truncated successful JUnit output, supplies validator/install/realtime summaries."]}
    retain = {"bundle-inventory.json.gz": inventory_raw, "moduleinfo.json.gz": moduleinfo_raw,
              "archive.sha256.gz": archive_digest}
    return report, retain


def main():
    metadata = json.loads((BASE / "final-metadata.json").read_text())
    assert metadata["run"]["id"] == RUN and metadata["run"]["head_sha"] == SOURCE
    assert metadata["run"]["run_attempt"] == 1 and metadata["run"]["conclusion"] == "success"
    assert len(metadata["jobs"]) == 4 and len(metadata["artifacts"]) == 8
    assert metadata["source"]["sha"] == SOURCE and metadata["source"]["tree"]["sha"] == TREE
    assert [p["sha"] for p in metadata["source"]["parents"]] == [PARENT]
    lock_raw = (ROOT / "data/dependencies/vst3-sdk-lock.json").read_bytes()
    lock = json.loads(lock_raw)
    assert lock["version"] == "3.8.1" and digest(lock_raw) == "ef3dfdf3feb5747967fe205ba196f5ef1b01457653f6ad7a62fffefd702ba965"
    workflow = (BASE / "source-workflow.txt").read_bytes()
    assert workflow == (ROOT / ".github/workflows/native-vst3.yml").read_bytes()
    assert digest(workflow) == "6bc30e3fcb880d456a5ec4af98e2d2950d5c340285948cd01dc230ba3625d734"
    results = [(family, *inspect_family(family, metadata, lock, lock_raw)) for family in FAMILIES]
    for family, report, retain in results:
        directory = BASE / family
        directory.mkdir(exist_ok=False)
        archives = []
        for name, raw in retain.items():
            compressed = gzip.compress(raw, mtime=0)
            assert gzip.decompress(compressed) == raw and compressed[4:8] == bytes(4) and compressed[3] & 8 == 0
            path = directory / name
            with path.open("xb") as output:
                output.write(compressed)
            archives.append({"path": str(path.relative_to(ROOT)), "stored": identity(compressed), "decoded": identity(raw),
                             "encoding": "gzip", "mtime": 0, "embedded_filename": None})
        report["retained_original_bundle_text"] = archives
        with (directory / "validation.json").open("x") as output:
            json.dump(report, output, indent=2)
            output.write("\n")
    print(json.dumps([{"family": family, "job_id": report["job"]["id"], "tests": report["ctest_count"],
                       "seconds": report["ctest_total_seconds"], "header": report["independently_parsed_module_header"],
                       "validator_passed": report["actual_module_validator"]["passed"],
                       "install_methods": report["install_methods_executed"],
                       "archive": report["archive"], "unchanged_from_original_run": report["unchanged_from_original_run"]}
                      for family, report, _ in results], indent=2))


if __name__ == "__main__":
    main()
