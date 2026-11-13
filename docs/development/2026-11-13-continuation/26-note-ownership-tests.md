# Assignment 26 — independent note-ownership tests

- Actual agent: `/root/w05_a26_note_ownership_tests`.
- Wave: 05, assignment 26 of this continuation's sixty new assignments.
- Date: 2026-11-13 UTC.
- Scope: independent permanent tests of the public bounded host-note ownership
  policy; no production, CMake, shared-status, index, commit or push changes.
- Outcome: **passed** the dedicated strict Release CTest target; no implementation
  mismatch found. Full combined-tree and hosted qualification remain separate gates.

## Inputs and evidence boundary

Read `AGENTS.md`, README, current status/next steps/development log, the project
plan, the retained complete atlas review, and atlas pp. 130, 132 and 151. Those
pages motivate bounded external ownership, explicit duplicate/FIFO policy,
same-offset ordering, and retention of the original manual after route changes.
They do not establish physical contact behavior or native-host qualification.

The frozen [public header](../../../include/hammond/NoteOwnership.h) and
[ownership contract](../../NOTE_OWNERSHIP.md) were the test specification.
Production `NoteOwnership.cpp` was not inspected to construct the oracle.
Expected event/owner tables are written independently; the tests do not implement
a second copy of the matching/compaction algorithm.

The new [test source](../../../tests/test_note_ownership.cpp) is the only executable
repository change owned by this assignment. This note is the second owned file.
No earlier fixture, test, model, control ID or runtime behavior was changed.

## Permanent coverage

| Contract | Independent checks |
| --- | --- |
| Default routes and checked queries | Bus 0 Upper / bus 1 Lower; empty owners; all 122 physical-key counts; invalid route, manual, pitch and owner-index queries preserve destinations |
| Identified notes | First/final ownership; exact first velocity; duplicate identity idempotence; distinct bus/channel identities; conflicting pitch rejection for On, Off and zero-velocity On; proper release permits same-offset ID reuse |
| Anonymous notes | FIFO ordering, identified/anonymous separation, exact bus/channel/pitch matching and unmatched-release no-op |
| Route changes | Existing identified and anonymous owners retain their original manual; FIFO releases an older Upper owner before a later Lower owner of the same external pitch |
| Channel retirement | Other channels and buses retain ownership; multiple NoteOff events follow final-owner removal order; no Engine AllNotesOff event is emitted |
| Valid input domain | All **1,952** bus/channel/pitch combinations (`2 × 16 × 61`), ID zero and `INT32_MAX`, and all **127** positive velocities |
| Invalid input domain | Every unsupported 8-bit event kind, bus, channel, pitch and velocity value in the tested field domains; invalid signed-ID boundaries; canonical AllNotesOff requirements; ordered offsets, half-open boundaries and frame limits |
| Owner capacity | Exactly 256 simultaneous owners, including a 256-owner physical key; duplicate/no-op acceptance at capacity; transient 257th-owner rejection even if a later release would restore the final count; release-before-add acceptance |
| Input/output capacity | Exactly 1,024 input no-ops with zero output capacity; exactly 1,024 emitted physical events; 1,025 input rejection; insufficient destination rollback; 558 valid input commands that would expand to 1,098 outputs reject even with a larger supplied span |
| Atomic failure | Complete adapter equality, zero result counts and unchanged output storage after every rejection; a subsequent valid retirement/fresh-note continuation matches an untouched copy |
| Output ownership | Exact event fields and original positive velocity; only the returned prefix changes, including when the supplied span is shorter than the sentinel storage |
| Partition/flush behavior | One independently specified 32-frame event timeline yields the same ten absolute physical events under eight block sizes, with and without separate zero-frame boundary flushes |
| Value ownership | Mutating a copied adapter does not change the original; failed route edits preserve live owners and both route slots |

The invalid-input tests include a valid prefix before the invalid command.
Separate dynamic-conflict and capacity cases exercise rollback after candidate
ownership changes, including emitted events that would otherwise be written.
Assertions compare semantic fields or the public value object's equality; they
do not compare structure padding with `memcmp`.

## Executed checks

Toolchain: GCC 14.2.0, C++20, Release, repository strict warnings including
`-Werror`. The dedicated build is outside the repository. The exact commands were:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/Hammond-B3-Organ \
  -B /workspace/scratch/60e8291da354/a26-note-build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a26-note-build \
  --target test_note_ownership -j 4
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a26-note-build \
  --output-on-failure -V -R '^test_note_ownership$'
```

The initial strict build and test passed. A nonfatal Make jobserver FIFO message
appeared during concurrent builds; compilation and linking still exited zero.
After reviewing coverage, anonymous-origin isolation and invalid route edits with
live ownership were added. The final rebuilt target passed **1/1 in 0.02 seconds**
with no skipped test. Its observed report was:

```text
note ownership: 2127 accepted calls, 2264 atomic rejections with future checks, 5226 expected physical events, 541 retained owner rows, 16 partition/flush cases
```

Counts are instrumented test observations, not estimates of all possible states.
The 16 partition cases and the per-rejection future probes are additional to the
accepted-call counter. Seven failed route edits against populated state also
have explicit equality checks; they are not included in the translate-rejection
counter. The suite has eleven named behavioral functions within one CTest target.

Observed SHA-256 identities of the final tested inputs/output:

| File | SHA-256 |
| --- | --- |
| `include/hammond/NoteOwnership.h` | `03baaa46de8c24d346c86a64a09e0503e85b78854d143a1cd616aeda38e4b1dc` |
| `src/NoteOwnership.cpp` | `f16e7a2f1698898a5552f73004992fb16225b1247d4e0f3170cca201e78b5751` |
| `tests/test_note_ownership.cpp` | `342e552db0a22200b24778bbb2e84cd275ad2f1cce0b2efbf60452ab33f0e6ea` |
| Local `test_note_ownership` executable | `ef4eff7d30dd3a19a7ad3a1bba4bb884409658e40884e66c0358b8a382a39973` |

The permanent test contains no scratch path or dependency on these retained local
binaries. CMake discovers it through the existing `test_*.cpp` rule.
Both owned files passed explicit UTF-8, trailing-whitespace and final-newline
checks; all three local Markdown links resolve. No-index diff checks emitted no
whitespace diagnostic (their difference status is expected for new files).

## Limits and next step

This is a typed software-policy test. It does not parse raw MIDI, exercise a DAW,
render audio, measure contacts, validate a percussion circuit, instrument callback
allocations or establish a deadline. Building the shared core/profile prerequisites
does not turn those unrelated behaviors into assertions of this target.

Assignment 29 must verify atomic cooperation between translation and Engine:
stage ownership, let Engine accept the translated block, and commit ownership only
after successful processing. Engine output-buffer, preparation, timeline and
capacity failures must preserve both domains. Root should include this test and
note in the wave-05 checkpoint, execute the full exact staged-source gate, publish
with the expected-head guard and observe the hosted matrix before extending the
qualification claim. No additional approval or unresolved implementation defect
blocks that integration.
