#!/usr/bin/env python3
"""Bounded A44 installed-flow observation; copies/removes only its private inputs.

Replays the actual generated root installer with only source/build root
substitutions, as test_registration_install.py does. No configure, build, CTest,
SDK, product mutation, or genuine-input removal is performed.
"""

import argparse
from array import array
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import time
import traceback
import wave


STEMS = (
    "01 Quiet Foundation", "02 Warm Comp", "03 Clear Lead", "04 Reed Edge",
    "05 Bright Ensemble", "06 High Shimmer", "07 Percussive Pair", "08 Slow Accent",
    "09 Split Dialogue", "10 Pedal Study", "11 Fixed Contrast", "12 Manual Return",
)
BINARIES = ("hammond_render", "hammond_model_info", "hammond_parameter_info",
            "hammond_console_trace", "hammond_pedal_trace", "hammond_registration")
FIXTURES = (
    "catalog-v1.json", "a4-fundamental-v1.events", "two-manual-changes-v1.events",
    "low-fold-coherent-v1.events", "held-bank-cancel-v1.events", "high-fold-coherent-v1.events",
    "console/console-catalog-v1.json", "console/console-travel-v1.events",
    "console/console-percussion-legato-v1.events", "console/console-routing-mask-v1.events",
    "pedals/pedal-catalog-v1.json", "pedals/pedal-mixtures-v1.events",
    "pedals/pedal-shared-source-v1.events", "pedals/pedal-held-routing-v1.events",
    "pedals/pedal-phrase-v1.events",
)
SCORE = b"""0 note_on upper 60 100
0 note_on lower 48 100
0 pedal_on lower 1 100
8000 select_preset upper 0 8
18000 select_bank upper 0 0
18000 select_bank lower 0 0
30000 select_bank upper 0 1
30000 select_bank lower 0 1
40000 note_off upper 60 0
40000 note_off lower 48 0
40000 pedal_off lower 1 0
"""


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    mode = path.lstat().st_mode
    assert stat.S_ISREG(mode), f"Expected ordinary file: {path}"
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": sha(data), "mode": oct(stat.S_IMODE(mode))}


