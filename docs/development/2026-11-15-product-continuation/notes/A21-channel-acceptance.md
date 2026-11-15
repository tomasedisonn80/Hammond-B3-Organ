# A21 — independent MIDI channel-mode boundary acceptance

Actual worker `/root/w04_a21_channel_acceptance`, wave 4. Read the full standing
instructions, M0–M9 plan, session scope/checkpoint, channel-mode contract and
Session/MidiInput/UiModel implementation. Starting HEAD `af006b0` with the
integrator's frozen wave-3 production overlay. Owned only
`apps/standalone/tests/test_standalone_channel_acceptance.cpp` and this note.

Added complementary acceptance beyond the author's ordinary scope tests:

- An exactly full 256-command FIFO containing sound-off, notes and expression
  edits matches separately specified physical Engine events. Same-pitch UI,
  other-manual and pedal owners survive the addressed retirement.
- A second full queue deliberately overflows. All queued changes are discarded,
  original applied controls survive, and the existing global recovery releases
  every owner. A subsequent audible press matches the continuously running
  physical reference sample-for-sample.
- Every remaining domain byte, both invalid-bus ranges and both domains' channel
  ranges are rejected before sequence reservation, including at a finite
  sequence budget's exact endpoint. An untouched peer matches all audio and
  holds; only a later valid command requests the declared exhaustion recovery.
- CC121 on each remapped division with inverted calibration preserves desired
  drawbar/pedal edits across real partial and stale acknowledgments, subsequent
  scoped sound-off, and final acknowledgment. Repeated reset emits no duplicate
  control update; owners and calibration remain intact.

GCC 14.2.0 isolated Release compilation passed with C++20, `-O2 -DNDEBUG`
and all project warning flags plus `-Werror`. From the repository directory,
compile the new test with `-Iapps/standalone -Iinclude -Itests`, the existing
`build-native/generated` include path, `HAMMOND_TEST_PROFILE` pointing to that
build's `nominal.b3p`, and `HAMMOND_SOURCE_DIR` pointing here. Link read-only
`build-native/apps/standalone/libhammond_standalone_support.a`, then
`build-native/libhammond_core.a`, with `-pthread`.

The isolated executable passed **2 saturated batches, 3,444 invalid scopes,
3 partial-ack reset cases and 812 exact stereo sample comparisons** (0.004s).
Whitespace validation passed. Test SHA-256: `22dc6f09c3c89395dfb7c2cf24a7655649fbf020c140f68d32285ac26896533d`.
Production dependency SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `apps/standalone/Session.h` | `dc729465578ed02a8cb0640d07de679be33d731cdece947a09bce736bc84c929` |
| `apps/standalone/Session.cpp` | `256c0ef82e5a6639b3437d01754a0b27673a9d4096fe099a8b66351818ef2ae3` |
| `apps/standalone/MidiInput.h` | `4024723a91c28c8884ca065d167524c599d6816d047bcc834ea025b1dd734394` |
| `apps/standalone/MidiInput.cpp` | `4ddd655fb4a21040f2f83228fb23e38f98d0abe21d5bce7f0e28d064b5b7477c` |
| `apps/standalone/UiModel.h` | `d94e90be25812c6d21b61f37f2b0547704d14866c45fbbb21131ec70b6389bd3` |
| `apps/standalone/UiModel.cpp` | `49c68995aad96aa5e316613412c93931a1082d0e4a3ad3758ac63484af963064` |

Profile SHA-256: `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
No production defect found. Root next: coherent glob-discovered CTest
`test_standalone_channel_acceptance`, then broader integration. No shared build
mutation, commit, physical-device, concurrency or non-ideal Session claim.
