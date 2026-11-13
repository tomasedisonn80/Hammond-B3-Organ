# Assignment 23 — reproducible nominal console fixtures

- Agent: `/root/w04_a23_console_fixture_catalog`.
- Date: 2026-11-13 UTC; continuation wave 04.
- Scope: three original console scores, a separate bound catalog, actual-PCM
  acceptance tests and replay documentation. No core, CMake, legacy-catalog,
  shared-status, commit or push changes.
- Reviewed: `AGENTS.md`, current engine/model/rendering and plan contracts,
  prior catalog/examples, and atlas pp. 115, 118, 127, 128, 135, 137 and 447.
  This is a focused implementation review, not another claimed full-PDF reading.

## Deliverables and decisions

The new `examples/fixtures/console-catalog-v1.json` is separate from the existing
five-fixture `catalog-v1.json`. Its schema version identifies this catalog, not
the renderer or evidence-manifest schema. All three renders require renderer
schema 2 with source `ideal-shared-sine-v1`, contacts
`nominal-linear-travel-v1` and percussion `shared-readiness-v1`.

| Score | Scope | Frames at 48 kHz | Seed |
| --- | --- | ---: | ---: |
| `console-travel-v1.events` | Separate upper/lower A4 contact travel, velocity-independent level and continuous shared phase | 14400 | 2623 |
| `console-percussion-legato-v1.events` | Shared fast decay across a joining C5, elapsed release recovery and another A4 attack | 42000 | 2624 |
| `console-routing-mask-v1.events` | Held-key A/B/Cancel, edit while cancelled, upper-only one-foot masking, retained B setting and lower independence | 38400 | 2625 |

The scores total 1.975 seconds per partition. Each explicitly sets normalized
expression to 0.5. The first exploratory render exposed that the retained source
profile's full expression branch amplitude is 0.03; adding the explicit 0.5
control made the intended 0.015 branch baseline concrete. No engine change or
unreported output normalization was used to satisfy the assertions.

The catalog retains score hashes, source profile identity, model IDs, invocation
controls, frames/rate/seed/registration, bounded windows and numeric tolerances.
It explicitly labels the gestures and thresholds as synthetic/proposed. The
source profile canonical authoring hash remains
`49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`;
compiled profile SHA-256 remains
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.

### Independent acceptance method

`tests/test_console_catalog.py` validates bounded JSON/profile/score identities,
event grammar, timing and score counts before launching the actual C++ renderer.
Missing build prerequisites fail explicitly; no checks are skipped or replaced
with a mocked renderer. It renders every score at block sizes 1, 127 and 1024,
requiring byte-identical WAVs within that build, valid PCM16 stereo, identical dry
channels, no clipping, finite float metrics and agreement with serialized PCM.

It checks exact silent regions and meaningful audible peaks. The 8-foot contact
edges use an independent analytic calculation from the declared thresholds and
full-travel durations: upper make/break 160/6438, lower 7126/13447. Adjacent PCM
samples must expose those exact transitions; the chosen seeds give nonzero
samples on each audible side.

Thirteen regression windows fit 21 tone components using absolute-frame
sine/cosine bases. Independent closed-form elapsed-time exponentials describe
the declared detector/route history rather than replaying the engine's readiness
recurrence. This tests a joining note without a new envelope, finite recovery,
and phase continuity after release or route changes. The routing fixture checks
880 Hz percussion is absent in A/Cancel/off windows and the 3520 Hz one-foot
component is 0.015 for lower only or 0.03 when both retained branches sound.
The source phase PRNG and production evidence validators are not imported.

The reviewed limits are maximum fit residual 2 PCM16 units, component peak error
0.00004, and normalized phase-vector distance 0.006. They are software acceptance
criteria, not physical measurement uncertainty. The fit uses a bounded two-tone
least-squares system with partial pivoting; no third-party numerical dependency.

## Observed verification

The initial direct invocation against the integrated Release renderer passed
**4/4 methods in 0.713 s**, executing nine actual render processes.

An isolated strict Release build used GCC 14.2.0 and Python 3.12.14:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S . -B /workspace/scratch/60e8291da354/a23-console-build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a23-console-build \
  --target hammond_render -j 4
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a23-console-build \
  -R '^python_test_console_catalog$' --output-on-failure
```

The CTest-discovered suite passed **1/1 in 0.99 s**, proving its prerequisite
environment is supplied by the existing CMake discovery. A separate numeric
report using the same independent regression produced:

| Fixture | Actual float peak | Actual float RMS | Maximum residual, PCM units |
| --- | ---: | ---: | ---: |
| Travel | 0.014999974519014359 | 0.009922471939366217 | 0.5124918392154427 |
| Percussion legato | 0.02311086840927601 | 0.010041421951160305 | 0.5141091946453713 |
| Routing/mask | 0.029997941106557846 | 0.014766988701836972 | 0.5268236799037709 |

The observed renderer executable SHA-256 is
`b9c0acab7615820091bd7baaf782d894a8b85bb910a2dfba72b84463445d74c9`.
This identifies the tested local integration binary, not a portable release or
cross-compiler byte identity guarantee. The catalog retains the final score
hashes; the original five fixture files/catalog/tests have no scoped diff.
Assigned-file `git diff --check` passed.

## Changed files

- `examples/fixtures/console-catalog-v1.json`
- `examples/fixtures/console-travel-v1.events`
- `examples/fixtures/console-percussion-legato-v1.events`
- `examples/fixtures/console-routing-mask-v1.events`
- `tests/test_console_catalog.py`
- `examples/README.md` — appended console explanation and complete replay commands.
- This assignment note.

## Limitations and handoff

No generated WAV is committed. Reproduction uses the exact bound inputs and the
built renderer. These tests qualify short nominal behaviors only. Contact edges
are sample-grid binary switches without bounce/antialiasing; the shared readiness
model is not a complete AO-28 circuit. Physical preset loading, loaded expression,
pedal audio, scanner, Leslie, native hosts and instrument calibration remain open.

Root should include these seven files in the combined staged checkpoint, run the
full suite and observe the hosted matrix before publication claims. A later
packaging assignment must explicitly add this separate catalog and its three
scores if they should accompany the existing OfflineTools install. The current
install list was deliberately not changed by this scoped assignment. The next
evidence integration should replay these exact options into schema-2 bundles and
check them with the independent verifier; direct PCM/catalog qualification does
not substitute for bundle integrity qualification.


The first combined full gate passed 29/30 suites. The historical catalog
deliberately accounts for every top-level `.events` file. Root preserved that assertion and all five
legacy fixtures by moving the three new scores and their catalog into
`examples/fixtures/console/`. Their bytes/hashes are unchanged; current replay
commands and the new test use the new location. The console catalog now also
rejects unlisted `.events` files in its own directory. The assignment23 note retains its
original pre-integration path listing.
