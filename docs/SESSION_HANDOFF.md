# Operational handoff for the next development agent

**Coordinator completion update:** all sixty original workers have completed their
assignments in ten waves of six. The final session record contains their complete
notes and current handoff. Published
`61c6ecbd87f46a91b4d0d975c823eeae2e2fb3f8` contains the demo/replay, exhaustive
routing gate, documents and final repairs through original note 56. Its exact
tree passed 26 local Release suites and 274 Python methods with zero skips.
Hosted run 43368537860 passed the same counts in all four jobs; the complete
archives and effective leak-enabled sanitizer settings were audited independently.
Incoming `7a24a30` is preserved as its
parent. That commit adds nominal contact/percussion components and model metadata,
while engine/renderer integration remains the continuation's next wave.
Preserve the final review's nearest-rounding serialization repair
when implementing the proposed `B3CONTROLS2` migration. The current
[assignment ledger](development/AGENT_LEDGER.md), [status](STATUS.md) and
[next steps](NEXT_STEPS.md) supersede this document's dated inventory for task
selection; historical execution evidence below remains attached to its revision.

## Historical wave-09 inventory and operational procedures

**Written during wave 09 on 2026-11-13.** The inspected published code is
`6c3dd8bc923a3c11f6b234425b056e135fbe9f4b`, tree
`eb41dad04f43804b42d90befdc98e47c6f651c56`. It supplies a useful nominal dry
organ and offline renderer. Wave 09 additions are local work awaiting integration;
wave 10 review, publication and final verification are still pending. This page
does not declare all 60 original assignments complete.

The next agent must refresh the revision and assignment information below before
changing code. The separate console continuation is actively developing M3, so
this dated inventory is not an instruction to restart its contacts/percussion work.

## Start by reconciling ownership and the current revision

Read [AGENTS.md](../AGENTS.md), [PROJECT_GUIDE.md](PROJECT_GUIDE.md),
[STATUS.md](STATUS.md), [NEXT_STEPS.md](NEXT_STEPS.md), the latest entry in
[DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md), [PLAN.md](PLAN.md), and the
[acceptance matrix](ACCEPTANCE_MATRIX.md). Then read both session ledgers:

- [Original session](development/WAVE_LOG.md): ten development waves, original
  assignment IDs 01–60, with actual reports in `development/agent-notes/`.
- [Separate console continuation](development/2026-11-13-continuation/README.md):
  its own assignment namespace; six completed full-atlas reviews and an active
  contact/percussion wave at this snapshot. Its commit
  `5dcd94292fbd5af61b5bf3bb7e06a1f5f2c4f181`, including the continuing-session
  rules in AGENTS, is preserved as an ancestor of `6c3dd8b`.

From the repository root, inspect before integrating anything:

```sh
git status --short --branch
git log -8 --oneline
git rev-parse HEAD 'HEAD^{tree}'
git fetch origin main
git log --left-right --oneline HEAD...origin/main
rg --files docs/development include src tests tools data
```

If remote `main` has advanced, inspect the incoming diff and newest ledger before
choosing a task. Preserve uncommitted work and all existing commits; reconcile in
an isolated checkout if necessary. Do not blindly pull into a shared dirty tree.
Agree on one integration owner, explicit file ownership and the pass evidence
before parallel edits. Workers write their assigned notes; the integrator owns
shared status, next steps, logs, staging and publication. A planned ledger row is
not evidence that its work exists or has passed.

Read the [complete review](research/ATLAS_REVIEW.md),
[errata](research/ERRATA.md) and the task's atlas chapters. The supplied
[500-page atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) remains unchanged.
Research waves, development-agent waves and implementation milestones M0–M9
are three different organizations.

## Publication and test evidence at this checkpoint

