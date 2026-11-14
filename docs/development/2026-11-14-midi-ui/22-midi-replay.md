# A22 — Bounded synthetic MIDI replay data

Actual assignment: `/root/w04_a22_midi_replay`, wave 4 of the
`2026-11-14-midi-ui` session. Completed 2026-11-14. This is one newly dispatched
worker and does not recount prior workers or their acceptance results.

## Owned changes and result

Owned paths only:

- `apps/standalone/MidiReplay.h`
- `apps/standalone/MidiReplay.cpp`
- `apps/standalone/tests/test_standalone_midi_replay.cpp`
- `docs/MIDI_REPLAY.md`
- This evidence note.

**Result:** implemented the SDK-free, value-owned `B3MIDIREPLAY1` parser and
bounded regular-file loader. The public header was frozen and communicated
before implementing the body so A23 could integrate the actual main loop.
Root added `MidiReplay.cpp` to `hammond_standalone_support`; this worker did not
edit CMake, main, shared status, ledger or other workers' source. No commit,
publication or subagent dispatch was performed.

The strict direct compile and fresh SDK-free CMake Release target both passed.
The targeted CTest gate passed **1/1**, with **eight scenarios**, **18 successful
parses**, **237 parse rejections**, **three successful loads**, **13 load
rejections** and **zero capability skips** on this Linux runner. No compile or
test failure preceded those passing results.

Source/contract reading included `AGENTS.md`, the current MIDI/UI scope and
atlas summary, project plan, relevant status/handoff context,
[`MIDI_INPUT.md`](../../MIDI_INPUT.md), and the existing
`ScriptedInput.h/.cpp` parser and loader. The existing nonsymlink regular-file
loading policy was preserved. This assignment does not claim another complete
independent atlas/PDF reading.

## Implemented boundary

The public plan owns at most 2048 records. Each contains an unsigned millisecond
time, one of `Bytes`, `Connect`, `Disconnect` or `BackendFault`, three zero-filled
byte slots and a payload size. It contains no pointer into input text, runtime
cursor, SDL value, Session reference or physical-device object.

The parser accepts exact `B3MIDIREPLAY1`/`duration_ms` header lines, a duration
from 250 through 10000 ms, and nondecreasing event times below that duration.
Records are `N bytes HH [HH [HH]]`, `N connect`, `N disconnect` and
`N fault backend`. All raw values 00 through FF are preserved, including invalid
MIDI semantics. The decoder remains responsible for malformed, unsupported,
unmapped and out-of-range outcomes. Equal-time records retain source order.

Limits are 65536 total bytes, 256 bytes per line excluding LF/CRLF, and 2048
events. Header placement, ASCII/line endings, full-line comments, decimal times,
exact two-digit hexadecimal bytes and absence of trailing fields are validated.
No arbitrary command, include, callback, execution or filesystem write is
available through file contents. Failure preserves all destination fields.

The loader validates the same opened handle, rejects leaf symlinks/reparse
points and non-regular inputs, reads no more than 65537 bytes, and rejects a
detected size change. Parent-directory links remain permitted. POSIX open uses
nonblocking mode so a FIFO with no writer cannot stall before type validation.
A same-size concurrent file rewrite is not independently detected.

The [public replay contract](../../MIDI_REPLAY.md) also records the application
requirements coordinated with A23: initially disconnected input, counted/dropped
closed packets, explicit fresh-epoch connect, release acknowledgment before
following packets cross into the new epoch, at most 512 due source records per
turn followed by the existing 32-packet inbox drain, and independently ordered
equal-duration UI/MIDI streams. Those runtime requirements are not claimed as
executed by the parser test.

## Independent acceptance observations

| Scenario | Actual assertion boundary |
| --- | --- |
| Grammar and owned storage | Empty valid plan; CRLF and tabs; source-order ties across all four kinds; payload/tail zeroing; every inactive entry reset; original input overwritten after parsing without changing the plan. |
| Every raw byte | All 256 values in one-, two- and three-byte records, mixed upper/lower hexadecimal spelling: 768 ordered events with literal numeric byte expectations. |
| Malformed syntax and ASCII | Invalid magic/header placement, inline comments, unknown actions/faults, invalid hex tokens and every disallowed byte including NUL, DEL and high bytes. Every failure preserves active and inactive sentinel fields. |
| Duration and ordering | Both duration endpoints, final admissible timestamps, decimal leading zeroes, negative/positive signs, numeric overflow, fractions, suffixes, decreasing times and equality with duration. Repeated or disconnected-state actions remain unsimplified data. |
| Resource bounds | Exactly 2048 accepted and 2049 rejected events; exactly 256 accepted and 257 rejected line bytes, including comments/blank lines; exactly 65536 accepted and 65537 rejected total bytes. |
| Filesystem admission | Unicode/space paths, missing/empty/NUL/directory paths, malformed file, exact maximum file, oversized regular/sparse files, valid/dangling leaf symlinks, permitted linked parent, unwritten FIFO and `/dev/null`. All rejected loads preserve the complete destination. |
| Existing decoder reached | Eight parsed records enter the real inbox and decoder: three malformed, two unsupported, one unmapped, one out of range and one action. The script parser does not silently normalize them. |
| Actual inbox overflow | One parsed connect followed by 257 same-time packets is retained as 258 events. Manual test feeding accepts 256 real pushes and observes the 257th overflow; faults block dequeue, preserve output and discard 256 packets on quiescent reset. No fabricated overflow signal is used. |

