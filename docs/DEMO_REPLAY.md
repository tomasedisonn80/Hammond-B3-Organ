# Retained demo verification and local replay

Agent 51 independently consumed the [four-second two-manual demo](../examples/rendered/nominal-two-manual-v1/README.md)
on 2026-11-13, then built a fresh Release renderer from an archive of revision
`6c3dd8bc923a3c11f6b234425b056e135fbe9f4b` and actually rendered the retained
profile, score and settings again. The two executables were byte-identical on
this local toolchain. The complete WAV, decoded stereo PCM payload, input and
compiled-profile bytes, actual stdout/stderr, and reported metrics also agreed.
These are observed local synthetic-engineering results. Authentication, build
provenance, cross-platform reproducibility and instrument fidelity remain
unestablished.

The producer's pristine seven-file `bundle/` was never edited. Its manifest
SHA-256 remains `74ad49caa3cc5170870bed1002ea64ffaaf8a202c0614095b31fdcd8308da2ce`.
Its historical Git record says `6c3dd8b`, `dirty: true`, and
`binary_association: not_established`. A later successful replay does not rewrite
that original record or turn its sampled checkout identity into a build attestation.

## Portable retained-bundle gate

Run the standard-library test directly, or use CTest after configuration:

```sh
python3 tests/test_demo_bundle.py -v
ctest --test-dir build-release -C Release -R '^python_test_demo_bundle$' \
  --output-on-failure --no-tests=error
```

Use `python` if that is the Python 3 command on the current platform. CMake's
existing `test_*.py` discovery registers this test; no workflow edit or dependency
is needed. Missing retained files fail explicitly, with no skipped assertions.
The gate does not require or launch the current build's renderer.

Agent 51's original seven methods cover these artifact boundaries:

- Consume the bundle with [the independent verifier](RENDER_VERIFICATION.md),
  require exactly seven files, and pin all their raw-byte SHA-256 identities.
- Bind the entire profile and score to the current versioned source bytes and
  catalog. Require 192,000 frames at 48,000 Hz, block size 127, seed 2601,
  initial drawbars `006400000`, all 34 events on both manuals, file-event mode,
  a null default note, and `fail_on_clip: true`.
- Independently decode every PCM frame, require equal dry channels, the exact
  retained integer peak and sum of squares, nonzero audio in all four chord
  spans, and exact leading/final silence. Require zero reported clipping and
  the declared float-versus-PCM quantization bound.
- Copy the untouched bundle to a new directory and consume its manifest through
  the real verifier CLI. Preserve the historical absolute invocation paths.
- Exercise an unavailable historical executable, foreign POSIX path metadata,
  and continued rejection of present executables with changed bytes, a nonfile
  type or unacceptable ancestry.

Pinned audio bytes identify this particular retained artifact. They are not an
expected output hash for future renders by AppleClang, MSVC, other GCC builds,
other standard libraries or other architectures. Existing musical-fixture tests
own current-renderer behavior; this gate owns the retained demo's integrity.

Agent 56's subsequent [final evidence review](reviews/FINAL_EVIDENCE_REVIEW.md)
added an eighth method for a real former build-directory path that now names a
regular file. The executable below that path is absent; verification now reports
it unavailable instead of failing with `NotADirectoryError`. The expanded
8-method demo suite and existing 27-method verifier suite passed locally with
zero skips. Present executable checks and all frozen bundle bytes remain unchanged.
These later results supplement the original seven-method run recorded below.

## Historical paths and the reproduced consumer defect

The manifest's Linux absolute paths describe the producing session. They are
not substituted with current paths, used as commands, or asserted to exist on
another machine. The copied `profile.json`, `profile.b3p`, `events.txt`, WAV and
logs are the consumer's evidence. A foreign operating-system executable path
reports `renderer.status: unavailable`; absent or unreadable native executable
paths also report unavailable. A readable present executable must still match.
The verifier always reports `replay.status: not_performed`, even when its
executable hash matches. Actual replay is the separate operation below.

