#!/usr/bin/env python3
"""Retain one original A32 qualification command and its complete byte streams."""

from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


REPORTS = Path(__file__).resolve().parent
REPO = Path("/workspace/scratch/21cce69f7784/Hammond-B3-Organ")


def main() -> int:
    if len(sys.argv) < 3 or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", sys.argv[1]):
        raise SystemExit("usage: record_command.py step-name command [argument ...]")
    name, command = sys.argv[1], sys.argv[2:]
    output_path = REPORTS / (name + ".stdout.log")
    error_path = REPORTS / (name + ".stderr.log")
    record_path = REPORTS / (name + ".json")
    for path in (output_path, error_path, record_path):
        if path.exists():
            raise SystemExit(f"Refusing to overwrite an original command artifact: {path}")
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    clock = time.monotonic()
    print(f"A32 {name}: starting {command!r}", flush=True)
    with output_path.open("xb") as output, error_path.open("xb") as error:
        result = subprocess.run(command, cwd=REPO, env=environment, stdout=output, stderr=error,
                                check=False)
    record = {
        "schema_version": 1,
        "worker": "A32",
        "cwd": str(REPO),
        "argv": command,
        "started_utc": started,
        "ended_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "elapsed_seconds": time.monotonic() - clock,
        "exit_code": result.returncode,
        "environment_override": {"PYTHONDONTWRITEBYTECODE": "1"},
        "stdout": {"path": output_path.name, "bytes": output_path.stat().st_size,
                   "sha256": hashlib.sha256(output_path.read_bytes()).hexdigest()},
        "stderr": {"path": error_path.name, "bytes": error_path.stat().st_size,
                   "sha256": hashlib.sha256(error_path.read_bytes()).hexdigest()},
    }
    with record_path.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(f"A32 {name}: exit {result.returncode}, {record['elapsed_seconds']:.3f} seconds; "
          f"stdout {record['stdout']['bytes']} bytes, stderr {record['stderr']['bytes']} bytes",
          flush=True)
    for label, path in (("stdout", output_path), ("stderr", error_path)):
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        if lines:
            print(f"{label} last {min(len(lines), 35)} lines:", flush=True)
            print("\n".join(lines[-35:]), flush=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
