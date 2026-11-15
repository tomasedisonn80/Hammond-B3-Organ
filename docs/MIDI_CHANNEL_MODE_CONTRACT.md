# Native MIDI channel modes

Contract: `standalone-channel-modes-v1`. This is the implementation and
acceptance target for the [product continuation](development/2026-11-15-product-continuation/README.md),
not an executed acceptance result. Basis: atlas pp. 151–156 and the MIDI
Association's [message summary](https://midi.org/summary-of-midi-1-0-messages)
and [controller table](https://midi.org/midi-1-0-control-change-messages),
inspected 15 November 2026 UTC. Those public tables are overviews, not a claim
of complete MIDI/General MIDI conformance. The product policies below explicitly
describe this instrument's shared controls and ownership.

## Wire admission and distinct operations

The existing complete-packet validation, mapped-channel routing, arrival order,
bounded inbox and per-turn drain budget remain unchanged. A mapped wire channel
selects exactly one existing internal Upper, Lower or Pedal owner namespace.
An unmapped channel remains `UnmappedChannel` and performs no operation.

| Input | Accepted value | Native action and scope |
| --- | --- | --- |
| CC120, All Sound Off | 0 only | A distinct `ScopedSoundOff` Session command retires every owner belonging to the addressed internal bus/channel and manual/pedal domain. With the admitted ideal-contact Engine, its final-owner contributions are absent from the first rendered sample after application. |
| CC121, Reset All Controllers | 0 only | Produce `MidiParameterEdit{8192, 1.0}` through `UiModel::external_parameter`. This resets the single declared expressive controller, global expression, without releasing notes. |
| CC123, All Notes Off | 0–127 | Preserve the existing lenient decoder compatibility: all values release addressed ownership through `AllNotesOff`. The MIDI-defined wire value is 0; accepting other values is this receiver's historical extension. |

Nonzero CC120/121 values return `OutOfRange`, with no action. Malformed packet
shape/data still takes precedence. Repeated valid mode packets are separately
decoded and counted; a controller reset already at its default may produce no
redundant UI snapshot. CC122 and CC124–127 remain unsupported.

CC121 **bypasses endpoint/inversion calibration**: it requests normalized 1.0,
not a synthetic raw CC11 value of 127. The installed calibration, channel map,
device epoch, note owners, four drawbar banks, fixed selections, percussion
settings and pedal mixtures remain unchanged. CC11 already controls one global
expression value from any mapped division, so CC121 on any mapped division
affects the whole instrument's expression. It is not a per-channel gain reset.
It neither clears nor reloads saved controls; the normal dirty/pending and
acknowledgment path applies. Concurrent pending UI edits must be retained.

## Typed boundary and immediate-silence limit

Append `ScopedSoundOff` to `SessionCommand`, preserving the order of its four
existing alternatives. Its proposed fixed payload is a `SoundOffDomain` enum
(`Manual = 0`, `Pedal = 1`), `std::uint8_t bus` and `std::uint8_t channel`.
Reject unknown domains, buses outside the corresponding ownership namespace
and channels outside 0–15 in `Session::post`, before reserving a sequence or
queue slot. The command has no timestamp: like every Session command it applies
at the next accepted callback's offset-zero boundary.

Both typed domains admit buses 0 and 1 under their existing ownership constants;
the current MIDI pedal mapping uses only bus 0. The exact payload is
`enum class SoundOffDomain : std::uint8_t { Manual = 0, Pedal = 1 };` and
`struct ScopedSoundOff { SoundOffDomain domain{SoundOffDomain::Manual};
std::uint8_t bus{0}; std::uint8_t channel{0}; };`.

MIDI decoding supplies the existing mapped scope: Upper `(Manual,0,1)`, Lower
`(Manual,1,2)`, Pedals `(Pedal,0,3)`. UI owners remain on channel zero. Other
Session callers can deliberately target another valid origin; the decoder
never broadens a mapped packet to a different origin or a global Panic.

The immediate-silence reduction is valid **only for `ContactMode::Ideal`** in
this contract. The existing `Engine::contact_mode()` returns the owned
ContactBank mode, and standalone `Session::Impl::prepare` calls the two-argument
`Engine::prepare`, which selects ideal contacts. No guessed model-name comparison
or change to Engine sound is necessary.

Inside `Session::Impl::apply`, validate the ideal-mode precondition before
lowering `ScopedSoundOff` to one canonical `HostNoteEvent::AllNotesOff` or
`PedalNoteEvent::AllNotesOff` through the existing performance transaction.
That internal reduction removes addressed owners in stable order and emits
ordinary releases only when their final physical owner retires. It is justified
by this Session's ideal-mode guarantee, not a general equivalence of the two
MIDI messages. If a future Session prepares non-ideal contacts, this command
must return `Status::InvalidEvent` before performing that reduction; the normal
Session command-failure/recovery contract remains authoritative.

That existing failure recovery is global. It is not a promise of scoped silence
for a future non-ideal Session; such a configuration needs a new policy before
it can advertise this feature.

Do not add a partially supported generic core note action. `HostNoteKind`,
`PedalNoteKind`, both ownership translators, PerformanceInput, InputProcessor,
HostTimeline and Engine remain unchanged. In particular, the generic
finite-travel Engine gains no advertised All Sound Off support from this work.

This deliberate refusal prevents an ordinary release from masquerading as
immediate silence in the finite-travel contact model. Current ideal contacts
have no release tail; percussion audio is multiplied by currently connected
contacts. Do not reset the shared percussion readiness/amplitude, oscillator
phases, sample clock, presets or expression to handle CC120. A UI or other
channel owner of the same physical key keeps that key audible. Another division
must remain audible. With no surviving owners, all addressed sustained and
contact-borrowed percussion contributions are zero from the application boundary.

The command does not establish a persistent mute: a later fresh NoteOn can play.
An unmatched old NoteOff before a fresh press is harmless; anonymous raw MIDI
does not promise to distinguish a stale release arriving after a new same-pitch
press. Shared amplifier/reverb tails, non-ideal contacts, sustain extensions and
VST3 channel-mode delivery require separate future policies and tests. Global
Panic retains its separate existing behavior.

## Implementation ownership and acceptance

Session worker paths: `apps/standalone/Session.h/.cpp` and its contract comments.
Decoder worker paths: `apps/standalone/MidiInput.h/.cpp`, coordinated sequentially
with expression calibration. No parameter registry, state serialization, core
ownership/processing, ContactBank, plugin UUID or R4 change is authorized here.

Independent acceptance must establish:

1. Canonical distinct CC120/121/123 decoding on every channel mapping, malformed
   and nonzero rejection, legacy CC123 compatibility and repeat behavior.
2. Upper/Lower/Pedal isolation, same-pitch UI/MIDI owners, anonymous duplicates,
   stable survivors, fresh presses, late releases and unchanged controls.
3. Immediate zero contribution in an ideal Engine, including percussion, and
   continued source phase/clock against an independently rendered control trace.
4. Invalid typed scope refusal before queue publication, preserved existing
   variant identities, explicit ideal preparation and defensive ideal-mode guard.
   Do not claim an executed non-ideal Session test when its public preparation
   API cannot create one; non-ideal core support remains outside scope.
5. CC121 applies expression 1.0 with inverted/narrow calibration, preserves
   simultaneous pending UI controls and does not release notes or reset settings.
6. Session queue rejection/recovery, partition equivalence, bounded work and
   allocation-free accepted processing. Record actual source/configuration/results.

Preserve all 47 parameters, `B3CONTROLS4` and readers 1–3. A native replay does
not qualify a physical MIDI device, DAW, deadline or measured organ.
