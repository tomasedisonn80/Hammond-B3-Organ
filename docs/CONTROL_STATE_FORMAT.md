# Control snapshot format: B3CONTROLS4

This engineering format retains the exclusive A/B console controls described in
[CONSOLE_EXTENSION.md](CONSOLE_EXTENSION.md) and the retained percussion controls
in [CONSOLE_DYNAMICS.md](CONSOLE_DYNAMICS.md), the two nominal pedal mixture
positions in [PEDAL_INTEGRATION_CONTRACT.md](PEDAL_INTEGRATION_CONTRACT.md),
and the two retained fixed modes in
[PRESET_SELECTION_CONTRACT.md](PRESET_SELECTION_CONTRACT.md).
It stores 36 manual drawbar positions, two remembered bank values, global
expression, four percussion settings, two pedal positions and two fixed modes,
plus two independent manual route-enable bits. The public registry has 47
parameters; its two new effective selectors are derived from the remembered
bank, raw fixed mode and route bit, rather than being additional saved fields.
Version 4 also binds these controls to one exact immutable registration catalog.
Hidden bank positions, fixed modes, percussion settings and pedal positions
remain present when the current routing or zero pedal gain makes them inaudible.
Pedal Mixture 1/2 are independent retained controls, not members of a manual bank. Manual Cancel and
selection do not change them.

The source distinction between musical snapshots and dynamic checkpoints is
recorded in atlas pp. 151-156, 389, 394 and 401. This format is a versioned internal
control contract. It is not the atlas's full proposed instrument patch schema or
a verified native-host state format.

## Public API and execution boundary

`hammond/ControlStateIO.h` declares:

```cpp
bool serialize_controls(const ControlSnapshot& snapshot,
                        std::string& destination, std::string& error);
bool parse_controls(std::istream& input,
                    ControlSnapshot& destination, std::string& error);
```

Both functions may allocate. Use them with processing stopped or on a control
thread operating on an independently and safely copied snapshot. Reading live
mutable engine state from another thread is not made safe by these APIs. There
is no concurrent publication protocol or Engine dependency here. Parsing, stream
access, formatting, allocation and destruction stay outside the audio callback.

The serializer validates the entire snapshot, including every percussion and
fixed-registration enum and both pedal positions, builds an owned string, and
replaces `destination` only on success. The caller
owns file opening, publication, overwrite and recovery policies; these functions
never open or write a file. Destination and error strings must be distinct:
aliasing returns false without changing the shared value and cannot supply a
separate diagnostic. New serialization always emits version 4.

The parser reads bounded temporary storage, checks the whole document and
validates a fresh candidate before assigning the complete destination. Failure
preserves every destination field, including cancelled fixed memory, percussion
and pedal settings. It may consume input or change stream status flags; the
stream's locale and exception mask are
unchanged. Read failures, including a streambuf exception or a failure after the
last payload byte, reject. Normal EOF succeeds even when the caller configured
an EOF exception. Success clears `error`; rejected calls set a diagnostic except
for the serializer alias case. Allocation failures can propagate; destination
publication still occurs last.

## Exact version-4 grammar

Names are case sensitive. Records appear in this exact order, with no optional
or duplicate fields:

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

Each bank has nine positions in physical drawbar order: 16-foot, 5-1/3-foot,
8-foot, 4-foot, 2-2/3-foot, 2-foot, 1-3/5-foot, 1-1/3-foot and 1-foot. A position
is exactly one ASCII digit `0` through `8`; signed, padded, floating and hexadecimal
integers reject. Selectors are exactly `A` or `B`, and route-enable values exactly
`0` or `1`. A disabled route does not erase or change its remembered bank or
fixed mode. Every bank remains mandatory even while a fixed registration sounds.

The fixed token is exactly `none`, `C#`, `D`, `D#`, `E`, `F`, `F#`, `G`, `G#`
or `A`, mapping in order to `FixedRegistration` values 0 through 9. Numeric
spellings, `None`, enharmonic names, C/Cancel, A#/bank A and B/bank B reject.
`none` selects the remembered adjustable bank when the route is enabled; it has
no fixed matrix row. Any of the ten retained fixed modes is valid with either
remembered bank and either route bit. Cancel saves the route bit as zero while
preserving both the fixed mode and the bank. Saving only the effective selector
would lose that remembered state.

