# Core state and ownership review

Agent 31 reviewed the nominal dry core on 2026-11-13 from baseline `b9c1cac`.
This is a bounded source review and Linux software check, not host qualification
or physical instrument evidence. The relevant architecture source is atlas
chapter 063, PDF pp. 385-390, particularly timing and ownership on pp. 387-389.

## Inspected scope

The review inspected `Types`, `Profile`, `TonewheelBank`, `Engine`, `ControlState`
and `ControlStateIO`, their public headers, the engine/profile/control contracts,
and the existing C++ tests. It concentrated on indexing, narrowing, arithmetic
limits, caller-owned lifetimes, transactional failure and stream exceptions.
The renderer's WAV publication and CLI parsing were outside this review.
Agent 32 separately owns the observed macOS floating decimal conversion failure.

## Fixed finding: original stream exceptions escaped profile loading

`load_runtime_profile` caught `std::ios_base::failure` but an exception-enabled
`std::istream` can rethrow its stream buffer's original exception. A custom buffer
throwing `std::runtime_error` therefore escaped the boolean/error read boundary.
Existing profile transport tests covered an `ios_base::failure`, so they did not
detect this case. The control-state parser already handled original exceptions.

The fix retains the existing clean-EOF handling and catches an additional
`std::exception` only when the input has `badbit`, confirming a stream failure.
The destination remains untouched and the loader returns its existing read-error
message. Unrelated exceptions without `badbit` propagate; this is not a promise
that allocating offline loaders can never throw.

`test_core_robustness` injects the original exception before the first byte,
halfway through a valid profile and immediately after its complete contents.
Each location runs with the default mask, `badbit`, and all three failure bits.
The nine cases require rejection, preservation of every profile field and the
caller's locale/mask, a fresh error, and successful subsequent loading. An error
after all bytes have arrived must still reject; a clean throwing EOF must succeed.
The new test failed before the fix with the injected original exception and
passed after it.

## State and numeric boundary assessment

| Boundary | Inspected guarantee and existing evidence |
| --- | --- |
| Profiles, copies and moves | Runtime profiles, bank state, held keys, controls and coefficient caches are fixed-size values. Implicit copies/moves retain no borrowed profile/event storage. Existing profile-mutation, expired-profile and future-output tests exercise ownership. No custom copy/move code is needed. |
| Process spans | Empty output is a deliberate disconnected-output case. A nonempty short output rejects before mutation. Output beyond `frames` remains untouched. Events are read only during the call and are not retained. Existing tests cover these cases. |
| Event dispatch | Every event's enum, manual, payload, offset and order are checked before dispatch. Array-index and integer conversions happen after validation. A valid event prefix cannot partially modify state when a later event fails. |
| Capacity and clock | `frames <= 65536` bounds the frame loop; event count is checked against 1024 before conversion to `uint32_t`. Overflow uses subtraction before clock addition. Existing tests reach `UINT64_MAX`, reject positive advancement there, and permit zero-frame flushes. |
| Failed preparation | Bank and engine candidates validate before installation. Existing future-output tests catch damage to hidden state as well as copied diagnostics, including failure at the final source. |
| Failed restoration | Complete snapshot validation precedes replacement. Valid restoration changes controls and invalidates coefficients while retaining keys, phases and time. Existing tests compare subsequent audio after invalid snapshots. |
| Mix magnitude | At most `2 * 61 * 9 = 1098` branches contribute. Validated source amplitudes, drawbar gains, expression and output gain are bounded by one. This is far below finite `float` range; intentional values above PCM full scale remain possible. |
| Bounded profile I/O | Reading accepts at most 128 KiB and consumes at most one additional byte to reject oversized input. Token views refer to the local byte string only during parsing. The validated fixed-size candidate commits last. |

These findings assume well-formed C++ objects and live spans with the declared
extent. A dangling pointer, forged span or concurrently mutated input is a caller
precondition violation, not malformed payload that the core can safely validate.
Engine diagnostics, copies, preparation and control restoration still require
stopped or same-processing-thread access. There is no concurrent publication or
retirement protocol.

## Open numerical boundary: extremely small source frequencies

The runtime validator accepts positive frequencies below Nyquist. The bank also
rejects an increment that divides to zero, but a positive representable increment
can still disappear when added to a larger phase. In a bounded scratch probe,
tone 1 at `1e-300 Hz`, rate `48000 Hz`, seed zero prepared successfully. Its
increment was `2.0833333333333334e-305` turns/sample; its phase remained exactly
`0.88331080821364261` after 1024 frames, yielding a constant source sample of
`-0.66923577657334576`.

This is an unresolved extreme-frequency accuracy limit of the double phase
recurrence, not a memory or integer overflow. The supplied nominal 12-TET profile
does not contain such frequencies. A later numerical review must choose and
document a supported lower frequency/increment bound or a different phase
accumulator, with a behavioral regression for that policy. This review neither
changes that policy nor adds a test that treats the stalled source as desirable.

## Executed checks and limits

GNU 14.2.0, strict-warning Release build, isolated directory `agent31-release`:

```sh
cmake --build ../agent31-release --target test_core_robustness test_profile test_engine test_controls test_control_io test_tonewheel -j 2
ctest --test-dir ../agent31-release -R '^test_(core_robustness|profile|engine|controls|control_io|tonewheel)$' --output-on-failure
```

The CMake/CTest executables used were from `../build-tools/cmake/data/bin/`.
All six suites passed after the build completed. An earlier invocation while the
last target was still building reported `test_tonewheel` as Not Run; the corrected
run above passed. The new test's pre-fix run failed as described above.

An isolated sanitizer directory was configured but no sanitizer tests were run
for this change; the integrator owns that gate. No leak, callback deadline,
allocation, macOS, Windows or native host pass is claimed here. Agent 28 owns the
separate callback allocation audit. Later combined parser edits require the
integrator's joint build/test result; this review's execution predates them.
