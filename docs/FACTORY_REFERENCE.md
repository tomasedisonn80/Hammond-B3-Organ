# Factory Table III comparison, version 1

**Result, 2026-11-13:** two independently frozen direct-image transcriptions agree
on **all 549 manual assignments and all 200 pedal positions**. Each transcription
also agrees, cell for cell, with the identified existing project data. The pedal
comparison includes **195 connected assignments and all five disconnections**.
No discrepancy or correction was required.

This is later **documentary routing evidence** for exact retained data digests.
It establishes agreement with one identified factory-manual scan. It does not
measure an instrument, establish manufacturing revisions, or verify tuning,
gearing, amplitude, phase, loading, contacts, percussion, pedal audio or acoustic
fidelity. The original nominal authoring data and compiler remain unchanged.

## Retained evidence and independence

- [Review A](research/FACTORY_REVIEW_A.md), Agent 37:
  [manual CSV](../data/references/review-a-manual.csv) and
  [pedal CSV](../data/references/review-a-pedal.csv).
- [Review B](research/FACTORY_REVIEW_B.md), Agent 38:
  [manual CSV](../data/references/review-b-manual.csv) and
  [pedal CSV](../data/references/review-b-pedal.csv).
- [Comparison manifest](../data/references/factory-table-iii.json), Agent 39:
  source identity, page locators, column meanings, frozen input identities,
  exact comparison scope and explicit claim limits.
- [Validator](../tools/validate_factory_reference.py) and
  [mutation tests](../tests/test_factory_reference.py).

The two reviewers read the source images and entered literal cells independently.
They froze and reported their raw CSV hashes before consulting each other or the
derived maps. Their retained notes describe the procedure and uncertainties.
The comparator began after both freezes. Identical hashes establish identical
retained bytes; independence rests on those recorded review procedures, not on
the hashes themselves.

The manifest is a new comparison/provenance record. It contains no replacement
numeric matrix and does not recover the atlas's absent companion JSON. No formula
or generated routing table supplies its reference cells. The four CSVs remain the
independently entered numerical evidence.

## Source identity, applicability and locators

