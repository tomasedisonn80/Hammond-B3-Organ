# Agent 07 — C++ types and stopped-thread profile boundary

## Assignment and evidence

- Wave 02 implementation assignment; modified only `include/hammond/Types.h`,
  `include/hammond/Profile.h`, `src/Profile.cpp`, and this note.
- Read the standing instructions, current handoff/plan, implementation contract,
  profile format, relevant wave-01 reviews, and atlas PDF text pp. 61, 64, 94, 96,
  98-99, 102 and 385. `docs/research/ATLAS_REVIEW.md` was not yet present.
- The definitions are original C++20 implementation. No missing companion header
  or schema was recovered. Source amplitudes are normalized peaks, never volts.
- Working branch was `main`; preserved pre-existing coordinator/agent changes.

## Implemented contract

- Fixed domains: 91 sources, two manuals, 61 playing keys, nine drawbars/positions,
  manual MIDI 36..96, one-based sources 1..91, manual source range 13..91.
- Fixed event capacity 1,024; hard block-frame ceiling 65,536. `Manual` has only
  Upper/Lower. Event records retain ordered sample offsets and MIDI/drawbar indices.
- Added `ProcessSpec`, explicitly numbered `Status`, `ProcessResult`, status names,
  supported-rate predicate and checked ID/index conversions.
- `RuntimeProfile` owns every array and bounded NUL-terminated ID/digest. Its
  zero-initialized state is invalid; there is no implicit nominal-profile fallback.
- Validation is allocation-free and checks all metadata/numeric/map ranges,
  finiteness, exact drawbar endpoint gains, supported rates 44.1/48/96 kHz and
  positive source frequencies strictly below the selected Nyquist frequency.
- Stream/file loading is stopped-thread work. It bounds input to 128 KiB, parses
  the exact ordered version-1 grammar, rejects partial/unknown/trailing records,
  checks canonical source order and exact counts, and preserves the destination
  on failure. Errors identify the failed field or expected record.
- Decimal parsing is locale-independent with classic ASCII whitespace. Hex floats,
  non-finite spellings, overflow/underflow, numeric suffixes and uppercase SHA hex
  are rejected. The file stream explicitly uses the classic locale.
- Public functions: `validate_runtime_profile`, `load_runtime_profile` (istream),
  and `load_runtime_profile_file` (filesystem path).

## Executed checks

- PASS: `g++ -std=c++20 -Wall -Wextra -Wpedantic -Werror -Iinclude -c`
  `src/Profile.cpp`; object was written outside the repository.
- PASS: same warnings-as-errors flags compiled and ran the external scratch
  `agent07-profile-smoke.cpp` harness against `src/Profile.cpp`.
- Harness rejected 35 malformed inputs with descriptive errors and byte-for-byte
  unchanged destination, covering header/version/ID/digest/count/order/range,
  malformed numbers, missing/extra records, embedded NUL and oversized input.
- Harness also passed all supported rates; invalid/NaN/infinite rate rejection;
  exact Nyquist rejection; NaN amplitude/infinite gain/metadata rejection;
  comma-locale isolation; exact 128-KiB acceptance; throwing-at-EOF and failed
  stream handling; missing/valid file loading; checked domain conversions.
- This was a focused smoke harness, not the assigned independent committed suite.
  No sanitizer, callback allocation instrumentation, host or audio tests were run
  by this agent. No commits or pushes were performed.

## Limits and next dependency

- The loader cannot verify an embedded authoring digest against an unseen JSON
  file. It checks its syntax and retains it as compiler-supplied provenance.
- Baseline equation/map authenticity remains the Python semantic compiler's task;
  C++ checks structural/numeric safety, not independent factory transcription.
- Stopped-thread lifecycle is a documented caller obligation; no locking or
  cross-thread publication was added. Engine preparation must copy this value.
- Next: integrate source/engine/renderer against these headers, compile the nominal
  authoring input, and run the independent profile/event/lifetime test suite.
