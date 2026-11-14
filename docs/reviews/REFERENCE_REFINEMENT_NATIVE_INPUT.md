# Native OS input evidence and current-source applicability

**Accepted within its recorded scope.** The retained X11 journey qualifies
executable `6eea84ba830ea8710b550c14561b4dd887bea8aac489fa82a467e3708e071b13`.
It establishes keyboard-held pedal continuity across one layout breakpoint,
persistent admitted mouse capture through an inside/outside/inside/outside
path, explicit release, and stopped/unheld joined cleanup. It does not supply
a new OS-input result for the later v4 executable. A51 reviewed existing bytes,
typed diagnostics and source; no application, desktop, device, build or CTest
was launched for this audit.

## Evidence and identities

The [original diagnostic](../development/2026-11-14-reference-refinement/reports/desktop-acceptance.json),
[root's observed journey](../development/2026-11-14-reference-refinement/reports/root-desktop-acceptance-review.json)
and [pre-run source/runner inventory](../development/2026-11-14-reference-refinement/reports/root-desktop-acceptance-source.json)
remain unchanged. The source record names base commit `e4968b2a`, with an exact
161-path worktree inventory; the base commit alone does not identify that
executable's complete inputs. Root's post-run review records those 161 inputs
unchanged across the original run. A51 independently rehashed the retained
artifacts and compared every recorded path to published source
`0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b`, tree
`f8144b771cda1264a8788f8297f5bfec999f4a08`.

| Retained artifact | Independently recomputed SHA-256 |
| --- | --- |
| `desktop-acceptance.json` | `60aab57cd4a5d134765db921e111586299902cda9c02b8358579b06cb9ed7326` |
| `root-desktop-acceptance-review.json` | `ff6b371a6b3e796c758551c9ec53101015097d7af364760b69724a60f275255a` |
| `root-desktop-acceptance-source.json` | `6e6970c797fd6f55bc736e9a5486a72f1739d4f44a0d779d39eae4b24e9dff74` |
| Startup PNG | `9cb1ac834a30855cd2e15162854f256c38326dcc3361be93fc53b8070fbba54a` |
| Startup BMP, still available in scratch at audit | `656af3b42fb3a588c48cb780c77049347ea140eda28b25195d9338e83db2f2d6` |
| Empty stdout and stderr, each | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

All **1,148,000 RGBA pixels** of the 1400×820 PNG equal the original BMP; decoded
RGBA SHA-256 is `b5a67cf3b065dd742ab89e7137c05cb901628e2ffda9bfa43c8dcde090fcdc37`.
A51 visually inspected the retained Dimensional Play image. Its diagnostic
identifies image 1 at 1 ms with no held targets and `controls_pending=true`.
This is the startup frame, not an image of later navigation or capture. Root
observed intermediate desktop images live; the primary bundle retains no
per-step lossless desktop screenshots. The old 1400-pixel window extended 41
pixels beyond the observed 1364-pixel desktop, although its interactive interior
was visible. The complete application PNG does not remove that display limit.

## What the painted observations establish

The ordinary runner specifies X11 video, software rendering and dummy audio;
it supplies no input/MIDI replay or smoke option. Typed runtime diagnostics
agree: SDL 2.32.10, X11/software, dummy 48 kHz stereo audio with 512-frame
callbacks, and no selected physical MIDI input. There are **19 observations**
within a 512-record capacity, with `observations_truncated=false`. Each retained
observation has an available, successfully read current snapshot. Render image,
elapsed time, frame-clock and capture counters are monotonic.

Indices below are zero-based indices into `presentation.observations`. Counts
are applied logical targets from the exact copied state used for painting;
they do not identify individual owners, MIDI pitches or audible sound. See
[A20's diagnostic semantics](../development/2026-11-14-reference-refinement/notes/A20-native-observation.md)
and the unchanged [`main.cpp`](../../apps/standalone/main.cpp) observation path.

| Observation indices | Actual retained sequence | Admissible interpretation |
| --- | --- | --- |
| 1–4 | Play Upper 0; Service Upper 0; Service Upper 1 at 12,714 ms; Service Upper 0 at 14,194 ms | The OS chord produces a held Upper target after Service navigation and then releases. No painted pre-held keyboard prefix precedes the transition. |
| 5–8 | Dimensional Play Upper 0; Flat Play Upper 0; Flat Upper 1 at 14,424 ms; Flat Upper 0 at 15,893 ms | The OS chord produces a held Upper target after the Flat transition and then releases. This also lacks a painted pre-held prefix. |
| 9–11 | Pedals 1 at 1400×820 / 37,060 ms; Pedals 1 at 1180×820 / 37,424 ms; Pedals 0 at 37,478 ms | A keyboard-held pedal survives the wide-to-compact branch crossing and releases afterward. Root's action record says F3 then held A while the mouse drags the resize edge. This is not a pointer-held pedal. |
| 12 | Both capture flags true, one attempt and one success, Upper 0 | Capture admission is painted before the applied note becomes visible. Admission alone does not establish a held note. |
| 13–16 | Upper 1→0→1→0 at 72,508 / 72,688 / 72,846 / 73,125 ms; both capture flags stay true | With root's observed pointer path, this establishes persistent capture through inside/outside/inside/outside movement. The note target is not continuously held. |
| 17–18 | Both capture flags false, one explicit release call; all targets 0; subsequent Service frame remains unheld | Explicit release is observed, followed by an unheld navigation endpoint. No fresh post-release pointer press is retained. |

The capture record ends with attempts/successes/losses/release calls **1/1/0/1**.
`sdl_captured` copies the application's admitted-capture flag; the event loop
checks SDL's window capture flag for loss. `release_calls` counts an explicit
API call, not its successful return value. The typed trace does not record
pointer coordinates or physical press IDs; the path's spatial attribution comes
from root's contemporaneous observed review. The unsuppressed pointer source
releases a target outside a playing key and can acquire one on reentry. The
separate suppression path after a workspace/presentation/resize transition was
not exercised by this pointer sequence. See unchanged
[`UiModel::pointer`](../../apps/standalone/UiModel.cpp).

The last painted frame, image 2828 at 81,716 ms, is unheld and uncaptured.
Joined diagnostics retain **7,420 callbacks / 3,799,040 frames**, zero sample,
format, nonfinite and overrange failures, zero application errors, zero Session
faults/overflows/rejections/recoveries, and `running_after_shutdown=false` /
`held_after_shutdown=false`. They also explicitly retain **one discarded
command**, resolved sequence 138 and last applied sequence 137. Its identity
is **unassigned**: the diagnostics do not name it. The unchanged shutdown path
joins audio callbacks before Session stop, which can discard queued commands;
that source mechanism does not identify the observed command or justify a
zero-discard/all-commands-applied claim.

Root records ordinary Alt+F4 and a return to Terminal. The final diagnostics and
unchanged [`AudioDevice::close`](../../apps/standalone/AudioDevice.cpp) /
[`Session::stop`](../../apps/standalone/Session.cpp) path support joined cleanup.
The primary bundle has no separate numeric process-exit receipt or supervisor
status record. Empty stdout/stderr and this audit do not manufacture an exit
code. The observed close was Alt+F4, not a newly observed click on the window's
close control.

## Applicability to published source

**159 of 161 retained paths are byte-identical to published `0881d1f4`; all 161
current worktree paths match its published blobs.** The changed files are:

| Path | Source change since the old OS run | Qualification consequence |
| --- | --- | --- |
| `apps/standalone/InstrumentView.cpp` | A26 forwards Flat material selection to Audio/MIDI/Help panels/buttons; A40 changes only wide Dimensional title/caption typography. | Paint output has changed. Old interactive evidence cannot qualify the new appearance or a different executable's OS behavior. |
| `apps/standalone/CMakeLists.txt` | Adds the ten-line material-acceptance test target registration. Removing exactly that block reproduces the retained old file hash. | Test registration changed; application input/ownership source was not changed by this block. |

The old painter hash is `4127c0b2feb9b04f591fa9af82e4a6f3bbc162228205d7d92c8bdcca911ac45f`;
the published painter is `f323c8c2f5529b03c25deccb74f482d8b6312487492a45d14b94ef0e24cfbb6a`.
Exact bytes outside the three affected paint functions are identical. All
recorded `main`, `UiModel`, Session, AudioDevice, MIDI input, StateFiles, Engine,
manual/pedal note ownership and parameter-registry inputs remain identical.
The [audit report](../development/2026-11-14-reference-refinement/reports/A51-native-input-evidence.json)
retains their hashes and the complete comparison digest. This is source
applicability evidence; the 161-path inventory is not a full compiler/dependency
closure or a rerun of native input against the later binary.

The current desktop executable independently rehashes to
`01fe78a55b7a9bc72228dafe175f5a8eb48481c063f217606474d4dff682320f`, matching
[A46's v4 record](../development/2026-11-14-reference-refinement/reports/A46-final-native-gallery.json).
Those eight actual application captures use dummy audio/video and software
rendering; their settled replay endpoints remain distinct from actual OS
capture. A18/A23's six genuine pending/acknowledged frames are a windowless,
device-free native Session rendering harness, with their own source and binary
identities. Existing model/replay checks cover the separate pre-held navigation
sequence and ownership rules. [A34's dry-audio/state isolation](../development/2026-11-14-reference-refinement/notes/A34-audio-state-isolation.md)
retains its own executed boundary. None of these records retroactively upgrades
the old OS run or transfers it to v4. Earlier desktop-baseline/refinement reports
remain historical.

## Concrete next actual display/device journey

The [desktop contract](../REFERENCE_REFINEMENT_DESKTOP.md) remains the acceptance
authority. Reserve one native build/display owner; freeze the intended published
source and retain exact dependency, configuration, source and executable hashes.
Use fresh state/diagnostic outputs and an ordinary launch without replay/smoke.
Record the physical display, resolution/scaling, OS/window manager, keyboard,
pointer, audio backend/device and MIDI controller/port. Physical-device claims
require real devices; the old dummy configuration does not close them.

1. At 1672×941, retain a painted keyboard Upper C4 and pointer Upper C2 hold
   **before** F5/F7/F6/F4. Capture every transition, then resize to 960×700 and
   repeat in reverse. Verify the original owners persist through navigation,
   hidden controls cannot acquire a new hold, and clocks/controls do not reset.
2. In that suppressed pointer state, retain outside movement and outside release;
   return button-up, move over a different key, then freshly press/release it.
   Separately distinguish ordinary unsuppressed in/out target changes from
   persistent capture. Repeat the layout crossing with the **pointer itself**
   holding a pedal. Record deliberate focus loss and absence of resurrection.
3. On identified hardware, retain overlapping UI/MIDI owners and both release
   orders with exact routing. Observe the actual audio path separately from UI
   held flags; record device faults and explicit reconnection where exercised.
   Review readability/hit targets at the selected real display scales.
4. Close a separate ordinary launch through its actual close control. Retain
   numeric exit/status and timeout/signal information, joined diagnostics,
   available final snapshot, stopped/unheld state, all failures/discards and
   lossless per-step frames with untruncated typed observations.

This closes only the specific journey actually executed. DAW hosting, native
semantic accessibility, audio deadlines, literal reference equality and physical
instrument/cabinet fidelity continue to require their own evidence.

## Reproduce this evidence audit

From the repository root, with Python 3 and Pillow for the optional BMP decode:

```sh
python3 docs/development/2026-11-14-reference-refinement/reports/A51-audit-native-input.py \
  --repo . --published 0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b \
  --startup-bmp ../desktop-acceptance-startup.bmp \
  --current-app ../build-desktop/apps/standalone/hammond_standalone \
  --output /tmp/A51-native-input-evidence-recheck.json
```

The retained run passes **33/33 offline evidence checks**. This command only
reads artifacts/source/Git blobs and writes its selected audit report; it never
launches the native executable. If the optional scratch BMP or current binary
is absent, omit its argument and retain the narrower result without claiming
those checks. A preliminary manual image read used the wrong relative BMP path;
the corrected absolute path succeeded. That audit setup failure is retained in
the report and is not an application failure.
