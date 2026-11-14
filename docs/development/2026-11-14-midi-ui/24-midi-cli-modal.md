# A24 — Native MIDI CLI and modal acceptance

Actual assignment: `/root/w04_a24_midi_cli_modal`, wave 4 of the
`2026-11-14-midi-ui` session. This is one newly dispatched worker. No preceding
session worker or acceptance result is counted again.

**Final result:** the strict native replay unit passes, and the complete new
CLI/modal suite passes **15/15 methods / 95 actual subprocesses** on the rebuilt
application. All eleven modal application replays correctly report failure on
this host because ALSA enumeration fails; the suite verifies that failure plus
the delivered keyboard/pointer actions, routing changes and shutdown state.

## Owned changes

Owned paths only:

- `apps/standalone/ScriptedInput.cpp`
- `apps/standalone/native_tests/test_standalone_input_replay.cpp`
- `apps/standalone/native_tests/test_standalone_midi_cli.py`
- This evidence note.

The application already recognizes Ctrl+M and Command+M, but the B3UIREPLAY1
whitelist rejected `M`. The production change adds that exact uppercase name,
`SDL_SCANCODE_M` and `SDLK_m`; it does not change any existing event, modifier,
duration, size, coordinate, file-admission or queue-delivery meaning. The unit
test's independent literal whitelist now includes M and rejects lowercase `m`
and the `SDL_SCANCODE_M` alias. A dedicated actual SDL queue test checks both
complete Ctrl+M and Command+M presses/releases, nonrepeat bits, window identity,
final delivery marker and absence of duplicated delivery.

The new Python suite contains **15 methods**. It imports only Python's standard
library and launches the actual application with independent literal results;
it does not import production handlers, parsers, layout calculations or any
legacy Python acceptance helper. The parent integrator registered
`test_standalone_midi_cli` with a 90-second CTest timeout.
The suite requires `HAMMOND_STANDALONE_EXECUTABLE` and accepts ordinary unittest
method selection. SDL video/audio dummy drivers are explicit for every windowed
case. Syntax/help/list cases use nonexistent SDL drivers to make initialization
order observable.

No main application, old Python workflow/schema/layout fixture, core, parameter
identity, state format, MIDI replay feature, shared status file or ledger was
edited by this worker. No commit, push or subagent dispatch was performed.

## Acceptance coverage and bounds

| Area | Independent acceptance |
| --- | --- |
| Channel syntax | All three options reject signs, leading/trailing spaces, floating/exponent/hex forms, nonnumbers, trailing junk and integer overflow; 0/17/256 are out of range. Empty/missing arguments reject. Channel 1 and 16 are admitted in every route position, including accepted decimal leading zeros. |
| Distinct routing | Each default-channel collision rejects even with `--help`, proving full validation precedes the early help return. |
| Repeated options | Repeated list, port and each routing option reject; both orders of conflicting audio/MIDI lists reject. |
| Exact name arguments | Numeric strings, whitespace, option-looking names and Unicode remain names. 1024 encoded bytes are admitted; 1025 ASCII bytes and 1026 UTF-8 bytes reject. Existing state, image and diagnostics sentinels remain byte-identical during parse/help admission. Embedded NUL is not passed through `subprocess`, whose OS argument boundary cannot represent it. |
| List ordering | `--list-midi` reaches the real backend and returns its actual success or failure with deliberately invalid video/audio drivers. An unavailable backend, successful empty/nonempty enumeration and enumeration failure remain separate accepted outcomes; no ports are opened by listing. |
| Startup | Omitted port leaves MIDI inactive, generation zero, no packet/callback activity and no decoder epoch, with default or explicitly changed routing. Successful dummy audio smoke is still required. |
| Negative open | One unique, explicitly nonexistent exact name, including surrounding spaces and Unicode, is requested with finite `--smoke-ms 600`. The name remains exact in diagnostics, startup and smoke fail honestly, and no MIDI input activates. Backend-disabled and backend-enabled failure counters have separate expectations. |
| Open/close | Ctrl+M and Command+M suppress keyboard playing while the modal is open; Escape restores ordinary playing. Pointer opening/Apply/Disconnect/Close uses independent literal centers at 960×700 and 1280×900 for the existing 740×520 modal. |
| Eight controls | Previous port, next port, upper/lower/pedal channel, Apply, Disconnect and Close are navigated in order. Any browsed choice is explicitly returned to No input before Apply. Forward Tab wraps after eight controls; reverse Tab from the initial control reaches Close. |
| Channel edits | Home/End and all arrow directions exercise 1/16 wrapping; applying No input updates routing without starting an epoch or opening a device. |
| Rejected Apply | Duplicate staged channels preserve previously applied routing. A second case fixes only the duplicate in the same open dialog, proving the other staged channel values survive rejection and are subsequently applied. The earlier error remains visible in the replay failure accounting. |
| Escape/guards | Escape discards unapplied changes when reopened. Shortcut repeats, Alt shortcuts, modified Tab and repeated navigation are ignored. |
| Honest diagnostics | All modal cases require all planned events delivered, replay completion, final Session acknowledgment, no held notes after shutdown, quiescent MIDI and running dummy audio before shutdown. Enumeration errors cause `replay.passed=false`, exit 1 and the exact additional replay error; they are never mislabeled successful replays. |

