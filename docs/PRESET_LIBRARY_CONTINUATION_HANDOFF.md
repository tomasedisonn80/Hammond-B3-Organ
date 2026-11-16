# Portable registrations and reference apron: continuation handoff

16 November 2026. This continuation delivers a usable, bounded M9 preparation
and audition path plus one reference-derived visual surface. The playable
instrument remains a nominal dry organ. **Literal whole-interface 1:1 remains
unmet and unwaived.** This document records the current delivery; the complete
[M0–M9 plan](PLAN.md#milestones-and-exit-evidence), [status](STATUS.md) and
[next actions](NEXT_STEPS.md) retain every engineering and release exit.

## Source and provenance

The sole writable checkout is
`/workspace/scratch/3edffb787db3/Hammond-B3-Organ`, started from
`54df95fe343d417dd89bb7a91f85e4f51c08dfe7`. Read the
[session](development/2026-11-16-preset-library-continuation/README.md),
[checkpoint](development/2026-11-16-preset-library-continuation/CHECKPOINT.md),
[decisions](development/2026-11-16-preset-library-continuation/ROOT_DECISIONS.md)
and [actual ledger](development/2026-11-16-preset-library-continuation/assignments.json)
before resuming. **All sixty new distinct workers are accepted in ten waves of
six**; the [strict record check](development/2026-11-16-preset-library-continuation/reports/final-session-validation.json)
passes with zero errors. Earlier workers and repeated follow-ups supply no new credit.

The [verified follow-up publication](development/2026-11-16-preset-library-continuation/reports/followup-publication.json)
is `cc6be852d616ec5887485e3fccc39ddb1db22006`, tree
`201e38b05901fa30e3d053b9c245829818a5b52e`, sole parent
`20739f6280b95e567e84615d5c5aee443fc3b93d`. Its content equals reviewed local
commit `503ed724eaeb3c31eae3c6f31b31cc9a2acd9eb3`; provider metadata differs.
The closing documentation is separate from that implementation tree. The
[final hosted admission](reviews/PRESET_FINAL_HOSTED_ADMISSION.md) observes ten
successful Linux/Windows jobs and three macOS cancellations without a runner or
steps. All three workflow aggregates report failure; full platform acceptance
remains open, with no cancellation cause established.

Six fresh readers covered all 500 atlas pages under the
[coverage receipt](development/2026-11-16-preset-library-continuation/reports/atlas-reading-coverage.json).
The unchanged PDF SHA-256 is
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
The [delivery crosswalk](reviews/ATLAS_DELIVERY_CROSSWALK.md) distinguishes atlas
research waves, product milestones and staffing waves. Reading supplies no
missing measurements or independent verification of every cited source.

## Implemented behavior

[`hammond_registration`](../tools/registration.cpp) lists, inspects, imports and
materializes explicit flat libraries without SDL, a display, audio device or
profile. Its [shared input reader](../tools/ControlFileInput.cpp) accepts regular
files up to 16,384 bytes, refuses leaf symlinks/reparse points and malformed
payloads, and preserves the destination on failure. Readers 1–4 remain available;
new output is canonical `B3CONTROLS4`. Inspection creates nothing. Import and
materialize publish new files without replacement, with input revalidation and
explicit JSON outcomes. This does not complete the existing native browser.

| Operation | Actual expression semantics |
| --- | --- |
| Registration materialization | Requires valid `--current FILE`; takes only its expression and every other saved field from the selected entry. |
| Performance materialization | Forbids `--current`; takes the complete entry, including saved expression. |
| Renderer `--controls`, generic native Load or `--state` | Restores the complete file, including expression, regardless of suffix. |

Both materialization scopes create `.b3performance` output. The
[renderer](../tools/render.cpp) restores all banks, selectors, routes, retained
fixed modes, pedals, percussion and expression before score events, including
frame-zero events. Its schema-6 provenance reports the full initial canonical
snapshot and `full-state-including-expression`; later score overrides remain
separate. Explicit drawbar/pedal/percussion options conflict with `--controls`.
Notes, phase, contact/percussion histories and clocks are not saved.

The [compatibility review](reviews/REGISTRATION_COMPATIBILITY_ADMISSION.md)
preserves 91 shared free-running sources, 47 parameter identities, plugin UUIDs,
`B3CONTROLS4` and readers 1–3, four banks, 147 playing keys and 24 reversed
presets. UI/file preparation introduces no Engine route or sound-state migration.

The [pack](../data/registrations/starter-v1/README.md) contains twelve original
proposed, unmeasured software recipes in 24 paired canonical files. Its
[native generator](../tools/generate_starter_registrations.cpp), literal oracle,
manifest and [provenance](development/2026-11-16-preset-library-continuation/reports/starter-provenance.json)
retain their identities. They supply no factory, artist or measured-profile
claim. The [32 original one-second auditions](reviews/STARTER_AUDIO_PROVENANCE_ADMISSION.md)
at 48 kHz include sixteen identical whole-WAV suffix pairs. Those pairs test full
restore; they do not test expression-preserving materialization. All 101 original
files remain in the linked archive, with extraction instructions in its
[reader](development/2026-11-16-preset-library-continuation/reports/starter-auditions.md).

## Setup and practical use

A fresh checkout needs C++20, CMake 3.21+ and Python 3.10+. For a new headless
configuration, run from the repository root:

```sh
cmake -S . -B build-registration -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=OFF -DHAMMOND_BUILD_STANDALONE=OFF \
  -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_ENABLE_MIDI=OFF
cmake --build build-registration --config Release \
  --target hammond_registration hammond_render --parallel 2
```

Use [guide sections 2–4](REGISTRATION_GUIDE.md#2-inspect-and-import-selected-recipes)
for exact list/import/materialize/render commands, score precedence and output
paths; sections 5–6 document migrations, exits and failures. Windows and
multi-configuration builds require the documented executable location adjustment.
The [normal native setup](../README.md#build-and-launch-the-native-application)
retains real desktop/audio backends; it differs from dummy-SDL recovery here.

[Installation](REGISTRATION_GUIDE.md#7-install-explicitly-and-relocate) explicitly
selects `RegistrationTools` and `StarterRegistrations`: two tool/guide files plus
26 pack files. Components are copy-only, excluded from ordinary installation,
and create-only; existing targets refuse replacement or merging. They run no
generator and import no user library. Renderer/profile installation separately
uses OfflineTools. A late copy failure can leave partial output; inspect before
retrying. CLI report-output failure can follow a committed save.

Conservative alias protection can refuse distinct Unicode sibling directories.
The independently admitted layout places both library and current snapshot
beneath ASCII `inputs/`, for example `inputs/Ma bibliothèque Ω` and
`inputs/Current état.b3controls`, with destinations beneath
`outputs/Auditions été`. Quote paths, use fresh destination names and retain
`ProtectedPath` refusals; do not disable protection. The
[first-use review](reviews/REGISTRATION_FIRST_USE_ADMISSION.md) preserves the
original refused journey separately from its successful 14-process repeat.

## Executed evidence and retained failures

| Observation | Retained result |
| --- | --- |
| [Earlier coherent implementation](development/2026-11-16-preset-library-continuation/reports/w04-coherent-qualification.json) | 230/230 CTests, 229.18 seconds. |
| [Full integrated run](development/2026-11-16-preset-library-continuation/reports/w07-integrated-qualification.json) | 234/235, 225.77 seconds; copied audition links failed. The later focused integrity repair passed, without relabeling the full run. |
| [Clean SDK-free configuration](reviews/HEADLESS_REGISTRATION_BUILD_ADMISSION.md) | Eight targets, 12/12 focused CTests in 5.50 seconds, exact 2+26 installed files and restricted-environment inspection. |
| [Windows raw-path guard](reviews/WINDOWS_REGISTRATION_PATH_ADMISSION.md) and [hosted execution](reviews/PRESET_FINAL_HOSTED_ADMISSION.md) | Six affected Linux CTests passed in 11.33 seconds with identical binaries. Exact-source Windows core passes 202/202 in 206.72 seconds; native passes 61/61 in 462.22 seconds. Both guard tests, actual native Load, Unicode-checkout generation and package archival pass. |
| [Final hosted matrix](development/2026-11-16-preset-library-continuation/reports/root-final-hosted-observation.json) | Ten successful Linux/Windows jobs, including both sanitizer jobs, native MIDI configurations, VST3 and full R4; native sanitizer passes 28/28. Three macOS jobs cancelled without execution; workflow aggregates report failure. |

The original first publication's
[final hosted observation](development/2026-11-16-preset-library-continuation/reports/first-ci-final-observation.json)
records **six successes, four failures and three macOS cancellations**. Linux
Release/sanitizers exposed copied-report links; Windows core/native also exposed
the ambiguous-path assertion. Cancelled macOS jobs have `runner_id: 0` and no
steps: no macOS execution or cancellation cause is established. The Windows
repair checks requested spellings before normalization at both storage entry
points, preserving resolved checks and exact `.`/`..` navigation. Original
failures and thresholds remain; no all-platform pass is claimed.

Earlier generator qualification retained its 19/20 false-refusal failure before
the independently admitted [ASCII-component distinction repair](reviews/REGISTRATION_PATH_ADMISSION.md).
That proof never promised arbitrary Unicode sibling admission. Separate repairs
made [late audition-report failure](reviews/STARTER_FAILURE_BOUNDARY_ADMISSION.md)
truthful while preserving partial artifacts and added missing
[installed apron provenance/notices](reviews/PRESET_ASSET_PROVENANCE_ADMISSION.md).
Their original observations and bounded qualification remain distinct.

Independent [native Load](reviews/STARTER_NATIVE_LOAD_ADMISSION.md) uses four
actual dummy-SDL processes and two materializations to check complete restoration.
The [installed journey](reviews/INSTALLED_REGISTRATION_RENDER_ADMISSION.md)
relocates 51 files across three components, removes only private installer inputs,
then materializes and renders two full snapshots with expressions 0.25/0.5.
Its genuine source/build and system runtime remained accessible. Neither journey
qualifies physical devices or a native library browser.

## Actual apron and remaining interface work

The masked atlas apron preserves live footer text and excludes baked lettering.
[Twenty-five genuine paired cases](reviews/REFERENCE_APRON_RASTER_ADMISSION.md)
cover 61,780,011 pixels with zero forbidden/footer changes, eight exact
hidden/inactive frames and exact creation-failure fallbacks. Only canonical
1672×941 establishes 32,544 exact exposed source pixels and 56,016 exact footer
pixels; resizing uses the frozen nearest mapping.

The [thirteen actual native captures](design/native-gallery-preset-v1/README.md)
include 1920×1080 and bind executable, source, state and pixels. Software-rendered
stills do not qualify real display/DPI or accessibility. The
[residual review](reviews/WHOLE_INTERFACE_DELIVERY_ADMISSION.md) retains title,
tracking, caps, panel lighting, furniture, manual and layout differences.

## Recovery, owners and next priorities

Root coordinates the sole `../build-native`: Ninja Release, standalone/tests ON,
MIDI/VST3 OFF and X11/Wayland/ALSA/PulseAudio/JACK OFF. SDL 2.32.10 at
`/workspace/scratch/ade21b726509/SDL2` remains read-only. Reuse existing builds;
`../a38-headless` is the justified SDK-free exception. The
[resource audit](reviews/PRESET_RESOURCE_RECOVERY_ADMISSION.md) observes about
40 GiB free, 150 MB native and 6 MB headless builds. Preserve genuine
`../baseline-native` origins, original failures, auditions and gallery identities;
rebuilding does not recreate originals. Other workspaces remain read-only.

On context recovery, inspect HEAD/index/worktree and fresh remote state after
reading AGENTS and the session records. Root assigns paths, builds, integrates
and publishes accepted chunks. Existing owners retain ScannerLineFoh/library/
browser, contact/audio/manual/rim, semantic-entry/cap, leakage/harmonic sources,
crossover/MIDI retirement and R4 work; recover their checkpoints before overlap.

First obtain actual macOS execution and complete the required platform matrix.
Then independently freeze T2 rack-heading tracking/baseline, separately T3 title
weight/highlight/shadow, followed by one panel-material slice from genuine
baselines. Scanner, AO-28 and Leslie audio remain unconnected. Physical
acquisition, native accessibility, devices/DAWs, callback deadlines/retirement,
rights and signed release retain separate gates.

After review and affected checks, root commits/pushes authorized accepted work
with a fresh expected parent and no force, preserving concurrent advances.
If shell credentials remain unavailable, use verified immutable blobs and a
SHA-only tree; independently verify remote commit/tree/parent/content and observe
required hosted results at that source. Checkpoint each wave and before long
operations. Strict ledger validation establishes record consistency, not product
completion or external participation.
