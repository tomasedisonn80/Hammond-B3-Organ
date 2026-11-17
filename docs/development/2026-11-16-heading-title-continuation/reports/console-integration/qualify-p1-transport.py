#!/usr/bin/env python3
"""Once-only, bounded before/after observation for the reviewed P1 fixture repair.

This is transport equivalence evidence, not a new paired historical P1 admission.
Use the existing comparator Runner and parser without changing their limits.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def identity(path):
    data = path.read_bytes()
    return dict(path=str(path), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--phase", required=True, choices=("before", "after"))
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--comparator", required=True, type=Path)
    parser.add_argument("--fixture", required=True, type=Path)
    args = parser.parse_args()
    output = Path(__file__).resolve().parent / ("p1-" + args.phase + "-transport")
    output.mkdir(exist_ok=False)
    module_spec = importlib.util.spec_from_file_location("p1_transport_comparator", args.comparator)
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = module
    module_spec.loader.exec_module(module)
    inputs = {"binary": identity(args.exe), "fixture": identity(args.fixture),
              "comparator": identity(args.comparator)}
    for path in ("apps/standalone/InstrumentView.cpp", "apps/standalone/UiModel.cpp",
                 "apps/standalone/UiModel.h", "apps/standalone/Drawing.cpp",
                 "apps/standalone/main.cpp"):
        inputs[path] = identity(args.repo / path)
    store = module.ArtifactStore(output)
    runner = module.Runner(store, 60, 1200)
    report = dict(schema=1, phase=args.phase, inputs=inputs,
                  scope="Transport, complete frozen inventory, and canonical stream equivalence only; existing CTests cover native and numerical acceptance.",
                  timeout_seconds=60, whole_run_seconds=1200, retry=False,
                  commands=runner.commands, passed=False)
    try:
        record, inventory = runner.command(args.exe, ["--list"], "inventory", module.MAX_HEADER)
        assert record["exit_code"] == 0 and not record["errors"], record
        module.validate_inventory(inventory, module.scenarios())
        record, payload = runner.command(args.exe, ["--case", "0"], "canonical", module.MAX_STREAM)
        assert record["exit_code"] == 0 and not record["errors"], record
        header, rgba = module.parse_frame(payload, 0)
        split = payload.index(b"\n") + 1
        report["canonical"] = dict(width=header["width"], height=header["height"],
            stream_bytes=len(payload), stream_sha256=module.sha(payload),
            header_bytes=split, header_sha256=module.sha(payload[:split]),
            rgba_bytes=len(rgba), rgba_sha256=module.sha(rgba))
        report["inventory_sha256"] = module.sha(inventory)
        report["complete_inventory_matches_frozen_34_cases"] = True
        if args.phase == "after":
            previous = json.loads((output.parent / "p1-before-transport" / "report.json").read_text())
            assert previous["passed"]
            assert previous["canonical"] == report["canonical"]
            assert previous["inventory_sha256"] == report["inventory_sha256"]
            for path in inputs.keys() - {"binary", "fixture", "comparator"}:
                assert inputs[path] == previous["inputs"][path]
            report["before_after_complete_canonical_stream_and_inventory_identical"] = True
        report["passed"] = True
    finally:
        report["inputs_unchanged"] = all(identity(Path(item["path"])) == item for item in inputs.values())
        if not report["inputs_unchanged"]:
            report["passed"] = False
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ("phase", "passed", "inputs_unchanged", "canonical")}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