def inventory(root):
    result = {}
    for path in sorted([root, *root.rglob("*")]):
        mode = path.lstat().st_mode
        relative = path.relative_to(root).as_posix()
        if stat.S_ISDIR(mode):
            result[relative] = {"type": "directory", "mode": oct(stat.S_IMODE(mode))}
        else:
            result[relative] = {"type": "file", **identity(path)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--report-stem", default="a44-installed-flow")
    args = parser.parse_args()
    repo, work = args.repo.resolve(), args.work.resolve()
    assert work.parent == repo.parent and work.name.startswith("a44-"), work
    assert args.report_stem.startswith("a44-") and Path(args.report_stem).name == args.report_stem
    reports = repo / "docs/development/2026-11-16-preset-library-continuation/reports"
    receipt_file = reports / (args.report_stem + ".json")
    archive_file = reports / (args.report_stem + "-originals.tar.gz")
    assert not receipt_file.exists() and not archive_file.exists()
    work.mkdir()  # Deliberately refuse to reuse or clean an existing fixture.
    build = repo.parent / "build-native"
    source_copy, build_copy = work / "source", work / "build"
    original_prefix = work / "initial-prefix"
    relocated = work / "installed/package é音"
    foreign = work / "work/use é音"
    foreign.mkdir(parents=True)
    native_env = {"PATH": "", "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC"}
    install_env = {key: value for key, value in os.environ.items()
                   if not key.upper().startswith(("HAMMOND_", "CMAKE_GENERATOR"))}
    for key in ("DESTDIR", "CMAKE_INSTALL_MODE", "PYTHONPATH", "PYTHONHOME"):
        install_env.pop(key, None)
    logs, commands = {}, []
    receipt = {"schema": "a44-installed-registration-render-v1", "outcome": "running",
               "agent": "/root/w08_a44", "wave": 8,
               "started_at_utc": datetime.now(timezone.utc).isoformat(),
               "repo": str(repo), "genuine_build": str(build), "private_root": str(work),
               "relocated_prefix": str(relocated), "execution_cwd": str(foreign),
               "native_environment": native_env,
               "platform": platform.platform(), "python": sys.version,
               "harness_sha256": sha(Path(__file__).read_bytes()),
               "commands": commands,
               "boundary": "Only private copied installer source/build inputs are removed. "
               "Genuine checkout, build, dependencies and system runtime remain accessible. "
               "This is compatible Linux execution, not cross-host isolation or physical/UI acceptance."}

    def run(label, argv, *, cwd=foreign, env=install_env):
        start = time.monotonic()
        result = subprocess.run(list(map(str, argv)), cwd=cwd, env=env,
                                capture_output=True, check=False, timeout=45)
        base = f"commands/{len(commands):02d}-{label}"
        logs[base + ".stdout"] = result.stdout
        logs[base + ".stderr"] = result.stderr
        commands.append({"label": label, "argv": list(map(str, argv)), "cwd": str(cwd),
                         "environment": "minimal-native" if env is native_env else "install-sanitized",
                         "exit": result.returncode, "seconds": time.monotonic() - start,
                         "stdout_sha256": sha(result.stdout), "stderr_sha256": sha(result.stderr),
                         "stdout_member": base + ".stdout", "stderr_member": base + ".stderr"})
        assert result.returncode == 0, (label, result.returncode,
                                        result.stderr.decode("utf-8", "replace"))
        return result.stdout

    try:
        receipt["head"] = run("head", ["git", "rev-parse", "HEAD"], cwd=repo).decode().strip()
        receipt["head_tree"] = run("head-tree", ["git", "rev-parse", "HEAD^{tree}"], cwd=repo).decode().strip()
        receipt["pending_tracked_paths"] = run("pending", ["git", "diff", "--name-only"], cwd=repo).decode().splitlines()
        cmake = Path(shutil.which("cmake"))
        receipt["cmake"] = run("cmake-version", [cmake, "--version"]).decode().splitlines()[0]
        compiler = next((build / "CMakeFiles").glob("*/CMakeCXXCompiler.cmake"))
        compiler_text = compiler.read_text()
        receipt["genuine_configuration"] = {
            "build_type": "Release", "generator": "Ninja",
            "compiler_id": re.search(r'set\(CMAKE_CXX_COMPILER_ID "([^"]+)"', compiler_text)[1],
            "compiler_version": re.search(r'set\(CMAKE_CXX_COMPILER_VERSION "([^"]+)"', compiler_text)[1],
            "CMakeCache": identity(build / "CMakeCache.txt"),
            "compiler_record": identity(compiler)}
        expected, genuine_inputs = {}, {}

        def copy(original, destination, installed=None):
            original_id = identity(original)
            genuine_inputs[str(original)] = original_id
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, destination)
            assert identity(destination) == original_id
            if installed is not None:
                expected[installed] = {"source": str(original), **original_id}

        for name in BINARIES:
            copy(build / name, build_copy / name, "bin/" + name)
        copy(build / "nominal.b3p", build_copy / "nominal.b3p",
             "share/hammond-b3-organ/nominal.b3p")
        for name in ("plot_console_trace.py", "plot_pedal_trace.py"):
            copy(repo / "tools" / name, source_copy / "tools" / name, "bin/" + name)
        for name in FIXTURES:
            copy(repo / "examples/fixtures" / name, source_copy / "examples/fixtures" / name,
                 "share/hammond-b3-organ/fixtures/" + name)
        copy(repo / "docs/REGISTRATION_GUIDE.md", source_copy / "docs/REGISTRATION_GUIDE.md",
             "share/hammond/REGISTRATION_GUIDE.md")
        pack_relative = Path("data/registrations/starter-v1")
        pack_files = ["entries/" + stem + suffix for stem in STEMS
                      for suffix in (".b3registration", ".b3performance")]
        pack_files += ["README.md", "recipes.json"]
        for name in pack_files:
            copy(repo / pack_relative / name, source_copy / pack_relative / name,
                 "share/hammond/registrations/starter-v1/" + name)
        for name in ("InstallHammondTools.cmake", "InstallRegistrationTools.cmake"):
            copy(repo / "cmake" / name, source_copy / "cmake" / name)
        original_script = (build / "cmake_install.cmake").read_bytes()
        genuine_inputs[str(build / "cmake_install.cmake")] = identity(build / "cmake_install.cmake")
        script = original_script.decode().replace(str(build), str(build_copy)).replace(str(repo), str(source_copy))
        assert str(repo) not in script and str(build) not in script
        private_script = build_copy / "cmake_install.cmake"
        private_script.write_text(script, encoding="utf-8")
        logs["installer/genuine-root-cmake_install.cmake"] = original_script
        logs["installer/private-root-cmake_install.cmake"] = private_script.read_bytes()
        receipt["installer"] = {"method": "generated root script; only source/build root substitutions",
                                "original": identity(build / "cmake_install.cmake"),
                                "private": identity(private_script), "CMAKE_INSTALL_LOCAL_ONLY": 1,
                                "configure_calls": 0, "build_calls": 0}
        source_paths = ("tools/registration.cpp", "tools/render.cpp", "tools/ControlFileInput.cpp",
                        "tools/ControlFileInput.h", "apps/standalone/RegistrationLibrary.cpp",
                        "apps/standalone/RegistrationLibrary.h", "src/ControlStateIO.cpp",
                        "src/ControlState.cpp", "src/Engine.cpp", "src/FixedRegistration.cpp")
        for relative in source_paths:
            genuine_inputs[str(repo / relative)] = identity(repo / relative)
        receipt["genuine_inputs_before"] = genuine_inputs
        receipt["expected_installed_files"] = expected
        assert len(expected) == 51
        for component in ("OfflineTools", "RegistrationTools", "StarterRegistrations"):
            run("install-" + component,
                [cmake, f"-DCMAKE_INSTALL_PREFIX={original_prefix}",
                 f"-DCMAKE_INSTALL_COMPONENT={component}", "-DCMAKE_INSTALL_CONFIG_NAME=Release",
                 "-DCMAKE_INSTALL_LOCAL_ONLY=1", "-P", private_script])

        def check_package(prefix):
            items = inventory(prefix)
            files = {name: entry for name, entry in items.items() if entry["type"] == "file"}
            assert set(files) == set(expected), (set(files) - set(expected), set(expected) - set(files))
            directories = {"."}
            for name in expected:
                directories.update(p.as_posix() for p in Path(name).parents)
                assert files[name]["sha256"] == expected[name]["sha256"], name
                assert files[name]["bytes"] == expected[name]["bytes"], name
            assert {name for name, item in items.items() if item["type"] == "directory"} == directories
            return items

        before = check_package(original_prefix)
        relocated.parent.mkdir()
        original_prefix.rename(relocated)
        assert check_package(relocated) == before
        for private in (source_copy, build_copy):
            assert private.parent == work and not private.is_symlink()
            shutil.rmtree(private)
        assert not any(p.exists() for p in (source_copy, build_copy, original_prefix))
        receipt["private_removal_before_native_use"] = {
            "removed": [str(source_copy), str(build_copy)],
            "old_prefix_absent": True, "genuine_checkout_accessible": repo.is_dir(),
            "genuine_build_accessible": build.is_dir()}
        receipt["installed_inventory_before_use"] = before
        assert list(foreign.iterdir()) == []
        tool = relocated / "bin/hammond_registration"
        renderer = relocated / "bin/hammond_render"
        pack = relocated / "share/hammond/registrations/starter-v1/entries"
        profile = relocated / "share/hammond-b3-organ/nominal.b3p"

        def cli(label, *arguments):
            raw = run(label, [tool, *arguments], env=native_env)
            assert raw.count(b"\n") == 1
            result = json.loads(raw)
            assert result["schema"] == "hammond-registration-cli-v1" and result["outcome"] == "ok"
            assert commands[-1]["stderr_sha256"] == sha(b"")
            return result

        catalog = cli("installed-list", "list", "--library", pack)
        assert catalog["catalog"]["complete"]
        assert {item["key"] for item in catalog["catalog"]["entries"]} == set(Path(p).name for p in pack_files[:24])
        assert list(foreign.iterdir()) == []
        inputs, controls, audio = foreign / "inputs", foreign / "controls", foreign / "audio"
        inputs.mkdir()
        audio.mkdir()
        current = inputs / "current.b3controls"
        current_bytes, count = re.subn(rb"(?m)^expression [^\n]+$", b"expression 0.25",
                                       (pack / "01 Quiet Foundation.b3performance").read_bytes())
        assert count == 1
        current.write_bytes(current_bytes)
        score = inputs / "phrase.events"
        score.write_bytes(SCORE)
        results, render_reports = {}, {}
        for scope in ("registration", "performance"):
            key = "12 Manual Return.b3" + scope
            original = (pack / key).read_bytes()
            inspected = cli("inspect-" + scope, "inspect", "--library", pack, "--key", key)
            assert inspected["entry"]["scope"] == scope
            assert inspected["entry"]["canonical_controls"].encode("ascii") == original
            argv = ["materialize", "--library", pack, "--key", key,
                    "--destination", controls, "--name", "Prepared " + scope]
            if scope == "registration":
                argv += ["--current", current]
            materialized = cli("materialize-" + scope, *argv)
            assert materialized["committed"] is True and materialized["save"]["scope"] == "performance"
            prepared = controls / ("Prepared " + scope + ".b3performance")
            actual = prepared.read_bytes()
            expected_controls = re.sub(rb"(?m)^expression [^\n]+$", b"expression 0.25", original) if scope == "registration" else original
            assert actual == expected_controls
            no_expression = lambda data: re.sub(rb"(?m)^expression [^\n]+\n", b"", data)
            assert no_expression(actual) == no_expression(original)
            assert no_expression(actual) != no_expression(current_bytes)
            expression = re.search(rb"(?m)^expression ([^\n]+)$", actual)[1].decode()
            assert expression == ("0.25" if scope == "registration" else "0.5")
            output = audio / (scope + ".wav")
            raw = run("render-" + scope, [renderer, "--profile", profile, "--controls", prepared,
                      "--events", score, "--output", output, "--sample-rate", "48000", "--frames", "48000",
                      "--block-size", "64", "--seed", "44", "--contacts", "ideal", "--fail-on-clip"], env=native_env)
            render = json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
            assert commands[-1]["stderr_sha256"] == sha(b"")
            assert render["status"] == "ok" and render["render_schema_version"] == 6
            assert render["evidence_status"] == "unmeasured"
            assert render["sample_rate"] == render["frames"] == 48000 and render["block_size"] == 64
            assert render["seed"] == 44 and render["channels"] == 2 and render["sample_format"] == "pcm_s16le"
            assert render["clipped_frames"] == render["clipped_channel_samples"] == 0
            assert all(math.isfinite(render[key]) and 0 < render[key] < 1 for key in ("peak", "rms"))
            assert render["controls"] == {"schema_version": 1,
                "restore_policy": "full-state-including-expression", "path": str(prepared),
                "source_version": 4, "source_bytes": len(actual), "canonical_b3controls4": actual.decode("ascii")}
            fixture_catalog = json.loads((relocated / "share/hammond-b3-organ/fixtures/catalog-v1.json").read_bytes())
            assert render["profile_id"] == fixture_catalog["profile"]["id"]
            assert render["authoring_sha256"] == fixture_catalog["profile"]["authoring_sha256"]
            assert sha(profile.read_bytes()) == fixture_catalog["profile"]["compiled_sha256"]
            with wave.open(str(output), "rb") as wav:
                assert (wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getnframes(), wav.getcomptype()) == (2, 2, 48000, 48000, "NONE")
                pcm_bytes = wav.readframes(48001)
            assert len(pcm_bytes) == 192000 and output.stat().st_size == 192044
            pcm = array("h", pcm_bytes)
            if sys.byteorder != "little":
                pcm.byteswap()
            assert pcm[::2] == pcm[1::2] and any(pcm)
            assert all(math.isfinite(value) and -32768 < value < 32767 for value in pcm)
            results[scope] = {"expression": expression, "all_other_control_bytes_exact": True,
                "prepared": identity(prepared), "wav": identity(output), "pcm_sha256": sha(pcm_bytes),
                "frames": 48000, "samples": len(pcm), "nonzero_samples": sum(value != 0 for value in pcm),
                "peak_pcm16": max(abs(value) for value in pcm), "peak": render["peak"], "rms": render["rms"],
                "clipped_frames": 0, "render_schema_version": 6}
            render_reports[scope] = render
            logs["outputs/" + output.name] = output.read_bytes()
            logs["outputs/" + prepared.name] = actual
        assert results["registration"]["pcm_sha256"] != results["performance"]["pcm_sha256"]
        assert results["registration"]["peak"] < results["performance"]["peak"]
        receipt["results"] = results
        receipt["render_provenance"] = render_reports
        for path in (current, score):
            logs["inputs/" + path.name] = path.read_bytes()
        assert current.read_bytes() == current_bytes
        expected_output_files = {"inputs/current.b3controls", "inputs/phrase.events",
            "controls/Prepared registration.b3performance", "controls/Prepared performance.b3performance",
            "audio/registration.wav", "audio/performance.wav"}
        outputs = inventory(foreign)
        assert {name for name, item in outputs.items() if item["type"] == "file"} == expected_output_files
        assert {name for name, item in outputs.items() if item["type"] == "directory"} == {".", "inputs", "controls", "audio"}
        receipt["output_inventory"] = outputs
        assert check_package(relocated) == before
        receipt["installed_inventory_unchanged"] = True
        observed_changes = {name: identity(Path(name)) for name, value in genuine_inputs.items()
                            if identity(Path(name)) != value}
        # Root may update the operator guide during this independent observation;
        # copied guide bytes remain recorded. Every executable/model/rule input is stable.
        assert set(observed_changes) <= {str(repo / "docs/REGISTRATION_GUIDE.md")}, observed_changes
        receipt["genuine_input_changes_observed"] = observed_changes
        receipt["original_inputs_remain_accessible"] = all(Path(name).is_file() for name in genuine_inputs)
        for name in ("hammond_registration", "hammond_render"):
            needed = run("runtime-" + name, ["/usr/bin/ldd", relocated / "bin" / name])
            assert b"not found" not in needed
        receipt["outcome"] = "pass"
    except Exception:
        receipt["outcome"] = "observer-or-product-failure"
        receipt["failure"] = traceback.format_exc()
        raise
    finally:
        receipt["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        with tarfile.open(archive_file, "w:gz", format=tarfile.PAX_FORMAT) as archive:
            for name, data in sorted(logs.items()):
                entry = tarfile.TarInfo(name)
                entry.size, entry.mtime, entry.mode = len(data), 0, 0o644
                archive.addfile(entry, io.BytesIO(data))
        receipt["originals_archive"] = {"path": str(archive_file.relative_to(repo)), **identity(archive_file),
                                        "members": len(logs)}
        receipt_file.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"outcome": receipt["outcome"], "receipt": str(receipt_file),
                          "commands": len(commands), "archive_bytes": archive_file.stat().st_size}))


if __name__ == "__main__":
    main()
