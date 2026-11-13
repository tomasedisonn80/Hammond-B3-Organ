# Nominal contact and shared percussion contract

This is the M3 integration contract for the console continuation. The source is the
[preserved research atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), particularly
pp. 37-42, 109-138, 389, 394, 401 and 447. Page references below identify that atlas;
its citations of factory documents are not a claim that this continuation has
independently measured or reconstructed the complete factory circuit.

The new contact and percussion modules are an explicitly nominal engineering
checkpoint. [STATUS.md](STATUS.md) records which integration and acceptance work
has actually run. Pedal audio, full physical preset latching, continuous drawbar
travel, loaded expression, scanner and AO-28 electronics retain separate gates.

## Model identity and ownership

[ConsoleModel.h](../include/hammond/ConsoleModel.h) owns two fixed-size parameter
values: `ContactProfile contacts` and `PercussionProfile percussion`. Default
construction and `make_legacy_console_model()` choose ideal contacts;
`make_nominal_console_model()` explicitly chooses linear contact travel. Both
supply the same nominal percussion coefficients. A parameter set does not enable
percussion: the retained `PercussionSettings::enabled` control defaults to false.

The existing `Engine::prepare(profile, spec)` contract retains the legacy default.
The integration overload `prepare(profile, spec, console_model)` installs a fully
validated copy while processing is stopped. Unsupported rates return `InvalidSpec`;
invalid console parameters return `InvalidProfile`. Failure must preserve the
previous engine, musical state and clock. Successful preparation deliberately
starts a fresh organ state; it is not a live sample-rate migration operation.

| Owner | Data and responsibility |
| --- | --- |
| Source `RuntimeProfile` and `TonewheelBank` | Existing routing, normalized source amplitudes, 91 shared continuously advancing phases and source samples |
| `ConsoleModel` | Immutable copied contact/percussion coefficients, separate from source profile and musical controls |
| `ContactBank` | 122 key trajectories/targets and 1,098 independent contact states; no oscillator or drawbar ownership |
| `ControlState` | Four retained drawbar banks, selected routes, expression and retained percussion settings |
| `PercussionState` | Exactly one evolving readiness value per organ; no per-note envelopes or source lookup |
| `Engine` | One sample clock; event validation; route eligibility; coherent mixing; detector and selected-harmonic routing |
| Host/input adapter | Bounded external note ownership, converted into physical-key targets; the legacy physical-key API stays idempotent |

The contact algorithm IDs are `ideal-contacts-v1` and
`nominal-linear-travel-v1`; percussion is `shared-readiness-v1`. These identify
algorithm families, not every possible custom profile. Evidence for a modified
profile must additionally retain its exact parameter identity. No value below is
a calibrated B-3 dimension, contact timing or output voltage.

## Contact parameters and behavior

Each manual key owns nine make thresholds and nine break thresholds, plus its
full-travel press/release durations. The named nominal factory repeats this
**proposed** table for every key while keeping each key's data separately editable:

| Parameter | Nominal factory value | Unit and evidence |
| --- | --- | --- |
| Make thresholds, contacts 0-8 | 0.12, 0.22, 0.32, 0.42, 0.52, 0.62, 0.72, 0.82, 0.92 | Normalized key travel; proposed synthetic values |
| Break thresholds, contacts 0-8 | 0.04, 0.14, 0.24, 0.34, 0.44, 0.54, 0.64, 0.74, 0.84 | Normalized key travel; proposed synthetic values |
| Full press duration | 0.008 | Seconds; proposed, unmeasured |
| Full release duration | 0.012 | Seconds; proposed, unmeasured |
| Contact amplitude | Open = 0; closed = 1 | Binary nominal connection; not conductance in siemens |

The rationale comes from the atlas's independent-contact/hysteresis architecture
(pp. 39-40, 115-120), not from a measured universal closure order. Actual thresholds,
key geometry, bounce and load-dependent resistance remain unknown. Repeating the
same factory defaults across keys is a declared simplification.

All profile values must be finite. Every contact requires
`0 <= off_threshold < on_threshold <= 1`; each duration must be within
`[0.0001, 1]` seconds. These are computational support bounds, not manufacturer
tolerances. Validation checks every key even in ideal mode, so unused malformed
travel values cannot silently survive preparation.

In linear-travel mode, a physical press/release sets target 1/0. Increasing
position uses full-travel step `1/(sample_rate * press_seconds)`; decreasing
position uses the corresponding release duration. Motion stops at the target.
A change of target starts from the current position, preserving incomplete return
and existing contact hysteresis. Duplicate commands do not restart motion.
Velocity does not scale sustained gain and is not used to invent measured motion.

