# A41 — focused native sanitizer qualification

Actual worker `/root/w07_a41_native_sanitizers`, assignment 41, wave 7.
Owned changes are this note, `docs/reviews/INTERFACE_SANITIZER_QUALIFICATION.md`
and `reports/a41-*`. No production, test, CMake, workflow, shared status, index or
commit change was made. The [review](../../reviews/INTERFACE_SANITIZER_QUALIFICATION.md)
and [JSON result](reports/a41-result.json) retain the complete handoff.

After A40 froze its three test-portability repairs, A41 recorded 354 source,
configuration, contract and protected inputs. All remained byte-identical
through configuration, the selected build and the original CTest gate; A12's
114 protected files also matched. The final source digest is
`b4a1caa57a92b2caadb7c07d0c951de73b4ab86bbdde412bf5941a5a87c80b44`.
The workflow freeze was explicitly released to A43 after that check.

The one new Release build uses the existing pinned SDL source and instruments
220 compiled units, including all 176 SDL C units. All thirteen selected
executables link both sanitizer runtimes. The build uses at most two jobs,
occupies 374.02 MiB and remains reusable as requested by the integrator.

Local LeakSanitizer failed its shutdown thread-suspension operation; the initial
CTest failure and one verbose exit-23 diagnostic are retained. Following explicit
integrator approval, the separate ASan/UBSan gate ran with leak scanning disabled.
It finished **10 passes / three original-limit raster timeouts**, exit 8, with no
ASan/UBSan diagnostic. Assertions and test limits were unchanged.

The integrator authorized one explicitly separate direct execution of each
timed-out raster binary, bounded at 240 seconds. All three completed with their
original executable hashes, zero assertion failures and no sanitizer diagnostic:
workspace raster **74.730474 s**, scaled view **172.510959 s**, and preset raster
**128.676768 s**. Their full 150-frame workspace, 168-frame scaled-view and
192-label/160-glyph preset matrices completed. These observations remain distinct
from the failed CTest gate and do not close leak qualification.

A43 and the integrator received every duration and retained diagnostic path.
Root subsequently added sanitizer-only 180/360/300-second limits, preserving
normal 60/60/30 limits. A41 records that later CMake/workflow change separately;
it does not replace the original source/configuration or imply a rerun. All
thirteen executable hashes and 114 protected files match after diagnostics.
The reusable sanitizer build is released for root's configure/property check.
A43 owns hosted leak-enabled qualification. No further local run is needed for
A41. No physical device, deadline, accessibility or fidelity result follows.