| Revision or work | Retained execution state | What a next agent may claim |
| --- | --- | --- |
| `9c8068c95f6843dce95f7f22d729738eef8074f6` | [Run 43363048563](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43363048563): all 16 suites passed in Linux/macOS/Windows Release and Linux ASan/UBSan/leaks. | Historical qualification of that offline revision. |
| `7c2ad2089f795b2147f5fc72cf10a4542d953a8c` | [Run 43364414017](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43364414017): Linux/macOS 18/18; Windows and sanitizer 17/18. [CI_QUALIFICATION.md](CI_QUALIFICATION.md) retains failures, counts, tools and archive identities. | A failed complete matrix. Later repairs do not erase its failures or establish the unobserved underlying sanitizer exception. |
| **Published `6c3dd8b`** | Integrator's completed audit of [run 43365901429](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43365901429): **21/21 suites, 257 Python methods and zero skips in each of all four jobs**; Linux/macOS/Windows Release plus Linux ASan/UBSan with leak detection. | The published offline software, including capture/factory checks, portability repairs and installation, passed this configured matrix. It does not qualify later local changes. |
| **Local work after that publication** | Agent 47's [factory runtime gate](FACTORY_RUNTIME_ACCEPTANCE.md); Agents 45–49's rights, host, navigation and acceptance documents; Agent 50's [four-second audible example](../examples/rendered/nominal-two-manual-v1/README.md); Agent 51's [independent replay](DEMO_REPLAY.md) and narrow historical-executable verifier repair. | Retain each assignment's local result and limitation. Publication, final integration and hosted qualification of these additions remain pending. Root owns integration of the verifier repair. |

Some earlier status/report paragraphs still describe a pending `6c3dd8b` audit.
The integrator owns their reconciliation and the final checkpoint update. A
workflow configuration, cached `origin/main`, successful local test, or an older
green run is not evidence that a new revision passed hosted CI.

## What exists, and where to work

This inventory describes the published revision above; compare it with current
`main` before making an absence claim.

| Area | Implementation and contracts | Present boundary |
| --- | --- | --- |
| Profile preparation | [Authoring JSON](../data/profiles/nominal-unmeasured-v1.json), [compiler](../tools/compile_profile.py), [Profile.cpp](../src/Profile.cpp), [PROFILE_FORMAT.md](PROFILE_FORMAT.md) | Validated, bounded, value-owned runtime data. Profile loading/replacement occurs with processing stopped. |
| Shared sources and dry engine | [TonewheelBank.cpp](../src/TonewheelBank.cpp), [Engine.cpp](../src/Engine.cpp), [public headers](../include/hammond/), [ENGINE_API.md](ENGINE_API.md) | 91 free-running sine sources, two manuals, coherent routing, ideal Boolean keys, sample-offset events, atomic rejection and a 64-bit render clock. Silence/disconnected output still advances source phase. |
| Console controls and save/load | [ControlState.cpp](../src/ControlState.cpp), [ControlStateIO.cpp](../src/ControlStateIO.cpp), [CONSOLE_EXTENSION.md](CONSOLE_EXTENSION.md), [CONTROL_STATE_FORMAT.md](CONTROL_STATE_FORMAT.md), [PARAMETERS.md](PARAMETERS.md) | Four retained A/B banks, hidden-bank edits, routing-only Cancel/reselection and linear expression. Saved controls exclude transient DSP histories. |
| Documentary routing | [Frozen independent CSVs and manifest](../data/references/), [FACTORY_REFERENCE.md](FACTORY_REFERENCE.md), [pedal data](../data/pedal-map.json), [PEDAL_ROUTING.md](PEDAL_ROUTING.md) | All 549 manual assignments and 200 pedal positions agree between the two readings and existing data. Pedals have 195 connections and five explicit disconnections; they have no runtime audio consumer here. |
| Offline audio and evidence | [render.cpp](../tools/render.cpp), [fixture catalog](../examples/fixtures/catalog-v1.json), [examples](../examples/README.md), [render evidence](RENDER_EVIDENCE.md), [bundle verification](RENDER_VERIFICATION.md), [PCM measurements](AUDIO_MEASUREMENTS.md) | Actual identical-channel stereo PCM16 WAVs, copied inputs, hashes, raw logs and separate float/PCM metrics. Retained-bundle verification does not run the executable. |
| Build and qualification | [CMakeLists.txt](../CMakeLists.txt), [presets](../CMakePresets.json), [tests](../tests/), [CI workflow](../.github/workflows/ci.yml), [callback audit](REALTIME.md), [numerical bounds](NUMERICAL_BOUNDS.md), [install](OFFLINE_INSTALL.md) | Framework-independent C++20 core, offline CLI, benchmark and tests. Observed allocation and finite-duration numerical checks have their own scope; they do not qualify a live audio deadline. |
| Acquisition and future product | [Capture format](CAPTURE_FORMAT.md), [validator](CAPTURE_VALIDATION.md), [protocol](CAPTURE_PROTOCOL.md), [host proposal](HOST_INTEGRATION.md), [rights inventory](DEPENDENCIES_AND_RIGHTS.md) | Planning/metadata/byte-integrity tools and proposed adapter gates. No admitted physical corpus, VST3, device-audio application or native UI at this revision. |

