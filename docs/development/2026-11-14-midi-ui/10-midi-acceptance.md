# A10 — Independent MIDI inbox and decoder acceptance

Actual assignment: `/root/w02_a10_midi_acceptance`, wave 2 of the newly
requested MIDI/UI session. Observed HEAD:
`7b36cfac2565397191b3df5e07112611e7f1b0e1`. Concurrent workers' changes were
preserved. This assignment owns only
[test_standalone_midi_input.cpp](../../../apps/standalone/tests/test_standalone_midi_input.cpp)
and this note; the integrator owns build integration, shared records and publication.

## Source and coverage

Read the standing agent rules, current scope, [frozen contract](../../MIDI_INPUT.md),
[declaration](../../../apps/standalone/MidiInput.h), existing standalone test
style and typed note/parameter declarations. The acceptance oracle uses literal
controller IDs and owner namespaces from the contract. No implementation was
available or consulted, and no contract, core, build file or other test was edited.

The ten behavioral scenarios cover:

- All 4,096 in-range route combinations and every representable out-of-range
  channel in every field; inactive/active rejection transactionality, retained
  configuration and counters, repeated end, successful restart and timestamp
  baseline resets. Sixteen explicit route permutations exercise every wire
  choice for every division, including channel 16 in each role.
- All 128 pitches in each division, adjacent endpoints, all 128 velocities at
  both endpoints, unmapped-channel precedence, canonical release velocity and
  offset, anonymous repeated On/Off commands without deduplication, and the
  exact ordered upper/lower/pedal scoped retirement commands.
- All 128 values for the 23 explicit parameter mappings and all three CC123
  mappings; every other controller; unsupported channel families/system
  statuses; missing/extra bytes, high-bit data and running-status fragments.
  Parameter edits must preserve the exact normalized fraction without adding
  a second drawbar rounding law.
- Equal, decreasing, zero and maximum receipt timestamps, next-observation
  comparisons rather than a high-water mark, and exact disposition/regression
  counters. Every active rejection family separately proves that its receipt
  timestamp becomes the next comparison baseline.
- Copy ownership, short-packet tail clearing including reused ring slots,
  FIFO order across 3,144 wraparound packets, exact 256-packet capacity and
  the 257th valid push fault, preserved destinations on unsuccessful pop,
  empty/oversized admission, fault-before-size and size-before-full precedence,
  independent/combined fault bits, lifetime reset/discard counters and no stale
  replay after reset. Quiescent accounting identities are checked explicitly.

## Verification actually executed

From the repository root, GCC **14.2.0** passed the following strict C++20
syntax check, without warnings, before and after the final edge-case review:

```sh
g++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion \
  -Wshadow -Werror -fsyntax-only -I apps/standalone -I include -I tests \
  '-DHAMMOND_TEST_PROFILE="syntax-only-unused.b3p"' \
  '-DHAMMOND_SOURCE_DIR="."' \
  apps/standalone/tests/test_standalone_midi_input.cpp
git diff --no-index --check /dev/null apps/standalone/tests/test_standalone_midi_input.cpp
```

SHA-256 identities at that check:

| Input | SHA-256 |
|---|---|
| Frozen `MidiInput.h` | `00a1e6d43f8db1721f7042b6c37b081f192dd85f55dc1bb999c81ee0a4014038` |
| Frozen `MIDI_INPUT.md` | `ca5310fac2b000f95f4857b8b79aba20ad9dc73b262b32d7fa2fff274df179b8` |
| Authored acceptance source | `a4d42a5be724ac04e8c113e409ae26ccb2ffced13fbc357bae054a4a809120fa` |

**Runtime tests remain unexecuted.** `MidiInput.cpp` was absent at handoff.
This check establishes that the acceptance source compiles against the frozen
declaration; it does not establish a decoder, queue, backend or device pass.
No commit or push was performed by this assignment.

## Next integration gate

After the implementation owner adds `MidiInput.cpp` to the SDK-free support
target, the existing standalone test glob discovers this file. Build and run
the actual target from one coherent source snapshot:

```sh
cmake -S . -B build-midi-acceptance -DBUILD_TESTING=ON \
  -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_STANDALONE=OFF \
  -DHAMMOND_BUILD_VST3=OFF
cmake --build build-midi-acceptance --target test_standalone_midi_input --parallel 2
ctest --test-dir build-midi-acceptance --output-on-failure --no-tests=error \
  -R '^test_standalone_midi_input$'
```

Retain any actual failure and repair before reporting acceptance. This suite
does not qualify live SPSC concurrency, allocations, saturated-counter limits,
Session/UI ownership integration, callback quiescence, the main-loop drain
budget, native backends, hardware timing or physical hotplug; those require
their separately assigned implementation and evidence.
