# Factory Table III: independent transcription B

Reviewer: Agent 38, wave 07. Review date: 2026-11-13 UTC.
Evidence class: `documented`, transcribed from a factory service-manual scan.
The two CSVs below were frozen before consulting the repository's derived maps,
atlas mapping rules, other transcription, or other reviewers' conclusions.

## Source identity

- Source title from PDF metadata: *Hammond Organ Service Manual - Early Models
  (A,B,C series, B3, A-100, RT, D, G, etc.)*.
- [Supplied source URL](https://medias.audiofanzine.com/files/hammond-service-manual-a-a-100-ba-bc-bcv-bv-b2-b3-c-cv-c2-c2-text-470145.pdf).
- Cached source supplied by the coordinator: `Hammond-factory-service.pdf`;
  220 PDF pages; 7,077,593 bytes.
- Verified SHA-256:
  `ec2ac51f363dcd1ee039f7711acda32fd014e15ad80dcb77ae199545f9130cc9`.
- Source PDF and inspection images remain outside this repository. Neither was
  changed or added to the deliverables.

Page indices in this note are one-based PDF page numbers. The independently
inspected printed footers on PDF pages 155, 156 and 157 read **3-76, 3-77 and
3-78**, respectively. Enlarged footer crops confirmed those readings.

## Model scope and meaning

The top note on PDF page 148, printed 3-69, names **B-3 and C-3** as the models
to which the following troubleshooting information specifically pertains. It
also says that much of the information applies to similar console models in
the manual. This review retains B-3/C-3 applicability; it does not treat that
general statement as a verified mapping for every other console model.

PDF page 154, printed 3-75, paragraphs 3-15 through 3-19 describe locating tones
on the upper and lower manuals and refer to Table III. Table III is titled
"Frequency Numbers Assigned to Keys and Pedals" and occupies PDF pages 155-157.
Its footnote on PDF page 157 explains that the assigned frequency numbers are
arbitrary identifiers for convenience, rather than actual frequency values.
The CSV entries therefore have no Hz units. Key/pedal ordinals, these source
identifiers, physical terminals, MIDI notes and software indices remain distinct.

## Direct inspection regions

The source images supplied for numerical review were
`factory-page-155-large.png`, `factory-page-156-large.png` and
`factory-page-157-large.png`. The first two measure 1099 by 1540 pixels;
the third measures 1120 by 1554 pixels. Coordinates below are approximate
image-pixel regions, with the origin at the upper left. They locate the viewed
printed table, rather than claiming a physical measurement.

| PDF page | Printed page | Region inspected | Transcribed rows |
| --- | --- | --- | --- |
| 155 | 3-76 | Table x=18-1071, y=74-1175; row groups y=210-518, 537-837, 861-1163 | Manual keys 1-36 |
| 156 | 3-77 | Table x=22-1077, y=100-923; row groups y=239-538, 563-863, 883-915 | Manual keys 37-61 |
| 157 | 3-78 | Table x=20-1082, y=103-952; row groups y=239-538, 563-744, 766-893, 914-944 | Pedals 1-25 |
| 157 | 3-78 | Footnote below the table, approximately x=31-1025, y=975-1027 | Identifier interpretation |
| 148 | 3-69 | Top scope note above "Trouble Location" | B-3/C-3 section scope |
| 154 | 3-75 | Right column, paragraphs 3-15 through 3-19 | Manual testing context |

The page 155 and 157 footers were inspected at the lower left; the page 156
footer was inspected at the lower right. Fresh renders of PDF pages 148 and
154 supplied the surrounding section context. PDF page 153 was also opened
while locating that context; it did not supply transcription data.

## CSV contract

- [Manual transcription](../../data/references/review-b-manual.csv): header
  `key,d1,d2,d3,d4,d5,d6,d7,d8,d9`; 61 ordered rows; 549 populated assignments.
- [Pedal transcription](../../data/references/review-b-pedal.csv): header
  `pedal,c1,c2,c3,c4,c5,c6,c7,c8`; 25 ordered rows; 195 populated assignments
  and five empty fields corresponding to printed dashes.
- Identifiers are decimal integers exactly as visually read. An empty pedal
  field preserves a printed dash/disconnection marker. It is not generator zero,
  an interpolated value, or an unreadable numeric cell.
- Column order is the printed order. In particular, pedal `c2` precedes `c3`
  although their printed headings are "3d harm." and "2d harm." respectively.

| Manual column | Printed role | Pedal column | Printed role |
| --- | --- | --- | --- |
| d1 | subfund. | c1 | Fund. |
| d2 | Sub-3d | c2 | 3d harm. |
| d3 | fund. | c3 | 2d harm. |
| d4 | 2d harm. | c4 | 4th harm. |
| d5 | 3d harm. | c5 | 6th harm. |
| d6 | 4th harm. | c6 | 8th harm. |
| d7 | 5th harm. | c7 | 10th harm. |
| d8 | 6th harm. | c8 | 12th harm. |
| d9 | 8th harm. | | |

## Independence and freeze procedure

1. Read `AGENTS.md` and the source images before entering data. Repository status
   and branch inspection listed paths and identifiers without reading map data.
   Potentially contaminating project-context documents were deferred until freeze.
2. Read every numeric cell directly from the three table images and typed the
   two CSVs row by row. No OCR, formula, source offset, interpolation, existing
   profile, or other transcription supplied a numeric cell. Printed repeated
   values and the five dashes were retained as seen.
3. Before freeze, ran only CSV header/shape/order/integer-bound checks and source
   size/hash checks. No cross-review or comparison with derived data was run.
4. Froze the byte identities below and reported both hashes and the uncertainty
   list to the coordinator before reading the required project-context documents.
5. After freeze, inspected enlarged printed footers and the surrounding scope
   note. Text extraction from factory PDF pages 140-154 helped locate the scope
   heading; that extraction was not used for Table III numbers. The required
   repository context and atlas chapters 015 and 022 were read only after freeze.
   The frozen CSVs were not edited after that reading.

| Frozen file | SHA-256 |
| --- | --- |
| `review-b-manual.csv` | `23ade40234db10d0bf99cd5acf9ee0ff29e4656e847e61409ebe8717f7cb9dc6` |
| `review-b-pedal.csv` | `b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1` |

Checks passed: exact requested headers; 61 and 25 data rows; consistent 10 and
9 field widths; consecutive row ordinals; every populated assignment an integer
in 1-91; no empty manual fields; source byte size and SHA-256 match the supplied
identity. These structural checks do not establish agreement with another
transcription. The coordinator assigned that separate comparison to Agent 39.

## Uncertainty and limits

**Uncertain numeric cells: none.** All numeric glyphs were readable in the
supplied images. The complete printed-dash list is pedal 8/c2, 9/c2, 10/c2,
11/c2 and 12/c2. These are intentional empty CSV fields, not unresolved cells.

This is an independent documentary transcription of one identified scan. It
does not establish specimen wiring continuity, manufacturing variation, actual
geared frequencies, tuning, pickup waveforms or levels, contact behavior,
electrical loading, acoustic response, or calibration. It is not a measurement
of an organ. The source title and B-3/C-3 section note do not identify a particular
instrument serial number or AO-28 revision.

The source URL and successful download do not establish a redistribution license.
This work adds the numerical transcription and provenance note only; it grants
no permission to redistribute the source manual or inspection images. No new
runtime behavior, profile modification, physical-fidelity claim, commit, or push
is part of this review.
