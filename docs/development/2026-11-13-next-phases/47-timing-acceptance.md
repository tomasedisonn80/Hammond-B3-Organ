# Assignment 47 — native timing acceptance repair

- Actual new agent: `/root/w08_a47_timing_acceptance`.
- Session: 2026-11-13 native standalone, assignment 47 of 60, wave 8.
- Parent/integrator: `/root`; this worker made no commit or push and did not
  edit shared status, next steps, manifest, ledger or another worker's files.
- Source basis: `c5452d10f3d6a9c861d1556ac030ada93b283000`, tree
  `c2b1699e1ac5750d5eb9698ded72c5b9b4c2b6a9`, plus explicit named overlays.
- Owned paths: `apps/standalone/main.cpp`,
  `apps/standalone/native_tests/test_standalone_app.py`,
  `apps/standalone/native_tests/test_standalone_workflows.py`,
  `docs/STANDALONE_APP.md`, this note, and
  `docs/reviews/STANDALONE_TIMING_REPAIR.md`.

## Implemented behavior

Smoke capture tests Upper MIDI 60 in the copied applied view that actually
painted the frame. Queuing release no longer suppresses capture of an already
observed held frame. Successful smoke with a requested screenshot now requires
a held image, and replay labels also use the painted view. Existing smoke
duration bounds, note release timing, interactive handling and replay drain
limits are unchanged. Native screenshot acceptance independently compares C4
pixels with unheld D4/E4 at reference and minimum sizes.

Resize acceptance now validates literal acknowledged command prefixes instead
of requiring a short held state at one sampled control transition. Separate
ordinary replay completion endpoints require the complete final controls with
Upper 60 held, then with the original modified key-up acknowledged and no held
notes. Exact On/Off counts, unchanged musical bytes, safety counters, final
acknowledgment and joined cleanup remain required. The workflow suite now
launches 17 processes rather than 15. Failure messages retain bounded copied
diagnostics before temporary-directory cleanup.

## Actual verification

The [full timing repair report](../../reviews/STANDALONE_TIMING_REPAIR.md)
records source/object/executable identities, commands, artifacts and limits.

- Reproduced the old screenshot defect on the first ordinary ASan/UBSan run:
  successful smoke, held image, false held label. A separate exact-source
  425 ms UI delay reproduced a missed held capture with an actually unheld
  BMP. These distinct failures were preserved.
- Clean repaired ordinary and 426 ms delayed runs both captured an actual
  held image, labeled it correctly and retained press/release, callback and
  joined-shutdown evidence within the original 600 ms smoke interval.
- Reproduced the old resize assertion failure using the real callback with
  two scratch-only public SDL delays. At 1366 ms the third control observation
  had the correct final control value, sequence 7 and no holds. The old test
  failed; the new test passed all four held/released size cases against that
  same instrumented native binary. All input and output artifacts were kept.
- Fresh Debug ASan/UBSan selected CTest gate: **3/3 passed in 50.084 seconds**,
  **38 methods / 210 native subprocesses**, zero disabled/skipped tests and no
  sanitizer reports. Counts are app 18/164, workflows 11/17 and replay
  boundaries 9/29. All 206 compiled objects, including 176 SDL C objects,
  carried ASan/UBSan/frame-pointer flags; all five archives showed both
  sanitizer runtimes.
- An incremental stale-object attempt failed 1/3 and was invalidated after
  its unchanged ordinary binary hash exposed preserved-copy timestamps.
  Its logs and JSON remain in the evidence. Qualification used a new build
  directory and a verified changed main object and executable, not that
  stale build.
- Python compilation and `git diff --check` were run for the owned changes.

Clean qualified ordinary executable SHA-256:
`6beb6705a4a967fe4cfb01a8f83fa4106dd646f08d86f250d9974f93fbd4b6b7`.
Frozen 837-file qualification archive SHA-256:
`4ed91cc80a551687f48f1e369388b13ff41bdd7a4e3171232ab4deebf94483d0`.
Evidence root: `/workspace/scratch/5ba97739b54c/a47-timing/`.

## Limits and next action

LeakSanitizer remains explicitly excluded (`detect_leaks=0`) after assignment
42's already proven ptrace failure. The earlier 92/94 full gate remains an
honest historical failure; none of its frozen artifacts were modified.
This worker qualifies the three selected suites, not the whole integrated
repository or physical audio hardware. The current-device-removal predicate,
nominal sound, 45 parameters, saved-state formats and plugin UUIDs remain
unchanged.

The integrator should review these six owned files, run the complete relevant
gate against the integrated revision, update current status and the actual
assignment record, then commit and push. Future agents should read the timing
report before using screenshots as held-note evidence or treating sampled
replay observations as a lossless event trace. Preserve the distinction between
painted state, accepted commands, acknowledged snapshots and joined shutdown.
