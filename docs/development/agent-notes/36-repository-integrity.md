# Agent 36 — source-archive repository integrity

## Assignment and boundary

Wave 06 / Agent 36 owns `tools/check_repository.py`, its Python mutation suite,
`docs/REPOSITORY_CHECKS.md` and this note. Read AGENTS, README, status/next-step/
plan/log, atlas review, source manifest, reconstructed index, existing profile/
pedal/catalog contracts and related review notes. Preserved concurrent changes.
No source PDF, shared status, build configuration or other agents' files edited.
No network, dependency additions, commits, pushes or delegated agents.

## Implemented

- Standard-library read-only CLI/API with independent check groups, readable or
  JSON results, bounded reads/inventory/parsing and nonzero mismatch status.
- Streamed source byte-length/SHA-256 agreement with the manifest; declared
  500-page identity and consistent source references across existing contracts.
- Reconstructed index: front matter 1–12, 80 six-page chapters 13–492, directory
  493–500, chapter/contents IDs, ten research waves, complete disjoint review
  coverage and existing chapter review notes with matching page coverage.
- Actual local Markdown destinations with source file/line errors; skips external
  links, fenced examples, inline code, comments and ordinary path mentions.
- Unique canonical positive agent-note filename IDs. Default permits progress
  gaps; explicit `--expected-agents N` requires the exact ID set 1..N.
- Existing nominal profile/pedal/schema atlas references, fixture authoring path,
  canonical profile identity and exact event-file hashes. No generic `path`
  policy, absent factory-manual requirement or fabricated measurement gate.
- Source-only Markdown scope; build/output/dependency trees are not traversed.

## Executed evidence

```sh
python3 -B tools/check_repository.py --json
python3 -B tests/test_repository_integrity.py -v
```

Initial smoke passed: source 21,248,265 bytes, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`,
all 500 indexed pages / 80 chapters / six review ranges / ten research waves,
five event-file hashes and canonical authoring identity. No pre-existing broken
Markdown targets were observed. Default accepted the then-present IDs 1..35.

Initial direct suite passed 39 unittest methods in 0.644 s with no skips. Cases
include changed/missing source, wrong manifest length, gap/overlap/missing chapter,
wrong note/source locators, missing/wrong/reference/image links, ignored examples,
duplicate/invalid/gapped notes, changed data/hash/path, strict JSON and resource
bounds. Tiny mutation sources avoid 21 MB copies; only the real smoke reads the
supplied PDF. CLI tests passed with Git absent from PATH and unchanged archive
contents/inventory, and verified nonzero structured failures.

Native CMake configured Release in `../agent36-integrity` without building any
renderer/profile. Its auto-discovered `python_test_repository_integrity` target
passed under Python 3.12.14 (39 methods / 0.78 s CTest wall time). The explicit
`--expected-agents 36 --json` smoke then passed all IDs 1..36 and 117 local links
across 67 Markdown files. `git diff --check` on assigned paths passed. Final
review added missing-field/omitted-profile-ID regressions and root `/` support.
Final CTest rerun passed all 41 methods in 0.645 s (0.80 s CTest wall time).
Default smoke also passed after wave 07 added IDs 37/38: 119 local links in 70
Markdown files. A stale explicit count of 36 correctly failed when ID 37 arrived;
default progress checks stayed green. Syntax and whitespace checks passed.

## Limitations and handoff

This verifies agreement with retained metadata, not source authenticity, rights,
review truth or physical fidelity. It validates declared PDF/index coverage but
does not decode the PDF page tree or independently reread its pages/titles.
The generated compiled-profile digest remains with compiler/catalog build tests;
no build artifacts are needed. This is a focused Markdown reader, not complete
CommonMark/HTML or anchor validation. Concurrent changes require a rerun; the
checker is not an atomic or adversarial filesystem-snapshot verifier.

Linux execution is the observed platform scope; native Windows/macOS execution
remains the integrating CI's responsibility. The integrator owns shared handoff
files, final expected-agent count, integration results and publication.
