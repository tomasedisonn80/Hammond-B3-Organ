# A19 — independent keyboard projection acceptance

Accepted the integrator's `UiModel.cpp` projection against
`standalone-perspective-keys-v1`. This assignment owns only
`apps/standalone/tests/test_standalone_projection.cpp`, this note and its
[machine-readable report](reports/a19-geometry-acceptance.json) /
[actual CTest transcript](reports/a19-projection-ctest.txt). No production code,
legacy assertions, CMake files, sound parameters or state formats were changed.

## Observed result

The new SDK-free Release target compiled under GCC 14.2.0 with all project
warning flags, including `-Wconversion -Wsign-conversion -Wshadow -Werror`.
CMake/CTest 4.4.4 reports **1/1 passed**, 0.18 seconds for the test and 0.19 seconds
total. No production defect was found.

The test executes **288 layouts**, checking **42,336 playing-key records** and
**6,912 preset records**. It combines all three workspaces, both presentations,
all four edited-bank combinations and twelve sizes: minimum 960×700, default
1280×900, reference 1672×941, all four 1399/1400×819/820 breakpoint combinations,
1280×819/820, 8192×8192, 8192×700 and 960×8192.

Each fixture retains all 147 playing-key identities, 24 distinct canonical preset
IDs, 36 naturals per manual and 15 pedal naturals. Checks cover actual visible
quad hits, accidental precedence over both underlying naturals, half-open edges,
exact shared white-key endpoints, finite positive geometry inside its panel and
window, front depth clamps, exact top/front partition seams, Flat's empty fronts,
and rectangular pedal plans. Interior front points hit; both top and front
sloped AABB corners miss in both manuals. Rotary/Service reject the same hidden
musical target points.

Malformed quads, nonfinite vertices/points, unequal horizontal edge coordinates,
zero/negative dimensions and maximum-finite slanted geometry are exercised.
Ten thousand huge-finite iterations pass without coordinate overflow. All 1,031
invalid layout calls preserve every destination byte, including both invalid
bank positions, all invalid byte-valued workspace/presentation enums and boundary,
NaN/infinite dimensions. This is bounded functional execution, not a rendering
performance claim.

## Independent expectations and numerical policy

The oracle uses long-double rational coefficients `47/(50−3v)`, independent
screen-y elimination for face intersections, and a literal pitch-class table.
It never calls a production projection helper. Known 100×100 rational landmarks
and literal default/reference coordinates qualify the oracle and retained panel
relationship. Coordinate comparisons allow `4 × float epsilon × max(width,height)`;
face intersections allow eight epsilon units because their production split uses
additional float arithmetic. These maxima are 0.00390625 and 0.0078125 logical
pixels at size 8192. Shared endpoints and top/front seams require exact equality.
Known binary-exact trapezoid edge probes use `nextafter` with exact half-open
expectations. Production neighboring probes stand 1/32 logical pixel from the
independently calculated boundary, avoiding float-edge ambiguity.

A18 independently covers original pointer, keyboard, Space and external-note
owners across resize, presentation and workspace changes; this assignment keeps
its focus on numerical geometry and silhouettes instead of duplicating that gate.

## Reproduction and identity

Working directory: `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`.
Reuse `/workspace/scratch/601951e27dc3/build-a13-sdkfree` after coordinating its
ownership. This run acquired it after A18 released it; no SDK copy was created.

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake -S /workspace/scratch/601951e27dc3/Hammond-B3-Organ -B /workspace/scratch/601951e27dc3/build-a13-sdkfree
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake --build /workspace/scratch/601951e27dc3/build-a13-sdkfree --target test_standalone_projection -j 2
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest --test-dir /workspace/scratch/601951e27dc3/build-a13-sdkfree -R '^test_standalone_projection$' --output-on-failure --no-tests=error
```

Base HEAD is `5d81199a9822874b55f3b0a124715cbd6eadf0e5`; tested code includes
the current working overlay. Exact source, contract, test, support/core-library
and executable SHA-256 identities are retained in the report. Key source hashes:

- `UiModel.cpp`: `c536c460c6157197bc98c12c1d9d865584c043c44d1c7d3ca6d3d539f74dc0c3`
- `UiModel.h`: `1c51aaa46ee12be91ae8729fa739d7f4d102dc030bae61dbf15fd0cc1692a98d`
- New test: `dc69d54421ef52dfdbd45e3436a89ba9ad3aa155ff76fae4a8cfc9fc56140fd8`

Next, include this auto-discovered target in the coherent SDK-free integration
gate and qualify native rendering against these same hit/top/front shapes.
Actual pixels, platform/device execution, accessibility, literal reference
fidelity and physical instrument fidelity remain separate acceptance work.
