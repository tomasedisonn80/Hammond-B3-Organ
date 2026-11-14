# A38 — Remove allocation-fixture stack pressure

Actual worker `/root/w07_a38_windows_allocation_repair`, wave 7. Read standing
instructions, the complete M0–M9 plan, current scope/checkpoint/manifest, A27 and
the complete allocation fixture. Owned only that test and A38 evidence. Root
retains publication and hosted execution. No product, CMake, workflow, numerical
budget, sanitizer setting or shared desktop input changed.

## Observed failure and diagnosis

Published `2e161dc3a60fc3442051799574feed37bffbfc5c` builds without warnings on
MSVC 14.44.35207, but Windows Release run `43641918154`, job `132591143228`,
passes **135/136**: `test_rotary_propagation_allocation` reports SEGFAULT after
0.02 seconds. Root's [connector-decoded primary log](../reports/root-windows-2e.log)
is retained unchanged. [The A38 report](../reports/A38-windows-allocation-repair.json)
hashes it and records exact excerpts; it does not claim original ZIP bytes.

The original fixture keeps a maximum-capacity history, complete byte snapshot
and large return temporaries on its stack. Isolated GCC 14.2 compilation with
the exported Release flags plus `-fstack-usage` reports a **693,904-byte**
`check_fixture` frame. Disabling optional copy elision raises it to **923,424**
bytes. An exact-source isolated executable passes normally and at a 1 MiB child
stack, but exits **SIGSEGV (-11)** at 512 KiB without output. The earlier shared
binary behaves identically; its sole source difference was a published trailing
LF removal, recorded explicitly.

This demonstrates real stack pressure, **not an exact MSVC crash diagnosis**.
The Windows log has no stack trace, and the GCC original passes at 1 MiB.
Compiler-dependent stack exhaustion remains the working explanation pending
the repaired Windows execution.

## Narrow repair and executed result

Construct the full `HistoryStorage` directly in a `unique_ptr<const
HistoryStorage>` before any view borrows it. Allocate its complete byte snapshot
separately, then compare every byte with `memcmp` after all operations. Preserve
the previous trivial-copyability assertion explicitly. Both owners remain alive
and stationary through every borrowed query; allocation and destruction occur
outside all observed intervals. No test input, numerical comparison or workload
is removed.

The repaired GCC static frame is **5,872 bytes**. Normal, 1 MiB and 512 KiB runs
all pass with **byte-identical stdout** to the original unrestricted run:
eight 4,097-segment fixtures, 16 twelve-overload calibrations, 40 preparations,
82,320 admitted queries, eight copy intervals and 856 rejections. Observed API
allocation/free counts remain zero; maximum work remains 40/48 evaluations and
maximum residual `9.7161861889460965e-15 s`.

From the repository, the targeted build and CTest pass:

```sh
../build-tools/cmake/data/bin/cmake --build ../build-native --parallel 3 --target test_rotary_propagation_allocation
../build-tools/cmake/data/bin/ctest --test-dir ../build-native -C Release --output-on-failure --no-tests=error -V -R '^test_rotary_propagation_allocation$'
```

Final CTest is **1/1 in 0.08 seconds**. Original, intermediate and final source,
binary, compiler-command, stack-output and run identities are retained. Child
stack limits were only tightened; child core dumps were disabled for the
deliberate crash. Parent/system limits and build stack settings were untouched.

Final test SHA-256:
`022845759fe2e604ad4c8003dc0acf4e2b693d79933da86e25a0ac8e0f9f39d7`.
Final executable:
`8ae80156b04a4fba4a034024547dcbfee398a9aca4ba08c9224f8dffa76a803f`.
Both rotary sources/headers and `TestSupport.h` match the published product.

Next: publish the exact repair and execute Windows Release and hosted
leak-enabled sanitizer gates. Their success for this repaired source remains
pending; the original Windows failure and A27's local LSan limitation remain
historical evidence.
