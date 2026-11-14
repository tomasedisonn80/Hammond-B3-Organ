# Development log

## 2026-11-14 — Begin native interface continuation from published preset source

Inspected published `main` at `d493e998e5dd7cf44db46854e87309745063ac54`
and created a separately owned lightweight source checkout. Six actual readers
completed every atlas page in disjoint ranges and retained exact page anchors
and selected original visual inspections. Established a new sixty-worker,
ten-wave manifest and [bounded M9 scope](INTERFACE_CONTINUATION_SCOPE.md).

The baseline combined Release build passed 136/136 tests in 155.19 seconds with
GCC 14.2.0, CMake 4.4.4 and Python 3.12.14. SDL2/RtMidi dependencies were reused
without copying SDKs per worker. Initial configuration lacked ALSA development
paths; specifying the existing sysroot exposed a pinned SDL/local ALSA signature
incompatibility. The retained corrected local configuration disables SDL ALSA
and uses dummy audio/video for acceptance; RtMidi ALSA remains compiled. The
[baseline record](development/2026-11-14-interface-continuation/reports/baseline.json)
retains exact source, binary and test identity. No physical device pass follows.

Observed published hosted results: Linux and macOS core, Linux sanitizer,
Linux/Windows standalone and all native VST3 jobs succeed. Windows core fails
in Python's `ctypes.CDLL(None)` rounding-environment setup; macOS standalone
fails one MIDI modal replay after an observed long event-delivery gap. Preserve
these failures and repair their causes before claiming current platform success.

## 2026-11-14 — Implement the exclusive fixed-registration path

The reviewed M3 selector now has immutable generated rows, retained A/B/Cancel
memory, phase-preserving core routing, upper-B percussion eligibility, state4
with legacy readers, append-only 47 parameters, exact new-selector binary64
conversion, raw StateExchange/Session transport, host anchors and 24 native preset
keys. Independent source, lifecycle, persistence and numerical checks retain
focused evidence in the [current session](development/2026-11-14-preset-continuation/README.md).
Native VST3 passes 8/8 suites and the offline validators pass 107 methods in 3/3 suites.
Initial failures and source identities remain in their individual records.
The renderer has actual three-size captures; final gallery/refinement and
integrated/platform gates remain pending. These changes are a development overlay
until a later publication record names their exact tree.

The published macOS startup repair at 35554c0 passes startup and installation.
The remaining 22/24 native result contains two replay failures, retained with
copied diagnostics and job identities for explicit diagnosis; ten other hosted
jobs pass. No unqualified unchanged retry is counted as a repair.

## 2026-11-14 — Repair macOS comparison of new output paths

The hosted renderer compile repair passed compilation and exposed a distinct
startup path-identity failure at `352a398`: macOS returned Operation not supported
when comparing absent output leaves. Calls to file equivalence now require two
existing leaves; canonical path equality still rejects future-file aliases.
Strict local compilation and all 18 actual native acceptance methods passed,
covering 164 child launches. [Failure and repair evidence](development/2026-11-14-preset-continuation/BASELINE_PATH_REPAIR.md)
retain the exact source and limits; hosted macOS verification follows publication.

## 2026-11-14 — Repair observed hosted macOS baseline build

The new source/contract checkpoint `70b3354` exposed an existing unused private
`kDark` constant in the native renderer under AppleClang's strict warning policy.
Removed only that unreferenced declaration. A coherent copy of the published
baseline reproduced the failure with strict GCC object compilation and passed
after removal. [The actual hosted failure and local check](development/2026-11-14-preset-continuation/BASELINE_MACOS_REPAIR.md)
remain distinct from the pending hosted repair qualification and in-progress
47-parameter preset work.

## 2026-11-14: fixed-registration continuation and complete source reading

Started from verified remote main `b79086f6bb0c42b97130c721c5c73c7c97a13887`
in an isolated checkout, preserving other working copies. Six new readers
covered all 500 unchanged PDF pages and selected diagrams;
[coverage and source findings](research/PRESET_ATLAS_REVIEW.md) support the
next M3 exclusive selector and M9 preset-key controls. The user requests sixty
actual agents in ten logical waves; [the new manifest](development/2026-11-14-preset-continuation/assignments.json)
records only dispatched identities and actual accepted results.

The baseline configured and built with CMake 4.4/GCC and passed 113/113 SDK-free
Release suites in 70.65 seconds. The retained
[baseline record](development/2026-11-14-preset-continuation/reports/baseline.json)
and complete test output give exact commands and source scope. Combined native
SDL/RtMidi/VST3 inputs were built using existing pinned checkouts; separate
actual native baseline qualification follows. No physical-device or hardware
fidelity result is inferred.

Independent design fixes typed fixed versus adjustable identities, retained
Cancel memory, source/owner/history continuity, the two upper-B eligibility
sites, canonical state 4 with all older readers and 47 parameters preserving the
first 45 records exactly. A direct source-read test fixture covers 18 rows/162 taps.
Production implementation follows contract freeze; current plans are not tests.


## 2026-11-14 — Integrated native MIDI replay, package and typography gates

Completed the first five logical waves and accepted the separate A31 native
replay assignment. The actual manifest now records 31 accepted workers; later
wave-six work remains in progress. Added bounded `B3MIDIREPLAY1` admission and
native delivery, schema-2 diagnostics, independent CLI/modal and musical replay
acceptance, preserved legacy workflow fixtures, exact 13/17-file installation,
the operational guide and a source-identified four-image initial gallery.
The reproduced small-glyph defect failed 48 isolated cases before repair and
passes all 144 after the final per-axis transparent-gutter correction. The first
broader-padding candidate was visually rejected despite its passing unit tests.

The [integration record](development/2026-11-14-midi-ui/reports/checkpoint3-integration.json)
retains all commands/logs, 280 source/test hashes, executable identity and the
original failure. The complete default run passed **112/113 suites in 212.30 s**;
the sole repository-integrity failure identified a wrong source-relative notice
link and a concurrently unfinished CI note. Correcting that link and completing
the note passes the unchanged affected suite **1/1 in 3.02 s**. The original full
result remains intact. The native gate passes **23/23 in 98.69 s**. A31's newly
registered independent application suite then passes **1/1 in 18.43 s** on the
same final executable, covering 11 methods and 12 native processes. Only that
CTest registration changed among the earlier 280 source/test inputs; compiled
production inputs stayed unchanged.

The hosted workflow now requires actual ALSA/CoreMIDI/WinMM builds and one Linux
MIDI-disabled build, exact prepared-source/font/reference identity, native-test
discovery and 13/17-file relocated packages. Local syntax, configuration,
File API and actual RtMidi ALSA library checks pass; hosted execution remains
pending until publication. The new handoff and README expose current setup,
actual UI captures, remaining visual differences and concrete continuation.
Physical device, deadline, accessibility and full reference-equality gates stay
separate. Original galleries and all preceding session records are preserved.

## 2026-11-14 — Initial MIDI implementation and reference renderer

Implemented the frozen optional MIDI queue/decoder, exact-port transport, shared desired-control bridge, three owner scopes, native settings dialog and bounded main-thread draining. The reference renderer now uses verified decorative RGB assets with live controls and shared resize geometry. All 45 public sound parameters, core sound behavior and `B3CONTROLS3` remain unchanged. The first 18 actual workers completed source, contract and implementation work; the live manifest records later independent acceptance separately.

Default and prepared-ALSA Release configurations each passed the three decoder/UI/control-bridge suites (3/3, 0.02 s); [exact intermediate identities](development/2026-11-14-midi-ui/reports/midi-support-stage.json) distinguish this worktree from its base commit. A18 independently passed four musical integration suites with real Session/Engine comparisons. The root integrated A20's unchanged-adapter fake dependency target and passed both ordinary and intentional-quarantine CTests (2/2, 0.02 s). Ordinary resource-balance and quarantine tests remain separate; normal LeakSanitizer execution is blocked by this executor's ptrace environment, while explicitly limited ASan/UBSan checks pass with leak detection disabled.

The complete native application built and passed actual SDL dummy-device/window smokes at 1672×941, 1280×900 and 960×700. [Initial capture identities](development/2026-11-14-midi-ui/reports/native-initial-captures.json) retain the source, binary, commands and pixel identities; A17's note records the exact boundaries. Actual `--list-midi` returned the ALSA `/dev/snd/seq` absence honestly, before SDL initialization. The MIDI settings capture displays that same error; it is not a passing controller test. A21's [independent visual review](reviews/MIDI_UI_REFERENCE_REVIEW.md) verifies dynamic control/key inventory and identifies a reproducible small-glyph raster defect for correction. Literal pixel equality is not claimed.

This is a reviewable implementation checkpoint. Existing native workflow fixtures still need explicit schema-2/layout reconciliation; synthetic native MIDI replay, packaging, hosted qualification, typography correction, final captures and the remaining requested waves are ongoing. Source/build notes retain earlier results rather than promoting a subset test or synthetic transport to a physical gate. Local native preparation explicitly disables SDL's ALSA backend because the available ALSA 1.2.14 development headers conflict with pinned SDL 2.32.10's old signature; the separately enabled RtMidi ALSA backend compiles. Hosted real platform-backend gates must remain enabled.

## 2026-11-13 local time — MIDI/UI continuation: source and baseline

New session `2026-11-14-midi-ui` (UTC storage date) begins at `0f7b90037e51e101d8fa0bfe31af40209d751659`. Six newly dispatched workers read every word on all 500 PDF pages in disjoint ranges and inspected selected figures; the [consolidation](research/MIDI_UI_ATLAS_REVIEW.md) and six substantive notes retain findings. Extracted the original cover/page409 JPEG without alteration and recorded its exact source/hash. The next dependency-ready M9 slice is external MIDI input and reference-led native UI refinement under [MIDI_UI_SCOPE.md](MIDI_UI_SCOPE.md).

Built baseline Release using GCC 14.2.0 and CMake 4.4.4; configured `BUILD_TESTING=ON`, no optional SDKs. `cmake --build build-baseline -j4` succeeded and `ctest --test-dir build-baseline --output-on-failure --no-tests=error -j4` passed 106/106 in 59.50 s. The [baseline record](development/2026-11-14-midi-ui/reports/baseline.json) and complete test output identify this existing code scope. No new MIDI/device/visual pass is implied. Updated permanent future-agent instruction to preserve the reference, publish actual native screenshots, keep status/next steps current and commit/push verified completed work.

## 2026-11-14 — Complete calibration records published and fetched

- Published `02810eb0724d7fe53ce6fda945772fac84589c78`, tree
  `f5696578f070587e8e2692dd845ed4f2cfff2eec`, with expected previous d7 and
  no force update. Root fetched main and verified exact equality with local
  `5302581`, a clean worktree and all five complete/qualified/concurrent ancestors.
  Local source history is preserved on `calibration-local-complete-60`.
- All sixty actual accepted records, the strict completion output, final source
  integrity, operational/acquisition guides and permanent AGENTS workflow are
  included. The post-record integrity check passes 623 Markdown files / 3,502
  local links; strict sixty-complete accounting also passes. No runtime or
  CaptureTools payload input changes from the all-ten-success d7 source.
- This final documentary receipt retains the actual observed publication in
  the integration record, handoff, session README and publication JSON. Its own
  subsequent commit records that event; inspect actual HEAD before new work.
  Continue the identified pilot/acquisition inputs and independently owned
  software contracts. Physical instrument and complete product gates stay open.

## 2026-11-14 — Complete immutable archive passes final record gates

- Fresh complete source `79bcc28`, tree `6f84cac7`, passes strict sixty-complete
  accounting and source-archive integrity with zero errors and empty stderr.
  All 1,041 files / 40,663,711 bytes remain unchanged. The actual integrity
  output checks 623 Markdown files / 3,498 local links, source PDF/chapter identity
  and named data relationships. Both exact outputs and hashes are retained.
- The equal-tree public source is be9479d8b0647705c92f9d599be09bac22402296,
  prepared as a child of qualified d7 and retained in the final publication.
  All 29 d7-to-complete changes are documents/records; all 56 CaptureTools inputs,
  installer and top-level CMake are unchanged. This is not a new full-suite run.
- The final integration record binds the actual complete source, independent
  final reviews, original failures and concrete next inputs. Root will finish
  the expected-head non-force publication and fetched commit/tree/ancestry
  verification, preserving all concurrent history and local source checkpoints.

## 2026-11-14 — All sixty actual calibration assignments accepted

- Accepted assignment 60 after reading its complete review, checking both frozen
  identities and compiling its Python example. Its source/payload/ancestry,
  complete-reading coverage, 683-link and standing-rule checks find no new
  production or operational blocker. Its original 58-complete snapshot and
  later root-attributed acceptance remain distinct from actual final closure.
- All sixty real rows are now complete in ten waves, with no planned/running
  identities. Root reconciled STATUS, NEXT_STEPS, handoff, session README,
  project navigation and AGENTS with that actual result and the next A1–A6
  inputs. The strict checker output is retained after acceptance, not inferred
  from requested counts. Whole-project physical/product gates remain open.
- The final root integration record preserves full106 and hosted d7 sources,
  nested capability limits, original failures, practical commands and guarded
  publication requirements. Complete documentary-source verification follows
  on the committed immutable snapshot; no new full runtime gate is claimed.

## 2026-11-14 — Accepted independent completion-accounting review

- Accepted assignment 59's fixed 6242c6d review: its actual expected-56 gate
  passes and premature expected-60 gate fails honestly. The current manifest
  now has 59 accepted workers; the final worker is still running.
- Independent checks cover every extracted source blob, 56 then-accepted notes,
  164 ownership references / 153 distinct paths, five separate-session identity
  sets, full 500-page coverage / 31 image declarations, original PDF bytes, four
  exact local/public mappings and five source ancestries. Historical counts are
  retained and are not silently rewritten to current completion.
- Root read the review, verified both frozen hashes and compiled its Python
  example. Earlier README corrections are retained and attributed. This is
  accounting/provenance evidence, not another full suite or launch attestation.

## 2026-11-14 — Accepted actual newer-runtime and context qualification

- Accepted assignment 58 after reviewing its frozen evidence and compiling all
  three retained Python examples. Actual CPython 3.13.5 passes the unchanged
  nine-method pipeline with 71 tool children, no failures/errors/skips.
- A separate twelve-process 3.12.14/3.13.5 matrix retains four exact own-runtime
  matches and four expected cross-runtime mismatches with identical sources.
  Failed/inconclusive engineering outcomes and every original input remain.
  An explicitly bounded runtime projection diagnoses the difference but never
  replaces full-byte public replay. The initial harness syntax error is retained.
- This is finite Linux runtime evidence, not a full 3.13 gate or execution of
  the declared 3.10 minimum. No production, test or package input changed.
  The manifest now has 58 accepted assignments and two final reviews running.

## 2026-11-14 — Final code passes all ten hosted jobs

- Accepted assignment 55 after reviewing its frozen evidence and independently
  fetching all ten completed/success job records at exact d7f6100. Four actual
  core diagnostic ZIPs match API size/digest and embedded source; all contain
  the exact 106-name test selection. Linux/macOS/Windows Release and Linux
  ASan/UBSan/leaks each pass 106/106. Standalone passes 14/14 on each platform;
  VST3 passes 8/8 Linux and 7/7 macOS/Windows.
- Actual Windows diagnostics run the pipeline 9/9, metadata 24/24, graph 7/7
  and demo 43/43 without skips; installation runs 16 methods with only its
  existing POSIX DESTDIR exclusion. The binary-copy preservation repair now
  has observed Windows evidence. Earlier failures remain unchanged history.
- Fixed the two README composition/readiness continuation pointers found by
  accounting review and updated the current M8 acceptance row and practical
  project navigation. The final complete code and CaptureTools payload inputs
  remain unchanged; these are documentation/record changes.
- All sixty workers are now actually dispatched, with fifty-seven accepted.
  Runtime-context, accounting and final independent review finish the last wave.

## 2026-11-14 — Accepted practical handoff and complete milestone reconciliation

- Accepted actual assignments 56/57. The independent guide review passes nineteen
  CLI processes, twenty-four option checks and fifty-eight links; it retains an
  initial harness-only usage-exit correction and requires no guide/code repair.
- The M0–M9 reconciliation checks forty-eight actual code/build/data/test files,
  source equality and ancestry, 91 source records / 45 controls / 18 chapel rows,
  the zero-asset planned capture and the unchanged PDF. Its seven continuation
  rows preserve actual subsystem ownership, the scanner G5 failure, nominal dry
  Engine scope and separate physical/product gates. No runtime pass is inferred
  from source inspection. Both records are linked from the current handoff.
- Fifty-six assignments are accepted, with fifty-nine actual workers dispatched.
  Fresh Windows, actual CPython 3.13 and final accounting reviews continue;
  the sixtieth worker remains planned until actual dispatch.

## 2026-11-14 — Published qualified code and completed nine calibration waves

- Guarded non-force publication d7f6100 preserves concurrent 7ec79fb and both
  exact tested source ancestors d377fab7/5e19022c. Root fetched the commit,
  verified tree 0140c737 against local `2671fa5` and checked all three ancestries.
  The published checkpoint contains 52 accepted records; later reviews remain
  distinct from its exact snapshot and full 106-suite source.
- Accepted assignment 53's acquisition plan: A1–A6, concrete physical input/disposition
  requirements, actual global/subset limits and supported-format boundaries;
  eleven actual CLI checks and 32 source identities remain its finite evidence.
- Accepted assignment 54's source/report audit: 20 check groups, 22 fresh CLI processes,
  thirteen complete summaries (eight matches/five expected source mismatches),
  and one noncanonical rejection. All three original/final analyses agree only
  under the explicitly bounded four-source-array projection; public replay
  remains full-byte and does not relabel old reports as matching. Root compiled
  all four frozen Python examples after the retained escaping correction.
- Nine waves / 54 workers are accepted; 57 actual identities are dispatched.
  Fresh platform, operational and whole-project handoff reviews continue.
  Publication is held while final-source hosted jobs execute.

## 2026-11-14 — Accepted operations and preserved final standalone hosted evidence

- Accepted assignment 52's runbook and fifteen actual command checks, including
  four exact replay outcomes and original-output preservation. Linked the guide
  from the repository README and calibration handoff without changing the
  57-file package inventory. The manifest has 52 accepted / 55 actual workers.
- Inspected the concurrent 7ec79fb documentation-only closure and preserved all
  ten changed paths, successful hosted records at 272 and next M9 contracts.
  Those 103-suite outcomes remain separate from this new 106-suite source.
- The merged a77eb83 archive passes 41/41 repository-integrity methods in
  2.459 seconds. Its production, tests, build, model and data bytes are unchanged
  from the full qualified 48a1907 source. Assignment 55 owns fresh hosted review
  after the next guarded publication; root will hold publication while it runs.

## 2026-11-14 — Preserved concurrent standalone completion and accepted setup compatibility

- The expected-head publication guard detected `27209a7` before changing main.
  Root inspected its 28 paths, merged all completed standalone records and
  current M9/PLAN instructions, preserved both logs, and retained the already
  qualified binary-copy installation fixture. No production/test/build/model
  bytes differ between merged `346d4ea` and the 106-suite calibration source.
- Its own fresh archive passes 16/16 installation methods in 6.207 seconds and
  41/41 repository-integrity methods in 2.434 seconds. The full gate remains
  attributed to exact `48a1907`; the affected documentation/install gates are
  separately retained in the wave-8 integration report.
- Accepted assignments 50/51: fresh setup completes 51 commands and 15 grouped
  checks, including exact 57+23 co-installation, relocation and public workflows
  after private source/build deletion. Compatibility completes 18 cases against
  158 identified files and reproduces the raw Git-filter repair independently.
  Core/VST3/control/state/profile identities and the original PDF are preserved;
  concurrent standalone changes are explicitly retained and attributed.
- The calibration manifest now records 51 accepted assignments and three running
  workers. Operational/acquisition guides and final report-identity review finish
  wave 9 before the six actual final-wave assignments.

## 2026-11-14 — Qualified combined calibration source and accepted hosted review

- Fresh immutable source `48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a`, tree
  `3edea0838b75feb06c19e151ec8539e80646fc03`, configures, fully builds and
  passes **106/106 unfiltered SDK-free Release suites in 192.51 seconds**.
  Its equal-tree GitHub source is `5e19022c8696023bb1aa841ebea2eaeec0d719a3`.
  [The integration record](reviews/CALIBRATION_WAVE8_INTEGRATION.md) retains
  actual commands, log identities, source mappings and excluded scopes.
- Accepted actual assignment 49's completed hosted review at `3b0979b`:
  nine successful jobs, one Windows installation-fixture failure. Four actual
  diagnostic ZIPs match GitHub SHA-256/size and embedded revision. Windows
  demo passes all 43 methods without skips; replay and platform capability
  counters are explicitly retained. Its full job log equals root's earlier
  capture, resolving the temporary metadata-lag uncertainty.
