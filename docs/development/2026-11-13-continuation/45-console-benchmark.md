# Assignment 45 — explicit console and owned-input benchmarks

Agent: `/root/w08_a45_console_benchmark`

Date: 2026-11-13 UTC. Continuation wave 08, assignment 45 of 60.

## Scope and implementation

Changed only `tools/benchmark.cpp`, new `tests/test_console_benchmark.py`,
`docs/BENCHMARKING.md` and this note. The integrator supplied the requested
benchmark test environment/dependency in CMake; this worker did not edit CMake,
shared status files, the index, commits or remote refs, and spawned no subagents.

The explicit `console_motion`, `owned_input` and `console_all` selections use
`hammond-console-benchmark-v1`. Legacy `all` still selects exactly its original
four cases and retains the original report fields, defaults and meanings.
Successful report values remain deterministic apart from elapsed observations.

Both new cases prepare nominal contacts and shared percussion, set all selected
drawbars to eight and flush On/Second/Normal/Fast percussion. Their 22 setup
events create no notes or owners and advance no frame. All input arrays, output
and timing storage are constructed before warmup. Absolute call numbering
continues through warmup into recording without resetting musical state.

- Direct console motion alternates prebuilt full-press/release `KeyPosition`
  arrays, one command for each of the 122 manual keys, all at offset zero.
- Owned input cycles first owners on, second owners on, first owners off and
  second owners off. Every call consumes 122 typed host messages. The four
  resulting owner counts are 122, 244, 122 and zero; only the first acquisition
  and final release emit 122 physical events. This uses the real transactional
  `process_owned_notes()` facade with sole note authority.

The new report identifies model versions, actual timed API, input-event domain,
separate host/direct and physical counts, warmup counts, boundary owner/key
counts, final readiness and a tracked primary key's motion/contact observations.
Every result is checked outside timing. `console_all` retains the existing
per-case bounds and admits at most 20,000 positive calls and 2,097,152 frames.
No speed threshold, deadline assertion or fabricated machine identity was added.

The source basis is the supplied atlas pp. 379–390, read for this assignment.
It separates arithmetic work from observed timing, bounded ownership from host
claims, and correctness instrumentation from named-machine deadline campaigns.
The public [benchmark contract](../../BENCHMARKING.md) records the exact schedules,
field semantics, timing exclusions and reproduction commands.

## Observed stdout defect and repair

The qualified wave-six benchmark returned **exit 0 with empty stderr** when its
small JSON report was redirected to `/dev/full`. A portable readonly-file sink
then reproduced the same false success for both the report and `--help`; existing
sink bytes were unchanged. Buffered output errors occurred after the old code's
last stream-state check.

The owned benchmark now explicitly flushes stdout before checking/reporting
success for JSON and help. Permanent portable regressions assign a readonly
file handle to stdout and require nonzero exit, a stdout diagnostic on stderr,
and unchanged file bytes. Both pass. The successful report contract is unchanged;
this repairs an observed reporting failure rather than relaxing acceptance.

## Coherent qualification and results

Qualification used immutable source tree
`b9146546fcf756360e1da89d6698c4999359579f`, overlaid with the frozen benchmark and
new test plus the integrator's current CMake file. The CMake overlay contains the
test registration and preceding install work; only the benchmark build and its
focused test were qualified here. All core headers and their library came from
the same archived tree. The separate full combined gate belongs to the integrator.

Strict GCC 14.2.0 Release compilation passed. The final focused gate passed
**1/1 CTest suite in 0.70 seconds: six Python methods, 33 actual CLI calls and zero
skips**. No new production compile failure or failing acceptance assertion was
observed. An initial successful test pass was followed by one explicit no-argument
default check; the final test file is the one identified below.

The permanent tests check both report schemas, all three supported rates,
minimum and maximum block sizes, maximum unsigned 64-bit seed, exact call/frame/
event/owner accounting, deterministic sinks, individual case selection, excessive
work and malformed input rejection, and the stdout repair. Independent rational
press/release calculations check final position, recorded motion counts and
contact-bit transitions. Maximum observed position error was
**`1.1102230246251565e-16`**, within the `2e-14` tolerance. Timing assertions check
finite nonnegative ordered statistics and stated arithmetic, with no speed bound.

A separate comparison invoked the previous qualified binary and the new binary
with the same compiled profile, 48 kHz, block 64, warmup 2, iterations 3 and seed
71. After removing only the timing observations and their interval fractions,
**all four legacy reports agreed**, including the complete remaining fields and
sample/source-phase checksums. This is a bounded same-toolchain compatibility
observation, not universal byte identity across platforms.

| Frozen identity | SHA-256 |
| --- | --- |
| `tools/benchmark.cpp` | `eb7e51a7dda1a65b2b312b2fd611ad186843006ecd0bbbf539471394143e95cc` |
| `tests/test_console_benchmark.py` | `c22d2beab08477838f0ac03bf0d2ae16cbfed05a8d485c1110577557305fa743` |
| Integrator CMake overlay | `3ebc6ef9e37e3fc3b3ad26e4908e4f852ec0329926d63b5d63234fc7b557b1e1` |
| Qualified benchmark executable | `5063270b9fef39e596390428b47d47cacd98acc7a2751df024b70b38c8b25e01` |
| Prior qualified benchmark executable | `63d710d315befdacf6b13e1204ef1755e271eb76cb82a8cb18d21cdda01b26d3` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

Commands actually run after archiving and applying only those overlays:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/a45-benchmark-qualification/source \
  -B /workspace/scratch/60e8291da354/a45-benchmark-qualification/build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a45-benchmark-qualification/build \
  --parallel 3 --target hammond_benchmark
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a45-benchmark-qualification/build \
  --output-on-failure -R '^python_test_console_benchmark$'
```

The scratch directory retains `snapshot.json`, `legacy-comparison.json` and the
CTest diagnostic log for this observed run. Permanent tests contain no scratch
paths. Future qualification must rebuild its actual retained revision rather
than depend on these temporary files or assume the earlier binary still exists.

## Next gate and limits

Integrate the four owned files with the root's CMake registration and the remaining
wave-eight work, qualify an exact combined staged tree, publish under the standing
workflow and observe its hosted matrix. This focused local check does not qualify
Windows/macOS, sanitizers, actual hosts/devices, C/libm allocation, concurrency,
cold first calls, long-tail timing, multi-instance load or a physical instrument.
The workloads exercise declared nominal behavior and report observations; they
do not establish a worst-case scheduling bound.