These tests use explicit literal boundaries and disposition expectations. The
test's `CHECK` macro exits on failure even under `-DNDEBUG`; it does not depend
on disabled C assertions.

## Exact executed commands and identities

Working directory for every command below:
`/workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ`.

Observed HEAD and local `origin/main` tracking reference were
`7b36cfac2565397191b3df5e07112611e7f1b0e1`, committed tree
`f6fe5ec715fe113d581e188834d51f9a30f52046`. This work is in the concurrent
uncommitted MIDI/UI candidate; that historical committed tree is not the tested
candidate. No fresh remote verification or full-source publication gate is
claimed here.

Toolchain: GNU C++ **14.2.0**, CMake/CTest **4.4.4**, configured Python
**3.12.14**. Both compilation paths used C++20 and
`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
The CMake Release compile commands also contain `-O3 -DNDEBUG`; production
support uses `HAMMOND_HAS_RTMIDI=0`.

```sh
mkdir -p /workspace/scratch/cd4bd06ce68f/a22-midi-replay
c++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -Iapps/standalone -Iinclude apps/standalone/MidiReplay.cpp apps/standalone/MidiInput.cpp apps/standalone/tests/test_standalone_midi_replay.cpp -o /workspace/scratch/cd4bd06ce68f/a22-midi-replay/test_standalone_midi_replay
/workspace/scratch/cd4bd06ce68f/a22-midi-replay/test_standalone_midi_replay
/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake -S /workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ -B /workspace/scratch/cd4bd06ce68f/a22-midi-replay/cmake-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_ENABLE_MIDI=OFF -DHAMMOND_BUILD_VST3=OFF
/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake --build /workspace/scratch/cd4bd06ce68f/a22-midi-replay/cmake-release --target test_standalone_midi_replay --parallel 2
/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/ctest --test-dir /workspace/scratch/cd4bd06ce68f/a22-midi-replay/cmake-release -R '^test_standalone_midi_replay$' --verbose --output-on-failure --no-tests=error --output-log /workspace/scratch/cd4bd06ce68f/a22-midi-replay/ctest-release.log
```

The fresh CMake directory rebuilt the core, generated routing/profile and all
standalone support sources before linking the test. CTest reported **1/1
passed, 0.01 seconds**. This observed duration is not callback performance or
device timing qualification. Direct and CMake execution both printed:

```text
Standalone MIDI replay acceptance: 8 scenarios passed; 18 parsed, 237 parse rejections, 3 loaded, 13 load rejections, 0 capability skips
```

Key source SHA-256 identities recorded after the build and checked again after
the CTest run:

| File | SHA-256 |
| --- | --- |
| `MidiReplay.h` | `c0a62c0d33e7b0c3b90237e82cf631222d3d5274bb6b45fa797906e1e77a3948` |
| `MidiReplay.cpp` | `a61047fcb0da050eae35a10e86205a496d13ea7d00fb8b113c8682d1556a88db` |
| `test_standalone_midi_replay.cpp` | `d7ce19f7e5d2d6082af726512cd54171a7686d1aa78834650f82c33021b3db2b` |
| Existing `MidiInput.h` | `00a1e6d43f8db1721f7042b6c37b081f192dd85f55dc1bb999c81ee0a4014038` |
| Existing `MidiInput.cpp` | `32e135e84a870dc0e7d6cd9f5a9804b6c75031d4b2fd8dcfcf4d0959bd210802` |

The CMake test executable SHA-256 is
`520104f1fb8b4360455429e386e3e6b75d06d1bd0146b547507f2bfd99b4a506`.
The earlier direct executable SHA-256 is
`0b34cd36b13821369900d74bb61c56ba2e56261f6851a8798cdaf36a0c182135`.
The verbose CTest scratch log SHA-256 is
`261de7d8f0eeb037b6d5796cd6d3988991488810c6474f0b10f4d38fc3c8adc5`.
These scratch artifacts are verification aids; the durable evidence is this
record and the retained test source. The integrator owns the final coherent
source freeze and published evidence.

Each of the five new owned files also received
`git diff --no-index --check /dev/null <owned-path>` without whitespace
diagnostics. The addition comparison exits with status 1 as expected. The
earlier scoped `git diff --check` emitted no diagnostics; untracked additions
require the explicit no-index checks above.

## Limits and next work

No observed production defect or unaddressed parser-test failure remains in this
scope. Not run by A22: native main-loop/SDL replay, the 512/32 runtime budgets,
Session release acknowledgment, UI/MIDI pairing, actual callbacks, RtMidi,
physical input, hardware timing/hotplug, audio fidelity, sanitizer or concurrent
file-mutation/error-injection testing, Windows/macOS builds, complete project
CTest, packaging and publication. The three successful file loads and zero
capability skips describe this Linux run only.

Next: A23 should finish the main-loop integration against the frozen header and
exercise initially closed packets, same-time reconnect barriers, scoped release,
paired UI ownership and actual 257-packet overflow through the real bounded
producer/drain. The integrator should rebuild this discovered SDK-free test
alongside those native tests from one coherent final source candidate. Hardware
qualification still requires an identified device, OS/backend and retained
controller observations.
