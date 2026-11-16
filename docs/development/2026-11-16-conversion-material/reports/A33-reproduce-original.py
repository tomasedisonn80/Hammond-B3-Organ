"""Reproduce the two old test premises, without changing production or snapshots."""
from __future__ import annotations

import argparse
import errno
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import time
import types
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[4]
REPORTS = Path(__file__).resolve().parent


def load_original(stem):
    archive = REPORTS / ("A33-before-" + stem + ".txt")
    module = types.ModuleType("a33_original_" + stem)
    # The retained test's imports still resolve from its original repository path.
    module.__file__ = str(REPO / "tests" / (stem + ".py"))
    exec(compile(archive.read_bytes(), str(archive), "exec"), module.__dict__)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists() or args.log.exists():
        parser.error("report/log must be fresh paths")
    binding = json.loads((REPORTS / "A33-before-bindings.json").read_text())
    for name, value in binding["files"].items():
        if name.startswith("tests/"):
            source = REPORTS / ("A33-before-" + Path(name).stem + ".txt")
        else:
            source = REPO / name
        assert hashlib.sha256(source.read_bytes()).hexdigest() == value["sha256"], name
    cli = load_original("test_contact_grid_conversion_cli")
    adversarial = load_original("test_contact_grid_conversion_adversarial")
    descriptions = []
    log = io.StringIO()
    started = time.monotonic()

    class AliasedParent(cli.ConversionCliTests):
        def setUp(self):
            super().setUp()
            alias = self.root / "parent-alias"
            alias.symlink_to(self.root, target_is_directory=True)
            self.destination = alias / self.destination.name
            assert self.destination.parent != self.destination.parent.resolve(strict=True)

    old_parent = AliasedParent("test_complete_payload_precedes_all_output_io")
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.TestSuite([old_parent]))
    assert result.testsRun == 1 and len(result.failures) == 1 and not result.errors and not result.skipped
    descriptions.append({"case": "real-directory-alias", "tests": 1, "failures": 1,
                         "errors": 0, "kind": "actual local filesystem alias; original assertion fails"})

    real_write = Path.write_bytes

    def encoding_refusal(path, data):
        if any(0xDC80 <= ord(char) <= 0xDCFF for char in str(path)):
            raise OSError(errno.EILSEQ, "injected filesystem encoding rejection", str(path))
        return real_write(path, data)

    old_bytes = adversarial.ProcessPublicationAdversaries(
        "test_valid_input_and_output_accept_non_utf8_posix_path_names")
    with patch.object(Path, "write_bytes", encoding_refusal):
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.TestSuite([old_bytes]))
    assert result.testsRun == 1 and len(result.errors) == 1 and not result.failures and not result.skipped
    descriptions.append({"case": "filesystem-EILSEQ", "tests": 1, "failures": 0,
                         "errors": 1, "kind": "injected exact error family; not a native macOS run"})
    payload = log.getvalue().encode("utf-8")
    args.log.write_bytes(payload)
    report = {"schema": 1, "status": "both-original-premises-reproduced",
              "platform": platform.platform(), "python": sys.version,
              "seconds": time.monotonic() - started, "cases": descriptions,
              "log_sha256": hashlib.sha256(payload).hexdigest(),
              "scope": "Two expected failures of retained original test code. Production unchanged."
                       " Hosted macOS evidence remains the original job log; local injection is not that execution."}
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
