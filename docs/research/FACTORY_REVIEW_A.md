# Factory Table III: independent transcription A

## Result and evidence class

Reviewer: Agent 37, wave 07; review date: 2026-11-13.
This review directly transcribed every printed assignment in factory Table III:
61 manual keys by nine drawbar columns and 25 pedals by eight printed harmonic
columns. The retained CSVs contain 744 numbers and five explicit empty cells.
All printed values were legible; there are **no unresolved cells** in review A.

The evidence class is **documented**. These are dimensionless factory frequency
numbers, not measured hertz, amplitudes, phases, contact timings, MIDI numbers,
storage indices, or an independently established physical-terminal numbering map.
The footnote below the pedal table describes the frequency numbers as arbitrary
identifiers rather than actual frequency values [S1, PDF p. 157 / printed 3-78].
No specimen was examined or measured. Table transcription cannot establish the
wiring, calibration, condition, or fidelity of a particular surviving instrument.

## Source identity and edition limits

**[S1]** Factory service-manual scan supplied by the integrating agent, with PDF
metadata title *Hammond Organ Service Manual - Early Models (A,B,C series, B3,
A-100, RT, D, G, etc.)*.

- Source URL: <https://medias.audiofanzine.com/files/hammond-service-manual-a-a-100-ba-bc-bcv-bv-b2-b3-c-cv-c2-c2-text-470145.pdf>
- Length: 220 PDF pages; file size: **7,077,593 bytes**.
- Raw PDF SHA-256: `ec2ac51f363dcd1ee039f7711acda32fd014e15ad80dcb77ae199545f9130cc9`.
- Both size and hash were independently checked against the supplied local PDF.
- The PDF metadata identifies Internet Archive digitization and a 2009 creation
  timestamp. Those are scan metadata, not evidence of the factory publication
  date, edition, authenticity, or permission to redistribute the scan.
- The exact factory edition/print date and applicable production revisions are
  **unestablished by this review**. The filename's model list is not used to
  expand the table's scope.

The opening note of **Trouble Location**, PDF p. 148 / printed **3-69**, states
that the following information specifically concerns **B-3 and C-3**. It then
qualifies possible use for other console models by their similarity. Accordingly,
this transcription retains B-3/C-3 applicability; it does not certify the same
assignments for A-100, RT/RT-2/RT-3, early consoles, or every production revision.
The contextual page was visually inspected, including its heading and note [S1].

PDF p. 154 / printed **3-75**, right column, paragraphs 3-14 through 3-19,
introduces the defective-tone checks and explicitly points to Table III for
key/drawbar frequency assignments. Paragraph 3-19 repeats the checks on the
lower manual. This connects the manual table to both manuals in the stated
B-3/C-3 service context; it is not a statement about measured output levels [S1].

## Page and region locators

PDF page numbers below are one-based. Printed folios were read from the images;
they are **3-76, 3-77, and 3-78**, not 3-16, 3-17, and 3-18.

| Source region | Directly transcribed content | CSV rows |
|---|---|---|
| PDF 155 / printed 3-76, Table III, upper data block | Manual keys 1-12, all nine drawbar columns | `review-a-manual.csv`, keys 1-12 |
| PDF 155 / printed 3-76, middle data block | Manual keys 13-24, all nine columns | keys 13-24 |
| PDF 155 / printed 3-76, lower data block | Manual keys 25-36, all nine columns | keys 25-36 |
| PDF 156 / printed 3-77, continuation, upper data block | Manual keys 37-48, all nine columns | keys 37-48 |
| PDF 156 / printed 3-77, middle data block | Manual keys 49-60, all nine columns | keys 49-60 |
| PDF 156 / printed 3-77, isolated final row | Manual key 61, all nine columns | key 61 |
| PDF 157 / printed 3-78, continuation, upper data block | Pedals 1-12, all eight columns, including five dashes | `review-a-pedal.csv`, pedals 1-12 |
| PDF 157 / printed 3-78, second data block | Pedals 13-19, all eight columns | pedals 13-19 |
| PDF 157 / printed 3-78, third data block | Pedals 20-24, all eight columns | pedals 20-24 |
| PDF 157 / printed 3-78, isolated final row | Pedal 25, all eight columns | pedal 25 |
| PDF 157 / printed 3-78, text immediately below the table | Frequency-number footnote | Identifier interpretation only |

