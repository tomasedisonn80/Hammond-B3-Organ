# Assignment 17 — independent native AC and process qualification

- **Worker:** `/root/w03_a17_native_ac_parity`, assignment 17 of 60, wave 3 of 10.
- **Status:** completed for integrator review on 13 November 2026.
- **Owned paths:** `tools/qualify_scanner_ac.py`, `tests/test_scanner_native_ac.py`, `docs/SCANNER_AC_PARITY.md`, and this note.
- **Inspected base:** local and observed remote `main` were `80ea8cd2d7febe12fc4dd382e475a00ff4181eac`, tree `d98d9baf666f048629f5c817ed0f040b215df0e4`.
- The prepared line, probe and new qualifier were uncommitted coordinated inputs. The base commit is ancestry, not a claim that it contains this runtime. Actual numerical inputs and executable identities are recorded below.
- No production line, Engine, controls, native plugin, shared CMake/status, Git index/ref or remote was changed by this worker. No worker was spawned.

## Scope and independent method

Read standing instructions, current status/next steps/handoff, session plan, the frozen numerical contract, source review context and relevant atlas pp. 157–159 and 181–186. The six dedicated session readers own complete 500-page coverage; this assignment does not claim another full reading or physical acquisition.

The qualifier calls the final assignment-16 native probe and independently stamps the admitted full passive graph through assignment 8’s nodal AC solver. It never imports C++ reduced operators, factorization or tap reconstruction. DC uses separate exact rational arithmetic. The frozen grid is independently restated from the contract, including the 282 positive bins, both modes and all fifteen host/multiplier labels. Eleven distinct internal rates are computed and explicitly referenced by all applicable labels.

The [companion contract](../../SCANNER_AC_PARITY.md) explains signed units, bilinear mapping, preserved same-hertz failures, phase/null handling, actual process fits, bounded startup refinement and report failure semantics. The full report preserves all native/reference complex values, errors, bounds, failed tap names, solves and phase exclusions. Its current dimensionless comparison includes `15000 ohms * input_admittance`; raw A/V values remain retained.

## Executed coherent build and commands

Working directory: `/workspace/scratch/1742da7072be/Hammond-B3-Organ`. Native source was frozen by assignments 13/16 before this private build. Both the line and probe were compiled together, with the compiler-generated graph, in new `/workspace/scratch/1742da7072be/a17-build`. Other workers continued disjoint work; whole-repository cleanliness is not claimed.

Observed toolchain: GCC 14.2.0, CMake 4.4.4, Ninja 1.13.2, Python 3.12.14, Linux x86_64/glibc 2.41. C++20 Release used `-O3 -DNDEBUG` plus repository strict warnings `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`; sanitizers were off for this run.

```sh
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH cmake -S . -B /workspace/scratch/1742da7072be/a17-build -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH cmake --build /workspace/scratch/1742da7072be/a17-build --target hammond_scanner_line_probe -j 4
python3 tools/qualify_scanner_ac.py --probe /workspace/scratch/1742da7072be/a17-build/hammond_scanner_line_probe --output /workspace/scratch/1742da7072be/a17-scanner-ac-final.json
HAMMOND_SCANNER_LINE_PROBE_EXECUTABLE=/workspace/scratch/1742da7072be/a17-build/hammond_scanner_line_probe python3 tests/test_scanner_native_ac.py -v
```

The native build passed. The full qualification exited 0 for the executed G3 frequency checks while explicitly reporting failed G5 same-hertz comparisons. The final regression run passed **13/13 methods in 2.044 seconds**, zero failed/skipped methods. Parent owns CTest wiring and later frozen whole-tree qualification; this worker directly ran the same Python suite with the required executable environment variable.

## Observed full-grid result

