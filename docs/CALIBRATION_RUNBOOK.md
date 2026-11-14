# Capture and calibration operations

Use this guide to inspect an audio archive, run declared comparisons, retain
every outcome and replay a complete result. The commands work from the source
checkout or the movable `CaptureTools` package. They require Python 3.10 or newer
and its standard library; the capture runtime performs no network requests.

Start with the supplied synthetic archive below. It contains deliberate passing,
inconclusive and failed comparisons, so a nonzero exit can be the expected
engineering result. Current qualification and publication belong to
[STATUS.md](STATUS.md) and the [handoff](CALIBRATION_HANDOFF.md). The
[project plan](PLAN.md) distinguishes this M0/M8 evidence tooling from physical
calibration and the native instrument product.

## 1. Select and identify the source

For a fresh checkout:

```sh
git clone https://github.com/tomasedisonn80/Hammond-B3-Organ.git
cd Hammond-B3-Organ
python3 --version
git status --short
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
```

Use the selected Python 3.10+ interpreter consistently. On Windows the command
may be `python` or `py -3`; substitute that executable for `python3` in the
examples. In an existing checkout, inspect local changes and fetched remote
history before updating it. Preserve unrelated work. A historical test report
does not qualify a modified working tree.

The integration records sometimes map a local acceptance commit to a different
published commit with the same complete Git tree. Use the **published** identity
when selecting a historical version from a fresh clone. A local-only SHA or an
agent's scratch path is not a public setup dependency. The current handoff and
integration records retain those mappings.

Keep tool sources and input archives unchanged while an operation reads them.
Job, study and replay reports retain original input hashes, observed source-file
identities and runtime context. Keep the `.py` sources beside their dependencies;
a compiled cache or a lone copied job script is not the complete toolchain.

## 2. Run the retained example

Run these examples from the repository root. Choose a new result directory; the
example name below must not already contain these report filenames:

```sh
mkdir capture-results
```

In PowerShell, the corresponding directory command is
`New-Item -ItemType Directory -Path capture-results`. Output parents must exist.
Report publication uses a filesystem supporting hard links and preserves every
existing destination, including a dangling link. Use fresh filenames for a new
execution instead of removing earlier evidence to reuse its name.

### Inspect the plan and actual demo bytes

```sh
python3 -B tools/validate_capture.py --input data/capture-planned-example.json
python3 -B tools/capture_readiness.py --input data/capture-planned-example.json --output capture-results/planned-readiness.json
python3 -B tools/capture_corpus.py --input data/corpus-planned-example.json
python3 -B tools/capture_corpus.py --input examples/capture-demo/corpus/corpus.json --check-files --check-audio
python3 -B tools/capture_audio.py --input examples/capture-demo/corpus/audio/reference.f32 --raw-format raw_float32_le --sample-rate-hz 4 --channel-count 1
```

| Command | Expected exit | Expected observation |
| --- | ---: | --- |
| Validate the planned v1 manifest | 0 | Structural validation is `pass`; the record remains `planned`. |
| Inspect plan readiness | 3 | `planned`, with 20 missing declarations among 21 checks. |
| Audit the planned corpus | 3 | `inconclusive`; no acquired stream or assigned purpose is invented. |
| Audit all demo files and selected audio | 0 | `pass` for the declared synthetic corpus. |
| Inspect the literal raw reference | 0 | `inspected`: four frames, one channel, declared rate 4 samples/s. |

The last command is a tiny software fixture, not an acquisition configuration.
Headerless audio requires caller declarations for its format, rate and channels.
Those declarations do not measure a physical clock or calibrated signal scale.
The [audio guide](CAPTURE_AUDIO.md) defines supported formats and bounds.

### Execute every declared comparison

```sh
python3 -B tools/capture_job.py --input examples/capture-demo/job-pass.json --output capture-results/job-pass.json
python3 -B tools/capture_job.py --input examples/capture-demo/job-inconclusive.json --output capture-results/job-inconclusive.json
python3 -B tools/capture_job.py --input examples/capture-demo/job-fail.json --output capture-results/job-fail.json
python3 -B tools/capture_study.py --input examples/capture-demo/study.json --output capture-results/study.json
```

| Input | Expected exit | Complete report |
| --- | ---: | --- |
| `job-pass.json` | 0 | `pass`; literal RMS error 0.25 FS. |
| `job-inconclusive.json` | 3 | `inconclusive`; literal RMS error 0.25 FS with a different fixed bound. |
| `job-fail.json` | 1 | `failed`; literal RMS error 0.5 FS. |
| `study.json` | 1 | `failed`; all three complete jobs remain, one of each outcome. |

