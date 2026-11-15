# A18 — native MIDI calibration overlay

Implemented the presentation half of `midi-expression-endpoints-v1` in
`apps/standalone/InstrumentView.h` and only the MIDI overlay/layout portions of
`InstrumentView.cpp`. A16 owns behavior and diagnostics in `main.cpp`. The prior
A15 manual-rack/key paint is preserved.

The centered dialog is now 740×600, fitting the 960×700 minimum with 50 px above
and below. Its shared rectangles add expression minimum, maximum and direction
after the three channel controls. The labels and selected values are separate
from an explicit active-calibration line. Inactive and pending reconnect states
are named; endpoint-order errors remain visible before Apply. The actual
connection result retains two lines. Dimensional and Flat material paths remain
shared with their existing presentation rules.

Independently useful control centers at 960×700, in focus order:

| Control | Center |
| --- | --- |
| Previous / Next port | (158,184) / (802,184) |
| Upper / Lower / Pedal | (244,308) / (480,308) / (716,308) |
| Minimum / Maximum / Direction | (244,401) / (480,401) / (716,401) |
| Apply / Disconnect / Close | (264,579) / (500,579) / (780,90) |

For 1280×900 add (160,100); for 1672×941 add (356,120.5).

Executed from the assigned repository: `g++ -std=c++20 -fsyntax-only -Wall
-Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -Iinclude
-Iapps/standalone -I/workspace/scratch/1bb6ee17ad7e/SDL2/include
-I/workspace/scratch/5b7d983ac078/build-native/_deps/sdl2-build/include
apps/standalone/InstrumentView.cpp` passed. `git diff --check` passed. No shared
build or renderer was run; these checks do not establish visual acceptance.

Header SHA-256: `b334ba3b085ec63fbbd715e4d2ae5fcecfc41a00dcdf7f4d079b7076c254c1f0`.
Painter SHA-256: `3687f96db4490e600d6107e6b39d7b7d568bdeb183f16f6aa397535a5f688567`.

Next: coherent root build; independently update old eight-stop/520-high MIDI
tests without weakening their behavior assertions; exercise all eleven stops,
invalid Apply and selected/active diagnostics; inspect actual minimum/reference
and Flat captures, including long backend/error text and focus outlines. The
existing material fixture should also cover the three new buttons. Physical
MIDI devices and semantic accessibility remain separate gates.
