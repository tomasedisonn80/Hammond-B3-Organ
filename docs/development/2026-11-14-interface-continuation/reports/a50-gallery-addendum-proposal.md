# A50 additive gallery-note proposal

Root-owned destination: append a short dated section to
`examples/demos/standalone-interface-preview-v2/README.md` beside source/provenance
qualification. Preserve the captured `inputs/source-qualification.json`,
`provenance.json`, payload manifest and original A46 reports. This proposal is
not an applied gallery change. Any later README change needs its own current
document identity; A46's final inventory remains its dated authoring snapshot.

Exact proposed text, with links relative to the gallery README:

```markdown
### A50 provenance reconciliation — 14 November 2026

An independent provenance review verified the original PDF/reference/assets,
all 98 observed product files against both `8673713` and published `cdbb2be`,
and every retained PNG's file and decoded-pixel identity. The ten-file capture
admission, 98-file product observation and 13-file selected build observation
remain distinct; this is not a complete source-to-binary rebuild attestation.

The capture's copied qualification pins an earlier 3,486-byte A44 package
result, SHA-256 `738ac4970c5cb225e9b3fda8933f6145eebb557e0c2d5ecb46de08a8b9095047`.
The published final report is 3,509 bytes, SHA-256
`332055972738e624a9ca75bae87557a96b45a8b4426c70006bcf1c906e9e12fd`.
[A50's reconciliation](../../../docs/development/2026-11-14-interface-continuation/reports/a50-a46-a44-edge-reconciliation.json)
reproduces the earlier hash exactly by changing only two top-level keys:
`runtime_packages` → `packages` and
`build_install_drift_during_runtime` → `build_install_drift`.
All values agree. The [retained reconstruction](../../../docs/development/2026-11-14-interface-continuation/reports/a50-reconstructed-a44-at-capture.json)
is derived from the final report, not an independently archived original.
The original capture records and manifest remain unchanged; the discrepancy
does not change the recorded executable, product inputs or PNGs. See the
[independent provenance review](../../../docs/reviews/INTERFACE_FINAL_PROVENANCE.md)
for the exact scope and remaining limits.
```
