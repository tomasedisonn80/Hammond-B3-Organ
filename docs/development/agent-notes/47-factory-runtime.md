# Agent 47 — factory-reference runtime acceptance

## Assignment and inputs

Actual wave-08 Agent 47. Own the C++ runtime gate and its acceptance document;
leave production code, frozen profile/data, CMake and shared status to root.
Read AGENTS, README, STATUS, NEXT_STEPS, PLAN, latest development log,
ATLAS_REVIEW/ERRATA, atlas pp. 97–108, FACTORY_REFERENCE, ENGINE_API,
Engine/TonewheelBank/Profile/Types and existing test support/routing tests.

## Changes and evidence boundary

Added [test_factory_runtime.cpp](../../../tests/test_factory_runtime.cpp) and
[FACTORY_RUNTIME_ACCEPTANCE.md](../../FACTORY_RUNTIME_ACCEPTANCE.md).
Expected routes come only from the strict parser of review-a-manual.csv;
review-b-manual.csv must match. Existing Python validation separately pins both
readings and profile identities. No generated foldback formula supplies an oracle.
A separately prepared TonewheelBank supplies nominal source samples; waveform
physics is shared with production and remains independently tested elsewhere.
Expected mixing directly sums CSV-selected branches, preserving duplicates.

At 48 kHz every 61×9 cell on both manuals is rendered: 1,098 one-hot cases.
At 44.1/96 kHz each, 32 cases cover both sides of eight selected fold transitions
on both manuals. All 79 CSV source IDs 13–91 are exercised; IDs 1–12 are absent.
Six coherent cases cover low duplicate drawbars, low overlapping keys and the
complete high-key row, each manual. Eight continuous stages cover manual
addition, each Cancel, both cancelled and B reselection with held keys retained.

Every prepared engine first checks 17 silent frames; cases/stages use 128 frames.
Totals: 150,528 matching nominal frames, 19,907 silent frames and 256 rejected
probe frames = 170,691 processed frames across 1,171 engine preparations.
Reference-bank budget: 1,041 frames at 48 kHz plus 145 at each other rate.
Double/float-scaled tolerance makes no extended-long-double assumption.

In-memory wrong route (13→20) and muted source (85) each disagree on 128/128
samples, with peak errors 0.0497971664381 and 0.0299972152215. Both exceed
1,000× their normal tolerance. Peak nominal error: 1.41557759958e-08.
The only production-map access is the deliberate local wrong-route mutation.

## Executed checks, 2026-11-13

Native tool prefix: `/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/`.
Isolated build: `/workspace/scratch/c871510c69b2/agent47-factory-release`.

```sh
cmake -S /workspace/scratch/c871510c69b2/Hammond-B3-Organ \
  -B /workspace/scratch/c871510c69b2/agent47-factory-release \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build /workspace/scratch/c871510c69b2/agent47-factory-release \
  --target test_factory_runtime -j 2
ctest --test-dir /workspace/scratch/c871510c69b2/agent47-factory-release \
  -R '^(test_factory_runtime|python_test_factory_reference)$' --output-on-failure -V
```

GNU 14.2.0 strict C++20 Release build passed. Two selected CTest suites passed:
runtime 0.19 s; factory-reference suite all 20 methods. No initial failed run.
Compiled profile SHA-256 remains
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
Both manual CSV hashes and raw authoring JSON hash were checked unchanged.

## Handoff and limits

CMake already discovers the new C++ target. Root owns integration, shared status,
commit/push and hosted results. This is documentary-reference-to-nominal-runtime
routing evidence. Source-bank common-mode errors need the independent source
tests; those were not rerun here. No Debug/sanitizer/macOS/Windows run is claimed.
No pedal audio, measured source/contact behavior, AO-28/scanner/Leslie, native
host/device or physical-fidelity acceptance follows from this result.
