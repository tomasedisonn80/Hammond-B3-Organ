# Registration and apron CI admission

16 November 2026; A37 (`/root/w07_a37`), wave 7. **Admitted for configured
coverage, source inspection and the local checks below. Hosted execution of
these changes remains pending.** Reviewed local HEAD is
`d281d4e3063f44b9eda6b5bc4ea44fc99a6c7f93`, tree
`1e59776459a05a9d934d0b519a45cd4c61b13ae9`, with the identified workflow overlay
and root's subsequent starter Load wiring.

## Existing coverage and bounded additions

Inspection of root CMake, the presets and all three workflows established that
the broad core jobs already build the registration inputs and run unfiltered
CTest. No additional registration job or repeated full build is needed.

| Existing jobs | Coverage and amendment |
| --- | --- |
| Core Release: Linux GCC, macOS AppleClang, Windows MSVC | Existing full CTest covers the CLI, shared reader, storage, renderer controls, generator, literal oracle, auditions, explicit installer and apron tools. A new discovery assertion requires all 12 named suites, with commands and without disabled flags. |
| Core Linux ASan/UBSan/leaks | The same 12 discovery requirements precede the unchanged full instrumented CTest run. |
| Native Release: three platforms with MIDI, plus Linux without MIDI | Existing `^test_standalone_` selection remains. Direct apron, candidate raster, unavailable-texture raster and real starter Load become explicit required names. Load discovery requires its actual script and both built executable paths. |
| Native Linux ASan/UBSan/leaks | All original 25 test-to-target pairs remain; the three apron executables bring exact discovery/build counts to 28. The fallback Drawing archive joins object/archive/runtime instrumentation checks. Its texture-creation seam and the fallback executable's link are checked. |
| Full R4 and three native VST3 jobs | Unchanged; their existing build, validator, experiment, packaging and evidence gates remain. |

All **13 matrix-expanded jobs**, triggers, permissions, concurrency rules, action
pins and job timeouts are preserved. Existing native sanitizer options, leak
checking, required source inputs, no-override policy and per-test timeout checks
remain. The calibration probe still must link its original six instrumented
archives; adding the independent fallback archive does not incorrectly require
the calibration probe to link it. New apron limits retain CMake's 30/60/60 seconds.

Root independently owns the new CMake registration and aggregate dependency for
`test_standalone_starter_load`. This workflow work changes no production source,
format, contract, fixture, asset, install inventory or native VST3 workflow.

## Windows Unicode source-root qualification

The existing Windows core Release job gains one ten-minute step. It archives
**only tracked HEAD** using `git archive`, checks the event revision and extracts
with Python's `data` filter into a fresh path containing spaces, `é` and `漢字`.
Private/untracked files are never copied. The actual generator alone is built
with testing, SDL, VST3 and MIDI disabled; dependencies are its ordinary core
and headless support targets. Configuration/build subprocess bounds are 120/360
seconds. CMake's Release codemodel must contain both generator `/utf-8` and the
exact Unicode source-root definition. Existing generator-only encoding scope is
unchanged.

The produced executable must emit 24 successful file records and a complete
summary, then match all 24 archived canonical files by filename, bytes and hash.
A second invocation targets an absent child of the **archived** authored pack:
it must report `ProtectedPath`, attempt/commit nothing and create nothing.
This exercises the compiled source root; a nonempty-directory refusal would
not suffice. The archived pack inventory must remain unchanged. Original
tracked source stays untouched; ordinary CI diagnostics use `ci-logs`. Command logs, codemodel, cache,
archive/source/binary identities, output inventory and refusal are retained
under the existing diagnostic artifact. Unicode construction failures are fatal,
without capability skips. This step is configured, not yet executed on Windows.

## Optional dependency boundary and executed checks

The ordinary jobs install neither NumPy nor Pillow. Linux Release additionally
runs the author/compiler and transport suites with `-S`, recording explicit
optional skips. From `/workspace/scratch/3edffb787db3/Hammond-B3-Organ`, Python
3.12.14 executed:

```sh
python3 -B -S tests/test_reference_apron_art.py -v
python3 -B -S tests/test_reference_apron_raster_checker.py -v
ctest --test-dir ../build-native -C Release --show-only=json-v1 --no-tests=error
git diff --check
```

Author/compiler: **19 pass, six Pillow skips**, 25 methods, 2.550 seconds.
Transport/boundaries: **12 pass, two NumPy skips**, 14 methods, 0.363 seconds.
These results do not qualify skipped source-decoding or pixel comparisons.
Read-only root Release discovery found 235 tests, including all 12 core names,
all 28 selected native sanitizer names with built inputs, and the seven-argument
Load command with both binaries and timeout 60. Discovery SHA-256 is
`f27e18c1b0bd0fba9f28189e3d716d13007cc0a6365c6de4dc46899b72d859d7`.
It is not a 235-test run or sanitizer execution.

Duplicate-key-aware YAML parsing passes all three files; `bash -n` passes all
47 run blocks and `ast.parse` passes all 16 Python heredocs. Baseline comparison
confirms retained jobs, matrices and original sanitizer pairs. `actionlint` and
`shellcheck` were unavailable. No configure/build, hosted dispatch, commit or
publication was performed by A37.

## Exact reviewed SHA-256 identities

| File | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `0c611ad28b8d314dde4ba7bff54b7269655a5b8c0fad394f27a29689405489af` |
| `.github/workflows/standalone.yml` | `63562572323414a3b74d247fa78d7d3a3c03d09489fd2311a2794865b0b99549` |
| Unchanged `.github/workflows/native-vst3.yml` | `2376f41bfd96ff5afa2c821299588de05e5c49221879aef91a82074955649721` |
| Root `CMakeLists.txt` | `87f5905c34c3dafcd6a113f9d362d5e135c5777751a1364370652b8fcfaf0313` |
| `apps/standalone/CMakeLists.txt` | `8c9083d5de40ab398c224e61550f5b218b02ebe7c8d7cc0bc94078e92dff99cf` |
| `tools/generate_starter_registrations.cpp` | `dd93af18acd911cc6f0420314d0811c34adaaddf496e86e9df120f3576382e91` |
| Native starter Load test | `22285ddcaec03adf61f97b1d65c7e70de4ee6c6437480267b4784ab8d360f5c7` |

Next: root publishes the reviewed changes and observes every required job at the
published revision, including the Windows Unicode step and all 28 native
sanitizer gates. macOS/Windows execution, native device/DPI/accessibility, exact
paired raster evidence and whole-interface/physical fidelity remain separate
claims; discovery and syntax checks cannot close them.
