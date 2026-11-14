# Desktop pointer boundary — A42

**Outcome: native persistent pointer capture remains NOT RUN.** A real desktop
and shared executable were available, but the pinned application exited before
creating a window: `Cannot initialize video: x11 not available`. This is a
concrete SDL build capability blocker, not a pointer-continuity failure or pass.
The [actual launch record](../development/2026-11-14-interface-continuation/reports/a42-desktop-launch.json)
and [qualification record](../development/2026-11-14-interface-continuation/reports/a42-desktop-pointer.json)
retain the attempted command, environment, exact stderr and unrun assertions.

## Source and executable

A42 privately copied A36's released executable and checked SHA-256 before and
after the attempt:
`bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2`.
The file is 3,707,640 bytes; no configure, compilation or product edit occurred.
[A36's build record](../development/2026-11-14-interface-continuation/reports/a36-build.json)
identifies the Release compiler/configuration and 327 source inputs. All
production inputs still matched. Four concurrent changes were explicitly
recorded: the standalone workflow and A40's three test fixtures. Those same
four differences existed before and after the attempt; they do not change the
pinned binary. Published HEAD alone does not identify its working A34/A36 fixes.

The generated SDL configuration in the existing native build defines dummy and
offscreen video but leaves X11 and Wayland undefined. `SDL_X11=ON` in the cache
is only a requested option; missing detected headers prevented that backend
from being compiled. SDL is statically linked, so setting `DISPLAY` or selecting
an installed shared SDL library cannot add X11 to these executable bytes.

## Actual desktop and launch

The prescribed first CUA call was `cua.getState()`, followed by Sky native
inventory and screenshots. There were no pre-existing windows. The project
executor initially had no DISPLAY variable or X11 socket, whereas the desktop
terminal visibly reported `DISPLAY=:0` and could read the pinned executable.
Its launched Python process independently recorded `/tmp/.X11-unix/X0`, hostname
`2b85fe4e0adc` and Python 3.13.5. The displayed terminal measured 817×485; the
inspected desktop raster was 1365×1024.

Sky `type_text` returned `text entry requires a focused application window`
after a screenshot-based click. The documented `press_key` path worked; it was
used to enter the display/path checks and launch the retained project runner.
No browser, private control API, new X server or SDK installation was used.

The application was requested at 1280×900, with explicit
`SDL_VIDEODRIVER=x11`, `SDL_AUDIODRIVER=dummy`, no MIDI port and no forced render
driver. It returned **1 in 0.00645 seconds**, well inside the 15-second wrapper
deadline. The terminal visibly showed the exact video-initialization error.
No Hammond window appeared. No renderer, drawable, scale, audio lifecycle or
pointer capture was observed. Native diagnostics and screenshot flags were
supplied using the executable's current `--help` grammar, but initialization
failed before the application could write either file. The wrapper preserved
stderr and its own process report instead. The process had already exited;
the diagnostic terminal was left showing the failure. CUA completion was
reported exactly once after the visible result.

## Prepared assertion, explicitly unexecuted

The retained [ten-second input](../development/2026-11-14-interface-continuation/reports/a42-desktop-pointer.b3uireplay)
would hold keyboard Upper C4, press the literal Upper C2 interior point
`(222,580)`, visit Service with F6, toggle Flat with F7, move over another key,
return through F4, resize to 960×700, move to `(-80,-80)`, release the original
pointer there, then release the original keyboard owner. Expected observations
are stable original note 36 plus independent note 60 until their respective
releases, no glissando or navigation control command, and two paired note-on/off
commands. **None of those events reached the native application in this run.**
The transport injects SDL events; even a future passing replay must not be
described as a human physical mouse press.

## Required next gate

Use the same identified product source with an SDL build that actually includes
the available desktop backend, then repeat this bounded flow with a visible
focused Hammond window. Establish a successful native capture request, the
original held-note observations through every transition and off-window Up,
and joined unheld shutdown. Inspect at most two representative app frames.
This binary exposes no capture-success/failure counter, so absent diagnostics
must remain **unavailable**, never zero. SDL accelerated-renderer selection
would also not establish physical GPU acceleration; identify its actual backend
and software rasterizer separately if one runs.

A18's model continuity and A21's dummy-driver CaptureLost cleanup remain valid
within their existing scopes. Neither closes this native boundary. Physical
audio/MIDI, screen readers, deadlines, reference equality and instrument fidelity
remain separate gates.
