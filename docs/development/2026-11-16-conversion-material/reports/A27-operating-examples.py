#!/usr/bin/env python3
"""Reproduce the operating-guide examples without changing source or build inputs."""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
PAYLOAD = (
    "tools/contact_grid_conversion.py",
    "tools/convert_contact_grid.py",
    "tools/contact_switching_io.py",
    "tools/fractional_contact_reference.py",
    "docs/CONTACT_GRID_CONVERSION_CONTRACT.md",
)
FIXTURES = tuple("data/contact-switching/reference-v1/" + name + "-48000-v1.json"
                 for name in ("F02", "F09"))


def identity(path):
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--probe", type=Path)
    args = parser.parse_args()
    if args.report.exists():
        raise SystemExit("report already exists; use a fresh path")
    watched = {name: identity(ROOT / name) for name in PAYLOAD + FIXTURES}
    result = {
        "schema": "contact-grid-operating-examples-v1",
        "scope": "guide command smoke; not independent numerical or install acceptance",
        "cwd": str(ROOT), "python": platform.python_version(),
        "platform": platform.platform(), "source_inputs": watched,
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "tree": subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip(),
        "runner": identity(Path(__file__)), "runs": [],
    }
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="A27-operating-", dir=ROOT.parent) as temp:
        work = Path(temp)
        result["temporary_root"] = str(work)
        inputs = work / "input"
        inputs.mkdir()
        for name in FIXTURES:
            shutil.copyfile(ROOT / name, inputs / Path(name).name)
        cert = work / "F02-grid-certificate.json"
        script = ROOT / "tools/convert_contact_grid.py"

        def invoke(name, command, cwd, *, stdin=None):
            clock = time.monotonic()
            done = subprocess.run(command, cwd=cwd, input=stdin, capture_output=True,
                                  timeout=60, check=False)
            record = {"name": name, "argv": list(map(str, command)), "cwd": str(cwd),
                      "exit": done.returncode, "elapsed_seconds": time.monotonic() - clock,
                      "stdout_bytes": len(done.stdout), "stderr_bytes": len(done.stderr),
                      "stdout_sha256": hashlib.sha256(done.stdout).hexdigest(),
                      "stderr_sha256": hashlib.sha256(done.stderr).hexdigest()}
            if stdin is not None:
                record["stdin"] = {"bytes": len(stdin), "sha256": hashlib.sha256(stdin).hexdigest()}
            if len(done.stdout) < 8192:
                record["stdout"] = done.stdout.decode("utf-8")
            if len(done.stderr) < 8192:
                record["stderr"] = done.stderr.decode("utf-8")
            result["runs"].append(record)
            return done, record

        done, run = invoke("source-F02", [sys.executable, "-B", str(script), "--input",
            str(inputs / "F02-48000-v1.json"), "--output", str(cert)], ROOT)
        assert done.returncode == 0 and done.stdout == done.stderr == b""
        raw = cert.read_bytes()
        document = json.loads(raw)
        assert document["status"] == "accepted" and document["audio_accuracy"] == "unqualified"
        assert len(document["edges"]) == 18 and len(document["arrivals"]) == 2
        expected_modules = {name: watched[name]["sha256"] for name in PAYLOAD if name.startswith("tools/")}
        assert document["provenance"]["implementation_sha256"] == expected_modules
        assert document["provenance"]["contract_sha256"] == watched[PAYLOAD[-1]]["sha256"]
        assert document["input_sha256"] == watched[FIXTURES[0]]["sha256"]
        assert document["input_bytes"] == watched[FIXTURES[0]]["bytes"]
        run["certificate"] = identity(cert)
        run["summary"] = document["summary"]
        run["counts"] = {name: len(document[name]) for name in
                         ("edges", "arrivals", "commands", "preorder", "position_samples", "root_bounds")}
        run["provenance"] = document["provenance"]
        for field, limit in (("max_position_error", Fraction(1, 2**18)),
                             ("max_root_error", Fraction(1, 2**10))):
            value = document["summary"][field]
            rational = Fraction(int(value["numerator"]), int(value["denominator"]))
            assert rational <= limit
            run[field + "_display_only"] = float(rational)

        refused_output = work / "F09-grid-certificate.json"
        marker = b"A27 previous destination; retain on refusal.\n"
        refused_output.write_bytes(marker)
        prior = identity(refused_output)
        done, run = invoke("source-F09-preserved-destination", [sys.executable, "-B", str(script),
            "--input", str(inputs / "F09-48000-v1.json"), "--output", str(refused_output)], ROOT)
        refusal = json.loads(done.stdout)
        assert done.returncode == 2 and done.stderr == b"" and done.stdout.count(b"\n") == 1
        assert refusal["code"] == "event_order" and refusal["path"] == "preorder[5]"
        assert refusal["witness"]["labels"] == ["C:2", "E:0:4:1:0"]
        assert refused_output.read_bytes() == marker
        run["destination_before"] = prior
        run["destination_after"] = identity(refused_output)
        run["refusal"] = refusal
        run["owned_temporaries_remaining"] = list(map(str, work.glob(".contact-grid-*.tmp")))
        assert run["owned_temporaries_remaining"] == []

        absent = work / "F09-absent-certificate.json"
        done, run = invoke("source-F09-absent-destination", [sys.executable, "-B", str(script),
            "--input", str(inputs / "F09-48000-v1.json"), "--output", str(absent)], ROOT)
        assert done.returncode == 2 and done.stderr == b"" and json.loads(done.stdout) == refusal
        run["destination_exists"] = absent.exists()
        assert not absent.exists()

        package = work / "copy-stage/share/hammond-b3-organ/contact-grid-conversion"
        for name in PAYLOAD:
            target = package / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        moved_prefix = work / "moved-prefix"
        (work / "copy-stage").rename(moved_prefix)
        moved = moved_prefix / "share/hammond-b3-organ/contact-grid-conversion"
        foreign = work / "foreign-cwd"
        foreign.mkdir()
        moved_cert = work / "F02-relocated-certificate.json"
        done, run = invoke("relocated-five-file-layout-F02", [sys.executable, "-B", "-E", "-s", "-S",
            str(moved / "tools/convert_contact_grid.py"), "--input", str(inputs / "F02-48000-v1.json"),
            "--output", str(moved_cert)], foreign)
        assert done.returncode == 0 and done.stdout == done.stderr == b""
        assert moved_cert.read_bytes() == raw
        inventory = {str(p.relative_to(moved)): identity(p) for p in sorted(moved.rglob("*")) if p.is_file()}
        assert inventory == {name: watched[name] for name in PAYLOAD}
        run["method"] = "Manually copied exact five-file layout then renamed prefix; no CMake installation performed by A27."
        run["package_inventory_after"] = inventory
        run["certificate"] = identity(moved_cert)
        run["byte_identical_to_source_certificate"] = True
        run["original_copy_stage_exists"] = (work / "copy-stage").exists()

        if args.probe is not None:
            probe = args.probe.resolve()
            probe_id = identity(probe)
            wire = document["transport"]["text"].encode("ascii")
            assert hashlib.sha256(wire).hexdigest() == document["transport"]["sha256"]
            done, run = invoke("F02-embedded-transport-native-probe", [str(probe)], foreign, stdin=wire)
            native = json.loads(done.stdout)
            assert done.returncode == 0 and done.stderr == b""
            assert native["model_id"] == "causal-contact-grid-v1"
            assert len(native["edges"]) == 18
            assert native["snapshot"]["phase"] == "closed"
            assert native["snapshot"]["cursor_frames"] == 256
            run["probe"] = {"path": str(probe), **probe_id}
            run["observed_summary"] = {"model_id": native["model_id"], "edges": len(native["edges"]),
                "phase": native["snapshot"]["phase"], "frames": native["snapshot"]["cursor_frames"]}
            run["scope"] = "smoke observation only; independent 557-process correspondence remains A21's evidence"
            assert identity(probe) == probe_id
        result["source_inputs_unchanged"] = watched == {name: identity(ROOT / name) for name in PAYLOAD + FIXTURES}
        assert result["source_inputs_unchanged"]
    result["temporary_root_removed"] = not Path(result["temporary_root"]).exists()
    assert result["temporary_root_removed"]
    result["elapsed_seconds"] = time.monotonic() - started
    result["status"] = "passed"
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "processes": len(result["runs"]),
                      "report": str(args.report), "elapsed_seconds": result["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
