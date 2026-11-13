# Current developer handoff — nominal console continuation

Start here for the implemented console and its offline tools. The older
[session handoff](SESSION_HANDOFF.md) preserves the original session's dated
inventory and evidence. [STATUS.md](STATUS.md), [NEXT_STEPS.md](NEXT_STEPS.md) and
the newest [continuation ledger](development/2026-11-13-continuation/README.md)
remain authoritative when a later checkpoint changes this page.

The project has a working nominal dry-organ engine and a **partial M3 console**.
Its source and console parameters remain unmeasured. Runtime pedals, physical
preset latches, continuous drawbars, switching bandwidth, loaded expression,
scanner, AO-28, Leslie processing, calibration and the playable plugin/device/UI
product still have separate gates in [PLAN.md](PLAN.md).

## The next developer's first 30 minutes

1. Read [AGENTS.md](../AGENTS.md), current status/next steps and the latest
   development-log entry. Inspect the current revision and other workers' file
   ownership before choosing a task. The original and continuation ledgers count
   different assignments; planned rows are not completed work.
2. Build and run the current Release suite from one coherent checkout or frozen
   archive. Record the exact source identity and actual result. Never combine an
   older static library with newer live headers.
3. Verify the retained console example, render a short WAV, and inspect a partial
   trace/plot using the commands below. This provides an observable baseline.
4. Take the first unowned step in [M3_NEXT_GATE.md](M3_NEXT_GATE.md): admit the
   existing pedal map into a fixed-storage routing/bus-excitation kernel before
   adding public pedal events or saved controls. Declare owned files and the
   evidence that will close the task.

For a new checkout:

```sh
git clone https://github.com/tomasedisonn80/Hammond-B3-Organ.git
cd Hammond-B3-Organ
```

For either a new or existing checkout, inspect without discarding local work:

```sh
git status --short --branch
git fetch origin main
git log --left-right --oneline HEAD...origin/main
git rev-parse HEAD 'HEAD^{tree}'
```

Reconcile incoming work before editing. A shared dirty tree needs coordinated
ownership or an isolated checkout; a blind pull/reset is not an integration plan.

## Qualification attached to actual revisions

| Checkpoint | Observed evidence | Scope |
| --- | --- | --- |
| `9a5c99a862daf26a2bab9b05613c98803727a3e7` | [Run 43375043990](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43375043990): all four jobs passed, each with 43 suites, 352 Python methods and zero skipped tests | Published partial-key, lifecycle, ownership, trace and plot code; Linux/macOS/Windows Release and Linux ASan/UBSan with leaks. The [platform review](reviews/CONTINUATION_PLATFORM_REVIEW.md) retains complete-log and artifact verification. |
| `2046b9388f6aab1122e37646b2f20199b5c6079f` | All 45 local Release suites passed in 12.91 seconds on tree `0c722f1ffa2a2f04522438a4cb86cec6b8d3e392`. Published tree `759ddcaf93be2047a5732034663e565f728fb5ad` differs only in Markdown result records; runtime/test blobs and archive checks were verified. | Adds enabled-path allocation checks, the 16-file install, console/owned-input benchmarks and the benchmark stdout-error repair. The integrator observed [run 43376892064](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43376892064) complete successfully in all four jobs, each reporting all 45 suites passed. |

Later demo, planning, handoff and review work has its own assignment notes and
integration gate. An earlier green matrix does not qualify later source changes.
Current [status](STATUS.md) and the ledger record subsequent observed outcomes.

## Architecture and invariants to preserve

