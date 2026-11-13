# Assignment 46 — portable recovery-boundary oracle

Actual agent `/root/w08_a46_concurrency_oracle`, assignment 46/60, wave 8.
The spawn response was interrupted, but this canonical assignment started and
continued once; no repeated agent is counted. Owned only the concurrency test,
[its actual existing guide](../../STANDALONE_CONCURRENCY.md),
[the repair review](../../reviews/STANDALONE_CONCURRENCY_PORTABILITY.md), and
this note. Root approved the existing guide name instead of the initially
suggested nonexistent `STANDALONE_CONCURRENCY_ACCEPTANCE.md`.

Read AGENTS, plan/atlas review, current status/next steps/handoffs and log, Session
contract/runtime, the entire existing test and assignment 22/35 evidence. The
Session contract's atlas basis is pp. 379–396, 425, 433–434, 442, 450 and 453;
this test repair introduces no physical model. Parent retained the actual
hosted failure under [platform follow-up](../../reviews/STANDALONE_PLATFORM_FOLLOWUP.md).

## Change and source boundary

Starting published HEAD was `5b8e2419d23fe27c51709d717812060eafd44dcc`, tree
`880682248c467a51cce14d920189cf0009b68d22`. Linux Release job `132222981693` in
run `43523378849` failed only the concurrency test's positive raced-discard
assertion, yielding 89/90 suites. Its ready flag precedes `render`; it cannot
guarantee which thread next executes. No production defect follows from that
single incidental scheduler outcome.

The repaired test retains 64 epochs and their four-callback exact reader oracle.
Two controlled schedules hold the consumer before its public render call; two
wait for completed render/ack before allowing late posts. Exact outcomes are
96 pending, 96 discarded and 192 accepted afterward. The remaining sixty
epochs retain concurrent late posts; all 5,760 attempts must reconcile as
pending, discarded or accepted after acknowledgment. Those counters are distinct
from the forced outcomes. The 8,192-post free-running phase, 16 active-overflow
rounds, two readers, exact musical/state/FIFO/accounting assertions, 256 forced
failed-read checks and portable unwind cleanup remain. No sleeps, retries,
watchdog increase, private-state hook or Session/Engine change was added.

## Executed qualification

Created `../a46-concurrency/source` with `git archive` of the published baseline,
then overlaid only the maintained test. Built fresh sibling `release` and `tsan`
directories against that immutable source. All 830 file hashes matched afterward.
Linux x86-64; GCC 14.2.0, CMake/CTest 4.4.4, Python 3.12.14. Actual test compile
commands retain `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow
-Werror`. Release uses `-O3 -DNDEBUG`; TSAN uses `-O2 -g -DNDEBUG` plus the
instrumentation below. Both native SDK options remain OFF.

From `/workspace/scratch/5ba97739b54c/a46-concurrency`:

```sh
cmake -S source -B release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build release --target test_standalone_concurrency --parallel 2
ctest --test-dir release -R '^test_standalone_concurrency$' --no-tests=error --output-on-failure -V
cmake -S source -B tsan -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBUILD_TESTING=ON \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF \
  '-DCMAKE_CXX_FLAGS=-fsanitize=thread -fno-omit-frame-pointer' -DCMAKE_EXE_LINKER_FLAGS=-fsanitize=thread
cmake --build tsan --target test_standalone_concurrency --parallel 2
TSAN_OPTIONS=halt_on_error=1 ctest --test-dir tsan -R '^test_standalone_concurrency$' \
  --no-tests=error --output-on-failure -V
```

The actual CMake/CTest binaries are in
`/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/`.
First Release gate: **1/1 pass**, 0.12 seconds test / **0.13 seconds total**.
First coherent TSAN gate: **1/1 pass**, **0.75 seconds total**, no race report.
All 23 built objects were matched to actual compile commands and carried TSAN
flags; both archives contain TSAN references and the executable links its runtime.
No uninstrumented earlier library was substituted.

The [review](../../reviews/STANDALONE_CONCURRENCY_PORTABILITY.md) retains every
major observed counter. Both runs prove the exact forced outcomes; concurrent
discards were 2,798 / 2,880 and concurrent post-ack accepted counts were zero.
The test no longer demands one particular concurrent outcome. An auxiliary
instrumentation audit initially misresolved object paths and raised
`StopIteration`; resolving compiler output paths against their recorded working
directory fixed that audit. No maintained source or successful execution changed.

## Exact identities

| Artifact | SHA-256 |
| --- | --- |
| Original published test | `ded6a4be5a4376e04f211e3ca7970b01120ec04135ff9b64bb19788185a0dff0` |
| Repaired maintained test | `637bba9c17452e129d4d236e1e679a5ed7433806909e9a421aea02ac86decc95` |
| Unchanged Session header | `0eed6c82d0cf5ffbeb0206f6f9702a93ef5a75cde6fd669b2862705dc7af84a0` |
| Unchanged Session implementation | `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae` |
| Frozen source inventory | `f0bbda12c49ff12e58859248c99f2c315bd514cfce228836543f661d2a1c9529` |
| Release executable | `106c2cec4a61eeb3b4af1782053be5519e525c5f60977f134b5dec2f2872544b` |
| TSAN executable | `cae64fc5dcf04eab54faf8684ad812541088c0ab48f04370b1a62e8c2c586447` |
| Release CTest log | `0c1393eeb190aac77676351c7a51dd72724ef31e2de02f3b18a12220d145cbb7` |
| TSAN CTest log | `5fe9eff0bdc2a9589c338ef3fe46813c6f412c45971cadf91b64d66902165bd2` |
| Both compiled nominal profiles | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

The private source, source inventory, configure/build/test logs, exact argv/time
records, compiler databases, object verification and binary/archive hashes remain
under `../a46-concurrency`. Root owns combined-source and hosted acceptance,
shared status/ledger updates and publication. This worker made no CMake,
production, shared-record or commit change. Next: rebuild the focused target in
the combined source, retain its result separately, publish and inspect actual
Linux/macOS/Windows reruns. The SDK-free Linux stress/TSAN result is not a proof
of every interleaving, physical backend behavior, callback deadlines or fidelity.
