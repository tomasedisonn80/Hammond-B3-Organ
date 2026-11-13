# Standalone window demonstration — 2026-11-13

## Evidence boundary

Assignment 40 captured four actual linked-application backbuffers and inspected
each retained PNG. This is an M9 native UI engineering demonstration against
the existing nominal dry core, following the walnut/charcoal/ivory/brass scope
in [STANDALONE_SCOPE.md](../STANDALONE_SCOPE.md) and atlas pp. 409–444 summarized
in [PLAN.md](../PLAN.md). It does not close the remaining M9 product gates.

The [bundle](../../examples/demos/standalone-window-v1/README.md) contains four
PNGs, their four unmodified application JSON diagnostics, two bounded replay
scripts and a complete provenance manifest. There are no generated mockups,
redistributed executables, BMPs or new audio claims in this bundle.

## Captured source and setup

| Identity | Observed value |
| --- | --- |
| Frozen source commit | `387275289410d12af27cf235d6e45fd91f29bafa` |
| Frozen source tree | `0d6da163edd6531338938e12e0d393841d569a80` |
| Executable SHA-256 | `7377e8c2c146636ef3b4ca28891d257bbfcc9db8b6f42caa257b6857d97d9925` |
| Build | GCC 14.2.0, CMake 4.4.4, Release; integrator-built frozen archive |
| SDL | 2.32.10, commit `5d249570393f7a37e037abf22cd6012a4cc56a71`, clean dependency source |
| Selected video/audio | Explicit `SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy` |
| Obtained renderer | `software`; logical size equals drawable size in every run |
| Profile | Embedded `nominal-unmeasured-v1`; compiled SHA-256 `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Image conversion | Python 3.12.14 / Pillow 13.0.0; RGBA BMP → PNG, decoded bytes identical |

The integrator confirmed the executable was ready before capture. Every run
used a fresh private working directory and absent `controls.b3controls`;
no state file appeared on exit. The binary hash matched before/after all runs.
Source files were compared with the named Git commit, and build/profile/font/
SDL artifact hashes are in the manifest. Its local absolute paths locate the
captured inputs, while the README supplies portable reproduction commands.

## Executed runs

All runs exited 0 with empty stderr and no recorded application error,
render/format/nonfinite/overrange failure, queue overflow, rejected command,
recovery or fault flag. Native stereo float32 was obtained; callbacks and frames
were positive, devices were open/running before close, and joined shutdown
left no notes held. Counts below describe these retained runs only.

| Capture | Pixels | Scheduling | Callbacks / frames | Result |
| --- | --- | --- | --- | --- |
| Reference | 1280 × 900 | `--smoke-ms 600` | 57 / 29184 | Hold/release observed; screenshot taken while Upper C4 held. |
| Minimum | 960 × 700 | `--smoke-ms 600` | 56 / 28672 | Hold/release observed; screenshot taken while Upper C4 held. |
| Help | 960 × 700 | 600 ms replay, 2 events | 61 / 31232 | Replay passed, delivered and acknowledged; Help left open. |
| Audio | 1280 × 900 | 1000 ms replay, 18 events | 464 / 76288 | Replay passed; 2 device starts; actual 96000 Hz / 128 frames. |

The first three runs obtained 48000 Hz / 512 frames. Audio counts accumulate
across its two device starts. Retained discarded-command counts are 1, 1, 1, 2;
the normal close path can discard queued release work after joining. They are
not omitted or confused with the zero overflow/rejection/fault counters.

## Direct visual findings

| State inspected | Findings | Remaining limit |
| --- | --- | --- |
| Reference | Header, drawbar banks, performance controls, two manuals, pedalboard and footer fit; brass held-key highlight is visible. No panel/control overlap or clipped keyboard edge observed. | One scale and one registration. |
| Minimum | All major regions stay within the 960 × 700 window; held-key highlight remains distinct; footer and toolbar do not collide. | Pitch labels and footer are small; real-display readability and musician usability remain unqualified. |
| Help at minimum | Entire modal, heading, nine instruction lines and Close focus outline are visible; no text collision or modal clipping observed. | This demonstrates drawn focus, not an OS accessibility tree. |
| Audio at reference | Device selector, rate, callback-frame value, explanatory lines and Apply/Close controls fit; cyan selector focus remains visible. Footer and actual diagnostics agree on 96000/128. | Dummy output only; the displayed callback size is not measured physical latency. |

Screenshots were read from the app's defined renderer backbuffer before Present;
they are not OS desktop captures. The four PNGs retain exact decoded BMP pixels,
with original BMP and final PNG hashes/dimensions in the manifest. Counters,
meters and wall-clock frame selection can vary on a rerun.

## Next concrete gate

Run the same states on an acquired real desktop/audio device and record OS,
renderer, device, logical/drawable sizes and obtained format. Inspect minimum
and reference windows at multiple pixel scales, exercise physical input/focus
and ask a musician to assess the compact labels. Retain a separate native
accessibility-tree/screen-reader evaluation. Acceptance requires observed real
platform evidence; this bundle supplies none for hardware sound, latency,
deadlines, high-DPI, accessibility, host support, signing or acoustic fidelity.
