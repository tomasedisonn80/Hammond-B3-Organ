# A07 - Independent core/API contract review

Assignment: `/root/w02_a07_core_contract`, wave 2. Owned deliverables are this
report and [PRESET_CORE_API.md](../../PRESET_CORE_API.md) only. The integrator
retains the shared proposal, production ownership and overall freeze decision.
No production source, tests, source data, other worker's files or Git state was
changed. No subagents were dispatched by this assignment.

## Inspected inputs and actual checks

Read `AGENTS.md`, the complete root selection proposal, existing `Types.h`,
`ControlState.h/.cpp`, `Engine.h` and the relevant complete Engine validation,
event dispatch, coefficient rebuild, restore and diagnostic functions. Reviewed
`PerformanceInput.h/.cpp` to identify the additional explicit control allowlist.
Reviewed the current chapel catalog contract and all eighteen rows in authoring
JSON and both retained CSV readings. The fresh A01-A03 reading records supply
the relevant atlas source interpretation; this assignment does not claim a
seventh complete atlas reading or new factory-source acquisition.

The parent identifies the starting revision as
`b79086f6bb0c42b97130c721c5c73c7c97a13887`. Independent file hashes identify the
actual source inspected here without assuming the entire live worktree is a
frozen build:

| Input | SHA-256 |
|---|---|
| `include/hammond/Types.h` | `c533cc0b59838e22aff1dd081e30482df76c747407ea76d4b1788e0536a3ef7b` |
| `include/hammond/ControlState.h` | `2fb1b7b7fc39363f7e53eb81e2edf3ddb88944b4aa20969b92a90f5c584b2edb` |
| `src/ControlState.cpp` | `d297545788fa62b0167fc0a9c07081b1f8af79bd1252ceb66d0d1326dd214e58` |
| `include/hammond/Engine.h` | `b2aea1dae1e54654cacb8576295b27d47673c87a9a01e17fd3eba7a843fa188c` |
| `src/Engine.cpp` | `e082d07323c506f58c726c76a8459bbbec9b01fcb7b20ca6d6323c065fa6664c` |
| Root proposal as reviewed | `068972efd37e87d6bb22d825b5bc8a0e715f863695f18be774d4bcfd3f7b24cd` |
| `data/registrations/atlas-chapel-nominal-v1.json` | `c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf` |
| Each independent chapel CSV | `dc2a8fd4e9750133c982bb42fd6cc7c12908f011154826035bb623f52d8de694` |

Executed a Python standard-library comparison of `(manual, preset_key, drawbars,
page)` in authoring order against each CSV. **All 18 rows and all 162 positions
agree.** This checks retained data consistency; it does not establish independent
factory Table IV provenance or physical gain. Read commands and hashing were
read-only; no production build or runtime test was appropriate for this
documentation-only assignment.

## Result of independent review

The proposed fixed/remembered-bank/route decomposition is sound for the declared
exclusive normal-mode scope. It avoids redundant selectors, preserves legacy
Drawbar semantics, admits Cancel while retaining a fixed choice, and makes old
states migrate naturally to None. The API contract resolves the previously
unspecified names, header placement, domain validation and label behavior:

- `FixedRegistration.h` depends only on `Types.h` and standard headers. Its
  `FixedRegistrationPositions` alias avoids importing `ControlState.h` and a
  circular dependency. Generated constants remain private to its `.cpp`.
- `fixed_registration_positions` returns a checked value copy, rejects None
  as a row, and leaves the entire output untouched on failure. It never returns
  a mutable reference to the catalog.
- `fixed_registration_catalog_id()` and
  `fixed_registration_catalog_sha256()` expose fixed program-lifetime identities.
  Short label functions distinguish retained `none`, momentary `C`, fixed `A`
  and adjustable `A#` without inventing voice names.
- `control_preset_selection(const ControlSnapshot&, Manual, PresetSelection&)`
  validates the complete copied state and provides the common UI/host meaning.
  `ControlState::selected_preset` and `Engine::selected_preset` use that meaning;
  the latter also requires preparation.
- `ControlState::select_preset` is the only new public mutator. The existing
  snapshot exposes retained fixed identity; no additional store or direct
  Engine setter is required.

A08 was informed of those exact names and the `none`/C#/A# spellings. Its proposed
state4 grammar matches this API. State parsing/conversion remains separately
owned; this review does not silently freeze its full grammar or normalized law.

## Concrete implementation hazards and resolutions

1. **Remembered B is insufficient for percussion eligibility.** Both
   `rebuild_coefficients` and `percussion_diagnostics` currently use only the
   route and bank. Add fixed-None to the same rule at both sites, preferably
   through one private predicate. Diagnostics must remain correct immediately
   after zero-frame events, before any deferred cache rebuild.
2. **Existing SelectBank can swallow a valid fixed-to-bank change.** Its old
   guard sees remembered B/enabled and skips the operation. Extend that guard
   to fixed mode or compare effective selection; `select_bank` itself always
   clears fixed mode before enabling the chosen bank.
3. **Active and editable positions have different meanings.** Existing
   `set_drawbar` and `drawbar_position` retain remembered-bank behavior even
   during fixed sound. Only active routing resolves fixed positions. Copying
   a row into a bank would violate the source and is excluded.
4. **Do not mutate note or DSP history.** The event is an admitted routing
   change. Fixed selection/Cancel never invoke prepare, panic, note events or
   percussion reset. Existing continuous readiness recovery is preserved and
   remains explicitly nominal.
5. **Keep old arithmetic order.** Resolve one position vector per enabled
   manual before the existing loop; preserve tone accumulation/gain operations.
   None must take the previous retained-bank values, enabling exact legacy PCM
   comparison rather than a broad tolerance that could hide changed behavior.
6. **Validate hidden fields and whole requests.** Cancel cannot hide an invalid
   fixed enum. Selection admission joins Engine preflight before mutation, and
   no invalid late event can partially apply an earlier valid selection.
7. **Update bounded adapters together.** PerformanceInput and Session control
   allowlists, host anchors/controller snapshots and both atomic encodings must
   carry the new fields/action. Those updates are separately assigned work;
   merely extending the core enum is not completion.

## Handoff and acceptance boundary

The API document contains an implementable header surface, exact transition and
label tables, event value 14, Engine integration steps, and twelve independent
acceptance categories. A13/data and A14/core can implement without changing these
names, while the state/parameter/adapter workers consume the copied-state helper.
The integrator should freeze the combined contract before those edits and build
all consumers from coherent source after the snapshot layout changes.

**Completed here:** independent source/API review, literal retained-table
consistency check, a precise core contract and coordination with A08.
**Not executed here:** C++ compilation, audio equivalence, allocation, thread,
native/UI or platform acceptance. No new physical or pixel-equality claim is
made. Their required evidence remains in the core contract and session scope.