Before the repair, an absent executable beneath a symlinked ancestor failed
with `VerificationError: directory is not a regular nonsymlink directory`.
The Linux reproduction used a real directory symlink, rather than merely
assuming that a native macOS runner would fail. From the repository root:

```python
from pathlib import Path
import importlib.util, json, shutil, tempfile
spec = importlib.util.spec_from_file_location("consumer_probe", Path("tools/verify_render.py"))
consumer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(consumer)
with tempfile.TemporaryDirectory(prefix="hammond-a51-probe-") as work:
    root = Path(work).resolve()
    bundle = root / "bundle"
    shutil.copytree("examples/rendered/nominal-two-manual-v1/bundle", bundle)
    real = root / "real-temporary-root"
    real.mkdir()
    alias = root / "tmp-alias"
    alias.symlink_to(real, target_is_directory=True)
    absent = alias / "expired-session" / "hammond_render"
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["renderer"]["path"] = str(absent)
    manifest["invocation"]["argv"][0] = str(absent)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    print(absent.exists(), alias.is_symlink())  # Observed: False True
    print(consumer.verify_bundle(bundle))
```

After the narrow repair, the same reproduction returned
`verified_retained_bundle`, `renderer: {status: unavailable, reason: FileNotFoundError}`,
and `replay: {status: not_performed, renderer_available: false, ...}`.
The consumer now checks the final external path's availability before inspecting
its ancestors. Existing external files still undergo all strict reader type,
ancestry, identity, stability, size and SHA-256 checks. Retained artifact and
directory rules are unchanged.

The new automated regression models the absent-path/ancestor condition without
requiring Windows symlink privileges. Another check changes only the consumer
module's OS view to exercise foreign-path classification while retaining real
local file reads. Neither simulated boundary is a native Windows or macOS run.
The actual hosted matrix must qualify this new gate and repair.

## Clean local Release build and actual replay

The fresh workspace was `/tmp/hammond-a51-replay-xuy_r2pb`. A new `source.tar`
was written by `subprocess.run(["git", "archive", "--format=tar", revision],
stdout=stream, check=True)` with the full revision above, then extracted into
an empty `source/` using Python `tarfile.extractall(..., filter="data")`.
The source archive SHA-256 was
`85f2f74457ae0defd672c9b19f717ada683ba941404ecc2a0392047f773798ff`.
The extracted source had no `.git` directory. No working-tree changes were
copied into that build.

Observed tools were CMake 4.4.4, `/usr/bin/c++` (GCC 14.2.0), and Python
3.12.14 on Linux x86_64. Both the producing and fresh builds used Release
`-O3 -DNDEBUG`, C++20 and the repository's strict warnings, with sanitizers off.
The fresh build disabled test targets and built only `hammond_render` and its
required core/profile dependencies. These exact configure/build commands exited 0:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /tmp/hammond-a51-replay-xuy_r2pb/source \
  -B /tmp/hammond-a51-replay-xuy_r2pb/build -G 'Unix Makefiles' \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=/usr/bin/c++ \
  -DBUILD_TESTING=OFF -DHAMMOND_ENABLE_SANITIZERS=OFF
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /tmp/hammond-a51-replay-xuy_r2pb/build \
  --target hammond_render --parallel 2 --verbose
