# Assignment 26 — bounded native UI replay

- Canonical agent: `/root/w05_a26_input_replay`, actual assignment 26, wave 5,
  standalone sixty-assignment/ten-wave session. No earlier assignment counted.
- Inspected foundation commit: `738162f0bc36f88f8c76268d04831862a8118d10`, tree
  `915e55dc7c3ad022042b188498aa41f2a7f40795`. This work was uncommitted and
  concurrent; these identities do not qualify the later live worktree.
- Owned only `apps/standalone/ScriptedInput.h`, `ScriptedInput.cpp`,
  `docs/STANDALONE_INPUT_REPLAY.md` and this note. Root owns main/CMake wiring;
  assignments 27/28 own maintained parser and actual workflow acceptance.
- Read standing instructions, current scope/status/session records, main input
  handling and UiModel contracts. Atlas product review covers pp. 379–420;
  queue/UI engineering does not establish the atlas's physical model fidelity.

## Implemented contract

The [format contract](../../STANDALONE_INPUT_REPLAY.md) defines exact header,
duration, key/modifier tokens, bounded coordinates, resize, focus and quit.
Parser admission is whole-file and transactional: 64 KiB, 256 actions, duration
250–10000 ms, nondecreasing offsets strictly below duration, fixed value-owned
plan, no unknown/trailing/partial/nonfinite fields. Native file handles reject
symbolic/reparse leaves and nonregular files, including FIFO/device inputs.
No core, parameter, saved-state format or audio command vocabulary changed.

One main-thread helper copies and validates the plan, pushes due input once,
and reports sticky SDL refusal. Physical scancodes, unshifted US keycodes,
window IDs, modifiers and pointer fields are populated consistently. Resizes
use the actual SDL window and queried dimensions. Consumed-prefix markers
before/after resizing prevent native resize coalescing or immediate window
mutation from reordering geometry relative to preceding/following inputs.

A unique registered final marker follows all scheduled events. Its observed
delivery is separate from elapsed duration and Session callback acknowledgment.
Empty plans are delivered immediately. No waits, files, script-supplied
callbacks or direct Engine operations occur in the pumping path. Parent window
lifetime, main-thread use and final application acknowledgment remain explicit.

## Executed checks and identity

Working directory: `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.
Compiler: GCC 14.2.0. Real pinned SDL2 2.32.10 source at `../SDL2`, commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`; linked `../sdl2-build/libSDL2.a`.
No substitute SDL declarations or fake event loop were used.

```sh
g++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion \
  -Wshadow -Werror -DSDL_MAIN_HANDLED -I../SDL2/include \
  -I../sdl2-build/include -c apps/standalone/ScriptedInput.cpp \
  -o ../a26-scripted-input.o
g++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion \
  -Wshadow -Werror -DSDL_MAIN_HANDLED -Iapps/standalone -I../SDL2/include \
  -I../sdl2-build/include ../a26-replay-probe.cpp apps/standalone/ScriptedInput.cpp \
  ../sdl2-build/libSDL2.a -pthread -lm -o ../a26-replay-probe
SDL_VIDEODRIVER=dummy ../a26-replay-probe
git diff --check
```

All returned success. The temporary focused probe executed malformed-input
preservation, 256/257 action boundary, symlink/directory/oversized-file rejection,
real SDL keys/pointer/focus/quit order across two tied resizes and five consumed
markers, actual final window dimensions, empty-plan delivery, elapsed-regression
failure, repeated-initialize preservation and filtered SDL-push failure without
retry. The probe is temporary scratch work; maintained independent acceptance
belongs to assignment 27. An initial package-file lookup used the nonexistent
`SDL2-static.pc`; inspecting `sdl2.pc` supplied the actual static link flags.

Qualified source SHA-256:

- `ScriptedInput.h`: `294b11d6a2c9b425d766b019b2ff1e7c460a308c93887c648dd7bce1d955c3d5`
- `ScriptedInput.cpp`: `ed6987b1b134737842028e611ed5f03ea67e9b232984284d885ca2c29d27809e`

## Remaining limits and next gate

Root must execute the integrated CLI/event loop with assignment 27/28's actual
parser/workflow acceptance and retain its coherent source identity. This note
claims no complete-app pass, physical capture, audio-callback deadline,
real output-device timing, macOS/Windows execution, native accessibility or
acoustic fidelity. Dummy capture failure remains a release/failure path.
Windows reparse/file handling was source-implemented and not executed here.
No commits, pushes, other workers' paths or shared status files were changed.