Every process has a 12-second outer timeout. UI plans use the existing bounded
format and durations below its 10-second maximum. No normal case applies a
discovered MIDI input. The nonexistent exact-name case is the only attempted
native open. Tests do not require physical ports, a working sequencer, or any
hardware callback. Empty/unavailable branches are specified but are not claimed
as locally executed on the enabled ALSA binary below.

## Source reading and scope

Read `AGENTS.md`, README, current status/next steps, the standalone handoff,
project plan, atlas review, MIDI/UI scope, ScriptedInput header/implementation,
native input replay tests, the actual application CLI/modal/diagnostic code,
`UiModel` header geometry and `midi_overlay_layout`.
The relevant atlas chapter text was read from the supplied per-page extraction:
chapter 068, pp. 415–420, and chapter 071, pp. 433–438. Those chapters distinguish
keyboard/pointer operation from native accessibility and physical/host evidence.
This assignment makes no full-PDF reread, visual-reference match, screen-reader,
host, device latency or instrument-fidelity claim.

Observed checkout HEAD: `e09107414896c2c53dad124a74f60c8043fadfe4`.
The local `origin/main` tracking reference was
`7b36cfac2565397191b3df5e07112611e7f1b0e1`; this is not a newly fetched publication
verification. Concurrent source work was present and preserved. The isolated
unit build below uses only this worker's ScriptedInput source/test, their stable
header, and the existing SDL static library, without rebuilding or modifying
another worker's build products.

## Executed verification

Working directory: `/workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ`.
Toolchain: GNU C++ **14.2.0**, Python **3.12.14**, C++20 with strict warnings.

1. Python compilation in memory passed for the new suite.
2. A fresh isolated strict C++ compile/link passed with:

   ```sh
   /usr/bin/c++ -DSDL_MAIN_HANDLED -Iapps/standalone \
     -I/workspace/scratch/cd4bd06ce68f/build-native/_sdl2/include \
     -I/workspace/scratch/cd4bd06ce68f/build-native/_sdl2/include/SDL2 \
     -I/workspace/scratch/cd4bd06ce68f/build-native/_sdl2/include-config-release/SDL2 \
     -O3 -DNDEBUG -std=c++20 -Wall -Wextra -Wpedantic -Wconversion \
     -Wsign-conversion -Wshadow -Werror apps/standalone/ScriptedInput.cpp \
     apps/standalone/native_tests/test_standalone_input_replay.cpp \
     /workspace/scratch/cd4bd06ce68f/build-native/_sdl2/libSDL2.a -lm -pthread \
     -o /workspace/scratch/cd4bd06ce68f/a24-input-replay
   SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
     /workspace/scratch/cd4bd06ce68f/a24-input-replay
   ```

   Actual result:

   ```text
   standalone replay acceptance (SDL dummy): 590 valid parses, 188 atomic parser rejections, 3 regular-file loads, 12 atomic file rejections, 51 forged-plan rejections, 122 checked queue actions, 14 acknowledged markers, 5 expected runtime failures, 4 lifetime cycles
   ```

3. The pre-rebuild enabled native executable passed **8/8 compatible methods**,
   **86 subprocesses**, in **4.036 seconds**. Selection consisted of all seven
   `test_cli_*` methods and
   `test_modal_pointer_open_apply_disconnect_close_at_two_sizes`. The two pointer
   modal executions each observed the actual ALSA enumeration failure caused by
   unavailable `/dev/snd/seq`, completed UI delivery and acknowledgment, and
   honestly failed the application replay. Their expected failure assertions
   passed: **0 successful UI replays, 2 expected failed UI replays**. The CLI
   no-input smoke cases passed; the explicit nonexistent-name startup failed as
   expected.
