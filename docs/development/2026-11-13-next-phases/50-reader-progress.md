# Assignment 50 — deterministic reader participation and progress

Actual agent `/root/w09_a50_reader_progress`, assignment **50/60**, wave **9**,
13 November 2026. Its initial spawn response was interrupted, but this canonical
worker started and continued once; no replacement or duplicate agent is counted.
Owned only:

- `apps/standalone/tests/test_standalone_concurrency.cpp`
- [STANDALONE_CONCURRENCY.md](../../STANDALONE_CONCURRENCY.md)
- [STANDALONE_READER_PROGRESS.md](../../reviews/STANDALONE_READER_PROGRESS.md)
- This assignment note.

Read the standing rules, current standalone scope/status/next steps, plan and
atlas review, Session contract and relevant implementation, the entire current
concurrency test, guide and assignment 46's repair/evidence. The source remains
the Session contract's atlas pp. 379–396, 425, 433–434, 442, 450 and 453; this is
a test-oracle repair and introduces no physical model. An initial oversized
combined read was truncated, so the test and relevant instructions were read
again in smaller complete chunks before editing.

## Failure, scope and implemented change

Starting published source was `649b12c7d1faa7601fde1019e913347c65a6634a`, tree
`cf63327d857b02029e8c5c6f406cab3d3c6890d1`. Root retained Linux Release run
`43526206646`, job `132232481835`: **89/90 suites**, **71.21 seconds**, with the
single concurrency failure `reader.active_reads > 0` at former line 328.
Earlier successes in other jobs did not establish that every reader must be
scheduled during the activity flag's interval.

The audit covered every positive reader-progress/overlap threshold, including
free-running producer observations and flagged deferred overflows. Root
approved explicit reader handshakes and one controlled after-callback overflow
round. Every reader now proves exact initial and changed/final publications,
with release/acquire acknowledgments and full field comparisons while the
consumer is quiescent. The intermediate reads retain their entire independent
coherence and failed-read immutability checks. Non-atomic statistics remain
reader-owned until after join. The activity-flag metric excludes forced
checkpoints and is reported as an observation, with no positive requirement or
claim of execution inside `render`.

All 8,192 ordered posts remain free-running between start/end checkpoints. All
64 recovery epochs / 256 callbacks remain, including assignment 46's controlled
**96 pending, 96 discarded and 192 after-ack accepted** outcomes and complete
classification of **5,760** concurrent attempts. Of the existing 16 overflow
rounds / 48 callbacks, the first now explicitly waits for callback return before
filling the queue and proves pending closure until the next callback; the other
15 remain raced. Exact controls, holds, sequences, FIFO Panic, counter identities,
256 forced exhausted reads and the portable unwind probe remain. No production
code, CMake, shared ledger, new dependency, sleep, timeout or watchdog limit was
changed. Assignment 46's immutable source/evidence was read only.

## Coherent executed commands and results

Created `/workspace/scratch/5ba97739b54c/a50-reader-progress/source` by archiving
the named published commit and overlaying only the maintained test. Inventoried
all 842 source files before building. Separate fresh Release and TSAN build
directories use that same frozen source. The actual CMake and CTest binaries are
under `/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/`.
Commands below use those binaries via their conventional names.

From `/workspace/scratch/5ba97739b54c/a50-reader-progress`:

```sh
cmake -S source -B release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build release --target test_standalone_concurrency --parallel 2
ctest --test-dir release -R '^test_standalone_concurrency$' --no-tests=error --output-on-failure -V
taskset -c 0 ctest --test-dir release -R '^test_standalone_concurrency$' \
  --no-tests=error --output-on-failure -V
cmake -S source -B tsan -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBUILD_TESTING=ON \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF \
  '-DCMAKE_CXX_FLAGS=-fsanitize=thread -fno-omit-frame-pointer' -DCMAKE_EXE_LINKER_FLAGS=-fsanitize=thread
cmake --build tsan --target test_standalone_concurrency --parallel 2
TSAN_OPTIONS=halt_on_error=1 ctest --test-dir tsan -R '^test_standalone_concurrency$' \
  --no-tests=error --output-on-failure -V
```

