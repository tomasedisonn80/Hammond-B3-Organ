# Assignment 31 — native processor boundary

Owner: /root/w06_a31_native_processor

Session: 2026-11-13 pedal development, wave 6, assignment 31 of 60.

## Scope and position

Owned only `plugins/vst3/Processor.h`, `plugins/vst3/Processor.cpp`,
[VST3_PROCESSOR.md](../../VST3_PROCESSOR.md), and this note. No core, controller,
factory, CMake, shared status, manifest or other worker file was edited. No
commits, pushes or subagent spawns were performed; root owns integration and
publication under the user's standing authorization.

Implemented the actual SDK `AudioEffect` processor using the frozen wave-5
HostTimeline and StateExchange. Its strict GCC translation-unit check passes
against the actual pinned SDK. A linked Hammond module, native ABI behavior,
SDK validator result, native callback allocation gate and Windows/macOS
execution are not established by this assignment's syntax check. Those are
the independently owned next integration gates, rather than assumed passes.

Read `AGENTS.md`, current README/status/next steps/development log, project plan,
atlas review and prior continuation handoff, the full VST3 spike/timeline/state
contracts, and actual profile, console, parameter, owner and exchange interfaces.
Read atlas pp. 385–396 in full for graph/wrapper separation, bounds, one clock,
state/lifetime, native bus/automation behavior and qualification boundaries.
The fresh full-500-page review belongs to assignments 1–6; this worker does not
claim another independent complete reading or visual inspection.

Read the pinned SDK's actual audio-effect/component/bus implementations,
processor/component/event/parameter-change declarations and relevant validator
lifecycle/flush tests. The SDK's disabled invalid-transition example is not a
reason to admit an unprepared instance. Repeated identical activation rejects;
supported setup remains an explicit prerequisite.

## Implementation decisions

The processor creates no audio inputs, one stereo float32 output and three
16-channel event inputs. It declares original FUIDs through assignment 32's
agreed header and uses all 45 existing parameter IDs without adding a native
Cancel, panic, bypass or program parameter. Manual mapping is MIDI 36–96;
native pedal bus 2 maps MIDI 36–60 to PedalId 1–25, logical origin zero, under
`vst3-pedal-midi36-v1`. This is software policy, not physical octave evidence.

The generated profile text is parsed only during first initialization. First
setup starts seed zero with explicit `make_nominal_console_model()`; subsequent
quiescent setup uses rate/block reconfiguration without resetting phase,
contacts, owners, readiness, anchors, carry or time. `setProcessing` is a
bounded Boolean update. Same-object terminate/reinitialize recreates SDK buses
while retaining its existing musical epoch and accepted state queue; a new
object starts a new lifetime. Host lifecycle serialization and quiescence are
required; plain lifecycle flags are not a substitute for synchronization.

Native admission checks signed counts before conversion, every supported
payload and offset before filtering, all queues/IDs/points, fixed capacities,
host accessor results and the entire output shape. The raw 1024-record budget
includes filtered native events and retained carry. Positive velocities never
round down to release. Valid out-of-range pitches and recognized unsupported
kinds have named counted filtering. Nonzero finite per-note tuning is counted
and ignored because the profile owns shared source frequencies; optional note
length is unused and does not create an automatic release. Supported in-range
notes on an inactive input reject, preserving releases and owner authority.

The output policy admits omitted outputs, inactive nullable stereo samples,
zero-frame zero-channel flushes and exact L/R aliasing. Distinct partially
overlapping output ranges reject using checked `uintptr_t` arithmetic. Inactive
output samples/flags are preserved; private processing still advances time.
Active output is copied completely only after success, and silence comes from
the actual rendered sample values. No output event or parameter interface is
written, and no transport/editor action controls the simulation clock.

The callback order is native admission, exchange peek/preflight, one timeline
transaction into private mono output, guaranteed exchange publication, then
host copy. The final exchange commit is nonfailing under its proved
sole-consumer/valid-snapshot preconditions and is not turned into a late
resource decision after Engine commitment. Active `setState/getState` use only
bounded off-audio stream helpers and the UI exchange; there is no direct UI
Engine snapshot. The complete contracts and failure policy are documented in
[VST3_PROCESSOR.md](../../VST3_PROCESSOR.md).

## Executed checks

The first strict compiler invocation passed. After inspecting the SDK's
identical-state transition example, same-value `setActive` was made explicitly
rejecting; the final compiler invocation also passed. This was a local design
review correction, not an observed module test failure. No native runtime
test or sanitizer run was performed by this worker.