No scanner, AO-28 electronics, Leslie electrical/acoustic DSP, physical contact
model or percussion exists in `6c3dd8b`. Source gearing, pickup waves/levels/phases,
loading, specimen identity and physical calibration remain open. The active
continuation may change the console inventory before the next agent starts.

### Identities and compatibility boundaries

| Identity | Exact baseline |
| --- | --- |
| Source model / authoring profile | `ideal-shared-sine-v1` / `nominal-unmeasured-v1`; schema/model version 1; compiled header `B3PROFILE 1` |
| Raw authoring JSON SHA-256 | `d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff` |
| Canonical authoring SHA-256 | `49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83` |
| Compiled profile SHA-256 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Internal console registry | Schema 1, `ideal-exclusive-ab-console-v1`, 39 proposed controls; raw JSON SHA-256 `e7a7a9938ff38fbd43cb18aa9a7da482628cb41550d56fd37f9c1d3216547e8e` |
| Stable internal IDs | Upper A `0x1000–0x1008`, Upper B `0x1010–0x1018`, Lower A `0x1020–0x1028`, Lower B `0x1030–0x1038`; expression `0x2000`; selectors `0x2010`, `0x2011`. These are not verified VST3 exports. |
| Musical control serialization | `B3CONTROLS1`: 36 drawbars, two selectors, expression and two route-enable bits. No held keys, source phase, seed, clock, contact/percussion histories, physical-profile identity or native wrapper state. |

The baseline uses proposed 12-TET frequencies, ideal sines, proposed seeded phase,
nominal 3 dB drawbar steps, normalized amplitude and a linear expression surrogate.
The later factory attestation preserves the original authoring provenance and
hashes. It does not make these source or control values measured.

Keep tone IDs 1–91, physical terminals, MIDI notes 36–96 and storage indices
distinct. Manual routes use tone IDs 13–91. Supported rates are 44,100, 48,000 and
96,000 Hz; block capacity is bounded by 65,536 frames and 1,024 events per call.
Notes never restart source phase or make steady amplitude velocity-dependent.
Cancel disconnects routing without releasing keys, erasing banks or stopping time;
reselecting the same bank can therefore be meaningful. Preserve these contracts
or introduce an explicit version and migration with retained regression fixtures.

## Reproduce build, tests, rendering and installation

Commands below are procedures for a future run, not new execution claims by this
handoff author. Use a quiescent source snapshot and a new build/output directory;
do not reuse another worker's build. Requirements are C++20, CMake/CTest 3.21+
and Python 3.10+. No host SDK or downloaded audio framework is required.

In the current managed workspace `cmake` and `ctest` were absent from `PATH`.
The following matched pair was checked as version 4.4.4. In another environment,
use that environment's installed tools instead of assuming this path survives:

```sh
export PATH="/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin:$PATH"
cmake --version
ctest --version
```

Run the following from the repository root. Build before CTest: CTest does not
compile executables or generate `nominal.b3p`.

```sh
cmake -S . -B build-handoff-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build-handoff-release --config Release --parallel 2
ctest --test-dir build-handoff-release -C Release -N
ctest --test-dir build-handoff-release -C Release --output-on-failure --no-tests=error
```