An open contact closes at `position >= on_threshold`. A closed contact opens at
`position <= off_threshold`. Between these thresholds, its previous state is
retained. Separate contacts remain separate even when foldback maps them to the
same tone source. Coefficients may be aggregated only after these connection
states have been evaluated (atlas pp. 100, 111, 464).

`ContactBank::set_position_target()` is an explicit normalized partial-hold extension.
Linear travel accepts finite targets in `[0,1]`; ideal mode accepts only 0 or 1.
An interior target in ideal mode is rejected without mutation. The diagnostic
`key_target` Boolean and Engine's `key_down`/active-key count mean `target > 0`,
not that any or every contact is closed. For
example, approaching 0.5 from below closes four contacts under the nominal table;
approaching it from above retains five because the fifth contact has break
threshold 0.44. This is a property of the declared hysteresis model.

Ideal mode applies an accepted endpoint command immediately to position and all
nine contacts, preserving the previous engine's sample-offset behavior. Its
`advance_frame()` performs no motion. `panic_manual()` immediately clears one
manual's targets, positions and contacts in either mode. It changes no source,
readiness or external clock. Engine `AllNotesOff` uses this explicit immediate
release policy; ordinary NoteOff in travel mode follows the release trajectory.

This checkpoint uses sample-grid binary switching. It does not implement measured
bounce, fractional contact edges, band-limited switching, an independent random
click burst, calibrated continuous position input, or physical key mechanics.

## One sample convention

State exposed at the start of a process call describes its next sample to render.
For each positive sample at absolute frame `n`:

1. Apply all events at `n` in supplied stable order. Ideal contact commands change
   contacts immediately; travel commands change targets without advancing time.
2. Resolve the current contact states, retained controls, upper-B eligibility,
   physical detector, sustained masks and selected percussion-harmonic routes.
3. Read the shared source frame and render using current positions and `q[n]`.
   Every contact referring to one source uses the same sample. Apply the common
   normalized output/expression surrogate once after the two musical paths meet.
4. Advance contact travel and readiness exactly once for `1/sample_rate` seconds,
   using the detector/settings resolved for this sample. Advance each source and
   the render clock once. The next sample observes the resulting state.

A source-bank method may internally advance after returning its current sample;
that implementation detail must not create a second advancement. Trajectory and
readiness advancement occurs even through silence, Cancel and disconnected output.

A zero-frame call applies accepted events and immediate ideal commands, then
returns without advancing positions, readiness, phases or clock. Releasing and
pressing at one offset supplies zero recovery time. The final connectivity after
that event cluster governs the next positive sample. A newly joining chord note
never initializes readiness. Invalid-call preflight covers the entire request;
rejection consumes no events and changes neither existing nor new state/output.

## Percussion routing and current-state gain

Stored percussion settings remain present when a route is ineligible. Define:

- `eligible = enabled && upper_route_enabled && upper_selected_bank == B`.
- `physical_detector = OR(upper-key contact[8])`, independent of drawbar positions.
- `routed_detector = eligible && physical_detector`.

Contact index 8 is the **ninth contact, 1-foot, eighth harmonic**. It is not the
eighth drawbar counted from the left. Lower-manual and pedal activity never enter
this detector (atlas pp. 127-128).

| Route/control condition | Percussion audio | Upper sustain | Lower sustain |
| --- | --- | --- | --- |
| Percussion disabled, upper A, or upper route cancelled | Muted | Ordinary selected routing; no percussion 1-foot mask or compensation | Ordinary routing |
| Eligible, Normal volume | Selected harmonic through shared current gain | Mask only contact/drawbar index 8; apply configured normal upper-sustain factor | Unchanged |
| Eligible, Soft volume | Selected harmonic through soft current gain | Mask only contact/drawbar index 8; unity compensation factor | Unchanged |

The audible 1-foot mask must not erase its stored drawbar value, physical contact
or source phase. Normal compensation applies only to eligible upper sustained
audio, never the lower path or percussion. The selected harmonic's sustained
return remains its ordinary drawbar branch; do not add it a second time.

Second-harmonic percussion sums existing upper contact/source routes at index 3
(4-foot); third harmonic uses index 4 (2-2/3-foot). It does not multiply those
routes by their sustained drawbar gains and does not create an oscillator. The
selected-harmonic contacts and the index-8 detector are intentionally distinct.
A partial hold can pass selected-harmonic audio while its keying contact is still
open; under this nominal model that audio sees recovered readiness. Do not add
an undocumented detector gate to hide this case. Hardware/circuit comparison must
later qualify the real transition (atlas pp. 128-138).

