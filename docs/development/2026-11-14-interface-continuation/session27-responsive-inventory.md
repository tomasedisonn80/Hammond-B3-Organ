# A27 — responsive ordinary-control inventory

Actual worker `/root/w05_a27_responsive_inventory`, assignment 27 of 60, wave 5.
The integrator owns shared documents, production source, build trees and
publication. This worker did not stage, commit or push.

## Outcome and owned files

The [review](../../reviews/INTERFACE_RESPONSIVE_AUDIT.md) and
[result](reports/a27-responsive-inventory.json) qualify 54 ordinary-control
layouts: nine sizes, three workspaces, two presentations. All 3,672 retained
records and 1,584 visible records have the expected inventory; bounds/label/
value/track containment, panel separation and 9,504 exposed-region/label-center
hits pass. The ten shared header controls stay in the header and retain the same
positions across workspaces/modes. The focus composition remains 71/10. A18's
focus/hidden-input proof and A19's 147-key/288-layout homography proof were read,
not repeated.

Inspected all eight existing native gallery PNGs, including all four minimum
views, and the unchanged reference image. No new native launch or CTest target
was needed. The probe uses actual UiModel geometry/hits and a separate Python
rectangle audit; it adds composition coverage without a second projection
oracle. Endpoint slider caps and slots are contained; ornamental shadows are
excluded. No production geometry defect was found in this matrix.

**Open for A34:** the minimum D# preset label requests size 9 but shrinks to
6.153846 logical units in its 10×11 label region. Its glyph envelope is only
9.038464×4.423065. The exact reproduction coordinates, practical hit centers,
breakpoint dimensions and possible next changes are in the review. A28 received
the findings for separate native-scale inspection. The geometry pass does not
assert full label legibility, native accessibility, touch compliance, physical
DPI, real devices or literal 1:1 fidelity.

Owned additions:

- `docs/reviews/INTERFACE_RESPONSIVE_AUDIT.md` and this note.
- `reports/a27-layout-probe.cpp`, a read-only exporter, and
  `reports/a27-analyze-layout.py`, the independent rectangle/inventory audit.
- `reports/a27-source-before.json` and `reports/a27-responsive-inventory.json`.

No duplicate production-source snapshot, dependency copy or build tree was
created. Temporary executable/raw measurements are under
`/tmp/b3-a27-responsive`; only reproducible compact evidence is retained here.

## Exact reproduction

Working directory: `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`.
The source report names the dirty overlay on HEAD
`5d81199a9822874b55f3b0a124715cbd6eadf0e5`, all audited source/font/contract
hashes, read-only archive hashes, compiler and gallery identities. The audit
checks those recorded inputs again after execution. All recorded inputs stayed
unchanged. GCC is Debian 14.2.0-19; the probe is 148,728 bytes with SHA-256
`56b8f5784311f10ad77e154e0c2e235d6094270ef26484f7a04af0a4f2a89314`.

```sh
mkdir -p /tmp/b3-a27-responsive
c++ -std=c++20 -O2 -Wall -Wextra -Wpedantic \
  -Wconversion -Wsign-conversion -Wshadow -Werror \
  -Iapps/standalone -Iinclude \
  docs/development/2026-11-14-interface-continuation/reports/a27-layout-probe.cpp \
  apps/standalone/UiModel.cpp \
  /workspace/scratch/601951e27dc3/build-a13-sdkfree/apps/standalone/libhammond_standalone_support.a \
  /workspace/scratch/601951e27dc3/build-a13-sdkfree/libhammond_core.a \
  -o /tmp/b3-a27-responsive/layout-probe
/tmp/b3-a27-responsive/layout-probe > /tmp/b3-a27-responsive/layouts.json
python3 docs/development/2026-11-14-interface-continuation/reports/a27-analyze-layout.py \
  /tmp/b3-a27-responsive/layouts.json \
  docs/development/2026-11-14-interface-continuation/reports/a27-source-before.json \
  docs/development/2026-11-14-interface-continuation/reports/a27-responsive-inventory.json
```

Final compilation/export/audit exited 0; audit has zero geometry failures.
An initial strict compilation caught two misleading-indentation lines in the
new probe; these were corrected in the probe before execution. This was not a
production defect. No write occurred inside `build-native` or
`build-a13-sdkfree`; their active owners were respected.

## Handoff

Root accepted the ordinary-control coverage provisionally and explicitly queued
the measured preset readability issue for A34. A34 needs a concrete label/layout
choice, shared-geometry preservation and native minimum/breakpoint verification.
If that work changes the renderer or geometry, rerun only the affected A27/A28
checks and retain a new source-qualified result. Current published HEAD, this
working overlay, the existing eight-image preview and a later final gallery
remain separate identities. Sound/state/core/VST3 and all 47 parameter records
were untouched.