The scratch `EmbeddedProfile.h` was generated from the exact 4,545-byte compiled
nominal profile in the frozen wave-4 build. Its SHA-256 is
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
The raw-string delimiter was checked absent from those input bytes. Assignment
33 owns the production generated-header path and exact-byte embedding check.

Executed from the repository root:

```sh
/usr/bin/g++ -std=c++20 -DNDEBUG=1 -DRELEASE=1 \
  -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  -I/workspace/scratch/f364bc93d920/Hammond-B3-Organ/include \
  -I/workspace/scratch/f364bc93d920/a31-processor-check \
  -isystem /workspace/scratch/f364bc93d920/vst3sdk \
  -fsyntax-only plugins/vst3/Processor.cpp
```

Observed compiler: `g++ (Debian 14.2.0-19) 14.2.0`. Final exit status **0**,
with **zero diagnostic bytes**. The command vector and empty diagnostic log
were retained in the scratch `a31-processor-check` directory. This syntax-only
invocation links no library, so it cannot accidentally mix an older core binary
with later headers; it also supplies no ABI/runtime evidence.

Direct `git rev-parse HEAD` checks of the external SDK and four submodules
matched the retained lock:

| Checkout | Observed commit |
| --- | --- |
| SDK root | `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` |
| base | `fcf9da0bd27a16f7f03773a3a39822f28f5c8477` |
| cmake | `054c9143cbb8d47fc4694e473f2ee3b4d951a8f5` |
| pluginterfaces | `4f547e8e102b47de4a8b8aaf343c73b700786372` |
| public.sdk | `586dc5e6c8012c3e4b01c79389375cbe96bdb1da` |

All four owned files pass explicit newline/trailing-whitespace checks.
The source freeze was sent to root and assignment 33 before its coherent
native snapshot, so later module failures/results can identify these bytes.

## Frozen source identities

| File | SHA-256 |
| --- | --- |
| `plugins/vst3/Processor.h` | `e85cdc6f7aaf70c05eda61630a5e3acee7c7f2fef2796a2c5f557ce034a54e72` |
| `plugins/vst3/Processor.cpp` | `a61e567798e7435c9d73ddab9bf925b6995396954e772c13f31571ad0a96f20b` |
| `include/hammond/HostTimeline.h` | `690e88fc73602b7edc39133f1a27e100ce1e1427dfcaa4543f318c208f681f9d` |
| `include/hammond/StateExchange.h` | `dfb4ec233f816edc223dfdf5b14da05cbca8a64534d5d725d307c2dff6d9933a` |
| `plugins/vst3/PluginIds.h` | `2bc93839216f52d5920046931d83ba14fd2d01e15fdbdd477b71b15ebb8415fc` |
| `plugins/vst3/StateStream.h` | `6493aa859427ad55cf81c84df29b4669f038828eb4d2c53f04e442aefadeea8e` |

The first two files belong to this assignment. The latter four are dependency
headers observed during the check, not files edited by this worker.

## Integration handoff

Assignment 32 owns `PluginIds.h`, `StateStream.h/.cpp`, controller and factory.
The frozen helper signatures return `Steinberg::tresult` and are `noexcept`:
`read_control_state(IBStream*, ControlSnapshot&)` and
`write_control_state(IBStream*, const ControlSnapshot&)`, in namespace
`hammond::vst3`. Assignment 33 owns optional build wiring and a generated
`EmbeddedProfile.h` with `inline constexpr std::string_view kEmbeddedProfileText`
in that namespace. Generated headers/SDK sources remain outside versioned input.

Next, compile and link all frozen native and core sources in one source snapshot,
load that actual bundle with the separate ABI harness and run the pinned SDK
validator against it. Native behavior review must explicitly activate all three
event buses, supply an audible registration, compare nominal-contact audio with
the same direct core, and exercise zero/max/disconnected/alias cases, offset-N
carry, all IDs, queued active restores, queue-full preservation and late invalid
input. A same-thread test can inspect `timeline_for_testing()` and copied
`last_process_diagnostics()`; these are not a concurrent UI API or a new native
SDK interface. Test process/setProcessing allocations on actual native calls.

Preserve the 1024 raw-record contract even if an optional exhaustive host stress
requests more work. Qualify any rejected configuration explicitly; do not change
the capacity or drop NoteOff records to obtain a validator pass. Actual DAW,
device, UI, signing, platform-distribution and physical-fidelity gates remain
separate. Root updates shared status and observed publication results after
the independent integration checks.
