# A14 — native MIDI adapter implementation

Actual worker `/root/w03_a14_midi_adapter`, wave 3, based on
`da48180390a9fd473643d1759c153cb9d37ecfb6`. Read standing instructions, session
scope, both complete MIDI contracts and A10's review.

## Delivered

- Appended `ScopedSoundOff` without changing existing variant indices. Both
  ownership domains admit buses 0–1/channels 0–15 before queue/sequence reservation.
  Application checks ideal contacts before canonical scoped ownership retirement;
  a future non-ideal refusal uses existing global failure recovery.
- CC120/121 accept zero only. CC120 preserves other owners and continuous source
  histories; CC121 emits expression 1.0 through the existing UI edit route and
  bypasses calibration. CC123's historical 0–127 acceptance remains unchanged.
- Added immutable epoch endpoint/inversion calibration, validation, destination-
  preserving mapping refusal and last-accepted accessor. Default CC11 arithmetic
  is bit-exact for all 128 values; other controllers retain their mappings.
- Added channel-mode and calibration author tests. Extended the existing decoder
  oracle with exact canonical scopes, every nonzero CC120/121 value, remapped
  channels and updated diagnostic counts. Unsupported-controller coverage and
  exhaustive CC123 checks remain; rejected timestamp observation now uses CC122.

Owned production files are `Session.h/.cpp` and `MidiInput.h/.cpp`; owned tests
are `test_standalone_midi_input.cpp`, `test_standalone_channel_modes.cpp` and
`test_standalone_expression_calibration.cpp`, all under `apps/standalone/tests`.
No main/paint/CMake/core/parameter/state changes or commit were made by A14.

## Executed checks

From the repository, GCC 14.2.0 compiled Session, MidiInput, UiModel and the
three tests with C++20, `-O2 -DNDEBUG -Wall -Wextra -Wpedantic -Werror`, linking
the unchanged baseline core. All three executables passed (0.003/0.007/0.002s).
`git diff --check` passed. Exact commands/output are retained in
`/workspace/scratch/5b7d983ac078/a14-checks/verification.log`; the shared build
was read only. Source manifest SHA256 (sorted `sha256sum` lines for those seven
files plus `UiModel.h/.cpp`):
`2ed440b1484b9ae1c39bac60c1449d2532b635b88197d210173a3e209aac960a`.
Linked `libhammond_core.a`:
`2e60507a07753f9d54b9451c13fe882a27fd4d8c1b82186a40afed360d787f24`.
Profile `nominal.b3p`:
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.

Next: integrate CLI/modal/reconnect configuration, then rebuild all affected
consumers and run independent acceptance from coherent source. These isolated
author checks do not establish native-device, non-ideal Session, DAW, allocation,
deadline or physical fidelity qualification.