## Readiness coefficients, provenance and replacement path

`shared-readiness-v1` uses one dimensionless `q` in `[0,1]`, prepared to 1.
Its proposed gain map is `F(q)=q`; `q` is not capacitor voltage. For constant
settings during one sample:

```text
connected: q[n+1] = q[n] * exp(-1 / (sample_rate * selected_decay_seconds))
open:      q[n+1] = q[n] + (1 - q[n]) * (1 - exp(-1 / (sample_rate * recovery_seconds)))
```

Preparation precomputes the coefficients; the callback performs no exponential,
allocation, file access or lock. The open-branch step may use `-expm1()` during
preparation for stable coefficient calculation. Current-sample audio uses `q[n]`,
so a recovered ideal press can begin at q = 1 before its first decay step.

| Profile value | Nominal factory | Evidence and applicable scope |
| --- | --- | --- |
| Slow decay | 1.551 s | Derived hypothesis `R58*C31`, using atlas p. 135 nominal components |
| Fast decay | `(1.5e6*4.7e6)/(1.5e6+4.7e6)*3.3e-7` s, approximately 0.3752419355 s | Derived isolated parallel-RC hypothesis, atlas p. 135 |
| Recovery | 0.03432 s | Derived hypothesis `(R55+R56)*C31`, atlas p. 135 |
| Normal / Soft percussion gains | 1 / 0.5 | Proposed normalized amplitudes; no measured level ratio |
| Fast gain multiplier | 1.5 | Proposed constant approximation to the qualitative gain coupling on p. 134; no fitted bias/valve transfer |
| Normal upper sustain factor | 0.70710678118654752440 | Proposed dimensionless attenuation; no measured production transfer |
| Soft upper sustain factor | 1 | Proposed bypass of nominal normal compensation |

The underlying nominal quantities on pp. 133-135 are C31 = 0.33 microfarad,
R57 = 1.5 megohm, R58 = 4.7 megohm and R55 + R56 = 104 kilohm. The resulting RC
products are not measured audible decay lengths. Specimen/revision, actual parts,
transformer loading, cutoff, valve transfer and waveform coloration are unresolved.

Support bounds require finite taus in `[0.0001,60]` seconds; normal/soft gains and
fast multiplier in `[0,4]`; and upper-sustain factor in `[0,1]`. These bounds are
engineering choices. Decay below the smallest normal double is flushed to zero
as a declared numerical policy, not measured leakage or a physical cutoff.

Every positive sample with `routed_detector == false` recovers readiness, including
while upper routing or the percussion control is disabled. Leaving B while holding
keys can therefore permit recovery; returning B uses the state actually accumulated.
This is a versioned nominal routing policy pending captures, not a statement that
all real switch transients follow this surrogate. Changing harmonic, volume, decay,
drawbars or routes never resets q. A panic clears contacts, after which elapsed
samples recover q; it does not make an instantaneous fresh attack.

A later component/behavioral model replaces the readiness/gain/transfer layer while
preserving the tested contact, routing and timeline contracts. Calibrated threshold,
recharge and held-switch captures, source-qualified AO-28 topology and independent
numerical checks are required before making the corresponding physical claim
(atlas pp. 131, 137-138, 447).

## Event and saved-control extension

Existing event numeric values 0-8 retain their meaning. Event value 8 remains
`EventType::Percussion`, with `manual = Upper` and finite integer value 0 or 1:

| Event index | Retained setting | Value 0 | Value 1 |
| --- | --- | --- | --- |
| 0 | enabled | Off | On |
| 1 | harmonic | Second | Third |
| 2 | volume | Normal | Soft |
| 3 | decay | Slow | Fast |

The Lower manual, other indices and fractional/nonfinite values are invalid for
this global upper-percussion event. Event application changes controls only;
route eligibility is derived afterward. Existing source IDs, parameter IDs and
drawbar normalization are preserved. Future host exports require their own mapping
and qualification; this event is an internal engine contract.

### Direct partial-key input

Event value 9 is `EventType::KeyPosition`. Its `manual` is Upper or Lower,
`index` is a manual MIDI note in 36-96, and `value` is a finite normalized target
in `[0,1]`. Offsets follow the ordinary half-open/stable-order event contract.
The current contact mode is part of admission: `LinearTravel` accepts the complete
range; `Ideal` accepts exactly 0 and 1. An interior ideal-mode target, invalid
manual/note, nonfinite value or out-of-range target returns `InvalidEvent` for the
entire call. Even valid events preceding the bad event are not applied, no events
are consumed, and state/output remain unchanged.