The `-N` inventory identifies the current suites; do not hard-code 21 for a later
revision. CMake discovers `src/*.cpp` and `tests/test_*.cpp`/`test_*.py`. CTest
provides exact renderer/profile/source paths, including multi-configuration paths;
missing prerequisites must fail. During a focused change, select its affected
suites, then run the full integration gate once the candidate is fixed. For the
local evidence additions, the relevant selection is:

```sh
ctest --test-dir build-handoff-release -C Release --output-on-failure --no-tests=error \
  -R '^(test_factory_runtime|python_test_factory_reference|python_test_demo_bundle|python_test_verify_render|python_test_install|python_test_repository_integrity)$'
```

For MSVC, configure a new directory in a Visual Studio developer terminal using
`cmake -S . -B build-handoff-release -G "Visual Studio 17 2022" -A x64 -DBUILD_TESTING=ON`,
then use the same build/CTest `--config Release` / `-C Release` arguments above.
The executable is normally `build-handoff-release/Release/hammond_render.exe`;
the profile is still `build-handoff-release/nominal.b3p`. Single-configuration
Linux/macOS paths are used in the render examples below. See [BUILD.md](BUILD.md)
for Debug and preset equivalents.

When sanitizer coverage is affected, use a separate supported GCC/Clang build:

```sh
cmake -S . -B build-handoff-sanitizers -DCMAKE_BUILD_TYPE=Debug \
  -DBUILD_TESTING=ON -DHAMMOND_ENABLE_SANITIZERS=ON
cmake --build build-handoff-sanitizers --config Debug --parallel 2
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 \
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1 LSAN_OPTIONS=exitcode=23 \
  ctest --test-dir build-handoff-sanitizers -C Debug --output-on-failure --no-tests=error
```

The current workspace previously produced an explicit LeakSanitizer/ptrace
failure. If reproduced, retain that blocker. A separately labeled local
`detect_leaks=0` ASan/UBSan run does not qualify leaks; the hosted Linux job must
exercise `detect_leaks=1`. Do not turn a blocked or failed gate into a skip/pass.

### Quick render and retained evidence

Choose an unused WAV filename. Publication preserves existing files and requires
hard-link support on the destination filesystem:

```sh
cmake -E make_directory out
./build-handoff-release/hammond_render --profile build-handoff-release/nominal.b3p \
  --output out/handoff-dry.wav --frames 96000 --sample-rate 48000 \
  --block-size 64 --seed 0 --drawbars 888000000 --note 60 --fail-on-clip
```

For a reproducible four-second score, the parent `out/` must exist and
`out/handoff-two-manual-v1` must not exist. Keep new reports outside the bundle:

```sh
python3 -B tools/render_fixture.py --renderer build-handoff-release/hammond_render \
  --profile-json data/profiles/nominal-unmeasured-v1.json \
  --output-dir out/handoff-two-manual-v1 \
  --events examples/fixtures/two-manual-changes-v1.events \
  --frames 192000 --sample-rate 48000 --block-size 127 --seed 2601 --drawbars 006400000
python3 -B tools/verify_render.py out/handoff-two-manual-v1 \
  > out/handoff-two-manual-v1-verification.json
python3 -B tools/analyze_wav.py --input out/handoff-two-manual-v1/render.wav \
  > out/handoff-two-manual-v1-analysis.json
```

Require producer `status: succeeded`, a zero child return code, zero reported
clipping and consumer `status: verified_retained_bundle`; inspect the retained
logs and report limitations. `--events` and explicit `--note` are mutually
exclusive. The wrapper always requests `--fail-on-clip`. Do not pass a
single-frequency expectation for this polyphonic score.

The retained demo candidate can be checked read-only with:

```sh
python3 -B tools/verify_render.py examples/rendered/nominal-two-manual-v1/bundle
python3 -B tools/analyze_wav.py \
  --input examples/rendered/nominal-two-manual-v1/bundle/render.wav
```

