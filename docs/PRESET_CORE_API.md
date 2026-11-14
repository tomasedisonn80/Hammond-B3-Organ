# Exclusive fixed-registration core API

Contract identity: **`exclusive-fixed-registration-core-v1`**. Assignment A07
fixes the API names and semantics below for the integrator's wave-2 freeze under
[PRESET_SELECTION_CONTRACT.md](PRESET_SELECTION_CONTRACT.md). This is an
implementation specification, not a claim that these APIs are already built or
qualified. The [A07 review](development/2026-11-14-preset-continuation/07-core-contract.md)
identifies inspected source and checks.

The source basis is atlas pp. 49-54, 121-138 and 151-156, freshly reconciled by
[A01](development/2026-11-14-preset-continuation/01-atlas-foundation.md),
[A02](development/2026-11-14-preset-continuation/02-atlas-console.md) and
[A03](development/2026-11-14-preset-continuation/03-atlas-scanner.md).
This implements the atlas's explicit normal-playing exclusive selection model.
It does not implement simultaneous physical latches, contact impedances or
measured loaded gains.

## 1. Header dependency and immutable data API

Create `include/hammond/FixedRegistration.h`. It includes `hammond/Types.h` and
the standard headers shown below; it must not include `ControlState.h`,
`Engine.h`, generated data, a host SDK or an application header. The generated
table is a private implementation dependency of `src/FixedRegistration.cpp`.
`ControlState.h` includes `FixedRegistration.h`, preserving an acyclic dependency.

```cpp
#pragma once
#include "hammond/Types.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace hammond {

inline constexpr std::size_t kFixedRegistrationCount = 9;
inline constexpr std::size_t kPresetSelectionCount = 12;
using FixedRegistrationPositions = std::array<std::uint8_t, kDrawbarCount>;

enum class FixedRegistration : std::uint8_t {
    None = 0, CSharp = 1, D = 2, DSharp = 3, E = 4,
    F = 5, FSharp = 6, G = 7, GSharp = 8, A = 9,
};

enum class PresetSelection : std::uint8_t {
    Cancel = 0, CSharp = 1, D = 2, DSharp = 3, E = 4,
    F = 5, FSharp = 6, G = 7, GSharp = 8, A = 9,
    BankA = 10, BankB = 11,
};

[[nodiscard]] constexpr bool is_valid_fixed_registration(
    FixedRegistration registration) noexcept {
    return static_cast<std::uint8_t>(registration) <= 9;
}
[[nodiscard]] constexpr bool is_valid_preset_selection(
    PresetSelection selection) noexcept {
    return static_cast<std::uint8_t>(selection) <= 11;
}

[[nodiscard]] bool fixed_registration_positions(
    Manual manual, FixedRegistration registration,
    FixedRegistrationPositions& destination) noexcept;

[[nodiscard]] std::string_view fixed_registration_catalog_id() noexcept;
[[nodiscard]] std::string_view fixed_registration_catalog_sha256() noexcept;
[[nodiscard]] std::string_view fixed_registration_label(
    FixedRegistration registration) noexcept;
[[nodiscard]] std::string_view preset_selection_label(
    PresetSelection selection) noexcept;

} // namespace hammond
```

`kFixedRegistrationCount` counts the nine rows **per manual**, excluding None.
`kPresetSelectionCount` counts all twelve reverse-key actions. Do not cast None
to Cancel to infer state: they are separate typed domains. Fixed A is value 9;
adjustable A# is `PresetSelection::BankA`, value 10, and refers to existing
`DrawbarBank::A`. Existing `DrawbarBank` values A=0 and B=1 do not change.

`fixed_registration_positions` accepts either valid manual and fixed values
1-9 only. None, invalid enum values and invalid manuals return false without
writing any destination element. A successful call copies exactly nine tap
indices in 0-8; it does not normalize amplitudes or expose a mutable table view.
No dynamic storage, file access, locks, initialization on first call or exceptions
are permitted. All table storage is immutable and exists for program lifetime.

Identity accessors return exactly:

| Accessor | Value |
|---|---|
| `fixed_registration_catalog_id()` | `atlas-chapel-nominal-v1` |
| `fixed_registration_catalog_sha256()` | `c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf` |

The SHA is the frozen authoring file's raw-byte identity, not a hash of a memory
layout, generated C++ file or selected row. The native data generator must first
admit the existing authoring and both frozen independent CSV readings through
the strict catalog compiler, then require the frozen identity before exposing
this model. Reformatting this frozen source cannot silently produce a different
saved-state identity under the same model. Preserve LF input bytes on every
build platform. A future changed matrix needs a separately reviewed model and
migration contract.

Label accessors return program-lifetime ASCII string views with no allocation:

| Numeric value | Fixed-registration label | Preset-selection label |
|---:|---|---|
| 0 | `none` | `C` |
| 1 | `C#` | `C#` |
| 2 | `D` | `D` |
| 3 | `D#` | `D#` |
| 4 | `E` | `E` |
| 5 | `F` | `F` |
| 6 | `F#` | `F#` |
| 7 | `G` | `G` |
| 8 | `G#` | `G#` |
| 9 | `A` | `A` |
| 10 | invalid: empty | `A#` |
| 11 | invalid: empty | `B` |
| Any other value | empty | empty |