All configure, build and test invocations succeeded on their first run. Normal
Release passed **1/1**, 0.16 seconds test / **0.17 seconds total**. Linux CPU-0
Release passed **1/1**, 0.53 seconds test / **0.54 seconds total**. TSAN passed
**1/1**, **0.89 seconds total**, with no race diagnostic. Linux x86-64 kernel
6.18.57 / glibc 2.41, GCC 14.2.0, CMake/CTest 4.4.4, Make 4.4.1, Python 3.12.14;
strict C++20 project warnings with `-Werror`. The constrained run selected an
actually permitted CPU from affinity set 0–8; it is a Linux-only experiment.

The [review](../../reviews/STANDALONE_READER_PROGRESS.md) retains all major
workload counters and exact checkpoint revisions. The constrained execution
recorded zero recovery/overflow activity-flag attempts for both readers,
zero flagged/deferred overflow observations and all 5,760 concurrent late
attempts accepted after acknowledgment. Every forced checkpoint and boundary
still passed. This directly exercises a legal schedule rejected by the former
positive metrics, without retries or extra sleeps.

Matched all 23 actual TSAN objects to their compiler commands: 19 core units,
Session, UI model, state files and this test. Every unit carried both required
instrumentation flags; both archives reference TSAN and the executable links
`libtsan`. No stale library was linked. The first auxiliary inventory audit
incorrectly assumed profile compilation would add no files and rejected two
generated `tools/__pycache__` bytecode entries. Corrected that audit to report
the additions explicitly and verify every inventoried source path/hash/mode
unchanged. This was an audit assumption failure; no fixture/source/test gate
was modified or rerun to obtain a pass.

## Retained source and artifact identities

| Artifact | SHA-256 |
| --- | --- |
| Original published test | `637bba9c17452e129d4d236e1e679a5ed7433806909e9a421aea02ac86decc95` |
| Repaired maintained test | `a309882bb248add7d2dc1e6bbec679482d66d162c2d1eb54b4c455d5194355e3` |
| Unchanged Session header | `0eed6c82d0cf5ffbeb0206f6f9702a93ef5a75cde6fd669b2862705dc7af84a0` |
| Unchanged Session implementation | `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae` |
| Frozen 842-file source inventory | `e591200b7165d8f03ed32aaf7bcab3a6137c0c6b95c44128703af1a2fc86bfeb` |
| Release executable, also used under CPU affinity | `0f5252feb0c1f322cfa657a3601e627f7156227236229b6b0ec517de1152b676` |
| TSAN executable | `3e32fbe9eb2bb655fff592540c2f74a3f18703b63ff91532979e42324270db01` |
| Release CTest log | `3afeab2e3581f724aa9ae06144be1c6859e912585f496a0639b448178fc95cf9` |
| One-CPU Release CTest log | `a1b4a0f91c6a2c9839fc437da67ba28874d2f109f0a491ca6d95e38673ae37dc` |
| TSAN CTest log | `86a3ee27a11b16761c6b8ba98f57d6e3351ba1a57045c117075f8c690210d02b` |
| Both compiled nominal profiles | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

The private directory retains the frozen source, inventory, configure/build/test
logs, exact argv and elapsed-time records, compiler databases, binary/archive
hashes, generated-cache identities and object/runtime verification. Other workers'
unrelated app changes and the shared session ledger were left to their owners.

## Handoff

The code was frozen and its exact hash reported to root before qualification;
all three first results and the zero-flag constrained schedule were reported as
soon as observed. Root owns shared status/next-step/log/manifest updates,
combined-source acceptance, commit/push and actual hosted reruns. Next rebuild
the focused concurrency target in root's coherent assembled source, require its
CTest pass, then inspect Linux/macOS/Windows publication jobs without treating
these local results as platform closure. No commit or push was made by this
worker. Bounded stress and one constrained schedule do not prove every
interleaving, weak-memory hardware, device threads, callback deadlines or
physical fidelity.
