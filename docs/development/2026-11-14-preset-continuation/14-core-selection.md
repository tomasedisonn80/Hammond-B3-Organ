# A14 — Exclusive core registration selection

## Scope and source

Actual assignment: **A14**, wave **3**, worker
`/root/w03_a14_core_selection`. This implements the frozen
`exclusive-fixed-registration-core-v1` contract after reading `AGENTS.md`, the
project plan, current README/status/next-step/log context, the selection,
core and state/parameter contracts, and the A01–A03 source findings.
The session production baseline is
`b79086f6bb0c42b97130c721c5c73c7c97a13887`; the integrator reported a later
documentation checkpoint during this assignment. The tested implementation
was an explicitly copied source snapshot, identified below, rather than an
assertion that an uncommitted worktree equals that baseline.

Owned changes are `include/hammond/Types.h`, `include/hammond/ControlState.h`,
`src/ControlState.cpp`, `include/hammond/Engine.h`, `src/Engine.cpp`,
`tests/test_fixed_registration_engine.cpp`, and this note. Existing core tests
were exercised without modification. A13 owns the immutable fixed-data module,
generator and CMake integration; its exact API was coordinated before use.
A15 owns saved-state I/O. No adapter, parameter, Session, shared status,
source-catalog/PDF, Git ref or publication operation was changed by A14.

## Implemented behavior

- Appended `EventType::SelectPreset = 14`, leaving 0–13 and the event layout
  intact. Whole-request preflight admits finite integral 0–11 values, index
  zero and either valid manual; negative zero means Cancel.
- Appended the two default-None retained fixed modes to `ControlSnapshot`.
  Full validation rejects invalid modes even on cancelled manuals. The new
  copied-state helper validates every field before reporting Cancel, a fixed
  key or a remembered bank. Checked queries preserve their destination on
  failure, including before Engine preparation.
- Implemented fixed/Cancel/bank transitions without replacing bank data.
  Selected-bank drawbar edits keep their remembered-bank meaning. Cancel
  preserves fixed memory. Both legacy and new bank selections clear fixed
  mode and reconnect routing.
- Corrected the legacy `SelectBank` no-op guard: choosing an already remembered
  B exits an enabled fixed route. The new event dirties coefficients only when
  the selected manual's bank, mode or route changes.
- Resolved the active nine-position vector once per enabled manual at
  coefficient rebuild. Fixed rows use A13's checked immutable lookup;
  bank mode uses the same existing retained array. Key/drawbar/tone iteration,
  gain lookup, coherent accumulation, pedal contribution and final arithmetic
  remain unchanged.
- Shared one private upper-percussion eligibility predicate between mixing and
  copied diagnostics: On, upper route enabled, no fixed mode, bank B.
  Fixed rows receive all their documented taps without upper-B masking or
  compensation. Selection performs no preparation, panic, note change or
  elapsed readiness update.

## Executed focused qualification

**All six directly compiled C++ test executables passed.** These are direct
compiler/executable runs, not a claim of six CTests or a complete product build.
GCC **14.2.0** compiled the nine required core translation units and each test
with C++20, `-O2`, and the repository's complete strict warning set with
`-Werror`; no compiler diagnostics were emitted. The source files and their
transitive headers were copied into `/tmp/hammond-preset-a14` before compilation,
so a concurrently edited I/O or adapter file could not alter an object layout.
All copied repository inputs still matched their recorded hashes after the
final test. No older static core library was linked against newer live headers.

| Executable | Observed result | Executed coverage |
| --- | --- | --- |
| `test_fixed_registration_engine` | Pass, final run 1.125 s | 108 literal-row/rate/contact audio cases; 532 invalid requests with later audio continuation; detailed cases below. |
| `test_controls` | Pass, 0.150 s | Existing retained bank controls, legacy reference rendering, held-key switching, cancellation, restore and rejection behavior. |
| `test_engine` | Pass, 0.194 s | Existing independent sine/routing, musical state, rejection and three-rate/six-partition timelines. |
| `test_console_engine` | Pass, 0.351 s | 1,179 source/audio oracles; 318 closed-form readiness checks; 42 partition/disconnected comparisons; 16 failure-preservation cases. |
| `test_pedal_engine` | Pass, 0.017 s | 1,442 exact audio comparisons; 11,921 exact phase comparisons; 19 rejected-event cases. |
| `test_engine_rate` | Pass, 0.932 s | 36 rate-pair scenarios; 81 rejected changes; 6,144 same-rate calls; 13,776 complete snapshots; 32,603 exact audio frames, plus independent numerical oracles. |

