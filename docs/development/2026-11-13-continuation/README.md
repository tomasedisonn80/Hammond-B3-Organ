# Console development continuation — 2026-11-13

This session starts from `9c8068c95f6843dce95f7f22d729738eef8074f6`.
The preceding session's work and agent notes remain history; they are not counted
as new assignments. The owner again requested sixty agents in ten waves. This
ledger records the **new** six assignments per wave, run in groups of at most
three workers because the session has four total concurrency slots including
the integrator. Planned entries are not completed agents.

The existing code already implements a nominal M0-M2 dry-engine foundation and
retained-bank console controls. This session continues the dependency-ready M3
contact/percussion work. It does not repeat the initial scaffold or imply that
physical instrument fidelity, a VST3 plugin, or a device-audio application exists.

## Baseline evidence

- All 16 local Release CTest suites passed with GCC 14.2.0 and Python 3.12.14.
- Hosted [run 43363048563](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43363048563)
  for the baseline passed Linux GCC, macOS AppleClang, Windows MSVC, and Linux
  ASan/UBSan/leak checks. This resolves the prior status document's pending rerun.
- The preserved atlas contains 500 pages and 1,294,656 extracted text characters.
  Six complete disjoint ranges were re-reviewed against current code; notes 01-06 retain coverage and selected visual checks.
- Direct Git push has no CLI credential. The connected GitHub app has push access;
  publication uses Git data API commits with an expected-head guard and verifies
  the remote tree and commit. No force push is permitted.

## Wave ledger

| Wave | New assignment IDs | Work | Status |
| --- | --- | --- | --- |
| 01 | 01–06 | Full 500-page continuation review | Complete; six retained notes |
| 02 | 07–12 | Contact and shared-percussion model contracts and unit verification | Complete; independent module tests passed |
| 03 | 13–18 | Engine, control persistence, renderer integration and behavioral verification | Complete; published in `4ead769` |
| 04 | 19–24 | Stable controls, evidence-format migration and reproducible fixtures | Complete; `72b5062` repair passes all four hosted jobs |
| 05 | 25–30 | Bounded host-input ownership and independent adapter verification | Complete; `093d985`, 34/34 local suites and all four hosted jobs |
| 06 | 31–36 | Phase-preserving sample-rate lifecycle and numerical verification | Complete; combined publication gate in progress |
| 07 | 37–42 | Observable console traces and explicit partial-key input | In progress |
| 08 | 43–48 | Integration, cross-platform checks and examples | Planned |
| 09 | 49–54 | User/developer handoff, verification records and exact next milestone | Planned |
| 10 | 55–60 | Independent final review, fixes and publication verification | Planned |

Each numbered note names its actual agent, scope, changed files, observed checks,
results and limitations. The integrator updates shared status/next-step/log files.
These are work waves, not the atlas research waves or M0–M9 product milestones.

## Incoming work preserved

During review, remote `main` advanced to `7c2ad2089f795b2147f5fc72cf10a4542d953a8c`.
That prior session's wave-06 numerical bound, benchmark and archive checker were
fast-forwarded without replacing local review notes. The combined baseline passed
all 18 local Release suites and the source-archive checker. The tiny-frequency
finding in continuation review01 describes its earlier reviewed commit; the incoming
numerical-bound implementation resolves that supported-range issue separately.

## Wave 02: independently tested model modules

Assignments 07-12 added the fixed 1,098-contact bank, one shared percussion
readiness state, a value-owned ConsoleModel contract, independent permanent tests
and an exporter of the actual compiled factory parameters. The contact tests
cover independent identities, analytic make/break times at three rates, partial
holds, reversal and failure atomicity. The percussion tests passed 103 closed-form
comparisons (maximum absolute error 1.1582061807e-12), 41 invalid profiles, eight
invalid rates and 762 invalid settings. Metadata output contains both factories
and remains below its 128 KiB bound. These are software-model results.

This publication checkpoint adds standalone modules and their contracts; Engine,
state-format and CLI integration is the next wave. The established ideal renderer
remains the public default until that integration is verified. No measured contact,
valve, scanner, Leslie, native-host or physical-fidelity gate is closed.

## Publication checkpoints and incorporated work

- `5dcd94292fbd5af61b5bf3bb7e06a1f5f2c4f181`: six full page-range reviews
  covering all 500 pages, plus continuation/standing workflow instructions.
- `7a24a30acd111a8f85cb8df65ba2ca59ada456e3`: standalone contact/percussion
  modules, public contracts, factory metadata exporter and independent tests.
  A fresh source archive of the exact published tree
  `fe2704e72f326f24e09baed98295f26a35db9783` built in Release and passed
  **24/24 CTest suites** before publication. Remote commit/tree were verified.
- Incoming `6c3dd8bc923a3c11f6b234425b056e135fbe9f4b` was integrated before
  that checkpoint without losing the concurrent engine/controls work. Its
  factory-reference, capture and portable installation additions belong to the
  earlier session. Because those workflows now exist, this continuation's later
  waves focus on runtime lifecycle and observable console input instead of
  duplicating acquisition tooling.

Hosted qualification of each new runtime checkpoint is tracked separately from
local checks. A previous run or a written workflow never substitutes for the
current commit's observed result.

The module checkpoint's hosted [run 43366836424](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43366836424)
completed successfully: Linux GCC, macOS AppleClang and Windows MSVC Release,
plus Linux ASan/UBSan with leak checking. This result applies to `7a24a30`'s
standalone-module checkpoint, before the subsequent Engine/CLI integration.