4. The first full integration run on rebuilt application SHA-256
   `48e308cfea28c7d26c9bf3efe99bf5a52eee80064db39c31f4b878e13bebd42e`
   ran **15 methods / 95 subprocesses** in **10.628 seconds**, with eleven modal
   subcase failures. Every failure was the same exact expected-message mismatch:
   the concurrent main change replaced `Native input replay failed...` with
   `Native replay failed...`. The earlier delivery, note-count, enumeration and
   error-count assertions all completed. A temporary updated literal verified
   **15/15 methods** on the same binary in **10.693 seconds**, including all
   channel, focus, invalid-Apply, pointer and Escape assertions. This run observed
   **13 enumeration errors, 0 successful UI replays and 11 correctly expected
   failed UI replays**. A23 then chose to preserve the original UI-only error
   wording, and this test restored its original independent literal rather than
   accepting both strings. The temporary pass does not replace final verification
   of the compatibility rebuild.
5. The integrator-built `test_standalone_input_replay` executable passed with the
   same complete counts as the isolated unit above. Its SHA-256 was
   `38d71855a5d46851879455dafe7e51edea74774e31b4410e31ada20e91ad4ae9`.
6. After A23 restored the original UI-only error wording, the final original
   expected literal and rebuilt application passed **15/15 methods / 95 actual
   subprocesses** in **10.769 seconds**. The observed totals remained
   **13 enumeration errors, 0 successful UI replays, 11 correctly expected
   failed UI replays**. All seven previously pending keyboard-modal methods
   executed and passed their assertions. Final application SHA-256:
   `e8871447021a1373e2bfdc262a513d12487e49fd0e833bad068f226a6938ed2d`.
   The exact direct full-suite command is retained below. No further test or
   production change was needed after that compatibility correction.
7. `git diff --check` passed for the tracked owned changes. Separate
   `git diff --no-index --check /dev/null <owned-path>` checks for the added
   Python and note files emitted no whitespace diagnostics; their exit 1 denotes
   an addition relative to `/dev/null`.

The tested pre-rebuild app was
`/workspace/scratch/cd4bd06ce68f/build-native/apps/standalone/hammond_standalone`,
SHA-256 `072f52ad299592f997af2aaeb2a140a3417e4a77542dd6afbfbae9fd4a60eb4b`.
It does **not** contain M admission, so its historical eight-method pass cannot
qualify the seven keyboard-modal methods. The rebuilt full-suite result above
is distinct. No failed keyboard run against the known-old parser was invented
or silently skipped by the suite.

| Isolated input/build product | SHA-256 |
| --- | --- |
| `ScriptedInput.cpp` | `7c143db56b1eda113886a3e2cd63ec3570483921adc2b57e1a4c8f0ef6235531` |
| `test_standalone_input_replay.cpp` | `b9bb55df6596ad65c080b0a600d69c16b58c70b97ef1b148ed7191659756d8e1` |
| Final Python test source | `f35a0ecb9b5efee711681664fa8e7af9e010ec4deee89c2d8f4d3694503b9b23` |
| Isolated unit executable | `0dd4a31a02486745b12483eeda018b564ec0f06899dd78bddfe940171a7dc240` |
| Existing `libSDL2.a` | `1e471c6f7a2c14eba9230c44e743e27c5dc68a243308427e5004d4e446db9324` |

## Reproduction and remaining qualification

The final complete run used this direct command. The parent also registered the
equivalent `test_standalone_midi_cli` CTest entry; this worker does not claim an
additional CTest invocation merely because registration exists.

```sh
HAMMOND_STANDALONE_EXECUTABLE=/workspace/scratch/cd4bd06ce68f/build-native/apps/standalone/hammond_standalone \
  python3 apps/standalone/native_tests/test_standalone_midi_cli.py
```

On this ALSA host, modal application replay failures are expected because
enumeration fails; the suite verifies those precise failures and the independently
observed modal behavior. The final rebuilt binary identity above is distinct
from the pre-rebuild eight-method result and the intermediate generic-error
binary. Backend-disabled, successful empty enumeration, populated enumeration
and actual macOS/Windows runs remain separate execution gates. Legacy Python
schema/layout maintenance belongs to A25, and the new MIDI script feature belongs
to A23. Root owns coherent broader qualification, shared records and publication.
