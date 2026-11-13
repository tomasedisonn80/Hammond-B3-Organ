# Nominal playable pedal integration contract

This contract adopts a specific, bounded pedal voice and its control/event
semantics after the [prepared routing kernel](PEDAL_RUNTIME_CONTRACT.md).
It is an implementation and acceptance contract, not a statement that every
gate has run. Current outcomes belong in [STATUS.md](STATUS.md) and the
[pedal-session record](development/2026-11-13-pedals/README.md).

The source basis is [atlas pp. 139-150](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=139),
the controls/history distinction on pp. 151-156 and 389-401, and the permission
for replaceable nominal console work on
[p. 447](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=447).
The numeric mixture below is an original, explicitly adopted engineering
fixture from [this session's console review](development/2026-11-13-pedals/02-atlas-console.md).
It is not a recovered atlas companion or a measured pedal transfer.

## Adopted voice, units and limits

Use the compiled `atlas-derived-b3-c3-pedal-v1` map with
`linear-pedal-bus-reference-v1`. The playable reference explicitly supplies
**weight +1 for all 200 positions**, including the five disconnected positions.
Unit weight means a normalized software branch contribution. It is not an
assumed physical conductance or a replacement for missing electrical values.

A physical pedal press closes all eight of that pedal's binary contact states
simultaneously; release opens all eight. The policy is ideal, has no travel
time or velocity-dependent loudness, and preserves all positions independently
for diagnostics. It does not reuse the manual's nominal travel thresholds,
invent a contact-bounce model, impose monophonic priority or add an envelope.

The voice identity is **`nominal-static-pedal-mixture-v1`**. Given the ordered
bus frame `b = [Brown, Red, Orange, Yellow]`, compute two separate mixtures:

| Retained control / mixture | Brown | Red | Orange | Yellow |
| --- | ---: | ---: | ---: | ---: |
| Mixture 1, storage index 0 | 1/2 | 1/4 | 1/8 | 1/8 |
| Mixture 2, storage index 1 | 1/8 | 1/2 | 1/4 | 1/8 |

Both rows sum to one. The binary-exact rational coefficients make the fixture
auditable and produce different registrations while retaining every bus in
both outputs. The user-facing labels are **Pedal Mixture 1** and **Pedal
Mixture 2**. Do not label this chosen matrix a calibrated 16-foot/8-foot voice.

For each retained integer position `p` in 0-8, the adopted audio gain law is
**`linear-pedal-position-v1`**, with `g(p) = p / 8`. If the two matrix outputs
are `z0` and `z1`, the separate pedal contribution is:

```text
P = g(p0) * z0 + g(p1) * z1
```

Positions default to `[0,0]`. This gain law is explicit and separate from the
manual profile's drawbar gain table. All inputs/outputs are dimensionless
source-normalized values, not volts, calibrated pickup amplitudes or dBFS.
For admitted bus values in [-50,50], each mixture is bounded by 50 and the
combined `P` by 100. These are mathematical bounds, not a promise of unclipped
output after adding manuals/percussion and the common profile gain.

The selected coefficients are fixed for this model identity. If a reusable
prepared model accepts caller-authored coefficients, it must validate the
complete candidate and retain a distinct caller-supplied model identity;
arbitrary coefficients cannot silently retain this named reference's identity.
Validate every bus, control and coefficient before destination/state changes.
The fixed reference requires no reactive history, sample-rate state or file
access during rendering. A loaded replacement will require a new identified
model with electrical units, coupling, state and its own admission tests.

## One source frame and a preserved dry path

The Engine continues to call `TonewheelBank::process_frame` exactly once per
rendered frame. Pedals consume that same 91-value array. A press, release,
manual Cancel, control restore, rate change, zero-frame flush, silent interval
or disconnected output must not restart or independently advance any source.

Keep `P` separately identifiable before the existing common expression and
profile output multiplier. It belongs to the future Great path alongside lower
sustain `L`; upper sustain `U` and upper percussion `Q` remain distinct semantic
contributions. This requirement does not authorize a second generator or a new
floating-point summation of the existing manual branches. The baseline mixes
upper/lower coefficients in a particular order. Preserve that arithmetic and
its no-pedal output bytes deliberately; an inaudible pedal path must not perturb
the legacy path merely by regrouping additions or applying new normalization.

The scalar expression control keeps its current meaning and acts once on the
combined dry contribution. Do not change the existing profile output gain,
normalize by held-key/pedal count, or add a limiter to conceal clipping under
dense registrations. Offline rendering must report actual clipping under its
existing contract.

The following independence rules are mandatory:

- Lower-manual Cancel and reselection change only the manual route. Held pedals,
  their controls and source phases survive.
- Manual `AllNotesOff` continues to panic only the selected manual; pedal panic
  is its own event.
- Pedals never enter upper ninth-contact detection, percussion readiness,
  upper-B eligibility or its sustained one-foot masking/attenuation.
- All 25 pedals may contribute simultaneously, including shared-source
  collisions with other pedals or manual branches.
- A muted pedal can remain held; increasing its retained control makes the
  current source phase audible without retriggering or creating a new owner.

## Appended physical events

Preserve `Manual::Upper=0`, `Manual::Lower=1` and all existing `EventType` numeric
values 0-9. Append these types; no third `Manual` value is introduced:

| Type / numeric value | `index` | `value` | Action |
| --- | --- | --- | --- |
| `PedalOn` / 10 | One-based pedal ID 1-25 | Finite integer velocity 0-127 | Positive velocity closes all eight contacts; zero is release. Velocity does not scale the voice. |
| `PedalOff` / 11 | One-based pedal ID 1-25 | Exactly zero | Opens that pedal's eight contacts. |
| `PedalDrawbar` / 12 | Mixture index 0-1 | Finite integer position 0-8 | Updates only the selected retained pedal control. |
| `PedalAllNotesOff` / 13 | Exactly zero | Exactly zero | Opens every pedal contact and clears physical held-pedal targets, preserving controls and source history. |

For every pedal event, `Event.manual` must be the canonical value
`Manual::Lower`. This is an unused-field admission convention and a declaration
of the later lower-path relationship, not a mapping of pedals into lower
manual MIDI keys. `Upper` and invalid manual values reject for these new event
types. Engine admission converts the explicit pedal `index` into the separate
checked `PedalId` domain. Existing manual events keep their original MIDI ranges
and payload rules.

The existing whole-call transaction remains in force: preflight prepared state,
block and output bounds, event capacity, timeline overflow, sorted offsets and
every payload before any output or runtime state changes. Any rejected event
rejects the entire call and consumes zero events. Retain the current error
precedence in [ENGINE_API.md](ENGINE_API.md); do not partially apply earlier
valid pedal events before discovering a later invalid event.

Positive calls use half-open offsets `0 <= offset < frames`. Equal offsets
retain input order; the resulting state applies to that frame's source sample.
Zero-frame calls accept only offset zero, apply the events once and advance no
clock, source phase, contact travel or percussion readiness. Repeated physical
On/Off commands are idempotent target edits, not counted external ownership.
Positive disconnected-output calls still process events and advance the one
source timeline. Changing only the output connection cannot change later audio.

`active_key_count()` remains a count of the two manuals, with its existing
maximum of 122. Provide separate pedal held-count/query diagnostics and expose
all 200 contact states, including inaudible disconnected states. Do not silently
change existing key diagnostics to count 147 combined keys and pedals. Queries
must retain the current stopped/same-thread and checked-destination guarantees.

If the implementation exposes last-rendered pedal buses, mixtures or `P`, keep
that record separate from current controls/contact queries. Tag it with the
absolute sample-frame identity and the sample rate actually used for that frame;
initially it is invalid. A successful positive process call updates it from the
same source frame already used by the Engine, including disconnected output.
Zero-frame edits do not create a rendered sample or relabel the old record.
Rate reconfiguration preserves the old record's actual rate/frame tags until a
new positive frame is processed. Rejected calls preserve it; only fresh
successful preparation invalidates it. Diagnostics must not call the source bank
again, advance time, or present a mixture recomputed from newer controls as the
previously rendered sample. This record remains outside musical snapshots.

## Retained controls and B3CONTROLS3

Add exactly two pedal positions to `ControlSnapshot` and `ControlState`.
They are global retained pedal controls, independent of four manual banks,
selectors, route-enable bits and percussion eligibility. Validate both positions
with the entire candidate snapshot before replacement. Hidden or inaudible
settings must remain available for editing and serialization.

The new writer emits **`B3CONTROLS3`**. Its exact new record is
`pedal drawbars <p0> <p1>`, after the complete percussion record and before the
upper manual. The rest of the version-2 grammar is preserved:

```text
B3CONTROLS3
expression <expression>
percussion enabled <0|1> harmonic <second|third> volume <normal|soft> decay <slow|fast>
pedal drawbars <p0> <p1>
manual upper selected <A|B> route_enabled <0|1>
bank A <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
bank B <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
manual lower selected <A|B> route_enabled <0|1>
bank A <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
bank B <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
end
```

Each pedal position is one ASCII digit `0` through `8`. A valid version-3
document contains 73 tokens. Keep the existing 16 KiB input bound, ASCII
whitespace, strict expression parsing, canonical LF serialization, locale and
rounding-mode guarantees, stream-failure handling, and destination atomicity
from [CONTROL_STATE_FORMAT.md](CONTROL_STATE_FORMAT.md). Extra/missing/duplicate
records, unsupported versions, out-of-range positions and trailing data reject.
Neither a version-3 header missing the pedal record nor a malformed version-2
document activates an implicit migration.

| Read format | Retained controls after successful loading |
| --- | --- |
| `B3CONTROLS1` | Existing manual/expression values; percussion explicitly Off/Second/Normal/Slow; pedal positions explicitly `[0,0]`. |
| `B3CONTROLS2` | Existing manual/expression/percussion values; pedal positions explicitly `[0,0]`. |
| `B3CONTROLS3` | Every field must be present and valid, including both pedal positions. |

Parse into a fresh candidate so old-format loading cannot inherit unrelated
pedal values already in the destination. Keep frozen historical version-1 and
version-2 fixtures as migration inputs. Re-saving any accepted format produces
version 3; there is no implicit downgrade that drops new controls.

Snapshots remain musical controls only. They contain no held pedals, contact
states, note owners, source phase, pending events, percussion readiness, render
clock or full DSP checkpoint. A live same-thread restore preserves those running
histories while applying the new controls. Fresh Engine preparation starts with
no held pedals and muted pedal controls. An adapter must coordinate its own
ownership reset when Engine is re-prepared; snapshot loading is not that reset.

## Stable internal parameter identities

Registry schema **3**, model **`exclusive-ab-percussion-pedal-console-v3`**,
appends two records and retains the earlier 43 parameter records unchanged:

| ID | Path | Label | Engine target |
| --- | --- | --- | --- |
| `0x4000` / 16384 | `pedal.drawbar.mixture1` | Pedal Mixture 1 | `PedalDrawbar`, canonical Lower, index 0 |
| `0x4001` / 16385 | `pedal.drawbar.mixture2` | Pedal Mixture 2 | `PedalDrawbar`, canonical Lower, index 1 |

Both records use kind `pedal_drawbar_position`, unit `drawbar-position`, plain
minimum 0, maximum 8, default 0 and step count 8. Their normalized domain is
finite `[0,1]`, default zero. Convert to a position under the exact existing
half-up threshold law: thresholds `1/16, 3/16, ..., 15/16` choose the higher
position at equality; plain-to-normalized is `p/8`. The native and Python
implementations must agree at each threshold and its adjacent binary64 values
under the supported rounding modes. This position conversion is separate from
the voice's adopted audio-gain law, even though both use divisions by eight.

There are 45 internal parameter records after this addition. Preserve all earlier
IDs, metadata, defaults, meanings and conversion laws, especially expression
`0x2000`. The atlas's different absent 62-entry proposal is not a migration
authority. Update compiled descriptors and offline inspection together, keeping
the diagnostic export schema distinct from registry, saved-state and evidence
versions. These internal records are not a claim of native VST3 exports.

## External ownership and controller mapping

Physical pedal events do not implement external ownership. A later adapter must
declare a bounded typed destination and an explicit input policy without
extending `Manual` or inferring a pedal-controller octave from source pitch.
The documentary map establishes no default MIDI-note range. Any controller
mapping must be named software policy, validate its range, and retain original
destinations for later releases after a route change.

Preserve first-owner On, last-owner Off, FIFO anonymous release and stable
identified-note semantics when applying the existing ownership pattern. One
input's release or channel panic must not release another surviving owner.
Prepare candidate ownership and translated events, ask Engine to accept the
whole block, and commit owners only after Engine succeeds. A failed mixed
manual/pedal call must preserve owners, Engine state and every output sample.

Do not interleave uncoordinated direct pedal contacts/panic with an owner that
still believes it holds them. A deliberate global reset must coordinate both
layers. Native MIDI-byte decoding, host buses, automation curves, device audio
and editor origin/focus behavior each need their own subsequent contract and
executed evidence.

## Required integrated acceptance

| Gate | Evidence required before claiming the corresponding behavior |
| --- | --- |
| Voice arithmetic | Independent four-bus basis and mixed-frame oracle; exact rational matrix cases; all 81 drawbar pairs; finite/domain rejection and destination preservation. Confirm declared bounds without altering the adopted coefficients after observing results. |
| All pedal routes | Every pedal and all 200 contact positions remain observable; exercise both exceptional boundaries, the five nulls and separate duplicate branches through actual Engine use. |
| Shared source coherence | Pedal/manual collisions consume the same source sample. Compare synchronized isolated and combined contributions with a predeclared float-rounding bound; inspect all 91 phase histories through notes, silence and disconnected output. |
| Legacy output | Frozen baseline versus new executable comparisons for manual-only ideal/percussion-off and enabled-console fixtures. Retain exact PCM/WAV where the contract preserves arithmetic; report any deliberate metadata additions separately. |
| Division independence | Lower Cancel/reselect and manual panic leave pedals intact; pedal panic leaves manual holds intact; all percussion modes/readiness/detection ignore pedal changes; muted-to-audible held pedals preserve phase. |
| Event transactions | Stable same-offset permutations, zero-frame flushes, block-end boundaries, regular/irregular partitions, full occupancy, invalid enums/IDs/values, late-invalid batches and timeline/output/capacity rejection. |
| Controls and migration | Both pedal positions round-trip; v1/v2 load into a nonzero destination with explicit mute; malformed v3 rejects atomically; live restore retains owners/contacts/phases/readiness/clock; old 43 records remain exact. |
| Rate and lifecycle | Supported 44.1/48/96 kHz transitions preserve pedal controls/contacts and existing source histories; same-rate no-op and rejected transitions remain atomic. No artificial pedal time state is introduced. |
| Ownership | Overlapping origins/channels, anonymous repeats, identified conflicts, mapping changes, capacity failures and Engine-rejected blocks preserve the declared first/last-owner and transaction rules. |
| Runtime and evidence | Allocation/deallocation checks cover the enabled path and maximum occupancy; bounded timing reports name their workload. Render/evidence/diagnostic exports retain model/map/voice/gain identities, events, rate, seed, partitions, measurements and actual clipping. |

The resulting accepted scope is an audible **nominal pedal division in the
shared offline engine**. It does not establish physical reactor/source loading,
complex low-wheel spectra, true contact travel/bandwidth, a calibrated footage
response, complete M3, scanner/AO-28/Leslie modeling, native product readiness
or one-to-one measured fidelity. Those remaining dependencies stay visible in
[M3_NEXT_GATE.md](M3_NEXT_GATE.md), [PLAN.md](PLAN.md) and the next handoff.