Run the lines separately, or use a harness that records each declared expected
code. Do not join the study and replay with a success-only `&&` chain: the
deliberately failed study still produces the complete report needed by replay.
In a POSIX shell inspect `$?` immediately after a command; PowerShell uses
`$LASTEXITCODE`.

The policies are fixed examples, not physical acceptance tolerances. No gain,
delay, resampling, channel fitting or threshold adjustment is silently applied.
The [job](CAPTURE_JOB.md), [policy](CAPTURE_POLICY.md) and
[study](CAPTURE_STUDY.md) guides define the admitted inputs and complete results.

### Replay the complete saved reports

```sh
python3 -B tools/verify_capture_report.py --kind job --input examples/capture-demo/job-pass.json --report capture-results/job-pass.json --output capture-results/pass-replay.json
python3 -B tools/verify_capture_report.py --kind job --input examples/capture-demo/job-inconclusive.json --report capture-results/job-inconclusive.json --output capture-results/inconclusive-replay.json
python3 -B tools/verify_capture_report.py --kind job --input examples/capture-demo/job-fail.json --report capture-results/job-fail.json --output capture-results/fail-replay.json
python3 -B tools/verify_capture_report.py --kind study --input examples/capture-demo/study.json --report capture-results/study.json --output capture-results/study-replay.json
```

All four should exit **0** with `status: "match"` under the same coherent sources
and runtime. Their saved and replayed engineering statuses remain respectively
`pass`, `inconclusive`, `failed` and `failed`. Replay reruns the complete job or
study and compares all canonical report bytes. It does not turn a failed
comparison into a pass.

Retain the exact saved UTF-8 report bytes. Reformatting keys, changing whitespace
or line endings, or serializing `1` as `1.0` is not an equivalent saved report for
this verifier. Prefer the tools' explicit `--output` option when retaining a
report, especially in shells that may recode redirected text. Readiness reports,
audio/corpus reports, generation inventories and `EXPECTED.json` are not job/study
replay inputs. See the [replay contract](CAPTURE_REPLAY.md).

### Create another copy when needed

```sh
python3 -B tools/make_capture_demo.py --output capture-results/new-demo
```

The new directory must be absent and its parent must exist. This creates the
same sixteen original files and returns an inventory with `execution: "not_run"`.
The contained `EXPECTED.json` is a literal expected-result document with the same
execution marker. Neither is a saved execution report. Run the jobs/study against
that new archive explicitly when an executed result is wanted. The
[generator contract](CAPTURE_DEMO.md) preserves partial new creation after a
failure and never recursively removes it.

## 3. Interpret exits and failures

| Tool | Exit 0 | Exit 1 | Exit 2 | Exit 3 |
| --- | --- | --- | --- | --- |
| v1 validator, audio inspector, demo generator | Successful operation or help | Admission, I/O, publication or delivery failure | Usage error | Not used |
| Readiness | `declarations_complete` or help | Rejection/publication/delivery failure | Usage error | `planned` or `declarations_incomplete` |
| Corpus, job, study | `pass` or help | Complete `failed` result, or rejection/I/O/publication/delivery failure | Usage error | Complete `inconclusive` result |
| Report replay | Complete `match`, or help | Complete `mismatch`, or rejection/I/O/publication/delivery failure | Usage error | Not used |

An exit code alone does not distinguish a complete failed comparison from rejected
input. Inspect the report and diagnostic. With a valid completed job/study result,
the report retains its outcome. Admission rejection yields no new report.

File publication and stdout delivery are separate effects. A command can publish
a complete `--output` file and later return 1 because its output pipe closed.
Keep that file; verify the appropriate job/study report against its original input
using a new summary path. If the destination already existed before execution,
the rejection preserves that older file instead. Do not infer a new successful
publication merely because a path exists. If stderr itself is unavailable, a
second diagnostic cannot be delivered there.

The tested CLI boundary retires failed original standard streams so ordinary
closed-pipe failures retain exit 1 instead of CPython's shutdown status 120.
[The independent process review](reviews/CALIBRATION_CLI_PIPELINE.md) records the
actual failures, repair, standalone-script checks and platform limits. A partial
stdout sequence cannot be withdrawn. These checks do not make stdout and file
publication atomic, or establish recovery from every crash or filesystem failure.