Incoming `61c6ecb` was integrated during wave 04, preserving the earlier session's
original assignments through 56, retained audible demo, factory runtime tests and
review fixes. Its hosted run 43368537860 passed all four jobs. A renamed canonical
test-fixture identifier caused an initial merged-source compile failure; root
reconciled the new v2/legacy names and retained both rounding-mode rejection cases.
This is an integration finding, not a change to historical evidence bytes.


## Waves 03-04: integrated nominal console and versioned evidence

All twelve assigned notes 13-24 are retained. Engine/CLI integration, control v1
migration, four appended permanent control IDs, evidence schema2 production and
independent schema1/schema2 verification have focused acceptance evidence. The
original five fixtures remain unchanged. Three new console scenarios have a
separate catalog with exact score identities and PCM timing/amplitude checks.
The independent end-to-end evidence suite renders and verifies 18 bundles, checks
27 closed-form windows at three rates and compares six exact partition pairs.
Maximum observed amplitude error was 1.132816160855088e-6; its largest fraction of
the independently derived PCM bound was 0.02061797620259823. These are nominal
software oracles, not physical measurements.

The complete merged checkpoint's staged-source and hosted results follow below.


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


Published `4ead76957c763afbbddde1bc96f1128384329e50` with exact tree
`c4890143cb7ea17bfcd1a8cfcbfdc3733d87784d`; all 30 local Release suites passed on
that tree and the remote commit/tree were verified. Hosted run 43369940466 passed
Linux Release and ASan/UBSan/leak checks. Windows and macOS each passed 29/30,
with one shared expected-path assertion in the evidence-producer test. The
[CI repair review](../../reviews/CONSOLE_CI_REPAIR.md) records both job IDs, cause,
local before/after reproduction and the required new hosted check. The original
27 producer methods plus the new portable regression pass locally (28/28).


The path repair was published and verified as `72b5062dd4d02acc42c30faf291465c7633b87d9`.
Hosted run 43370542634 passed Linux/macOS/Windows Release and Linux ASan/UBSan/leak
checks. That qualification applies to the integrated console/evidence checkpoint;
wave05's new ownership/native-adapter runtime has its own subsequent gate.


## Wave 05: bounded typed input and controls

All six assignments 25-30 have completed their retained notes and scoped checks.
The fixed 256-owner translator preserves per-channel identities and original
manual routes, with FIFO release for anonymous repeats. Its Engine facade commits
ownership only after successful processing. Native normalized conversion matches
all 43 proposed IDs, preserving exact binary threshold decisions and the original
39 records. Dedicated diagnostics expose the compiled mappings for independent
registry comparison. These are typed core adapters; native host/device and byte-
level MIDI integration remain unimplemented. The next checkpoint qualifies their
combined source independently of the active sample-rate lifecycle edits.


Wave05 was published as `093d985150a5d7e18b9c210126af0f08504024ce`, exact tree
`3f50aafc240100d888870e55bc0062d136de45d0`. Its clean source archive passed
**34/34 Release CTest suites** in 9.02 seconds. The remote commit and tree were
verified, preserving active lifecycle work as unstaged changes. Hosted run
43371559575 passed Linux GCC, macOS AppleClang and Windows MSVC Release plus Linux
ASan/UBSan with leak checking. This qualifies that runtime checkpoint separately
from the earlier console repair and the subsequent lifecycle changes.


## Wave 06: phase-preserving lifecycle

Assignments 31-34 add atomic rate transitions to the source bank, contact bank,
shared percussion and Engine. The supported rates remain 44100, 48000 and 96000 Hz
subject to owned source-increment bounds. Source phases, all contact positions/
threshold history, shared readiness, controls, held targets and frame count are
preserved. Same-rate requests advance and rebuild nothing. Independent module
checks cover all old/new rate pairs, future-output preservation after rejection,
analytic phase/contact/readiness evolution and exact same-rate continuation.

The integrator froze the production core in staged tree
`4370375d5dfe2161d8eefbf492cd692f2613d9c6` before wave 07's Engine edits. The
independent Engine and owned-input tests use that tree with their own test files,
preventing accidental qualification against changing live headers. The full
checkpoint's actual result and remote identity follow once observed.


Assignment 35's permanent Engine gate passed four focused suites. It checks all
91 sources and 122 keys, 36 rate-pair scenarios, 36 independent detector-edge
scenarios, 81 rejected changes, 6144 same-rate requests and 32603 bit-identical
future audio samples. Maximum phase and readiness errors against its analytic
models were respectively 5.55951e-14 turns and 5.51774e-14. These bounded nominal
software oracles do not establish physical calibration or native-host timing.

Assignment 36 independently passed its owned-input lifecycle suite against the
same frozen core. Twelve mixed-rate runs use a hand-written 3814-frame physical
timeline in both contact modes and several partitions. Fourteen rejected-rate
probes, 42 rejected input blocks, 50 future-output probes and 10086 exact state
comparisons preserve ownership, original routes and Engine state. All six wave-06
notes are now retained.


The combined wave-06 staged tree
`b204d1d91e473929fc92b5563bc97274dd2e2966` built in strict GCC Release from a
clean archive and passed **39/39 CTest suites in 8.80 seconds**. The archive
contains all five new lifecycle suites and the prior ownership, console, evidence
and install gates. Active wave-07 source and build changes were excluded from
this checkpoint. Final publication and hosted results are tracked separately.
