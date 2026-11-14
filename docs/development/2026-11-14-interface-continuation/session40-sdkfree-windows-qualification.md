# A40 — SDK-free qualification and Windows fixture repair

Actual agent: `/root/w07_a40_sdkfree_windows_qualification`, wave 7.

Owned three test sources: workspace acceptance under `apps/standalone/tests/`,
and scaled view/workspace raster under `apps/standalone/native_tests/`. Repaired
the observed MSVC warnings using explicit bounded integer-to-float casts and
existing `SDL_getenv`, preserving every assertion and timeout. No production,
CMake, shared status, staging or publication changes were made by this worker.

Strict native rebuild and focused CTest passed **3/3**. Reconfigured and rebuilt
the reusable SDK-free Release tree; fresh discovery and full CTest passed
**130/130**, with no skipped tests. The frozen 335 inputs, 75 SDK-free outputs
and protected 114-file inventory remained unchanged. Both build leases are free.

[Review and reproducibility](../../reviews/INTERFACE_SDKFREE_QUALIFICATION.md) ·
[Result/commands](reports/a40-result.json) ·
[Frozen inputs](reports/a40-source-freeze.json) ·
[Original Windows failures](reports/root-ui-ci-windows-failures.json).

The repair hashes were sent to root and A41 before the full SDK-free gate.
Windows closure requires root publication and A48's observed hosted MSVC results;
Linux GCC success is recorded separately.
