# Scanner development handoff

## Active scope

The [2026-11-13 scanner session](development/2026-11-13-scanner/README.md) continues from commit `6dc0702d5473912268e8af8f852b9b9984198ef3`. It requests sixty distinct assignments in ten logical waves of six; the [manifest](development/2026-11-13-scanner/assignments.json) records actual dispatched identities and outcomes. Earlier completed sessions are preserved.

The next engineering work is the documented nominal scanner: reconstructed graph admission, independent numerical references, prepared physical-state runtime and one continuing rotor. The graph/compiler, primary-source comparison and independent AC reference are now implemented; the physical-state line, independent full-graph transient reference and continuing rotor are implemented. Full-grid frequency/process and independent rotor checks have passed, while matched-step/combined-stage checks are in progress. Current scope and test evidence are updated at each integration checkpoint. The source remains the unchanged 500-page atlas; original missing companion files are not recovered by newly authored implementations.

## Verified starting point

The integrator built the default Release source at the starting commit with GCC 14.2.0, CMake 4.4.4, Ninja 1.13.2 and Python 3.12.14. CTest passed 71/71 suites with zero failures in 42.88 seconds. All three historical sixty-complete record checks passed. No scanner implementation is included in that baseline result.

Existing dry organ, native wrapper, render and install commands remain in [PEDAL_HANDOFF.md](PEDAL_HANDOFF.md). All 45 parameters, old state migrations, source profile, routing data and retained musical examples are compatibility inputs.

## Standing continuation rule

Every future agent follows [AGENTS.md](../AGENTS.md): read current status, next steps, the plan and relevant PDF chapters; claim a bounded task; record the exact source/data identity and actual commands/results; preserve unresolved physical and product gates; update status, next steps, development log and affected contracts; then commit and push completed authorized work to main, without force-pushing. Verify the fetched remote revision and report CI according to observed results.

## Graph and reference commands

From the repository root, using Python 3.10+ and CMake 3.21+:

```sh
cmake -E make_directory out
python3 tools/compile_scanner_line.py --input data/scanner/atlas-late-b3-nominal-v1.json --output out/scanner-line.json
python3 tools/scanner_ac_reference.py --output out/scanner-ac.json
python3 tests/test_scanner_line_profile.py
python3 tests/test_scanner_ac_reference.py
cmake -S . -B build-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build-release --config Release --parallel 3
ctest --test-dir build-release -C Release --output-on-failure --no-tests=error
```

The compiler validates the exact full graph before producing SI JSON or a `--format header` native representation. Source fixture SHA-256 is `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604`; generated header SHA-256 is `d508e3856e637a8e107364ad2a8fed09893a2e50ae05d99db3d4b3da37a5a082`. Original unknown physical values remain null with acquisition tasks. Invalid inputs preserve an existing destination.

The default AC report contains 564 positive-frequency solves, 10,716 complex tap transfers, exact-rational DC, signed return/current, residuals/conditioning, phase eligibility and group-delay diagnostics. Largest residual was 3.2486101684985267e-16. An independently implemented loaded-ladder recursion agrees within 5.6647284161045834e-14. Root reran 19 graph/compiler methods and 16 AC methods with no failures. [The numerical contract](SCANNER_NUMERICAL_CONTRACT.md), hash `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9`, was frozen before runtime grading.

Primary source comparison corroborates every passive/output and the sixteen-position cycle, with an explicitly shifted phase origin. It does not identify a specimen, verify 412rpm, supply winding losses/loading, or turn ideal-network tests into physical fidelity. Refer to [the source review](research/SCANNER_PRIMARY_REVIEW.md) for exact pages and source identities.

The [coherent wave 2 integration](reviews/SCANNER_WAVE2_INTEGRATION.md) qualifies commit `74473fa`, tree `6c76bba650c033d9e8ade7ba3b2347ce569a10b6`: a new detached-source Release build passed 73/73 suites in 50.00 seconds, zero failures. It excludes unfinished runtime source from the next wave.


## Runtime integration in progress

The prepared [`ScannerLine`](SCANNER_LINE.md) and independently stamped
[transient reference](SCANNER_TRANSIENT_REFERENCE.md) are implemented. The
[native state acceptance](SCANNER_LINE_ACCEPTANCE.md) checks nonzero histories,
energy, bounds, rate migration and exact rejected-call continuation. Root's
live-tree integration passed the line and install suites (2/2, 7.52 seconds);
this is a focused result, not a frozen full-runtime qualification. All wave 3 workers have completed the native probe, full AC comparison and independent
transient regressions; wave 4 owns the remaining combined and matched-step checks. Consult the actual manifest before assuming completion.

A repeated default configure exposed a CMake 4.4.4 GNUInstallDirs cache behavior:
it leaves a derived empty DATADIR, which the project's explicit-empty guard then
rejected. The installation module now materializes and tracks its automatic
default, follows DATAROOTDIR changes and preserves explicit custom DATADIR.
The real configure regression passes repeated defaults, changed roots and custom
paths while retaining rejection of explicit empty/absolute/traversal paths. For
a known older automatically generated empty cache only, clear that cache entry
once with `cmake -U CMAKE_INSTALL_DATADIR -S . -B <build>`; fresh builds need no
workaround. This does not authorize changing an unknown user override.

## Publication identity

The tested local foundation commit `74473facf8efc3332497ab969017c718458d6921`
was published through the connected GitHub account as
`cdada3c8dc655d27033dd15f3417d39a7a82ecb9`, with identical tree
`6c76bba650c033d9e8ade7ba3b2347ce569a10b6`. Its documentation follow-up is
`80ea8cd2d7febe12fc4dd382e475a00ff4181eac`, tree
`d98d9baf666f048629f5c817ed0f040b215df0e4`. Root fetched and verified both
file trees and adopted the published history without altering in-progress work.
CLI push had no stored credentials; the authenticated connector completed the
conditional non-force update. Hosted CI and native runs were observed queued,
not passed; their later states require inspection.


## Executed frequency and rotor gates

[The full AC/process qualification](SCANNER_AC_PARITY.md) passes its G3 portion:
160,740 logical positive tap comparisons, exact DC and all 88 process carriers.
The report retains the five earlier unsettled attempts and the successful
bounded pre-roll refinement; no gain, sign, phase or latency correction was fit.
[Independent rotor acceptance](SCANNER_ROTOR_ACCEPTANCE.md) passes the G4
six-mode, map, signed weight, clock and failure-continuation requirements.
Full matched-step state parity and combined routing/allocation are in progress.

G5 same-hertz accuracy **fails at every allowed research rate**, including
1,536,000 Hz. Selecting a multiplier cannot close that gate. Keep this result
and realization as evidence while investigating a separately identified
alternative realization or justified policy under the unchanged numerical
contract. Converged transients, rotating output, real interpolation/filter and
latency evidence remain separate. No Engine/native scanner control is added by
the independent research modules.


The [coherent line/rotor checkpoint](reviews/SCANNER_WAVE3_INTEGRATION.md) qualifies local commit `babb8975d6881db6629e570e10ee619c70ba8be3`, tree `14572ab24e67489997cee20ae452c0635178dca0`: **77/77 Release suites passed**, zero failures, in 50.64 seconds from a new detached-source build. Combined-stage work is excluded from that result.
