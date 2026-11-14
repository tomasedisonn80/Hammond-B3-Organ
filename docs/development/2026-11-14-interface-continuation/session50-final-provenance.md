# A50 — Final visual provenance and retained evidence graph

Actual assignment **50/60**, logical wave **9**, worker
`/root/w09_a50_provenance_assets`, 14 November 2026.

## Scope and result

Read AGENTS, the complete project plan, current session/checkpoint/scope,
consolidated atlas reviews and relevant product/source/asset/font records.
Compared published `cdbb2beaa28bf136f9a8db6213819129514e2ae9` with the
`8673713a484c40e26ac7810c7c4cbc22fa874426` captured product inputs. Owned only
this note, [the final provenance review](../../reviews/INTERFACE_FINAL_PROVENANCE.md)
and `reports/a50-*`; source, gallery, shared documents, prior reports and
publication remain root-owned.

The [read-only audit](reports/a50-provenance-audit.json) verifies all 15 A12
visual/source entries; the unchanged 500-page PDF and identical original JPEG
stream on pages 1/409; three compressed/decompressed/source-crop/generated-array
identities; two source fonts and both encoded/decoded font atlases; complete font
notice retention; the exact executable; all 98 product files across both commits;
the retained 13-file build snapshots; both gallery payload manifests; all 41 v1
published files and 41 v2 final-inventory entries; eight PNG hashes/dimensions and
their corresponding native diagnostic records. All 233 targeted local Markdown
links resolve. This is provenance inspection, not A51's visual comparison or
A49's native execution.

## Concrete discrepancy and additive resolution

Of 45 targeted report-hash edges, three A46 edges refer to one unavailable
earlier A44 report shape; the other 42 match. A46 pins 3,486 bytes /
`738ac4970c5cb225e9b3fda8933f6145eebb557e0c2d5ecb46de08a8b9095047`;
the final published A44 result and A45's pin are 3,509 bytes /
`332055972738e624a9ca75bae87557a96b45a8b4426c70006bcf1c906e9e12fd`.

[Reconciliation](reports/a50-a46-a44-edge-reconciliation.json) proves exact
reconstruction by two top-level key renames, with every value unchanged.
[Reconstructed bytes](reports/a50-reconstructed-a44-at-capture.json) retain
the expected old hash and are explicitly derived, never described as an
independently archived original. Raw-byte hashing in A46's helper rules out an
inventory/canonical-JSON digest confusion. No timing/actor is inferred. Root
agreed to preserve original inputs and add the
[supplied note](reports/a50-gallery-addendum-proposal.md) linking this explanation.

## Executed command and bounded correction

From `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`, with Python 3.12.14,
Pillow 13.0.0 and PyMuPDF 1.26.6 already available:

```sh
python3 -B docs/development/2026-11-14-interface-continuation/reports/a50-provenance-audit.py
```

The script writes only A50 outputs. The first authoring pass used a list
comparison for A44's dictionary-shaped guide-change field in a supplementary
boolean; inspection corrected the reader to compare its keys and final payload
values, and the second pass returned all semantic checks true. This was an
audit-reader correction, with no product or retained-evidence mutation.

No configure, build, native launch, image generation/capture, external lookup,
commit or push occurred. No full source-to-binary, physical device, literal visual
equality, legal-clearance or seventh complete atlas-reading claim follows.
Root owns additive gallery/shared-document integration and guarded publication.