- The independent affected-installation check passes 1/1 from immutable `c352d68`;
  root's separate full installation run passed 16/16. Both remain Linux evidence.
  The new full source includes that repair and the actual stream-boundary fix;
  observe its next real Windows run after publication.
- The manifest records 49 accepted workers and three running assignments;
  clean setup, compatibility and the operating guide are in progress. The
  historical full-gate snapshot keeps its own 48-accepted/51-dispatched counts.
- Added a dated CaptureTools distribution inventory after compatibility review
  found the existing rights handoff omitted the new source-only component.
  Existing project/PDF rights decisions are unchanged and no license is invented.

## 2026-11-14 — Completed calibration wave 8 and retained portability repairs

- Accepted actual assignments 43–48: a minimal metadata allocation change with
  retained before/after reports and independent 357-method acceptance, seven
  graph methods covering 43 complete audits, a real-pipe process repair with
  nine independent methods/71 child processes, and 30 evidence-boundary audit cases.
  The session now has 48 accepted workers in 8 complete logical waves.
- The original pipe matrix retained 24 failing subcases; a first producer candidate
  then failed the generator's independent-script contract. Both failures are
  retained. The final guard preserves all 228 existing top-level definitions and
  standalone generator/validator dependencies; no numerical policy changed.
- Hosted `3b0979b` has 9 successful jobs and one Windows Release failure: 102/103 suites.
  The prior demo defect is resolved; the installation fixture expected LF from a
  native CMake text writer. Root's c352d68 copies literal binary marker bytes
  instead; all 16 installation methods pass from that frozen archive in 6.133 s.
  The exact repaired test SHA is c7731f8bbcec56ed65243bb483cf59031048d978ebd0b9a7582ea6a429ea3602.
  Native Windows requalification of the new fixture remains pending.
- Root proved Git text-auto filtering changed valid raw float32 bytes `410d0a3f`.
  Marking `*.f32` binary preserves the exact blob; original demo/PDF bytes are unchanged.
  [The byte-identity record](reviews/CALIBRATION_RAW_GIT_IDENTITY.md) retains
  the before/after evidence. No artificial physical measurement was introduced.
- Updated the acquisition protocol's stale future-tooling/current-task pointers
  and led the handoff with verified `3b0979b` while retaining older source mappings.
  Fresh setup, compatibility and actual hosted-outcome review continue in wave 9.

## 2026-11-14 — Published complete session and all final hosted gates passed

- Published `27209a7fec075b082aa911c9ea2159938deaae85`, tree
  `087d81ba1ea83834e866ab47cdd44a53fd9251ec`, with expected parent 3b and no force
  update. This is the exact tree of local `9b68f776`; root fetched it, compared
  trees, verified a clean worktree and preserved local history on
  `standalone-local-completed-session`. All sixty substantive assignments and
  their final evidence/handoffs are included, with concurrent calibration intact.
- All three workflows and all ten jobs at that exact source are observed
  completed/success: CI `43537087807`, standalone `43537087781` and VST3
  `43537087764`. Core Release on Linux/Windows/macOS and Linux sanitizers/leaks
  each pass **103/103**; native standalone passes **14/14** on each platform;
  VST3 passes **8/8 Linux / 7/7 Windows/macOS**. Full decoded logs were retrieved;
  public identities, durations and retained log hashes are in the
  [closure results](reviews/STANDALONE_CLOSURE_HOSTED_RESULTS.json).
- Downloaded the actual Windows core diagnostic artifact 14090826655, verified
  its 57,055 bytes/SHA-256 and matching source identity, and read the CTest XML.
  The install case ran: 16 internal methods, **15 passes and one existing POSIX-only
  DESTDIR skip**. The corrected late-abort preservation method passes. The outer
  Windows gate has 103 tests, zero failures/disabled/skipped cases and 181.38
  seconds wall time. The original 3b 102/103 failure remains retained.
- Updated current handoffs, status, next steps, README and release assessment
  with the completed gate. The 621 actual standalone package audit, 183 local
  110-suite gate and local native ASan/UBSan scope keep their original identities.
  This follow-up records evidence only; it changes no tested code or dependency.
  Continue external MIDI, native semantic accessibility and typed fixed-preset
  selection under the documented ownership and physical-evidence boundaries.
- The evidence-only follow-up passes `git diff --check`, the strict sixty-agent
  checker, and source integrity for 583 Markdown files / 3,236 local links with
  the original PDF identity. All ten job records and all three workflow records
  agree on the exact tested source; no temporary artifact download URL is saved.

## 2026-11-14 — Final concurrent integration and package fixture correction

- Preserved calibration publication `3b0979b` and completed standalone closure
  in local merge `3e1a6cdec048d2b3926457cb2e20a6c4e7dedaa5`, tree
  `4c2f1f6c9e31e364029cbc13ebb53165fc1be062`. Shared status/log conflicts retain
  both tracks' complete records. All standalone, core and plugin implementation
  inputs match the 621 checkpoint; the new CaptureTools component remains
  separate. No additional agent is counted.
- From the immutable 993-file merge archive, root executed
  `python3 -B tests/test_capture_replay.py -v` and
  `python3 -B tests/test_capture_install.py -v`: **69/69** and **16/16** passed,
  respectively. All source files remained unchanged. These are focused suites,
  not an invented new full native-enabled gate.
- Actual 3b Windows core job `132262885865` passed **102/103**; its sole failure
  compared LF sentinel bytes with CMake's native CRLF write in the intentional
  late-install-abort fixture. Root removed the sentinel newline in both the
  fixture and expected bytes. Rejection, diagnostics, partial-package counts,
  copied bytes and capability policy remain unchanged; no production code changed.
  The exact frozen one-test overlay passes all **16 methods** with zero skips
  in 6.262 seconds (6.405 recorded process time). Original failure, source and
  log identities are retained in the
  [concurrent integration report](reviews/STANDALONE_CONCURRENT_CALIBRATION_INTEGRATION.md).
- Reconciled current M8 acceptance/next steps with implemented replay and package
  installation. The older Windows demo repair is now explicitly closed at 621;
  the new package fixture's hosted recheck is a separate forthcoming gate.
  Final standalone accounting remains sixty accepted assignments in ten waves.
- Before publication, `git diff --check` passed; the strict 60-assignment check
  passed again with no pending rows. Source integrity passed 583 Markdown files,
  3,229 local links and the original 500-page PDF identity. The calibration
  component include is the only top-level CMake change from 621; all tracked
  standalone/core/plugin implementation paths compare equal.

## 2026-11-14 — All sixty standalone assignments accepted

- Accepted assignment 60's complete final platform/artifact audit. All ten jobs
  at `6214032f` succeeded: core Release on three platforms and Linux sanitizers/
  leaks each 101/101, standalone 14/14 on each, and VST3 8/8 Linux / 7/7
  Windows/macOS. Root independently fetched all completed job states and
  rehashed all six actual downloaded standalone ZIPs. The audit retains all
  27 installed file identities, complete corrected notices, platform modes and
  the separately downloaded Windows core diagnostics.
- Actual relocated Linux replay uses the downloaded ELF, empty PATH, explicit
  dummy drivers and a Unicode/space directory: 238 callbacks / 121,856 frames,
  four On/four Off, final sequence 9, every original owner/prefix, preserved
  controls/inputs and joined empty shutdown with zero reported faults. Native
  Windows/macOS execution remains the named hosted scope. Capability skips,
  runtime floors and signing/physical limits stay explicit in the report.
- The final strict standalone checker passed with **60 dispatched / 60 completed,
  ten complete waves and zero running, blocked or undispatched assignments**.
  Its actual output is retained in `completion-check.json` in this session's
  directory. The preceding source-integrity check passed 564 Markdown files /
  3,156 local links and the unchanged PDF; later integrated files need their
  own final source check. Original-session consistency counts are not reused.
- Reconciled README, AGENTS, plan, status, operational handoff, next steps and
  acceptance/release assessments. Every future agent must inspect current
  ownership/source, complete meaningful checks, preserve failures and physical
  limits, update durable context, commit/push authorized work and verify the
  guarded remote result. This sixty-agent session is complete; successor work
  is concrete in the handoff and does not fabricate another dispatch.
- Before closure, fetched concurrent calibration `3b0979b`, which adds qualified
  report replay, a separate CaptureTools package, resource profiling and accounting.
  Its own local 103-suite result is separately named. Its delta preserves all
  standalone source and adds only a separate installation include to top-level
  CMake. Root is integrating that accepted remote work and validating affected
  inputs before the final guarded documentation publication.

## 2026-11-14 — Final standalone code and completed local qualification

- Published final test-source candidate
  `6214032f3565f9e221fcf3988e33a22a73bb4ea8`, exact tree
  `10f070c54d176571f1919d8141d24dd82db0e41c`, with expected parent
  `183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e`. Root fetched and compared exact
  trees, verified the index and preserved local source history on
  `standalone-local-final-oracle-code`. No force update was used. Its delta
  contains only the independently reviewed workflow and demo test corrections;
  production, CMake and installed payload inputs are unchanged from 183.
- Root's fresh 957-file combined 183 archive passed **110/110 native-enabled
  Release suites in 130.339 seconds**, explicit nine-file installation and source
  integrity: 554 Markdown files / 3,066 local links, with unchanged PDF bytes.
  Every Git blob/mode remained intact. The Release app is byte-identical to the
  named chapel demo binary. See the
  [combined final gate](reviews/STANDALONE_COMBINED_FINAL_GATE.md); it does not
  silently qualify the two later test changes or claim all Python capabilities.
- Accepted assignment 55's complete final native qualification. Original 0085
  Release remains **105/105**; the first instrumented group retains **13/14**
  with a chapel sample assertion. The chapel-only repaired group retains a
  second **13/14**, with two general workflow sample assertions. Literal applied
  command prefixes plus explicit bounded endpoints replace those particular
  sample requirements, preserve original scripts/timeouts/controls/counts/state
  bytes and retain bounded failure diagnostics. Focused Release and ASan checks
  pass, followed by **14/14 ASan/UBSan native suites in 117.292 seconds** with
  25 workflow processes and 22 chapel auditions. All 213 instrumented objects,
  five archives, ten runtime executables and generated inputs match before/after;
  the separate CTest driver preserves every original setting after the frozen
  source substitution. No local leak-detection pass is inferred.
- Accepted assignment 58's independent portability investigation and one added
  Unicode-path/StringIO regression. It preserves the calibration authors'
  producer fixes, all 41 original Windows failure/error records and the first
  correctly rejected authored fixture. All four affected suites pass locally:
  210 methods, 208 passes and two existing capability skips. Real text-wrapper
  and ancestor-alias counterexamples fail on original source and pass repaired
  source; these Linux probes do not substitute for Windows execution.
- Windows core at 183 then passed the four capture suites but retained **100/101**:
  the newly integrated demo fixture compared native symlink target spelling
  with its creation argument. Root recorded the actual target before the call,
  required its exact preservation afterward and added same-lstat metadata
  checks, retaining rejection/type/absent-target assertions. The frozen 43-method
  demo suite passes; a real relative-target counterexample fails the old fixture
  and passes the correction. No producer or new skip changed. See the
  [final portability repair](reviews/STANDALONE_FINAL_PORTABILITY_REPAIR.md).
- Accepted assignment 59's independent producer AST, stream/error, sampled-state,
  diagnostic retention, Windows link-preservation and operational recipe review.
  Concrete negative controls remain sensitive to wrong ownership, early/backward
  application, incomplete acknowledgments, altered controls and device epochs.
  It verifies all 57 benchmark inputs and selected chapel-demo source identities.
- All sixty actual assignments are dispatched; 59 are accepted at this entry.
  The final actual hosted/package audit is assignment 60. Its source-specific
  results, artifact bytes and final session acceptance are recorded separately.
  Current handoffs now name external MIDI ownership, native semantic accessibility
  and the typed fixed-registration selector as concrete independent next work,
  preserving scanner G5 and physical AO-28/Leslie/acquisition prerequisites.

## 2026-11-14 — Qualified replay/install source and completed calibration wave 7

- The immutable combined commit `16d72e1` (tree `5619bbb018830e071bc2ce45af84984cdd16bfc1`)
  configures, builds and passes **103/103 unfiltered SDK-free Release suites in
  197.85 seconds**. The exact GitHub source equivalent is `7caee9e5a1aadfa36f2a87b6855684cbd730d803`.
  [The integration record](reviews/CALIBRATION_INSTALL_REPLAY_INTEGRATION.md)
  retains source mapping, commands, log hashes, method/skip distinctions and limits.
- Accepted assignments 40–42 after independent review: the twelve-case resource
  profile preserves all 36 ordinary samples and separate instrumentation; the
  composition audit passes 220 finite cases against an actual unchanged package;
  the accounting audit retains two dated snapshots and twelve negative/positive
  cases. Seven logical waves and 42 distinct assignments are accepted.
- Updated historical admission counts explicitly: original wave-4 results remain
  historical; the integrated corpus has 59 methods and audio has 63 including
  two explicit capability skips. Running/finished-but-unaccepted workers remain
  separate from accepted results. New dispatches are registered immediately.
- Inspected and merged `6214032` before publication, preserving the native
  workflow endpoint checks and stronger actual-link/stat preservation fixture.
  The fresh merged archive `0f41ccc` passes all 43 demo methods in 1.519 seconds.
  Native workflow changes retain their owning track's qualification; the original
  full 103-suite gate remains attached to its earlier exact source.
- The observed replay allocation prompted assignment 43's minimal descriptor-size
  read proposal and independent assignment 44; those source changes are excluded
  from this 103-suite source. Graph-scale acceptance is independently dispatched
  as assignment 45. No physical evidence or maximum-resource guarantee is inferred.

## 2026-11-14 — Accepted replay, installation and actual hosted review

- Accepted assignments 35–39, bringing the calibration total to 39. Replay
  passes 69 independent methods; one initial metric-record lookup error in the
  test harness is retained with unchanged numerical expectations. Complete
  canonical-byte equality distinguishes replay match from engineering outcome.
- The separate 57-file CaptureTools component passes 16 independent methods,
  including all 57 missing-input preflights, Unicode relocation with private
  source/build deletion, standard-library-only installed execution and four
  exact replays. The unchanged 23-file OfflineTools suite passes 2/2 through a
  private current configuration with 95 source identities checked before reusing
  complete qualified binaries. The initial AST-relative-import harness error is
  retained; no production repair or inventory change was needed.
- Assignment 39 inspected all ten completed hosted logs at `955fc4c`: nine
  successes and one Windows Release failure. Linux/macOS Release and Linux
  sanitizer each pass 101/101; the native standalone and VST3 matrices succeed.
  Earlier canonical-output, alias-fixture and progress failures are resolved at
  this exact source. See [the hosted recheck](reviews/CALIBRATION_HOSTED_RECHECK.md).
- Windows failed one of 43 demo methods because `readlink()` returns its native
  extended absolute target spelling. Root captures the actual target before
  rejected generation and requires it unchanged afterward; link-presence and
  absent-target assertions stay intact. All 43 methods pass locally in 1.223 s.
  A reached original/repaired spelling probe reproduces the old failure and new
  pass. No producer changed, and a new native Windows result is still required.
- The fetched concurrent main advance `183fc9e` contains standalone chapel
  replay/demo/audit work and an additional corpus Unicode regression. The merge
  preserves that advance; its sole development-log insertion conflict retains
  both complete histories. The coherent gate follows this combined source.

## 2026-11-14 — Verified calibration publication through assignment 34

- Published with an expected-head guard from remote `0085e33`, without force.
  Fetched main is exactly `955fc4c41f74ada094f14fbaf386c943811e9050`, tree
  `70956d0f0e125d57abfbf1aed56460c067f8ef28`, identical to the reviewed local
  committed tree. Active replay/install worker files remained outside it.
- Retained the exact tested source trees as separate reachable commits:
  `340903a333ecfa5c684620ae8ac54e2e917a6217` for the 99-suite combined gate,
  and `783363f627afeb07f1401fcff042d1a24df094dd` for the 16-suite study/demo
  gate. Qualification reports map their local freeze identities explicitly.
- Actual hosted runs are CI `43531758072`, native standalone `43531758095`
  and native VST3 `43531758175`. Initial completed observations include Linux
  Release and sanitizer success, native standalone Linux success and native
  VST3 Linux/Windows success. Windows Release/standalone and all macOS results
  were still running or queued at that observation. Assignment 39 independently
  records exact later states and completed logs; no pending job is called pass.

## 2026-11-14 — Final standalone reviews and observed candidate failures

- Accepted the completed multi-configuration installation and milestone reviews,
  two actual chapel audition captures and the partial session/workflow audit.
  Root independently viewed both PNGs and ran the ten-file retained demo verifier:
  165,762 bytes, both complete control/held endpoints, zero recorded faults and
  joined empty shutdown. These are dummy audio/video software renders.
- The actual manifest now records 59 dispatched / 56 accepted assignments and
  nine complete waves. Assignment 60 has not yet been dispatched. The session
  audit's frozen 57/54 counts remain historical; its deliberately premature
  strict-sixty check correctly failed and was not reclassified as acceptance.
- At published `0085e33`, fresh complete native-enabled Release passes 105/105.
  The first fully instrumented native group retains 13/14: a chapel assertion
  required a sampled Upper-only state during a 100ms interval. Assignment 55
  retains that failure and qualifies exact legal command prefixes plus separate
  held endpoints without changing production code or increasing existing scripts.
- Hosted core run `43529788060` has successful Linux Release and sanitizer jobs;
  Windows job `132244338459` retains 92/96 and all original calibration failure
  details. Native run `43529788101` and VST3 run `43529788109` pass Linux/Windows.
  Their three queued macOS jobs were subsequently cancelled without observed
  execution. Dispatch and cancellation are not platform passes.
- Fetched concurrent calibration `955fc4c`, which already contains its authors'
  UTF-8/LF output, canonical fixture-path and observable-mutation repairs along
  with new offline job/readiness/study/demo work. Assignment 58 preserves that
  authorship and independently checks the fixes against every original Windows
  failure, adding only a meaningful missing Unicode/StringIO regression.
- Assignment 59 found two remaining copied build recipes that selected default
  configuration before referring to Release. Root added `--config Release` in
  the app/install guides, as already done in the operational handoff. Standing
  instructions now say all active tracks, and logical six-assignment waves no
  longer imply two synchronized batches. Integration and final publication follow
  only after the accepted changed-source evidence is complete.

## 2026-11-14 — Calibration wave 5 gate and accepted study/demo

- Accepted 34 distinct calibration assignments: five complete logical waves
  plus the study/demo producer and independent acceptance pairs. Replay and its
  reviewer finish wave 6; the dependency-ready installation component begins
  wave 7. The manifest retains 37 actual identities at this observation, with
  three running. A date change does not create another session or recount workers.
- Inspected and merged remote `0085e338388f2c7516a7d455f11692b94e9451f4`,
  preserving the separate standalone reader-progress/configuration/notices work.
  Frozen combined source `fd0fb58d2f882aa76c7e40e510f44766f762727c`, tree
  `3329cf68bb9ea84479e254934778935bb5c44773`, passed the complete SDK-free
  Release build and **99/99 suites in 180.68 seconds**. See the
  [wave-5 evidence](reviews/CALIBRATION_WAVE5_INTEGRATION.md). This source
  excludes the later study/demo/private job extension and their focused gate.
- The later study/demo source `1aef68489fc18b860bbab8fd06a65fdde8a4d6cd`,
  tree `5ed86b2f0eeee4e00926aebaaf4432ec61760328`, passes **16/16 focused
  suites in 40.21 seconds** from a fresh archive after building the renderer.
  The [focused report](reviews/CALIBRATION_STUDY_DEMO_INTEGRATION.md) records
  scope and the separately retained GitHub source commits for both tested trees.
- Bounded studies preserve all ordered jobs and complete shared snapshots.
  Independent acceptance passes 61 methods plus the unchanged 81-method public
  job regression. Fourteen temporary-source mutation processes test both
  between-job and final-return phases; actual eight-job/64-manifest/256-reference
  composition stays within independently derived bookkeeping bounds.
- The original 16-file, 32,831-byte synthetic archive passes 43 independent
  methods. Literal quarter/half-offset comparisons produce pass, inconclusive
  and failure; the study retains all three and deliberately fails. All identities
  and date placeholders are disclosed constructions, rights remain unknown and
  physical claims remain unestablished. No cached execution report is substituted
  for the literal `EXPECTED.json` oracle.
- Hosted failures at `779fb6e` remain recorded. Windows canonical-byte writers
  and canonical-path fault fixtures pass locally; the standalone scheduling
  repair is now integrated. Fresh hosted results are still needed. No physical,
  native device, every-host or final-release gate is inferred from these checks.

## 2026-11-13 — Published standalone final code candidate

- Published `0085e338388f2c7516a7d455f11692b94e9451f4` with guarded parent
  `779fb6e13b8f60236cad4aedb9999ba16198f920`. Its exact tree
  `19c763503f67e1f054d2d27b6ec3d8fca2e36474` matches local `fa6df9d` and was
  independently fetched and compared after publication. No force update was used.
  The local source history remains on `standalone-local-w9-checkpoint`.
