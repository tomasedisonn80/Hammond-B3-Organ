# A32 — Immutable-data generation and dependency closure

Actual worker `/root/w06_a32_generator_boundary`, logical wave 6, 2026-11-14.
Checkout context was `35554c068492fe2b20c1f8a602d8354ae762dc42`; the accepted
preset implementation was an uncommitted overlay. That commit alone does not
identify this worker's tested source.

## Owned work and finding

Read the standing instructions, complete project plan, current status and next
steps, frozen selection contract, A13 generation implementation and A10 source
oracle. Inspected the existing 17 native-generation methods and the underlying
23-method documentary compiler suite before choosing the remaining boundary.
Those existing tests already cover duplicates, exact row/identity/limitation
checks, both readings, aliases, bounded input and atomic publication faults.

An isolated real CMake reproduction exposed stale strict-compiler bytecode after
a same-size source edit within one integer timestamp second. Root authorized a
bounded source-loader repair in `tools/compile_fixed_registrations.py`. The new
`tests/test_fixed_registration_source_admission.py` detects this in both rule
directions and in timestamp/unchecked-hash cache modes. Detailed behavior and
limitations are in [the review](../../reviews/PRESET_GENERATOR_ACCEPTANCE.md).

The original near-second-boundary probe did not reproduce stale reuse. The
corrected fixture explicitly uses quarter/three-quarter timestamps and verifies
the actual cache metadata and integer source timestamp. Only that verified
fixture supports the reported original exit-0 versus uncached exit-2 finding.
No failed unchanged rerun is presented as a production repair.

## Executed checks

Working directory:
`/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`.

```sh
python -B tests/test_fixed_registration_source_admission.py
python -B tests/test_compile_fixed_registrations.py -v
python /tmp/hammond-preset-a32/run_boundary_gate.py
```

The new regression passes **one method / four cache-direction cases / eight
subprocesses** in 0.477 seconds. The existing generator suite passes **17 methods**
in 2.287 seconds. Both successful initial tool results are recorded as observed
results; no raw transcript was captured for those two initial invocations.
A separate copy of the new regression against A31's original generator fails
all four subcases, with its complete failure log retained.

The actual CMake gate uses CMake 4.4.4 at
`/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake`, Python
3.12.14, Unix Makefiles and a fresh seven-input copy under
`/tmp/hammond-preset-a32/final-source`. Its independent minimal project defines a
marker-writing dependent target and includes the unchanged production CMake
module. The build directory is `/tmp/hammond-preset-a32/final-build`.
All **25 commands** passed their declared success/rejection expectation; **eight
builds intentionally rejected** invalid or unavailable inputs. No C++ consumer,
native SDK, musical matrix or physical device was executed by this gate.

The [machine acceptance record](reports/a32-generator-acceptance.json),
[original cache reproduction](reports/a32-cache-result.json),
[build record](reports/a32-boundary-result.json),
[source inputs](reports/a32-source-inputs.json) and
[ordered CMake output](reports/a32-cmake-transcript.txt) are retained in Git.
The exact executed [probe script](reports/a32-cmake-boundary-probe.py) retains its
historical workspace paths; it is evidence, not a general installed tool.

## Exact identities and handoff

| Identity | SHA-256 |
|---|---|
| Repaired fixed-data generator | `770eff9d031961de81d4520136d1781795a9e2b494f2a9c4a44c727b5c0f1644` |
| New regression source | `0dbb1417444d6cd314128f31d10a1c743c5462577bebc1717f8d2fba72d552a7` |
| Unchanged strict compiler | `ae54bbc196d779b2b1b369aa2c2e7db4268dd175201d6b193fed8256e6420826` |
| Seven-input manifest | `f259a11d57ed2d05ff8b5de4927302e40ff335880db65dd51ec624f0af1ec8a7` |
| Repaired generated header / unchanged A31 header | `66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6` |

Every copied production input still matches its repository bytes after the gate;
temporary mutations stayed in the isolated probe. The 2,099 output bytes equal
A31's frozen header exactly. A31 and A33 received the stable generator and output
identities so their compiled runtime results can retain their original scope.
There is no additional source-loader dependency to add to CMake or the benchmark
fingerprint: the existing generator and strict-compiler paths are already named.

The integrator owns the complete source/platform gate, current shared documents,
actual assignment accounting and publication. The new regression is picked up
by the existing Python-test glob. No root CMake, strict compiler, data, runtime,
shared status, preserved build or A31 frozen tree was modified; no commit, push
or child agent was performed. Source freshness is distinct from underlying
factory-document independence and physical calibration.
