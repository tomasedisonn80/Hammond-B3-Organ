# A28 — full-view scale, text and clipping audit

Actual assignment `/root/w05_a28_scale_text_audit`, wave 5. The
[detailed audit](../../reviews/INTERFACE_SCALE_TEXT_AUDIT.md) and
[result](reports/a28-scale-text-audit.json) retain scope, failure and limits.

Added the full native `test_standalone_scaled_view.cpp` and found four failures
in preset focus: integer logical clip reads lost odd physical edges at 1.5×/2×.
Root expressly authorized the narrow `InstrumentView.cpp::paint_preset_focus`
physical-clip intersection/restoration repair. Final renderer SHA-256 is
`6b498c9ba2c47acf432216189159b928d2a5d31368ec34c1fe8dc906710e8a67`.
Geometry, material, text and sound controls were preserved. Root owns CMake.

Strict Release build and scaled/preset CTest gates pass **2/2** in 27.90 seconds.
The new suite covers 168 full-view frames, 168 state checks, 90 clipping checks,
16 scaled key-focus cases, 56 Service values and 58 actual value lines. Minimum
and default logical dimensions are rendered at 1/1.5/2; default 2× uses four
bounded tiles. Existing preset raster acceptance also passes. Final app SHA-256:
`55b0947985ee562cce3d04eae66cc4d44f805420f475dd578f00373dd2bef6cd`.

**Visual scaling remains open.** Inspection of two retained 1.5× injected
renderer PNGs found every third row unpainted in dimensional surfaces. In a
28,500-pixel card patch, all 9,500 third-row pixels equal clear walnut. Logical
one-row strips in `Drawing::gradient/rounded` are truncated by SDL software
scaling. A31 owns this repair/regression; A34 separately owns the measured
6.153846-unit D# legend. No OCR, physical DPI or full legibility pass is claimed.

Reproduction from repository root, using the coordinated existing native build:

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake \
  --build ../build-native --target test_standalone_scaled_view \
  test_standalone_preset_raster hammond_standalone -j 3
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir ../build-native -R '^test_standalone_(scaled_view|preset_raster)$' \
  --output-on-failure --no-tests=error -V
```

For two optional BMP proofs, supply a fresh directory as the executable's sole
argument, or set `HAMMOND_SCALED_VIEW_CAPTURE_DIR` for the filtered CTest run.
The committed PNGs are verified lossless copies totaling 669,453 bytes; they are
injected paint frames, not application screenshots. The original failed log is
retained. Build-native was released to root after the final gate; no further
production/test edits, staging or publication were performed. Root/A31/A34 own
the remaining integration, surface repair and readability follow-up.
