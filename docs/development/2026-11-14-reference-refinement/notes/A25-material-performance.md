# A25 — Same-geometry material paint timing

Actual worker `/root/w05_a25_material_performance`, wave 5. Owned the manual
[benchmark](../../../../tests/benchmarks/standalone_material_timing.cpp), this
note and `reports/A25-*`. No production/CMake edits, shared builds, commits,
publication or child dispatch. Read AGENTS, the full plan, current scope and
checkpoint, materials timing contract, atlas-interface review and A12/A14/A22.

## Outcome

Completed nine paired cells, with **30 warmup + 300 measured draws per process**.
Every pair had identical current model/layout fingerprints and renderer settings.
The three Dimensional material cells stayed below the combined investigation
threshold. The reference Flat control initially exceeded it; the one authorized
reverse-order repeat did **not** reproduce the increase. Both observations remain
separate. No optimization or further timing run followed.

All values below are milliseconds for **paint + explicit SDL flush + software
surface present**. Median averages sorted samples 150/151; p95 is sample 285/300.

| Size / presentation / overlay | Before median | Current median | Before p95 | Current p95 | p95 change |
|---|---:|---:|---:|---:|---:|
| 960×700 Dimensional / None | 46.205 | 47.579 | 52.353 | 55.532 | +6.07% |
| 960×700 Flat / None | 11.879 | 11.772 | 13.793 | 13.563 | −1.67% |
| 1280×900 Dimensional / None | 80.940 | 82.338 | 87.785 | 90.933 | +3.59% |
| 1280×900 Flat / None | 21.138 | 21.106 | 24.926 | 23.245 | −6.74% |
| 1672×941 Dimensional / None | 109.187 | 108.250 | 128.731 | 121.008 | −6.00% |
| 1672×941 Flat / None, initial | 30.247 | 31.163 | 33.042 | 41.206 | **+24.71%** |
| 1672×941 Flat / Help | 55.689 | 41.731 | 61.931 | 47.771 | −22.86% |
| 1672×941 Flat / Audio | 58.330 | 40.867 | 65.070 | 46.321 | −28.81% |
| 1672×941 Flat / MIDI | 65.024 | 43.939 | 72.712 | 52.705 | −27.51% |
| Flat / None, sole reverse-order repeat | 30.615 | 30.057 | 35.663 | 33.114 | −7.15% |

The initial control increase was **8.164 ms**, exceeding both **15% and 2 ms**.
It occurred inside paint: final flush/present p95 was only 0.000631 ms. Current
versus before process wall/user time was 10.653/10.608 versus 10.158/10.124 s,
with 120 versus 108 involuntary context switches. The repeat changed p95 by
−2.549 ms, with 90 versus 44 switches. These observations do not establish a
scheduling cause, statistical equivalence or a persistent renderer hotspot.
The report retains fifty-frame distributions and all original samples without
averaging away the trigger.

## Exact setup and identity

Observed HEAD was `e4968b2acd37b6f79683704356350070fe2fc329`, tree
`1aff4305e347b46c659dcbc27eb524649a4c54c8`; concurrent worktree edits were preserved.
The before painter was verified byte-for-byte against `d2972a5`. Both executables
linked the same frozen current Drawing/support/UiModel/core/SDL archives, whose
hashes also match A22. A26 completed its modal Flat repair before current was
compiled; no renderer change occurred during measurement.

| Item | SHA-256 |
|---|---|
| Benchmark source | `58f6c7e0a7d940c9732b955df3b659cc84f45f4a3ac1dbb21abcc3d42d05b43a` |
| Before InstrumentView | `920f58ca287eca607632698c52a1e1fa819eb623a0be4828f082b2c6b0701912` |
| Current InstrumentView, including A26 | `428f74c4b2aae72e1ee048d1fa878575d0cd2edc064b1a3865ba40c446c30da2` |
| Shared current UiModel.cpp | `49c68995aad96aa5e316613412c93931a1082d0e4a3ad3758ac63484af963064` |
| `material-before` executable | `6e7c930bc166d88d88a0f6f4b3c64752050020d5727e75abc98d5631b4e92a47` |
| `material-current` executable | `40858109328da9bac777ace052d26af8510fd0cb3d623638cc437541b932c0da` |

Runtime: Linux 6.18.57 x86-64, glibc 2.41, exposed **AMD EPYC 9V74 80-Core
Processor**, nine available virtual CPUs. Actual affinity `[0–8]` was narrowed
to `[0]` and verified in a child, then asserted again by both runners. GCC
14.2.0 (Debian 14.2.0-19), `-O3 -DNDEBUG -std=c++20`, warnings as errors; SDL
2.32.10 at `5d249570393f7a37e037abf22cd6012a4cc56a71`. Software renderer,
RGBA32 surface, batching enabled, scale 1, full viewport, no clip, no initialized
window/audio subsystem. MIDI/VST3 are disabled in the reused native configuration.

Each process renders Play from the same fixed copied controls, six held notes,
Upper C focus and fixture device strings. No live Session/Engine runs. Drawing
initialization, warmup, hashing, sorting, JSON output and file I/O are excluded
from samples. SDL can flush internally during paint, so the separate final
flush statistic is not all backend work. Maximum surface: **6,293,408 bytes**;
maximum observed child RSS: **16,256 KiB** including the follow-up (original
matrix: 14,208 KiB). No large captures were created.

## Reproduction and handoff

Root coordinated a quiet local interval; A26/A27 deferred heavy work. The main
matrix ran **20:55:34–21:00:40 UTC**, 2026-11-14. The sole follow-up finished
**21:01:22 UTC**. Alternating pair order limited systematic order bias; virtual
host activity remained outside this task's control. There were 5,400 original
measured draws plus 600 follow-up draws, each process with its own 30 warmups.

The [compact report](../reports/A25-material-performance.json) retains exact
compile/link arguments, source/header/archive and dynamic-library identities,
settings, resource observations and interpretation. [Raw samples](../reports/A25-material-samples.jsonl)
and the [separate repeat](../reports/A25-material-investigation.json) are retained.
From the repository root, with the identified isolated binaries:

```sh
../a25-material-benchmark/material-before 1672 941 flat none
../a25-material-benchmark/material-current 1672 941 flat none
```

The reusable benchmark belongs under `tests/benchmarks/` because it is manual
qualification with machine-dependent timings, not a timing-sensitive CTest or
product executable. Root owns any CMake integration and publication. Next:
integrate this source-specific result alongside A26 and native gallery evidence.
It establishes no display FPS, audio latency, real-device deadline or
cross-device performance guarantee.
