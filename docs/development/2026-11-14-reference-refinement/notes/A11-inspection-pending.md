# A11 — Inspection wording and pending boundary

Worker `/root/w02_a11_inspection_pending`, wave 2. Owned only this note and
`docs/REFERENCE_REFINEMENT_INSPECTION.md`; no production edit, commit or push.
Inspected HEAD `8bd999efc13e309b932e6ac41d72ceb7b9b80a5f`, tree
`c37da16cedbb91573476a44bd4eafe5a5e30134a`. Concurrent documentation is preserved;
the inspected production paths had no tracked diff.

Read current AGENTS/scope/checkpoint/manifest, full PLAN, current operational
entries and A01/A02 findings. Reviewed InspectionModel, Session, UiModel,
InstrumentView, main, native CMake, inspection author/acceptance tests, preset
raster fixtures and `capture_standalone_interface.py`.

Finding: observed counts always retain plural units. A one-line unit selection
after the existing observed guard repairs all three rows. Acceptance must cover
0/1/2+/unavailable, retained singular and real multi-owner counting.

The genuine deterministic seam already exists between `post`/`submitted` and
`render(0, {})`. Existing inspection acceptance exercises it, but existing
pending raster fixtures construct applied snapshots. The full-app gallery
requires final acknowledgement. The companion contract specifies a bounded
real-Session/native-painter harness with honest device metadata and separate
capture provenance; it introduces no production audio stall.

Executed from repository root:

```sh
../build-tools/cmake/data/bin/ctest --test-dir ../build-native -R '^test_standalone_inspection_(author|acceptance)$' --output-on-failure --no-tests=error
```

Result: **2/2 existing suites passed, 0.01 seconds** against the root's unchanged
Release baseline. This does not verify the proposed singular repair or new
capture. Documentation whitespace was checked. Next owner implements the
specified repair/tests/harness, rebuilds coherent inputs and retains reviewed
pre-flush/acknowledged captures. Whole-app pending capture, real device timing,
physical fidelity and desktop qualification remain separate.
