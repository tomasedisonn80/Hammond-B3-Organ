# Installed heading, title and header journeys

**A41 — bounded installed-use results, 17 November 2026. Five of the six
original journeys matched their expected outcomes. The canonical 600 ms smoke
failed and remains failed. One separately authorized 2000 ms canonical
diagnostic passed every unchanged smoke correctness assertion.** This review
does not admit the six-journey set as an unconditional pass.

The [original-output receipt](../development/2026-11-16-heading-title-continuation/reports/a41-installed-journeys.json)
records seven actual processes, **155 passed checks and one retained failed
check**, exact commands, environments, timeouts, source/package/input identities,
and original stdout/stderr/diagnostics. Original three-run and six-run receipts
are retained byte-for-byte inside it. Twenty-four compressed byte records were
decoded and hash-verified; no later result replaces the first failure.

## Source and installed payload

| Input | Exact identity |
| --- | --- |
| Current painter | `0bf731a692b7cb7c88c200afea86f4ca14239f20a7000f06be484f2a11ebc20d` |
| Built, installed and relocated executable | `bfe8e36d16f4c5fd15009f2fc4707c06c93388f40870dc9f84696d3367447e7b` |
| Unchanged application/replay source | `89b24fdeae438b77309904d12c32e3e2ae5e964e99968a8656c5b0a710e237c4` |
| Original 2700 ms Load script | `489218ab81d669aa6899223bf0ed03b248c101e354083db841a566df54e66821`, 3,479 bytes |

Root completed the coherent Release GCC/C++20 build and installed the explicit
`Standalone` component to `../install-header-h1`. A41 performed no configure,
build or install. Its [installation contract](../STANDALONE_INSTALL.md) requires
**17 files with MIDI disabled**: the executable and sixteen documentation,
capability, provenance and notice files. All seventeen paths and file identities
matched, including each metadata source and the configured capability hashes.
The payload names SDL 2.32.10, embedded nominal profile/fonts/reference assets,
and an unavailable physical MIDI backend. All **38 installed relative guide
links** resolved within the exact payload.

A41 copied that complete payload into its private `copied organ Ω` directory,
then actually renamed it to `relocated organ Ω`. Every command ran from its
own directory under `../a41-installed/operator-session`, outside the checkout
and installed prefix. Both original and relocated package trees remained
identical after all seven processes, including executable status. Private
state and replay inputs also retained their exact bytes.

Profile, glyphs, reference decoration and masked apron are embedded. Installed
manifests identify authoring inputs; they are not additional runtime asset
paths. The application has no `--version` or data-discovery command. Its actual
`--help` and `standalone-capabilities.json` are the operator entry points. The
checkout, build and dependency directories remained present and untouched;
this review does not claim a syscall trace or removal of every fallback source.

## Actual journeys

| Journey | Observed result | Wall time |
| --- | --- | ---: |
| Help before SDL | Exit 0 with deliberately invalid audio/video driver names. The supported state, replay and expression options were printed without SDL initialization. | 0.016 s |
| Physical MIDI unavailable | Expected exit 1: `MIDI backend: unavailable`, with the explicit compiled-capability error. No SDL initialization or substitute device. | 0.007 s |
| Canonical 600 ms Play | **Unexpected exit 1.** Actual 1672×941 dummy/software rendering produced two images, 155 callbacks and 79,360 frames with zero audio render/format/nonfinite/overrange failures. Neither smoke note event was sent; held/release observations and peak remained zero. | 2.465 s |
| Generic full-state Load | Exit 0. The original 2700 ms script at 1280×900 acknowledged the copied saved state, a fully altered state, then a new Ctrl+O restoration of the complete original state. Forty-four images, 194 callbacks, no application errors. | 2.937 s |
| Inverted expression | Exit 0. The installed guide's 800 ms synthetic CC11 example mapped raw 40 through inverted endpoints 20/100 to expression **0.75**. Calibration was active before shutdown and null afterwards; notes were released. | 0.937 s |
| Unavailable audio | Expected exit 1 with explicit selected-driver failure and no fallback. Zero callbacks/frames, unprepared zero-clock session, completed-but-failed smoke, and eleven rendered Service/Flat images. | 0.737 s |
| Separate 2000 ms canonical diagnostic | Exit 0 at the same 1672×941, executable, absent state and dummy/software drivers. All note-on/off, held/release, render-error and shutdown assertions passed: eighteen images, 194 callbacks, 99,328 frames, zero errors. Root held concurrent native/compile work for this one diagnostic. | 2.387 s |

The two unavailable-capability exits are expected refusals, not successful
physical-device operation. No journey selected a physical MIDI port or produced
a native MIDI callback. No state file was implicitly saved.

The generic Load input was a private copy of
`data/registrations/starter-v1/entries/12 Manual Return.b3performance`. Its
literal expected state includes all four banks, selected banks, fixed modes,
routes, pedal mixtures, percussion and expression 0.5. The live-edit history
changed several of those values before Load; an acknowledged restoration was
required, so startup equality alone could not pass. The exact script and oracle
were checked against the maintained independent fixture before execution.
Generic native Load restores the complete file regardless of its scope suffix;
registration materialization's expression policy is a separate operation.

## The retained 600 ms boundary

`advance_smoke` submits note-on only when `30 <= elapsed < smoke_ms / 2`,
audio and the copied snapshot are running, and controls are no longer pending.
The application performs a complete `render_frame` between main-loop checks.
The 600 ms command therefore has only the **[30, 300) ms** eligibility window;
the separate 2000 ms diagnostic has **[30, 1000) ms**.

The failed process proves that no eligible note-on was submitted under its
observed workload. It supplies no per-turn timestamp, first-paint trace or
pending-control timeline. Scheduler contention, cold software painting and
initial snapshot readiness cannot be separated causally from this evidence.
The callback was running and reported no render errors; that does not establish
a callback deadline or explain the missed UI smoke event. The longer diagnostic
shows successful bounded installed operation at its own duration. It neither
repairs nor qualifies the original 600 ms condition, and no production code,
test assertion or existing timeout was changed by A41.

## Admission boundary and next work

The exact copy/relocation/capability/link preservation and the five expected
original outcomes are supported. The separate 2000 ms canonical result is
supported at its precise inputs. **The original 600 ms canonical journey remains
open.** A future owner should capture an independent per-turn readiness/timing
trace or reproduce the same source under controlled conditions before assigning
a cause or proposing a reviewed scheduling change. Preserve the failed receipt
and all existing correctness assertions.

These selected Linux software/dummy journeys do not replace root's complete
coherent suite, independent paired visual/material admission or exact-source
hosted results. Real display/DPI/input, native accessibility, physical audio/MIDI,
DAW behavior, callback deadlines and OS retirement, physical calibration, rights,
signing and distribution retain separate gates. Literal whole-interface
**1:1 remains unmet and unwaived**.
