# Native smoke scheduling admission

**Admit the scheduling-only change to `test_standalone_app`.**
A24, **16 November 2026 (America/Halifax)**.
The [independent receipt](../development/2026-11-16-ui-delivery/reports/app-smoke-scheduling-admission.json)
binds source hashes, original failures, generated properties and observed order.

`RUN_SERIAL TRUE` is a justified isolation measure for this timing-sensitive
correctness smoke. `main.cpp` and its complete Python acceptance script remain
byte-identical to committed HEAD. The 600 ms workload, all assertions,
eight-second subprocess guard and 60-second CTest timeout remain unchanged.

| Retained observation | Result |
| --- | --- |
| Original affected run | 42/43; three failed subprocesses inside the app suite |
| Unchanged executable, isolated app check | 1/1; 15.42 seconds CTest wall |
| Reconfigured three-test check, requested parallelism 3 | 3/3; 43.19 seconds CTest wall |

All three original failures were inactive-title 1280×900 cases. Restored controls
were first observed at 356, 470 and 416 ms, after the exclusive 300 ms note-on
cutoff; each recorded three images and no note-on. Audio callback progress and
zero reported processing faults support UI contention over a failure in the
changed title path. Causal attribution remains an inference.

Generated CTest properties confirm serialization. The completed log places app
startup after both concurrently running raster tests finish. This single result
proves neither repeated stability nor behavior under unrelated host load.
The original 42/43 failure remains; no replacement 43/43 is claimed. Integrated
qualification, hosted platforms, real devices and callback deadlines remain
separate gates.
