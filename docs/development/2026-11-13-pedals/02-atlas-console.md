Owner: /root/w01_a02_atlas_console

# Assignment 02: complete atlas pages 85-168 and pedal design review

Wave: 1. Assignment: 02 of the new sixty-assignment pedal continuation.
Scope: read every assigned page, inspect the pedal illustrations, compare the
current implementation boundaries, and recommend the next nominal pedal model.
This note is a documentary/design review with the limited executed data checks
listed below. It does not implement or qualify pedal audio.

## Coverage and source identity

I read all **84 pages, PDF/printed pages 85-168**, including each chapter's
evidence, equations, implementation proposal, acquisition plan and acceptance
section. The extracted text was read in complete ranges 85-91, 92-98, 99-108,
109-120, 121-132, 133-144, 145-156 and 157-168. An initially combined tool output
was truncated; the affected 85-98 text was subsequently read again in smaller
untruncated ranges. No coverage claim relies on that truncated output.

Source: [preserved research atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`,
confirmed locally. I rendered and visually inspected **all six pages 139-144**
using Poppler at a 1600-pixel maximum dimension. The visible page-140 boundary
rows, page-141 matrix visualization and page-142 transfer/units description agree
with the extracted text. The patent plate on page 140 remains a historical
embodiment; I did not treat its miniature circuit as a production B-3 netlist.
This is not a fresh independent transcription of the underlying service manual.

The pages cover the following complete chapters:

| Pages | Chapter | Development requirement |
| --- | --- | --- |
| 85-90 | 013, mechanical modulation | Preserve shared phase and distinguish angular, gap, hum, scanner and rotary mechanisms. Source nominal rates do not establish modulation amplitudes. |
| 91-96 | 014, calibration data | Separate observations, profiles, compiled banks and runtime history. Declare source voltage boundary; keep unknowns explicit and reject malformed data before publication. |
| 97-102 | 015, manual mapping | Keep key, source, physical terminal and MIDI identities separate. Preserve repeated-source branches and repeated upper octave folding. Pedal routing is distinct. |
| 103-108 | 016, shared oscillator implementation | Evaluate one 91-source frame per sample; preserve phase through silence, notes, rate changes and zero-frame calls. Bound callback work and validate against a scalar oracle. |
| 109-114 | 017, drawbars and bus mixing | Nominal 3 dB gains are a proposed reference, not measured transformer taps. Keep branch identity until loading is resolved and avoid polyphony normalization. |
| 115-120 | 018, contacts and click | Preserve nine individual manual contacts and phase-dependent switching. Make/break histories, gesture, click and percussion are separate. Switching precedes bandwidth reduction. |
| 121-126 | 019, presets | Cancel changes routing, preserves held keys and phases, and leaves pedals independent. Four banks retain their positions; physical multi-latch behavior needs a network model. |
| 127-132 | 020, percussion trigger | One shared upper-B detector/history; lower and pedal keys never enter it. Ownership and same-timestamp ordering must not invent recharge time. |
| 133-138 | 021, percussion circuit | Borrow existing generator signals. Separate sustained return, upper attenuation, gain and capacitor history. Nominal RC products are not audible decay calibration. |
| 139-144 | 022, pedal map and shaping | Preserve 25-by-8 topology, four buses, two drawbars, shared sources and lower-path identity. Physical transfer, spectra and contact parameters remain unmeasured. |
| 145-150 | 023, expression | Model common preamplifier expression separately from a final monitor gain. A scalar is a named surrogate; all divisions must traverse the common path once. |
| 151-156 | 024, console/MIDI state | Separate controls, owners and DSP history. Retain original destinations for releases; ordinary state recall cannot restore held notes or claim deterministic checkpoint behavior. |
| 157-162 | 025, scanner line | Freeze a revision-specific 18-inductor/18-capacitor/19-output graph and signed references; compare independently solved loaded responses. |
| 163-168 | 026, scanner rotor | Distinguish 16 plate positions, nine terminals and 19 ladder outputs. Capacitive coupling is not metallic contact switching; preserve rotor history. |

## Current repository boundaries inspected

I read `AGENTS.md`, `docs/M3_NEXT_GATE.md`, `docs/PEDAL_ROUTING.md`,
`docs/research/ERRATA.md`, `include/hammond/Types.h`, `Engine.h`,
`ControlState.h`, `NoteOwnership.h`, and `src/Engine.cpp`. I inspected the map,
both retained pedal CSV transcriptions and the nominal profile's gain records.
The inspected baseline is the new session's starting code at `b4fc61c`.

The present Engine evaluates one `TonewheelBank::process_frame` call in its
sample loop and combines manual/percussion audio before the common
`profile_.output_gain * controls_.expression()` factor. It has no pedal audio
consumer. Its `Manual` enum has only Upper and Lower, and its existing event
values 0-9 have established meanings. `NoteOwnership` has two manual-only buses
and retains original destinations. These boundaries should be extended with
explicit pedal identity; adding a third value to `Manual` would alter assumptions
throughout the current code.

The existing source profile's output multiplier is 0.03, explicitly proposed
software headroom. It already permits clipping under dense material. A pedal
integration must report clipping honestly and must not silently alter that gain
or normalize by the count of held notes to make a maximum-occupancy test pass.

## Required pedal implementation contract

1. **A shared source frame.** Consume the existing 91 values once per rendered
   sample. A pedal edge cannot create, reseed, reset or advance a second source
   bank. Keep the same behavior with no output buffer, both drawbars muted, and
   after a rate change (pp. 103-108, 139, 141).
2. **All physical positions.** Store 200 contact states, including the five
   electrically absent positions. For pedals 1-7, columns 1 and 2 in zero-based
   indexing select the same source but belong to distinct Brown and Red branches.
   Pedals 8-12 have an absent column 1. Preserve the 7/8 and 12/13 boundaries;
   absence is tagged, never encoded as an audible source-zero workaround
   (pp. 140, 144).
3. **Four fixed buses.** Contact columns 0/1 feed Brown, 2/3 Red, 4/5 Orange,
   and 6/7 Yellow. The membership supplies no conductance or calibrated gain.
   Keep source identity, contact state, weight and bus destination independently
   inspectable (pp. 140-142).
4. **A routing kernel before a voice.** The first accepted checkpoint should be
   the existing next-gate proposal `linear-pedal-bus-reference-v1`: fixed
   storage, explicit dimensionless reference weights, finite bounded inputs,
   transactional preparation/edits and a four-output scalar sum. Its linear
   oracle is explicitly allowed by p. 144. Do not call that routing result a
   calibrated pedal timbre.
5. **An explicit output transfer.** A later playable reference needs an identified
   four-input/two-output transform and two retained controls. The atlas provides
   no numerical transfer matrix or physical gain law. An original proposal can
   be useful if its coefficients, law, units, identity, limitations and replacement
   boundary accompany it. Actual electrical coupling remains pending (p. 142).
6. **Division independence.** Retain a separate pedal contribution associated
   with the lower/Great path before common expression. Lower Cancel must leave
   held pedals audible; upper percussion eligibility, ninth-contact detector,
   one-foot mask and readiness must ignore pedal state. Manual panic must not
   become pedal panic accidentally (pp. 121, 127-132, 139, 150).
7. **State and input compatibility.** Append event/control identities, retain
   existing meanings, and define the adapter's pedal range as an explicit software
   policy. The map does not establish a MIDI octave convention. Old saved
   controls should migrate to two muted pedal controls. Live restore preserves
   pedal ownership/contact state and source history; fresh construction starts
   with no held pedals (pp. 151-156).
8. **Scope of contacts.** All-eight ideal closure is a valid declared first
   playing policy over independent binary branches. The manual's 8/12 ms travel
   constants are not evidence of pedal travel. Do not introduce unmeasured pedal
   attack/release envelopes or a monophonic bass policy as historical behavior
   (pp. 139, 142-144).

## Concrete nominal mixture recommendation

The following is an **original engineering proposal for later integration**,
not an implementation, atlas value, measured transfer or selected final design.
It gives reviewers a bounded, reproducible reference while preserving four-bus
visibility. Root may choose different coefficients if the adopted contract
states them equally clearly.

Use identity `nominal-static-pedal-mixture-v1`. Let the ordered input be
`b = [Brown, Red, Orange, Yellow]`, with dimensionless source-normalized units.
Return two separate dimensionless mixture outputs `z = A*b`:

| Output | Brown | Red | Orange | Yellow |
| --- | ---: | ---: | ---: | ---: |
| Mixture 0 | 1/2 | 1/4 | 1/8 | 1/8 |
| Mixture 1 | 1/8 | 1/2 | 1/4 | 1/8 |

These nonnegative binary-exact rational coefficients were chosen for a transparent
test oracle: each row sums to one, both outputs retain all four bus inputs, and
the two registrations differ. They are not reconstructed reactor responses or
claims of exact 16-foot/8-foot acoustic voicing. Avoid presenting those footage
labels as validated by this matrix.

For this specific proposal, use a separately named `linear-pedal-position-v1`
law `g(p)=p/8`, for integer markings 0-8, and let
`pedal = g(p0)*z0 + g(p1)*z1`. Both default positions are zero. This is deliberately
specified instead of silently copying the manual profile's 3 dB table. An explicit
alternative gain table is also possible; whichever is adopted needs its own
identity and tests. The separable controls are a declared limitation of this
static reference, not an assertion that the real loaded drawbars are independent.

With bounded bus excitations of absolute value at most 50, each mixture is bounded
by 50 and their unscaled sum by 100. That is a mathematical bound, not calibrated
voltage or a promise of unclipped PCM after the common 0.03 gain. A future coupled
loaded model should replace this module at the same four-bus/control interface;
it must carry reactive history, source-loading interaction, load and voltage
references rather than pretending this static matrix already represents them.

Useful independent tests include unit-bus impulses, all 81 drawbar combinations,
the two endpoints, invalid/nonfinite coefficients, preservation of destination on
rejection, separate duplicate branches, and exact binary-rational arithmetic.
PCM tests should compare pedal-only plus manual-only with a simultaneous render
from the same initial state using a declared float-rounding bound; three unrelated
unsynchronized renders are not a phase oracle.

## Critical pitfalls for subsequent phases

- Page 92's Table V readings are service measurements at preamp G-G, not raw
  source amplitudes. Do not use them to calibrate the nominal pedal source bank.
- Page 141 separates intrinsic low-wheel harmonics (multiples of that wheel's
  phase) from borrowed sources (their own gearing and phase). A sine-only source
  bank is a reduced model; a rich-waveform extension needs a bandwidth policy.
- Pages 145-150 describe a loaded capacitive expression network. Applying a
  future AO-28 expression response and the current scalar without an explicit
  boundary policy can attenuate or color the pedal contribution twice.
- Page 166's printed purported sixteen-entry scanner traversal has **fifteen**
  entries. Existing erratum E01 correctly preserves this discrepancy and the
  inferred trailing index 1. Do not copy the printed array into a sixteen-index
  runtime loop. The inference still needs the stated independent documentary
  confirmation before M4 acceptance.
- Page 143's 475 pedal/control capture states are a proposed acquisition plan:
  25 times 17 axis states gives 425, plus 25 times two paired states gives 50.
  The atlas does not supply those recordings or fitted physical coefficients.

## Executed checks and results

The following actual commands/operations were executed for this assignment:

```sh
pdftoppm -f 139 -l 144 -scale-to 1600 -png \
  Hammond_B3_Leslie_Research_Atlas_500pp.pdf \
  /workspace/scratch/f364bc93d920/atlas-review/a02/pedal
python3 tools/validate_pedal_map.py --input data/pedal-map.json
python3 tests/test_pedal_map.py -v
```

The validator reported **25 pedals, 200 positions, 195 connected and five
disconnected**. All **15** existing pedal-map Python methods passed in the
observed run, with no skips. Separate Python `csv.DictReader` comparisons checked
each native source JSON row against **both** retained CSVs: all 200 positions
matched in each comparison, including all five blanks. This checks documentary
consistency with the retained independent readings; it does not re-establish
the original reviewers' independence or verify an actual specimen.

The raw map SHA-256 was confirmed as
`58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd`.
The two retained CSV files were observed byte-identical, consistent with their
matching transcriptions. No source/code, map, PDF, shared status or historical
ledger was modified by this assignment. No pedal kernel, render, allocation,
cross-platform, host or physical-fidelity test was run here.

## Handoff

Proceed with the prepared routing kernel and independent CSV/native acceptance
from [the existing next gate](../../M3_NEXT_GATE.md). Freeze its API and evidence
identity before assigning the playable transfer, controls, events or input
ownership changes. The root integrator owns the chosen nominal coefficients,
shared status records, source freeze, regression qualification and publication.
Physical contacts, source spectra, reactor/loading and specimen agreement remain
separate acquisition and validation work after the software routing gate.