| Measurement | Actual result |
| --- | --- |
| Host/multiplier coverage | 15 labels, 11 distinct internal rates, 22 rate/mode cases |
| Positive native recurrence solves | 6,204 unique; 8,460 logical label/mode/bin combinations |
| Positive tap comparisons | 160,740 logical label/mode/bin/tap combinations; all 19 taps retained |
| Independent nodal AC solves | 6,812 including mapped, same-hertz and process carrier references |
| Exact DC | 22 actual rate/mode cases cover all 30 logical labels; zero failures |
| Maximum DC complex error | `1.900701818158268e-13` |
| Maximum mapped complex error | `1.0892198819708419e-12` |
| Maximum mapped error/bound ratio | `2.5513724285702037e-6` |
| Maximum native recurrence residual | `7.188282363802996e-16` |
| Maximum mapped reference residual | `3.642084162578825e-16` |
| Maximum native/reference scaled condition estimates | `1590.3109557605446` / `3017.986309087789` |
| Residual/conditioning failures | Zero; all executed G3 stationary cases passed |
| Actual process carriers | 88 distinct rate/mode/carrier cases, 182 measurements |
| Process acceptance | All settled and passed; zero inconclusive/conditioning-limited cases |
| Maximum accepted process complex error | `1.520540673420773e-11` |
| Maximum accepted process error/bound ratio | `2.0658965195856536e-5` |
| Accepted process startup durations | 250 ms or 500 ms; all attempted windows retained |
| Phase-ineligible bins retained | 10,325 tap/bins in each paired phase diagnostic across distinct rate cases |
| Same-hertz result | **Failed at every investigated internal rate**, with 40,786 failed tap comparisons across distinct rate/mode cases |

The following table counts actual distinct-rate cases. A failed bin is a frequency with at least one failed tap; it is not a count of discarded data.

| Internal rate, Hz | Vibrato failed taps / bins | Chorus failed taps / bins |
| ---: | ---: | ---: |
| 44100 | 2690 / 213 | 3842 / 210 |
| 48000 | 2675 / 210 | 3814 / 207 |
| 88200 | 2510 / 205 | 3607 / 202 |
| 96000 | 2479 / 202 | 3578 / 201 |
| 176400 | 2246 / 196 | 1998 / 145 |
| 192000 | 2206 / 196 | 1839 / 129 |
| 352800 | 1729 / 120 | 987 / 87 |
| 384000 | 1649 / 115 | 900 / 84 |
| 705600 | 795 / 58 | 255 / 38 |
| 768000 | 674 / 56 | 200 / 31 |
| 1536000 | 95 / 12 | 18 / 4 |

Even at 1,536,000 Hz, the worst same-hertz error/bound ratios are `5.283394239484229` for vibrato v5 at 7,075 Hz and `2.0203840693543573` for chorus v11 at 7,075 Hz. Their complex errors are `0.015519709307631253` and `0.017869023894915265`, against bounds `0.0029374505486734802` and `0.00884436982351854`. No admitted multiplier qualifies the frozen full-grid same-hertz criterion.

## Startup finding and reporting repair

The initial diagnostic used two fixed pre-rolls, 125/250 ms, at 48 kHz with five bins and the four required carriers. Vibrato 7 kHz at 125 ms failed five complex tap comparisons, with maximum ratio `1.3480022464781343` and maximum tap fit-residual RMS `6.837118032414983e-7 V`; half-window estimates also had not converged. At 250 ms, its maximum complex ratio was approximately `0.0001446363`. The preliminary report is retained separately; no tolerance changed.

The final, identified `scanner-process-settling-refinement-v1` protocol tests 125/250/500/1000 ms and retains every attempt. It stops only when two consecutive process estimates and their half-windows converge without reference fitting, then grades the last estimate against independent AC. The full run retained five early attempts outside the complex budget. Six cases used three pre-roll attempts: vibrato 7 kHz at 44,100, 48,000, 88,200, 96,000, 176,400 and 192,000 Hz. The last case needed longer half-window convergence even though its initial full-window complex error was already below the bound.

Final audit also found a report-status propagation gap: G5 same-hertz status retained reference residual/conditioning flags but did not include native flags, although G3 did. The qualifier now includes both, and its injected diagnostic regression asserts that neither flagged result can remain a same-hertz pass. The complete numerical run was repeated after this repair. Every report field other than the source-snapshot identity was exactly equal to the prior full report; actual runs had no residual/conditioning flags. The old report remains retained rather than overwritten.

## Exact evidence identities

