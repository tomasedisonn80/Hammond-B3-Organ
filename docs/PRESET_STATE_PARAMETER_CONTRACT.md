# Fixed-registration state and parameter contract

Contract identity: **`fixed-registration-state-parameters-v1`**. A08 independently
reviewed this specification against `b79086f` and the
[continuation proposal](PRESET_SELECTION_CONTRACT.md). These are the exact
decisions recommended for the integrator's wave-2 freeze; implementation and
executed acceptance remain separate. The [A08 record](development/2026-11-14-preset-continuation/08-state-parameter-contract.md)
identifies the inspected source and checks.

## 1. Canonical B3CONTROLS4

The public I/O function signatures and 16,384-byte input/output limit remain
unchanged. Every successful new serialization writes version 4, even when no
fixed registration is selected. There is no implicit downgrade writer.

Names are case-sensitive. The exact ordered grammar is:

```text
B3CONTROLS4
registration_catalog atlas-chapel-nominal-v1 sha256 c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf
expression <expression>
percussion enabled <0|1> harmonic <second|third> volume <normal|soft> decay <slow|fast>
pedal drawbars <p0> <p1>
manual upper selected <A|B> fixed_registration <fixed> route_enabled <0|1>
bank A <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
bank B <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
manual lower selected <A|B> fixed_registration <fixed> route_enabled <0|1>
bank A <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
bank B <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
end
```

`<fixed>` is exactly one token from `none`, `C#`, `D`, `D#`, `E`, `F`, `F#`,
`G`, `G#`, `A`, mapping to `FixedRegistration` values 0-9 in that order. These
tokens intentionally cannot be confused with adjustable A#/bank A. Numeric
spellings, `None`, enharmonic aliases and full-selector values 10/11 reject.
`FixedRegistration::None` has no fixed matrix row.

A complete version-4 document has **81 tokens and 12 canonical lines**. The
catalog record has four tokens; each manual adds two fixed-registration tokens
to the version-3 grammar. Both manual records and every bank remain mandatory,
including while cancelled. The exact catalog ID and lowercase SHA-256 above
must match the compiled frozen catalog; a well-formed but different digest also
rejects. Validation is unconditional, including when both fixed modes are
`none`. This avoids a future file silently changing meaning when its inactive
registration becomes active. There is no search, download or replacement path
inside parsing.

The catalog digest identifies the existing **authoring file bytes**, not the
compiled JSON wrapper, PDF, canonical JSON digest or either CSV review. The
unchanged admitted authoring file supplies this identity; native generation
must not silently substitute a differently hashed file. The documentary
compiler's existing ability to inspect differently formatted equivalent JSON
does not authorize changing the runtime catalog identity.

Retain all existing expression syntax, finite/range checks, signed-zero and
subnormal behavior, ASCII whitespace rules, token order, stream failure policy,
locale independence and destination atomicity. Canonical output uses one ASCII
space between tokens, no trailing spaces, and LF after every line including
`end`. Expression uses the existing classic-locale `max_digits10` formatter
under its temporary nearest-rounding guard. Parser/serializer restore the
caller's rounding mode and do not add audio-thread work.

Parse into a fresh candidate and assign only after the complete document and
snapshot validate. Missing, extra, duplicate, reordered or mismatched catalog
and fixed records reject; a malformed version-4 file never falls back to legacy
migration. No owners, held notes, phase, contacts, readiness, clock, input devices
or UI state are serialized.

## 2. Legacy migration and retained selection

The existing version-1/2/3 grammar and frozen input fixtures remain readable
unchanged. New fields are initialized independently of the caller's destination.

| Input | Percussion | Pedals | Fixed registrations |
|---|---|---|---|
| B3CONTROLS1 | Off / Second / Normal / Slow | `[0,0]` | `[None,None]` |
| B3CONTROLS2 | Read all four fields | `[0,0]` | `[None,None]` |
| B3CONTROLS3 | Read all four fields | Read both positions | `[None,None]` |
| B3CONTROLS4 | Read all four fields | Read both positions | Read both fixed tokens; validate catalog |

All versions preserve their supplied expression, four banks, selected banks and
route bits. Catalog/fixed records in an old format remain unsupported extras.
In particular, change the existing version-3-only pedal condition to explicitly
admit versions 3 **and 4**; do not accidentally treat version 4 like version 2.
Re-saving any successfully read version produces canonical version 4.

The snapshot stores three independent routing facts per manual:

| Stored fact | Domain | Meaning |
|---|---|---|
| `selected_banks[m]` | A/B | Remembered adjustable bank and legacy `Drawbar` edit target |
| `fixed_registrations[m]` | None or one of nine fixed rows | Retained fixed mode, including while cancelled |
| `route_enabled[m]` | false/true | Whether that manual is connected |

Derive the **effective** selector with the checked
`control_preset_selection(snapshot, manual, destination)` helper:
disabled -> Cancel/0; otherwise fixed mode 1-9 -> that key; otherwise bank A/B ->
10/11. Do not serialize only this effective value: Cancel/0 cannot reconstruct a
remembered fixed row, and a fixed row cannot reconstruct its remembered bank.
`none` with either remembered bank and either route bit is valid. Every fixed
mode with either remembered bank and either route bit is also valid.

## 3. Appended parameter identities

Freeze all **45 previous records** without changes to any field, including
labels, provenance pages, defaults, units and normalized metadata. Preserve the
existing 39- and 43-record compatibility checks and add the 45-record guard.
Sorting the complete old records by numeric ID and encoding with Python
`json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=True)`
then ASCII yields SHA-256:

`13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad`

Registry root schema becomes **4**, count **47**, model
`exclusive-fixed-percussion-pedal-console-v4`. Only root provenance is updated
to describe the new scope. A historical version-3 registry fixture may be added
from the exact baseline before editing the active registry; no historical
fixture is rewritten to match the new output.

| Field | Upper | Lower |
|---|---|---|
| ID | 20480 | 20481 |
| Path | `manual.upper.preset_selection` | `manual.lower.preset_selection` |
| Label | `Upper preset selection` | `Lower preset selection` |
| Event manual | upper | lower |

Both new records have `kind="preset_selector"`, `unit="preset-key-index"`,
minimum 0, maximum 11, default 11, `step_count=11`, evidence class `proposed`,
and event `{type: "select_preset", manual: <above>, index: 0}`. Source pages are
`[50,52,121,122,124,126,153,389,397,398,401,402,410,415,418]`.
Normalized metadata is minimum `0.0`, maximum/default `1.0`,
`meaning="exclusive-preset-key-index-fraction"`,
`to_plain="count(u >= nearest-binary64((2*k+1)/22), k=0..10)"`,
`to_normalized="nearest-binary64(x / 11)"`.

Values 0-11 mean C/Cancel, C#, D, D#, E, F, F#, G, G#, A, A#/bank A, B/bank B.
These are ordinary explicit routing parameters, not host programs or total-state
recall. Old bank IDs 8208/8209 retain their old target and 0/1 law; they explicitly
select a bank, clear fixed mode and reconnect the route.

## 4. Exact binary64 conversion law

For a valid normalized input `u`, return the number of the eleven frozen
thresholds less than or equal to `u`. Equality selects the higher key. For a
valid integral plain value `k`, return its frozen canonical normalized value.
The hexadecimal literals below are exact binary64 values, so neither operation
depends on the caller's floating-point rounding mode.

| k | Canonical normalized value for k | Threshold from k to k+1 |
|---:|---|---|
| 0 | `0x0.0p+0` | `0x1.745d1745d1746p-5` |
| 1 | `0x1.745d1745d1746p-4` | `0x1.1745d1745d174p-3` |
| 2 | `0x1.745d1745d1746p-3` | `0x1.d1745d1745d17p-3` |
| 3 | `0x1.1745d1745d174p-2` | `0x1.45d1745d1745dp-2` |
| 4 | `0x1.745d1745d1746p-2` | `0x1.a2e8ba2e8ba2fp-2` |
| 5 | `0x1.d1745d1745d17p-2` | `0x1.0000000000000p-1` |
| 6 | `0x1.1745d1745d174p-1` | `0x1.2e8ba2e8ba2e9p-1` |
| 7 | `0x1.45d1745d1745dp-1` | `0x1.5d1745d1745d1p-1` |
| 8 | `0x1.745d1745d1746p-1` | `0x1.8ba2e8ba2e8bap-1` |
| 9 | `0x1.a2e8ba2e8ba2fp-1` | `0x1.ba2e8ba2e8ba3p-1` |
| 10 | `0x1.d1745d1745d17p-1` | `0x1.e8ba2e8ba2e8cp-1` |
| 11 | `0x1.0000000000000p+0` | None |

All inputs must be finite and in range; plain input must also be integral.
Unknown IDs and every rejection preserve the entire output destination.
Normalized negative zero is accepted and selects Cancel; plain negative zero is
accepted and canonicalizes to positive zero **for the new selector only**.
Existing expression and old discrete signed-zero behavior remain unchanged.
No converter changes the floating-point rounding mode.