The new suite checks all **1,600** retained-mode/bank/route combinations and
**960** selection transitions, accepted no-ops, every invalid byte-valued
retained mode and selector, full-snapshot helper validation, and checked query
destination preservation. All eighteen audio references come directly from
`PresetTestOracle.h`, not the production lookup or generated table. The
108 cases cover each row at 44.1, 48 and 96 kHz with ideal and moving contacts,
both held folded chords and pedals, a timed selection during continuing phase,
and later audio. Fixed data never overwrites the four deliberately different
retained banks.

Additional executed cases cover editing all four retained banks while fixed
audio remains bit-identical, returning to each bank through legacy events from
enabled and cancelled fixed states, source/contact/pedal history under
zero-frame selection and restore, partial release motion, and independently
silencing only the cancelled manual while the lower route and pedals continue.
All nine upper fixed rows bypass percussion, one-foot masking and sustain
compensation at all three rates. Held B/fixed/B readiness is checked against
closed-form decay/recovery with a `2e-12` absolute budget, and future bank-B
audio is compared against a matched continuously evolving reference.

Both orders of same-offset bank/fixed events have explicit reference audio.
Zero-duration B/fixed/B changes no history; lower selection leaves upper
percussion unchanged. One 2,305-frame timeline matches bit-for-bit across
partitions 1, 17, 64, 127, 512 and 1,024 at every supported rate and both contact
modes, including disconnected-output evolution. Invalid selectors follow
otherwise valid control, note and pedal events; rejection preserves every
caller-output element, controls, all source phases, all manual contacts and
targets, held pedals, percussion readiness, last pedal frame, clock and later
audio. Invalid hidden modes also reject whole-control restore transactionally.

The first strict build and initial new-suite run passed. The final new-suite
revision added explicit cancelled-bank return and reverse same-offset ordering
coverage and also passed; no earlier failed runtime result is being hidden.

## Build inputs and reproducible commands

Working directory was
`/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`. Required core source stems:

```text
ContactBank ControlState Engine FixedRegistration PedalRouting PedalVoice
Percussion Profile TonewheelBank
```

The copied generated pedal header and compiled profile came from the
integrator's already prepared `/workspace/scratch/a472c29da8b3/build-baseline`.
The copied generated fixed header came from A13's admitted
`/tmp/hammond-preset-a13/generated/hammond/generated/FixedRegistrationData.h`.
Their identities below are part of the tested snapshot. No profile or source
catalog was regenerated or changed by this assignment.

Each listed source was compiled separately with the following exact command
shape, substituting its stem for `NAME`:

```sh
c++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  -I/tmp/hammond-preset-a14/include -I/tmp/hammond-preset-a14/generated \
  -I/tmp/hammond-preset-a14/tests \
  -c /tmp/hammond-preset-a14/src/NAME.cpp -o /tmp/hammond-preset-a14/NAME.o
```

Each of the six test stems in the table was then compiled and linked with the
same flags/include paths, these definitions, its copied `tests/NAME.cpp`, all
nine newly built objects, and `-o /tmp/hammond-preset-a14/NAME`:

```sh
'-DHAMMOND_TEST_PROFILE="/tmp/hammond-preset-a14/nominal.b3p"'
'-DHAMMOND_SOURCE_DIR="/workspace/scratch/a472c29da8b3/Hammond-B3-Organ"'
```

Each resulting executable was invoked directly with no arguments. The final
new-suite standard output was:

```text
fixed registration engine: 108 literal-row/rate/contact audio cases, 532 rejected calls with future-audio continuation; passed
```

The complete frozen input SHA-256 manifest follows. `generated/` and
`nominal.b3p` paths are relative to the copied test snapshot; other paths are
relative to the repository.