An accepted travel target changes the destination while retaining current
position and all nine contact histories. Repeating an identical target preserves
the existing motion segment. Applying a target itself advances no time; the next
positive sample renders current contact connectivity before one travel step.
Same-offset events retain their supplied order, with the final target governing
subsequent motion. Endpoint ideal commands change connectivity immediately under
the existing ideal timing convention. Source phases, readiness and the frame
clock never reset because of a key-position event.

An ordinary positive-velocity NoteOn always commands target 1, including when a
positive partial hold already makes `key_down` true. NoteOff and zero-velocity
NoteOn command target 0 through ordinary release travel. `AllNotesOff` remains
the separate immediate manual panic. A positive target can count as held before
any contact closes; a target-zero key can retain closed contacts while returning.
Use `contact_snapshot()` to inspect the actual position, target and nine bits.

The atlas explicitly separates measured gesture input from a named MIDI surrogate
and requires partial depression to preserve a contact subset (pp. 115-120,
especially p. 117). This event supplies an explicit normalized **target** to the
existing nominal trajectory. It is not a calibrated position sensor sample,
measured finger trajectory, velocity-to-motion curve or new physical model.
Sample-grid switching and all existing bandwidth/calibration limitations remain.

`KeyPosition` is direct physical-key input, independent of counted host note
ownership. [InputProcessor](INPUT_PROCESSOR.md) must remain the sole note authority
for keys assigned to its ownership object. Do not interleave uncoordinated direct
KeyPosition, NoteOn, NoteOff or manual panic commands with adapter-owned keys.
No ownership merge, authority-transfer operation or automatic adapter reset is
introduced here. Partial targets are transient dynamics and are excluded from
musical-control persistence along with positions, contacts, readiness and phases.

### Musical-control persistence

Control persistence moves to `B3CONTROLS2`, adding the following mandatory tokens
immediately after expression and before the existing ordered manual/bank blocks:

```text
B3CONTROLS2
expression <finite decimal in 0..1>
percussion enabled <0|1> harmonic <second|third> volume <normal|soft> decay <slow|fast>
manual upper selected <A|B> route_enabled <0|1>
bank A <nine positions>
bank B <nine positions>
manual lower selected <A|B> route_enabled <0|1>
bank A <nine positions>
bank B <nine positions>
end
```

Each bank retains nine single-digit positions 0-8. Whitespace remains token-based;
serialization emits canonical lines. Read `B3CONTROLS1` with the previous grammar
and migrate percussion to Off/Second/Normal/Slow. New serialization emits version
2; unsupported future versions and malformed/incomplete version-2 fields reject
atomically. Do not fill missing mandatory version-2 fields with defaults. Keep the
bounded 16 KiB input contract and immutable historical migration fixtures.

A snapshot stores musical controls, including all hidden banks and percussion
settings, not current notes/owners, contact positions, q, source phases or clock.
Successful control restoration changes routes/settings while preserving these
live histories. Failed restoration changes nothing. Serialization/parsing remains
outside processing; copied diagnostics require stopped or same-processing-thread
access. This is not a concurrent UI publication or exact DSP checkpoint format
(atlas pp. 389, 394, 401).

## Acceptance evidence to retain

Independent integration checks should establish the specified behavior with exact
source/model/build identities, not just compare two instances of the same new code:

- Legacy ideal mode with percussion disabled preserves the existing dry fixtures.
- All 122 keys expose nine distinct states; partial holds and hysteresis, interrupted
  release/repress and per-key threshold differences behave as declared.
- Keying remains active with a silent 1-foot drawbar; its mask does not alter stored
  controls; lower and upper-A sustain remain unaffected.
- Overlap, duplicate physical presses and zero-gap off/on do not reset q; increasing
  positive release gaps produce finite monotonic recovery under fixed settings.
- Second/third source routing, independent drawbar gain, upper-only normal
  compensation and fast/soft switches each have a separate oracle.
- Zero-frame flushes, disconnected output, Cancel/reselect and control restoration
  preserve the declared histories; invalid requests remain atomic.
- One absolute timeline gives the same state/audio for fixed and irregular block
  partitions at each supported rate, with appropriately timed cross-rate comparisons.
- The changed processing path has its own bounded-storage, allocation, sanitizer
  and observed runtime checks. Source inspection alone is not a deadline result.

Keep software behavior, numerical support, specimen correspondence and product
qualification separate. Current runnable interfaces and observed passes belong in
[STATUS.md](STATUS.md), with the next concrete task in [NEXT_STEPS.md](NEXT_STEPS.md).
