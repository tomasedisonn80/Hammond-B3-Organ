# A36 — successful Load status clarity

Actual worker: `/root/w06_a36_status_clarity`, logical wave 6 of this requested
60-worker, ten-wave session. Read repository instructions, complete M0–M9 plan,
current session/checkpoint, workspace/geometry/inspection contracts, runbook,
A30-G2 and relevant main/UI/inspection paths before changing production.

**Result:** one literal in `apps/standalone/main.cpp` now says **Loaded saved
controls.** A34 explicitly released source and `build-native` after its capture;
A36 then held the shared build exclusively through the bounded rebuild and
observation. The other 326 recorded paths, linked libraries and build settings
were unchanged.
No audio/state/algorithm/ABI, model, units, error handling or test-target change.
No staging or commit; root owns integration/publication. A36 owns this note,
[the review](../../reviews/INTERFACE_STATUS_CLARITY.md) and `reports/a36-*`.

## Exact setup and execution

Working directory: `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`.
Reused Release build with standalone/MIDI enabled, VST3 disabled and SDL ALSA
disabled; native RtMidi ALSA remains compiled. Toolchain: GCC 14.2.0,
CMake 4.4.4, Python 3.12.14 and Pillow 13.0.0. The [build record](reports/a36-build.json)
pins source files, dependency revisions, linked archives and generated build
inputs. It records source and linked-input stability, not a fresh full-suite pass.

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/601951e27dc3/build-native \
  --target hammond_standalone --parallel 2
python3 docs/development/2026-11-14-interface-continuation/reports/a36-load-observation.py \
  --executable /workspace/scratch/601951e27dc3/a36-status-bin/hammond_standalone \
  --expected-sha256 bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2 \
  --output docs/development/2026-11-14-interface-continuation/reports/a36-load-evidence
```

The pinned executable was copied from the rebuilt app before the replay.
Reproduction requires a fresh output path. The helper uses isolated temporary
state/input paths, `SDL_AUDIODRIVER=dummy`, `SDL_VIDEODRIVER=dummy`, and a
nine-second process deadline. Exact subprocess arguments and all input/output
hashes are retained in [the observation](reports/a36-load-evidence/result.json).
One native run passed: acknowledgment at 2189 ms; one inspected 960×700 Service
PNG at 3162 ms shows the corrected notice beside CURRENT SNAPSHOT with pending
false. The saved state remains byte-identical to A30; the held Upper note survives
Load and releases later. The BMP was removed only after decoded PNG equality.

The [final record](reports/a36-status-clarity.json) preserves A30's original
failure and separates executed checks from source-only semantics. A23/A28 gates
were not repeated. Native MIDI scoped-release wording remains an unexecuted
review candidate. A36 released source/build immediately after observation;
**A37** should continue the final operator flow on the exact new executable.
Physical devices, display/DPI, accessibility, deadlines and fidelity remain
outside this dummy-driver observation.
