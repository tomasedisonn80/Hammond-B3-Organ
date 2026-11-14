# A27 — R3 allocation, lifetime and sanitizer gate

Actual worker: `/root/w05_a27_rotary_realtime_sanitizer`; wave 5. Read the
standing instructions, complete plan, current scope/checkpoint/assignment,
numerical and propagation contracts, Motion/Propagation sources and A17/A19
evidence. Observed HEAD: `e4968b2acd37b6f79683704356350070fe2fc329`.
Owned the new auto-globbed `tests/test_rotary_propagation_allocation.cpp`, this
note and four A27 reports. No production changes, shared-build mutation,
commit or push. Respected A25's quiet interval until its 21:01:22 UTC release.

## Meaningful workload and exact result

**Optimized gate: PASS. Complete ASan/UBSan/leak gate: FAIL, environment blocked.**
The [summary](../reports/A27-r3-summary.json) distinguishes both outcomes and
hashes the original execution, verbose diagnosis and PTY retry reports.

Eight fixtures cover all four rates and both directions, with caller-owned,
constant 4,097-segment arrays. Dense command transitions, startup/prehistory,
Mach 0.25, separate receivers and fractional full-day endpoints are exercised.
A non-inlined preparation function returns before copied views/paths are
queried; the original view, original paths and intermediate copies have ended
their lifetimes, while their immutable backing arrays remain valid. No dangling
span is deliberately accessed. Every anchor is queried immediately before and
exactly on its boundary. Sixteen observations repeat 32 times per fixture.

The executable follows the project's complete C++ allocation-interposition
convention. Sixteen calibrations detect exactly **192 allocations and 192
deallocations** across ordinary, array, nothrow, aligned and sized overloads.
Calibration, fixture construction, assertions and reporting occur outside
observed primitive intervals.

Observed **zero C++ allocations and deallocations** in 40 successful preparations,
82,320 admitted queries, eight copy intervals and 856 rejected calls. Queries
comprise **69,776 history evaluations, 8,448 path solves and 4,096 geometry calls**.
Maximum solve work was **40/48 evaluations**; maximum residual was
`9.7161861889460965e-15 s`. Failed preparation/query calls preserve complete object
and destination bytes, including a failure after solve entry when a bracket
emission exceeds the negative epoch. Later successful results remain identical;
all backing-history bytes remain unchanged.

## Commands, sanitizer limitation and identities

Working directory: `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`.
GCC **14.2.0-19**, C++20, `-DNDEBUG`, all project warning flags including
`-Wconversion -Wsign-conversion -Wshadow -Werror`. Directly compile
`src/RotaryMotion.cpp src/RotaryPropagation.cpp tests/test_rotary_propagation_allocation.cpp`
with `-Iinclude`, `HAMMOND_TEST_PROFILE="unused"`, `HAMMOND_SOURCE_DIR="."`:

- Optimized: `-O2`, then `/tmp/a27-rotary-allocation-optimized`; compile/run exit 0.
- Sanitized: `-O1 -g -fno-omit-frame-pointer -fno-optimize-sibling-calls
  -fsanitize=address,undefined -fsanitize-address-use-after-scope
  -fno-sanitize-recover=all`; compile exit 0.
- Run `/tmp/a27-rotary-allocation-asan_ubsan` with
  `ASAN_OPTIONS=detect_leaks=1:detect_stack_use_after_return=1:halt_on_error=1:abort_on_error=1:strict_string_checks=1`,
  `UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1`,
  `LSAN_OPTIONS=exitcode=23:report_objects=1`.

Exact argv, executable/runtime hashes and all diagnostics are retained. Normal
execution aborted with SIGABRT; PTY retry exited 134 after printing the identical
successful workload. Verbose LSan reports **“Could not attach to thread 6
(errno 1)”** and **“Failed suspending threads.”** Observed `TracerPid=0`,
`NoNewPrivs=1`, `Seccomp=2`; the precise policy causing EPERM remains unidentified.
No protection changed, check disabled or finding waived. Leak freedom remains
unqualified. Two isolated binaries total 1,278,744 bytes.

| Source | SHA-256 |
| --- | --- |
| Motion | `a3f986892078254f6dfae936bbbf1b5e1c4967882d06c13b3b28649f2273cfa1` |
| Propagation | `dcc36819747b8d215130c5031a955e4b00af29a114832d0bf273ca60eaaf0c2e` |
| New test | `b7329be029b8ddd41d8f6f43b5b007ee9c5ab60fcbff7c2dd23c026c4278f45d` |

All relevant source/header/contract hashes remained unchanged. Next: root runs
the unchanged target on a hosted sanitizer runner permitting LSan thread
inspection, with leak checking enabled. This probe observes one thread's global
C++ calls, not arbitrary C/system allocation, locks or deadlines. R4 waveform
history/interpolation/transactions, R5 audible policy, Engine/R6 integration and
physical qualification remain separate.