| Area | Start in | Current responsibility |
| --- | --- | --- |
| Authoring and preparation | [Profile contract](PROFILE_FORMAT.md), `data/profiles/`, `tools/compile_profile.py`, `Profile.h/.cpp` | Validate rich data outside processing; install a value-owned `RuntimeProfile`. The build generates `nominal.b3p`. |
| Shared source field | `TonewheelBank.h/.cpp`, [numerical bounds](NUMERICAL_BOUNDS.md) | Exactly 91 free-running sine sources. Every branch selecting a tone ID shares its phase/sample; silence and disconnected output still advance the field. |
| Console dynamics | `ContactBank.h/.cpp`, `Percussion.h/.cpp`, `ConsoleModel.h`, [console contract](CONSOLE_DYNAMICS.md) | Two 61-key manuals with nine independent contacts per key; partial travel/hysteresis and one shared upper-B readiness state. Defaults remain ideal contacts with percussion off. |
| Mixing and musical controls | `Engine.h/.cpp`, `ControlState.h/.cpp`, [Engine API](ENGINE_API.md) | Fixed-capacity sample-offset dispatch, coherent branch sums, retained A/B banks, Cancel/reselection, expression and percussion routing. |
| External input | `NoteOwnership.h/.cpp`, `InputProcessor.h/.cpp`, `ParameterBridge.h/.cpp` | Bounded external owners, transactional physical-key dispatch and all 43 normalized internal control mappings; no native host SDK or MIDI-byte decoder. |
| Offline inspection | `tools/`, `tests/`, [evidence](RENDER_EVIDENCE.md), [traces](CONSOLE_TRACE.md) | WAV rendering, independent retained-bundle verification, factory/parameter metadata, sample-aligned CSV, SVG and observed workload intervals. |

Keep one-based tone IDs, physical terminals, MIDI notes and array indices
distinct. Manual MIDI notes are 36–96, while their routes use tone IDs 13–91.
The separate [pedal map](../data/pedal-map.json) contains 200 positions, including
five tagged disconnections; it has no runtime audio consumer yet.

The core's [processing contract](ENGINE_API.md) admits at most 65,536 frames and
1,024 events per call, subject to the prepared block limit. It preflights the
entire call before changing state/output. Events preserve supplied equal-offset
order. A sample uses the state after its events, then advances sources, contacts
and readiness once. A zero-frame flush advances none of them. Rejection does
not silently clear the caller's output.

[NoteOwnership](NOTE_OWNERSHIP.md) has 256 owner slots. Use one coordinated note
authority for a physical key: uncoordinated direct NoteOn/NoteOff/KeyPosition or
panic calls bypass the owner's bookkeeping. [InputProcessor](INPUT_PROCESSOR.md)
commits owners only after Engine accepts the translated block. A successful
Engine re-prepare requires corresponding ownership preparation; changing only
one side can strand keys or suppress a later press.

| Operation/state | Required distinction |
| --- | --- |
| Musical save/load | [B3CONTROLS2](CONTROL_STATE_FORMAT.md) writes 43 controls plus two route-enable bits. It reads version 1 with explicit percussion defaults. The registry's earlier 39 records remain unchanged. |
| Dynamic history | Owners, contact trajectories, readiness, source phase and frame count are not saved musical controls. Restoring controls does not reset them. |
| Rate transition | [Reconfigure sample rate](SAMPLE_RATE_LIFECYCLE.md) preserves history at supported 44.1/48/96 kHz when the owned profile admits the rate. Same-rate calls are exact no-ops. Mixed-rate seconds require a retained segment schedule. |
| Thread boundary | Processing, diagnostics and state changes require stopped or same-processing-thread access. Loading, serialization and filesystem work stay outside processing; there is no concurrent UI publication protocol. |

The [enabled-path audit](REALTIME.md) observes C++ allocation/deallocation calls
within its declared scope. The conservative mix-rebuild bound is one complete
rebuild per rendered frame because contact edges can change connectivity without
new events. Neither that bound nor the benchmark supplies a native callback
deadline guarantee.

## Build once, then use the matching tools

Requirements are C++20, CMake 3.21+ and Python 3.10+. From the repository root:

```sh
cmake --preset release
cmake --build --preset release --parallel 2
ctest --preset release
```

These presets select Release for both single- and multi-configuration generators.
The generated profile is always `build-release/nominal.b3p`. Native executable
locations depend on the generator:

| Generator | Typical renderer path |
| --- | --- |
| Single-configuration Makefiles/Ninja | `build-release/hammond_render` |
| Visual Studio / multi-configuration Release | `build-release/Release/hammond_render.exe` on Windows; use the corresponding configuration directory on other platforms |

The commands below use POSIX single-configuration paths and `python3`. On Windows,
use your Python 3.10+ command, the `.exe`/configuration paths above, and PowerShell's
`&` invocation for quoted executable paths. [BUILD.md](BUILD.md) and
[OFFLINE_INSTALL.md](OFFLINE_INSTALL.md) retain complete PowerShell examples.
For example, the direct-render command is a single line in PowerShell:

