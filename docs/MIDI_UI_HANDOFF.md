# MIDI and native interface handoff

This is the operational entry point for the `2026-11-14-midi-ui` continuation.
Read [STATUS.md](STATUS.md), [NEXT_STEPS.md](NEXT_STEPS.md), the latest
[development log](DEVELOPMENT_LOG.md), [scope](MIDI_UI_SCOPE.md) and actual
[assignment manifest](development/2026-11-14-midi-ui/assignments.json) before
choosing new work. The manifest records actual workers; it is not a plan that
may be marked complete in advance.

## Implemented product boundary

The current application plays the existing nominal dry organ. The optional
RtMidi 6.0.0 input uses ALSA, WinMM or CoreMIDI according to the configured
platform. A fixed device inbox separates the native callback from the main
thread, which remains the sole Session command producer. Default wire channels
are Upper 1, Lower 2 and Pedals 3. Device owners remain separate from UI owners.
Faults retire stale packets and release device-owned notes; reconnect requires
an explicit action after retirement is acknowledged. Receipt timestamps are
diagnostic, with admitted events applied at audio callback boundaries.

The [input contract](MIDI_INPUT.md), [backend lifetime contract](MIDI_BACKEND.md)
and [synthetic replay contract](MIDI_REPLAY.md) specify the exact supported
messages, bounded work and failure behavior. The synthetic path drives the
actual native application while identifying itself in diagnostics; it does not
qualify an OS MIDI callback or physical controller.

The native canvas uses the atlas cover/page-409 composition, verified decorative
pixels and live controls. All 45 sound parameters, `B3CONTROLS3`, 61+61 manual
keys, 25 pedal keys and retained banks remain unchanged. The cabinet is
illustrative; scanner and rotary audio remain separate tracks. The
[reference specification](REFERENCE_UI_DESIGN.md),
[independent comparison](reviews/MIDI_UI_REFERENCE_REVIEW.md) and
[initial actual gallery](../examples/demos/standalone-midi-ui-v1/README.md)
retain exact source identities and visible differences. Later corrections must
produce a new gallery rather than rewriting an earlier captured source.

## Build, operate and verify

Follow [MIDI_UI_RUNBOOK.md](MIDI_UI_RUNBOOK.md) for platform prerequisites,
explicit pinned dependency acquisition, normal source builds, device selection,
channel routing, saved controls and recovery. The ordinary default build requires
neither SDL nor RtMidi. Enabling the native window requires the separately
acquired locked SDL checkout; enabling MIDI additionally requires the locked
RtMidi checkout. Configure does not fetch either dependency.

Use [STANDALONE_CI.md](STANDALONE_CI.md) for the current hosted matrix and
[STANDALONE_INSTALL.md](STANDALONE_INSTALL.md) for the fresh-prefix component.
The package contains 13 files with MIDI disabled and 17 with it enabled,
including exact reference/font/dependency provenance and capability metadata.
An installation is a byte-preserving local staging operation; it is not an
installer, runtime bundler, signing or distribution-clearance result.

Always build the matching test inputs before CTest. For a configured native
build, the required bounded application gate is:

```sh
cmake --build build-standalone --config Release --target hammond_standalone_test_inputs
ctest --test-dir build-standalone -C Release -R '^test_standalone_' \
  --output-on-failure --no-tests=error
```

Run the complete ordinary suite separately for a default configuration. A
filtered native result does not replace the full core/tooling gate. Preserve
original failures, platform capability distinctions and the source identity of
every result. The session reports identify the local toolchain and the explicit
SDL ALSA compilation workaround; that workaround must not enter hosted real
backend gates. The local executor also blocks ordinary LeakSanitizer through
ptrace, so limited ASan/UBSan runs must say when leak detection is disabled.

## Current continuation and publication

The current session is still in progress. Its first source-review checkpoint is
`7b36cfac2565397191b3df5e07112611e7f1b0e1`. The
[publication record](development/2026-11-14-midi-ui/reports/publication-checkpoints.json)
distinguishes local commits, equivalent repository commits, prepared objects and
actual observed branch publication. Inspect the current remote before writing;
do not infer the branch head from a historical document.

Finish independent native MIDI acceptance, lifetime and portability review,
observed reference refinements, coherent source qualification and hosted checks.
Keep the current README image tied to the latest reviewed application capture.
Then reconcile all actual worker notes and the exact source/test/package records,
update shared status and concrete next steps, and publish with an expected-head
guard and no force update. Verify the fetched commit and tree after publication.

Physical controller/audio acquisition, actual display and assistive-technology
acceptance, scanner/rotary integration, specimen fidelity, and signed release
remain separate tasks with their own required inputs. The complete
[M0–M9 plan](PLAN.md) remains the project plan after this session closes.
