# A07 - Frozen standalone MIDI ingress and musical contract

Actual assignment: `/root/w02_a07_midi_contract`, wave2, newly requested
MIDI/UI session. Starting source is `0f7b90037e51e101d8fa0bfe31af40209d751659`;
concurrent scope, reference and source notes were preserved. The integrator
owns shared status, accounting and publication.

## Owned outputs

- [MidiInput.h](../../../apps/standalone/MidiInput.h): SDK-free declarations for
  fixed messages, the SPSC inbox, route configuration, decoder, parameter-edit
  records and the fixed three-command owner-retirement sequence.
- [MIDI_INPUT.md](../../MIDI_INPUT.md): complete behavior, timing, ownership,
  controls, desired-state merge, recovery/lifetime and independent exit criteria.
- This substantive assignment note.

No implementation `.cpp`, UiModel, Session, Engine, build file, shared status,
old assignment or source PDF was modified. No commit or push was performed.
These files establish a contract, not an executed MIDI feature or physical pass.

## Context and selected decisions

Read the standing agent rules, current MIDI/UI scope, Session/UiModel declarations
and relevant implementation, PerformanceInput and ParameterBridge, the six fresh
atlas source-review notes, standalone operational context and the complete-plan
context inherited from the integrating session. The MIDI/UI reviews identify
three especially consequential traps: UI-channel collision, a second Session
producer, and stale whole-UI snapshots undoing external controller changes.

The declaration resolves those traps with explicit finite policy:

1. One physical input port supplies three distinct configurable one-based wire
   channels from1-16. Defaults1/2/3 target Upper/Lower/Pedals. Their internal
   namespaces are fixed1/2/3; UI stays0. Routing cannot mutate an active epoch.
2. A fixed-capacity256-message SPSC ring connects exactly one backend producer
   to the main consumer. The consumer processes at most32 packets per loop turn.
   Faults latch; clearing an epoch requires joined backend/consumer quiescence.
3. Note messages become the existing anonymous FIFO owner events, preserving
   repeated Note Ons, zero-velocity release, independent UI holds and fixed
   manual/pedal pitch domains. No new gain, phase or physical-contact model is
   introduced.
4. CC11 targets existing nominal expression. CC16-24 target fixed manual B banks;
   pedal CC16-17 target the two nominal mixtures. Conversion uses the existing
   normalized parameter bridge. CC123 releases only its addressed external
   division. Program Change, CC120/121, sustain, bend, pressure and system
   messages are explicitly unsupported in this first slice.
5. Controller results are `MidiParameterEdit`, separate from posted note/release
   commands. The future main integration must route them through a narrow
   `UiModel::external_parameter` method which updates the same pending desired
   snapshot as local UI edits, then uses existing submission acknowledgment.
   Direct partial-Event posting in addition to that snapshot is prohibited.
6. Receipt timestamps are diagnostic steady-clock nanoseconds. All message
   scheduling remains arrival-order and next-callback-boundary, with decreasing
   timestamps counted. No device latency or sample accuracy is asserted.
7. Retirement emits Upper bus0/channel1, Lower bus1/channel2 and Pedal
   bus0/channel3 scoped AllNotesOff. Old buffered packets are discarded after
   joined close. New explicit connection waits for release resolution or
   confirmed Session global recovery. UI focus loss alone leaves MIDI active.

## Coordination with backend contract owner

A08 and A07 exchanged the exact inbox API before either backend implementation:
`push(span,arrival_ns)`, `pop(packet)`, `signal_fault`, `faults`, `pending`,
`diagnostics` and `reset_quiescent`. Both contracts preserve inbox lifetime until
all backend callbacks finish. A08's device close does not touch Session or reset
caller-owned storage. It signals a fault so the main owner performs retirement.

The backend receives complete messages and stores at most three bytes. Its
steady-clock observation does not enter an audio-clock mapping. Explicit
fault/race documentation avoids falsely promising an atomic hardware-time cut:
an already returned packet may race fault publication, and subsequent scoped
release also retires that packet's ownership.

A08 independently found a pinned upstream CoreMIDI initialization defect and
reported its reviewed build-copy repair to the integrator/A12. That backend
finding is not implemented or independently qualified by this header assignment.

## Verification actually executed

Compiled a translation unit including the new header with GCC C++20 and the
repository's strict warning policy:

```sh
g++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion \
  -Wshadow -Werror -fsyntax-only -I apps/standalone -I include \
  /workspace/scratch/cd4bd06ce68f/a07-header-check.cpp
```

The declaration syntax check passed. It additionally asserted fixed-message
trivial copyability and lock-free32/64-bit atomics on this target. The header
also makes both atomic properties compile-time prerequisites, rather than
silently introducing a hidden library lock on an unsupported target. Checked
all authored Markdown links against the actual checkout and checked for trailing
whitespace. No runtime behavior, throughput, allocation, data race, native
backend, Windows/macOS or physical-controller claim follows from a declaration
compile check.

## Concrete next implementation and acceptance

A13 can implement the exact declared APIs without changing core types. Its
queue must use proper release/acquire payload publication, reject/full/fault
semantics, bounded ring indices and saturating lifetime counters. Its decoder
must obey documented validation order, range/channel/controller decisions and
one-action maximum. Independent acceptance should drive Session and inspect
actual holds/controls, rather than only comparing the decoder with itself.

Main integration needs the described UiModel bridge and recovery-count handling.
The most important regression is CC11 followed by an unrelated native drawbar
edit before any audio callback: both values must survive in the final applied
snapshot. Other mandatory cases include repeated notes, UI/device overlap,
exact capacity overflow, old-epoch discard, disconnect under a held chord,
failed submission and explicit restart without resurrecting prior holds.

The integrator must bind final checks to coherent source/dependency identities,
update current setup/status/next steps and publish observed results. Physical
controller timing/hotplug remains a separate environment-dependent gate.
