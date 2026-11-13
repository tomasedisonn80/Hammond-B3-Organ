# Assignment 41 — actual native concurrent state gate

Agent: `/root/w07_a41_native_concurrency`.
Wave: 7 of the new 2026-11-13 pedal/native session.

## Assignment, ownership and source basis

Implemented the missing actual loaded-module UI/audio concurrency gate. Owned
only `plugins/vst3/tests/test_native_concurrency.cpp`,
`docs/VST3_CONCURRENCY.md` and this note. No shared status/manifest, production
source, SDK source or existing harness was modified. No commits or pushes were
performed by this worker; the parent integrates and publishes the wave.

Read `AGENTS.md`, current README/status/next-step/log context, the plan and atlas
review, the previous handoff's historical status, native processor/harness,
StateExchange contract and relevant actual atlas text on pp. 389–390, 393–394
and 400–401. Those pages require active state calls to use a verified transfer,
preserve musical versus transient state, test exhausted queues and delayed
readers, and retain actual host evidence. This worker does not claim a new
independent reading of all 500 pages; the six current session readers own that
complete coverage.

Starting published commit was
`d7b886103f8c9d4649ffa1c35930b79808217a3d`, tree
`018c3897889aaae0070f632981e0c889a35cad30`. A private `git archive` became
`/workspace/scratch/f364bc93d920/a41-source`, with only the new test and a private
native CMake overlay added. Every other archived file was compared with the
committed base and remained identical. The overlay adds the host test and
`Threads::Threads`; it does not change production compile or DSP policy.
Parent integration separately registers the test with a 240-second timeout.

Final source manifest `a41-source-final.json` lists 475 files, SHA-256
`4570565b87a0f650ea6490ba13f84e3f8e901669da1607a38410e8721c0988f3`.
The private CMake overlay is 8,721 bytes, SHA-256
`ac897ab2546151091264276aa9e2b5339a6da4b174313f0ff9183f686cb561bc`.
Root's frozen checkpoint builds and other workers' active files were untouched.

## Implemented qualification

The [native concurrency contract](../../VST3_CONCURRENCY.md) details the cases.
One UI thread performs all actual component state calls; one audio thread calls
the actual processor. The lifecycle remains stable, interfaces remain alive,
and all threads join before shutdown. There are no production hooks or direct
native Engine diagnostics.

At each of 44.1/48/96 kHz:

- Eight controlled rounds fill all four pending state slots using partial stream
  reads, destroy the caller's accepted byte storage, verify the latest pending
  save, reject a fifth state and malformed data, then reject an invalid audio
  call while preserving output, flags, queue capacity and pending save.
- A successful boundary applies the known four snapshots before expression
  automation. The following save must show acknowledged audio controls. A plain
  Engine receives the independent physical note/restore/event timeline; both
  native channels and later held-note audio compare bitwise.
- A publication-only phase requires 1,024 successful complete audio-family saves,
  followed by at least 32 callbacks while the UI performs no state reads.
- A free-running stress phase accepts 1,024 UI loads, interleaves saves and invalid
  states, retries explicit queue-full responses off audio, and checks every
  successful snapshot against a complete independently encoded family. Busy
  saves must leave the actual caller stream unchanged with zero writes.
- Every audio callback supplies all 45 independently numbered sample-zero
  controls. A separate audio-owned Engine renders its known complete pattern,
  without asking which UI states were consumed. The final drain and 512-sample
  continuation expose stale acknowledgement or lost held-note/source history.

No `HostTimeline`, `ParameterBridge`, `StateExchange` cell decoder or production
snapshot generator is used as the expected-value oracle. The host fixture's
stream reader parses returned bytes through the established bounded control
format; all resulting field values and expression bits are checked independently.

Fixed totals are 24 controlled rounds, 3,072 accepted stress loads, 3,072 required
publication-only saves, at least 96 reader-paused callbacks, 3,174 total accepted
loads, 24 rejected process calls, 462 malformed loads and 6,168 future frames.
Other counters depend on scheduling and are reported as observations.

## Actual commands and results

Toolchain: Linux x86-64, GCC 14.2.0, CMake 3.31.6, Python 3.12.14. The unchanged
SDK at `/workspace/scratch/f364bc93d920/vst3sdk` passed the project lock and
primary-license checks during each configure. Root commit and submodule pins
remain those in `data/dependencies/vst3-sdk-lock.json`.

From `/workspace/scratch/f364bc93d920`, using the task-local CMake/CTest programs
under `tooling/cmake/data/bin`:

```sh
cmake -S a41-source -B a41-build-release -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT="$PWD/vst3sdk"
cmake --build a41-build-release --target test_native_concurrency --parallel 2
ctest --test-dir a41-build-release -R '^test_native_concurrency$' --verbose --output-junit a41-release-final.xml --output-log a41-release-final.log
```

The first strict compile succeeded. An initial successful run covered load/save
stress but mostly returned pending UI copies. Review added the publication-only
phase and explicit stalled-reader progress before freezing, so the final result
does not infer publication coverage from those pending saves.