```json
{
  "include/hammond/ConsoleModel.h": "e6ef911961c1aca1ce72bca8d2cfba9c765665d7cef30446adfe53b9ba59db51",
  "include/hammond/ContactBank.h": "a083dcd65d989cc5be78a393fad74f40cbb530e33f89492d523e406f477be99d",
  "include/hammond/ControlState.h": "aab82b082f9cf77dadf763148cade9eae04f6f7df68b302b1832f21f78034856",
  "include/hammond/Engine.h": "da1adc2e635e5acfa3f214447b722122c3a162eb9ec602ba14fa744eb9d39ba6",
  "include/hammond/FixedRegistration.h": "4548240ce25f5200442bfe4607ba755feee822a91c8b1a97af9bf7837e3634a0",
  "include/hammond/PedalRouting.h": "e77c52f1c541ef301fff4c8b0fb9a9449f93be632630326f2d7640694384bea8",
  "include/hammond/PedalVoice.h": "694961946eac838c689547fc403c84e49a429f3337816ea9ad3a751bf305ddaf",
  "include/hammond/Percussion.h": "5eb87fdd2342410b63f7e6ec55ac11c645d2b7185287fb49ff8e5e53095a2722",
  "include/hammond/Profile.h": "b1180b3dc04030e0555ef3eb44a21617fc06e93150a9ecb48ebb05955b3e5fd0",
  "include/hammond/TonewheelBank.h": "694acaece901e18b4e089264218d8f217cfe3d2f8ea2a9adfb5ff6773b2f756b",
  "include/hammond/Types.h": "0abecd960c50186da5348570bfad820cf0f7f3c89c675743eb810b2ebda0dda8",
  "include/hammond/detail/Decimal.h": "ae2c63ec61e823fda198a4951e029df11184980c9bc8394142a2d46951338c42",
  "src/ContactBank.cpp": "91747d963d6cec74b3be12549abd8e816f4c176ce172fba52f9cdbc593c6e9e1",
  "src/ControlState.cpp": "9026aa0338b905a005912e4c7734eedd36cbf204ae43fa4631bdc5aadaa86a5d",
  "src/Engine.cpp": "ea94f27be2ce6e374537c616bdde34c32c3276df6f7f24e112f52a35d1a4bd3a",
  "src/FixedRegistration.cpp": "690e45e5738c3c25ae1082e31a49debdfbca994b68d6b0a28ef865df7991769d",
  "src/PedalRouting.cpp": "8d05dedb9015863dfd88668e5ea27d6be42ea1fcdb600cf34787e446e14d22af",
  "src/PedalVoice.cpp": "88fb5afa936784be351b2940ee6f81216975112f860b007d40f3b6a3d9f7c6ba",
  "src/Percussion.cpp": "823685b879fad12492f86bbf5e78294668ee9b0567c58c26ac0b44aa28b1390a",
  "src/Profile.cpp": "80f5c7456311c77a83df23c548c02cabbf9c1cf1621cff89867d0d0c688ebe54",
  "src/TonewheelBank.cpp": "ebc26e2e61cc88d5525e390abf3897ebeae38e652c13ea3ef02818b2b3849e0b",
  "tests/PresetTestOracle.h": "c2361bc68ff297977e246da391872fc69fe380d8bdd6230efb6a77a9aad61274",
  "tests/TestSupport.h": "8869acab1e7492699b656984c7b24eb6d33f09dad6f989814a8a0c04e3c86be5",
  "tests/test_console_engine.cpp": "e83b53b2f34fca27c16b515a846a9b1d9e63dfa995767341e5b5526f11466c76",
  "tests/test_controls.cpp": "d24544051f8f72cf62635657302bc64aff14fc088a122fb502aed7889bd4b477",
  "tests/test_engine.cpp": "b9b27637dca3205fadde34bde3cdad9b1789a96f67d3b71bd83ee4734cf80289",
  "tests/test_engine_rate.cpp": "78fe4833d01c0b20f703de799ae3a9767a2a5545dc3f06d8092d819d6a371dfe",
  "tests/test_fixed_registration_engine.cpp": "948cec6d39dba622690f85a3c8af8b64eac0d225081d0a1cc8190dce97c570d7",
  "tests/test_pedal_engine.cpp": "17ad6af9b42c8d1659ca2b7d9c289284f681429694821b28097cc6d31bd00371",
  "generated/hammond/generated/PedalRoutingData.h": "efddce2ea3619a7dd9e153382e307928f7aed60bdb8a0318ca6c0e71ee5f6034",
  "generated/hammond/generated/FixedRegistrationData.h": "66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6",
  "nominal.b3p": "b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f"
}
```

## Remaining integration and evidence limits

The bounded core implementation is ready for the integrator's coherent full
build. Saved-state v4/legacy migration, both atomic encodings, parameter and
adapter allowlists, host ordering, standalone/native controls and independent
callback allocation/lifetime acceptance remain assigned integration work;
none was qualified by this isolated core build. This assignment did not run
sanitizers, a complete CMake build, native UI/host checks or hosted CI. Root owns
shared documentation, final source freeze, acceptance, commit and publication.

This is the atlas-supported exclusive nominal selector. The frozen chapel
digits remain documentary tap indices used with the existing nominal gain
law. Physical multi-latching, contact/load networks, acquired factory Table IV,
specimen gains and held-key B-transition measurements remain separate gates.
The scanner/AO-28/Leslie and physical fidelity scopes are unchanged.
