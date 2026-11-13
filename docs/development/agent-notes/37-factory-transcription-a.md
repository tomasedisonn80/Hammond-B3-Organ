# Agent 37 - independent factory transcription A

Date: 2026-11-13. Assignment: wave 07, Table III review A.

## Delivered

- `data/references/review-a-manual.csv`: 61 rows, nine assignments per key.
- `data/references/review-a-pedal.csv`: 25 rows, eight printed columns per pedal.
- `docs/research/FACTORY_REVIEW_A.md`: source, scope, locators, procedure and limits.
- This handoff. No shared status, source, active data, code, or review B edits.

## Independence and source

Read AGENTS.md and project guidance for scope. Did not open existing profile or
pedal numeric tables, generated mapping code, or B files before freezing.
Every CSV value was entered literally from visual inspection of PDF pages
155-157; no formula or OCR numeric extraction produced the entries.

Source: the coordinator's 220-page factory scan from Audiofanzine.
Verified size: 7,077,593 bytes.
Source SHA-256:
`ec2ac51f363dcd1ee039f7711acda32fd014e15ad80dcb77ae199545f9130cc9`.

Printed table folios are 3-76/3-77/3-78, directly verified from images.
The assignment's initial 3-16/3-17/3-18 locators were corrected with root informed.
PDF 148 / printed 3-69 explicitly limits the following service information to
B-3/C-3, with qualified possible applicability to similar console models.
PDF 154 / printed 3-75 connects Table III to upper and lower manual checks.
Exact factory edition/date and production-revision coverage remain unestablished.

## Frozen identities

Reported to root before any B or derived-model comparison; no subsequent CSV edit.

- Manual: 1,852 bytes; SHA-256
  `23ade40234db10d0bf99cd5acf9ee0ff29e4656e847e61409ebe8717f7cb9dc6`.
- Pedal: 677 bytes; SHA-256
  `b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1`.

## Executed checks

`sha256sum` and `pdfinfo`: source identity, size and page count verified.
`pdftoppm`: rendered contextual PDF pages 148 and 154 outside the repository.
Direct image review: full Table III and surrounding applicability text.
Python `csv`/`hashlib`: exact headers, row widths, ordered identities, integer
syntax, 1-91 bounds, LF/final newline and raw hashes all passed.
Manual: 549 numeric cells, no empty cells, observed range 13-91.
Pedal: 195 numeric cells, range 1-68; five empty cells at c2, pedals 8-12.
No unresolved printed glyphs or uncertain cells remain in this reading.

## Limits and next owner

Evidence is documented factory assignment data, not specimen measurements.
Frequency numbers remain dimensionless identifiers; no measured tuning, amplitude,
physical contact order, or terminal correspondence was inferred.
No source PDF or images were added to the repository; no redistribution license
or factory-edition authenticity was established.
Agent 39 owns independent comparison and disagreement resolution.
No commits, pushes, subagents, physical tests, or model comparisons were performed.
