# Fixed-registration continuation handoff

## Resume at the current source, not a historical test count

This is the initial operational handoff prepared by A30 during the
[2026-11-14 preset continuation](development/2026-11-14-preset-continuation/README.md).
The integrator updates its final publication and qualification checkpoint as
the remaining assignments finish. Read [STATUS.md](STATUS.md),
[NEXT_STEPS.md](NEXT_STEPS.md), the
[actual manifest](development/2026-11-14-preset-continuation/assignments.json)
and [publication record](development/2026-11-14-preset-continuation/PUBLICATION.md)
before changing code. The manifest records this session's actual workers;
earlier sixty-agent sessions are separate history.

At A30's inspection, HEAD was
`35554c068492fe2b20c1f8a602d8354ae762dc42`, tree
`6a6881eeee1943665694e988208b2d6710731919`. That published commit contains the
source/contract baseline and two macOS compile/startup repairs. **The preset
implementation is an uncommitted development overlay at this checkpoint.**
HEAD alone does not identify any worker's changed-source test result.
Each accepted record retains its copied-source/input identity and executable.

The working checkout is
`/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`. Other scanner, rotary and
MIDI/UI working copies are separately owned. Preserve them. Do not rebuild the
retained original `/workspace/scratch/a472c29da8b3/build-baseline` or
`/workspace/scratch/a472c29da8b3/build-native`; later comparison gates need their
original executables. New checks require a coherent source copy and a new build
directory, particularly when shared headers or snapshot layouts change.

## Implemented slice and authoritative contracts

The six fresh source readers covered every one of the 500 unchanged PDF pages;
[the review](research/PRESET_ATLAS_REVIEW.md) retains their exact ranges and
source identity. This M3/M9 slice implements ordinary exclusive selection of
the eighteen atlas-page-122 chapel rows. It preserves the 91 continuously
running sources, two 61-key manuals, 25 pedals, four adjustable banks and
existing nominal audio laws. Physical multiple latches, switching/loading
networks and calibrated gains remain separate work.

| Boundary | Current implementation and authoritative reference |
| --- | --- |
| Frozen source data | `FixedRegistration.h/.cpp`, `CompileFixedRegistrations.cmake` and `compile_fixed_registrations.py` admit the catalog and both readings before native generation. [Core API](PRESET_CORE_API.md). |
| Console and Engine | Fixed keys reconnect; Cancel retains raw fixed/bank memory; bank selection clears fixed mode. Notes, phases, contacts, pedals and readiness remain continuous. [Selection contract](PRESET_SELECTION_CONTRACT.md). |
| Persistence | Canonical state4 pins the catalog and saves both raw fixed modes. Readers 1/2/3 remain. [State format](CONTROL_STATE_FORMAT.md). |
| Parameters and hosts | Two appended ordinary selectors, IDs 20480/20481, bring the count to 47. All previous 45 records retain their identities. New binary64 thresholds/canonical values are literal and separately qualified. [Parameter contract](PRESET_STATE_PARAMETER_CONTRACT.md). |
| Thread publication | StateExchange and Session preserve raw modes independently of effective selection and remembered bank; whole-state restore reinitializes host anchors. [StateExchange](STATE_EXCHANGE.md), [HostTimeline](HOST_TIMELINE.md). |
| Native UI | 24 reversed preset keys, 147 playing keys and 67 focus stops; separate applied, pending, focus and Cancel states. [UI design](PRESET_UI_DESIGN.md). |
| Offline and native reporting | Offline `select_preset` stays in render schema 3. Native diagnostic schema 3 and benchmark-v2 expose raw fixed modes and derived selections. [Offline](PRESET_OFFLINE.md), [native workflows](PRESET_NATIVE_WORKFLOWS.md). |

Use [PRESET_RUNBOOK.md](PRESET_RUNBOOK.md) for setup, playing, migration,
replay/capture, rendering, recovery and staging. Its source-build examples use
fresh directories and actual CMake options/targets. The pinned dependency
contracts remain [SDL](STANDALONE_DEPENDENCY.md), [RtMidi](RTMIDI_BUILD.md) and
[VST3](VST3_BUILD.md). Current observed Linux workers use GNU 14.2.0,
CMake/CTest 4.4.4 and Python 3.12.14; this does not substitute for published
AppleClang/MSVC or physical-device qualification.

## Evidence available at this handoff

These are separate focused qualifications, not one combined-source pass:

| Accepted evidence | Scope |
| --- | --- |
| [Core lifecycle](reviews/PRESET_CORE_LIFECYCLE_REVIEW.md) and [persistence](reviews/PRESET_PERSISTENCE_REVIEW.md) | Continuing musical histories, rate/restore behavior, exact state4 and independent old-format inputs. |
| [Parameter oracle](reviews/PRESET_PARAMETER_ORACLE_REVIEW.md) | Independently derived binary64 boundaries and preserved legacy conversion behavior. |
| [Native VST3](reviews/PRESET_VST3_INTEGRATION.md) | Eight native suites passed; 47 exported parameters and 47 SDK internal checks are distinct counts. Original fixture failure and SDK diagnostics remain recorded. |
| [Offline A24](development/2026-11-14-preset-continuation/24-offline-events.md) | 107 methods across three suites, all eighteen literal rows, ordering, preflight and historical-schema rejection. |
| [UI A25](reviews/PRESET_UI_ACCEPTANCE.md) | Model acceptance and 96 native label/focus cases; two actual focus defects repaired, with original/candidate failures retained. |
| [Realtime A26](reviews/PRESET_REALTIME_REVIEW.md) | 761 calibrated calling-thread C++ allocation regions observed no allocations/deallocations; scoped allocator limits remain. |
| [Session A27](reviews/PRESET_SESSION_CONCURRENCY.md) | 3,264 concurrent restores, pending/acknowledged distinction, copied state4 saves and specified queue recovery. |
| [A30 operating examples](development/2026-11-14-preset-continuation/30-operating-handoff.md) | Actual native fixed→Cancel→Save replay and independently verified two-second offline demonstration using the named existing binaries. |

A28 owns the current native workflow integration and the remaining hosted
replay diagnosis. Its [contract](PRESET_NATIVE_WORKFLOWS.md) is written; use
its completed execution record and the integrator's acceptance before claiming
that entire gate. A30's single bounded example does not qualify every native
workflow. The original published macOS result and copied evidence remain in
the [baseline follow-up](development/2026-11-14-preset-continuation/BASELINE_REPLAY_FOLLOWUP.md):
the narrow focus observation window had no sampling-latency guarantee, and the
separate modal timeout lacked sufficient diagnostic detail. Later fixes and
hosted results must retain that original distinction.

## Next integration steps

1. Finish the native diagnostic/state4 workflow qualification and record the
   corrected observation policy and exact source. Preserve the two-second
   drain bound and full assertion-time diagnostics; do not close the unclassified
   CoreMIDI timeout through a Linux result or an unchanged retry.
2. Build the complete integrated source in a new directory; discover and run
   the relevant core, standalone and VST3 suites with required inputs built.
   Compare no-fixed audio with the preserved baseline executable. Keep failures,
   affected repairs and current source identities distinct.
3. Regenerate the actual native gallery after A25's renderer repairs, refine
   the remaining material/perspective differences, and update the README.
   A23's earlier images remain historical. Literal 1:1 equivalence and very
   small accidental-label readability are open; source art is not an app capture.
4. Qualify relocation and the exact enabled/disabled packages, including the
   current operating guide. Update the installed historical guide's stale
   45-parameter/state3/diagnostic2 instructions. Complete platform/sanitizer
   evidence for the published source and actual sixty-worker accounting.
5. Update this handoff, shared status/next steps/log, plan and affected contracts;
   publish completed authorized work to `main` with a checked expected parent,
   no force, and observed remote/CI results. [AGENTS.md](../AGENTS.md) makes this
   the standing rule for every future agent.

## Engineering and physical work after this slice

The [complete M0–M9 plan](PLAN.md) remains authoritative. The next M3 physical
inputs are an identified factory Table IV comparison and specimen-specific
switch/contact/loading captures, including held upper-B/fixed/Cancel transitions.
Documentary taps and nominal software histories do not supply those inputs.

M4 retains the observed **G5 same-hertz failure** under the
[frozen scanner numerical contract](SCANNER_NUMERICAL_CONTRACT.md); resolve it
with an identified realization or reviewed policy under unchanged budgets before
Engine integration. M5 needs the connected revision-specific AO-28 graph and
validated dry electrical boundaries. M6 needs separate identified Leslie
122/147 electronics, loads and measurements. M7's independent nominal
motion/propagation work retains separate horn/drum boundaries and must not be
reported as connected cabinet audio. Preserve each track's ownership.

For M8, follow the [next acquisition sequence](CALIBRATION_NEXT_ACQUISITION.md)
to obtain the real pilot archive, chain/clock/uncertainty records and declared
held-out groups before fitting. M9 still needs shared transformed geometry for
any true perspective redesign, native semantic accessibility, named real
controllers/audio devices and DAWs, qualified deadlines and distribution gates.
Choose the next dependency-ready task with explicit inputs and exit evidence;
do not use agent counts or synthetic tests as a physical-fidelity result.
