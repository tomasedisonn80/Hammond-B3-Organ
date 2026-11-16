#!/usr/bin/env python3
"""Bounded authoring smoke of the real five-file component in a private project.

This is A23's implementation check, not A30's independent acceptance suite.
No native build or live checkout input is modified. Refuse report replacement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[4]
COMPONENT = "ContactGridConversionTools"
PACKAGE = Path("share/hammond-b3-organ/contact-grid-conversion")
PAYLOAD = (
    "tools/contact_grid_conversion.py", "tools/convert_contact_grid.py",
    "tools/contact_switching_io.py", "tools/fractional_contact_reference.py",
    "docs/CONTACT_GRID_CONVERSION_CONTRACT.md",
)
INSTALLERS = (
    "cmake/InstallHammondTools.cmake",
    "cmake/InstallContactGridConversionTools.cmake",
)
ORIGINAL_TOOLS = (
    "fractional_contact_reference.py", "contact_switching_io.py",
    "contact_switching_reference.py", "contact_switching_oracle.py",
    "contact_switching_study.py", "make_contact_switching_fixtures.py",
)
ORIGINAL_DOCS = (
    "FRACTIONAL_CONTACT_REFERENCE.md", "CONTACT_SWITCHING_VALIDATION.md",
    "CONTACT_SWITCHING_GUIDE.md", "CONTACT_REFERENCE_INSTALL.md",
)
ORIGINAL_PAYLOAD = (
    *("tools/" + name for name in ORIGINAL_TOOLS),
    *("docs/" + name for name in ORIGINAL_DOCS),
    *(f"data/contact-switching/reference-v1/F{recipe:02d}-{rate}-v1.json"
      for recipe in range(12) for rate in (44100, 48000, 96000)),
    "data/contact-switching/reference-v1/manifest.json",
    "data/contact-switching/reference-v1/probes.json",
)
BASE = "a411268fd498f65c083203137831bf5afed83bd8"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def environment():
    value = dict(os.environ)
    for name in tuple(value):
        if (name.startswith(("HAMMOND_", "CMAKE_GENERATOR"))
                or name in ("CMAKE_INSTALL_MODE", "DESTDIR", "PYTHONPATH", "PYTHONHOME")):
            value.pop(name)
    value["PYTHONDONTWRITEBYTECODE"] = "1"
    return value


def inventory(directory):
    if not directory.exists():
        return None
    result = {}
    for path in sorted(directory.rglob("*")):
        key = path.relative_to(directory).as_posix()
        if path.is_symlink():
            result[key] = {"kind": "link", "target": os.readlink(path)}
        elif path.is_dir():
            result[key] = {"kind": "directory"}
        else:
            result[key] = {"kind": "file", "bytes": path.stat().st_size,
                           "sha256": sha(path.read_bytes()),
                           "mode": stat.S_IMODE(path.stat().st_mode)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    options = parser.parse_args()
    if options.report.exists():
        raise SystemExit("Report already exists; use a fresh path")
    cmake = shutil.which("cmake")
    if not cmake:
        raise SystemExit("CMake 3.21+ is required")
    originals = {name: (ROOT / name).read_bytes() for name in PAYLOAD}
    watched = {name: sha((ROOT / name).read_bytes())
               for name in (*PAYLOAD, *INSTALLERS,
                            "cmake/InstallContactReferenceTools.cmake", *ORIGINAL_PAYLOAD)}
    original_bindings = {}
    for name in (*ORIGINAL_PAYLOAD, "cmake/InstallContactReferenceTools.cmake"):
        old = subprocess.check_output(["git", "show", BASE + ":" + name], cwd=ROOT)
        assert sha(old) == watched[name], "Original reference input changed: " + name
        original_bindings[name] = watched[name]
    report = {"schema_version": 1, "scope": "private authoring installation smoke",
              "component": COMPONENT, "package": PACKAGE.as_posix(),
              "base_commit": BASE, "python": platform.python_version(),
              "platform": platform.platform(), "source_sha256": watched,
              "original_reference_payload_count": len(ORIGINAL_PAYLOAD),
              "original_reference_sha256": original_bindings, "commands": [], "checks": []}
    started = time.monotonic()

    def run(label, command, cwd, *, env=None, expected=0):
        before = time.monotonic()
        result = subprocess.run(list(map(str, command)), cwd=cwd,
                                env=environment() if env is None else env,
                                capture_output=True, timeout=45)
        report["commands"].append({"label": label, "command": list(map(str, command)),
                                   "cwd": str(cwd), "exit_code": result.returncode,
                                   "seconds": time.monotonic() - before,
                                   "stdout": result.stdout.decode("utf-8", "replace")[:16384],
                                   "stderr": result.stderr.decode("utf-8", "replace")[:16384]})
        assert (result.returncode == 0) if expected == 0 else (result.returncode != 0), label
        return result

    try:
        with tempfile.TemporaryDirectory(prefix="a23-contact-grid-install-") as raw:
            temporary = Path(raw)
            source, build = temporary / "private-source", temporary / "private-build"
            for name in (*PAYLOAD, *INSTALLERS):
                target = source / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            (source / "tools/unlisted.py").write_bytes(b"must not be installed\n")
            (source / "sentinel.txt").write_bytes(b"ordinary install remains independent\n")
            (source / "CMakeLists.txt").write_text(
                'cmake_minimum_required(VERSION 3.21)\n'
                'project(A23ConversionInstall LANGUAGES NONE)\n'
                'include(cmake/InstallHammondTools.cmake)\n'
                'include(cmake/InstallContactGridConversionTools.cmake)\n'
                'install(FILES sentinel.txt DESTINATION ordinary COMPONENT Sentinel)\n',
                encoding="utf-8")
            run("configure-private-no-language-project", [cmake, "-S", source, "-B", build,
                                                          "-Wno-dev"], temporary)

            def install(label, prefix, *, selected=COMPONENT, env=None, expected=0):
                command = [cmake, "--install", build, "--prefix", prefix, "--config", "Release"]
                if selected is not None:
                    command += ["--component", selected]
                return run(label, command, temporary, env=env, expected=expected)

            # Every required input is checked before either a fresh prefix or an
            # unrelated existing prefix can be changed. All mutations are private.
            for index, name in enumerate(PAYLOAD):
                item = source / name
                held = item.with_suffix(item.suffix + ".held")
                item.rename(held)
                try:
                    for existing in (False, True):
                        prefix = temporary / f"missing-{index}-{existing}"
                        if existing:
                            prefix.mkdir()
                            (prefix / "keep.txt").write_bytes(b"retain\n")
                        before = inventory(prefix)
                        failure = install(f"missing-{name}-{existing}", prefix, expected=1)
                        assert COMPONENT.encode() in failure.stderr
                        assert Path(name).name.encode() in failure.stderr
                        assert inventory(prefix) == before
                    if index == 0:
                        prefix = temporary / "default-with-missing-converter"
                        install("ordinary-install-excludes-converter-preflight", prefix, selected=None)
                        assert (prefix / "ordinary/sentinel.txt").read_bytes() == b"ordinary install remains independent\n"
                        assert not (prefix / PACKAGE).exists()
                        install("unknown-component-is-no-op", temporary / "unknown", selected="Unknown")
                        assert not (temporary / "unknown").exists()
                finally:
                    held.rename(item)
            report["checks"].append("All five missing inputs preserve absent/existing prefixes; default/unknown component isolation")

            mode_prefix = temporary / "noncopy-must-remain-absent"
            env = environment()
            env["CMAKE_INSTALL_MODE"] = "SYMLINK"
            install("noncopy-mode-refused", mode_prefix, env=env, expected=1)
            assert not mode_prefix.exists()

            linked_leaf = source / PAYLOAD[0]
            held = linked_leaf.with_suffix(".held")
            linked_leaf.rename(held)
            try:
                linked_leaf.symlink_to(held)
                prefix = temporary / "linked-source-must-remain-absent"
                install("source-leaf-link-refused", prefix, expected=1)
                assert not prefix.exists()
            finally:
                linked_leaf.unlink()
                held.rename(linked_leaf)

            outside = temporary / "outside-destination"
            outside.mkdir()
            (outside / "keep.txt").write_bytes(b"outside remains unchanged\n")
            before = inventory(outside)
            linked_prefix = temporary / "linked-prefix"
            linked_prefix.symlink_to(outside, target_is_directory=True)
            install("linked-prefix-refused", linked_prefix, expected=1)
            assert inventory(outside) == before
            report["checks"].append("Noncopy mode and representative source/destination links refuse before writes")

            prefix = temporary / "prefix with spaces-é"
            install("explicit-five-file-install", prefix)
            package = prefix / PACKAGE
            files = {p.relative_to(package).as_posix(): p for p in package.rglob("*") if p.is_file()}
            assert set(files) == set(PAYLOAD)
            for name, path in files.items():
                assert not path.is_symlink() and path.read_bytes() == originals[name]
                assert not os.path.samefile(path, source / name)
                if os.name != "nt":
                    assert stat.S_IMODE(path.stat().st_mode) == 0o644
            report["installed_payload"] = inventory(package)
            before = inventory(prefix)
            install("existing-package-refused", prefix, expected=1)
            assert inventory(prefix) == before
            report["checks"].append("Exactly five nonaliasing byte-identical copied files; existing package preserved")

            foreign = temporary / "foreign-working-directory"
            foreign.mkdir()
            fixture = foreign / "F02-48000-v1.json"
            fixture.write_bytes((ROOT / "data/contact-switching/reference-v1/F02-48000-v1.json").read_bytes())
            for name in PAYLOAD[:4]:
                (foreign / Path(name).name).write_bytes(b'raise AssertionError("wrong import root")\n')
            relocated = temporary / "relocated prefix-é音"
            prefix.rename(relocated)
            moved_package = relocated / PACKAGE
            shutil.rmtree(source)
            shutil.rmtree(build)
            before = inventory(relocated)
            output = foreign / "accepted-certificate.json"
            result = run("relocated-installed-converter-with-source-build-removed",
                         [sys.executable, "-B", "-E", "-s", "-S",
                          moved_package / "tools/convert_contact_grid.py",
                          "--input", fixture, "--output", output], foreign)
            assert result.stdout == result.stderr == b""
            certificate = json.loads(output.read_bytes())
            assert certificate["status"] == "accepted"
            assert certificate["conversion_id"] == "fractional-to-contact-grid-rne-v1"
            assert certificate["fixture_id"] == "F02-48000-v1"
            assert certificate["input_sha256"] == sha(fixture.read_bytes())
            assert certificate["input_bytes"] == fixture.stat().st_size
            assert certificate["grid_case"]["sample_rate_hz"] == 48000
            assert certificate["grid_case"]["frames"] == 256
            assert certificate["provenance"]["implementation_sha256"] == {
                name: sha(originals[name]) for name in PAYLOAD[:4]}
            assert certificate["provenance"]["contract_sha256"] == sha(originals[PAYLOAD[4]])
            assert certificate["provenance"]["python_version"] == platform.python_version()
            assert inventory(relocated) == before
            assert not source.exists() and not build.exists() and not prefix.exists()
            report["relocated_smoke"] = {
                "certificate_bytes": output.stat().st_size,
                "certificate_sha256": sha(output.read_bytes()),
                "fixture_sha256": sha(fixture.read_bytes()),
                "edges": len(certificate["edges"]), "arrivals": len(certificate["arrivals"]),
                "source_and_build_removed": True, "installed_package_unchanged": True,
                "bytecode_files_present": False,
            }
            report["checks"].append("Relocated converter runs with private source/build removed and hostile-named cwd modules; all five provenance hashes match")
        report["status"] = "passed"
    except Exception as error:
        report["status"] = "failed"
        report["error"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        report["elapsed_seconds"] = time.monotonic() - started
        after = {name: sha((ROOT / name).read_bytes()) for name in watched}
        report["watched_sources_unchanged"] = after == watched
        report["changed_sources"] = [name for name in watched if after[name] != watched[name]]
        report["script_sha256"] = sha(Path(__file__).read_bytes())
        options.report.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    assert report["watched_sources_unchanged"]
    print(json.dumps({"status": report["status"], "commands": len(report["commands"]),
                      "checks": len(report["checks"]), "elapsed_seconds": report["elapsed_seconds"],
                      "watched_sources_unchanged": report["watched_sources_unchanged"]}))


if __name__ == "__main__":
    main()