```

The original producing executable was
`/tmp/hammond-wave07-asuv11lz/build/hammond_render`. All files in the original
staged source's `src/` (5), `include/` (7), `tools/` (11), `tests/` (22), and
`data/` (11) matched the fresh archive by relative name and SHA-256, excluding
generated `__pycache__` contents. This is a local file comparison, not
authenticated source/build provenance.

The following exact invocation used the archived wrapper and retained inputs,
writing to a previously nonexistent `rerender/` directory. It exited 0 with
`status: succeeded` and `evidence_scope: synthetic_engineering`:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 \
  /tmp/hammond-a51-replay-xuy_r2pb/source/tools/render_fixture.py \
  --renderer /tmp/hammond-a51-replay-xuy_r2pb/build/hammond_render \
  --profile-json /workspace/scratch/c871510c69b2/Hammond-B3-Organ/examples/rendered/nominal-two-manual-v1/bundle/profile.json \
  --events /workspace/scratch/c871510c69b2/Hammond-B3-Organ/examples/rendered/nominal-two-manual-v1/bundle/events.txt \
  --output-dir /tmp/hammond-a51-replay-xuy_r2pb/rerender \
  --frames 192000 --sample-rate 48000 --block-size 127 --seed 2601 \
  --drawbars 006400000 --timeout-seconds 120
PYTHONDONTWRITEBYTECODE=1 python3 tools/verify_render.py \
  /tmp/hammond-a51-replay-xuy_r2pb/rerender
```

Independent verification of the fresh bundle also exited 0. Its manifest
SHA-256 was `cb47d646f392423b82cf8d2fc5123f5159f7ce7c0d7e4eece60d48bd7755c7c4`.
The archived wrapper correctly recorded null Git HEAD/dirty fields and
`git HEAD unavailable`; it did not invent repository metadata for an archive.
Timestamps, output paths and sampled Git fields were excluded from the replay
comparison. The original manifest remained unchanged.

| Compared quantity | Observed result for retained and fresh output |
| --- | --- |
| Executable, 106,368 bytes | Byte-identical; SHA-256 `8e781cb1df6f87443c4b6c88587cfa0e7d2bc8e23d32b5ef0a0bfb84d9ee8be4` |
| Complete WAV, 768,044 bytes | Byte-identical; SHA-256 `9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd` |
| Interleaved stereo PCM payload, 768,000 bytes | SHA-256 `1c2216be3fced52b677be9e09393d0edccf98292529668019f88495a7c88600f`; all frames agree |
| Profile JSON / compiled profile / events / stdout / stderr | Each complete byte stream is equal |
| Parameters and actual renderer metrics | All fields equal |
| Engine pre-quantization peak / RMS | `0.08130008727312088` / `0.02006219567993473` |
| Decoded one-channel integer peak / sum of squares | `2664` / `82976846092` |
| Decoded PCM peak / RMS | `0.081298828125` / `0.020062170290109253` |
| Clipped frames / channel samples | `0` / `0` |
| Channels / decoded frames | Two identical dry channels / `192000` |

## Executed checks and remaining gates

The direct new gate passed all 7 methods in 0.525 seconds; the affected verifier
suite passed all 27 methods in 0.899 seconds. Both reported zero failures and
zero skips. The exact commands were:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_demo_bundle.py -v
PYTHONDONTWRITEBYTECODE=1 \
  HAMMOND_RENDER_EXECUTABLE=/tmp/hammond-wave07-asuv11lz/build/hammond_render \
  HAMMOND_TEST_PROFILE=/tmp/hammond-wave07-asuv11lz/build/nominal.b3p \
  python3 tests/test_verify_render.py -v
```

A separate configuration of the current working tree at
`/tmp/hammond-a51-replay-xuy_r2pb/gate-build` used the same CMake options above
with `-S .` and `-DBUILD_TESTING=ON`. No renderer or unrelated test targets were
built there. The new retained-artifact gate was discovered and passed as 1/1
selected CTest test in 0.52 seconds:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /tmp/hammond-a51-replay-xuy_r2pb/gate-build -C Release \
  -R '^python_test_demo_bundle$' --output-on-failure --no-tests=error
```

No redundant full CTest suite, local sanitizer run, native Windows/macOS run,
host/device test, listening trial or physical comparison was performed for this
assignment. The fresh render was measured and compared as files; playback was
not claimed. Hosted CI for the integrated revision remains a separate gate.
The result closes this retained artifact's local integrity and same-toolchain
replay checks; it does not qualify a playable product or a measured Hammond.
