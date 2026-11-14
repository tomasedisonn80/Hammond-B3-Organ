# Exclusive fixed-registration continuation

Frozen contract: **`exclusive-fixed-registration-v1`**, accepted by the integrator
on 2026-11-14 after independent A07/A08/A09 review and A10 source-oracle admission.
The precise [core API](PRESET_CORE_API.md),
[state/parameter grammar](PRESET_STATE_PARAMETER_CONTRACT.md) and
[native UI design](PRESET_UI_DESIGN.md) complete this contract. Implementation
and executed acceptance remain separate. The source is the unchanged atlas, especially pp. 49-54,
121-138, 151-156 and 397-402. The new session begins at `b79086f`.

## Scope and identity

Advance the explicitly named next M3 slice: select the eighteen documentary
chapel registrations without overwriting either manual's retained A/B banks.
Expose the selector as two new ordinary parameters, not host programs. Integrate
the actual controls into the native instrument and retain the complete previous
dry-model arithmetic whenever fixed registration is unused. The physical
multi-latch/contact/loading model and measured gains remain separate work.

The frozen table remains `atlas-chapel-nominal-v1`, originating in atlas p. 122.
Its authoring file SHA-256 is
`c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf`.
Both existing independent CSV readings remain required build inputs. Generate
bounded native data only after the existing strict compiler has admitted all
eighteen rows, identities and limitations. No JSON, file access, allocation,
locking, host SDK or source-data parsing enters audio processing. Do not rename
registrations: the source does not publish historical voice names.

## Typed control model

Add `FixedRegistration.h` and its implementation with:

- `enum class FixedRegistration : std::uint8_t` with `None=0`, `CSharp=1`,
  `D=2`, `DSharp=3`, `E=4`, `F=5`, `FSharp=6`, `G=7`, `GSharp=8`, `A=9`.
- `enum class PresetSelection : std::uint8_t` with `Cancel=0`, the same fixed
  values 1-9, `BankA=10`, `BankB=11`. Fixed key A and adjustable A# / bank A
  are different identities.
- Checked allocation-free lookup of a fixed registration's nine positions for
  either manual, program-lifetime catalog ID/hash and display labels. Invalid
  manual/registration preserves the destination, including `None` for a row
  lookup. `None` is a valid retained mode but has no fixed row.

Append `fixed_registrations[2]`, default `None`, to `ControlSnapshot`; preserve
`selected_banks`, `route_enabled`, all four bank arrays and every existing field.
The retained bank is the legacy edit target, even while a fixed row sounds.
Snapshot validation admits only 0-9, including a retained fixed choice while
cancelled. No redundant independently editable full-selector field is stored.

| Action | Retained bank | Fixed mode | Route | Other state |
|---|---|---|---|---|
| Select a fixed key 1-9 | Preserve | Set selected row | Enable | Preserve |
| Existing or new bank A/B selection | Select bank | Clear to None | Enable | Preserve |
| Existing Cancel or new selection 0 | Preserve | Preserve | Disable | Preserve |
| Edit an A/B drawbar | Existing target semantics | Preserve | Preserve | Preserve |

The effective public selector is Cancel when disabled; otherwise its fixed row
when present; otherwise bank A/B. Cancel is a command and must return visually
to rest: show the cancelled route as status without a persistently depressed C
key. A fixed selector release does not release notes or clear the selection.

Add `ControlState::select_preset(Manual, PresetSelection)`, checked effective
selection queries for copied snapshots/control state, and a corresponding Engine
diagnostic as needed. Keep `drawbar_position`'s legacy retained-bank meaning;
`active_drawbar_position` resolves the fixed row or selected bank and returns zero
while cancelled. Existing `select_bank` must clear fixed mode even when the
remembered bank and route were already unchanged.

Append `EventType::SelectPreset = 14`; manual Upper/Lower, index exactly 0,
finite integral value 0-11. Preserve every earlier EventType value. Preflight the
entire request before any mutation, including zero-frame calls. Direct events
at the same offset retain input order. A selection consumes no elapsed time,
never reseeds sources, releases owners/contacts, changes pedals/expression or
resets percussion readiness. Invalid requests preserve output and future state.

## Percussion and audio