- Final source/executable manifest SHA-256: `c5c829652c14f67e123fceeb9a202f7141df668210fbeca0ebc1c4f2ce48e392`. All its inputs were checked again unchanged after the full run.
- Generated header SHA-256: `d508e3856e637a8e107364ad2a8fed09893a2e50ae05d99db3d4b3da37a5a082`.
- Final raw report: `/workspace/scratch/1742da7072be/a17-scanner-ac-final.json`; 60,757,299 bytes; SHA-256 `b156605e1807c0210820b5b27784f1a455c4dff694f7e6107d4efd1130183498`.
- Deterministic gzip (level 9, `mtime=0`): `/workspace/scratch/1742da7072be/a17-scanner-ac-final.json.gz`; 21,061,708 bytes; SHA-256 `362cfd051824c685ec8583ca49d246f3d6b7ff2ca5b2006c006977ce1ec90461`.
- Prior full report before status propagation repair: `/workspace/scratch/1742da7072be/a17-scanner-ac-full.json`; 60,757,299 bytes; SHA-256 `557425dacc5180481b739af81b737936dad1ed3e2faaa3ecf84606b108a3c0e3`.
- Initial fixed-warmup diagnostic: `/workspace/scratch/1742da7072be/a17-small-ac.json`; 237,271 bytes; SHA-256 `ba804cbd153d8d87018e27ab1cd8f3cbe99e437b8002eef7285e39bdd8fd9938`.
- First bounded-startup diagnostic: `/workspace/scratch/1742da7072be/a17-small-ac-settled.json`; 257,787 bytes; SHA-256 `83d44cb801a0d3139c473d8abfacbaecfa0afe61311a32a9a68c918bfa88c021`.

These are scratch execution outputs supplied to the integrator for selected durable numerical-data retention. This note retains compact exact evidence and reproduction commands; it does not claim that an untracked scratch path is already published. The raw report stores all source hashes below and its CMake cache identity/flags, precision and platform. Binary/source hashes identify inputs; the actual private build above establishes their local build relationship.

| Input | SHA-256 |
| --- | --- |
| `include/hammond/ScannerLine.h` | `c249f7c5556d6a6c8c58978928f0b860be442cb1188d35e49c59575729af00c7` |
| `include/hammond/Types.h` | `c533cc0b59838e22aff1dd081e30482df76c747407ea76d4b1788e0536a3ef7b` |
| `src/ScannerLine.cpp` | `4280db3caa3f7aa225c58a0fa64ec4ca31add55ab8bb46a27aca2deba4544336` |
| `tools/scanner_line_probe.cpp` | `4a283205949a837df8835f2b86874ee66624631d05fbdf8a6ccce7ff54e16fdb` |
| `tools/CliArguments.h` | `8ac5d91ebf66c31456159f028bce3c1c4b0dcd0c09118ac8c8d55c53a8912a47` |
| `include/hammond/detail/Decimal.h` | `ae2c63ec61e823fda198a4951e029df11184980c9bc8394142a2d46951338c42` |
| `tools/compile_scanner_line.py` | `56c60cf511144d552fdeb2708711b32469f350593b391c7619ebb92b41b6dd7e` |
| `tools/scanner_ac_reference.py` | `5472dbe96839a64e864e3d6275ea326b6a497fe5c06997f0a23a3d230763bd1e` |
| `tools/qualify_scanner_ac.py` | `33e32ca06d60a93be87fa7497f31b41be682bf2f1386d75697b29e4031a42548` |
| `docs/SCANNER_NUMERICAL_CONTRACT.md` | `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9` |
| `data/scanner-line.schema.json` | `602d3b75f316d0c0523c1ecab49204607785ce8f83508a3e0014d22793221f29` |
| `authoring_input` | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |
| `native_executable` | `c038fb6b9feb1fd3a852bfaa7ba58e5ff7b1de48032c5df777841027ddb55173` |
| `tests/test_scanner_native_ac.py` | `0ee15e83ad52ee0436b41d70538741ff426d44ee6587678afa9840350a907ec1` |

## Maintained checks and next work

The thirteen regression methods cover three actual host rates and all four process carriers; exact rational DC and independent ideal-boundary KCL identities; same-hertz failures preserved alongside passing G3; a deliberately reversed v7; failed residual and inconclusive conditioning states; null-separated phase/group-delay segments; mismatched probe identity, operation, endpoint convention and nonfinite shapes; changes to a source snapshot during execution; regular-file/alias/serialization/atomic-replacement failures; invalid CLI preservation; and unsorted/duplicated/unsupported selections. No production matrix or reference expectation is copied into the mutation checks.

This assignment qualifies the named frequency/process portion of G3 only. Full matched-step physical-state parity and the separate rotor are other assignments. G5 is blocked by the observed same-hertz result even before transient, rotating-output or filtering evidence is considered. The next numerical task is an explicitly identified alternative realization/policy investigation under the unchanged full grid and budgets, with independently converged transient and rotating references. Do not add undocumented damping, select a multiplier by label alone, change the graph identity, or silently relax the acceptance contract.

Root owns integration, shared handoff/status, source freeze, retention of selected detailed report data, commit and push. Physical specimen captures, winding/coupling/source/receiver loading, AO-28, Leslie, public scanner controls, host integration and product fidelity remain unqualified by these tests.
