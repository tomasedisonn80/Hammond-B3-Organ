# A42 — desktop pointer qualification boundary

Actual worker `/root/w07_a42_desktop_pointer`, logical wave 7. Owned only this
note, `docs/reviews/INTERFACE_DESKTOP_POINTER.md` and `reports/a42-*`. Read current
AGENTS/scope/checkpoint, M0–M9 plan, workspace/geometry/inspection requirements,
A21 native acceptance and A37's final operator flow. Root retains shared guides,
builds, production, index and publication; A40/A41 work was preserved.

## Result

**Blocked before native initialization; persistent pointer capture NOT RUN.**
Sky's actual desktop was accessible and its terminal saw both DISPLAY `:0` and
the shared pinned executable. The one actual application attempt selected X11
video and dummy audio and exited 1 in 0.00645 seconds with
`hammond_standalone: Cannot initialize video: x11 not available`.
The generated SDL config has dummy/offscreen video, with X11/Wayland undefined.
No app window, renderer, audio lifecycle, replay input, native diagnostics or
app screenshot was produced. No physical audio or MIDI was connected.

Executable before/after SHA-256:
`bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2`.
All A36 production inputs matched; the four existing CI/test-only differences
are retained exactly. No rebuild or production repair was attempted. The
[review](../../reviews/INTERFACE_DESKTOP_POINTER.md), [launch](reports/a42-desktop-launch.json)
and [qualification JSON](reports/a42-desktop-pointer.json) distinguish actual
terminal observations from the unexecuted pointer assertions.

## Reproduction and next action

From an actual desktop terminal in this shared checkout, the retained one-shot
runner was executed through `sh /workspace/scratch/601951e27dc3/a42-run.sh`; that
launches [a42-desktop-probe.py](reports/a42-desktop-probe.py). Its output directory
is exclusive and refuses overwrite. The exact native argument list and selected
environment are in the launch JSON; the replay is retained beside it. The
startup failure occurs before the normal shutdown diagnostics path.

Next obtain an identified SDL backend-capable build of this source, verify an
actual focused window and capture success, then execute the one retained
keyboard/pointer/navigation/resize/off-window release flow. Preserve A18/A21's
distinct model and capture-failure evidence. The missing backend is now concrete;
the native ownership contract itself remains unqualified. The A42 application
exited by itself; its diagnostic terminal remains visible. CUA completion was
sent exactly once; no further desktop exploration occurred.