Agent 50's WAV has SHA-256
`9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd`.
Its historical temporary renderer path is provenance, not a required future
installation location. The verifier's contract permits an unavailable historical
executable while verifying retained artifacts; a present readable executable
with changed bytes fails. Agent 51 reproduced a failure in that unavailable-path
handling under a symlink ancestor and supplied a narrow local repair plus tests.
Root must integrate and qualify it. Do not rewrite the retained manifest or
create an executable at its old path to make verification pass. Hash consistency,
replay and a matching binary do not authenticate the original invocation or
establish specimen fidelity. The [separate replay record](DEMO_REPLAY.md) retains
the clean `6c3dd8b` local Release build, byte-identical renderer/WAV/PCM/metrics,
seven new gate methods and 27 existing verifier methods passing with zero skips.
Those same-toolchain observations do not claim cross-platform bitwise identity.

### Local install and relocation

The full CTest run includes `python_test_install`; it actually installs, moves a
prefix containing spaces, compares WAV/PCM/JSON and rejects a missing profile.
For manual use, choose two absent prefixes and a fresh output filename:

```sh
cmake --install build-handoff-release --config Release --component OfflineTools \
  --prefix "$PWD/out/hammond-local"
cmake -E rename "$PWD/out/hammond-local" "$PWD/out/hammond-moved"
"$PWD/out/hammond-moved/bin/hammond_render" \
  --profile "$PWD/out/hammond-moved/share/hammond-b3-organ/nominal.b3p" \
  --events "$PWD/out/hammond-moved/share/hammond-b3-organ/fixtures/a4-fundamental-v1.events" \
  --output "$PWD/out/handoff-installed-a4.wav" --sample-rate 48000 --frames 72000 \
  --block-size 127 --seed 2602 --drawbars 008000000 --fail-on-clip
```

The default component installs exactly eight files: renderer, compiled profile,
catalog and five scores. Installation does not build missing inputs and may
replace files in an existing prefix. It supplies no Python tools, headers, core
archive, compiler runtime bundle, device backend, plugin or signed installer.
Use explicit installed profile/event paths after relocation; there is no fallback
profile discovery. [OFFLINE_INSTALL.md](OFFLINE_INSTALL.md) gives PowerShell and
custom-relative-directory equivalents.

### Data and repository checks

```sh
python3 -B tools/compile_profile.py --input data/profiles/nominal-unmeasured-v1.json \
  --output build-handoff-release/nominal.b3p --check
python3 -B tools/validate_factory_reference.py
python3 -B tools/validate_parameters.py data/parameter-registry.json
python3 -B tools/validate_capture.py --input data/capture-planned-example.json
python3 -B tools/check_repository.py --json
```

The planned capture example asserts no acquisition. `--check-files` is a separate
operation for actual recorded artifacts with an explicit artifact root; neither
metadata nor byte integrity establishes physical admission. Repository checks
validate source/data identities and local file links, not external links, review
quality, DSP behavior or agent completion. They require no build or network.

## Ranked queue: take the first unowned, dependency-ready task

Do the useful work supported by available inputs. If another session owns the
first engineering task, take independent review/test work or an acquisition task
instead of creating a second implementation. Record the selected claim, inputs,
owner, exact files and closure evidence before editing.

