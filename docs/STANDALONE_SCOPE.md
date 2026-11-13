# Native standalone scope and integration boundary

This session advances the M9 adapter permitted by atlas pages 391–444 and 450
against the existing nominal dry organ. The scanner continuation is a separate
concurrent development track. This document is an initial integration boundary;
the implementation contracts and executed acceptance records will refine it.

## Product slice

Build an optional native desktop executable with an instrument window, two
61-key manuals, retained A/B drawbar editors, independent pedal controls,
percussion, nominal expression, computer-key and pointer playing, audio device
selection, and control-state save/load. The window uses the atlas's walnut,
charcoal, ivory and brass direction with a visible focus treatment. Editing a
bank and selecting the sounding bank are separate actions. Every displayed
control must correspond to an implemented core behavior.

The existing 45 parameter identities, core sound, profile, VST3 UUIDs and saved
state formats remain authoritative. Fixed chapel presets, scanner, AO-28,
Leslie, room, physical expression and continuous drawbar conductance are future
runtime model work. An explanatory service view may name those gaps without presenting
them as working controls. A native canvas with keyboard operation does not by
itself establish assistive-technology accessibility.

The later dependency-ready source slice imports the atlas p122 chapel matrix
under `data/registrations/`, with two independent image transcriptions, strict
offline compiler and admission tests. This is the [documentary catalog](CHAPEL_PRESETS_CATALOG.md),
not a runtime fixed-key selector. An explicit audition export may translate its
digits into the existing nominal drawbar controls and ordinary `B3CONTROLS3`;
it must preserve all existing identities and identify the unmodeled physical
latch, loading and percussion interlock. Source facts and nominal audition
choices remain separate. Scanner, rotary and capture/calibration work retain
their own concurrent ownership.

## Technical boundary

- Keep standalone-specific sources under `apps/standalone/` and tests under its
  own test directory. The default SDK-free build remains available.
- Use an explicitly enabled, pinned SDL2 dependency for desktop window/input and
  audio transport. Configuration must not download dependencies. Retain the
  version, source commit and license; use a separately acquired source checkout.
- One serialized audio callback owns the Engine and note ledgers. The main
  thread owns display, input gestures and files. Exchange bounded copied
  messages and snapshots. No UI access to a live Engine, callback file access,
  allocation, locks, widget calls or deferred destruction.
- UI gestures enter a declared callback-boundary timing contract. Do not claim
  hardware MIDI timestamps or sample-accurate event acquisition without an
  implemented adapter and corresponding evidence.
- Preserve the original manual/note identity until its matching release. Ignore
  keyboard repeat, handle off-window release, and give focus loss, queue overflow
  and emergency Panic explicit recovery semantics. Cancel changes routing.
- Prepare and replace devices while callbacks are stopped. Validate the
  obtained sample rate, channel layout, sample format and buffer bound before
  activation. Shutdown must quiesce the callback before destroying its state.
- Save musical controls through the existing strict format outside processing.
  Held notes, source phases, transient histories and window geometry are not
  musical control snapshots. Validate loads before publication.

## Evidence required

Acceptance must include a real linked executable, meaningful command/ownership
tests, callback boundary/overflow/lifecycle checks, a calibrated callback
allocation probe, coherent state exchange under load, actual dummy-device runs,
and actual window rendering at supported sizes. Retain software-rendered
screenshots and reproducible interaction scripts. Dummy-device execution and
synthetic callback timing are separate from physical-device latency, underruns,
musician usability trials and native accessibility qualification.

The integrator records a coherent source identity, toolchain, commands and
failures for each checkpoint, reviews the concurrent remote branch, and publishes
completed work without force-pushing. The new session's actual sixty-assignment
ledger is [here](development/2026-11-13-next-phases/README.md). Earlier session
ledgers and the unchanged 500-page PDF remain preserved.
