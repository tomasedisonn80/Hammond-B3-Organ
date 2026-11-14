# A13 — Bounded MIDI inbox and decoder implementation

Actual assignment: `/root/w03_a13_midi_implementation`, wave 3 of the new
MIDI/UI session. Observed HEAD was
`7b36cfac2565397191b3df5e07112611e7f1b0e1`; the implementation and frozen
contract/acceptance files were uncommitted concurrent work. This assignment
owns only `apps/standalone/MidiInput.cpp` and this note. It made no changes to
the frozen header, acceptance source, Session, UiModel, core, build files or
other workers' outputs, and performed no commit or push.

## Implemented behavior

Implemented every declaration in the frozen
[MIDI input contract](../../MIDI_INPUT.md): the 256-packet SPSC inbox with one
unused slot, routing validation and epoch transactions, complete-message
decoder, cumulative diagnostics and ordered scoped retirement commands.

The producer publishes copied packets with a release write-index store; the
consumer acquires that index before reading the payload. The consumer releases
its read index after copying, and the producer acquires it before slot reuse.
Indices remain within the 257-slot ring. Short packets are constructed with
zeroed unused bytes. Fault checks precede push-size admission and pop delivery;
full admission latches the overflow bit, and refused pops preserve destination.
An independent error thread only atomically ORs fault bits. A packet already in
progress when a fault races remains covered by the documented retirement rule.
Only quiescent reset discards queued packets and clears indices/faults.

All counters saturate at `UINT64_MAX`. Each active inbox diagnostic counter has
one writer; the atomic load/store update therefore needs no CAS retry loop.
Discard/reset counters are written only with both participants quiescent.
Concurrent diagnostic readers see independent atomic observations. No inbox
operation allocates, waits, locks, performs I/O or calls Session. The decoder
has fixed storage and runs only on the main thread.

The decoder observes timing before active-packet validation and follows the
declared malformed/system/unmapped/unsupported precedence. Notes remain
anonymous FIFO commands with canonical zero offset and release velocity;
wire routing maps to the fixed upper/lower/pedal owner namespaces. CC11,
manual B-bank CC16–24, pedal CC16–17 and scoped CC123 retain their exact
identities. Parameter edits retain `value / 127.0`, leaving the existing bridge
responsible for discrete conversion. No private ownership ledger, scheduler,
source-phase reset, control-state format or sound behavior was added.

## Executed verification

Working directory:
`/workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ`.
Compiler: GCC **14.2.0**, Debian build `14.2.0-19`. The existing Release core
archive and nominal profile were provided by the integrating agent. The
protected `include`/`src` diff was empty at this check.

The untouched independent acceptance compiled without warnings under the
project's strict warning policy and executed successfully:

```sh
g++ -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror \
  -I apps/standalone -I include -I tests \
  '-DHAMMOND_TEST_PROFILE="/workspace/scratch/cd4bd06ce68f/build-baseline/nominal.b3p"' \
  '-DHAMMOND_SOURCE_DIR="/workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ"' \
  apps/standalone/MidiInput.cpp \
  apps/standalone/tests/test_standalone_midi_input.cpp \
  /workspace/scratch/cd4bd06ce68f/build-baseline/libhammond_core.a \
  -o /workspace/scratch/cd4bd06ce68f/a13-test-standalone-midi-input
/workspace/scratch/cd4bd06ce68f/a13-test-standalone-midi-input
```

Observed result, exit **0**:

```text
Standalone MIDI inbox/decoder acceptance: 10 behavioral scenarios passed
```

`git diff --no-index --check /dev/null apps/standalone/MidiInput.cpp` produced
no whitespace diagnostics; its exit 1 denotes the new-file difference. No
implementation or acceptance failure preceded this pass, and no oracle was
relaxed. The integrator separately reported a passing three-test MIDI-input,
external-control and existing-UI CTest run; that command belongs to the
integrator's evidence, rather than this worker's execution record.

| Verified input | SHA-256 |
|---|---|
| `MidiInput.cpp` | `32e135e84a870dc0e7d6cd9f5a9804b6c75031d4b2fd8dcfcf4d0959bd210802` |
| Frozen `MidiInput.h` | `00a1e6d43f8db1721f7042b6c37b081f192dd85f55dc1bb999c81ee0a4014038` |
| Frozen `MIDI_INPUT.md` | `ca5310fac2b000f95f4857b8b79aba20ad9dc73b262b32d7fa2fff274df179b8` |
| Independent acceptance source | `a4d42a5be724ac04e8c113e409ae26ccb2ffced13fbc357bae054a4a809120fa` |
| Existing Release `libhammond_core.a` | `a73f6bb2ab0591265b10883a3de4b1fc91c6bef9308251d02b13c90d27b83986` |

## Remaining integration gates

This assignment establishes the independent ten-scenario decoder/inbox pass.
It does not establish live producer/consumer stress, runtime allocation probes,
saturation-boundary injection, backend callback quiescence, main-loop drain
budget, native-port lifecycle, actual MIDI hardware or physical timing.
Those remain separately assigned gates. CMake integration, coherent final-tree
qualification, shared status updates and publication belong to the integrator.
No disagreement with the frozen contract or independent oracle was found.