| Rank and task | Inputs and likely files | Required pass evidence | Blocker and compatibility boundary |
| --- | --- | --- | --- |
| **1. Finish this session's integration and wave 10 review.** | Current remote head; original ledger/notes; local factory runtime gate, demo/replay and verifier repair; acceptance/rights/host documents; shared handoff records. | Independent assigned reviews; fixed candidate tree; complete local suite and source check; publication of exactly that tree; four observed hosted jobs with actual suite/method/skip audit and retained failures. Require IDs 01–60 only after all original assignments actually finish. | Await actual remaining work and hosted execution. Root owns publication. Preserve original demo bytes, manifest and old CI results; a new revision needs its own result. |
| **2. Continue the existing M3 contacts/percussion stream.** | Newest continuation ledger, contracts/code and published history; atlas chapters 17–24, pp. 109–156. Inspect current `include/hammond/`, `src/`, `tests/` and model documents before naming new files; `Engine`, `Types`, controls and fixtures are integration boundaries. | Nine separately represented manual contacts; shared upper-manual percussion/recharge; held keys/partial release/repress, same-frame ordering, Upper B and Cancel/reselection, finite recovery, all rates, block invariance and continuous source histories. Retain the named nominal model's units, source pages and limitations. | Already actively assigned; coordinate or review the current implementation. Missing captures block measured timing/circuit claims. Preserve stable IDs, ideal-baseline compatibility where promised and separation of controls from dynamic histories; version/migrate deliberate changes. |
| **3. Close remaining M3 preset, pedal and expression gaps.** | Stable contact/percussion contract; [pedal map](../data/pedal-map.json), factory readings and source review; current `Engine`/`ControlState`, registry, state format and tests. | Explicit physical-preset latch/loading approximation; all pedal connections/disconnections and coherent duplicates; declared pedal weighting/shaping; expression units/law; held-note/switching/state tests and updated audible fixtures. | These are not completed by exclusive A/B banks or routing data alone. Use a named nominal surrogate until loading/response evidence exists. Never reuse IDs or silently change `B3CONTROLS1`, normalized laws or an existing profile's meaning. |
| **4. Advance physical reference and acquisition in parallel.** | [CAPTURE_PROTOCOL.md](CAPTURE_PROTOCOL.md), schema/planned example, rights/variant records; actual specimen, AO-28/cabinet identity, permission, rig, clocks and calibration. Files belong in versioned capture metadata and a corpus/group ledger. | Identity/permission lock; calibrated dry-source/contact/percussion/expression takes; immutable masters/hashes; independently reviewed signal boundaries and uncertainty; whole-take ancestry/duplicate/group audit and frozen untouched holdouts. | Actual hardware, qualified acquisition and permissions are missing. Keep unknowns null with reasons; never promote a plan or synthetic WAV to a recorded specimen. Avoid fitting downstream cabinet effects to compensate for an unvalidated dry organ. |
| **5. Prepare the M4 scanner reference before production DSP.** | Atlas pp. 157–192 and 465; [ERRATA.md](research/ERRATA.md); selected connectivity, loads, port conventions and one scanner-history contract. Retain reviewed graph/derivation and independent numerical-reference evidence before adding a production module. | Resolve 15-versus-16 traversal and reported WDF algebra/sign hazards; compare all 19 signed outputs against an independent loaded AC/transient formulation; test six modes, transitions, continuity and numerical stability. | Documentary/model gaps block a complete electrical claim; missing captures block specimen response. Keep one owner for scanner return/phase, units and loads. Do not import a component inventory as connectivity or double-count dry/chorus return. |

M5 needs reviewed AO-28 connectivity, active revision, transformers/loads and dry
G-G validation before cabinet fitting. M6/M7 keep Leslie 122 and 147 separate.
M8 needs actual independent holdouts. M9 needs actual plugin/device/UI code,
host/device runs, stable wrapper migrations, callback deadlines, accessibility,
resolved rights and platform packages. [HOST_INTEGRATION.md](HOST_INTEGRATION.md)
is an adapter proposal, not an implemented or executed product gate. Scoped
adapter research can proceed after stable core contracts without closing M9.

## Permanent integration, commit and push workflow

[AGENTS.md](../AGENTS.md) records the owner's standing authorization: run necessary
checks, inspect the diff, commit completed work in reviewable chunks and push to
`main`, unless a later instruction or branch protection changes that route.
Preserve another session's history and work. Do not force-push, reset away changes,
delete other workers' outputs or create unsolicited issues/messages.

1. **Refresh the remote and freeze the candidate.** Record the observed remote
   head, reconcile incoming changes, and finish affected checks. Update status,
   next steps, development log, contracts and the correct session ledger with
   actual results. Stage only intended paths and inspect the staged diff. If
   publishing the retained demo for the first time, explicitly add only its
   ignored `bundle/render.wav` and `bundle/profile.b3p`; do not broadly add build
   outputs or change ignore rules to capture arbitrary generated files.