- Frozen archive integrity passed 525 Markdown files / 2,925 local links, the
  unchanged 500-page PDF and this session's actual 55-dispatched / 52-completed
  record at the candidate. The source checker also reports the separate original
  session's sixty notes; that number is not reused for this active session.
- Hosted core `43529788060`, standalone `43529788101` and VST3 `43529788109`
  were observed queued against this exact commit. Execution, artifact bytes and
  completed results require their own observation. Assignment 55 starts a fresh
  complete local Release build and fully instrumented native gate on the same
  tree; assignment 56 will use its completed binary read-only for an actual
  chapel demonstration.

## 2026-11-13 — Combined source freeze for final standalone integration

- Inspected and merged concurrent calibration publication
  `779fb6e13b8f60236cad4aedb9999ba16198f920`, tree
  `f9baccbb54f51063b01a0859d2c10cdadfbd238b`. Its independently owned audio,
  corpus, comparison/policy and admission work is preserved. The reported
  96/96 SDK-free result belongs to its named wave-4 source; this combined source
  will receive its own full native-enabled gate in assignment 55.
- Accepted assignment 52's complete 60-case benchmark matrix: 6,000 measured
  calls, 4,761,600 measured frames, all 240 state snapshots and all timing
  arithmetic pass. Root independently reran the retained artifact verifier.
  All 26 above-period observations remain in the data; no device deadline or
  controlled performance comparison is claimed. See the
  [matrix report](reviews/STANDALONE_BENCHMARK_MATRIX.md).
- Assignment 53 reproduced unknown multi-configuration installation returning
  success with eight metadata files and no executable. Its frozen repair adds
  an unconditional component-scoped configured-name guard before all writes.
  Debug/Release maintained tests pass, mixed-case names preserve CMake behavior,
  and unknown names preserve fresh/existing destinations. Its remaining runtime
  audit and final report are still active; the final combined gate will exercise
  the maintained single-configuration branch as well.
- Assignment 54 identified a concrete bundled-notice omission. Root retained
  the exact pinned yuv2rgb notice and selected HIDAPI BSD text, plus the Sun
  math fallback notice for configurations that include it. The audited Linux
  binary demonstrably links yuv2rgb; compilation of fallback math archive members
  alone is not reported as linked fallback code. The existing combined notice
  carries these texts without changing the nine-file layout.
- Refreshed current README/guide/status/milestone navigation while preserving
  the original pedal result tables as explicitly historical. Current scanner
  G5, physical M3/M5/M6/M7/M8 and device/accessibility/release gates remain open.
  The actual ledger has 55 dispatches / 52 accepted results; no final-wave
  completion or new full-source test pass is claimed yet.

## 2026-11-13 — Accepted standalone timing, reader and preservation evidence

- Accepted assignment 47: screenshot labeling/capture uses the actual painted
  applied state, and successful requested smoke requires the held-key image.
  Independent pixels and acknowledged held/released resize endpoints supplement
  diagnostics. A fresh fully instrumented core/SDL/app gate passed 3/3 suites,
  38 methods and 210 processes in 50.084 seconds; deterministic old failures
  and an invalidated stale-object attempt are retained. See the
  [timing review](reviews/STANDALONE_TIMING_REPAIR.md). Leak detection remains
  explicitly excluded for the demonstrated ptrace limitation.
- Accepted assignment 50: each of two readers acknowledges exact initial/newer
  final snapshots in all three phases. A controlled after-return overflow
  supplements fifteen races; all prior FIFO/recovery/coherence workloads remain.
  Fresh Release, one-CPU Release and coherent TSAN passed on their first runs.
  The constrained run legitimately observed zero flagged overlap in two phases,
  while every required checkpoint and recovery passed. See the
  [progress review](reviews/STANDALONE_READER_PROGRESS.md).
- Accepted assignment 51: all 196 protected pre-existing files and all 45
  parameter records match baseline; state migrations and generated inputs pass.
  Eleven selected suites passed per fresh revision. Forty renders over
  3,241,200 frames matched exactly, and the two renderer binaries are themselves
  byte-identical. See [preservation evidence](reviews/STANDALONE_CORE_PRESERVATION.md).
- The actual ledger has 54 dispatched / 51 completed assignments and eight
  completed waves. Wave 9's remaining three reviews are active; six final-wave
  assignments remain undispatched. The combined-source gate and publication are
  still required for the accepted repair code.

## 2026-11-13 — Standalone repaired publication and independent setup audit

- Published `649b12c7d1faa7601fde1019e913347c65a6634a`, exact tree
  `cf63327d857b02029e8c5c6f406cab3d3c6890d1`, using an expected-head update.
  Fetched the remote commit and verified identical local/remote trees; preserved
  concurrent rotary/calibration work and unfinished assignment 47 changes.
- [Observed platform results](reviews/STANDALONE_PLATFORM_FOLLOWUP.md): all
  three standalone jobs passed 14/14 and packaging; all VST3 jobs passed.
  Core Windows 90/90 in 148.78 seconds, macOS 90/90 in 88.80 seconds and Linux
  ASan/UBSan/leaks 90/90 in 104.86 seconds passed. Linux Release retained 89/90
  in 71.21 seconds because `reader.active_reads > 0` depended on scheduling.
  Assignment 50 replaces the remaining incidental-positive oracles with exact
  publication handshakes and controlled recovery coverage; its qualification
  is separate from these published results.
- Accepted [assignment 48](reviews/STANDALONE_HOSTED_PLATFORM_REVIEW.md): actual
  earlier `5b8e241` Linux/Windows ZIP digests, inventories and payload bytes
  match; the downloaded Linux executable completes the 18-event keyboard replay
  after relocation. Windows execution evidence comes from its actual runner.
- Accepted [assignment 49](reviews/STANDALONE_CLEAN_SETUP.md): 842 frozen source
  blobs/modes, fresh Unicode/space-path builds, eight selected SDK-free suites,
  complete 14/14 native suites in 63.97 seconds, nine-file installation and
  seven direct relocated invocations with private original paths absent. The
  benchmark, explicit chapel export, keyboard ownership, Save/Load and empty
  fresh-process note state match independent expectations. All 23 recorded
  commands returned zero; no production change was needed for this scope.
- The actual ledger now has 51 dispatches and 48 accepted results; assignments
  47, 50 and 51 remain active. Nine assignments remain undispatched. The original
  instrumented 92/94 result, current reader assertion and physical product
  gates remain visible; no passing subset substitutes for their evidence.

## 2026-11-13 — Independent capture/calibration-readiness scope

- Accepted assignments 29-30, completing five waves and 30 distinct results.
  Numerical acceptance passes 19 methods using 90-digit independent references
  and an actual maximum-frame sparse comparison. Schema review executes 665
  cases. It reproduces terminal-LF admission in five old v1 schema string
  families; root's schema-only repair preserves all v1 fields and runtime
  meaning. The optional audit package's absent date-time checker caused four
  initial audit expectation failures, retained and correctly classified.
- Inspected completed hosted jobs at `779fb6e`. All Linux/macOS/Windows native
  standalone and VST3 jobs and the Linux sanitizer job succeeded. General
  Release failed: Windows CLI byte translation, macOS/Windows fault-fixture
  ancestor aliases, and one separate Linux standalone scheduling assumption.
  Root repaired canonical UTF-8/LF output in audio/corpus, made test hooks target
  canonical paths and prove interception, and made in-place mutation stamps
  explicitly observable. New CRLF/ASCII-wrapper and real ancestor-alias probes
  reproduce the old defects and pass the repairs. See
  [retained hosted diagnosis](reviews/CALIBRATION_HOSTED_PORTABILITY.md).
  Root did not edit the concurrently owned standalone C++ test; its committed
  progress repair will be integrated after publication.

- Accepted assignments 25-28. File jobs bind declared original metadata, audit
  the whole corpus, compare explicit untransformed windows and retain complete
  policy/corpus outcomes. A 14-line private corpus-core extraction preserves
  its public API and passes both existing corpus suites (47 and 57 methods).
  Independent job acceptance passes 81 methods with no skips or defects.
- Declaration readiness reads one unchanged v1 manifest, reports exactly 21
  checks plus three per channel, preserves original reasons and retains seven
  unestablished evidence claims. Independent acceptance passes 65 methods,
  repeated by root in 0.580 seconds with no skips. A complete declaration is
  not an artifact, calibration, permission or fidelity pass. The supplied plan
  intentionally exits 3 with 20 missing declarations.

- Published the reviewed wave-3/4 toolchain as
  `779fb6e13b8f60236cad4aedb9999ba16198f920`, tree
  `f9baccbb54f51063b01a0859d2c10cdadfbd238b`, using an expected-head guarded,
  non-forcing update from `649b12c`. Fetched remote identity and exact tree
  equality were verified before aligning this checkout. Ongoing wave-5 files
  were preserved and excluded from that publication.

- Frozen wave-4 commit `1c2ea32` passed 11/11 focused suites in 12.57 seconds.
  Remote standalone main then advanced to `649b12c`; root inspected and merged
  its device/portability changes. Fresh combined source `45f875d`, tree
  `2dcfc0e8071cdc30d75f8fb9be340826296fcbaf`, passed the full SDK-free Release
  build and 96/96 CTest suites in 177.43 seconds. The exact commands, log hashes,
  native-capability skips and excluded later work are retained in
  [wave-4 integration evidence](reviews/CALIBRATION_WAVE4_INTEGRATION.md).

- Accepted assignments 19-24. Fixed policy evaluation retains the original
  policy-byte identity, strict report admission and all uncertainty decisions;
  its independent suite passes 49 methods. The file-job contract and schema
  were independently reviewed. Root resolved a composition gap by requiring
  the corpus audit to reuse admitted metadata and to check every artifact in
  the final snapshot. Compact original policy bytes must never be replaced by
  a pretty reserialization before evaluation.
- Independent corpus admission reproduced an opened-leaf descriptor leak on
  parent-close failure. Root transferred resource ownership before fallible
  closes and preserved primary/cleanup and cancellation outcomes. The retained
  suite passes 57 methods, repeated by root in 1.571 seconds; the existing
  47-method corpus suite also passes the repaired source.
- Independent audio admission reproduced unsupported-width rejection masking
  an earlier contradictory byte-rate field. Root restored byte-position error
  precedence without weakening the frozen contract. The retained suite runs
  62 methods: 60 pass, two skip for unavailable native Unix socket creation and
  Windows reparse execution. Root repeated it in 2.158 seconds. Existing audio
  acceptance still passes 41 methods. Sparse file-size admission and reduced
  resource guards are not reported as full maximum-stream scans.
- Integrated concurrent standalone commit `5b8e241` without changing its scope.
  Frozen combined source `8864c05` passed the complete SDK-free Release build
  and 93/93 CTest suites in 59.29 seconds. That snapshot predates the later
  policy and parser repairs; its report names that boundary explicitly.
  Wave-4 source is frozen separately before assignment 25 may share the corpus
  audit core. The next independent job tests must retain original policy bytes
  and prove preflight occurs before artifact work.

- Accepted independent assignments 16-18: audio 41/41, corpus 47/47 and metrics
  42/42 methods, all repeated by root with no skips. Initial test-control/oracle
  errors and their corrections are retained in the worker notes; no producer
  change was needed to pass these suites. The legacy capture suite also passed
  41/41 methods.
- A direct legacy analyzer run passed its first 14 methods but could not enter
  renderer integration because this checkout had no built `hammond_render`.
  This was an explicit setup failure, not an analyzer result. The coherent gate
  must build the renderer/profile before running that required integration.

- Published the reviewed foundation as `5026f671e788eb5e1a77c8ed4046a34afd539200`,
  tree `2ed85b986f70895000f086039750f44773508819`, and fetched exact identity.
  The frozen-source focused integration passed 3/3 suites; see
  `reviews/CALIBRATION_WAVE2_INTEGRATION.md`. All three hosted workflows at this
  commit were observed queued, with no pass claimed.
- Accepted producers 13-15: bounded full-stream audio inspection and windows,
  strict cross-manifest corpus/lineage auditing, and array comparison metrics.
  Their notes retain exact source hashes and author checks. Independent workers
  16-18 now qualify these modules; producer assertions are not counted as
  independent acceptance. Root inspection also exercised the maximum report
  channel/frequency shape and a typed current-directory I/O failure.
- Frozen audio/corpus/comparison contracts now specify exact APIs, sample/byte
  identities, whole-group lineage and uncertainty-aware criteria. Independent
  integration review verified literal hashes and equations and clarified the
  final/final_test role mapping and comparison-report numeric bound.
- Independent JSON-helper acceptance reproduced descriptor leaks on fdopen
  failure and cleanup errors masking publication outcomes. Root repaired those
  paths and retained the failures/regressions. The complete independent suite
  now passes 49/49 methods; root repeated it with no failures or skips.

- Wave 1 completed: six distinct new workers read every PDF text page 1-500
  in disjoint ranges and inspected 31 selected original page images. The new
  source review records coverage, requirements and unavailable physical evidence.
- The frozen starting source passed 85/85 Release CTest suites in 61.53 seconds;
  see `reviews/CALIBRATION_BASELINE.md`. Scope checkpoint `08fa8de` was published
  and fetched with exact tree identity. Hosted workflows were observed queued,
  not passed, at the first check.
- Root added bounded strict-JSON primitives and non-replacing JSON publication
  for subsequent offline tools. A direct smoke check passed exact hash readback,
  preserved an existing destination and left no temporary files. Independent
  acceptance is pending; this smoke does not replace it.

- Inspected authenticated repository permissions and remote `main` at
  `38c1fac949368fa54bd86c6c00a5997a73480f5e`, then created a separate checkout.
  Other checkouts have unfinished scanner, rotary and native standalone work;
  their files and histories remain untouched.
- Selected the explicitly pending M0/M8 capture/corpus/evaluation tooling under
  `CALIBRATION_SCOPE.md`. The existing capture validator checks metadata and
  optional byte identity, but not actual audio headers/content or corpus splits.
