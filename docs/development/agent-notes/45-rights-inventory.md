# Agent 45 - rights and dependency inventory

Wave 08; actual assignment 45/60; reviewed 2026-11-13 UTC.
Scope: documentation only, from shared `main` working tree based on `7c2ad20`.
Owned files: `THIRD_PARTY_NOTICES.md`, `docs/DEPENDENCIES_AND_RIGHTS.md`, this note.

## Inputs and actual inspection

- Read `AGENTS.md`, README, status/next steps/latest development log, plan,
  atlas review, `docs/research/RIGHTS_AND_SOURCES.md` (the existing rights file),
  atlas pp. 475-480, CI/workflow, CMake and offline-install contract.
- Read source manifest, both factory review procedures, factory comparison and
  provenance manifest, nominal/proposed data and planned capture example.
- Inspected tracked plus proposed nonignored paths, C++ include names, Python
  AST imports and CMake dependency/link/install statements. Only standard-library
  imports and project-local `analyze_wav` were found; no external audio/GUI/SDK
  runtime dependency, package fetch or vendored library tree was found.
- Rehashed the supplied atlas and all four CSVs: bytes and SHA-256 match the
  retained source/comparison records. The atlas is the only PDF/image/audio/font
  asset among the reviewed tracked/proposed files. Build/output scratch is a
  different scope, not a source-distribution inventory.

## Primary-source verification

- Inspected `https://prng.di.unimi.it/splitmix.c` through web retrieval and
  compared its constants/shifts with `src/TonewheelBank.cpp`. Vigna's 2015 header
  explicitly supplies a public-domain dedication, permission and disclaimer.
  The notice is retained without assigning that statement to the entire project.
- Web fetches of GitHub license pages were disabled. The GitHub connector then
  successfully fetched only `LICENSE` at each of the three actual workflow pins:
  checkout `3d3c42e5aac5ba805825da76410c181273ba90b1`, setup-python
  `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0`, and upload-artifact
  `cf430e030ddbb5b0abf93d22962f4752f3646cd9`. All state top-level MIT and
  GitHub/contributor copyright. Exact primary URLs are in both deliverables.
- No additional manuals, rendered pages, SDKs or dependency source trees were
  fetched/copied. No future SDK version/license was selected or asserted.

## Result and handoff

- Inventory separates source checkout, eight-file local install, CI-fetched
  actions/toolchains and generated synthetic renders. It records the existing
  SplitMix adaptation and full upstream notice, current standard-library build,
  supplied-atlas unknown rights, new factual CSVs and independent procedures.
- Factory scan stays external; exact edition/revision applicability remains
  unknown. CSV provenance does not establish manual redistribution permission.
  Proposed schemas/data remain separate from absent recovered companions.
- No project `LICENSE` exists; no broad license or ownership choice was made.
  Physical capture permissions remain separate from software/SDK licensing.
- Added a six-item version/hash/source/license/attribution/distribution gate for
  future SDK, GUI/device, runtime, recording, photo/font and final-payload work.
- Current `OfflineTools` install does not stage these notices. Integrator was
  informed; future packaging must carry appropriate notices and inventory the
  exact included runtimes. No install/code/CI/shared-status files changed here.
- A later synthetic demo is planned but was not present at this review. Update
  the inventory's generated-output row when its actual path/hash is retained.

## Validation

`python3 tools/check_repository.py` passed source identity, chapter index,
Markdown links, agent notes and data references. Targeted local-link, final-newline
and whitespace checks passed; all three deliverables have at most 80 lines.
Reviewed the added-file content and baseline tree (only README and supplied PDF).
No behavioral tests were added for this documentation-only change. No commits,
pushes, external messages or subagents were created by this assignment.

Integration note: the coordinator retained upstream attribution and a linked
terms summary in the final notice document; the full wording remains at the
primary source. This does not select a project license.
