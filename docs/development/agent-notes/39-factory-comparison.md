# Agent 39 — factory Table III comparison

Wave 07, 2026-11-13. Read AGENTS.md, project/status/plan/research context,
review A/B notes, the relevant atlas mapping context and the existing data/compiler.
Both independent readings were frozen before this comparison began.

## Delivered

- data/references/factory-table-iii.json: collateral comparison/provenance
  manifest, not an atlas companion recovery or replacement numeric table.
- tools/validate_factory_reference.py: bounded, read-only stdlib validator.
- tests/test_factory_reference.py: 20 meaningful mutation/integration methods.
- docs/FACTORY_REFERENCE.md: scope, identities, commands and versioned next path.

## Actual results

All 549 manual assignments match A/B and each reading matches the profile.
All 200 pedal positions match A/B and each reading matches data/pedal-map.json:
195 connections plus five nulls, precisely pedals 8, 9, 10, 11 and 12 at c2.
No discrepancy, unresolved cell or correction; correction_history remains empty.
Compiled output also matches all 549 manual assignments from each reading.

Verified raw CSV identities (both A and B):

- Manual: 1,852 bytes;
  23ade40234db10d0bf99cd5acf9ee0ff29e4656e847e61409ebe8717f7cb9dc6.
- Pedal: 677 bytes;
  b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1.

Verified source: 7,077,593 bytes, 220 pages by pdfinfo;
ec2ac51f363dcd1ee039f7711acda32fd014e15ad80dcb77ae199545f9130cc9.
Inspected source images: B-3/C-3 scope at PDF148/printed3-69; manuals at
PDF155-156/printed3-76–3-77; pedal table at PDF157/printed3-78, including all dashes.
The source PDF and rendered images remain outside the repository.

Preserved nominal profile raw/canonical hashes:

- Raw: d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff.
- Canonical: 49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83.
- Compiled, 4,545 bytes:
  b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f.

## Checks run

- Validator default run: pass; explicitly reports source bytes not checked.
- Validator with external source-review/Hammond-factory-service.pdf: pass.
- python3 tests/test_factory_reference.py: 20/20 passed.
- python3 tests/test_pedal_map.py: 15/15 passed.
- python3 tests/test_compile_profile.py: 37/37 passed.
- Native CMake configured /workspace/scratch/c871510c69b2/factory-comparison-check.
- CTest selected python_test_factory_reference: 1/1 passed, 0.39 s.
- git diff --check: passed at the validation checkpoint.

Mutation checks cover first/last and foldback cells, all five nulls individually,
moved-null/count-preserving errors, coordinated A/B/target tampering, exact
metadata/locators, shapes/order/types, duplicate/nonfinite/oversized/deep input,
source identity, CLI failures and bounded exact-cell diagnostics.

## Handoff and limits

Original independent_factory_verification=false and pedal transcription="missing"
remain original authoring provenance. The separate later attestation identifies
their exact digests; any authoring integration needs a new version and explicit
compiler/schema/migration support. No source gearing, tuning, calibration,
specimen continuity, pedal audio, percussion or physical fidelity was established.
Scope is one identified B-3/C-3 documentary table; edition/revision remain unknown.
No frozen transcription, existing authoring data/compiler, shared status or
runtime file was changed. No commit, push or subagent was made.
