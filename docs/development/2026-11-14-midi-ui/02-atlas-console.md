# A02 - Complete atlas console and ownership reading

## Actual assignment and source

- Worker: `/root/w01_a02_atlas_console`; wave 1, assignment A02 of this
  separately requested session. No earlier worker is counted here.
- Inspected source HEAD: `0f7b90037e51e101d8fa0bfe31af40209d751659`.
- Owned output: this review only. No production code, shared status, previous
  ledger or source PDF was changed; no commit or push was performed by A02.
- Source: [the unchanged atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
  edition 12 November 2026, SHA-256
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- **All text on PDF pages 85-168 inclusive was read**, covering all fourteen
  chapters 013-026. The six sequential, untruncated tool outputs covered
  85-98, 99-112, 113-126, 127-140, 141-154 and 155-168.
- The 84 extracted pages contain 212,152 Unicode characters. SHA-256 of their
  UTF-8 contents concatenated in page order, without added separators, is
  `c65d90f319a7367dca2ff21e41f53fa4beca67db2ffe83b90b150a258a8a8a75`.
  This identifies the extraction used for reading; it does not replace the PDF.
- Rendered and visually inspected complete pages **122, 140 and 152** at a
  1,500-pixel maximum dimension. This checks the chapel matrix, exceptional
  pedal map and ownership table against their actual page layout. It does not
  claim that every photograph, patent plate or cited external source was read
  independently.
- Inspected `AGENTS.md`, current status and handoff entries, the existing atlas
  consolidation, `Session.h`, `PERFORMANCE_INPUT.md` and `NOTE_OWNERSHIP.md`.
  README, PLAN and NEXT_STEPS were also available in the inherited parent
  context. Earlier source reviews remain their own historical evidence.

## Implementation decision for this session

The next dependency-ready work is the independent M9 input adapter and native
view. These pages support an explicit raw-MIDI-to-console boundary with retained
origin, deterministic ownership and bounded recovery. They do **not** justify
changing the shared generator, nominal gain curves, pedal network, percussion
calibration or scanner integration merely to make a new input device or drawing
look more complete.

The existing `Session` interface is suitable for single-producer command
serialization, but its UI namespace must be resolved before raw MIDI is admitted.
`kUiInputChannel` is zero; `ReleaseUiNotes` clears that channel on both origin
buses. A direct raw-MIDI channel-number copy would let MIDI channel 1, represented
internally as zero, collide with UI release behavior. Different note IDs alone do
not solve a channel-wide release. Freeze an explicit supported routing and source
namespace policy, including channel and device limits, and independently test UI
focus loss while an external controller holds the same and different pitches.

All current Session commands enter at offset zero and are applied at an audio
callback boundary. A backend timestamp is useful provenance but does not make
that contract sample-accurate. Either retain and disclose boundary quantization
with a deterministic late-event policy, or deliberately extend the scheduling
contract with tests. Do not quietly describe callback-boundary delivery as
sample-exact hardware MIDI.

## Complete chapter findings

| Chapter / pages | Source finding | Consequence for current work |
| --- | --- | --- |
| 013 / 85-90 | Shared mechanical residuals, local angular/gap variation, electrical hum, scanner and Leslie movement have different causes. Nominal forcing rates do not identify modulation depth. Random processes require sample-time indexing and persistent seeds. | Notes, controller reconnection, view redraws and transport must not reset source state or manufacture per-note irregularity. Do not add an undocumented wow/tremolo effect as part of UI work. |
| 014 / 91-96 | Immutable observations, model profiles, compiled banks and advancing playback state are separate. Evidence, units, IDs and explicit unknowns belong to each quantity. Table V concerns G-G service output, not raw pickup amplitude. | MIDI/UI configuration must not rewrite calibration. A valid schema is not hardware validation; nil observations cannot become zero-valued defaults. File/profile work stays outside the callback. |
| 015 / 97-102 | Each manual has 61 playing keys, separate from 12 reverse-colored preset keys. The proposed software mapping is MIDI 36-96 to keys 1-61. Harmonic routing uses 549 explicit entries and repeated octave foldback. | Reject out-of-zone MIDI notes or apply a documented input transpose before admission. Do not fold out-of-range controller notes into the manual; harmonic foldback belongs inside a valid playing key. |
| 016 / 103-108 | One generator field owns 91 shared continuous sources. Notes, drawbars, presets and rate changes do not implicitly restart phase. Zero-frame flushes do not advance time. | Use the existing Engine ownership rather than allocating a synth voice per MIDI note. Keep the UI and MIDI adapters from preparing/resetting a live engine during routine control changes. |
| 017 / 109-114 | Physical marking 0 is silent and 8 is full. A roughly 3-dB nominal table is an explicit surrogate; a loaded matching-transformer network is separate. Same-source paths add coherently. | Use existing parameter conversion, cap direction and integer values. Do not reverse a cited table's indexing, normalize chords by held-key count or call the current gain law measured. |
| 018 / 115-120 | A manual key owns nine contact histories with a shared gesture; make and break need distinct evidence. Ordinary MIDI selects a named synthetic trajectory; velocity need not scale steady organ loudness. | Preserve velocity as an input datum under the existing core contract. MIDI-byte decoding must not add velocity-sensitive steady gain, an arbitrary click sample, or a generic debouncer that erases future contact behavior. |
| 019 / 121-126 | C is momentary Cancel with no electrical contacts; C#-A selects nine fixed registrations; A# and B select retained banks. Physical simultaneous latching is possible but requires a separate network model. Upper B changes percussion eligibility without resetting its charge history. | Keep Cancel distinct from Panic and note release. A visual reverse octave needs explicit functionality/status; the existing A bank corresponds to the A# adjust concept, not a new fixed preset. Ordinary program mapping must not silently introduce full-state recalls. |
| 020 / 127-132 | Percussion is one shared upper-manual process, reached through upper B and the 1-foot contact. Additional owners/notes do not create new independent envelopes. Zero-duration off/on pairs provide no recharge time. | MIDI duplicates, overlaps, note ordering and scoped releases are audible correctness requirements. A second controller cannot prematurely release the key or retrigger percussion. |
| 021 / 133-138 | Harmonic return, percussion audio, upper attenuation, gain and charging are distinct routes. Listed RC products are derived electrical time constants, not measured audible decay lengths. | Controller/UI actions must use the existing four percussion parameters and preserve the displayed retained state while ineligible. Do not turn a drawbar into percussion volume or invent a calibrated readiness/decay display. |
| 022 / 139-144 | The pedalboard has 25 notes, eight contacts and four buses; the third-contact column has documented duplicates and five disconnections. It consumes the same sources as both manuals. | Specify a separate MIDI-note-to-PedalId mapping, display that policy, and reject outside it. Do not reuse the 61-note manual mapper, create another bass oscillator or label nominal mixtures as measured 16'/8' responses. |
| 023 / 145-150 | Expression is a common preamplifier network, distinct from final monitoring gain. CC11 is proposed as an assignable controller with endpoint calibration/inversion before the instrument curve. | An initial CC11 adapter can target the existing explicitly nominal expression parameter; call it that. Keep device calibration, stored expression and DSP history separate. Resolve multiple sources through one command order. |
| 024 / 151-156 | Controls, physical ownership and DSP history have distinct owners. Releases use original destinations; anonymous repeated notes have a declared bounded FIFO policy. CC120/121/123 have distinct semantics. | This is the direct M9 contract: origin-aware routing, single producer, stable ordering, bounded admission, observable recovery and truthful timestamp qualification. |
| 025 / 157-162 | The selected nominal scanner line has 18 inductors, 18 capacitors and 19 observed voltages; it needs a full loaded graph, separate references and numerical evidence. | A control/visual upgrade must not silently enable scanner audio before its numerical gate. A source nominal or a nice picture does not resolve the currently documented same-hertz failure. |
| 026 / 163-168 | Sixteen stator positions, nine terminal values and nineteen ladder outputs are separate domains. Rotor phase continues through bypass and silence. Coupling/loading and speed remain unmeasured. | Keep future visual rotor/camera state separate from audio angle and physical parameter provenance. Do not expose a decorative scanner as a functioning calibrated module. |

## Concrete MIDI contract and independent acceptance recommendations

### Identity, ownership and routes

The original policy on pp. 130 and 151-152 records source, bus, channel,
identity/fallback serial, destination, key and press sequence. For the first
implementation, explicitly state the maximum active devices and supported MIDI
channels. If only one device and three division channels are supported, expose
that finite scope directly instead of claiming arbitrary multi-device routing.

Use a distinct, collision-free internal ownership mapping. A channel split alone
does not prove device isolation when two ports deliver the same channel/pitch.
The actual `HostNoteEvent` key space currently distinguishes bus, channel and
optional note ID, while `PedalNoteEvent` uses a separate namespace. Do not extend
those persistent core types casually as part of a backend adapter.

For anonymous repeated MIDI NoteOn messages, preserve a documented bounded
policy. The atlas proposes FIFO; existing anonymous core events already use it.
An identified duplicate is idempotent, but inventing the same per-pitch identity
for every incoming NoteOn would silently change that anonymous policy. Decide
whether the adapter uses anonymous ownership or generated identities and test
the matching release behavior independently.

Acceptance must include these authored streams:

1. A UI key and a MIDI controller hold the same manual pitch; releasing either
   alone leaves the other owner held. Window focus loss releases only UI notes.
2. Two external origins/channels hold one pitch, then one releases; the physical
   key remains down and no second oscillator or percussion attack was added.
3. NoteOn, repeated NoteOn and two releases exercise the chosen duplicate/FIFO
   policy, including unmatched releases and distinct velocities.
4. A routing configuration changes while notes are held; releases go to their
   original destinations. Alternatively, reject active remapping or retire its
   precise owners under a declared rule; never strand old holds.
5. Raw `0x9n` velocity zero releases, and raw `0x8n` release velocity is converted
   to the canonical core release value. This is a raw-MIDI rule, not a blanket
   assertion about every host's normalized event format.
6. Manual range 36-96 and the explicitly chosen 25-note pedal range accept both
   endpoints and reject adjacent pitches without transposition/foldback leakage.

### Time, buffering and recovery

Only the main/UI producer may call `Session::post()`. Backend callbacks must feed
a separate bounded transport to that producer, or a supported polling backend
must be serviced by the producer itself. A second direct poster would violate
the present queue's concurrency contract even if it appears to work in a smoke
test. Backend handles, vector resizing, logging, mutex operations and joins stay
outside the audio callback.

Define time in one stated unit and clock domain. A device-relative timestamp
cannot be compared directly with an arbitrary host epoch. Retain arrival ordering
for equal-time messages and specify what happens to late, regressing or far-future
timestamps. The proposed atlas host-container priority on p. 153 is an adapter
policy; the actual combined core facade preserves its input order. No hidden
sort may reorder a note-off/on pair or a route transition.

Overflow and disconnect need executable recovery evidence. A full queue cannot
drop just a note-off and keep its note-on alive indefinitely. The current Session
queue deliberately requests global recovery when exhausted; the MIDI layer must
observe that outcome, clear stale adapter state and avoid automatically replaying
notes. A normal device disconnect should retire only that device's owners if the
declared namespace supports it. If broader recovery is unavoidable, record its
exact user-visible effect instead of claiming isolation.

Independent tests should cover transport capacity endpoints, overflow while
notes are held, queued note-on followed by disconnect, reconnect with a new
generation identity, malformed message fragments, source shutdown before object
destruction, and no post/join race. Add physical controller/backend timing and
hotplug qualification separately once a real device is available. Synthetic
streams validate policies but cannot attest physical latency or dropout rates.

### Controllers and honest feature scope

Pages 148 and 156 provide an implementation direction, not a complete MIDI
specification. Freeze an explicit mapping table and independently check the
chosen backend's actual protocol documentation during implementation.

| Message family | Appropriate first-slice decision |
| --- | --- |
| Notes | Canonical ownership events with the declared division zones and velocity policy. |
| CC11 | Optional mapping to the current normalized nominal expression coordinate through the same parameter bridge. |
| CC123 | Scoped ordinary release of addressed owners, preserving other owners and continuous shared source phase. |
| CC120 | Distinct immediate-suppression policy if actually implemented; do not merely relabel ordinary release or a global Panic. |
| CC121 | Reset only the explicitly declared controller defaults, without resetting source phases or unrelated registrations. |
| CC64 sustain | Disabled/ignored with a documented diagnostic policy in the vintage baseline unless a separately named extension is deliberately built. |
| Program change | Ignore explicitly, or map only a frozen approved set of existing selectors. A reverse-key selection is not an implicit whole-preset restore. |
| Pitch bend/aftertouch/SysEx/clock | Declare supported or ignored status; no guessed pitch bend, synthesis feature or unbounded payload accumulation. |

Unsupported messages should not be misreported as working controls. Any deliberate
restriction can still produce a useful first external-MIDI milestone when the
supported contract and recovery behavior are tested.

## UI implications and visual review

The p. 122 photograph shows a reversed preset octave adjacent to playing keys,
and the table contains eighteen nine-digit registrations. It is a contextual
hardware photograph with a named CC BY-SA 3.0 source, not an application-wide
pixel reference or proof of the selected specimen's exact proportions. The
p. 152 half-moon photograph identifies Chorale and Tremolo; it does not establish
a third Stop position. The p. 140 patent plate explicitly belongs to a historical
embodiment, not the selected production circuit.

Do not add decorative interactive controls whose audio functions are absent.
Maintain separate EDIT and SOUNDING bank indications; editing an inactive bank
must not change the active registration. If reverse preset keys are drawn, C
must return after Cancel rather than appear persistently latched. A#/B labels can
explain the physical convention while preserving current stable A/B parameter
identities. Fixed chapel selectors must wait for their agreed selector/state
contract rather than copying a catalog row invisibly on a graphic-only click.

Percussion's stored tablets remain visible when upper B is ineligible. Cancel
must neither clear held-note indicators nor mute the other manual/pedals.
Keep numeric MIDI pitches/PedalIds available to diagnostics so note-name octave
conventions do not alter behavior. A display can faithfully reflect these
contracts without claiming measured component geometry or sound.

No singular full-product UI reference was established within the assigned pages.
The integrator and design-page reviewers must identify the exact requested image
and retain an actual side-by-side/difference review before asserting a one-to-one
match. This review does not establish pixel parity.

## Executed work, boundaries and handoff

Executed: complete 84-page text reading; independent local PDF hash; sequential
extraction identity calculation; Poppler rendering and visual inspection of three
named pages; inspection of current adapter and ownership contracts. All six text
reads completed without output truncation. No application build, test suite,
hardware MIDI run, measured audio comparison or UI parity check was executed by
this research assignment.

The next implementation owners should freeze namespace/timestamp/recovery rules
before editing the adapter, then write independent streams that prove those rules
against the actual Session and Engine. Keep the shared core, physical acquisition
gates and other development tracks intact. The parent integrator owns acceptance,
shared documentation, session accounting, commits and verified publication.