The catalog record is mandatory and must match both the exact ID and lowercase
SHA-256 above, as exposed by the compiled frozen catalog. The SHA identifies the
raw authoring file bytes, not a generated table, PDF, compiled JSON wrapper or
CSV review. Validation is unconditional, including when both fixed modes are
`none`. A correctly shaped but different digest, unknown catalog, missing record
or duplicate record rejects transactionally. Parsing never searches for,
downloads or substitutes another catalog. Catalog identity is immutable program
metadata; no strings or pointers are added to `ControlSnapshot`.

The percussion record has nine tokens. `enabled` accepts only `0` or `1`, not
numeric alternatives or words such as `true`. Harmonic, volume and decay use the
lowercase names in the grammar. All four fields are mandatory even when percussion
is disabled. Neither upper-bank selection nor Cancel changes these stored values.
The pedal record has exactly four tokens: `pedal drawbars` followed by the two
positions, each one ASCII digit `0` through `8`. The first position controls
Mixture 1 and the second Mixture 2; these labels do not claim calibrated footage
or physical reactor behavior. Both values are mandatory, including when muted.
The record follows percussion and precedes the upper manual. A valid version-4
document contains **81 tokens and 12 canonical lines**. The catalog contributes
four tokens and each manual contributes two fixed-registration tokens beyond
the historical version-3 grammar.

Expression is a finite, representable `double` in `[0,1]`. Accepted decimal syntax
is `[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][+-]?[0-9]+)?`. Examples include `0`,
`1.`, `.375`, `+3.75e-1` and `-0`; signed zero is retained. NaN, infinities,
overflow, unrepresentable underflow, decimal commas, hexadecimal forms and partial
tokens reject. Numeric conversion is independent of the caller's locale.

Tokens are separated by one or more ASCII whitespace bytes: space, tab, LF, CR,
form feed or vertical tab. Leading and trailing ASCII whitespace is permitted;
line breaks are otherwise insignificant. Only whitespace may follow `end`.
Comments, unknown versions or extensions, extra records, UTF byte-order marks,
embedded NULs and non-ASCII whitespace reject. The whole input, including whitespace,
is limited to **16,384 bytes** (`kMaxControlStateBytes`). The reader consumes at most
16,385 bytes to detect excess length; this does not bound stream latency.

## Historical version-1, version-2 and version-3 migration

`B3CONTROLS1` remains readable with its original **60-token grammar**: the same
expression and manual/bank records, with neither percussion nor pedal records.
`B3CONTROLS2` retains its original **69-token grammar**, adding the complete
percussion record but no pedal record. `B3CONTROLS3` retains its original
**73-token grammar**, adding the two pedal positions but no catalog or fixed
fields. Parsing starts from a fresh `ControlSnapshot`, so old-format migration
never inherits previously stored
values in the caller's destination:

| Input version | Percussion after loading | Pedal positions after loading | Fixed modes after loading |
| --- | --- | --- | --- |
| 1 | Explicit Off / Second / Normal / Slow | Explicit `[0,0]` | Explicit `[None,None]` |
| 2 | All four values read from the document | Explicit `[0,0]` | Explicit `[None,None]` |
| 3 | All four values required in the document | Both values required in the document | Explicit `[None,None]` |
| 4 | All four values required in the document | Both values required in the document | Both values required; catalog must match |

All old drawbars, selectors, route bits, expression and supplied percussion
values retain their original meaning. A percussion record inside version 1, or
a pedal record inside version 1/2, is an unsupported extension and rejects.
A catalog or fixed-registration record inside version 1/2/3 is also an
unsupported extension and rejects. A version-2 header missing percussion rejects.
A version-3 header missing pedals or percussion also rejects. Version 4 requires
its catalog, percussion, pedals and both fixed fields; a missing new record is
never treated as an old-format migration. Merely changing a historical document's
header does not supply its missing records. Unsupported future versions reject
without destination mutation.

Re-saving any accepted document produces canonical `B3CONTROLS4`. There is no
older-version writer, so new settings cannot silently disappear through an
implicit downgrade. Frozen historical version-1, version-2 and version-3 fixtures
remain unchanged as migration inputs.

## Canonical serialization

