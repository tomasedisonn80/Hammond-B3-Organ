# A26 — Native calibration lifecycle acceptance

**Actual assignment:** `/root/w05_a26_native_calibration_lifecycle`, wave 5.
Read the complete standing instructions, plan, expression-calibration and channel-mode contracts, session handoff, and A16/A18/A22/A24 evidence. Production remained frozen; only the three assigned native-test files and this note changed. Closing repository base: `ff41d412d03f2c5767aa4057b29fa8ec1627449b` plus these uncommitted fixture files.

The fixture includes unchanged `main.cpp` with renamed entry points and calls its real `guarded_application`. A separately compiled unchanged `MidiDevice.cpp` uses an isolated RtMidi facade. Discovery and transport share a mutex-protected, bounded 4096-event log; callback offers occur synchronously at native API boundaries. Real SDL dummy audio callbacks, native discovery, UI replay, snapshots, and A22 exact public schemas supply the acceptance evidence.

**Passed:** 9 tests, 10 actual subprocesses, 7 native lifecycles in **20.304 seconds**. Healthy identical Apply preserves generation/epoch and held notes. Changed calibration, routing and exact port retire all three MIDI owners and reopen only after observed release acknowledgment. Selected/configured/active/pending states remain distinct; Apply leaves expression unchanged until another CC11. No-input Apply retains settings. Failed activation discards three admitted prefix packets; a later native fault discards two. Both require explicit recovery, retain failure history, and therefore deliberately return replay failure. The fault releases MIDI owners while the original UI owner survives until its key-up. Every opened transport closes and cancels; all dependency clients are destroyed. Close/admission and counter assertions passed. No production defect found.

Commands executed from the repository:

```sh
python3 ../a26-checks/build_fixture.py
HAMMOND_STANDALONE_CALIBRATION_PROBE=/workspace/scratch/5b7d983ac078/a26-checks/hammond_standalone_calibration_probe HAMMOND_NATIVE_CALIBRATION_EVIDENCE=/workspace/scratch/5b7d983ac078/a26-checks/evidence-attempt1 python3 apps/standalone/native_tests/test_standalone_native_calibration.py
git diff --check
```

GCC 14.2 Release/C++20, strict warnings including `-Werror`; shared libraries remained read-only. `../a26-checks/` retains commands, library/source hashes, original fixture-only deprecated-path compilation failure, successful build/test logs, diagnostics, scripts and bounded traces (4.7 MB total). Final source-hash recheck passed.

- `main.cpp`: `937b837d4ef4317d02ea2862ac34dc95031c73f0f32719b0924de29f4b721027`
- `MidiDevice.cpp`: `48ee8dbe72a1a243fcc3bc1037df782690894cb26ef2291ba253611b48bfc324`
- Fixture binary: `e498c86aa18aa21128b05e54a769e1da4ef7b9dccae6d39c42db9575b6c16378`

**Next:** root wires the supplied native-only CMake/CTest contract and verifies the integrated target. No production hooks, failed-close/quarantine/leak exceptions, hardware, OS callback concurrency, timing-deadline, sanitizer or cross-platform qualification are claimed.
