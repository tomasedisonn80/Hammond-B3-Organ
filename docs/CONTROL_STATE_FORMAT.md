# Control snapshot format: B3CONTROLS1

This is an engineering format for the early exclusive A/B console model in
[CONSOLE_EXTENSION.md](CONSOLE_EXTENSION.md). It retains all **39 controls**:
36 drawbar positions, two selected-bank values and global expression. It also
retains the two independent route-enable bits, including Cancel state. Hidden
bank positions are present even when their manual's route is disabled.

The source distinction between musical snapshots and dynamic checkpoints is
documented in atlas pp. 151–156, 389 and 401. This smaller format implements only
the controls currently present in `ControlSnapshot`; it is not the atlas's
complete proposed instrument patch schema.

## Public API and execution boundary

`hammond/ControlStateIO.h` declares:

```cpp
bool serialize_controls(const ControlSnapshot& snapshot,
                        std::string& destination, std::string& error);
bool parse_controls(std::istream& input,
                    ControlSnapshot& destination, std::string& error);
```

Both functions may allocate. Use them only with processing stopped or on a
control thread operating on an independently and safely copied snapshot. Reading
live mutable engine state from a control thread is not made safe by these APIs.
There is no concurrent publication protocol or Engine dependency here. Parsing,
stream access, formatting, allocation and destruction stay outside the audio
callback.

The serializer validates the complete snapshot with
`is_valid_control_snapshot`, builds an owned string, and replaces `destination`
only on success. The caller owns its file opening, atomic publication, overwrite
and recovery policies. These functions never open or write a file. The serializer's
destination and error strings must be distinct: aliasing returns false without
changing their shared value and cannot supply a separate diagnostic.

The parser reads into bounded temporary storage, checks the entire document,
validates its candidate with the same helper, and assigns the complete snapshot
only on success. Failure preserves every destination field; it may consume input
or change the stream's status flags. The stream's locale and exception mask are
unchanged. Read failures, including a streambuf exception and a failure after the
last payload byte, reject the candidate. A normal EOF still succeeds when the
caller configured its stream to throw at EOF. Successful operations clear `error`;
other rejected calls set a diagnostic except for the alias case above. Allocation
failures can propagate as exceptions; destination publication still happens last.

## Exact token grammar

All names are case sensitive. The header is the single token `B3CONTROLS1`.
Records must appear in exactly this order, with no optional or duplicate fields:

```text
B3CONTROLS1
expression <expression>
manual upper selected <A|B> route_enabled <0|1>
bank A <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
bank B <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
manual lower selected <A|B> route_enabled <0|1>
bank A <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
bank B <p0> <p1> <p2> <p3> <p4> <p5> <p6> <p7> <p8>
end
```

Each bank has exactly nine positions in `ControlSnapshot` drawbar-index order
(16′, 5⅓′, 8′, 4′, 2⅔′, 2′, 1⅗′, 1⅓′, 1′). Each position is one ASCII digit
`0` through `8`; signed, padded, floating and hexadecimal integers reject.
Selectors are the exact tokens `A` or `B`; route-enable values are the exact
tokens `0` or `1`. A disabled route does not erase or alter its selected bank.
There are exactly 60 tokens in a valid document.

Expression is a finite, representable `double` in the closed interval `[0,1]`.
Accepted decimal syntax is the regular expression
`[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][+-]?[0-9]+)?`. Examples include `0`,
`1.`, `.375`, `+3.75e-1` and `-0`. Signed zero is retained. `NaN`, infinities,
overflow, unrepresentable underflow, decimal commas, hexadecimal forms and
partial tokens reject. Numeric conversion is independent of the caller's locale.

Tokens are separated by one or more ASCII whitespace bytes: space, tab, LF, CR,
form feed or vertical tab. Leading and trailing ASCII whitespace is permitted;
line breaks are not otherwise significant. After `end`, only that whitespace
may remain. Comments, extensions, unknown versions, extra records, UTF byte-order
marks, embedded NULs and non-ASCII whitespace reject. The complete input,
including whitespace, must be at most **16,384 bytes** (`kMaxControlStateBytes`).
The reader consumes at most 16,385 bytes to detect excess length; this is a byte
limit, not a stream latency guarantee.

## Canonical serialization

Serialization emits the exact line layout above, one ASCII space between tokens,
no trailing spaces, and an LF after every line including `end`. Expression uses
the classic locale's decimal point, C++ general floating formatting and
`std::numeric_limits<double>::max_digits10` significant digits, so every accepted
snapshot expression round-trips without precision loss. For example, `0.1` is
written as `0.10000000000000001` on the supported binary64 implementation.
Discrete values always use the exact short tokens above.

A full example is:

```text
B3CONTROLS1
expression 0.375
manual upper selected A route_enabled 0
bank A 0 1 2 3 4 5 6 7 8
bank B 8 7 6 5 4 3 2 1 0
manual lower selected B route_enabled 1
bank A 1 3 5 7 0 2 4 6 8
bank B 8 6 4 2 0 7 5 3 1
end
```

## Deliberate scope and verification

This document stores no held keys or note owners, pending events, source phases,
random seed/state, frame clock or time, capacitors, scanner/filter histories,
percussion charge, rotary state or tails. Loading controls cannot resurrect saved
notes or resume exact DSP history. The format also contains no physical profile
identity/digest, registry identity, input mapping, native host state, editor state
or migration/host compatibility manifest. A future wrapper must own those
identities and compatibility policies; successful parsing makes no host, audio
fidelity or exact-render continuation promise. No legacy format is migrated, and
future version markers reject without changing the destination.

`test_control_io` checks every retained control, all selector/route combinations,
all nine positions in each stored bank, exact canonical fixtures, decimal round
trips through subnormal values, malformed versions/records/enums/numbers/counts,
truncation, duplicates, trailing data, byte limits, locale independence and stream
failures. Atomicity compares semantic fields and existing string bytes, never
`memcmp` over structure padding. These are software-contract tests.
