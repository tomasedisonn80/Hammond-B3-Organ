# Assignment 13 — contact and shared-percussion engine integration

Agent: `/root/w03_a13_engine_integration`, continuation wave 03, 2026-11-13.
This assignment owns `Engine.h`, `Engine.cpp`, the event extension in `Types.h`,
and this note. It uses the independently implemented contact/percussion modules
and assignment 14's retained-control API. Shared status, CLI, saved-state tests,
CMake and publication remain with their assigned owners.

## Implemented contract

- Existing `prepare(profile, spec)` delegates to the legacy ideal-contact model;
  the overload with `const ConsoleModel&` validates and prepares local source,
  contact and percussion candidates before installing any state. Both model
  coefficients and source data are value-owned.
- Every positive sample applies stable ordered events, resolves current contacts
  and routing, reads one shared source frame, and renders with current readiness.
  Readiness and contacts advance once afterward, including disconnected output.
  Zero-frame calls apply controls/ideal targets without advancing histories.
- `EventType::Percussion = 8` preserves values 0-7. It accepts Upper only, index
  0 enable, 1 harmonic, 2 volume, 3 decay, and integer values 0/1. The entire
  request is validated before state/output mutation.
- Sustain coefficients aggregate independently evaluated contact connections.
  Releasing contacts continue to contribute after a key's target becomes up.
  Contact transitions invalidate the cache for the next sample. The default
  ideal/percussion-off path retains the previous coefficient and sample summation
  order and arithmetic.
- Upper-B eligibility is separate from the physical index-8 detector. Selected
  harmonic audio uses upper contact indices 3/4 and the existing shared sources,
  independently of drawbar gains and detector connectivity. Eligible percussion
  masks only the upper sustained 1-foot branch. Normal compensation affects only
  eligible upper sustain. No extra oscillator or duplicate sustained return exists.
- Joining notes, bank/Cancel/tablet edits and ordinary control restoration never
  reset readiness. `AllNotesOff` immediately clears the selected manual's targets,
  contacts and interrupted travel; subsequent samples recover readiness normally.
- `contact_snapshot()` returns checked copied per-key state; `contact_mode()`
  identifies the prepared contact family. `percussion_diagnostics()` returns
  `PercussionRoutingDiagnostics` with `prepared`, `readiness`, `physical_detector`,
  `eligible`, `routed_detector`, `gain` and `upper_sustain_gain`. It derives routing
  from current controls, so zero-frame edits cannot expose stale cached eligibility.

The source basis and nominal policies are in [CONSOLE_DYNAMICS.md](../../CONSOLE_DYNAMICS.md),
particularly atlas pp. 37-42, 109-138 and 447. No full console/circuit or instrument
fidelity gate is closed by this integration.

## Observed checks

Strict GCC 14.2 Release configuration used an isolated `a13-release` directory.
CMake and CTest were the existing 4.4.4 binaries. Executed:

```sh
cmake -S <repository> -B <scratch>/a13-release -DCMAKE_BUILD_TYPE=Release
cmake --build <scratch>/a13-release --target hammond_render test_engine test_controls test_realtime test_tonewheel test_numerics -j 3
ctest --test-dir <scratch>/a13-release -R '^test_(engine|controls|realtime|tonewheel|numerics)$' --output-on-failure
```

All five selected suites passed. The allocation test covers its existing tested
legacy callback cases; this is not a claim that the new enabled-percussion/travel
path has independent allocation or deadline qualification yet.

An executable comparison against the integrator's frozen baseline renderer ran
all five existing musical fixtures at block sizes 1, 127 and 1024. **All 15 pairs
had identical WAV bytes and identical renderer JSON**, including float statistics.
The baseline executable SHA-256 was
`8e781cb1df6f87443c4b6c88587cfa0e7d2bc8e23d32b5ef0a0bfb84d9ee8be4`.
These results precede the separate CLI metadata extension; later CLI work must
retain the audio regression while explicitly versioning metadata.

A separate strict C++ scratch integration probe linked the built core and passed:

- 18 exact audio/history partition comparisons: one 2,053-frame nominal-contact
  timeline at each of 44.1/48/96 kHz, partitioned into 1/17/64/127/512/1024 frames.
- Three disconnected-output comparisons, including all 122 contact snapshots,
  readiness/routing/controls, all 91 source phases, and subsequent connected audio.
- Six explicit source/audio/readiness oracles: second/third harmonic at each rate,
  silent selected-harmonic drawbars, a retained-but-masked 1-foot drawbar, upper-only
  compensation and unattenuated lower sustain. Readiness used a closed-form
  elapsed-time exponential; current-sample output tolerance was `5e-9` amplitude
  and readiness tolerance `1e-11`, engineering targets rather than physical limits.
- Zero-gap release/repress and bank-A routing preserved readiness; an actual
  subsequent ineligible sample recovered it. The bank-A source sum was checked.
- Invalid final-key contact data, invalid retained percussion enum and a valid
  event prefix followed by an invalid Lower percussion event all preserved state
  and future audio. Rejected output sentinels were unchanged.

The scratch probe and comparison report remain in the task's temporary evidence
directory for integration. Permanent independent integration tests are a later
assignment. `git diff --check` passed. No sanitizer, hosted platform, physical,
full-M3, VST3, device-audio or callback-deadline result is claimed here.

## Reviewed source identities

| File | SHA-256 at this handoff |
| --- | --- |
| `include/hammond/Types.h` | `5bf9327c4ef768f7954b160fc6f47c32534cff2c1e60b9c989a6255ddb93fc1f` |
| `include/hammond/Engine.h` | `c41c65ab153d2ecb60e9ced49e18f269d483c8643085f732b86b0e09086a7af0` |
| `src/Engine.cpp` | `3ac33dcb6d22458821c07de854aba46d6a797190325f858c352ea527ca640f5f` |

No commits or remote writes were performed by this agent. Partial-position events,
host note ownership, rate migration, measured contacts, antialiasing and complete
circuit behavior remain separate work; the new core API does not imply them.