An empty label never substitutes for validation. The UI adds division, Cancel,
fixed/adjustable and bank explanations around these short key labels. The atlas
does not provide historical voice names; do not invent them.

## 2. Snapshot and copied selection

Append this member after the existing `pedal_drawbars` in `ControlSnapshot`:

```cpp
std::array<FixedRegistration, kManualCount> fixed_registrations{
    FixedRegistration::None, FixedRegistration::None};
```

Keep all existing members, defaults, array order and `DrawbarPositions` aliases.
The new `FixedRegistrationPositions` alias has the same array element/count as
`DrawbarPositions` without moving that existing declaration. Do not store an
additional independently mutable `PresetSelection` field, pointer, catalog
string or runtime history in the snapshot. Defaulted equality must include the
new member. Full snapshot validation rejects fixed values outside 0-9 even
when a manual is cancelled. Hidden invalid controls are not ignored.

Add this free function **in `ControlState.h`**, after `ControlSnapshot` and its
validation declaration; implement it in `ControlState.cpp`:

```cpp
[[nodiscard]] bool control_preset_selection(
    const ControlSnapshot& snapshot, Manual manual,
    PresetSelection& destination) noexcept;
```

It validates the **complete snapshot** and the manual before writing destination.
Failure leaves destination unchanged. Success reports, in this order:

1. `Cancel` when `route_enabled[manual]` is false.
2. The fixed key when the enabled manual has a non-None fixed registration.
3. `BankA` or `BankB` from the retained bank otherwise.

The complete validation makes this helper safe for copied external state; do
not call it inside the per-key/per-drawbar mixing loop. The retained fixed mode
and bank remain available in the snapshot while the effective selection is
Cancel. That is intentional persistence, not multiple simultaneous routes.

## 3. ControlState additions and retained semantics

Add only these two public members to `ControlState`:

```cpp
[[nodiscard]] bool select_preset(
    Manual manual, PresetSelection selection) noexcept;
[[nodiscard]] bool selected_preset(
    Manual manual, PresetSelection& destination) const noexcept;
```

The member query uses the copied-state helper's effective-selection semantics.
The existing snapshot accessor is the retained fixed-mode diagnostic; no second
public retained-mode store or setter is needed. All methods retain the existing
same-thread/stopped-access contract and fixed-size, allocation-free behavior.

Validate manual and selection before changing any state. A true result includes
accepted no-op selections. The exact transition is:

| Operation | `selected_banks[m]` | `fixed_registrations[m]` | `route_enabled[m]` |
|---|---|---|---|
| `select_preset(m, Cancel)` or existing `cancel(m)` | preserve | preserve | false |
| `select_preset(m, fixed 1-9)` | preserve | selected fixed key | true |
| `select_preset(m, BankA)` or existing `select_bank(m, A)` | A | None | true |
| `select_preset(m, BankB)` or existing `select_bank(m, B)` | B | None | true |
| Existing explicit-bank drawbar edit | preserve | preserve | preserve |
| Existing selected-bank drawbar edit | preserve | preserve | preserve |

Every row preserves the other manual, all four bank values except an expressly
edited drawbar, expression, percussion settings and both pedal positions.
`set_drawbar` continues to edit the **remembered bank**, including while a fixed
row sounds or the route is cancelled. It must not rewrite a fixed row, select a
bank or reconnect the route. `selected_bank` and `drawbar_position` keep that
remembered-bank meaning. UI edited-bank state remains a separate UI-owned value.

Update `active_drawbar_position` without changing its signature. After valid
manual/index admission it returns zero when cancelled; otherwise it returns the
selected fixed row's position when present, or the selected retained bank's
position. Invalid input preserves destination. Resolve a fixed row with the
checked immutable lookup. None is handled as bank mode before row lookup.

`restore` continues to validate the complete candidate before installing it.
It neither infers a fixed row from matching bank values nor clears a fixed mode
because one bank happens to have equal positions. These represent different
musical controls despite possible equal audio.

## 4. Event and Engine integration

Append `SelectPreset = 14` to `EventType`. Do not renumber entries 0-13 or change
the `Event` layout. Its shape is:

```cpp
Event{offset, EventType::SelectPreset, manual, 0,
      static_cast<double>(static_cast<std::uint8_t>(selection))}
```

Both manuals are valid; index must be exactly 0; value must be finite, integral
and in 0-11. A signed negative zero is an admitted numeric zero, as for existing
integer controls, and means Cancel. Reject fractions, nonfinite values, other
indices, invalid manuals and all other values before applying any event in the
request. Positive calls retain half-open offset bounds and stable equal-offset
input order. Zero-frame calls require offset zero.

Add this checked diagnostic to `Engine`:

```cpp
[[nodiscard]] bool selected_preset(
    Manual manual, PresetSelection& destination) const noexcept;
```

