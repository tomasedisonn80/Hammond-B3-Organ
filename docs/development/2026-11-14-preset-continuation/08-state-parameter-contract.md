# A08 - State and parameter contract review

Actual worker: `/root/w02_a08_state_parameter_contract`, wave 2. Owned outputs:
this note and [PRESET_STATE_PARAMETER_CONTRACT.md](../../PRESET_STATE_PARAMETER_CONTRACT.md).
This assignment reviewed and specified the next implementation contract; it did
not edit production code, shared root documents, source data, Git history or
another worker's files, and did not spawn workers.

## Inspected source

Baseline commit: `b79086f6bb0c42b97130c721c5c73c7c97a13887`. Read the current
`AGENTS.md`, the complete root preset proposal, state format documentation,
`ControlStateIO.*`, `ParameterBridge.*`, `HostTimeline.*`, the StateExchange
payload, relevant controller methods, the registry validator and the saved-state
and conversion acceptance fixtures. The atlas source constraints supplied by
the six fresh readers were used; this assignment does not claim another complete
PDF reading.

| Inspected input | SHA-256 |
|---|---|
| `data/parameter-registry.json` | `a80b0f391a37dd9264dc6962131e61c6ba8a0b8ce570d15e89042abe13d148c4` |
| `data/registrations/atlas-chapel-nominal-v1.json` | `c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf` |
| `src/ControlStateIO.cpp` | `a1043d29d2321cccad4e994afbf62e16d93ce6cd15ce5c7593556daff1b0a8cf` |
| `src/ParameterBridge.cpp` | `14d7dcfd24f5e7d6d59de8b31999ee52b33c64f73df453bff82b9eaa4f89dce0` |
| `src/HostTimeline.cpp` | `37941dc9d833cabc1ed7ca22327ad23240ea8c04e6de9fc3f447222d2ebb41dd` |
| `src/StateExchange.cpp` | `10a85957cad8e87e00f8ada543f697b9db4d59590b306baaae05fc0120a2a2bf` |
| `tools/validate_parameters.py` | `c621746f0cbd8db31e7b8271122669fe22d6962e10dfa3f4576f2af0ddf21485` |

The complete old 45-record canonical digest was independently recomputed with
Python `json`, sorting by numeric ID and using `sort_keys=True`, compact comma/
colon separators and ASCII encoding. It is
`13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad`,
matching the integrator's independently supplied value. All old record fields,
not merely IDs, are included in that digest.

## Concrete decisions and findings

The companion contract specifies an exact **81-token, 12-line B3CONTROLS4**
grammar: one unconditional catalog ID/hash record, existing global controls,
and one explicit named fixed token per manual. `none` and C# through A map to
raw fixed values 0-9. Every older version migrates fixed mode to None from a
fresh candidate, retaining its previous percussion/pedal rules. Resaving always
uses version 4. Inactive/cancelled fixed selections and all banks survive; saving
only an effective Cancel/0 would lose information.

Confirmed integration hazards:

- The existing parser consumes pedal records only for `version == B3CONTROLS3`.
  Version 4 must be explicitly included, while missing new fields remain errors.
- Existing semantic snapshot comparisons enumerate old fields. They must add
  fixed modes or use a suitable full semantic comparison; old passing tests could
  otherwise hide a discarded new field.
- StateExchange's old 45-control encoding and comment require extension. The
  new two payload values must be **raw fixed modes**, not effective full selectors.
  The standalone publication encoding needs the same retained information.
- `HostTimeline` already emits explicit unchanged parameter points. Preserve
  this: repeated bank B must exit fixed mode. Its raw normalized curve anchors
  are separate from actual routing; no blanket post-callback recanonicalization
  may destroy legacy interpolation or fractional values.
- The VST3 controller caches raw accepted host values and receives restored
  state separately. Do not describe that cache as acknowledged applied routing.

## Independently checked numerical tables

Used Python's `fractions.Fraction`, `float.hex`, `math.nextafter` and `struct`
to derive all **11 midpoint thresholds** and **12 canonical k/11 values**.
For each of the 23 values, exact rational distance to the proposed binary64
value was checked against both adjacent binary64 values. The companion contract
retains all exact hexadecimal literals, equality policy and signed-zero rule.
This is a contract-level calculation, not an executed test of future C++ code.

The current Python integer-ratio half-up law disagrees with the newly proposed
rounded-threshold policy at **five** threshold values: 3/22, 5/22, 7/22, 15/22,
17/22. Their nearest binary64 values round downward, yet equality selects the
higher new key. The new kind therefore needs its own comparison-table branch;
all earlier converters and metadata remain unchanged. Runtime division by 11
under an arbitrary caller rounding mode likewise cannot implement the frozen
canonical encoder; use the exact table.

Coordinated directly with A07: its `control_preset_selection` helper checks the
whole snapshot, fixed labels match the grammar, and catalog ID/hash functions
return immutable program-lifetime strings. No dynamic catalog string is added
to `ControlSnapshot` or an audio callback payload.

## Result and handoff

The specification is ready for the integrator's explicit freeze and subsequent
implementation assignments. It provides the exact grammar, append-only records,
conversion constants, alias ordering, payload guidance and eight concrete
acceptance groups. No production build, native runtime or physical validation
was executed by A08, and this review does not claim those gates passed.