## Column and empty-cell conventions

The key/pedal numbers are the printed row identities, beginning at one.
The printed note-name column is omitted from the requested CSV schema; it was
used as a visual alignment aid, without conversion to MIDI or octaves.

| CSV | Columns, in the source's left-to-right order |
|---|---|
| Manual `d1` through `d9` | subfundamental; sub-third; fundamental; second; third; fourth; fifth; sixth; eighth harmonic |
| Pedal `c1` through `c8` | fundamental; third; second; fourth; sixth; eighth; tenth; twelfth harmonic |

The pedal third-harmonic column precedes its second-harmonic column in the scan;
the CSV preserves that order. The `c` labels are positional table columns and do
not independently establish a physical contact sequence.

The printed dashes at pedal rows **8, 9, 10, 11, and 12**, column **c2**, are
represented by empty CSV cells. They mean the table prints no assignment there,
retained as the requested disconnection representation. They are not zeros,
unreadable glyphs, inferred frequencies, or values filled from a formula.

## Independent procedure and freeze

1. Read repository guidance and project scope without opening the current
   profile/pedal numeric tables, generated mapping code, or review B files.
2. Verify the supplied PDF's bytes and SHA-256; inspect the three table images
   directly. Inspect surrounding service text for applicability and meaning.
3. Enter each printed value as a literal CSV field, reading every row and column.
   No routing formula, recurrence, octave rule, OCR numeric output, or existing
   project table generated or supplied the entries.
4. Review the literal entries against the displayed source rows and preserve
   each printed dash as an empty field.
5. Validate only the two review A files and source identity: headers, row widths,
   contiguous ordered identities, integer syntax, bounds, and empty positions.
   These checks did not compare the table to the project's derived model.
6. Compute raw-byte hashes and report them to the integrator as the freeze
   identity **before any B or derived-model comparison**. The frozen CSVs were
   not altered afterward. Agent 39 owns comparison and any disagreement process.

### Frozen artifacts and structural validation

| File | Raw bytes | Raw SHA-256 |
|---|---:|---|
| `data/references/review-a-manual.csv` | 1,852 | `23ade40234db10d0bf99cd5acf9ee0ff29e4656e847e61409ebe8717f7cb9dc6` |
| `data/references/review-a-pedal.csv` | 677 | `b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1` |

Python standard-library `csv` and `hashlib` checks passed. Manual data has
61 ordered rows, ten fields per row, 549 assigned cells, no empties, and observed
identifier range 13-91. Pedal data has 25 ordered rows, nine fields per row,
195 assigned cells, the five specified empties, and observed identifier range
1-68. All numeric entries satisfy the checked integer bound 1-91. Both files
use LF line endings and a final newline. Source byte count and hash match S1.
Shape and range checks establish structural validity, not transcription accuracy
or agreement with another model; independent comparison is a separate activity.

## Rights, scope, and handoff

Only factual assignment transcriptions and this original review record are
added to the repository. The source PDF, rendered pages, and contextual images
remain outside it and are not redistributed by this task. Public availability
and scan metadata are not treated as a redistribution license. No additional
rights determination or permission acquisition was performed.

Agent 37 changed only the two review A CSVs, this note, and the assigned agent
handoff. It did not change source material, active profile data, generated code,
shared status files, or review B. It made no commit or push. Follow-on reviewers
must retain the frozen identities and report disagreements with precise cells
and source locators rather than silently replacing an independent reading.
