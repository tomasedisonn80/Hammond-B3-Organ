"""Check the repaired test's capability boundary; this is not a native macOS run."""
from __future__ import annotations

import argparse
import errno
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import platform
import subprocess
import time
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[4]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        parser.error("report must be a fresh path")
    path = REPO / "tests/test_contact_grid_conversion_adversarial.py"
    spec = importlib.util.spec_from_file_location("a33_repaired_adversaries", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    real_write = Path.write_bytes
    records = []
    start = time.monotonic()
    for leaf in ("input-\udcff.json", "certificate-\udcfe.json"):
        for code in (errno.EILSEQ, errno.EACCES, errno.ENOSPC, errno.EIO, errno.EINVAL):
            injected = []

            def fail_selected(selected_path, payload):
                if selected_path.name == leaf:
                    injected.append(str(selected_path))
                    raise OSError(code, "injected fixture preparation error", str(selected_path))
                return real_write(selected_path, payload)

            case = module.ProcessPublicationAdversaries(
                "test_valid_input_and_output_accept_non_utf8_posix_path_names")
            with patch.object(Path, "write_bytes", fail_selected), patch.object(subprocess, "run") as run:
                result = unittest.TestResult()
                case.run(result)
                run.assert_not_called()
            assert result.testsRun == 1 and len(injected) == 1 and not result.failures
            if code == errno.EILSEQ:
                assert len(result.skipped) == 1 and not result.errors
                outcome = "capability-skip"
                diagnostic = result.skipped[0][1]
            else:
                assert len(result.errors) == 1 and not result.skipped
                outcome = "test-error-retained"
                diagnostic = result.errors[0][1].splitlines()[-1]
            records.append({"leaf": leaf, "errno": code, "name": errno.errorcode[code],
                            "outcome": outcome, "subprocess_calls": 0,
                            "diagnostic": diagnostic})
    report = {"schema": 1, "status": "passed", "platform": platform.platform(),
              "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "cases": records, "seconds": time.monotonic() - start,
              "counts": {"cases": len(records), "capability_skips": 2, "other_errors_retained": 8},
              "scope": "Injected preparation errno checks only; no CLI child is launched and no suite is skipped."
                       " Full repaired suites and real Unicode/alias journeys are separate local runs."}
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "cases"}, indent=2))


if __name__ == "__main__":
    main()
