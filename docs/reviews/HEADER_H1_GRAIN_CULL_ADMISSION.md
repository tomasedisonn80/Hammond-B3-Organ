# H1 grain culling: independent correction admission

**A27 follow-up, 17 November 2026: admit the proposed one-line deletion in
`reference_header_h1_material`.** This is the same A27 worker, with no extra
worker credit. The [H1 contract](../design/HEADER_MATERIAL_H1_CONTRACT.md),
SHA-256 `07d64498a14431b64742d79e7fbe4d2ac71d77fe51d09f71c638f52594fd9282`,
and all earlier reviews remain unchanged.

Verified current painter and [preserved initial source](../development/2026-11-16-heading-title-continuation/inputs/InstrumentView-h1-initial.cpp)
both have SHA-256
`0385765af919cac92e334d103f02c0f342cbf2fbd6060ca71a1a715ec7cdcb16`.
The [original static rejection](../development/2026-11-16-heading-title-continuation/reports/h1-grain-cull-static-rejection.json)
remains valid and preserved; no native candidate result is inferred.

## Independently reproduced counterexample

Canonical logical size1672×941, physical output200×120, zero origin and physical
clip `(7,0,1,120)` are sufficient. Binary32 renderer scale0.1 is exactly
`0.10000000149011612`, within the admitted finite-positive-through-two domain.
The field's intrinsic x interval is
`[ceil(76*rx−0.5), ceil(1596*rx−0.5)) = [8,160)`. Clipping produces `[8,8)`.

Grain uses the separately specified SDL software fill rule: binary32 origin
multiplication, truncation toward zero, and minimum extent one. Canonical
origins x78/79 consequently paint device x7. Independent enumeration of all
16,384 prescribed marks reproduces **exactly all 21 records** in root's
receipt, occupying **nine pixels** at x7 and y1,2,3,4,5,6,8,9,10. For example,
pair146/bright has canonical `(78,28)` and device `(7,2)`. No grain color or
candidate raster was evaluated.

The field-only early return therefore skips prescribed visible grain. An
empty field intersection does not prove the union of field and grain empty.
The contract has no lower renderer-scale cutoff permitting this omission.

## Exact admitted change and remaining work

Delete only this line **inside the H1 helper**:

```cpp
        if (edges.front() >= edges.back() || first_row >= end_row) return;
```

The expected resulting whole-file SHA-256, calculated by deleting those exact
75 bytes in memory, is
`0bf731a692b7cb7c88c200afea86f4ca14239f20a7000f06be484f2a11ebc20d`.
The identical lines in UpperRack and LowerRack remain untouched. Preserve the
global `raster.visible()` guard: an empty viewport/output/clip intersection
excludes both operation families. Existing row/span loops naturally skip empty
field coverage; the raster guard then restores both scales before the bounded
grain loop. The enclosing color guard, blend/clip/viewport behavior, ordering,
seed, field values and `257R+16,384` primitive ceiling remain unchanged.

A34 owns this exact source correction; root verifies its resulting hash and
rebuilds before required native comparison, timing and visual gates. This
admission changes no threshold, support, renderer domain or contract. Only this
new review was written; no production/tool/test/build/configuration/native run
or capture occurred here. Candidate acceptance remains pending.
