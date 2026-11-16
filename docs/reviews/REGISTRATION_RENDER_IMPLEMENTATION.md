# Saved-controls renderer implementation admission

A21, `/root/w04_a21`, wave 4, 16 November 2026. Review of
[registration-render-controls-v1](../REGISTRATION_RENDER_CONTRACT.md) against
the working overlay on `54df95fe343d417dd89bb7a91f85e4f51c08dfe7`.

## Findings and disposition

**No production defect found in this reviewed scope.** The remaining concrete
coverage gap was initial restoration of every fixed mode against literal audio
rows. The author suite exercised two fixed selections and retained banks, while
the existing general renderer suite exercised all fixed rows through events.
Those are different entry paths. The added
[independent suite](../../tests/test_render_controls_admission.py) closes that
gap and strengthens observable filesystem admission. No production file, DSP,
parameter identity or state format was changed by this review.

`load_controls` uses the shared no-follow reader before resolving ancestors.
The helper admits the opened regular handle, reads at most 16,385 bytes,
enforces the 16,384-byte whole-input limit and assigns its destination only
after parsing and canonical serialization succeed. Initial raw count/version
and complete canonical snapshot are copied separately from Engine state.
Path conversion/UTF-8 validation, profile, complete score and optional leakage
admission precede temporary WAV creation. Existing-output rejection covers
hard links; canonical input comparisons cover resolved aliases; publication
retains the existing atomic hard-link no-replace operation.

`Engine::restore_controls` executes while its clock is zero, before every
score/default-note event or positive processing call. The alternative branch
alone flushes old default drawbar/percussion/pedal setters. Stable scored events
therefore override the restored state, while schema-6 provenance retains the
initial parsed payload. Core `ControlState`, `ControlStateIO`, Engine,
parameter bridge and fixed catalog sources remain unchanged from HEAD; the
review introduces no new parameter, transient state or physical model.

## Executed independent checks

From `/workspace/scratch/3edffb787db3/Hammond-B3-Organ`, using root's existing
coherent Linux native Release executable and profile, without configure/build:

```sh
env HAMMOND_RENDER_EXECUTABLE=../build-native/hammond_render HAMMOND_TEST_PROFILE=../build-native/nominal.b3p python3 -B tests/test_render_controls_admission.py -v
git diff --check
git diff --name-only HEAD -- src include plugins
```

Final focused run: **5 methods, 45 actual renderer invocations, all pass in
2.179 seconds**. Diff whitespace checks pass; the core/include/plugin diff
query is empty.

| Check | Independent observation |
| --- | --- |
| All 18 restored fixed selections | Complete WAV equality to retained page-122 literal tap rows, with low/middle/high notes, nonzero PCM in each sounding interval, exact cancelled silence, reselect, and later audible return to both original hidden banks. Reference scores use no fixed selector and no controls restoration. |
| Entire state changed at frame zero | A score changes all 36 positions, both remembered selectors/fixed modes/routes, both pedals, all four percussion settings and expression. Audio equals an independently event-initialized render; the complete reported canonical payload remains the original input. |
| Empty score | Restored upper-B eligibility, enabled percussion and nonzero pedals create no note or percussion audio; canonical state remains exact. |
| Preflight before mutation | Linux inotify observes a positive successful-staging witness, then no create/delete/move/content-write events for invalid controls, profile, late score event or leakage input. After-run snapshots also remain exact. |
| Destination race | After observed staging creation, the renderer is stopped briefly, a destination is created exclusively, then rendering resumes. Publication refuses with exit 1 and no stdout; destination bytes and inode survive; all staging is removed. |

The fixed rows retain the provenance and limits of
[PresetTestOracle.h](../../tests/PresetTestOracle.h); this is an independent
software entry-path comparison, not new atlas/factory transcription or measured
gain evidence. No duplicate rate/block/contact Cartesian sweep was added.

## Bound identities and compatibility evidence

SHA-256 values at the final focused run:

| Input | SHA-256 |
| --- | --- |
| `tools/render.cpp` | `eee9b565f0ca2ca1e780ba6cd8bd118967728f2246b0023f609da89408739928` |
| `tools/ControlFileInput.cpp` | `0a174b171dfb3f0253cd6beb12707fda4da5ffb88c898727fb80ca111049cf5d` |
| `tools/ControlFileInput.h` | `74fe88ed36c8b00b56f3a3f15874f22ec418ce4ea8932995c7829b68c4f02ade` |
| `tests/test_render_controls.py` | `554360f2817b3819e07f258bf445fc81b1074f9d736310316cd09bdf4e38f66b` |
| `tests/test_render_controls_admission.py` | `337c2396bddf564f38ac682ac1361ef7d50282385a5dc0d7179f9c99384cc411` |
| `../build-native/hammond_render` | `671375f6f9d393295bca148bcb546a1eb387dd865e994e755f16933389a16263` |
| `../build-native/nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| `../baseline-native/hammond_render` | `928205dc3b31e57faa7664cb39e691659d1c7f7430b5555ade70b4a9830835bf` |

The retained [genuine-baseline comparison](../development/2026-11-16-preset-library-continuation/reports/renderer-legacy-comparison.json),
SHA-256 `e831218f75377f8d075eda3678700537b47558ed3db7a7cd0f80c5a3177a8a27`,
uses these same executable identities. Its default and nominal/percussion
fixtures preserve complete no-controls WAV and stdout bytes. This review
verified identities and inspected that receipt; it does not recount its two
earlier comparisons as new invocations. The author suite's 18 methods/109
invocations remain separate evidence for versions 1–4, signed zero, input
bounds/aliases/UTF-8, leakage, clipping and its rate/block/contact matrix.

## Limits and next integration

The added observation/race methods run only on Linux; other platforms explicitly
skip those two methods while retaining the portable audio checks. The race
proves one controlled destination interposition, not arbitrary concurrent input
replacement or hostile parent-directory changes. Raw notes and histories are
not introspected through this CLI. Exact PCM proves these nominal fixtures;
it does not calibrate an organ or establish real-time/device behavior.

Root retains CMake registration, coherent integration, existing renderer/state
gates, publication and exact-source hosted Windows/macOS acceptance. No build,
commit, push or hosted/platform acceptance was performed by A21.