```powershell
cmake -E make_directory out
& .\build-release\Release\hammond_render.exe --profile .\build-release\nominal.b3p --output .\out\quick.wav --frames 48000 --sample-rate 48000 --block-size 64 --seed 0 --drawbars 008000000 --note 60 --contacts nominal --percussion second --percussion-volume normal --percussion-decay fast --fail-on-clip
```

When sanitizer qualification is required, use the separate supported GCC/Clang
`sanitizers` preset and the effective leak-enabled environment in
[CI](CI.md). Preserve a local tooling blocker explicitly; disabling leaks does
not qualify the leak gate. Do not run binaries built against another revision's
headers, and rebuild consumers after an API/layout change.

### Render and retain evidence

Create `out/` first and choose unused WAV, trace, plot and bundle destinations.
Renderer/trace/plot publication preserves existing files; shell redirection of
JSON remains the caller's responsibility.

```sh
cmake -E make_directory out
./build-release/hammond_render --profile build-release/nominal.b3p \
  --output out/quick.wav --frames 48000 --sample-rate 48000 --block-size 64 \
  --seed 0 --drawbars 008000000 --note 60 --contacts nominal \
  --percussion second --percussion-volume normal --percussion-decay fast --fail-on-clip
```

The [two-second console example](../examples/rendered/nominal-console-v2/README.md)
has a retained score/bundle and a separate diagnostic trace/plot. Check its bundle
read-only, or produce fresh evidence using its retained profile and explicit settings:

```sh
python3 -B tools/verify_render.py examples/rendered/nominal-console-v2/bundle
python3 -B tools/render_fixture.py --renderer build-release/hammond_render \
  --profile-json examples/rendered/nominal-console-v2/bundle/profile.json \
  --output-dir out/console-evidence \
  --events examples/rendered/nominal-console-v2/console-demo.events \
  --frames 96000 --sample-rate 48000 --block-size 127 --seed 0 --drawbars 008000008 \
  --contacts nominal --percussion second --percussion-volume normal --percussion-decay fast
python3 -B tools/verify_render.py out/console-evidence > out/console-verification.json
python3 -B tools/analyze_wav.py --input out/console-evidence/render.wav > out/console-analysis.json
```

Require a successful process exit, producer `status: succeeded`, zero clipping
and verifier `status: verified_retained_bundle`. Keep reports outside the bundle.
The verifier checks retained integrity without executing recorded commands; a
historical executable path can be unavailable. Do not edit a genuine manifest to
make it pass. Schema 2 supports `key_position` with mode-aware validation; the
historical schema-1 bundle remains supported without that new command.

### Inspect parameters and sample-aligned behavior

```sh
./build-release/hammond_model_info > out/console-models.json
./build-release/hammond_parameter_info --normalized 0.5 > out/parameters.json
./build-release/hammond_console_trace --profile build-release/nominal.b3p \
  --scenario partial --sample-rate 48000 --seed 0 --output out/partial.csv
python3 -B tools/plot_console_trace.py --input out/partial.csv --output out/partial.svg
./build-release/hammond_benchmark --profile build-release/nominal.b3p \
  --case console_all --sample-rate 48000 --block-size 384 --warmup 1 \
  --iterations 7 --seed 71 > out/console-benchmark.json
```

[Model metadata](MODEL_METADATA.md) describes the compiled factories, not arbitrary
custom parameters or a live Engine. [Parameter metadata](PARAMETER_BRIDGE.md)
describes proposed internal mappings, not verified VST3 exports. The trace's
`partial`, `legato` and `routing` scenarios each last 120 ms. Its
[SVG](CONSOLE_TRACE_PLOTS.md) retains exact contact/target transitions and declared
extrema-preserving plotting reductions. The [console benchmark](BENCHMARKING.md)
reports observed intervals and work accounting; its legacy `all` still selects
the original four cases and has a separate report schema. Check exit status before
accepting any stdout report.

### Install and move the offline package

After the complete Release build, choose an unused absolute prefix and a second
unused destination for relocation:

```sh
cmake --install build-release --config Release --component OfflineTools \
  --prefix "$PWD/out/hammond-local"
cmake -E rename "$PWD/out/hammond-local" "$PWD/out/hammond-moved"
b3_prefix="$PWD/out/hammond-moved"
"$b3_prefix/bin/hammond_console_trace" \
  --profile "$b3_prefix/share/hammond-b3-organ/nominal.b3p" \
  --scenario partial --sample-rate 48000 --seed 0 --output "$PWD/out/installed-partial.csv"
python3 "$b3_prefix/bin/plot_console_trace.py" \
  --input "$PWD/out/installed-partial.csv" --output "$PWD/out/installed-partial.svg"
```

The [16-file component](OFFLINE_INSTALL.md) contains four native tools, the plot
script, the compiled profile, two catalogs and eight scores. Pass installed
profile/event paths explicitly after moving it; there is no source/build-path
fallback. Installation does not build missing inputs and can replace files in
an existing prefix. The benchmark, other Python evidence tools, headers and core
archive remain development-tree tools. This package is not a native audio-device
application, plugin or signed installer.

## The next development gate

Implement the staged [pedal routing/bus-excitation plan](M3_NEXT_GATE.md). First
freeze a separate contract and admit all 200 map positions into fixed storage,
preserving one-based pedal IDs, four bus identities, repeated-source branches and
five explicit disconnections. The first kernel retains 200 independent binary
connection states and returns four normalized bus-excitation values. Consume the
already shared 91-source frame; do not create a pedal oscillator bank or reinterpret
a disconnection as source zero/one.

The first linear reference fixture uses explicit caller-supplied dimensionless
coefficients. It supplies no invented four-to-two transfer, factory reactor,
resistor, physical drawbar defaults, waveform or MIDI octave. Independent
CSV-selected all-cell checks using both retained transcriptions, phase/coherent-sum oracles,
bounded processing and failure atomicity precede public Engine pedal events,
drawbar persistence and host routing. The plan separates this engineering slice
from the later loaded network and physical admission.

Continue preset latching, continuous drawbars/switching and loaded expression as
separate remaining M3 tasks. Scanner topology and its errata precede M4 production
DSP; complete dry AO-28 validation precedes cabinet fitting. Leslie 122/147
identities, real captures/holdouts and actual host/device/UI tests remain the
later M5–M9 gates in [PLAN.md](PLAN.md). Documentary wiring agreement and synthetic
audio do not establish a measured specimen match.

## Finish every change with a reviewable, durable checkpoint

The owner's standing workflow in [AGENTS.md](../AGENTS.md) is to complete necessary
checks, update the handoff, commit completed work and push to `main`, unless a
later instruction or branch protection changes that route.

1. Refresh the remote, inspect incoming changes and preserve unrelated work.
   Update status, next steps, development log, changed contracts and the correct
   session ledger with actual results, failures and unrun gates. Stage explicit
   intended paths; do not include another worker's unfinished files.
2. Inspect `git diff --cached --check` and `git diff --cached --stat`. Record
   `git write-tree`, archive that candidate and build its core, tools and tests
   together outside the mutable checkout. Run the required integration gate and
   source checks. Qualify subsequent changes according to what actually changed;
   do not silently describe a dirty-tree build as the staged result.
3. Commit and publish against the observed remote head. Use ordinary non-force
   Git publication when credentials support it. For the connected GitHub Git-data
   route, inspect current tool/account contracts, construct the exact tested tree,
   use the observed parent, and update `main` with `expected_sha` equal to that
   parent and `force: false`. Never put credentials or account tokens in files.
4. Read back the remote commit, parents and tree; compare them with the intended
   candidate. Observe that exact revision's hosted jobs through completion and
   retain the run identity, complete test counts/skips, failures and diagnostics.
   If the expected head changed, inspect/integrate it and rerun affected checks;
   do not remove the guard or force-push around another session's work.

Use [repository checks](REPOSITORY_CHECKS.md) and each ledger's current instructions
for source and assignment accounting. The original checker's
`--expected-agents 60` refers to `docs/development/agent-notes/`; it does not count
the continuation's separate workers. Preserve prior evidence and use a new
corrective/revert commit when needed. New model meanings, control laws, IDs or
saved formats require explicit identities/migrations before publication.

The scope and actual command checks for this handoff are retained in
[assignment 51](development/2026-11-13-continuation/51-operational-handoff.md).
