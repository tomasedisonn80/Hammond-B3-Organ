# A57 X11 setup and desktop acceptance — recovery receipt

## Identity, scope and authorship

The actual worker was `/root/w10_a57_desktop_setup`, assignment 57 in wave 10. Root read its full completed review before the workspace interruption. This document is **new recovery prose authored by root from the worker's delivered findings**. The original local report, note and raw desktop artifacts are unavailable for transfer. No new desktop run was performed during recovery.

A57's task was to resolve A42's concrete `x11 not available` startup blocker using the existing source and dependencies, then exercise a bounded real desktop journey. Product source and dependency contents were not edited or downloaded. The result is accepted as a **partial capability and interaction qualification**, with the unexecuted remainder retained below.

## Actual build and environment

The worker configured the separate `../build-desktop-qualification` tree. Configure took 29.66 seconds and the two-worker build took 90.59 seconds; allocated build storage was 34,148 KiB. The recorded tools were GCC 14.2.0, CMake 4.4.4, SDL 2.32.10 and RtMidi 6.0.0. MIDI support and RtMidi ALSA were enabled; SDL ALSA audio was disabled in this identified environment.

The existing X11 headers were under `/workspace/scratch/641ca55ce6de/native-sysroot/usr/include`. Its unversioned library links were dangling, while the installed versioned runtime libraries existed. A57 supplied X_INCLUDEDIR and explicit X11_LIB, XEXT_LIB, XCURSOR_LIB, XI_LIB, XFIXES_LIB, XRANDR_LIB, XRENDER_LIB and XSS_LIB paths under `/usr/lib/x86_64-linux-gnu/`: libX11.so.6, libXext.so.6, libXcursor.so.1, libXi.so.6, libXfixes.so.3, libXrandr.so.2, libXrender.so.1 and libXss.so.1. The generated SDL configuration explicitly enabled X11 and its dynamic library names. XScreenSaver remained unavailable because its header was absent.

The resulting executable was 3,847,536 bytes with SHA-256 `fff5d06a48fd156e89219d30781223b3a366126776005b6a3a7851fdf912950c`. All 98 product inputs matched the polished published source and all 114 protected inputs remained stable. This desktop-capable executable differs from the dummy-capture executable; their results must not be interchanged.

## Observed desktop behavior

A focused actual application window opened on DISPLAY=:0 using X11 and software rendering. Window and drawable were both 1280 by 900, located at desktop coordinates 42,62. Six desktop frames were viewed live. A real click selected Upper C2; F6, F7 and F4 preserved the remembered C2 focus. **No held note was carried through that navigation**, so it does not qualify held ownership during workspace changes.

A real atomic drag started on Flat Upper C2 and ended outside the window. The following Service frame reported zero held notes. This proves the observed released endpoint; there was no intermediate observation of a held state and no completed capture-return journey. Alt+F4 did not close the application.

The 90-second supervisor bound sent SIGTERM. SDL handled the quit path and the process exited zero at 90.79034 seconds with joined/stopped/unheld diagnostics and no stderr. The supervisor recorded `timed_out=true` because it reached its bound. This is a bounded, observed SIGTERM cleanup outcome, not a successful Alt+F4 interaction or an unconstrained spontaneous exit. Diagnostics recorded 3,116 rendered images, 8,102 dummy-audio callbacks and 4,148,224 audio frames, zero error counters and one discarded close command. MIDI remained closed; no discovery or hardware input occurred.

After window destruction, attempted desktop keys were not delivered to the terminal. A temporary launcher was not discovered or launched; task-owned launcher files, link and extra terminal were removed. The worker released its desktop lease and completed its desktop session. These observations do not imply physical audio or MIDI qualification.

## Unexecuted work and acceptance boundary

The original A42 thirteen-event replay was **not run**. Held owners through navigation and resize, persistent OS capture and capture return remain unqualified. The interactive command omitted a screenshot destination and the planned replay did not execute, so **no lossless desktop screenshot was retained**. The six live frames are not an archived image deliverable. The [eight-image v2 gallery](../../../examples/demos/standalone-interface-preview-v2/README.md) remains explicitly dummy/software native output.

Root accepted the actual build and partial interaction findings, including all limitations, before the interruption. The next desktop worker should first inspect the restored environment and generated SDL settings, then run the full bounded held-owner/resize/off-window/capture-return flow with retained lossless screenshots and source-identified diagnostics. Real device selection, DPI, screen-reader semantics and timing each need their own evidence.

Use the [recovery record](reports/root-workspace-recovery.json) and [current checkpoint](CHECKPOINT.md) before touching the old local index. Do not reuse these historical absolute paths without checking that they still exist.