Eligibility requires enabled percussion, enabled upper route, no fixed mode and
retained upper bank B. Apply this rule to both mixing and copied diagnostics.
Fixed presets use all their documented tap positions without upper-B masking or
compensation. Lower selection cannot change upper percussion.

Preserve the existing nominal readiness law: when the routed detector is absent,
readiness recovers according to elapsed rendered samples. A held B-to-fixed-to-B
transition consumes the current readiness; a zero-duration sequence creates no
recovery. No new physical circuit or measured switching claim is made.

## Parameters and host ordering

Retain all 45 existing descriptor records, IDs, defaults, units and conversions.
Append IDs **20480** (`manual.upper.preset_selection`) and **20481**
(`manual.lower.preset_selection`), kind `preset_selector`, plain 0-11, default
11, eleven steps, target `SelectPreset` on the corresponding manual. Registry
schema becomes 4, model `exclusive-fixed-percussion-pedal-console-v4`, count 47.

New selector normalization uses midpoint bins: each adjacent threshold is the
nearest binary64 value of `(2*k+1)/22`, k=0..10; equality selects the higher key.
Freeze literal binary64 thresholds and use comparison so caller rounding mode
cannot move a boundary. Plain-to-normalized maps each integer k to the canonical
nearest binary64 k/11; the old 0/1/8-step paths remain bit-identical. Test exact
thresholds and both adjacent representable values under all supported rounding
modes. Reject nonfinite, fractional plain, out-of-range and unknown IDs without
changing the destination.

Preserve the existing host timeline's established order. Where old bank and new
selector automation occur at the same sample, descriptor/ID order applies: the
new higher-ID selector is applied after the old bank parameter. Direct core and
standalone command order remain stable input order. Tests must make this
interaction explicit; controller display/restored anchors must derive the new
selector from actual controls and preserve the legacy bank value.

## Saved controls

Write canonical **B3CONTROLS4**. Preserve old B3CONTROLS1/2/3 readers and fixtures.
Older formats migrate both fixed modes to None, independent of the destination;
all their bank/Cancel/percussion/pedal migrations retain their meaning.

Version 4 includes the exact fixed catalog ID and authoring hash, plus each
manual's retained fixed mode alongside its existing selected bank and route bit.
The exact record spelling is frozen in
[PRESET_STATE_PARAMETER_CONTRACT.md](PRESET_STATE_PARAMETER_CONTRACT.md). Unknown/mismatched catalogs, missing/duplicate/extra records,
invalid enums and oversized/truncated input reject transactionally. There is no
silent fallback or substituted newer matrix. Keep the 16 KiB maximum.

Only musical controls are saved: no owners, keys, contacts, phase, readiness,
clock, devices or UI focus. Cold load creates no held notes; existing live-load
semantics preserve current histories. Update both atomic publication encodings,
host anchors, standalone snapshots, controller normalization and state tests so
the new fields cannot be lost across thread boundaries.

## UI and source truth

Use the atlas's original cover/page-409 artwork as visual direction. Preserve
correct playing-key counts, footage, controls and all live state. Add an explicit
fixed-preset selection surface per manual; show actual applied selection and
distinct edited bank, with keyboard and pointer operation at minimum/default/
reference sizes. Selection does not invoke ordinary note ownership. Keep focus,
pending/rejected commands and Cancel distinct from sounding keys.

Improve reference material/depth and proportions through actual native drawing.
Retain actual application captures at 960x700, 1280x900 and 1672x941 and compare
them with the exact source. Correct source-image legends remain intentional
differences. Update the README with verified current screenshots; source art
must never be presented as a running application or literal 1:1 qualification.

## Required evidence and continuation

Independently compare all eighteen literal rows to equivalent continuously
running banks; include held chords/foldback, inactive edits, Cancel, pedals,
upper-B readiness, partial contacts, equal-offset ordering, block partitions,
all supported rates, invalid-call rollback and zero-frame changes. Exercise
new parameters and all old state migrations through core, host, standalone
publication and native controls. Measure callback allocation on affected paths.

Retain coherent source identities, exact commands, real results and original
failures. Update status, next steps, plan, affected format/build/runbook documents,
development log, README and AGENTS guidance. Commit and push completed authorized
work to main with remote-advance inspection and no force. Inspect hosted gates
for the published source. Worker accounting uses only this session's actual
sixty assignments, not prior sessions or planned entries.
