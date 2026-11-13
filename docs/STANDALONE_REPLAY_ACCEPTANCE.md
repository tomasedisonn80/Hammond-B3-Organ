# Standalone input replay acceptance

`apps/standalone/native_tests/test_standalone_input_replay.cpp` maintains the
native-only `test_standalone_input_replay` gate for the public
[`ScriptedInput`](../apps/standalone/ScriptedInput.h) and
[replay grammar](STANDALONE_INPUT_REPLAY.md). It links the real pinned SDL2
library, calls `SDL_SetMainReady`, and requires explicit `SDL_VIDEODRIVER=dummy`.
The release-active checks use no private members, symbol replacement, mock
queue, Engine, Session, renderer, audio device, or OS input injection.

## Acceptance boundaries

| Area | Retained checks |
| --- | --- |
| Grammar | Physical header/duration lines, LF/CRLF/final-newline rules, horizontal whitespace, full-line comments, optional leading zeroes, printable ASCII, and stable equal timestamps. |
| Limits | Exact 65536-byte and 256-record admission; one-over rejection; 250/10000 ms durations; events strictly before duration; coordinate and resize endpoints. |
| Payloads | An independent literal table of all 34 allowed names/scancodes; every name with all 16 canonical left-modifier masks; exact repeat tokens; all eight action kinds. |
| Rejection | Unknown/duplicate/trailing/missing fields, inline comments, aliases, duplicated modifiers, bad repeat, unsorted/out-of-range times, partial/fractional/nonfinite/overflow numbers, NUL/DEL/non-ASCII and bare CR. Every failed parse preserves every destination field, including inactive records. |
| Files | Unicode and space paths; exact-limit regular file; empty/missing/directory/NUL paths; final regular/directory/dangling symlinks rejected; parent symlinks admitted; FIFO rejected without a writer on POSIX; oversized and 64 MiB sparse regular files rejected atomically. |
| Mutable plans | Duration/count/order/type/key/modifier/repeat/coordinate/resize validation, preserved helper on rejection, inactive capacity ignored, repeated initialization preserved, copied plan independent of later caller mutation. |
| Actual SDL queue | Incremental and equal-time pumping; no early/repeated actions; literal key symbols/modifiers/repeat/window IDs; left-button transitions, coordinates, relative motion and focus-loss state; quit. |
| Geometry | Actual `SDL_SetWindowSize`/queried dimensions and ordered input before/between/after tied resizes. SDL's own extra resize notifications are permitted. |
| Delivery | Unique helper markers; wrong helper/window/owner rejected; polling alone does not set delivery; explicit acknowledgment required; completion requires delivery and elapsed duration; empty plans and maximum elapsed time. |
| Failures/lifetime | Uninitialized pump, elapsed regression, real SDL filter refusal for action and marker, actual queue exhaustion, retained accepted prefix, sticky failure without retry, pending events after helper destruction and four legal window/helper lifetime cycles. |

The full-queue test stops after 70000 attempts, every poll loop is bounded, and
CTest has a 15-second timeout. No sleeping or wall-clock replay wait is needed:
the public pump receives explicit elapsed values. The FIFO test's timeout also
guards against opening an unvalidated blocking special file.

## Reproduce

From the repository root, with the separately acquired locked SDL2 checkout:

```sh
cmake -S . -B build-native -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT=/absolute/path/to/SDL2
cmake --build build-native --target test_standalone_input_replay --parallel 2
ctest --test-dir build-native -R '^test_standalone_input_replay$' \
  --output-on-failure --no-tests=error
```

The native integration links `hammond_standalone_replay`; the ordinary SDK-free
configuration does not enter this test. An independent direct-build equivalent,
using the local SDL source/build layout from assignment 27, is:

```sh
g++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion \
  -Wshadow -Werror -O2 -DSDL_MAIN_HANDLED -Iapps/standalone \
  -I../SDL2/include -I../sdl2-build/include-config-release/SDL2 \
  apps/standalone/native_tests/test_standalone_input_replay.cpp \
  apps/standalone/ScriptedInput.cpp ../sdl2-build/libSDL2.a \
  -pthread -ldl -lm -o ../test_standalone_input_replay-a27
SDL_VIDEODRIVER=dummy timeout 15s ../test_standalone_input_replay-a27
```

## Observed assignment-27 result

GCC 14.2.0 strict C++20 compilation passed. The independent CMake 4.4.4 Release
harness passed **1/1** canonical replay tests in **0.02 seconds** against SDL
2.32.10, commit `5d249570393f7a37e037abf22cd6012a4cc56a71`. It reported
**573** valid parses, **186** atomic parser rejections, **3** regular-file
loads, **12** atomic file rejections, **51** forged-plan rejections, **116**
checked queue actions, **13** counted marker acknowledgments, **5** expected
runtime failures and **4** lifetime cycles. The direct executable also passed
under a 15-second subprocess timeout: 0.022 seconds and 9248 KiB peak child RSS.
The [assignment record](development/2026-11-13-next-phases/27-replay-acceptance.md)
retains exact source/library/executable hashes and commands. This is the
isolated helper gate; the integrator qualifies full native CMake registration
and the complete application's workflows separately.

## Limits

Linux dummy execution is the observed platform result. Conditional Windows
symlink checks print an explicit not-run reason when link creation is denied;
POSIX FIFO checks are absent there. Windows/macOS and native window-manager
constraints remain separate runs. Sparse-file rejection plus the loader's
same-handle bounded-read source inspection supports this file-size check;
concurrent file replacement/growth races are not dynamically induced here.
The live window must outlive its helper. Deliberately dangling window pointers
are outside the public precondition and are not passed to SDL.

Acknowledgment proves queue delivery, never UI application, Session callback
application, audio correctness or sample timing. No physical keyboard/mouse,
capture, input-device timing, latency, screen-reader or acoustic-fidelity claim
follows from this gate. Whole-application replay acceptance belongs to its own
maintained executable workflow test.
