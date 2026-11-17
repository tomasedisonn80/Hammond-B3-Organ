# UI delivery test portability review

16 November 2026, America/Halifax. A25, wave 5. **Source inspection is
complete; platform execution remains pending.** This review covers the new
[H1 fixture](../../apps/standalone/native_tests/test_standalone_header_material.cpp),
[title-density reader](../../apps/standalone/native_tests/test_standalone_title_density.py),
[CMake registrations](../../apps/standalone/CMakeLists.txt) and optional
[capture extension](../../tools/capture_standalone_interface.py). Exact inspected
identities and remaining gates are in the
[machine report](../development/2026-11-16-ui-delivery/reports/new-native-tests-portability.json).
No source edit, build, native run or capture was performed. The inspected painter
contains T3 but no H1 helper; historical platform passes cannot qualify these additions.

## What inspection establishes

The H1 target compiles `InstrumentView.cpp` exactly once, through its fixture
include. Its linked drawing/support libraries do not compile that painter.
The common configuration requires C++20 and treats warnings as errors under
GCC, AppleClang and MSVC. `requires` and `std::bit_cast` therefore have an
explicit language requirement. `SDL_MAIN_HANDLED` and `SDL_SetMainReady` supply
the intended portable console entry. The pinned SDL 2.32.10 dependency, generated
art, checked-in font atlas, core/support libraries and Python 3.10+ are required;
the title reader itself uses only the Python standard library.

The fixture explicitly converts glyph metrics, clip coordinates, enums, indices
and stream lengths at their representation boundaries. Its literal dimensions
bound every float-to-integer operation; binary32 and four-byte RGBA assumptions
are asserted. RGBA32 surfaces and pitch-aware row copies avoid native integer
pixel-order and padding assumptions. SDL scale pointers are `float*`, colors are
byte pointers, clip state is compared with `SDL_TRUE`, and before/after checks
cover logical/physical clip and viewport, blend and scale. Helper probes additionally
check draw-color preservation. These checks still need execution on each target.

Both raw-frame producers set Windows stdout to `_O_BINARY` before frame export;
JSON precedes an exact byte count and diagnostics use stderr. CMake's quoted
`TARGET_FILE` expression resolves configuration-specific executable paths, while
Python uses argument lists and resolves the source beside `__file__`.
`.gitattributes` enforces LF, preserving the title reader's raw fixture hash.
That reader rejects duplicate keys, nonfinite constants and overflowing float
tokens, bounds nesting/numbers/pipes, and checks exact inventory/types/frame length.

## Concrete limits and next gates

The ordinary standalone regex includes both tests and its aggregate target
builds their native inputs. At inspection, its required-name assertion and the
explicit sanitizer map omitted both additions. **A26 separately owns that CI
repair**; this review does not claim it completed or validated.

The default H1 CTest emits a summary, so it never executes H1's binary `--case`
branch. Platform qualification must additionally read `--list` and binary exports,
including clipped/uncut and case 46 history/fresh variants, with exact payload
length and state checks. Windows binary-mode behavior is otherwise unobserved.

The fifteen-view extension reuses existing argument/path handling and validators.
Two inherited capture limits remain: `build_paths()` omits MSVC `.lib` and
configuration subdirectories; `read_json()` rejects `NaN`/`Infinity` tokens but
has no finite `parse_float`, so `1e999` reaches validation as infinity. Positive
counter checks can accept it before receipt serialization rejects it. Neither is
an observed capture failure; Windows build provenance and malformed-number
rejection need explicit follow-up. Real captures additionally require Pillow.

At the published source, retain passing Linux GCC MIDI ON/OFF, macOS AppleClang
ARM/Intel and Windows MSVC x64 native jobs, the repaired Linux ASan/UBSan/leak
selection, and `python_test_capture_standalone_interface` in all four core Release
jobs. Confirm both new names actually execute, preserve failures/cancellations,
and separately qualify real fifteen-frame platform captures before claiming their
portability. No fixture result establishes literal whole-interface 1:1.