2. **Test the exact staged tree.** Record `git write-tree` and build an isolated
   archive of it. A dirty working-tree build cannot establish that the staged
   publication contains every required file. Repeat only the checks affected by
   a subsequent candidate change, plus the required final integration gate.
3. **Commit and publish against the expected head.** Use ordinary non-force Git
   publication when credentials support it. This session's continuation reported
   no direct Git-push CLI credential; it used the connected GitHub Git-data tools.
   Inspect current tool contracts and the repository account rather than assuming
   that access still exists. The current API path is described below.
4. **Verify what reached the remote.** Read back `main`, the resulting commit's
   parents and tree, and compare them with the intended revision/tree. Observe
   that revision's CI run through completion. Keep configure/build logs, complete
   `LastTest.log`, JUnit, toolchain/revision files, artifact hashes and count/skip
   audit. Hosted diagnostics currently have 14-day retention; retain needed
   evidence promptly. A push success or a run for another SHA is not a CI pass.

An exact staged-tree check can use these POSIX commands after intentional staging
has finished. Stop on a nonzero command result. The archive is temporary, and its
source files must remain unchanged during the run:

```sh
git diff --cached --check
git diff --cached --stat
b3_candidate_tree=$(git write-tree)
b3_snapshot=$(mktemp -d "${TMPDIR:-/tmp}/hammond-handoff.XXXXXX")
git archive "$b3_candidate_tree" | tar -x -C "$b3_snapshot"
cmake -S "$b3_snapshot" -B "$b3_snapshot/build" \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build "$b3_snapshot/build" --config Release --parallel 2
ctest --test-dir "$b3_snapshot/build" -C Release --output-on-failure --no-tests=error
python3 -B "$b3_snapshot/tools/check_repository.py" --root "$b3_snapshot" --json
```

Only at actual original-session closure, run the checker on that same candidate
with `--expected-agents 60`. It requires exactly IDs 1–60 in the original direct
agent-note directory. It does not count the continuation's six reviews as new
original agents or verify the truth of their reports.

For the connected GitHub publication route, use the repository
`tomasedisonn80/Hammond-B3-Organ` and the verified account's `link_id`. Do not place
credentials or account tokens in the repository. The currently exposed tools
have these relevant fields:

| Tool | Required publication relationship |
| --- | --- |
| `github_create_blob` | Upload intended file bytes using `content` and `encoding: utf-8` or `base64`; preserve binary WAV/profile bytes. |
| `github_create_tree` | Use `base_tree_sha` from the observed remote head and explicit `tree_elements`; preserve every unrelated path and mode. Compare the returned tree with the tested candidate. |
| `github_create_commit` | Use the tested `tree_sha`, observed `parent_sha`, and a reviewable `message`; preserve any intentionally required additional ancestry through `additional_parent_shas`. |
| `github_update_ref` | Use `branch_name: main`, `sha: <new commit>`, **`expected_sha: <observed remote head>` and `force: false`**. Read back the branch/commit/tree after success. |

If the expected head is rejected, fetch/read the new head, inspect and integrate
its work, rebuild the candidate and rerun affected gates. Do not retry by merely
changing `expected_sha`, removing the guard or enabling force. The separate
continuation already advanced `main` during this session; this is an observed
collaboration requirement, not a hypothetical cleanup task.

Rollback uses a new reviewed corrective/revert commit and the same verification
and publication process. Retain old reports and immutable input bundles. A model,
profile, serialized-state, control-law, signal-boundary or acquisition change must
name which earlier claims it invalidates. Preserve readable prior state through
an explicit migration or declare incompatibility before publishing the change.
No project-wide license is selected; the [rights inventory](DEPENDENCIES_AND_RIGHTS.md)
and [notices](../THIRD_PARTY_NOTICES.md) remain distribution gates.

The scope of the authoring checks for this page is retained in
[Agent 53's note](development/agent-notes/53-session-handoff.md). They are source,
identity, CLI-contract and link checks; this documentation assignment performs
no new full build, DSP run, hosted matrix or physical acquisition.
