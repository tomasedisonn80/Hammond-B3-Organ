# Assignment 18 — independent renderer console regressions

Date: 2026-11-13. Continuation wave 03, assignment 18 of 60.

## Scope and files

Extended `tests/test_render.py` against the actual C++ `hammond_render` executable.
All **20 existing test methods remain**; **14 new methods** bring the suite to
**34 methods**. No core, renderer, producer, verifier, CMake or shared status file
was changed by this assignment. This note and the test file are the deliverables.

The old summary expectations now include the three intentional universal fields:

| Field | Expected value |
|---|---|
| `render_schema_version` | Integer `2` |
| `contact_model` | Default `ideal-contacts-v1`; explicit nominal mode uses `nominal-linear-travel-v1` |
| `percussion_model` | `shared-readiness-v1` |

Existing source model, profile identity, metrics, stereo format, clipping and
path-safety assertions remain. Test helpers gained optional console arguments;
old callers retain their old behavior. The tests use only Python's standard
library, an explicitly located built renderer and an explicitly located compiled
profile. Missing build inputs still fail, and no test depends on a retained
historical binary or a session-specific directory.

## New permanent checks

- All 24 documented combinations of contact mode, percussion selection, volume
  and decay render; the largest legal note-based and score-based argument sets
  work. Explicit defaults reproduce the implicit default WAV and summary.
- Each new option rejects missing, empty, oversized, unknown, wrong-case and
  whitespace-padded values, and both identical and conflicting duplicates.
- Percussion score events accept all four indices and both integral values.
  Lower/unknown manuals, out-of-range or malformed indices, fractional and
  nonfinite/out-of-range values, malformed arity and wrong-case types reject
  without altering inputs or leaving output.
- Initial percussion controls precede frame-zero score events. Score overrides
  enable, harmonic, volume and decay, and can mute initially enabled percussion.
  Stored volume/decay settings survive an initially disabled state and later
  enable, without being reapplied at each processing block.
- All nine nominal contact onsets and release openings are checked at 44.1,
  48 and 96 kHz against the named 8 ms press / 12 ms release model. The audible
  segment matches the continuously running ideal source exactly. Nominal note
  release retains its contact tail; panic mutes immediately.
- Both percussion harmonics, both volumes and both decay settings are checked
  against independently evaluated exponential envelopes applied to separately
  rendered shared source samples. A later additional held key does not reset the
  shared readiness. Duplicate targets and zero-elapsed-time release/repress
  preserve complete WAV bytes in both contact modes.
- A finite 137-frame open interval checks recovery from the prior readiness,
  including subsequent shared source phase. Nominal harmonic closure before the
  ninth detector contact checks the documented pre-detector audio policy.
- Lower-manual and upper-A audio remain unchanged by percussion selection.
  Eligible upper-B percussion masks the stored one-foot drawbar; disabling it
  reveals the retained registration without another drawbar event.
- A dense console score has 1,024 events at frame zero, another 1,024-event tie,
  and more than 1,024 events within large host blocks. Its exact WAV and all
  block-independent summary values match a sparse equivalent at all three rates
  with block sizes **1, 17, 64, 127, 512, 1,024 and 65,536**, including partial
  final blocks. A 1,025-event timestamp rejects.
- Nominal contacts plus percussion retain clipping metrics, exit code 2 and
  complete output cleanup under `--fail-on-clip`. Input collisions, hard-link
  aliases and existing output bytes/timestamps remain protected with the new
  console flags enabled.

The envelope comparison permits at most 1.3 PCM16 least-significant bits, derived
from rounding two independently quantized streams with a maximum tested gain of
1.5, plus a small allowance for float conversion. Contact and partition checks
use exact PCM/WAV equality where no numerical tolerance is required.

## Commands and observed results

The actual local CMake executable was
`/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake`; the build
directory was isolated from other agents. From the repository root:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S . -B /workspace/scratch/60e8291da354/a18-renderer-build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a18-renderer-build \
  --target hammond_render -j 2
python tests/test_render.py \
  --renderer /workspace/scratch/60e8291da354/a18-renderer-build/hammond_render \
  --profile /workspace/scratch/60e8291da354/a18-renderer-build/nominal.b3p
```

**Observed:** GCC 14.2.0 / Python 3.12.14, Release build succeeded; **34 methods
passed in 2.166 seconds**, with no skipped methods. An AST comparison with the
parent checkpoint independently confirmed that all 20 old method names remain
and that exactly 14 new methods were added. No implementation defect was found
by these checks. This assignment did not run the full CTest matrix, hosted CI,
sanitizers, macOS or Windows tests.

## Separate historical compatibility experiment

A scratch-only experiment invoked the retained baseline renderer and the new
Release renderer with the same compiled profile. It checked **13 render pairs**:
one default-options render of 1,031 frames, plus 5,003-frame renders over three
rates × two block sizes (17 and 127) × two registrations (`888000000` and
`008000000`), with seed 7 and the default note. Contact/percussion flags were
omitted to exercise compatibility defaults.

All **13 complete WAV byte streams matched**. Removing only the three new fields
from each new JSON report left **exactly equal old summary dictionaries**. The
new fields were separately checked for the exact default values above, and the
compiled profile bytes matched between build directories.

| Artifact | SHA-256 |
|---|---|
| Retained baseline executable | `8e781cb1df6f87443c4b6c88587cfa0e7d2bc8e23d32b5ef0a0bfb84d9ee8be4` |
| Newly tested Release executable | `b9c0acab7615820091bd7baaf782d894a8b85bb910a2dfba72b84463445d74c9` |
| Common compiled profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

The per-case scratch record was written to
`/workspace/scratch/60e8291da354/a18-renderer-build/baseline-comparison.json`.
That file and the baseline binary are supplemental session evidence; permanent
tests do not refer to either path. Cross-build and cross-platform bit identity
are not inferred from this same-environment comparison.

## Handoff

The integrator can include the test file and this note in the wave-03 checkpoint.
Wave 04 must update and verify the evidence producer/verifier for schema 2;
those wrappers were deliberately outside this assignment's ownership. Run the
complete integrated gate and the configured hosted matrix before describing
the integrated checkpoint as qualified.

These results validate software timing, routing, serialization and publication
behavior for **named nominal, unmeasured** models. They establish no measured
contact timing, physical percussion curve, instrument match, VST3 behavior,
device-audio support or real-time deadline guarantee.