For a replay mismatch, inspect `context.same_runtime` and
`context.same_tool_sources` as well as the retained input and complete report
identities. A changed Python/platform or observed tool source can explain a
mismatch even when the numerical values agree. Keep the old report unchanged,
retain the new result under a fresh name, and document the change. Hashes and a
matching replay do not establish historical authorship or when a policy was frozen.

## 4. Use the movable CaptureTools package

Running an already installed package needs only Python and its standard library.
Creating it through the repository's normal configuration additionally needs
CMake **3.21+** and a working **C++20 compiler**. Native target compilation is not
required for this component. From the source root, choose unused build and package
destinations:

```sh
cmake -S . -B build-capture-tools -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
cmake --install build-capture-tools --config Release --component CaptureTools --prefix "$HOME/hammond capture"
```

If CMake selects the wrong interpreter, add
`-DPython3_EXECUTABLE=/absolute/path/to/selected/python` at configuration. For
PowerShell use the same flags with a prefix such as
`--prefix "$env:USERPROFILE\hammond capture"` from a configured compiler
environment. A multi-configuration generator uses `--config Release` at install;
the capture payload itself has no configuration-specific native outputs.

The explicit component selection matters: an unqualified install does not select
`CaptureTools`. Leave `CMAKE_INSTALL_MODE` unset or use `COPY`. The package has
**57 files** under:

```text
<prefix>/<CMAKE_INSTALL_DATADIR>/hammond-b3-organ/capture-tools
```

The default data directory is `share`. Move the complete directory or containing
prefix while preserving its internal paths. For example, after choosing the
actual moved location and an existing report directory:

```sh
hammond_capture="$HOME/hammond moved/share/hammond-b3-organ/capture-tools"
hammond_reports="$HOME/hammond reports"
mkdir -p "$hammond_reports"
python3 -B "$hammond_capture/tools/capture_study.py" --input "$hammond_capture/examples/capture-demo/study.json" --output "$hammond_reports/study.json"
python3 -B "$hammond_capture/tools/verify_capture_report.py" --kind study --input "$hammond_capture/examples/capture-demo/study.json" --report "$hammond_reports/study.json" --output "$hammond_reports/study-replay.json"
```

Run the last two separately: expected exits are **1 then 0**. Use fresh filenames
if that reports directory has been used before. The package's root `README.md`
and copied [installation guide](CAPTURE_TOOLS_INSTALL.md) provide the complete
inventory and additional commands. This repository runbook is a companion;
it is not an extra file in the frozen 57-file package.

Keep the ten packaged modules together for the full pipeline. The original
generator and v1 validator separately retain single-file, standard-library-only
execution; that exception does not make a lone job, study or replay script a
complete installation. Use `-B` to avoid bytecode caches; `-S` may also be used
to exclude site packages. Neither setting replaces retaining actual source files.

Installation rejects an existing `capture-tools` destination before copying.
A later failure can leave a partial new package and deliberately does not remove
it. Retain the nonzero result and inspect that directory; choose another fresh
destination for a separate installation. Source files and destination directories
must remain quiescent during installation. The detailed preflight/partial-copy
boundary is in the installation contract.

### The other components remain separate

| Component | Contents and next guide |
| --- | --- |
| `CaptureTools` | The 57-file Python/data/documentation pipeline described here; no native build output. |
| `OfflineTools` | Five native executables, two plot scripts, one compiled profile and fifteen fixture/catalog files: 23 files. Build its required targets before installing. See [OFFLINE_INSTALL.md](OFFLINE_INSTALL.md) and [PEDAL_HANDOFF.md](PEDAL_HANDOFF.md). |
| Native standalone and VST3 | Optional instrument adapters with their own dependencies, build/install commands and qualification. See [STANDALONE_HANDOFF.md](STANDALONE_HANDOFF.md) and [VST3_BUILD.md](VST3_BUILD.md). |

The capture and offline components can share a prefix while keeping their
separate inventories. Unlike the capture destination preflight, the existing
offline install can replace selected files in its prefix; use a new prefix to
retain a separate version. The [clean-setup review](reviews/CALIBRATION_CLEAN_SETUP.md)
records an actual coherent co-installation, relocation and execution with the
private source/build removed. Native device, DAW and physical fidelity claims
remain separate from those software workflows.

## 5. Apply the pipeline to a real archive

1. Retain original files and their acquisition context before making derivatives.
   Keep raw/derived ancestry and channel meaning explicit. `.f32` is marked binary
   in Git because valid sample bytes can resemble text line endings; retain
   original hashes across every transfer. See the [byte-identity finding](reviews/CALIBRATION_RAW_GIT_IDENTITY.md).
