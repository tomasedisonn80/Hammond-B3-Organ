# Assignment 11 — independent rotary profile admission

**Agent:** `/root/w02_a11_profile_tests`; wave 2, assignment 11/60; 13 November
2026. Owned changes are this note and
[test_rotary_profile.py](../../../tests/test_rotary_profile.py). No production,
schema, fixture, CMake or shared-status files were edited by this worker. Root
owns integration, commits and publication.

## Inputs and claim

Read the repository agent rules, [rotary scope](../../ROTARY_SCOPE.md),
[profile contract](../../ROTARY_PROFILE.md),
[numerical contract](../../ROTARY_NUMERICAL_CONTRACT.md), immutable rotary types,
validator, schema and proposed fixture. The new suite qualifies **R1 admission**:
bounded parsing, provenance, SI projection and the full-orbit constraints. It
does not qualify motion, propagation, rendering, spectral behavior, real-time
execution or a measured cabinet.

The checkout HEAD during execution was
`6b4b6bd3a881dd13e6e3b7f846993f0fbbb977f9`, tree
`a2fd40769d47444bc2fc5b5e8ad16e3703388041`. Wave-2 files were working-tree inputs;
these SHA-256 values identify the actual tested versions:

| Input | SHA-256 |
| --- | --- |
| `tests/test_rotary_profile.py` | `d44bb15a3cc72b7e77240381e0371b66012671c9b4b21933f8b4b1466ec1335f` |
| `tools/validate_rotary_profile.py` | `260b63aaf3e22e136ce85143565c5df721ad2869b4ed377f1c5e95d454de5279` |
| `data/rotary-profile.schema.json` | `3bc684558171645ac4b20caa3fa4e2aa6ae6e072e63e3501f61c4e0e0e390d38` |
| `data/rotary/nominal-research-v1.json` | `c0473cb20604726d989d7c280700109f647f7b227edb71c61d275ed9bfd67443` |
| `include/hammond/RotaryTypes.h` | `b27ce4934188c24ebe557469fa5191dd7cdcd98a1c3fdbe274b0d7585e4578b4` |
| `docs/ROTARY_NUMERICAL_CONTRACT.md` | `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63` |

## Independent constructions and retained coverage

Each horn/drum and left/right pairing is isolated in the geometry regressions.
A receiver directly above the circular path has closest distance exactly its
height: 0.02 m is accepted, and its representable predecessor is rejected.
A 19.5 m horizontal axis/receiver separation with a 0.5 m radius gives a
farthest distance exactly 20 m; a representably larger distance is rejected.
Another case starts with the mouth 1 m from the microphone but intersects it
half a revolution later. This distinguishes full-orbit admission from an
initial-position check.

Valid cases include zero-radius point sources, receivers on the axis and
inside the orbit's projected disk, vertical separation, and rigid rotation
plus translation. The sonic boundary uses radius 0.5 m, sound speed 320 m/s
and speed 160 rad/s, so the rim speed is exactly one quarter of sound speed.
Both a fast target and an independently larger initial speed exercise this
boundary and its immediate excluded neighbor.

Other checks retain exact unit/evidence requirements on all 22 quantities,
eight explicitly unknown physical fields, both signs and commands, speed
ordering, phase endpoints, source/model identities, detached normalization,
and unchanged values/container identities after rejection. A file replacement
during validation proves the reported digest belongs to the already-read
bytes, not a second read of the pathname.

Parser cases include duplicate and escaped-duplicate members, malformed UTF-8,
BOMs, trailing data, nonfinite tokens, booleans, huge integers, Unicode controls
and surrogates, excessive depth/collections/value count, cycles and non-JSON
Python objects. Byte-limit tests include exactly 128 KiB and simulated file
growth after metadata inspection. Nonregular descriptor classifications are
mocked; this is not an actual FIFO/device or Windows execution claim. CLI
subprocesses check success/error JSON, exit 0/2, help and unchanged temporary
file contents and modification times.

## Observed defect and repair

The original schema prose pattern allowed NUL through its `\S` term and a
trailing newline through `$`. At `speed_of_sound.evidence.reason`, schema
validation accepted `"valid reason\n"`, `"A\u0000B"` and `"\u0000"`; semantic
admission rejected all three. A trailing newline in `profile_id` had the same
schema-only discrepancy. Ordinary prose passed and whitespace-only prose
failed. These observations were reported to root and the profile owner before
repair; the semantic validator was already correct.

Root repaired 30 schema patterns, explicitly excluding controls and using an
absolute-end assertion. The retained optional audit now applies these cases
across every reason/acquisition field and the identifier, plus Unicode prose,
unit/provenance and closed-object cases. Four intentional schema limitations
are tested separately: an integral float metadata token, reversed targets,
orbit intersection and excessive initial rim speed require semantic rejection.
No bounds, fixture values or physical claims were changed to obtain a pass.

## Executed commands and handoff

Working directory: repository root. Host: Python **3.12.14**.

```sh
python3 tests/test_rotary_profile.py -v
python3 tests/test_rotary_profile.py --schema-audit
```

The final default run passed **33 tests in 2.062 seconds**, exit 0, no skips.
The explicit schema audit passed **358 cases**, exit 0, `failures: []`, using
the already-installed **jsonschema 4.26.0** and the schema hash above. The
default suite requires only the standard library. The optional invocation
reports a missing dependency as not run with exit 2; it cannot count that as a
passed or skipped audit. No dependency was installed or added.

Next: root integrates this maintained test into the complete source snapshot
and runs the repository gates before publication. Later runtime owners must
qualify R2–R6 independently against the frozen numerical contract. Keep the
original schema failure and the repair evidence when subsequent schema or
admission changes create a new tested identity.