The scan's metadata title is *Hammond Organ Service Manual - Early Models
(A,B,C series, B3, A-100, RT, D, G, etc.)*. Its
[source URL](https://medias.audiofanzine.com/files/hammond-service-manual-a-a-100-ba-bc-bcv-bv-b2-b3-c-cv-c2-c2-text-470145.pdf)
identifies the acquired scan. The cached PDF has **220 pages, 7,077,593 bytes**,
and raw SHA-256:

    ec2ac51f363dcd1ee039f7711acda32fd014e15ad80dcb77ae199545f9130cc9

Agent 39 independently checked the supplied file's raw identity and inspected
its metadata/page count with pdfinfo. The service section's opening note
explicitly concerns B-3/C-3. The broad metadata title does not extend this
attestation to every model in that title. Exact factory edition, print date and
applicable production revisions remain unestablished. Scan creation metadata is
not a factory publication date. Source PDF and rendered images stay outside the
repository; public availability does not establish redistribution permission.

| Subject | One-based PDF page | Printed folio | Source region |
| --- | ---: | --- | --- |
| B-3/C-3 applicability | 148 | 3-69 | Opening note above Trouble Location |
| Upper/lower manual context | 154 | 3-75 | Right column, paragraphs 3-15 through 3-19 |
| Manual keys 1-36, all nine columns | 155 | 3-76 | Table III, three 12-key blocks |
| Manual keys 37-61, all nine columns | 156 | 3-77 | Table III continuation, two blocks and final row |
| Pedals 1-25, all eight columns | 157 | 3-78 | Table III continuation, all four row groups |
| Meaning of frequency numbers | 157 | 3-78 | Footnote immediately below the table |

The printed folios are **3-76, 3-77 and 3-78**, as visually checked by both
transcribers and the comparator. The entries are dimensionless factory
frequency-number identifiers. They are not hertz, physical terminal numbers,
MIDI notes or zero-based storage indices. The manual context applies the
assignments to both manuals; it does not establish output levels.

## Column order, shapes and disconnects

| Table | Retained order | Project comparison |
| --- | --- | --- |
| Manual, 61 rows × 9 columns | d1 subfundamental; d2 sub-third; d3 fundamental; d4 second; d5 third; d6 fourth; d7 fifth; d8 sixth; d9 eighth | manual_map.tone_ids, in the declared nine-drawbar order |
| Pedal, 25 rows × 8 columns | c1 fundamental; c2 third; c3 second; c4 fourth; c5 sixth; c6 eighth; c7 tenth; c8 twelfth | Ordered rows[].sources, with the existing project column names |

CSV row identities are one-based and consecutive. Manual CSVs contain 549 integer
assignments in 13-91, with no empty fields. Pedal CSVs contain 195 integer
assignments in 1-68, within the declared source domain 1-91. Their five empty
fields preserve printed dashes and compare to JSON null, never source zero:

| Pedal row | CSV column | JSON source index | Factory locator |
| ---: | --- | ---: | --- |
| 8 | c2 | 1 | PDF 157 / printed 3-78, upper block |
| 9 | c2 | 1 | PDF 157 / printed 3-78, upper block |
| 10 | c2 | 1 | PDF 157 / printed 3-78, upper block |
| 11 | c2 | 1 | PDF 157 / printed 3-78, upper block |
| 12 | c2 | 1 | PDF 157 / printed 3-78, upper block |

Agent 39 visually checked these dashes against the supplied pedal image.
The printed third-harmonic column precedes the second-harmonic column. Positional
column correspondence does not independently establish a physical contact sequence,
wire colors, bus membership or electrical mixture topology.

## Frozen identities and actual comparison

| Artifact | Raw bytes | Raw SHA-256 |
| --- | ---: | --- |
| Review A manual and review B manual, each | 1,852 | 23ade40234db10d0bf99cd5acf9ee0ff29e4656e847e61409ebe8717f7cb9dc6 |
| Review A pedal and review B pedal, each | 677 | b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1 |
| nominal-unmeasured-v1.json | 19,627 | d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff |
| pedal-map.json | 3,267 | 58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd |

The profile's unchanged canonical authoring SHA-256 is:

    49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83

The pedal JSON canonical SHA-256 is:

    7b2631a0c7d55a18f8225d4ee420e472c23b9f2809eec69865474eafce6f5fb2

Canonical bytes use the existing project's sorted-key, compact-separator,
UTF-8 JSON convention, with ensure_ascii=False, allow_nan=False and no final
newline. This is not a claim of RFC 8785 canonicalization.

| Actual comparison | Positions checked | Mismatches |
| --- | ---: | ---: |
| Manual A versus manual B | 549 | 0 |
| Pedal A versus pedal B | 200 | 0 |
| Manual A versus profile | 549 | 0 |
| Manual B versus profile | 549 | 0 |
| Pedal A versus project pedal map | 200 | 0 |
| Pedal B versus project pedal map | 200 | 0 |

The test suite also compiles the unchanged profile and compares **all 549 compiled
routes** with each independent manual CSV. Its 4,545 compiled bytes retain SHA-256:

    b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f

Existing runtime routing consumes that matrix; this task changes no runtime code.

## Reproduce the checks

From the repository root:

~~~sh
python3 tools/validate_factory_reference.py
python3 tests/test_factory_reference.py
~~~

To verify the separately acquired source PDF too:

~~~sh
python3 tools/validate_factory_reference.py --source-pdf /absolute/path/Hammond-factory-service.pdf
~~~

The default run validates the pinned source metadata and locators but clearly
reports that the external PDF's bytes were not checked. The source-pdf option
verifies its exact byte size and SHA-256. It does not download a file, parse PDF
pages, authenticate the publication, or establish rights. The 220-page count was
checked with pdfinfo during this comparison and is bound to that source hash.

The standard-library validator is read-only. It bounds CSV input at 8 KiB,
JSON/review-note input at 256 KiB, and optional PDF input at 16 MiB. It rejects
nonregular files, changing reads, duplicate JSON names, nonfinite numbers,
excess depth/nodes/string length, wrong shapes, reordered IDs/columns, invalid
integer types, changed hashes, metadata and source locators. Failures include
cell identities and PDF/printed-page locators for numeric disagreements. At most
64 diagnostic entries are retained; further diagnostics are counted explicitly.
No successful result is printed after a failed check.

**Executed checks:** the validator passed both without and with the acquired
source PDF. All **20 test methods passed**, including mutations of numeric cells
on both manual pages, target-only changes, the same illicit change in both reviews
and the target, every one of the five null positions, a moved null with unchanged
counts, changed column order, Boolean/float/string/zero identifiers, every
manifest leaf, false source/scope metadata, malformed/bounded inputs, source hash
failure, diagnostic truncation and CLI failure behavior. CMake discovers the
test_factory_reference.py suite through its existing test_*.py rule; a fresh
external Release configuration ran that registered suite successfully.
The unchanged pedal-map and profile-compiler suites also passed 15 and 37 methods,
respectively. Review prose is retained for human audit; the validator checks its
presence and nonempty content, not authorship or semantic truth.

## Original provenance and future integration

The existing profile's independent_factory_verification=false records its
**original authoring provenance**. The existing pedal record similarly retains
independent_factory_transcription_status="missing". Those files were created
before these independent readings existed. Their metadata and raw/canonical
identities remain deliberately frozen for deterministic replay and historical
evidence. This later collateral attestation supplies documentary agreement for
the exact digests above; it does not pretend that the original files already
contained the later provenance.

A future integration should introduce a separately versioned authoring identity
and supported compiler/schema contract that links this attestation and its
source/review hashes. That work must retain v1 replay support, define migration
explicitly, verify all compiled routes again, and record the new canonical and
compiled identities. Merely changing the old Boolean or explanatory text would
alter the historical profile digest and is not an authorized migration.

There were no disagreements, so correction_history is empty. If a future check
finds one, preserve both frozen readings; inspect the precise source cell;
retain old/new values, source image/document identity, PDF/printed locator,
reviewer, date and reason in a versioned correction record. Re-run the complete
comparison and issue a new attestation identity. Never silently edit a frozen
CSV, manufacture agreement, or extend this result to unmeasured physical data.