The current Python integer-ratio half-up formula is **not** this new law at five
downward-rounded thresholds: 3/22, 5/22, 7/22, 15/22 and 17/22. Those binary64
thresholds lie just below the mathematical midpoint, but equality intentionally
selects the higher key. Give only `preset_selector` a separate literal-threshold
and canonical-table branch. Preserve the previous integer-ratio oracle and
native 0/1/8-step behavior for all old kinds. Do not use runtime `u*11+0.5`,
runtime division by 11 under an arbitrary rounding mode, or a blanket replacement
of existing parameter conversion.

## 5. Host curves, aliases and publication

Keep `HostTimeline`'s existing curve reconstruction and admission limits except
for its descriptor count. Restores run before carried/fresh parameter points;
all controls at a sample are ordered by numeric parameter ID before note events.
For one ID, fresh points at zero follow carried points, and duplicate equal-time
points remain last-wins. Explicit points dispatch even when their normalized or
plain value is unchanged. A repeated old bank-B point must therefore leave a
fixed mode and reconnect B.

Old bank and new preset controls are interacting commands. If both emit at the
same sample, the higher-ID new selector acts last. An absent queue does not
continually reassert its cached value. Interpolated curves keep the established
rule of emitting on a discrete plain-value change or an explicit point; an
unchanged plateau is not another selector gesture.

**Raw curve anchors and applied routing are separate diagnostics.** Preserve
each parameter's last rendered normalized automation value; do not re-derive or
quantize every anchor from the effective engine state after each callback.
For example, a new fixed selector can change the applied route while the old
bank parameter's normalized anchor remains its last automated value. A later
explicit old bank point reasserts that route. Whole-state restore is the defined
operation that reinitializes every anchor from the restored controls, using the
effective helper for new IDs and remembered bank for old IDs. This preserves
legacy raw fractional anchors and interpolation behavior.

Likewise, the VST3 controller's host-value cache is not an audio acknowledgment.
`setComponentState` maps new IDs from the restored effective route; existing
`setParamNormalized`/`getParamNormalized` retain their raw accepted-value policy.
Native applied-route labels derive from copied audio snapshots, never a stale
host anchor or a retained bank alone. No new bidirectional host/editor protocol
is implied by adding two descriptors.

Both atomic publication formats must retain the two **raw fixed-mode** values,
not only effective selectors. The core StateExchange payload can use cells
45/46 for raw fixed modes, then route bits and acknowledgment, keeping its
`kParameterCount+3` capacity (50 cells). Its old descriptor-order comment must
be corrected because these raw cells differ from the new descriptor values.
Standalone `Session` pack/unpack also needs both fields with explicit masks and
range/shape assertions. Catalog strings are immutable program metadata and do
not enter callback payloads.

## 6. Required acceptance before implementation closure

1. Preserve all old fixtures as inputs; verify migrations into destinations
   containing nonzero fixed modes, varied banks, cancelled routes and percussion.
   Require exact canonical version-4 output and its 81-token grammar.
2. Round-trip all 100 fixed-mode pairs with all 16 remembered-bank/route-bit
   combinations, preserving every other field and signed expression zero.
3. Reject every invalid byte-valued fixed enum, all catalog identity mutations,
   missing/extra/duplicate/reordered fields, truncation, unsupported versions,
   16,384/16,385-byte boundaries and stream faults without partial publication.
4. Verify all eleven thresholds and adjacent representable values, all twelve
   canonical values, finite-domain rejection and caller-mode preservation under
   all four standard rounding modes. Independently verify nearest values using
   rational arithmetic, not a shared production table as the only oracle.
5. Preserve all 45 old records' digest, every old native/Python conversion and
   the earlier 39-/43-record guards. Match both new records across JSON, native
   descriptors, CLI output and actual VST3 descriptor export.
6. Test old/new same-sample conflicts, repeated unchanged bank-B points while
   fixed, new Cancel, absent queues, interpolation plateaus, endpoint carry,
   zero-frame callbacks, restore-plus-carry, and complete rejected-callback
   rollback. Compare coherent source across callback partitions.
7. Exercise raw fixed-mode round trips through core StateExchange and standalone
   snapshots, including cancelled fixed routes, queue-full/rejection behavior,
   concurrent publication and allocation probes. Update semantic comparison
   helpers that currently enumerate only old snapshot fields.
8. Through actual native state/automation paths, verify all 47 exports, state4
   recall and legacy recall, stable UUIDs, independent held notes/history and
   real serialized bytes. These are engineering gates; they do not establish
   physical latching, loaded gains or measured organ fidelity.
