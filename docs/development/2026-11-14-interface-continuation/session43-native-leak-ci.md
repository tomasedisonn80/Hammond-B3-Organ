# A43 — Focused native sanitizer and leak CI

Actual worker `/root/w08_a43_native_leak_ci`, assignment **43/60**, logical wave
**8**. Ownership is `.github/workflows/standalone.yml`, this note,
`docs/reviews/INTERFACE_NATIVE_SANITIZER_CI.md` and `reports/a43-*`; root owns
CMake, shared status, staging and publication.

Added a Linux GCC native ASan/UBSan/leak job for the exact thirteen A41 interface
targets, with project C++ and pinned SDL C instrumentation, compile/link checks,
exact nonempty discovery, serial CTest and always-retained diagnostics. The
entire A39 workflow prefix remains byte-identical; existing Release rows,
required names, packages and deadlines are preserved. Hosted inventory becomes
twelve jobs. [Review](../../reviews/INTERFACE_NATIVE_SANITIZER_CI.md) and
[machine inventory](reports/a43-native-sanitizer-ci.json) retain the scope.

Static validation passes three YAML workflows, 36 Bash blocks and 12 Python
blocks, plus the thirteen CMake/discovery mappings. No local build/test,
dispatch, index update or commit was performed. A41 released its 354-input
workflow freeze before this edit; root first staged A39 independently.

**Pending:** A41's separate direct diagnostics of the three original-limit
raster timeouts and root's budget decision, then publication and A48/A58's
observation of the exact hosted revision. The local LeakSanitizer attachment
failure, ten passes and three original-limit timeouts remain distinct evidence;
no leak or complete thirteen-suite pass is claimed.

## Root integration follow-up

After A43 completed its static implementation, A41 finished all three separately
bounded raster diagnostics. Root added only sanitizer-conditional CTest budgets
180/360/300 seconds and corresponding workflow discovery assertions, preserving
normal60/60/30 limits and every test assertion. The review above distinguishes
this later integration from A43’s initial static snapshot. Configured-property
and exact hosted leak qualification remain separate recorded checks.