It returns false without modifying destination before preparation or for invalid
manuals; otherwise it delegates to `ControlState`. It reads current controls,
not the possibly dirty coefficient cache. No direct Engine mutator is added:
processing events and the existing validated whole-control restore remain the
mutation boundaries.

The new event dispatches to `ControlState::select_preset` and dirties routing
coefficients when the route/mode/bank changes. The existing SelectBank handler's
no-op condition must additionally inspect fixed mode: remembered bank B plus an
enabled fixed route is **not** a no-op when B is selected. Either compare the
effective selection against the desired bank or extend the old guard with
`fixed_registrations[m] != FixedRegistration::None` before calling `select_bank`.

At coefficient rebuild, resolve the selected nine-position vector once per
enabled manual, before its key/drawbar loop. Keep all existing iteration order,
coherent tone accumulation, profile gain lookups, pedal path and final arithmetic.
The bank-mode vector is exactly the previous bank array; the fixed-mode vector
contains documentary tap indices used with the same nominal gain law. This
preserves legacy dry PCM when both fixed modes are None.

All selections preserve held-key targets/owners, contact travel and hysteresis,
pedal state, shared source phases, source/profile identity, readiness and clock.
No selection calls prepare, panic, reset, note-on or note-off. Cancel only
disconnects one manual route; ordinary source/contact/readiness evolution still
occurs during subsequent rendered samples, including disconnected output.
Zero-frame selection changes controls and diagnostics but advances none of
those histories. Whole-call rejection preserves caller output and future audio,
not just the visible snapshot.

## 5. One eligibility rule, both observable paths

Use the same rule in coefficient rebuilding and `percussion_diagnostics()`:

```cpp
controls.percussion.enabled && controls.route_enabled[0] &&
controls.fixed_registrations[0] == FixedRegistration::None &&
controls.selected_banks[0] == DrawbarBank::B
```

A small private predicate in `Engine.cpp` may share this rule; no additional
public predicate is required. The copied diagnostic must derive it afresh after
zero-frame events/restores, because coefficient rebuilding can be deferred.
Lower fixed selection cannot enable, disable or reset upper percussion.

An upper fixed route receives neither the upper-B 1-foot sustain mask nor its
percussion-related sustain compensation, even if bank B remains remembered and
the percussion tablet is On. Preserve `PercussionState`'s existing nominal law:
readiness recovers during an ineligible fixed interval by actual elapsed samples
and is consumed on returning to B without reset. Equal-offset B/fixed/B or a
zero-frame sequence adds no elapsed recovery. This software policy does not
claim the unacquired physical held-key transition of atlas p. 249.

## 6. Adapter and persistence obligations

The state/parameter contract owns the exact new grammar and conversion law.
It consumes `control_preset_selection` for the effective parameter value while
serializing both retained fixed values independently. Old state versions migrate
both fields to None; no old parameter ID is reused. UI Cancel status does not
make C visually latched, and reverse preset keys never become note owners.

Implementation must update all explicit event/control allowlists, including
`PerformanceInput` and standalone Session, plus the corresponding parameter
metadata, host anchor extraction and native controller snapshot conversion.
Both atomic snapshot encodings must copy the two retained enum values, including
cancelled states. These are integration obligations, not permission for this
contract author to edit separately owned modules.

## 7. Acceptance required before engineering completion

| Independent check | Required observation |
|---|---|
| Every one of 18 literal rows | Correct key/manual lookup and nine unchanged digits; invalid/None lookup preserves destination. |
| Snapshot and selection domain | All 0-9 retained fixed modes valid, invalid hidden modes rejected; 12 effective selections unambiguous; fixed A differs from bank A#. |
| Equivalent-bank audio | All fixed rows match an independent bank-A reference with percussion disabled at matched continuously running phase, including held/folded chords. |
| Legacy behavior | Both modes None preserve existing outputs and event/state behavior; all old parameters retain exact identity. |
| Retained editing | Editing either inactive bank changes only its stored value, leaves fixed PCM unchanged and becomes audible on a later explicit bank selection. |
| Stale remembered bank | B -> fixed -> existing SelectBank B exits fixed mode despite the retained bank already being B. |
| Percussion | Both diagnostics and audio exclude every fixed row; held B/fixed/B recovers only by elapsed samples; lower changes leave upper history unchanged. |
| Cancellation | Cancel preserves fixed memory, bank values, notes, partial contacts, phase and pedals, and only mutes the selected manual. |
| Temporal boundaries | Stable equal-offset order, zero-frame no-time behavior and matching absolute timelines across block partitions and supported rates. |
| Failure continuation | Invalid selector after an otherwise valid event rejects the entire call; complete output/state and later audio match an untouched control engine. |
| Restore and thread publication | Every retained mode survives new-format, queue and atomic snapshot round trips; legacy migrations clear it; no transient histories enter saved controls. |
| Callback constraints | Measured affected-path allocation/lifetime acceptance and coherent source builds. |

Contract approval fixes semantics; only executed independent acceptance can
qualify the implementation. Physical source wiring, loaded gains, simultaneous
latches, scanner/AO-28/Leslie integration and a literal UI match retain their
separate gates.