**Final Release: 1/1 passed, zero failures/skips, 0.36 seconds.** Observed 1,458
accepted callbacks, 288 zero-frame callbacks, 66,797 bit-exact frames (all audible),
10,274 queue-full results, 16,821 successful saves and 367 busy saves with untouched
streams. Successful saves included 13,670 pending and 3,103 published snapshots.
Maximum audio error was zero. All fixed requirements above passed.

A separate two-thread atomic GCC ThreadSanitizer probe compiled and ran with
exit zero. Then the same frozen source was rebuilt, including core, plugin, SDK,
loader, harness and test:

```sh
cmake -S a41-source -B a41-build-tsan -DCMAKE_BUILD_TYPE=RelWithDebInfo -DHAMMOND_BUILD_VST3=ON -DHAMMOND_VST3_SDK_ROOT="$PWD/vst3sdk" '-DCMAKE_CXX_FLAGS=-fsanitize=thread -fno-omit-frame-pointer' '-DCMAKE_C_FLAGS=-fsanitize=thread -fno-omit-frame-pointer' -DCMAKE_EXE_LINKER_FLAGS=-fsanitize=thread -DCMAKE_MODULE_LINKER_FLAGS=-fsanitize=thread -DCMAKE_SHARED_LINKER_FLAGS=-fsanitize=thread
cmake --build a41-build-tsan --target test_native_concurrency --parallel 2
TSAN_OPTIONS=halt_on_error=1 ctest --test-dir a41-build-tsan -C RelWithDebInfo -R '^test_native_concurrency$' --verbose --output-junit a41-tsan.xml --output-log a41-tsan.log
```

**ThreadSanitizer: 1/1 passed, zero failures/skips, 2.76 seconds, no detector
report.** Observed 1,397 callbacks, 276 zero-frame callbacks, 64,225 bit-exact
frames (all audible), 8,560 queue-full results, 15,116 successful saves and 110
busy saves with untouched streams. Saves included 11,956 pending and 3,112
published snapshots. Maximum audio error was zero. All fixed requirements passed.

All 178 configured translation-unit commands had the instrumenting flag; 78
object files were actually built for the requested target, and all 78 were
instrumented. `ldd` shows both host executable and loaded module linked to
`libtsan.so.2`. The module dynamic table contains 20 actual detector references.
`nm -D --defined-only` found zero exported Hammond symbols in both host test
executables, preventing host reference DSP symbol substitution into the module.
No detector suppressions, custom synchronization annotations, skipped cases or
disabled detector options were used.

## Identities

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Final test source | 24836 | `1d1aff01b8655091c3212e44068e6513064c914e491598d0262eb82f283798e2` |
| Release test executable | 309792 | `03d81590342a014f81a67ae4708873057d994985c98ea97df251a35283f0aac7` |
| Release actual HammondB3.so | 434168 | `d87353b237e52c8d1f91af27933493a4cf78ba4a06af4a96c9930c0ecec1d3ff` |
| Compiled profile | 4545 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| TSAN test executable | 4077728 | `cc9e2c715a5c943425ecd02c30621a386caaf70051b1a1375d2732f24ead8a43` |
| TSAN actual HammondB3.so | 565536 | `efd989ef8d30573a4320df0eb6e846b3c00711c3d231315fadaeb8a4b2da90c0` |
| a41-release-final.log | 1975 | `3264efabe1d8780f41dc25c0273ffaf38930a15c68ea99bb99bba809badbf996` |
| a41-release-final.xml | 773 | `a7e0a382196b5b93825254f7665ec36d33d6af848ff85586444c308638e7d76c` |
| a41-tsan.log | 1958 | `185ae3fc19a8fd80d632d4bad2a581e93716694a611f1346406ccc0b9ea15bdf` |
| a41-tsan.xml | 771 | `eb0f71170ed8e09da87c774be75eca5b54c06552bf60951fbb6542e66af484da` |

The ordinary Release module is byte-identical to the previously qualified native
module; the sanitizer module has its own identity. Logs/manifests remain in the
scratch paths above; these recorded hashes identify the executed observations
without claiming the temporary files are permanent repository artifacts. The
committed test and commands allow fresh execution, and the native hosted workflow
retains complete logs for its own runs.

## Review outcome and next step

No production defect was found in the executed scope. Final owned source matches
the tested private source byte-for-byte. The parent's concurrent macOS-framework
and Windows floating-point build repairs are separate; this test did not alter
or weaken them. Parent has registered `test_native_concurrency` with the existing
native host target, `Threads::Threads`, module/profile dependencies and 240-second
timeout. Its combined seventh-wave archive and exact hosted Windows/macOS/Linux
execution remain the next integration gate.

This finite native Release/TSAN workload supports the stated one-UI/one-audio
protocol. It is not proof for every interleaving, unsupported concurrent producers
or lifecycle mutation, callback deadlines, allocation behavior, DAW behavior,
physical organ fidelity or platform-wide sanitizer qualification. Preserve those
boundaries when updating shared status and future-agent handoffs.