- Verified the unchanged 500-page PDF, SHA-256
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`;
  extracted every page for six fresh readers. The actual new manifest records
  each distinct dispatch and accepted result; no previous session is recounted.
- Started a clean archived-source Release baseline using GCC 14.2.0, CMake 4.4.4
  and Python 3.12.14, both optional native adapters OFF. Completion/results will
  be recorded separately after execution finishes.
- CLI push dry-run has no configured password. Authenticated GitHub publication
  remains available and authorized; use Git data operations with an expected-head
  guard and verify the fetched tree. No force-push is used.



## 2026-11-13 — Rotary contracts and independent acceptance foundation

- Accepted assignments 07-12: frozen R1-R6 numerical/types boundary, strict
  proposed profile/schema/validator, independent 80-digit motion and Cartesian
  bisection reference, native exact-segment motion, and independent regression.
  No fixture value is promoted to a factory or measured value.
- Profile tests passed 33/33. A separate 358-case JSON Schema audit found and
  retained a prose-control/terminal-newline pattern defect; repaired patterns
  now pass all 358 cases. The default suite remains standard-library-only.
- Independent reference tests initially reported three failing subcases in two
  methods: full-day zero and positive decay hit an inappropriate exponent guard.
  The integrator preserved ordinary scalar bounds, admitted compact state
  exponents within the private context, canonicalized zero and retained positive
  tails. The unmodified suite then passed 33/33 in 2.227 seconds, exit 0.
- The native motion implementation has strict GCC 14.2 author checks; complete
  independent R2 acceptance remains in wave 3. Geometry and fractional-history
  workers were dispatched only to disjoint paths while wave 2 acceptance closed.
- The session's retained checker distinguishes actual planned/running/complete
  records; it cannot attest external dispatch or replace substantive acceptance.
  Exact coherent integration and publication evidence is recorded separately.
- Coherent staged source tree `b4bf3bf65ef6706f2c613f875d759f9d71431d1f`
  configured and built successfully; 81/81 Release suites passed in 38.03 seconds.
  Repository integrity and the explicit 12-complete checker passed. See
  [integration evidence](reviews/ROTARY_WAVE2_INTEGRATION.md). Active wave-3
  implementation was excluded from that qualification.
- Before publication, inspected and merged concurrent standalone commit
  `219821dfaca6bfee8ba0905993ed8deec7a66396`. The new coherent source tree
  `1d78b5663b30cb48984e6b810ed33ede4894ced8` passed strict Release build and
  85/85 suites in 38.91 seconds, plus source/accounting checks. Both tracks and
  their separate claims remain preserved; optional native/device gates were
  not part of this combined SDK-free run.

## 2026-11-13 — Independent rotary foundation begins

- Cloned main at `96a37a977ef22b7adf38e1a841f57ffcf32519a7` into a separate
  checkout and inspected the active scanner and standalone ownership. Their
  uncommitted work remains in their own checkouts.
- Created a distinct sixty-assignment, ten-wave rotary ledger and split all
  500 unchanged atlas pages among six fresh readers. The new nominal M7 scope
  preserves separate horn/drum radiation inputs and all unresolved M5/M6,
  measured-fidelity and product-integration gates.
- Bare `cmake` initially failed because it was absent from PATH. Located the
  existing build tools and qualified a clean source archive with GCC 14.2.0,
  CMake 4.4.4, Ninja and Python 3.12.14: 79/79 default Release CTest suites
  passed in 50.43 seconds. See [baseline evidence](reviews/ROTARY_BASELINE.md).
- Updated permanent future-agent scope and handoff rules. No rotary runtime,
  physical acceptance or new publication is claimed by this initial record.

Every future agent must append actual changes and executable evidence here or
provide an assigned note for the integrating agent, then update the status and
next-step documents. See the mandatory [agent instructions](../AGENTS.md).

Entries below preserve observations at the time of each assignment or checkpoint.
Later repairs and hosted results supplement earlier failures and pending gates;
they do not rewrite those records. Use [STATUS.md](STATUS.md) and
[CI_QUALIFICATION.md](CI_QUALIFICATION.md) for current, revision-specific results.
The [project guide](PROJECT_GUIDE.md) distinguishes the original session ledger
from the independent continuation ledger and its separate assignment identities.

## 2026-11-12 — Initial implementation session (in progress)

- Baseline repository commit: `501c68ba44c16e8a787bba69a272d4c44fe5308a`.
- Source: 500-page research atlas, 21,248,265 bytes, SHA-256
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Confirmed repository contained only the PDF and minimal README. Referenced
  companion assets were absent. Extracted all 500 pages for bounded review;
  no page lacked extractable text. Temporary extraction is outside the repo.
- Assigned complete coverage to agents 01-06 with disjoint inclusive ranges.
  Their committed notes retain exact page ranges and visual-review coverage.
- Established `AGENTS.md`, source manifest and M0-M2 implementation contract.
- Published `93924088e6de8879b8f13a69bc20a4016b5742cd` to `main` and fetched
  the same remote head. CLI push lacked a configured credential; the connected
  GitHub API published the commit with an expected-head guard.
- Build environment: GCC 14.2.0, GNU Make 4.4.1, Python 3.12, CMake 4.4.4
  installed in temporary task-local tooling. No host audio SDK required.

This is an intermediate record; no engine/test/release pass is claimed here.

### Wave 01 — complete atlas review

All six assigned ranges were read: 1-84, 85-168, 169-252, 253-336,
337-420 and 421-500. Each reviewer retained its exact coverage and inspected
selected figures. The combined review identified the complete M0-M9 sequence,
recoverable routing/preset/pedal data, missing companion assets, proposed versus
measured evidence boundaries, scanner pseudocode/equation issues, and separate
organ/Leslie/host/UI gates. See notes 01-06 in `development/agent-notes/`.

Wave 02 begins the typed profile contract, strict authoring compiler and build
foundation. No hardware fidelity claim has changed.

### Wave 02 — profile and build foundation

Agents 07-12 implemented fixed-size C++20 types/profile loading, strict JSON
authoring validation and deterministic compilation, CMake/Make/test tooling,
independent permanent tests, and full atlas navigation/errata/source notes.
The profile explicitly contains 91 sources, 549 manual routes and 9 drawbar gains.

Observed verification: strict GCC 14 Debug and Release builds; 37 Python unittest
cases; 2,601 malformed C++ payload cases with field-preserving rejection; exact
byte limits, six printed routing rows, source anchors, locale and I/O failure
checks. The source PDF hash and 500-page/80-chapter coverage were rechecked.
ASan+UBSan passed for the profile test with `ASAN_OPTIONS=detect_leaks=0`. Default
LeakSanitizer finalization failed because the executor runs under ptrace; leak
checking is not claimed. No Windows/macOS or host/audio fidelity result yet.

Profile identities: canonical authoring SHA-256
`49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`;
compiled bytes SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.

Wave 03 implements the shared bank, dry graph and renderer against frozen timing
and file contracts. See individual notes 07-12 for exact commands and limitations.

### Wave 03 — working shared sources, dry engine and offline audio

Agents 13-18 implemented a value-owned 91-source sine bank with deterministic
SplitMix64 initialization, transactional dry Engine, strict offline CLI/WAV writer
and independent permanent source/engine/CLI tests. The core shares each source
sample across every routed contact and adds branch gains coherently. It does not
restart phase on notes or normalize by polyphony.

Observed checks: all supported rates 44100/48000/96000; 440 crossings in 1 second
for tone 46; long-double phase/sine oracles; coherent doubling of 6.020599913 dB;
stable ties, flushes, disconnected rendering, caller-owned profile changes and
failure atomicity.
The 2053-frame engine timeline matches bitwise over blocks 1/17/64/127/512/1024.
The CLI's 20 retained unittest cases include dense subdivision, little-endian WAV
headers/channels, clipping/no-clobber failure and partial-final-block handling.
A separate 3856-event smoke matched blocks through 65536; its concurrent destination
race preserved the other writer's file. No hardware, host or deadline pass follows.

The callback currently has discrete control steps and ideal gates. Native automation
curves, hot profile exchange and physical circuit/rotary stages are deferred.
Wave 04 adds an explicitly exclusive four-bank model and Cancel while preserving
legacy audio. Permanent notes 13-18 identify actual commands and limits.

### Wave 04 — early console state and documentary control data

Agents 19-24 added four retained A/B drawbar banks, route-only Cancel, explicit
bank events, snapshot restoration and bounded `B3CONTROLS1` serialization.
The 39-entry internal parameter registry has permanent bank identities but no
verified native host mapping. Pedal data reconstructs 25x8 contacts with 195
connections and 5 nulls; pedal audio, physical weights and full transcription
verification remain open.

Strict Debug/Release control and legacy engine/CLI tests passed. The integration
matched the frozen wave 03 renderer in 24 WAV-byte/JSON comparisons. New timeline
tests cover 3 rates and 6 partitions, held-key switching, Cancel/reselect/panic,
all 91 phases, 81 malformed snapshots and 68 invalid new-event calls. Control I/O
rejects 330 malformed inputs atomically. The registry's 19 and pedal map's 15
Python tests pass. Root updated the legacy invalid-enum test from 5 to 255 because
5 is now the documented BankDrawbar event; the invalid-enum assertion itself remains.

No physical contact, percussion, multi-preset latch, pedal-audio or host gate was
closed. Current tasks move to render provenance, fixtures and independent evidence.

### Primary-source acquisition during wave 05

The coordinator retrieved the atlas-linked 220-page factory service scan from
Audiofanzine for documentary review. Its SHA-256 is
`ec2ac51f363dcd1ee039f7711acda32fd014e15ad80dcb77ae199545f9130cc9`
and its byte size is 7,077,593. PDF pages 155–157 contain Table III, including
the manual and pedal source assignments. The file is retained outside the
repository for review; no additional manual is redistributed. This acquisition
opens independent transcription work in wave 07 and closes no physical gate.
The separate Synthmania compilation was accessible to web extraction, but its
direct download returned HTTP 406; it was not used for numerical verification.

### Wave 05 — initial render evidence and CI infrastructure

Agents 25–27 added a bounded reproducible renderer wrapper, five explicit event
fixtures and an independent streaming PCM16 analyzer. Their targeted suites passed
14 wrapper tests, the five-render catalog checks and 15 analyzer tests with an
actual C++ renderer. The A4 steady-window crossing estimate was
439.9999816417002 Hz at a 48 kHz file rate; this is a serialized nominal fixture,
not a measurement of a physical generator. No fixture clipped.

Agent 29 added pinned official GitHub Actions, three Release platforms and a
Linux ASan/UBSan/leak job, with read-only repository permissions and retained
diagnostics. Initial hosted status is pending. Agents 28 and 30 continue the
callback boundary audit and independent bundle verification. The coordinator
will test a clean staged snapshot before publishing this evidence checkpoint.

### First hosted CI result — `b9c1cac`

[Run 43361632464](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43361632464)
passed all 12 CTest suites on Linux Release and Linux GCC ASan/UBSan with
`detect_leaks=1`. macOS AppleClang 17 compiled against a libc++ without floating
`std::from_chars`, failing in control parsing. Windows MSVC compiled with zero
warnings/errors and passed 10 of 12 suites. The fixture catalog caught Git
checkout CRLF hash changes; the evidence wrapper rejected unchanged files at its
path-stat/descriptor-stat comparison, and one raw subprocess fixture expected a
POSIX newline. These are recorded failures, not waived checks. Wave 06 will
implement portable decimal conversion and evidence file handling; a later hosted
run must verify the changes. No native host/audio-device claim follows from CI.

### Wave 05 completion and wave 06 robustness

Agent 28’s calibrated global C++ allocation probes observed zero allocation and
deallocation calls during 63 accepted and 33 rejected prepared callbacks, covering
216,255 frames and 23,919 events. Static inspection found only fixed storage and
bounded project callback work; linked math internals, C/system allocation, other
threads and timing deadlines remain outside that evidence. Agent 30’s independent
bundle consumer passed 27 test methods against actual renders and mutated
artifacts. It keeps integrity, authenticity, build provenance and fidelity distinct.
All six wave-05 assignments are complete.

Agent 31 reproduced an original stream-buffer runtime exception escaping the
profile loader. A narrow bad-stream exception handler and nine deterministic
failure/recovery cases now pass, alongside five existing Release core suites.
Portable numeric parsing and Windows evidence handling are in progress; combined
changes require integration and actual hosted qualification. A separately reported
extreme-frequency phase-stall case is assigned to the numerical boundary review.

### Portable numeric and evidence repairs

Agent 32 replaced floating `from_chars` with one shared classic-locale decimal
converter, preserving integer parsing, strict syntax, finite/subnormal range
handling, signed zero, nearest rounding and failure atomicity. Its new vectors
cover 16,547 accepted exact/round-trip values and 106 invalid tokens; all 16
then-current Release suites passed. The canonical nominal profile and compiled
profile identities remain unchanged.

Agent 33 preserved raw artifact identity across Git checkouts with LF attributes
and repaired invalid cross-API file-stat equality in both hash and WAV readers.
Within-API before/after checks, regular-file bounds, raw hashes and POSIX
device/inode binding remain. It reproduced all five bad Windows score hashes
from CRLF conversion and tested an isolated autocrlf checkout. Nineteen wrapper
methods, the five-render catalog and 27 independent verifier methods passed.
Raw output capture still preserves its bytes. An actual hosted rerun must close
the macOS/Windows gates. Root updated the stale Profile.cpp parser comment.

### Hosted portability repairs verified — `9c8068c`

[Run 43363048563](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43363048563)
completed successfully. All four jobs passed all 16 registered suites: Linux GCC,
macOS AppleClang and Windows MSVC Release, plus Linux ASan/UBSan with leak
detection enabled. The macOS numeric replacement and Windows evidence repairs
therefore have actual hosted results. These jobs qualify only the tested offline
software scopes; audio-device, host, hard-deadline and physical gates remain open.

### Wave 06 completion — numerical and tooling boundaries

Agent 34 reproduced a positive source increment that rounded away, then added
an atomic preparation rejection below `2^-53` turns per sample. Four affected
Release suites passed. The 262,144-frame nominal check at each rate observed
maximum circular phase error `7.722181563901e-12` turns within its derived
`3.637978893828e-11` budget. The source/sample recurrence and nominal profile
bytes remain unchanged; progress near the new support floor is not an accuracy
claim. The synthetic maximum mix reached both signs of 1,098 finite coherent
branches without asserting physical output level.

Agent 35 added a bounded four-case prepared-engine benchmark and CMake target.
Strict Release build, 16 individual-versus-all workload equivalence checks and
29 invalid argument/work/profile rejections passed. Its temporary shared-tree
run includes a scheduling outlier beyond the nominal interval; no deadline gate
was inferred. Final publication uses a new immutable staged snapshot.

Agent 36 added a read-only source-archive checker with 41 passing mutation/CLI
methods and a real-PDF smoke. It checks source identity, reconstructed index and
review coverage, local Markdown file links, actual note IDs and existing data
hashes without Git or built artifacts. The optional exact agent-count check is
reserved for the relevant snapshot/final session. All six wave-06 assignments
are complete. Wave 07 now compares two independently frozen factory readings
and prepares explicit acquisition metadata and acceptance procedures.

### Wave 06 published checkpoint and remaining hosted failures

Commit `7c2ad20` matches the tested staged tree
`a3416cd144e8ae07f291434aa0b883b5a61796f4`. Its clean Release build passed
18/18 CTest suites, the source checker passed with exactly agents 01–36, and
the four-case benchmark completed with its qualified timing report.
[Hosted run 43364414017](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43364414017)
passed Linux and macOS Release. Windows passed 17/18 suites but three checker
assertions expected forward-slash origin paths while diagnostics used native
backslashes. Root changed that repository-relative diagnostic to `as_posix()`;
all 41 existing checker methods pass locally. The sanitizer job passed 17/18
suites and failed the executable-mutation evidence test at an unexpected error
stage. The cause remains under investigation; no failure is waived and the
checkpoint has no complete hosted qualification.

### Wave 07 independent factory routing evidence

Agents 37 and 38 independently entered and froze the factory Table III manual
and pedal cells before comparison. Agent 39 compared each reading against the
other and the original project data: all 549 manual assignments and all 200
pedal positions agree, including all five disconnections. The raw profile,
canonical profile and compiled profile hashes remain unchanged. The new
provenance manifest and validator pin the documentary scope separately from
the original authoring metadata. Twenty mutation methods passed; all compiled
routes also match both readings. Original pedal and compiler suites passed.

The source scan is 220 pages with the previously retained hash. Correct table
locators are PDF 155–157 / printed 3-76 through 3-78. Exact factory edition and
production revisions remain unestablished. No additional manual/images are
redistributed, and no gearing, specimen, calibration or physical-audio claim
follows. Shared current-status documents now distinguish completed documentary
routing corroboration from the remaining physical M2 gates.

### Wave 07 capture metadata and independent validation

Agent 40 added an original proposed capture schema, planned example and bounded
standard-library validator. It separates header rate from physical sample clock,
declared calibration from verification, and metadata checks from explicit file
checks. Unknowns retain reasons; local ancestry and grouping are explicit. The
only committed example is planned, with no fabricated acquired evidence.
Agent 41 independently constructed 39 passing methods and ran the selected
CTest gate successfully. The examples used for file tests contain only temporary
synthetic bytes; hardware declarations used for semantics remain in memory.

Root then reproduced an alias-check gap with real linked files and simulated
unavailable descriptor identities. The byte checker now uses a nonzero path
identity as fallback and rejects if neither API supplies an identity. Two targeted
regressions bring the capture suite to 41 passing methods. This is an observed
contract gap under the simulated metadata condition, not an observed Windows
runner failure. Metadata/file passes establish neither physical calibration nor
rights, authenticity, signal format or specimen fidelity.

Agent 42 completed the acquisition protocol after reading atlas pp. 109–156
and 349–366. It maps specimen/permission lock, the external pilot, dry sources,
contact/percussion/expression work and later circuit/cabinet captures to the
actual v1 fields. Whole takes, synchronized channels, chunks and derivatives
retain one grouping identity; a separate corpus ledger must govern validation
and untouched final holdouts. Its planning fragments validate without timestamp
or file claims, and all ten local links resolve. All six wave-07 assignments are
complete. Wave 08 addresses observed CI failures and local installation/usability.

### Wave 08 CI audit and local installation

Agent 43 audited all four complete diagnostic archives for `7c2ad20`: each
contains 18 suites and 195 Python methods with zero test skips. The report retains
exact toolchains, artifact IDs/hashes and both failures. The executable mutation
test now prepares a separate modified copy, replaces the checked path after real
execution and verifies both hashes. It still requires the exact integrity error
and additionally requires a successful child and complete logs. Nineteen methods
passed against Release and local ASan/UBSan binaries. The original hosted exception
remains unestablished; local original-method probes did not reproduce it. Local
leak-enabled execution explicitly failed under ptrace, so local instrumented checks
used `detect_leaks=0`; hosted leak qualification remains required.

Agent 44 added the OfflineTools local install component and a real relocation
test. It installs exactly the renderer, generated profile and six fixture/catalog
files, then moves a prefix with spaces and compares actual PCM, full WAV bytes
and JSON against the build renderer. A temporary changed installed profile affects
identity/output, and its removal rejects without fallback. Default and custom
relative layouts passed; missing build inputs and unsafe install destinations
rejected before copying. No dependency, system install, runtime bundling, plugin
or device application was added. The combined checkpoint now requires its clean
staged build and new hosted matrix results.

### Wave 08 documentation review

Agent 48 added a practical project guide and clearer README navigation for the
plan, current status, build/render/install workflows, evidence contracts, original
atlas/reviews, rights and the two distinct session ledgers. The build guide now
separates the initial local foundation evidence from later revision-specific
hosted qualification. The initial implementation contract points to current API
and console/state contracts and labels host integration as a proposal.

Early log entries had joined words and numbers; their spacing and prose were
repaired without changing recorded results. A comparison retained every numeric
sequence, inline command/identity and external URL in the earlier historical
entries. The read-only repository checker passed all five groups, including local
Markdown links and source/data identities, with zero errors. Scoped diff and
whitespace checks passed. This prose-only work ran no C++ suite and claims no new
hosted or physical qualification; its note records the remaining review boundary.

### Preserved continuation and qualified factory/capture checkpoint

Before publication, incoming continuation commit `5dcd942` was inspected: its
AGENTS additions and seven review documents were disjoint from the original
session's staged work. The coordinator preserved it as parent of `6c3dd8b`; no
force push or history replacement occurred. The tested original staged code,
tests and data were unchanged by that documentation integration, and the combined
archive passed the explicit 44-agent source check.

Actual hosted run [43365901429](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43365901429)
passed all four jobs at `6c3dd8b`: Linux GCC, macOS AppleClang and Windows MSVC
Release, plus Linux ASan/UBSan with leak detection enabled. The coordinator
downloaded all four complete diagnostic archives, checked returned ZIP digests,
source revisions, JUnit and LastTest logs: each contains 21 suites, 257 Python
methods and zero skips. The sanitizer log explicitly retains fatal ASan/UBSan/LSan
settings and `detect_leaks=1`. The earlier failed matrix and unestablished original
mutation exception remain historical facts in CI_QUALIFICATION.md.

### Completed waves 08 and 09 deliverables

Agent 45 recorded actual dependencies, distributed material and unresolved rights;
no project license or new third-party runtime was invented. Agent 46 wrote the
SDK-independent host/device integration proposal and eight unrun acceptance
groups. Agent 47 added independent CSV-selected runtime route checks covering
all 1,098 manual key/drawbar combinations, additional rates/folds/Cancel histories
and deliberate wrong-source probes. Its two selected Release suites passed;
source-waveform physics still shares TonewheelBank and is not independently
validated by that routing oracle. Agent 48's navigation work is recorded above.

Agent 49 audited M0–M9 requirements against actual source/tests and recorded open
physical/native-product gates. Agent 50 produced a real four-second, 192,000-frame
nominal dry-organ WAV with a seven-file evidence bundle and eight independent
reports. The WAV SHA-256 is
`9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd`;
the original manifest and its dirty `6c3dd8b` checkout context remain unchanged.
Actual float peak was 0.08130008727312088, RMS 0.02006219567993473, with zero
reported clipped samples. This is synthetic engineering audio, not acquired
instrument evidence.

Agent 51 independently rebuilt a clean `6c3dd8b` source archive. The local GCC
Release renderer executable and resulting WAV were byte-identical to the retained
original. Seven new portable demo methods and the existing 27-method verifier
suite passed. A reproduced absent historical executable beneath a symlinked
directory required an availability check before strict present-file checks;
retained bundle bytes were not edited. This observed replay does not establish
authenticity, source-to-binary provenance or cross-compiler output identity.

Agent 52 read atlas pp. 109–156 and wrote twelve M3 event/history scenarios plus
four numerical/compatibility gates, all explicitly proposed and unrun. Agent 53
provided exact revision/profile identities, runnable commands, ranked next work
and guarded publication/rollback guidance. Agent 54 read every original note
01–53, checked PDF/review coverage and publication ancestry, and retained sixty
assignment rows without counting the separate continuation's workers. Its exact
54-agent archive check passed. All six original wave-09 assignments are complete.

### Final reviews and preserved contact/percussion modules

Agent 55 reproduced a one-ULP control-expression persistence error under downward
and toward-zero rounding. Scoped nearest rounding now matches the decimal parser
and restores the caller's mode. The new fixed-vector test failed before repair;
three affected Release suites passed afterward. The format remains B3CONTROLS1.
Agent 56 reproduced two controlled-error gaps: an absent historical renderer below
a regular-file ancestor raised NotADirectoryError, and an escaped lone Unicode
surrogate escaped factory validation as UnicodeEncodeError. The repairs preserve
present-file integrity checks and reject invalid UTF-8 strings/keys before
canonical hashing. Factory 22, demo eight and verifier 27 methods passed locally,
with zero skips. All frozen profile, transcription and demo identities remain.

Remote `main` then advanced to `7a24a30`, a direct child of `6c3dd8b`. Its nineteen
paths were inspected and verified disjoint from local changes before integration.
It adds standalone ContactBank/PercussionState components, ConsoleModel, model
metadata and independent tests. The original renderer, Engine and saved-state
format are unchanged. This incoming commit and its separate twelve completed
worker notes are preserved, not counted in the original sixty. Its planned
B3CONTROLS2 and Engine integration must retain the rounding repair. The combined
snapshot needs a new clean full build and hosted matrix; historical passes are
not promoted to qualification of these additions.

### Published combined code, demo and final platform qualification

The coordinator explicitly staged the intended demo WAV and compiled-profile
data, which the general binary-output ignore rules otherwise omit. All seven
bundle files retained their original bytes. Exact staged tree
`58cb96a7b620e63a94be2d062b7cf71f9c207a02` was archived into a clean source
directory, configured and built with local GCC 14.2 Release. All 26 CTest suites
passed; the complete LastTest log contains 14 Python groups totaling 274 methods
with zero skips. JUnit has 26 cases, zero failures and zero skipped nodes. The
source archive passed all five groups with exactly original notes 01–56.

Agent 59 had identified an incoming metadata-test portability gap: /dev/full
requires a platform-specific skip. With coordinator authorization, that method
now attaches a real temporary read-only file handle to the child stdout and
requires a nonzero exit, the exact exporter error and unchanged destination
bytes. The old Linux device check and the new real-handle reproduction passed;
the affected seven-method suite passed locally without skips. Production model
code and output semantics were unchanged.

The GitHub tree assembled from the intended text blobs and exact WAV blob matched
the tested tree. Commit `61c6ecbd87f46a91b4d0d975c823eeae2e2fb3f8` was created
on exact parent `7a24a30acd111a8f85cb8df65ba2ca59ada456e3`, then published to
`main` with the expected-head guard and no force. The coordinator fetched that
commit and moved the local index to that exact published SHA without discarding
active final-review files. Original completed notes 01–56 and all sixteen demo
package files are in the commit.

Actual hosted [run 43368537860](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43368537860)
passed Linux GCC, macOS AppleClang and Windows MSVC Release plus Linux
ASan/UBSan/leaks at that exact commit. Agent 59 downloaded all four full archives,
verified ZIP digests and revisions, matched all 26 registered names, and counted
274 actual Python methods with zero skips/disabled/failures in each job. The
metadata output-failure method executed on every platform. The sanitizer test
step explicitly enabled leak detection and fatal diagnostics; all 22 compile
commands and fifteen executable links were instrumented. The coordinator also
observed the live successful run and independently reconciled the four retained
source revisions, JUnit counts and complete Python totals. Detailed identities
and limitations are retained in the final platform review and CI qualification.

Agent 57 reviewed complete current/historical claims and navigation, directly
read twelve relevant atlas pages, checked identities and parsed 29 shell blocks.
Its concrete stale-state/navigation findings were corrected; the percussion
queue now explicitly integrates the existing module. Agent 58 independently
checked preserved incoming ancestry, unchanged PDF/demo identities, actual
versus proposed APIs and a bounded 220-path payload inventory. Neither worker
performed a broad DSP rerun or promoted source/document checks to physical
qualification. Their completed reports join the final documentation publication.

### Original sixty-agent session completed

Agent 59 returned its completed four-platform audit. Agent 60 then independently
verified committed ancestry, unchanged source PDF/manifest, complete page-range
coverage, all sixteen demo paths and frozen identities, the sixty unique original
assignment rows and the separate continuation namespace. It rechecked all four
raw CI source revisions, JUnit/full Python totals and ZIP digests, and reviewed
the updated operational handoff. Its focused verifier/compiler checks and 21
shell-block syntax checks passed; the source checker passed all five groups
with sixty retained notes. It introduced no source/test/data change and made no
claim that the coordinator's subsequent publication had already occurred.

The coordinator received actual completed results from all sixty distinct workers
and marked all ten waves complete. The final handoff names existing modules,
current legacy audio/state behavior, required M3 integration tests, actual custom
model metadata and parallel physical acquisition. Permanent AGENTS instructions
now also point directly to the operational handoff and original assignment record
while requiring fresh code/ownership/revision checks. Current status and evidence
addenda name the qualified `61c6ecb` result; older failures and review snapshots
remain preserved.

The completion record changes documentation only after `61c6ecb`; source, build
configuration, tests, model data and the retained demo stay unchanged. The final
archive must pass the explicit sixty-note source/link/identity check before the
expected-head publication, with the resulting remote tree and hosted run observed
by the coordinator. The commit containing this record identifies the final
documentation revision without inventing a self-referential commit hash.

The final clean source-archive check was executed with `--expected-agents 60`:
all five groups passed, zero errors, exact original IDs 01–60, eighty chapters
covering 500 pages, 131 Markdown files and 731 local links. A separate ledger
assertion verified sixty unique completed rows and six correct IDs per wave.
All intended changed files are Markdown, their whitespace/UTF-8 checks pass, and
no code/build/test/data/demo path differs from the qualified `61c6ecb` checkpoint.
The coordinator repeats the archive gate on the frozen publication tree after
retaining this result; full DSP reruns are supplied by that commit's hosted workflow.


## 2026-11-13 console continuation

The owner requested another complete PDF review and sixty actual new agents in ten
waves. The continuation starts from `9c8068c`; prior assignments remain separate.
Notes and the wave ledger are under `development/2026-11-13-continuation/`.
Assignments 01-06 read every page in six disjoint ranges and retained visual checks,
full-plan findings, model boundaries and an exact M3 entry task. Commit `5dcd942`
published these notes and the standing continuation rules in `AGENTS.md`.

Assignments 07-12 implemented independently testable value-owned contact and
percussion modules, the explicit console contract, analytic tests and compiled
factory metadata. Incoming `7c2ad20` and `6c3dd8b` were integrated without discarding
active work. The publication `7a24a30` has tree
`fe2704e72f326f24e09baed98295f26a35db9783`; a clean archive of that exact staged tree
passed 24/24 Release CTest suites. Hosted run 43366836424 subsequently passed all
four configured jobs, including leak-enabled Linux sanitizer execution.

Assignments 13-18 connected the modules to Engine, strict v1-to-v2 musical-control
migration, percussion events and renderer options. Independent tests cover shared
source audio, all nine contact thresholds at three rates, finite shared recovery,
zero-time routing/restore behavior, panic separation, arbitrary block partitions
and rejection atomicity. The renderer suite retains its original 20 methods and
adds 14. Thirteen separately retained legacy-render comparisons matched WAV bytes
exactly; removing only the three schema/model additions left identical old metrics.
Permanent tests do not depend on the saved old binary or a session path.

Assignment 19 added four stable percussion IDs to the proposed registry. All 39
old complete records retain the independent canonical digest
`61669b54e0a0499da950ece28c855e70ab4cb815d204f625f0aee8542d8b4f1b`;
24 parameter methods passed. Registry documents are schema 2; saved controls have
a separately specified B3CONTROLS1 migration. Assignment 20 migrated the evidence
producer to strict manifest schema 2 with explicit contact/percussion parameters,
argv and model identities. Assignment 22 preserved all 19 producer methods and
added eight; 27/27 passed against an actual renderer, including all 24 console
option combinations. Independent verifier migration and the new console catalog
complete wave 04 before the combined checkpoint is published.

No physical contact calibration, complete AO-28 percussion circuit, pedal audio,
scanner, cabinet or native host gate is closed by this nominal software work.
The integration checkpoint's full staged tests and hosted results must be recorded
separately from the earlier standalone-module qualification.


### Incoming review fixes and integration checks

Remote `main` advanced to `61c6ecb` while wave 04 was active. Its audible v1
bundle, factory runtime acceptance, original assignments 45-56, rights inventory
and prior-session handoff were retained. Hosted run 43368537860 passed all four
configured jobs at that incoming commit. A three-way integration preserved the
nearest-rounding serialization repair inside the new B3CONTROLS2 writer and kept
the historical renderer-availability handling in the versioned verifier.

The first merged-source compile exposed the incoming rounding test's old
`kCanonical` name, replaced by explicit legacy/v2 fixtures in the migration tests.
The test now exercises expression-underflow rejection for both versions under
all four standard rounding modes. No original historical input was rewritten.
The pre-merge working integration passed 26/26 suites; the merged checkpoint needs
its separately recorded clean full gate and new hosted qualification.


Assignments 21-24 finished the independent version-selected verifier, comprehensive
producer tests, three separate console fixtures and the end-to-end PCM acceptance
layer. Schema1 historical bundles remain supported without rewriting their bytes.
The new console catalog passed four methods/nine actual renders; independent fits
had maximum residual 0.526824 PCM units below the declared two-unit allowance.
The end-to-end suite passed three methods/18 verified bundles and 27 analytic
windows; its largest error was 2.062 percent of its own quantization-derived bound.
The incoming demo/verifier/rounding/metadata merge gate passed 4/4 after the fixture
name correction. The combined exact-source gate is the next publication step.


The first combined full gate passed 29/30 suites. The historical catalog
deliberately accounts for every top-level `.events` file. Root preserved that assertion and all five
legacy fixtures by moving the three new scores and their catalog into
`examples/fixtures/console/`. Their bytes/hashes are unchanged; current replay
commands and the new test use the new location. The console catalog now also
rejects unlisted `.events` files in its own directory. The assignment23 note retains its
original pre-integration path listing.


The corrected console integration source tree
`f1b5ac9ca543fcb51bac5360c2c0c782c5a6166d` passed **30/30 Release CTest suites**
in 8.63 seconds. Before publication, remote `main` advanced to `7bbd8e7` with
Markdown-only completion of all 60 original assignments. Those historical notes,
reviews, stronger handoff and standing instructions were integrated. No runtime,
fixture, build or test bytes changed in that incoming revision. The current
continuation keeps its own separate assignment count and current M3 status.


### Console publication and observed portability repair

Commit `4ead769` published exact tree `c4890143cb7ea17bfcd1a8cfcbfdc3733d87784d`
after all 30 Release suites passed (6.85 seconds on the final tree). Remote commit
and tree were verified. Hosted run 43369940466 passed Linux Release and the
leak-enabled sanitizer job; Windows/macOS each passed 29/30 suites. Their full
logs identified the new producer assertion's unresolved temporary-path spelling:
Windows short versus long user directory and macOS `/var` versus `/private/var`.
The canonical invocation was correct. Root reproduced the same assertion locally
using a real output path containing `..`, then corrected the expected path while
preserving full exact argv checking. All 28 producer methods passed in 4.355 s.
The retained CI repair review records the IDs, failure boundary and follow-up gate.
Only this test and documentation are in the repair; wave 05/06 files stay separate.


The repair was published as `72b5062` with verified tree
`81bbceb5b01673f1412026fefb83da1442ce5aae`. Its staged source passed all 28 producer
methods (4.082 seconds) and all five archive groups. Hosted run 43370542634 passed
all four jobs, including leak-enabled sanitizer execution. The observed canonical-
path portability failure is closed; its original failure evidence remains retained.

### Wave 05 bounded host-input foundations

Assignments 25-30 implement and independently test fixed note ownership, native
normalized-parameter mapping and a transaction that commits ownership only after
Engine accepts translated notes. The original physical-key API remains idempotent.
All 43 parameter targets preserve their fixed IDs and exact quantization boundaries;
the bridge is independent of JSON parsing and any host SDK. Independent owner tests
passed 2,127 calls, 2,264 atomic rejection/future probes and 5,226 expected physical events.
Native conversion tests passed 5,635 comparisons and 25,243 rejection checks across
all 43 Engine targets and all four floating rounding modes; eight Python methods
used 97 actual metadata CLI calls. The independent input transaction suite passed
44 rejection/future probes, 66 timing partitions and 459,896 exact audio comparisons.

One initial scratch harness linked an older library against concurrently changed
TonewheelBank headers, producing an ABI mismatch. Agent 29 froze a coherent source
snapshot and reran the unchanged harness successfully (17,844 assertions); agent 30
independently qualified its own frozen snapshot. No wrapper correction was needed.
`AGENTS.md` now explicitly requires coherent source/header qualification and keeps
unfinished runtime edits outside publication snapshots. A full combined staged
checkpoint and hosted run still qualify these new runtime paths separately.


Wave 05's clean staged tree `3f50aafc240100d888870e55bc0062d136de45d0` built under
strict GCC Release and passed all 34 CTest suites in 9.02 seconds. It was published
as `093d985150a5d7e18b9c210126af0f08504024ce`; remote commit/tree were verified.
All active lifecycle header/source changes remained outside that checkpoint.
Hosted run 43371559575 provides the new checkpoint's own platform gate.


### Wave 06 phase-preserving sample-rate lifecycle

Hosted run 43371559575 completed successfully for the prior native-input commit
`093d985`: Linux GCC, macOS AppleClang and Windows MSVC Release, plus Linux
ASan/UBSan with leak checking. Wave 06 adds explicit rate transactions to the
source, contact, shared-percussion and Engine layers. Each validates candidates
before installation; no sample elapses and all musical history is preserved.
Same-rate requests are exact no-ops. Owned source parameters can reject an
otherwise supported rate when its increment falls outside `[2^-53, 0.5)`.

The four implementation assignments retained independent module oracles and
coherent Engine smoke evidence. The Engine core was frozen in staged tree
`4370375d5dfe2161d8eefbf492cd692f2613d9c6` before the next wave's partial-key edits.
Assignments 35/36 qualify that immutable core with separate Engine and owned-input
acceptance suites. The lifecycle contract records mixed-rate seconds as the sum
of per-segment frame counts divided by segment rates, and separates this stopped/
same-thread API from native host/device transitions. The complete staged gate
and its publication are recorded below when observed.

The independent Engine gate passed 4/4 focused suites, including 36 rate-pair
scenarios, 36 detector-edge scenarios, 81 rejected transitions and 32603 exact
future samples. The separate owned-input lifecycle suite passed 1/1, exercising
12 mixed-rate runs, 14 rate rejections, 42 input rejections and 50 future probes.
Both used immutable tree `4370375` plus only their own test, and found no production
defect. All six wave-06 notes are retained before the combined gate.


The combined wave-06 staged tree
`b204d1d91e473929fc92b5563bc97274dd2e2966` built in strict GCC Release from a
clean archive and passed **39/39 CTest suites in 8.80 seconds**. The archive
contains all five new lifecycle suites and the prior ownership, console, evidence
and install gates. Active wave-07 source and build changes were excluded from
this checkpoint. Final publication and hosted results are tracked separately.


Wave 06 was published as `53bb6e1e37eedf84f566ffb8bd9037b50f123a20`, exact tree
`c88d2f0a6749cf79b7310c131b4f5d335c7d6ab3`. Its final archive matched every staged
blob and passed all 39 Release suites in 7.47 seconds. The expected-head update
and remote commit/tree were verified without altering active wave-07 files.
Hosted run 43372984603 passed all four jobs: Linux GCC, macOS AppleClang and
Windows MSVC Release, plus Linux ASan/UBSan with leak checking.


### Wave 07 explicit partial-key input and observable console behavior

Assignments 37-39 append `KeyPosition` as event 9, preserving earlier event values.
Nominal travel retains a finite target in `[0,1]` without resetting current
position or contact history; ideal mode accepts endpoints only. Ordinary positive
NoteOn now commands full press after a partial hold. The offline renderer,
producer and independent verifier accept the new score command with mode-aware
preflight. Schema 2 retains its existing structure; schema 1 rejects the new command
and historical bundles remain valid. Saved controls and permanent parameter IDs
are unchanged.

The independent new tests passed both focused suites, including seven Python
methods. They check 234 exact state pairs, 51513 identical rendered samples,
768 independent current-phase audio predictions and 51 atomic rejections.
Nineteen direct CLI calls, two independently verified new bundles and three-rate
PCM checks cover early rejection, partial harmonic onset, block partitions and
legacy evidence compatibility. Maximum analytic float-sample error was
9.29094e-10; maximum independent PCM amplitude error was 7.02819526653e-7.
The changed production parsers also passed all 96 historical renderer/producer/
verifier methods. Each scoped build used a coherent frozen source snapshot.

Assignments 40-42 supply deterministic current-state CSV traces, independent
numerical/CLI acceptance and bounded SVG visualization. Their actual results and
the combined publication gate follow when observed.


The trace exporter uses three fixed 120 ms scenarios and public Engine snapshots.
Each row pairs the state after current-frame events with that same frame's audio,
before state advancement. It records 28 metadata comments and 36 numeric columns;
profile provenance is explicitly declared, and atomic hard-link publication
preserves existing destinations. Assignment 40 passed nine scenario/rate exports
and 22 protected-output/malformed-input checks. Its largest CSV was 2392173 bytes
under the 8 MiB limit.

Assignment 41's independent suite passed ten methods and 62 actual CLI invocations,
checking all 67716 rows across the three rates and scenarios. Exact rational
travel, separate hysteresis, closed-form readiness and independent source/audio
calculations bound maximum observed errors to 1.42248e-16 position, 7.67165e-14
readiness, 2.07723e-13 phase turns and 3.72430e-9 audio. Competing publishers produced
one complete expected CSV with no temporary residue. These are nominal software
checks, not physical captures.


Assignment 42 adds a standard-library CSV-to-SVG tool with strict bounded schema
validation, input-byte SHA-256 provenance and atomic no-clobber publication. Exact
contact/target transitions are retained; continuous trajectories and audio use
documented extrema-preserving time bins. All 11 Python tests passed, including
write/flush/close/link failures and output races. All nine actual traces plotted
successfully, producing 113384–119631-byte SVGs below the 1 MiB cap. A rendered
48 kHz partial-key figure was visually inspected with no clipping or overlap.
The first two QA rendering approaches were unavailable; installed librsvg/Cairo
completed the inspection without a new production dependency. All six wave-07
assignments are complete before the combined gate.


The combined wave-07 clean Release archive of staged tree
`1132e9cf242997473b87dd64a8a65086580d594c` passed **43/43 CTest suites in 12.59
seconds**. That gate includes all partial-key, trace and plot tests plus the
previous lifecycle, ownership, evidence and legacy-install suites. Active wave-08
CMake/install, realtime-audit and benchmark changes were excluded. Only this
result's Markdown recording changes before publication; the final archive is
checked for exact unchanged runtime/test blobs and current repository integrity.


Wave 07 was published and remote-verified as
`9a5c99a862daf26a2bab9b05613c98803727a3e7`, final tree
`a85f1bcb43d2815b6f661172f7ab394ad34bee7e`. The only difference from the full
43-suite tested tree is three Markdown result records. Every final archive blob
was verified against the staged tree and all five repository integrity groups
passed. Hosted run 43375043990 passed all four jobs. Each completed archive contains
43 suites and 352 Python methods with zero skipped, disabled or failed tests.
The independent platform review verifies complete logs and artifact digests. Active
wave-08 install, realtime and benchmark work remained outside this commit.


### Wave 08 enabled paths, relocatable tools and compatibility

All six assignments 43-48 are complete. The new allocation gate observes zero
C++ allocation/deallocation calls across 81 Engine calls, 45 owned-input calls,
six translations and 137 parameter calls, plus 14 separately labeled stopped
lifecycle calls. Calibration detects 12 allocations and 12 frees. The audit
corrects the conservative coefficient-work bound to one complete rebuild per
rendered frame: contact edges can change connectivity without new input events.
This does not establish a native callback deadline or general system-allocation
interception. The independent runtime-boundary review found no actionable defect
and passed its six selected suites.

OfflineTools now installs 16 files: four native tools, the standalone plotter,
the compiled profile, both catalogs and eight scores. The focused relocation
gate moved the prefix, removed HAMMOND_* environment inputs, and ran from an
unrelated directory. Installed/build WAVs, metadata, traces and SVGs matched;
missing profiles rejected without output. The pre-build install rejection also
preserved its destination.

Opt-in console_motion, owned_input and console_all workloads preserve legacy
benchmark defaults and use a separate report identity. The six-method gate passed
33 actual CLI calls and exact workload/accounting checks without speed thresholds.
It found and repaired a real buffered-stdout error: the old one-case JSON/help
path could return success on a readonly output handle. Explicit flush/checks now
reject both while preserving successful legacy report content and checksums.
The independent motion oracle's maximum error was 1.11023e-16.

The hosted audit verified complete logs and eight SHA-256-checked diagnostic
archives for the preceding lifecycle and partial-key checkpoints. Separately,
11 WAV/PCM pairs from a fresh 9c8068c source build matched current defaults,
11 default/explicit-ideal pairs matched, six partition comparisons passed, and
the retained schema1 demo verified unchanged. All 15 earlier metric fields remain
equal after removing only three declared schema2 additions. The retained older
executable has a different binary hash from the fresh baseline and is reported
as a separate cross-check. No runtime defect or audio mismatch was found.

Root registered the benchmark test environment after the install owner's frozen
CMake overlay. The combined staged archive and new hosted run now qualify these
changes together, independently of the earlier 43-suite checkpoint.


The combined wave-08 source tree
`0c722f1ffa2a2f04522438a4cb86cec6b8d3e392` passed **45/45 Release CTest suites in
12.91 seconds** from a clean archive. The new enabled allocation, benchmark and
expanded install gates all passed with the prior engine/evidence checks. An
initial status-text replacement matched an outdated heading and aborted; its
paragraphs were corrected before this gate, with no runtime/test/build changes.
Only Markdown result recording changes before publication; final archive integrity
and unchanged runtime/test blobs are checked separately. Wave-09 artifacts and
active handoff work remain outside this checkpoint.


Wave 08 was published and remote-verified as
`2046b9388f6aab1122e37646b2f20199b5c6079f`, tree
`759ddcaf93be2047a5732034663e565f728fb5ad`. The final archive differs from the
45-suite tested tree only in Markdown result records; all runtime/test blobs and
all five repository integrity groups were verified. Hosted run 43376892064 passed
all four jobs; root fetched each complete job log and observed all 45 suites
passing, including the expanded install and enabled allocation checks.
The active demo, next-pedal gate and operational handoff remain in wave 09.


### Wave 09 reproducible example and current developer handoff

Assignment 49 retained an original two-second nominal-console score and its
genuine schema2 bundle, five PCM measurement reports, provenance, and a separate
120 ms diagnostic CSV/SVG. The complete example contains 18 files and 1774391
bytes. The WAV reports zero clipping, peak 0.19528882205486298 and RMS
0.037407620567908695. Block sizes 64 and 127 produce identical WAV bytes; the
final 160 ms is exactly silent. The source was an exact archive of `9a5c99a`,
with all 296 blobs checked before and after generation. Root intentionally staged
the ignored WAV and compiled profile, verified all 18 staged files against the
worker's inventory, and independently verified the bundle extracted from the
staged tree. Its WAV SHA-256 is
`3cbfc2a80ee5ed014782d9abe33d5afc2cd7e494f3efdba280939b4d3d8f56b5`.
The separate partial CSV/SVG match the previously inspected diagnostic bytes.

Assignment 50 chose the next executable M3 slice: typed admission of the complete
25-by-8 pedal map, then a fixed-storage four-bus reference kernel using the
existing shared source frame. It preserves 200 contact positions, five explicit
disconnections and seven repeated-source pairs. Proposed normalized fixture
weights remain separate from unknown physical voicing/loading. Playable events,
controls, ownership and migrations follow a separate integration gate. Forty
complete relevant atlas pages and the actual data were inspected; both map and
factory-reference validators passed within their declared documentary scope.

Assignment 51's current operational handoff gives the first 30 minutes, coherent
build and tool commands, ownership/state/lifecycle boundaries and standing
publication procedure. Five bounded read-only command checks and all 38 scoped
links passed. The next navigation, identity and accounting assignments finish
this wave before six independent final reviews.


### Wave 09 identity, navigation and separate accounting complete

Assignments 49–54 are complete with 54 distinct dispatched identities and 54
retained notes in the new continuation; six wave-10 slots remain planned. The
navigation review checked 221 relative links and two anchors. The identity audit
confirmed unchanged PDF/profile/map/legacy-fixture bytes, all 39 original control
records and exactly four appended IDs, and passed both migration suites plus a
retained schema1 bundle verification. The original event values are 0–7;
percussion and KeyPosition were appended as 8 and 9 respectively.

The new bounded continuation checker validates this session's manifest and notes
independently of the original sixty. Its 12-method focused suite passes; the
actual 54-complete gate passes and the 60-complete gate correctly rejects the
unfinished final wave. Six older notes received labeled explicit owner-line
normalizations without changing their original evidence prose. Assignment 18's
identity-only follow-up reconfirmed its existing worker and adds no assignment.
The combined source archive is the next publication gate; focused checks do not
claim that gate or the new checkpoint's hosted results in advance.


### Frozen wave-09 gate and final-review findings

The exact staged source tree `805900d2339eb3975019581de5f8469e72e7509f`
built in Release and passed **46/46 CTest suites in 42.55 seconds**. Both the
original sixty-note repository gate and the separate 54-complete continuation
gate passed on that archive. Root independently verified its retained schema2
bundle and WAV hash. One preliminary verifier invocation used a nonexistent
filename; the corrected `tools/verify_render.py` invocation succeeded and no
artifact was changed.

Independent wave-10 review then reproduced a case beyond those existing tests:
renderer help and a one-frame render returned success when their small stdout
writes were buffered to a read-only descriptor. The WAV had already been saved
correctly in the render case. Assignment 57 owns an explicit flush/status repair
and regression; the next publication will include that correction and its own
combined gate. Assignment 56 is reconciling stale current-tense host-integration
instructions with the actual FIFO ownership, 43-control state and stopped
phase-preserving rate API. These are observed findings, not evidence that the
completed software or physical-instrument plan is fully qualified.


### Final review: runtime accepted and observed defects repaired

Assignments 55–57 are complete. The core review verified all 23 include/src blobs
against published `2046b93` and passed six independent runtime/lifecycle binaries.
The input review passed six ownership, parameter, persistence and mixed-rate
binaries, then corrected stale `HOST_INTEGRATION.md` and `NOTE_OWNERSHIP.md`
descriptions without changing runtime behavior. Their retained reports preserve
source identities, exact counters, limitations and the distinction between
implemented typed APIs and future native wrappers.

The evidence review reproduced both renderer stdout failures on the frozen
binary, added explicit flush/status checks and a permanent regression with two
subcases, and passed all **35 renderer methods**, zero skips, in a private coherent
Release build. The repaired block-size-257 replay exactly matches all 384044 bytes
of the retained two-second WAV. Both schema generations verify; independent PCM
window recomputation, exact CSV/SVG replay and seven no-clobber probes passed.
The render contract now explains that summary failure can follow successful WAV
publication. The core, profiles and historical artifacts were not changed.

All **60 actual workers have now been dispatched** in ten waves of six. At this
checkpoint 57 are complete and the final handoff, platform and readiness reviewers
are running. This is not yet a sixty-complete claim. Root's next combined source
gate includes the renderer correction and its regression; the earlier 46-suite
pass predates that repair and is not substituted for its qualification.


### Corrected combined candidate qualification

The corrected source tree `08d944734efcd1b7a8ed5a93392deabca70a178f` passed
**46/46 Release CTest suites in 14.68 seconds** from a new coherent archive and
build. The complete local log contains 24 C++ suites and 22 Python suites with
**371 Python methods**, with no skip reports. This includes the new renderer
stdout regression and continuation accounting suite. The actual 57-complete
continuation and original sixty-note source gates both pass; all sixty new
workers are dispatched, with the last three review outcomes still pending in
this publication snapshot.

The remote unreferenced Git tree independently equals this exact tested source
tree, including the WAV, compiled profile and trace assets. Only Markdown result
records are added for publication; root verifies unchanged code/test/data blobs
and the resulting full archive separately. No branch update or hosted result is
claimed until its actual publication is observed. The final reviewers' active
files remain outside this checkpoint.


The corrected candidate was published and remote-verified as
`6bdce067ecdfa2b918113e254ed0ae706fdc9b43`, final tree
`6f7948c1cc83945f2ca872b96e668de3796cf8a5`. The expected parent was `2046b93`;
the update used the expected-head guard with force disabled. Root fetched and
verified the commit/tree, then moved only the local branch reference while
preserving active final-review files. All runtime, test and artifact bytes match
the 46-suite tested tree; the four final Markdown result records and all 344
archive blobs were checked separately. Hosted run 43380337294 was observed in
progress, and assignment 59 owns its independent complete-log qualification.
Assignment 58's navigation/handoff review is now accepted, bringing the working
manifest to 58 complete and two running. The published manifest correctly retains
its earlier 57-complete snapshot.


### Windows accounting failure and explicit CRLF regression

The first corrected candidate run `43380337294` passed Linux/macOS Release and
ASan/UBSan/leaks, but Windows passed only 45/46 suites. Its accounting suite had
three failures and three errors because bounded raw reads preserved the CR in
CRLF fixture owner lines. All 35 renderer methods passed, including the stdout
repair. Root and assignment 59 independently reproduced the CRLF rejection on
Linux; the [repair record](reviews/CONTINUATION_CRLF_REPAIR.md) retains the failed
job and diagnostic archive identity.

Root added an explicit CRLF regression, observed it fail before the correction,
and normalized CRLF only after the raw-byte bound and UTF-8 decode. Strict owner
and duplicate-owner rules remain unchanged. All 13 accounting methods now pass,
zero skips, in 0.125 seconds; the actual 58-complete progress gate also passes.
Native source, headers, renderer, profile and retained audio bytes are unchanged.
The repaired archive and a new hosted run are the next gates. No worker was
added or counted again for this integrator repair.


The CRLF repair was published and independently remote-verified as
`7469ebf759ced820cc34fc9012beff6f772e4b89`, exact tree
`096e2cd13c5aa3fc40e996c923ed80be36b0f622`. Its coherent archive passed all
13 accounting methods in 0.179 seconds, the actual 58-complete continuation gate
and all five original source-integrity groups. All 347 archive blobs matched.
Only the accounting tool and its test changed beyond Markdown and assignment
records; native source, headers, renderer, build configuration and retained
artifacts remain byte-identical to `6bdce06`.

An initial batched publication-payload read aborted before a remote commit or
reference update; a single reread succeeded. The temporary payload helper now
checks a read-only index-entry digest rather than calling `write-tree` from
parallel readers. The unchanged staged tree, completed remote tree, expected
parent and fetched commit were verified before continuing. No force update or
worktree reset occurred.

Hosted repair run 43380966473 was observed in progress. Assignment 60's final
readiness report was accepted afterward; its note retains the actual first-run
Windows failure and root-owned repair qualification gates. The working manifest
then correctly reports 59 complete and only assignment 59 running, with all
sixty actual workers dispatched. Earlier published progress snapshots remain
historical records rather than being silently rewritten.


### Final sixty-worker completion and qualified software baseline

All sixty actual continuation workers have completed their assigned scope and
retained a substantive note; the integrator accepted assignment 59's final
platform report last. The actual manifest now has **60 complete, zero running,
zero planned, sixty distinct canonical identities and sixty numbered notes**, in
ten waves of six. Its explicit `--expected-complete 60` check passes. Earlier
original-session notes and assignment 18's identity-only follow-up were not counted
as new workers. All six final review files are retained.

The repaired code `7469ebf759ced820cc34fc9012beff6f772e4b89` passed every job of
hosted run 43380966473. Each complete archive contains 46 suites (24 C++ and 22
Python), 372 Python methods, and zero failed/disabled/skipped tests. Actual CTest
durations were Linux 24.66 s, macOS 27.36 s, Windows 44.51 s and sanitizer 42.82 s.
Assignment 59 verified all twelve diagnostic archives across the earlier
45-suite checkpoint, failed first candidate and repaired run. It independently
confirmed actual sanitizer instrumentation and leak settings, enabled allocation
counts, the 16-file relocated install and the bounded 33-call benchmark gate.
Root also fetched all four repaired-run job logs and observed their passing totals.

Final entry points now lead to the completed actual-state manifest, exact
qualified code/run, six final reviews and the next prepared pedal-routing gate.
The final result commit changes only Markdown and assignment state records; its
archive must pass both separate explicit sixty gates, focused accounting tests,
source/link checks and byte comparison against the qualified code/test/data.
Root then publishes with the expected-head guard, verifies the fetched commit and
tree, checks that the working tree is clean, and observes that final commit's CI.
These integrator publication actions are distinct from worker completion and do
not create a sixty-first assignment.


### Final archive gates observed

The completed-result archive tree `d34b4d94ffff6d9c67065ebf3b38a23c1ec705aa`
passed both explicit final commands: the continuation reports sixty complete,
zero running/planned, sixty actual identities and sixty notes; the original
repository checker separately reports its original sixty notes and all five
source-integrity groups passed. It checks all 500 PDF pages in the chapter index,
the unchanged PDF hash, data references and 1,221 local links across 202 Markdown
files. All 13 focused accounting methods passed, zero skips, in 0.152 seconds.

All 351 archive blobs (27,423,316 bytes before this result paragraph) matched
that exact staged tree. The 14 changed paths versus fully qualified `7469ebf`
are only Markdown and the actual assignment-state manifest; code, tests, build
configuration, data and retained audio/trace assets are byte-identical. The final
publication adds only these two Markdown result records, then rechecks archive
identity and both record/source gates. Broad DSP re-execution is unnecessary for
these records; the final commit's hosted workflow independently runs the full
matrix. The integrator verifies that actual result before the final user handoff.


## 2026-11-13 — new pedal session, source review and frozen baseline

Started from inspected remote `main` at `b4fc61ccfcc59724f14fb0cee947ed7bb7142075` in an independent clean checkout. The user requested sixty new agents in ten waves and continued development with commit/push and future-agent handoff rules. Created the separate `2026-11-13-pedals` actual-state ledger; the original and console continuation records are preserved. Updated AGENTS.md to point to the newest session and retain the standing workflow.

`pdfinfo` confirmed all 500 pages; `pdftotext -layout` extracted every page into six temporary disjoint review ranges. The first wave has real assigned readers and selected image inspections. Source bytes are unchanged.

The initial `cmake` attempt failed because CMake was absent. Installed CMake 3.31.6 in task-local tooling using the ordinary package route, then built a frozen `git archive` of the baseline with GCC 14.2.0 and Python 3.12.14: `cmake -S baseline -B baseline/build -DCMAKE_BUILD_TYPE=Release`, `cmake --build baseline/build -j 4`, `ctest --test-dir baseline/build --output-on-failure`. Result: **46/46 suites passed, 0 failures, 48.19 seconds**. The retained baseline executable will support exact legacy-audio comparisons. This is local baseline qualification, not a new-code or new hosted-CI result.

Wave 1 completed with six new workers covering all 500 pages, retaining individual notes and selected diagram inspection. Root also read milestone pages 445–450 directly. Review confirmed the existing kernel gate, explicit nominal mixture permission, 36+2 retained drawbars, Great/pedal routing, separate percussion, unchanged parameter identities and physical-calibration boundaries. The baseline GitHub run 43381864079 at b4fc61c was independently observed completed/successful. Wave 2 now owns the typed kernel, strict generated-data compiler and two implementation contracts.


### Pedal routing checkpoint — twelve new assignments complete

Wave 2 implemented `PedalRouting`, the strict documentary compiler and two adopted contracts. Independent acceptance compares both CSVs at all 200 positions, exercises each contact/all 91 source basis frames, preserves five disconnections and seven repeated-source pairs, tests transaction/domain failures, and checks coherent source histories across block/rate changes. The allocation probe calibrated all 12 relevant new/delete pairs then observed zero allocations/deallocations in 4,130 measured regions; it is scoped C++ instrumentation, not a device deadline claim. Separate worker notes retain counts/tolerances/identities.

Root archived staged tree `81b1c30436a239d8c04ffcd1ec658d356eb81acc` before any wave 3 header changes, then configured/built GCC 14.2 Release with CMake 3.31.6 and ran all 51 CTest suites. **51/51 passed, zero failures, 67.83 seconds.** The final result metadata/Markdown is checked separately against that coherent tested code tree. Runtime pedals remain a following integration gate.

Command-line Git write authentication was unavailable (`could not read Username`); the connected GitHub account retained verified write permission. Root published the first checkpoint through Git tree/commit/reference tools with an expected-head guard, observed exact tree equality, fetched commit `6a38805ea072627f383d9eb988d735dc259db472`, and aligned only the local branch reference with the identical published tree. Index and working files were preserved. Hosted run 43392041624 was later observed successful. Subsequent checkpoints use the same verified tree/expected-parent procedure; no force update is authorized.


### Nominal pedal Engine checkpoint — eighteen new assignments complete

Wave 3 added the original named `nominal-static-pedal-mixture-v1` matrix and `linear-pedal-position-v1` gain; two controls and strict `B3CONTROLS3` serialization/migration; Engine events 10–13; independent pedal held/contact state and tagged last-rendered diagnostics; and registry schema 3 with 45 records. The previous 43 full records are frozen independently in a retained v2 fixture. The Engine consumes one shared source frame and skips adding zero pedal contribution to preserve legacy arithmetic. Physical reactor loading and timbre remain unmeasured.

The independent integration assignment used both pedal CSVs and separately written integer-numerator mixture equations. It executed 2,203 oracle frames, 32,600 contact checks, 200,837 bitwise source-phase comparisons, 17,676 partition comparisons and ten late-invalid future-audio checks, with no runtime defect found. Other focused notes retain state, parameter, voice and runtime acceptance counts. These focused results do not substitute for the combined publication gate.

Pinned the official VST3 SDK 3.8.1 root and four submodules, verified the relevant MIT/Unlicense inventory, and built its headless validator outside the repository. Its own 51 selftests pass; no Hammond plugin has yet been built. The implementation contract freezes original processor/controller UUIDs, three native input buses, explicit software pedal mapping, 45 descriptors, piecewise-linear automation including offset-N endpoints, a bounded state queue and race-free publication. Ordinary project builds remain SDK-free.

Root's first frozen combined archive `24f80c3e8405fa0a49500a080967279e615a9b97` built cleanly and passed 54/55 Release suites in 57.72 seconds. `test_realtime_console` failed its fixture count at line418: a 45-element controls array still received 43 entries. Added the two appended pedal control events at position zero, retaining the earlier manual workload and its evidence boundary. Reconfigured/built repaired tree `e1828586c35ea40562d6de6be671c206d725edd2` in a separate archive and reran the complete gate. No active wave-4 source/header files enter either snapshot.

The preceding kernel commit `6768ef2388819ebbaaf7cc23bdf72265dc72c561` was verified after connected-account publication. Hosted run 43394209142 completed successfully on all four configured jobs; root inspected each job result, including the leak-enabled sanitizer gate. Local branch metadata was aligned only after exact tree equality; concurrent work remained untouched.


The repaired frozen tree `e1828586c35ea40562d6de6be671c206d725edd2` passed **55/55 local Release CTest suites, zero failures, in 54.86 seconds**, with GCC 14.2.0, CMake 3.31.6 and Python 3.12.14. Final result records differ only in Markdown and actual assignment-state metadata from that tested tree. Hosted qualification for this new publication is a separate observed gate.


The nominal pedal Engine checkpoint was published as `e493b9fed9e3ed8a294fb5d95af447132776cb3a`, tree `056a912a1e407d8d0a842442463fd487bf907690`. Root fetched and verified exact local/remote tree identity. Hosted [run 43397574429](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43397574429) subsequently passed all four configured jobs: Linux GCC Release, macOS AppleClang Release, Windows MSVC Release, and Linux GCC ASan/UBSan with leak checking. The new input/renderer scopes remain outside that checkpoint.


### Pedal input and offline checkpoint — twenty-four new assignments complete

Assignments 19–24 completed explicit pedal ownership, a single ordered manual/pedal/control transaction, four renderer score commands and initial pedal registration, schema-3 evidence with strict historical 1/2 verification, exact legacy replay and independent mixed-input acceptance. Both owner adapters have independent 256-owner capacities; the combined call admits at most 1024 raw and emitted events and advances the Engine once. Rejected calls preserve owner ledgers, Engine history and caller output. The independent test uses hand-written physical timelines and a separate Engine, not the production translator as its oracle.

All eight retained scores and both catalogs/profile inputs are unchanged. Twenty-four actual local executions compared the frozen baseline with current default 00 and explicit 00 pedals: full WAV and PCM bytes and retained common metrics matched for 670,800 frames per variant. Two migration-test assumptions (the exact parameter dictionary and an old 1 KiB metadata-read bound) were repaired, with no production defect. The new evidence test separately verified both genuine retained schema 1/2 bundles unchanged and rejected 80 full-bundle mutations.

Root's coherent frozen tree `f84cacb4e6eb01189ca29136fc838885fdd858f4` passed **60/60 local Release suites, zero failures, in 56.10 seconds**. The final source/test identities remain unchanged; subsequent differences are Markdown results and actual assignment states only. Assignment 24's final test hash matches that exact tree. The new trace/metadata/catalog scopes belong to wave 5 and are excluded from this checkpoint.

Actual root commands used a fresh `git archive` of the staged tree, `cmake -S checkpoint-w04/source -B checkpoint-w04/build -DCMAKE_BUILD_TYPE=Release`, `cmake --build checkpoint-w04/build -j 4`, and `ctest --test-dir checkpoint-w04/build --output-on-failure --output-junit checkpoint-w04/ctest.xml`. The local toolchain remains GCC 14.2.0/CMake3.31.6/Python3.12.14. Publication uses exact Git tree equality and an expected-parent guard; hosted results for the new commit must be observed separately.


### Windows renderer argument repair

The wave-4 publication `6bcf35cd0c2a54eeb31fabfde8b40bdfcb5b1f51` was fetched with exact tree identity. Hosted run 43399562616 passed Linux Release, macOS Release and Linux ASan/UBSan+leaks. Windows built successfully but passed 59/60 suites: a full-width digit in `--pedal-drawbars` had become an accepted ASCII value before strict parsing. The [retained review](reviews/PEDAL_WINDOWS_UNICODE.md) records the exact job, failure, diagnosis and official platform references.

Root changed the Windows entry point to checked lossless UTF-8 conversion from `wmain`, constructs its three filesystem arguments explicitly as UTF-8, and adds the MinGW Unicode startup link option. Existing strict-parser checks remain; new regressions preserve non-ASCII controls and exercise actual Unicode profile/score/output paths. The repair touches no DSP/data. On coherent frozen tree `73b7bccb70de21c1dbe9e23ed0d1c1cb10fef3a7`, all 8 relevant Release suites passed, zero failures, 16.87 seconds. The repair's native Windows qualification remains pending until the next exact-commit hosted result is observed.


### Native Unicode regression passed; diagnostic text follow-up

At repair `8d05734`, Windows passed all 19 pedal renderer methods, including lossless Unicode paths and the original non-ASCII digit rejection. Run 43401628824 still failed one older renderer assertion because the early oversized-argument message omitted its established word `oversized`. Root restored that word in the Windows-only literal, without changing control flow, limits, parser or DSP. No local Windows execution is claimed; the next exact-commit hosted job is the meaningful closure gate. The full record preserves both observed failures.


### Windows repair closure and fifth-wave integration

Published `a451ebd3ebd3752cef982777a438cf78eda64b36` was fetched and its tree
`297325bed036ef40f3c64dd5ca1305abbc9250e4` matched the local committed tree
exactly. Root aligned local branch metadata without touching concurrent working
files. In run 43402590446 the Windows MSVC job 131808878321 passed all 60
suites, closing both the Unicode admission and diagnostic-wording failures.
Linux Release and Linux ASan/UBSan with leak checking passed as well; macOS was
still queued when this entry was written.

Fifth-wave frozen sources add a bounded actual-Engine pedal trace, compiled
model metadata, four independently checked pedal scores, the sample-linear
HostTimeline, StateExchange and enabled-path allocation audit. The timeline
retains offset-N endpoints for both current interpolation and next-boundary
application, uses exact existing discrete thresholds and commits the entire
callback only after all candidate slices succeed. StateExchange provides four
pending UI loads and coherent atomic publication; its focused Release and
ThreadSanitizer runs passed. The allocation test measured 180 actual API
regions with zero observed global C++ allocations/deallocations, including the
complete proposed callback protocol. These focused results do not qualify the
new native wrapper, which is assigned to wave 6. Root's full coherent archive
gate follows before fifth-wave publication.


The complete frozen fifth-wave tree `06786b70f1cffcc6371600fd6e14306f16e8c985` passed **65/65
Release CTest suites, zero failures, in 65.41 seconds**, using GCC 14.2.0,
CMake 3.31.6 and Python 3.12.14. Root configured and built a fresh `git archive`
under `checkpoint-w05/source` and `checkpoint-w05/build`, then ran
`ctest --test-dir checkpoint-w05/build --output-on-failure --output-junit checkpoint-w05/ctest.xml`.
The final result publication differs only in Markdown and actual assignment
metadata from that tested tree; ongoing native wrapper files are excluded.
Hosted qualification of the new checkpoint remains a separate observed gate.


### Fifth-wave publication observed

Root published `88c36b4a72a07f6498f73279f25023278accd350` using an expected-parent
reference update, fetched it, and verified identical tree
`354b1e7660c25435f2f97617450cc86e76b26ce3`. The staged code/test/data are
unchanged from qualified tree `06786b70f1cffcc6371600fd6e14306f16e8c985`; only
Markdown results and assignment metadata differ. Hosted run 43404272839 has
successful Linux GCC Release (131814611978), Windows MSVC (131814612087), and
Linux ASan/UBSan with leaks (131814611668) jobs. macOS 131814612136 is still
queued. The preceding repair run's queued macOS job later ended cancelled, so that
earlier run is not a four-platform success. Its precise cause was not yet
observed; the original inference that a newer workflow cancelled it is withdrawn. These observations
do not qualify the separate native module currently being implemented.


### Hosted macOS acquisition failure, before project execution

Run 43404272839 subsequently concluded failure because macOS job 131814612136
was never acquired by a runner. Metadata shows an empty runner name, zero steps,
and cancellation after about fifteen minutes. Its four check annotations state
hosted-runner acquisition failure and repeat the ARM64-capacity notice. There
was no checkout, build or test execution, and the log endpoint has no blob.
The Windows/Linux/sanitizer successes remain their actual results.

Root verified remote main remains 88c36b4, inspected the public check annotations
with a read-only API request, and requested one targeted job retry through the
connected GitHub Actions tool. Official GitHub guidance still lists macos-15
as supported; the public status page reported no current incident. Neither
observation overrides the concrete failed acquisition. Root does not change
platform labels or weaken tests to mark a pass; the new retry remains pending.
The earlier causal guess about a newer push cancelling the repair's macOS job
is withdrawn in the active record. See reviews/PEDAL_RUNNER_AVAILABILITY.md.


### Native integration review before the combined gate

The first actual SDK module validator reports 47 passed/zero failed/exit zero,
while retaining 16 teardown messages from conflicting repeated-deactivation
expectations and nine ERROR-labelled unsupported-rate setup rejections. Root
inspected the pinned ProcessFormatTest and repeated-state/teardown code; those
diagnostics are not counted as failures by the SDK. The module remains float32
at 44.1/48/96 kHz, with no altered DSP contract or patched SDK to hide output.
The independent module harness separately checks actual supported processing
and balanced lifecycle. Its first fixture underexercised manual audio because
it edited A while the default selector was B; the worker corrected the fixture
and added isolated audible division probes before its final gate.

After assignment 33 froze its build files, root added the build-only
`hammond_vst3_test_inputs` aggregate. Native CI can build all registered test
inputs then execute one verbose CTest/JUnit run, instead of keeping a duplicate
explicit target list or running the entire native suite twice. The upcoming
frozen integration gate verifies this small CMake change with the complete
module/ABI/behavior set.


### macOS retry recovered and fifth-wave matrix closed

The one targeted macOS retry acquired an ARM64 runner and ran all 65 suites:
job 131822086122 passed in 45.86 seconds. Run 43404272839 attempt 2 is observed
completed/success at unchanged commit 88c36b4; all four latest jobs are
successful. The initial acquisition failure and lack of execution remain in
the runner review. This closes the fifth-wave core/offline hosted matrix,
without inheriting a native-module qualification for later uncommitted code.


### Native module checkpoint — wave 6 accepted — actual native module and qualification path

Assignments 31–36 completed the native processor, controller/factory/stream
helpers, explicit pinned build and embedded profile, actual loaded-module ABI
and behavioral gates, and separate native CI with bounded artifact inventory.
All 36 actual workers in the first six waves have accepted substantive notes.
The native module uses original UUIDs, exactly 45 stable controls, three event
buses and the existing nominal core. It has no custom editor or device backend.

The independent ABI gate compared 229,725 frames, and the behavior gate compared
233,792 plain-Engine reference frames plus post-rejection paired-module output.
All compared audio was exact under the recorded Linux toolchain. The controller
gate checks all metadata, thresholds under four rounding modes and strict
1/2/3 state migration. The actual SDK module validator reports 47 passed/zero
failed while retaining 16 teardown and nine unsupported-rate diagnostics. Its
summary is not a warning-free, float64 or arbitrary-rate claim.

Explicit fresh SDK acquisition passed; the SDK-free build helpers and bundle
inventory passed 14 and 16 methods respectively. The actual four-file Linux
bundle and tar/copy transport preserve bytes/modes. Native CI has not yet run
at this checkpoint draft. Root's coherent full archive gate and publication
follow separately; active wave-7 CLI/install/allocation work is excluded.


### Sixth-wave coherent integration gate

Root archived staged tree `b2dae50dcde294bde8e7acb7addb14456197a779` into
`checkpoint-w06/source`, excluding all ongoing seventh-wave files and hooks.
A fresh SDK-free Release build passed **67/67 CTest suites, zero failures or
skips, in 78.43 seconds**. A separate native Release build of the same source
used the locked SDK and the new `hammond_vst3_test_inputs` aggregate, then passed
**4/4 focused native suites, zero failures or skips, in 5.23 seconds**. These
include the actual module validator, controller, independently loaded ABI and
behavioral gates. The native binary remains byte-identical to the workers'
qualified module, SHA-256 `d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff`.

The [integration review](reviews/PEDAL_NATIVE_INTEGRATION.md) retains
commands, exact scope, log identities and validator limitations. Final checkpoint
changes after that gate are Markdown result records only; seventh-wave work is
unstaged. Hosted native execution remains a separate post-publication gate.


### Sixth-wave publication observed

Root published `d7b886103f8c9d4649ffa1c35930b79808217a3d` with an expected-parent
update, fetched it, and verified exact local/remote tree
`018c3897889aaae0070f632981e0c889a35cad30`. Only Markdown result records differ
from the qualified source tree. Core workflow 43411073429 and the first native
workflow 43411073407 were observed running at that exact commit. No hosted
result is inferred before the jobs finish. Seventh-wave work remains separate.


### First hosted native portability repair

At d7b8861, native Linux succeeded, macOS controller linking lacked CoreFoundation,
and Windows controller round-trip failed with inherited SDK `/fp:fast`. Core
Windows passed 65/67; new inventory full stat/fstat comparison and synthetic
read-only Git-object deletion failed. Linux/macOS/core sanitizers succeeded.
Root retained actual logs and repaired the four specific integration issues;
see [the review](reviews/PEDAL_NATIVE_PORTABILITY.md). Native repair tree
09e155a958ee4fb1310ef8f0d8cafa2f980d1125 passed 4/4 local native suites; completed
tree 7bf8c8d63ec6d816cbae86a1b1ee874666929eb5 changes only independently checked
Python inputs and passed 2/2 focused suites / 32 methods. The Linux module is
unchanged. Actual hosted recovery remains pending; W7 work is excluded.


### Wave 7 accepted — portable tools, installation and actual native audits

Assignments 37–42 are complete with six accepted substantive records. All six
CLI tools now share a strict Windows Unicode boundary. OfflineTools stages 22
files including the pedal trace and catalog; explicit NativeVST3 staging refuses
an existing bundle and the relocated actual Linux module passes its ABI gate.

The native allocation audit measured 133 actual API regions without global C++
new/delete calls, after proving selective module interposition and excluding an
initial broad-export method that could substitute test-host Engine symbols.
The dense-automation gate compares all 45 simultaneous curves, absent/empty
queues, carry/restores and later audible output to a plain Engine; each large
callback necessarily exceeds the fixed event-array capacity. Maximum observed
error is zero. The actual concurrent UI/audio gate passed Release and a fully
instrumented native ThreadSanitizer run, including 3,072 publication-only saves
and 3,072 concurrent accepted loads. These are finite scoped software gates.

The final legacy review compared 57 baseline files, all earlier 43 full registry
records and 24 actual old-score renders without differences. Parameter-info
schema 2 now states its SDK-free verification scope and distinguishes it from
actual native module qualification; the permanent 45 records are unchanged.

Root's combined seventh-wave archive gate follows before publication. Demo and
plot work in wave 8 remains outside that freeze. The separate native portability
repair was published as `9403debd754f771bf39bc8cd771ecfd86c0f14d6`, fetched with
exact tree `e2a00f7c270317b0f07be8a467120d8a573bb61a`; its core/native hosted
runs 43413518927/43413518971 are pending at this observation.


### Seventh-wave integration and observed platform repair

Root's coherent tree `7c3e1e2e93932dfa59f20e2be8ee4ab7f46b8f73` built successfully
and passed 8/8 native suites in 6.68 seconds. SDK-free CTest initially passed
67/68 in 70.98 seconds: only the installed parameter-info assertion still
expected schema 1 after assignment 42 intentionally introduced diagnostic
schema 2. The repaired tree `e50351633caddecc212aef3a934378aeda498870` changes only
that Python fixture and the inventory tool/tests. All compiled inputs remain
identical. Two install methods and 19 inventory methods passed from the repaired
archive using the original configured environment. This is focused follow-up,
not a second claimed full68/68 run. See the wave-7 integration review.

At published platform repair9403debd, native Linux/macOS completed tests and
artifacts; Windows passed all4 actual native suites but its later inventory
step still failed. Core Windows passed66/67, only inventory failing; the other
three core jobs passed. Root changed directory enumeration metadata reads to
fresh consistent path.lstat() calls, retained all mutation/identity guards,
added actual mutation regressions and bounded changed-field diagnostics. The
precise old failing field was not observed. Fresh hosted Windows inventory
remains required. Final W7 publication changes only Markdown result records
from the repaired source tree; live wave-8 work and metadata remain excluded.


### Wave-7 publication and observed Windows inventory closure

Published and fetched `7fb9b6121b729f46a9e18d80e8620eb21dc0847b`, exact tree
`19239e05f6c5219b50d3f398ba9a6eb3acc2a1ac`. In core run 43415692328, Windows
passed 68/68 in 84.18 seconds; Linux Release and sanitizers also passed. In native
run 43415692247, Windows passed 7/7 in 5.80 seconds and Linux 8/8 in 5.70 seconds. Both completed
inventory/copy checks and uploaded bundles. Root downloaded both actual ZIPs
and independently matched API ZIP digest, inner archive digest and every
payload byte/size/mode/hash. Windows fresh-path inventory now has observed
platform recovery. macOS remained queued; no full matrix pass is claimed at
this observation. Exact artifacts and limits are in PEDAL_NATIVE_PORTABILITY.md.

For wave 8, root added the completed pedal plotter to real OfflineTools preflight
and install rules, extending its exact payload from 22 to 23 files. Relocation
checks now compare all three actual pedal scenarios' source/installed SVGs,
embedded CSV hash and existing-output preservation. Missing pedal-script input
also preserves an existing prefix. The targeted private preflight method passed
in 0.469 seconds; combined relocation and full source qualification follow the wave 8 freeze.


## Wave 8 accepted — retained audio, plots and operational gates

Assignments 43–48 are accepted. The retained three-second pedal phrase includes
actual stereo PCM16, source/profile/score inputs, schema-3 provenance and seven
independent PCM windows. Its independent reviewer checked all 474 historical
Git blobs, relocated verification, ten rehashed semantic mutations, current
block partitions and manual/pedal counterfactuals. No physical fidelity is inferred.

The bounded standard-library plotter validates all 37 metadata declarations and
27-column rows, preserves contact/routing transitions and signal extrema, and
embeds the exact input hash. Sixteen focused methods passed against nine actual
scenario/rate traces; three SVGs were rendered and inspected. Root integrated
the frozen script as the 23rd OfflineTools file, including preflight and actual
relocated comparisons for all three pedal scenarios. The current operational
handoff and build/CI/project guide contain practical observed commands.

The remaining M3/scanner contract rereads 66 relevant atlas pages and 11 actual
rendered pages, preserving the page-166 traversal erratum. It specifies the next
50-component graph/compiler/independent numerical gate without inventing
companion files, specimen values or runtime results. The new bounded session
checker validates this ledger only; 24 independent methods pass. Root's explicit
48-complete gate reports eight complete waves and actual 50 dispatched identities.
The coherent full source/relocation gate and expected-parent publication follow.


### Eighth-wave coherent source qualified

Frozen tree `5370890e32045a556cb61a88cdb1f04fb5a18f7e` contains 534 files and
the actual 48-complete manifest (51 dispatched, three running, nine planned).
Fresh SDK-free and locked-SDK native Release builds succeeded. All **71/71
ordinary suites passed in 54.37 seconds**, and **8/8 focused actual native suites
passed in 7.87 seconds**, with zero failures, disabled tests or skips. This
includes the demo, plotter, session checker, exact 23-file relocation and actual
native bundle relocation. The local module and profile hashes remain unchanged.
The wave-8 integration review retains exact commands, scope, log/JUnit hashes
and the separate next hosted gate. Final changes are Markdown results only;
ongoing wave-9 work and later actual assignment states remain outside the freeze.


### Eighth-wave publication and independent review findings

Published `d601eb166ea3206748f8e012b20a463ff365c0b1`, fetched it and verified
exact tree `8af684dfe56f88222c52ff71d85a911ee1192fa1`. Native run 43417681882
and core run 43417681825 started at that revision. The wave-7 macOS jobs later
ended without runner/steps; actual annotations identify cancellation for a
higher-priority waiting request in each main concurrency group and separately
record ARM64-capacity notices. Their outcomes remain unqualified; no timeout
or project failure is inferred.

Independent final core/input and native-protocol reviewers found no actionable
production defect and executed their focused suites. The tools reviewer found
a real Windows reparse/junction admission gap in the bundle inventory; the
coordinated two-file repair belongs to wave 9, not the frozen wave-8 source.
The artifact/rights review also identifies the actual Windows SDK-default icon
bytes and its separate branding conditions; project-wide redistribution rights
and an original-icon replacement remain explicit release gates.


## Waves 9 and early 10 accepted — independent review and concrete repair

Assignments 49–54 completed core/input, native protocol, tools/evidence,
dependency/artifact, fresh-setup and exact hosted audits. Assignment 55 corrected
standing instructions and stale current input/native contracts, preserving
dated assignment evidence. Fifty-five actual workers are accepted: all nine
complete waves plus the first final-wave review.

The core and native reviewers found no actionable production defect and ran
their focused gates. Fresh Unicode-path setup and moved-prefix execution
succeeded with original source/build paths unavailable. Actual hosted W8
Linux/Windows/sanitizer core jobs passed 71 suites and 548 Python methods each;
native Linux passed eight and Windows seven suites. Seven downloaded artifact
ZIPs and all ten native payload members were independently verified. Both
initial macOS jobs failed hosted-runner acquisition, zero steps; root requested
one targeted retry for each after observing the actual capacity annotations.

The tools audit found a real Windows reparse/junction inventory gap. Its
two-file repair passes 20 local methods and preserves the actual Linux bundle
inventory bytes. The old-tool negative control fails in all three metadata
cases; actual Windows junction execution is the next hosted gate. Root will
qualify this source with unchanged compiled-input proof and focused Python/
record checks. The dependency audit records the exact SDK-default Windows icon,
its supported original-icon replacement path and separate release/rights gates.


### Final-review repair qualified from a coherent archive

Frozen tree `a8817841a0a348b6b742dfeb6668249aa9692a54` records 55 accepted workers,
three running and two planned (58 actual dispatched). Exact comparison with
qualified wave-8 tree 5370890e32045a556cb61a88cdb1f04fb5a18f7e confirms every compiled
CMake/C++/header/data/runtime fixture input unchanged. Besides Markdown and the
manifest, only the native-inventory tool and its Python regression differ.
Root separately configured the new source and generated the nominal profile.

The two actual matched CTest suites passed 44 Python methods in 1.62 seconds:
inventory 20 and current-session checker 24, zero failures or skips. The initial
regex also named two unregistered Python aliases; only two suites ran, with
repository/original-console/current 55-record gates separately executed as
explicit successful CLI commands. No four-suite or new full-C++ pass is claimed.
The integration review retains exact scope, command receipts and log hashes.
This initial Python-repair freeze preceded the macOS retry outcome below;
its scoped result remains valid. The final publication also includes the
separately qualified one-file native test repair described next.

### Observed macOS retry and portable concurrency-test repair

The initial review-repair publication was held before advancing main. At W8
`d601eb166ea3206748f8e012b20a463ff365c0b1`, the actual macOS core retry passed
71/71 suites and 548 Python methods in 57.99 seconds. Its native counterpart
acquired a runner and failed compilation because Apple libc++ lacks the test
harness's std::jthread/stop_token types; native tests and inventory did not run.
The original diagnostic artifact and its digest remain in the integration review.

Assignment 59 replaced only that test's thread owner with a nonmoving atomic
stop-token/std::thread helper whose destructor requests stop and joins. A bounded
exception-unwind probe verifies cleanup. All workload, oracle and production
inputs remain unchanged. Fresh local configuration/build and focused concurrency
CTest passed 1/1 in 0.33 seconds, zero failures/disabled/skips, maximum audio error
zero. Root verified all549 tracked bytes/modes against repaired Git tree
`81a1c466efdec3efe5c1d9af1e1663eb101dacde`, which adds just this test blob to
the earlier Python-repair tree. Two generated caches were hashed separately and
preserved; initial source-proof setup stops are recorded. Final result-only
Markdown edits do not alter the qualified inputs. Actual Windows junction and
macOS repaired native execution remain separate next hosted gates.

### Final-platform inventory fixture correction after actual hosted execution

Published/fetched feefe83 passed all three native platform jobs (Linux 8/8,
macOS 7/7, Windows 7/7), including actual inventories and artifacts. Core Linux
and sanitizers passed 71/71; macOS and Windows each passed 70/71 with the
inventory regression failing. The actual Mac temporary alias and Windows
8.3 path spelling bypassed two synthetic patches. Windows also exposed mklink
argument quoting and synthetic st_file_attributes=None. These are concrete
fixture failures, retained with full logs, not a fully passing matrix.

Assignment 59 repaired only tests/test_native_bundle_inventory.py: canonical
fixture roots, separate Windows command arguments, realistic integer attribute
metadata and an explicit two-success counter before the junction marker. The
old fixture reproduced the alias failure locally. The repair passed all 20 methods
both normally and under an actual symlinked temporary parent, plus each forced
special-mode/symlink fallback. No skips or production change. Root reviewed the
diff and bound the exact frozen test/tool inputs to tree
43ac9f5ae25e30f91b45279995ef44ecf01c357e. The retained repair report gives
commands, complete boundaries and log identities. Actual new-source Windows
junction and macOS suite results remain the next hosted gate. Every previous
job completed before this next publication; no outstanding job was cancelled.

## Pedal session complete — all sixty actual workers accepted

All sixty new assignments in ten logical waves of six are complete and accepted.
Six fresh readers covered the unchanged 500-page PDF. Final reviews 56–60 verified
source/scanner arithmetic, executed the actual hosted Linux artifact, updated
readiness and every milestone gate, qualified all seven exact-source platform
jobs, and audited honest accounting plus future-agent instructions. The earlier
original and console sixty-agent sessions remain separate preserved history.

Final code/test commit 0ad7240a88803de9d97bc265a8fd2b6e5d5d7e2b,
tree 41c0b421643d4076c65ecbac8a750b4aae4d5806, passed all four core jobs
(71/71 suites and 549 Python methods each) and native Linux 8/8, macOS 7/7 and Windows 7/7.
Every JUnit result has zero failures/disabled/skips. Ten downloaded ZIPs and
all 16 native payload files match their source/run/attempt and byte/mode/hash
records. Actual Windows junctions and all native cleanup probes passed. The
validator's 47/0 result retains its 16/9/15 diagnostic classes. Root independently
observed both successful workflow APIs and reconciled every JUnit/full LastTest
record. Initial root method/marker assertions used truncated JUnit output;
counting full LastTest logs corrected that parser setup error. No test failure
or hidden rerun is inferred from the parser correction.

Root consolidated current status, next tasks, README navigation, operational
handoff and CI entry points, preserving detailed earlier failures in the log,
notes and Git history. The final matrix and release-readiness documents clearly
separate nominal engineering, physical M3/scanner/AO-28/Leslie/calibration and
DAW/device/UI/distribution work. Assignment 60's read-only follow-up checked 212
local links and a fragment; root applied its three wording improvements. The
first next product task is scanner graph/schema/compiler admission with an
independent endpoint review, followed by an independent AC oracle. AGENTS.md
retains the standing authorized commit/push and durable handoff rule.

The final integration review records source identities, actual results, setup
corrections, sixty-complete archive checks and publication boundaries. This
last handoff changes only Markdown and actual completion metadata; qualified
production/build/test/data inputs remain byte-identical to 0ad7240.

### Final sixty-complete source-archive gates

Root archived staged tree 1aa9ab3620c525ae8c39042d53ca60d0e11d2fdb
(562 tracked files) and ran the repository/original, console-history and current
pedal explicit record gates. All three passed. The current result is 60 complete,
0 running, 0 planned, 60 distinct identities, 60 completed notes and 10 complete waves.
Repository integrity found zero errors, preserved the 500-page source/80-chapter
index and checked 2,161 local links across 317 Markdown files. Current-session
accounting is separate from both historical sixty-agent checks. Final result
updates are Markdown only after this qualified archive; code/build/tool/test/data
and the actual accepted manifest/notes are unchanged. The final integration
review retains exact commands, source tree, scope and receipt hash.

## 2026-11-13 — Scanner continuation begins (wave 1)

- Inspected clean main at `6dc0702d5473912268e8af8f852b9b9984198ef3`, tree `a4f1d4b300de236436e22b748b1d4c46ed501ceb`; confirmed the remote at the same commit.
- Created a distinct scanner-session manifest for the newly requested sixty-agent, ten-wave assignment scope; preserved all earlier completed ledgers. Six fresh readers completed all 500 PDF pages and selected actual visuals. Their notes retain precise source citations and actual checks.
- Default GCC 14.2.0 Release build with CMake 4.4.4/Ninja 1.13.2/Python 3.12.14 passed 71/71 CTest suites in 42.88 seconds. Historical repository/continuation/pedal checkers each passed their sixty-complete expectations.
- Root acquired the original DAFx 2016 scanner paper from its publisher archive for subsequent independent comparison: eight pages, 1,471,656 bytes, SHA-256 `ccdace0e88d456d7d80cd3b675a0936ab1313680f5b2dda0ba33445df0caae83`. The external PDF is an inspection input outside the repository; no new redistribution claim is made.
- Current work advances the nominal scanner graph, independent full-network reference and prepared physical-state module. No new scanner runtime or hardware qualification has yet passed. Existing 45 parameters, state formats and dry-engine arithmetic remain unchanged.

## 2026-11-13 — Scanner graph and independent AC foundation (wave 2)

- Completed all six wave 2 assignments: strict graph/schema/compiler, full-network AC reference, predeclared numerical contract, primary circuit/rotor review, independent graph admission tests, and independent loaded-ladder numerical tests. All twelve assignments in waves 1–2 have actual retained notes.
- Primary paper comparison matches 50/50 passive records, 19/19 signed outputs and 27 nodes. The 16-position cycle has primary support under the documented phase-origin shift; 412rpm and production/specimen applicability remain unverified.
- Full AC grid: 564 solves, 10,716 taps, maximum normalized residual 3.2486101684985267e-16. Independent loaded-ladder recursion maximum complex error 5.6647284161045834e-14. Root ran 19 graph/compiler methods and 16 AC methods successfully.
- Independent test review found a schema-only duplicate-ID gap in unknown/assumption arrays when prose differed. Root added per-ID contains cardinality constraints and directly verified valid/reordered fixtures plus both rejecting duplicate reproductions. The compiler already rejected those cases; regression is retained.
- CMake graph admission generated the native constants successfully in a new build directory, including independent creation of its output directory. Existing Engine/public controls/state/native processing and original physical inputs remain unchanged. Prepared line and independently stamped transient development are now assigned under the frozen numerical contract.

- Coherent wave 2 qualification: committed `74473fa`, created a separate detached worktree, configured/built from scratch and passed 73/73 Release CTest suites in 50.00 seconds, zero failures. [The integration report](reviews/SCANNER_WAVE2_INTEGRATION.md) records the full commit/tree, exact commands and source hashes. Later report changes are documentation only; unfinished wave 3 runtime files are excluded.


## 2026-11-13 — Scanner runtime and configuration integration begins (wave 3)

- Accepted assignment 13's bounded 36-coordinate physical line and assignment 14's independently stamped full-graph companion/MNA reference. The prepared line uses both return topologies and preserves physical coordinates across stopped rate changes; no Engine/native route or controls migration is included.
- Root's focused live-tree Release run passed `test_scanner_line` and `python_test_install`, 2/2 suites in 7.52 seconds. Full frozen runtime qualification remains pending the independent probe/parity workers.
- Reproduced a second-configure failure caused by CMake 4.4.4 caching an automatic empty DATADIR. Repaired the installation module to materialize/track automatic defaults, follow DATAROOTDIR changes and preserve explicit custom paths. Real repeated configuration, custom-path and existing explicit-empty/traversal/absolute rejection tests passed; no relocation rule was weakened.
- CLI push lacked credentials. Published the exact tested foundation tree through authenticated GitHub tree/commit/ref operations with an expected-head guard: code `cdada3c8dc655d27033dd15f3417d39a7a82ecb9`, documentation `80ea8cd2d7febe12fc4dd382e475a00ff4181eac`. Fetched and verified remote/local tree equality; retained local qualification history under `scanner-local-w2-qualification`. No force push or worktree discard occurred. Hosted core/native workflows were queued at inspection and are not yet claimed successful.


## 2026-11-13 — Independent runtime frequency and rotor results

- All assignments 13–20 are accepted. Prepared line, full-graph transient reference, process probe, independent state/reference tests and signed continuing rotor are implemented. Actual matched-step full-basis, combined-stage and calibrated allocation work remain separately assigned.
- Assignment 17 ran every frozen positive bin plus exact DC for all fifteen host/multiplier labels (eleven distinct rates), both modes: 6,204 unique positive native solutions, 160,740 logical tap comparisons and 6,812 independent nodal solves. G3 frequency checks passed; maximum mapped complex error 1.0892198819708419e-12, no residual/conditioning failures. All 88 actual process carriers passed after a bounded settling protocol; 182 measurements retain five earlier unsettled failures. No tolerance or alignment fit changed.
- G5 same-hertz failed at every rate, including 1,536,000 Hz. The exact report retains 40,786 failed tap comparisons; even the highest rate fails 95 vibrato and 18 chorus taps. No audible numerical policy is selected from those rates. An identified alternative realization/policy and independent transient/rotating/filter evidence are the next numerical dependency.
- Independent transient regression passed 21 methods, including literal KCL endpoint equations and source-work/all-resistor energy balance. Independent rotor acceptance passed 23,616 signed angular evaluations, 288 return-once cases, 76,800 checked clock frames and 716 nonzero-state rejection transactions. These do not qualify the still separate native callback or physical instrument.
- Root is preparing a new coherent code checkpoint excluding in-progress combined-stage files. Worker reports identify their coordinated source hashes; until that integration completes, no new all-suite frozen-tree result is claimed.

- Coherent line/rotor integration: local commit `babb8975d6881db6629e570e10ee619c70ba8be3`, tree `14572ab24e67489997cee20ae452c0635178dca0`, passed 77/77 Release suites in 50.64 seconds, zero failures, from a new detached source/build. The authenticated GitHub code object `772e3b3682c2026414e0a7b50eb726e8bddd7fed` has the identical tree. [The report](reviews/SCANNER_WAVE3_INTEGRATION.md) retains commands and exact input identities; publication verification is separate.


## 2026-11-13 — Independent standalone session, waves 1–2

- Read the complete unchanged 500-page PDF in six fresh bounded assignments and
  inspected selected original page images. The current-session notes preserve
  exact coverage and source identity; earlier session agents are not counted.
- Inspected remote baseline `ba0d9c9c75bd7a39152470f9f7ddb82287cb01b1` and created
  an isolated checkout because another active checkout owns unfinished scanner
  work. Advanced the dependency-ready M9 dry-organ adapter permitted by atlas
  p450; retained all core/control/state/native identities.
- Baseline GCC 14.2.0 / CMake 4.4.4 / Python 3.12.14 Release execution passed 77/77
  suites in 44.44 seconds. See [baseline evidence](reviews/STANDALONE_BASELINE.md).
- Wave 2 froze the bounded Session and UI contracts, pinned official SDL2 2.32.10
  at `5d249570393f7a37e037abf22cd6012a4cc56a71`, added explicit acquisition and
  offline verification, vendored licensed DejaVu 2.37 inputs and generated the
  native glyph atlases, and implemented the separate current-session checker.
- Root independently ran 22 dependency methods and 16 accounting methods,
  successfully verified the actual pinned checkout, and exercised fresh network
  acquisition through the maintained script. The first direct dependency-test
  invocation lacked CMake on PATH; setting `HAMMOND_TEST_CMAKE` resolved that
  setup error. It was not a failed dependency implementation.
- Published wave-1 review as `2e917509b378d48c85cc1d52c3aa446eef9552c8` and wave-2
  contracts/assets as `96a37a977ef22b7adf38e1a841f57ffcf32519a7`, exact tree
  `ab85e45d6776229c00fa394a540d72803daf8281`. CLI push has no configured credential;
  authenticated GitHub blob/tree/commit/ref operations used an expected-head
  guard and no force. Fetched each result and verified exact local/remote tree
  equality, preserving local commit identities on named branches.
- Hosted Native VST3 run 43505659847 and CI run 43505660090 both completed with
  success for `96a37a9`; these runs qualify that checkpoint only.

## 2026-11-13 — Standalone runtime integration, wave 3 in progress

- Accepted Session, UiModel and AudioDevice implementations with exact source
  identities in notes 13–15. The real unchanged engine plus pinned SDL dummy
  transport passed all 15 supported rate/buffer combinations: 30 callbacks,
  23,808 frames, zero render/format/nonfinite failures. Fault-injection doubles
  remain explicitly separate from actual-engine evidence.
- Root added the optional application/support CMake boundary, native drawing and
  instrument painting, and off-callback transactional control-file helpers. The
  root sources passed strict syntax checks. Actual software-renderer font and
  full-layout harness images were inspected at 1280x900 and 960x700. Those
  harnesses are intermediate checks, not completed app/device qualification.
- Independent maintained Session/UI tests and the complete executable are being
  implemented by assignments 16–18. Allocation, concurrent recovery, native app
  smoke, package installation and three-platform hosted acceptance follow.

- Root's new SDK-free Release build with both native options OFF passed all
  81/81 CTest suites in 61.60 seconds with zero failures (`--parallel 2`). This
  is an intermediate live-tree integration gate; independent Session/UI
  production and test inputs were stable during execution. The first serial
  run ended without a final result after 69 reported passes and a started
  fixture test; its execution session was no longer available. That interrupted
  run is not counted as a complete pass or a project failure. The complete
  repeated gate retained a normal zero exit and final 81/81 summary.

- Accepted the complete main application and independent maintained Session,
  UI, device and state-file suites (assignments 16–20). The actual device suite
  passes 15 configurations / 75 matrix callbacks / 59,520 frames, 31 expected
  open rejections, two real render faults and eight lifecycle cycles. Its
  adapter ASan/UBSan probe passes; LeakSanitizer is blocked by the environment's
  ptrace limitation and was explicitly disabled for that narrower successful run.
- The complete app passes actual SDL event/callback smoke at both supported
  reference/minimum window sizes. Root's first runs observed 59/56 callbacks,
  30,208/28,672 frames, positive finite peaks, visible held/released state,
  screenshots while held and no audio faults. Source main then received one
  stricter smoke predicate requiring the device still open/running before close;
  final source `6b3e5b13dc362495f0bd224a3a046a1129652385faa4d20804a03edd162d6f78`
  passes its own final smoke. Earlier results are retained under their old hash.
- A fresh optional configure exposed SDL's earlier GNUInstallDirs inclusion
  materializing an empty DATADIR cache sentinel. Root now materializes an
  unspecified default before entering SDL. Actual fresh, repeated, custom
  DATAROOTDIR-following and restored-default configurations pass; an explicitly
  empty DATADIR still rejects. The initial worker configure workaround remains
  recorded rather than being substituted for this integration correction.
- Updated root setup/status/model-scope and dependency notices. Source-font and
  selected SDL2 terms remain identified separately from unresolved project-wide
  and research/branding rights. The source-archive integrity check passes with
  2,382 local links across 383 Markdown files and unchanged 500-page PDF identity.

## 2026-11-13 — Native checkpoint through assignment 27

- Frozen runtime source `738162f`, tree `915e55dc7c3ad022042b188498aa41f2a7f40795`,
  passed the complete optional native Release gate: 83/83 suites, 78.62 seconds.
- Accepted calibrated actual-callback allocation, fully instrumented Session
  concurrency, the nine-file relocatable Standalone install, independent real
  executable acceptance, three-platform workflow definition and input-replay
  helper/acceptance. These are scoped engineering results, not physical devices.
- Independent executable acceptance found missing-leaf path aliases and then a
  symmetric dangling-state-symlink hazard. Root repaired preflight admission and
  retained both regression families. Final app acceptance: 18 methods, 164 runs,
  zero Linux skips. The assembled later native group passed 9/9 in 8.62 seconds.
- The [checkpoint report](reviews/STANDALONE_NATIVE_CHECKPOINT.md) records exact
  app/source identities and distinguishes the two test scopes. The hosted
  standalone workflow is authored but not yet executed; replay application and
  benchmark integration remain active assignments 28–30.
- Before publication, remote `main` advanced from `96a37a9` to `6b4b6bd` with a
  separate rotary review and documentation track. It is being integrated while
  preserving its actual ledger, evidence and scope; no force-push is authorized.

## 2026-11-13 — Scripted workflows, render benchmark and chapel source admission

- Published and fetched native checkpoint `219821dfaca6bfee8ba0905993ed8deec7a66396`,
  tree `f2db7aee1d45a897273e4e68a2fefc6a2de4d433`, after integrating rotary review
  `6b4b6bd`. Exact local/remote tree equality was verified; local commit history
  remains on `standalone-local-w3-checkpoint`. No force push was used.
- Hosted standalone run 43517181978 passed Linux, including installation and
  relocation. Windows/macOS failed test compilation. The four affected tests
  now use SDL's environment accessor, matching event integer types and portable
  stop/join ownership; all four local suites pass in 2.94 seconds. Original failed
  run/source identities remain in the [repair report](reviews/STANDALONE_PORTABILITY_REPAIR.md).
  Hosted Native VST3 passed at 219821d. Ordinary CI passed Linux/Windows/sanitizers;
  macOS failed its build. These results qualify only the named published source.
- Root integrated actual scripted SDL interaction, bounded changed-state
  observations, pre-shutdown acknowledgment and protected script/state/output
  paths. Assignment 28 passes 11 methods / 15 processes through ordinary handlers.
  Its initial zero-discard shutdown assertion was corrected to the existing
  documented scoped-release cleanup behavior; no production change was made
  for that test-only assumption. Exact musical paths and saved bytes remain strict.
- The SDK-free benchmark and source/toolchain identity pass independent 9 methods /
  111 CLI runs. Assignment 33 verified 54 input hashes, automatic reconfiguration on
  content/header changes and the Unspecified configuration fallback in private
  fixtures. Root's assembled native group passed 11/11 suites in 22.78 seconds.
  These results used main SHA-256 e2fc28db7852c23b46615d6c97d7967d133be810ccdd32e05f244dcda606aecb.
- Independent chapel image readings 31/32 agree on 18 rows and 162 digits, including
  all leading zeros and absent names. Strict compiler/JSON Schema/data and
  independent admission acceptance now exist. Canonical CMake target generated
  the 4,837-byte catalog SHA-256 f500fa0aaca0ba8652eeede330094deb888f6a516b5c51958fd2381778fb5a91.
  Root's canonical Python suite passed 18 methods / 111 CLI / 234 API rejections/five I/O
  probes in 6.86 seconds; worker 36 retains its separate direct/fresh-source results.
- Six waves / 36 actual assignments are accepted. Script maximum-plan bounds and
  explicit ordinary-control audition are in progress. The catalog does not
  implement physical preset selection, loaded gains or percussion interlocks;
  the atlas's underlying factory Table IV remains independently unverified.
- Remote main later advanced through rotary foundation 38c1fac and calibration
  scope 08fa8de. Their owned modules/evidence must be integrated and retained
  before the next publication; they are not counted as this session's workers.

## 2026-11-13 — Standalone combined-source gate and accepted work through 41

- Integrated rotary foundation `38c1fac` and calibration scope `08fa8de` into
  local `3872752`, tree `0d6da163edd6531338938e12e0d393841d569a80`, preserving
  both tracks. A fresh immutable source/native Release build passed **94/94**
  CTest suites in 98.80 seconds with zero failures. Exact commands, binary/data
  identities and log hashes are in the [integration report](reviews/STANDALONE_WAVE6_INTEGRATION.md).
- Accepted replay maximum-plan repair after reproducing an actual timeout;
  the unchanged 256-event allowance now drains through the public SDL queue.
  Its independent full-app/workflow/bounds subset passed 3/3 with 208 invocations.
- Accepted strict ordinary-control chapel export and independent byte-exact,
  failure-preservation and native Load/Save tests. Root rebuilt native inputs and
  passed the separate two-suite CTest focus in 18.22 seconds. This does not claim
  an unexecuted 96-suite full run. The native app hash stayed `7377e8c2…`.
- Accepted four actual native screenshot states and the actual downloaded older
  Linux package audit. All package bytes/modes and inventory passed; the archived
  ELF ran after relocation. Dummy/software evidence and runtime dependency limits
  remain explicit. Root also inspected each retained PNG.
- The actual manifest now records 41 completed and three running assignments.
  The first record check found missing canonical agent names in notes 40/41;
  root supplied those metadata fields without changing the reports' evidence.
  Running work covers coherent native sanitizers and identity-aware SDL output
  removal with separate independent acceptance. Future-agent continuation and
  guarded commit/push requirements remain in AGENTS.md.
- Before publication, inspected and merged calibration foundation `5026f67`.
  Its two isolated Python suites passed 49/49 and 27/27 methods from the merged
  immutable archive. Archive integrity passed 2,710 local links in 480 Markdown
  files and the unchanged PDF identity; the standalone checker reports the
  actual 41 completed / three running assignments, separately from older ledgers.
- Published `5b8e2419d23fe27c51709d717812060eafd44dcc`, tree
  `880682248c467a51cce14d920189cf0009b68d22`, with expected-head protection and no
  force update. Fetched exact tree equality passed; local history remains on
  `standalone-local-w7-checkpoint`. CI `43523378849`, Native VST3 `43523378803`
  and Native standalone `43523378962` were observed queued; no pass is inferred.
- The later [core platform follow-up](reviews/STANDALONE_PLATFORM_FOLLOWUP.md)
  observes actual failures at `5b8e241`: Linux Release 89/90 due to an incidental
  concurrency scheduling assertion; Windows Release 87/90 due to chapel reader
  cross-API file metadata comparisons and a calibration mock using the unresolved
  short TEMP path. The core sanitizer job passed. Native standalone build/test/
  package steps passed on Linux and Windows; macOS was still running.
- Root corrected only the calibration test's marked paths to match the checker's
  resolved root and required the injected metadata to be observed. All 27 methods
  passed locally in 0.904 seconds; Windows verification remains pending. The
  production checker and metadata rejection rules were not changed. Dedicated
  chapel-admission and concurrency-oracle repairs follow before final publication.
- Accepted assignments 43/44: the app now ignores removal notifications for zero,
  unrelated or capture IDs and closes only its current open output. The actual
  old application-source injection probe reproduced both false closures; all four
  repaired probes and the ordinary unshimmed smoke passed. Independent acceptance
  passed three lifecycle cycles, 93 actual queued events and exact musical state/
  callback accounting, including two observed SDL handle reuses.
- Root rebuilt the native input aggregate and passed the canonical device,
  callback-allocation and new removal subset **3/3** in **2.94 seconds**. The
  assembled ordinary executable SHA-256 is
  `f07c1d59c0241dd52079da9f14a64fe56e4ad2730aadd4250c5bd5ea19e21bfb`.
  The public predicate cannot authenticate event generations across reused IDs;
  physical hotplug remains explicitly unqualified. No core/control/state identity
  or callback lifecycle body changed.
- Accepted assignment 42's completed coherent instrumentation audit with its
  actual failed gate retained: 92/94 in 222.23 seconds, no ASan/UBSan diagnostics,
  separate leak probe exit 23/ptrace blocker. All 259 translation units, including
  176 SDL C units, carried sanitizer flags. Six smoke capture subcases and one
  resize observation subcase failed; their per-process temporary JSON was not
  retained by the old fixtures. Assignment 47 owns the bounded timing repair.
- Later macOS results at 5b8e241: core 89/90 failed the same unresolved-root
  calibration mock, while native standalone stopped before tests on unused
  `kPanel`/`kLine` constants. Root removed only those unused declarations;
  GCC strict syntax with `-Wunused-const-variable=1 -Werror` passes. Actual
  AppleClang rerun is still required. The native source hash is
  `1cfa38a407ad2b75c4f9fb910bfa7314c694c63b9e2dee4e41fb22faf0fd283a`.
  Linux and Windows native jobs completed successfully, including package upload.
- Accepted assignments 45/46. Chapel readers now retain within-API mutation
  stamps and compatible cross-API identities; both also close descriptors on
  stream-wrapper failure. Their complete suites passed 23/23 and 20/20 methods
  with original before-repair failures retained. Canonical catalog bytes remain
  unchanged. The recovery test now proves four controlled boundary schedules and
  reconciles all 5,760 attempts in sixty concurrent epochs without requiring an
  incidental race outcome. Its first Release and fully rebuilt TSAN gates pass.
- Root rebuilt the concurrency/catalog inputs and passed the four affected
  canonical CTest suites together in **17.28 seconds**. This is scoped Linux
  integration; actual Windows/macOS reruns remain necessary. The real manifest
  records 46 accepted, three running and eleven not yet dispatched assignments.
  Timing repair, hosted artifact audit and fresh Unicode/space-path setup follow.
