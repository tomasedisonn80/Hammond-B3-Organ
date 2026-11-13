# Assignment 31 - independent chapel source transcription A

Actual worker: `/root/w06_a31_chapel_source_a`; wave 6, assignment 31 of the
standalone session's requested sixty. Owned only:

- `data/registrations/review-a-chapel.csv`
- `docs/research/CHAPEL_PRESETS_SOURCE_A.md`
- This assignment note.

Read AGENTS, current status/next steps/handoffs, PLAN, atlas review, standalone
scope and remaining M3 contract. Root was integrating a concurrent remote rotary
review: initial observed HEAD `463c1479a1ae5551f09fc697c0995a4a00b4092e`, tree
`1ec01f2c53bae0e13e62e0a40134f74e477ddbf0`; the shared worktree had unrelated
changes. Those revisions identify context, not a whole-tree test by this worker.
No shared status, ledger, CMake, production code or other worker files were edited.

## Source work and independent freeze

Read complete atlas pages 119-126 and inspected the original rendered page 122
at 1556 by 2200 pixels. Manually entered the complete upper column, then complete
lower column, keeping the nine source key labels and all leading zeros. No other
worker transcription was opened before or after this freeze. Numerical authority
was the actual page image; the extracted text was supplementary.

The unchanged PDF has 500 pages and 21,248,265 bytes, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
Edition: 12 November 2026; this review: 13 November 2026. Numerical locator is
chapter 019, printed/PDF page 122. The source guide preserves the ordered footages,
lead colors and pp121-126 behavior/evidence boundaries.

The requested CSV name field is not supported by p122: the table prints keys and
tap numbers only. Reported that discrepancy to root before writing; retained
empty `preset_name` values instead of invented names. Atlas p122's own Table IV
comparison is a source claim, not an independent factory-manual check executed
by this assignment. A second atlas import cannot by itself close that distinction.

Frozen CSV SHA-256:
`dc2a8fd4e9750133c982bb42fd6cc7c12908f011154826035bb623f52d8de694`.
Notified root of the freeze and that no competing transcription had been read,
before another reader's subsequent comparison. No speculative gains or runtime
registration behavior were introduced.

## Commands and checks

Working directory: `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.
Linux, Python 3.12.14, Poppler `pdftoppm` 26.05.0. Scratch outputs were retained
under `../a31-chapel/`, not added to the product or numerical CSV.

```sh
mkdir -p ../a31-chapel
pdftotext -f 119 -l 126 -layout \
  Hammond_B3_Leslie_Research_Atlas_500pp.pdf ../a31-chapel/pages-119-126.txt
pdftoppm -f 122 -l 122 -scale-to 2200 -png -singlefile \
  Hammond_B3_Leslie_Research_Atlas_500pp.pdf ../a31-chapel/page-122
sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf
pdfinfo Hammond_B3_Leslie_Research_Atlas_500pp.pdf
```

Inspected the PNG through `view_image`. Its SHA-256 is
`dd4abdb5ffbad5c3d2f5b8d21efbb731b593978ad4e0accd3cbaf3979ae88f21`.
This identifies the exact viewed rendering; it is reproducible scratch evidence,
not a newly acquired original document.

Python `csv.DictReader` checked the literal five-column header, exactly 18 unique
ordered manual/key pairs, nine records per manual, nine digits per string in
0-8, all page values 122, 162 total positions, 16 rows retaining leading zeros,
and all 18 absent-name fields. Supplementary extracted text contains every
visually transcribed string. Results passed and are retained in scratch
`validation.json`. That same-PDF extraction is not an independent oracle.

No compile, audio, physical capture or runtime test was appropriate for this
read-only-source/data import. No project failure occurred. The environment's
runtime skill package was unavailable on this child; the PDF skill was read and
the already-installed Poppler/Python tools completed all requested operations.

## Handoff

Root should compare this frozen file with the other independently frozen review,
record all 162 comparisons, then decide the strict compiler/profile contract.
Keep missing names, primary-manual verification and specimen applicability
explicit. Any later preset runtime must preserve current 45 public controls,
state formats, inactive banks, held-key/source history and percussion policy
until a separate compatible change is implemented and tested. Physical multiple
latches and loaded transformer/percussion transitions remain their own gates.
The [source guide](../../research/CHAPEL_PRESETS_SOURCE_A.md) states those limits.
Root owns final acceptance, shared documentation, commit and guarded publication.
