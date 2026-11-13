# Assignment 32 - independent chapel transcription B

Actual worker: `/root/w06_a32_chapel_source_b`; wave 6, assignment 32 of this
session's requested sixty. Owned only
`data/registrations/review-b-chapel.csv`,
`docs/research/CHAPEL_PRESETS_SOURCE_B.md`, and this note. No core, UI, CMake,
shared status, assignment ledger or commit was changed by this worker.

## Basis and exact source

Read the standing instructions, M0-M9 plan, remaining M3/source contract,
standalone scope and active status/next steps. The bounded assignment is a
second independent import of the atlas table; it does not complete the broader
factory-source or physical preset gates. Starting HEAD was
`219821dfaca6bfee8ba0905993ed8deec7a66396`, tree
`f2db7aee1d45a897273e4e68a2fefc6a2de4d433`, with other workers' unfinished files.

PDF: `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`; 500 pages; 21,248,265 bytes;
SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
Printed and one-based PDF page 122 are the same numeric locator. The edition
line reads 12 November 2026. Tools: Poppler `pdftoppm` 26.05.0 and Python 3.12.14
on Linux; no new dependency was installed.

Working directory for executed commands:
`/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.

```sh
mkdir -p /workspace/scratch/5ba97739b54c/a32-chapel-source
pdftoppm -f 119 -l 126 -r 120 -png \
  Hammond_B3_Leslie_Research_Atlas_500pp.pdf \
  /workspace/scratch/5ba97739b54c/a32-chapel-source/atlas
sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf
pdfinfo Hammond_B3_Leslie_Research_Atlas_500pp.pdf
pdftoppm -v
python3 --version
```

All eight resulting original-page images were visually inspected. Page 122
was inspected first, and its complete table was entered as literal nine-digit
strings before consulting reading A. The original-page PNG SHA-256 was
`5c4f2e03eca154871f578417f909f992856923cc8f44798e5832a51e10f79f1d`.
The image is reproducible scratch evidence, not a new copy added to the repo.

## Independent freeze and executed comparison

The literal B values were serialized with Python's standard `csv.DictWriter`,
ASCII encoding and LF line endings. Structural assertions required eighteen
rows, nine digits per registration, and every digit in 0-8. The file was hashed
and a freeze record was written to scratch before opening A's CSV or source
guide. The integrator received the freeze identity at that point.

Frozen B CSV SHA-256:
`dc2a8fd4e9750133c982bb42fd6cc7c12908f011154826035bb623f52d8de694`.
The frozen reading was not edited after comparing A.

The post-freeze Python comparison independently required the exact five-column
header and ordered upper/lower C#, D, D#, E, F, F#, G, G#, A key domain; eighteen
unique pairs; nine-character `[0-8]` strings; page 122; and empty unpublished
names. It compared each of the 162 digits with a manual/key/position locator.
It also parsed A's retained footage/color table and compared it with the nine
positions independently read from the original image.

| Executed comparison | Observed result |
| --- | --- |
| Manual/key rows | 18/18 agree, nine per manual |
| Tap digit positions | 162/162 agree; zero discrepancies |
| Ordered footage/color entries | 9/9 agree |
| Leading-zero registrations | 16 in each reading; preserved as strings |
| Unpublished names | All 18 empty in each reading |
| Source locator | All 18 rows identify page 122 |
| CSV bytes and SHA-256 | Identical to A; hash above |

The comparison exited zero and wrote `../a32-chapel-source/comparison.json`.
After the independent freeze and comparison, supplementary page text was
extracted with `pdftotext -f 119 -l 126 -layout`; it did not supply the numeric
transcription. Final checks rehashed both CSVs, checked owned Markdown links
and whitespace, and confirmed the two owned reports remain within 120 lines.

## Handoff and limits

The [source guide](../../research/CHAPEL_PRESETS_SOURCE_B.md) records all nine
physical positions, the absent-name policy and the interpretation limits.
No transcription disagreement or production defect was found. Both reviewers
read the same atlas; this is not a second underlying documentary source. Direct
inspection of the cited factory Table IV printed page 4-1 remains unperformed.

Next: a strict, versioned matrix/compiler admission with both reviewed CSVs and
immutable source identity, followed separately by a nominal selector contract,
state migration, held-key/percussion behavior tests and actual primary-source
comparison. Physical latch overlap, contact resistance, loaded transformer
gains, specimen wiring and acquired transition behavior remain unqualified.
Root accepts the result, updates shared records, commits and publishes it.