Serialization emits the exact line layout above, one ASCII space between tokens,
no trailing spaces, and an LF after every line including `end`. Expression uses
the classic locale's decimal point, C++ general floating formatting and
`std::numeric_limits<double>::max_digits10` significant digits, so every accepted
snapshot expression round-trips without precision loss. Expression formatting
temporarily selects round-to-nearest, matching decimal parsing, and restores the
caller's floating-point rounding mode when the formatting scope exits, including
exception unwinding. A failure to select nearest rounding rejects serialization
with a diagnostic before changing the destination. Serialized bytes therefore
do not depend on the caller selecting downward, upward or toward-zero rounding.
For example, `0.1` is written as `0.10000000000000001` on the supported binary64
implementation.
Discrete values always use the exact short tokens above.

This example retains a cancelled upper C# registration and its remembered bank A,
an enabled lower fixed A with remembered bank B, and enabled percussion whose
upper route is currently ineligible:

```text
B3CONTROLS4
registration_catalog atlas-chapel-nominal-v1 sha256 c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf
expression 0.375
percussion enabled 1 harmonic third volume soft decay fast
pedal drawbars 2 7
manual upper selected A fixed_registration C# route_enabled 0
bank A 0 1 2 3 4 5 6 7 8
bank B 8 7 6 5 4 3 2 1 0
manual lower selected B fixed_registration A route_enabled 1
bank A 1 3 5 7 0 2 4 6 8
bank B 8 6 4 2 0 7 5 3 1
end
```

## Scope and verification boundary

Snapshots contain no held keys/pedals or note owners, contact targets/positions/history,
pending events, source phases, random seed, render clock, readiness `q`, capacitor,
scanner/filter histories, rotary state or tails. They contain no source/console
profile identity or digest, parameter-registry identity, input mapping, editor state
or native-host compatibility manifest. The version-4 document adds only the fixed
registration catalog ID/hash; it is not an engine/profile checkpoint. A future
wrapper owns the other identities and policies. Successful parsing alone makes
no host, physical-fidelity or exact-render
continuation claim.

`test_control_io` checks every retained control, all selector/route combinations,
all nine positions in each stored bank, exact canonical fixtures, decimal round
trips through subnormal values, fixed binary64 vectors under all four standard
rounding modes, mode restoration on successful and rejected calls,
malformed versions/records/enums/numbers/counts,
truncation, duplicates, trailing data, byte limits, locale independence and stream
failures. Atomicity compares semantic fields and existing string bytes, never
`memcmp` over structure padding. These are software-contract tests.

The state4 extension independently asserts the 81-token/12-line grammar and
exact canonical bytes for all 100 fixed-mode pairs times all 16 remembered-bank/
route combinations, including cancelled fixed memory, signed expression zero,
nondefault percussion and nonzero pedals. It applies all three unchanged legacy
grammars to each destination combination (4,800 migrations). It rejects every
invalid byte-valued fixed enum on each enabled and cancelled manual, every
single-character catalog-ID mutation, every digest-position substitution,
uppercase digest letters, missing/extra/duplicate/reordered records and
truncations. Catalog rejection is exercised with both fixed modes `none` and
with remembered fixed modes. The existing locale, stream-fault, four-rounding-
mode and 16,384/16,385-byte checks also cover version 4.

`test_pedal_controls` independently checks all 81 pedal position pairs,
canonical version-4 bytes, all three old-format migrations into every previous pedal
pair, every invalid byte-valued position, manual-Cancel/selector independence,
checked getters, value ownership, all four rounding modes, missing/duplicate/
reordered pedal records, late malformed input and output preservation. The
existing literal version-3 fixtures and grammar-rejection checks remain historical
input coverage. Every old version resets a destination's nonzero fixed modes.

`ControlState::restore`, `set_percussion_settings` and `set_pedal_drawbar` validate
before assignment.
Engine restoration changes musical controls while preserving live contact,
percussion and source histories; that behavior belongs to the separate engine
integration tests. The I/O API itself never accesses an Engine.

The [fixed-state assignment note](development/2026-11-14-preset-continuation/15-state-migration.md)
records the version-4 implementation and actual focused checks.
The [pedal-state assignment note](development/2026-11-13-pedals/14-pedal-state.md)
records the version-3 implementation and actual focused checks. The earlier
[percussion migration note](development/2026-11-13-continuation/14-control-migration.md)
remains the historical version-2 record. Full pedal Engine/history integration,
host state, concurrent publication and physical fidelity require separate
acceptance; this control format does not establish them.
