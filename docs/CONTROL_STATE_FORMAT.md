# Control snapshot format: B3CONTROLS2

This engineering format retains the exclusive A/B console controls described in
[CONSOLE_EXTENSION.md](CONSOLE_EXTENSION.md) and the retained percussion controls
in [CONSOLE_DYNAMICS.md](CONSOLE_DYNAMICS.md). It contains **43 controls**:
36 drawbar positions, two selected-bank values, global expression and the four
percussion settings. It also stores two independent route-enable bits, including
Cancel state. Hidden bank positions and percussion settings remain present when
the current routing makes them inaudible.

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

The serializer validates the entire snapshot, including every percussion enum,
builds an owned string, and replaces `destination` only on success. The caller
owns file opening, publication, overwrite and recovery policies; these functions
never open or write a file. Destination and error strings must be distinct:
aliasing returns false without changing the shared value and cannot supply a
separate diagnostic. New serialization always emits version 2.

The parser reads bounded temporary storage, checks the whole document and
validates a fresh candidate before assigning the complete destination. Failure
preserves every destination field, including percussion settings. It may consume
input or change stream status flags; the stream's locale and exception mask are
unchanged. Read failures, including a streambuf exception or a failure after the
last payload byte, reject. Normal EOF succeeds even when the caller configured
an EOF exception. Success clears `error`; rejected calls set a diagnostic except
for the serializer alias case. Allocation failures can propagate; destination
publication still occurs last.

## Exact version-2 grammar

Names are case sensitive. Records appear in this exact order, with no optional
or duplicate fields:

```text
B3CONTROLS2
expression <expression>
percussion enabled <0|1> harmonic <second|third> volume <normal|soft> decay <slow|fast>
manual upper selected <A|B> route_enabled <0|1>
bank A <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
bank B <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
manual lower selected <A|B> route_enabled <0|1>
bank A <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
bank B <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
end
```

Each bank has nine positions in physical drawbar order: 16-foot, 5-1/3-foot,
8-foot, 4-foot, 2-2/3-foot, 2-foot, 1-3/5-foot, 1-1/3-foot and 1-foot. A position
is exactly one ASCII digit `0` through `8`; signed, padded, floating and hexadecimal
integers reject. Selectors are exactly `A` or `B`, and route-enable values exactly
`0` or `1`. A disabled route does not erase or change its selected bank.

The percussion record has nine tokens. `enabled` accepts only `0` or `1`, not
numeric alternatives or words such as `true`. Harmonic, volume and decay use the
lowercase names in the grammar. All four fields are mandatory even when percussion
is disabled. Neither upper-bank selection nor Cancel changes these stored values.
A valid version-2 document contains **69 tokens**.

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

## Historical version-1 migration

`B3CONTROLS1` remains readable with its original **60-token grammar**: the same
expression and manual/bank records, with no percussion record. Parsing starts
from a fresh `ControlSnapshot`, so the migration is independent of previously
stored values in the caller's destination:

| New retained field | Explicit value after version-1 loading |
| --- | --- |
| Percussion enabled | Off (`false`) |
| Harmonic | Second |
| Volume | Normal |
| Decay | Slow |

All old drawbars, selectors, route bits and expression values retain their original
meaning. A percussion record inside version 1 is an unsupported extension and
rejects. A version-2 header without a complete percussion record also rejects;
it does not activate this migration or inherit the destination's old settings.
Unsupported future versions reject without mutation.

Re-saving a successfully migrated document produces canonical `B3CONTROLS2`.
There is no version-1 writer, so new settings cannot silently disappear through
an implicit downgrade. Keep historical test fixtures unchanged as migration inputs.

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

This example retains enabled percussion even though upper bank A currently makes
its route ineligible:

```text
B3CONTROLS2
expression 0.375
percussion enabled 1 harmonic third volume soft decay fast
manual upper selected A route_enabled 0
bank A 0 1 2 3 4 5 6 7 8
bank B 8 7 6 5 4 3 2 1 0
manual lower selected B route_enabled 1
bank A 1 3 5 7 0 2 4 6 8
bank B 8 6 4 2 0 7 5 3 1
end
```

## Scope and verification boundary

Snapshots contain no held keys or note owners, contact targets/positions/history,
pending events, source phases, random seed, render clock, readiness `q`, capacitor,
scanner/filter histories, rotary state or tails. They contain no source/console
profile identity or digest, parameter-registry identity, input mapping, editor state
or native-host compatibility manifest. A future wrapper owns those identities and
policies. Successful parsing alone makes no host, physical-fidelity or exact-render
continuation claim.

`test_control_io` checks every retained control, all selector/route combinations,
all nine positions in each stored bank, exact canonical fixtures, decimal round
trips through subnormal values, fixed binary64 vectors under all four standard
rounding modes, mode restoration on successful and rejected calls,
malformed versions/records/enums/numbers/counts,
truncation, duplicates, trailing data, byte limits, locale independence and stream
failures. Atomicity compares semantic fields and existing string bytes, never
`memcmp` over structure padding. These are software-contract tests.

`ControlState::restore` and `set_percussion_settings` validate before assignment.
Engine restoration changes musical controls while preserving live contact,
percussion and source histories; that behavior belongs to the separate engine
integration tests. The I/O API itself never accesses an Engine.

The continuation's [assignment 14 note](development/2026-11-13-continuation/14-control-migration.md)
records focused implementation checks. Independent permanent migration tests and
full integration results are recorded separately; a format specification is not
an executed host or hardware acceptance result.