2. Validate the v1 manifest and inspect readiness. Missing declarations remain
   explicit reasons. `declarations_complete` means declarations are present, not
   that their truth, calibration or permissions have been established.
3. Audit the **complete** corpus with the required file/audio flags. Structural
   mode alone does not read artifacts. File checks establish observed byte
   identities; audio mode also inspects selected streams. Support files are not
   decoded, and uninspected derivatives remain visible. The whole lineage/split
   graph must be considered before evaluating a selected pair.
4. Declare original policy bytes, windows, channels, units, uncertainty and roles
   before judging a candidate. Use the [job contract](CAPTURE_JOB_CONTRACT.md)
   and [policy guide](CAPTURE_POLICY.md). Preserve valid compact original JSON;
   parsing and reserializing it creates different bytes and is not a substitute
   for retaining the original binding.
5. Execute fixed jobs or their bounded study, retain every complete result, and
   replay with the original archive and a recorded source/runtime. Preserve
   failed and inconclusive results. A derived stream's own descriptor does not
   inherit its ancestor raw stream's physical calibration.
6. Keep the human acquisition, specimen, metrology, rights and held-out-history
   review alongside these digital checks. The [acquisition protocol](CAPTURE_PROTOCOL.md)
   defines those required observations. A clean graph, small residual or matching
   replay does not close them.

These commands perform no acquisition, model fitting or implicit physical
correction. The synthetic examples create no measured instrument value. Keep
scanner, AO-28, Leslie and adapter work under their current owners and applicable
gates rather than treating this toolchain's pass as their acceptance.

The retained [resource profile](../examples/benchmarks/capture-toolchain-v1/README.md)
and [metadata allocation experiment](reviews/CALIBRATION_METADATA_ALLOCATION.md)
are optional engineering diagnostics. Reproduce them with their explicitly
identified source sets and frozen criteria; substituting the current tool
directory changes the experiment. The [allocation integration record](reviews/CALIBRATION_ALLOCATION_INTEGRATION.md)
maps the historical local freeze to its published source equivalent. Private
paths in old execution notes describe those runs and are not installation
prerequisites. The measured Python allocation observation is not a general
latency, resident-memory or audio-callback guarantee.

## 6. Continue development from a reviewable state

Read [AGENTS.md](../AGENTS.md), the current status/next steps, relevant scope and
the actual [session manifest](development/2026-11-13-calibration/assignments.json)
before selecting work. Take explicit file ownership and a dependency-ready task.
The [calibration handoff](CALIBRATION_HANDOFF.md) is the current evidence pointer;
this runbook supplies commands and interpretation, not a replacement task ledger.

For a fresh source gate with the optional native adapters disabled:

```sh
cmake -S . -B build-review -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
cmake --build build-review --config Release --parallel 2
ctest --test-dir build-review -C Release --output-on-failure --no-tests=error
```

Use a coherent source snapshot and its own build directory. Discover the selected
configuration's tests instead of copying an old count. Preserve initial failures,
repairs, actual commands, source/data/tool identities and unrun scopes. An agent's
note, CTest suite, unittest method and subprocess invocation are different counts.
The session checker validates retained accounting consistency; it does not attest
external dispatch. Its strict sixty-complete gate belongs after substantive
acceptance of all sixty actual assignments in that requested session.

The integrator updates status, next steps, development log and affected contracts,
commits completed work and publishes under the standing owner authorization.
Inspect concurrent advances, integrate them without discarding another track's
work, use the guarded non-force workflow and verify the fetched remote commit/tree.
The next concrete project task remains in [NEXT_STEPS.md](NEXT_STEPS.md); physical
work begins with the acquisition protocol's actual identity/configuration/evidence
inputs, while independent engineering can continue under its explicit scope.

## Verification of this guide

Assignment 52 executed fifteen public source commands against one immutable
ten-module copy, from a foreign working directory with Unicode/space paths,
`python -B -S`, an empty `PYTHONPATH` and ASCII terminal encoding. All expected
outcomes, four exact replays, literal RMS values, original inputs, existing-output
preservation and the identical sixteen-file regenerated archive passed. Its
[assignment record](development/2026-11-13-calibration/52-operations.md) retains
the exact source identity, commands, results and corrected harness mistakes.

Assignment 50 separately executed the installed/co-installed flows cited above;
its clean-setup review owns that evidence. These local checks establish command
behavior for their identified source. They do not replace later source-specific
hosted checks, native device/host execution or physical calibration.
