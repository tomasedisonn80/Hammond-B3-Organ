# A15 — Canonical state4 and legacy migration

Assignment: **A15, wave 3**, worker `/root/w03_a15_state_migration`.
Date: **2026-11-14 UTC**. This worker implemented the frozen
`exclusive-fixed-registration-v1` / `fixed-registration-state-parameters-v1`
saved-control grammar. No child assignments, commits, pushes, full-tree builds,
plugin edits or parameter-registry edits were performed by this worker.

## Owned changes

- `include/hammond/ControlStateIO.h`: documents canonical state4, exact catalog
  binding, all three legacy readers and independent default initialization.
- `src/ControlStateIO.cpp`: writes the exact catalog record and each manual's
  raw fixed token; reads those fields only for version 4; explicitly admits
  pedals in both versions 3 and 4; preserves the existing stream, decimal,
  byte-limit and final-assignment boundaries.
- `tests/test_control_io.cpp`: retains the literal version-1/2/3 oracles, adds
  independent canonical state4 bytes and exhaustive new state coverage, and
  compares both retained fixed modes in semantic equality.
- `tests/test_pedal_controls.cpp`: ownership was explicitly extended by the
  integrator to writer/migration expectations and fixed-field equality. It now
  compares new writes to an independent state4 oracle while keeping literal
  legacy constructors, input grammar checks and existing core/route assertions.
- `docs/CONTROL_STATE_FORMAT.md`: records the complete 81-token, 12-line state4
  grammar, immutable catalog binding, raw selection memory and migration table.
- This assignment report.

The implementation consumes A13's immutable data identity API and A14's stable
snapshot header/validation. It does not introduce a duplicate effective selector
or put catalog strings in a snapshot. New writes always use `B3CONTROLS4`, even
with both fixed modes `none`. Unknown IDs and mismatched hashes reject before
publication, including when neither fixed mode is active. Cancelled manuals
retain both their remembered fixed row and adjustable bank.

Every parse starts from a fresh `ControlSnapshot`. Versions 1/2/3 therefore clear
both fixed modes to `None` independently of destination contents. Version 1
still resets percussion to Off/Second/Normal/Slow, and versions 1/2 still reset
pedals to `[0,0]`. Supplied historical controls retain their original meaning.
Missing state4 records never activate a legacy fallback. The 16,384-byte limit,
16,385-byte maximum consumption, signed expression zero, subnormal handling,
classic locale, nearest-rounding guard, caller-mode restoration, stream exception
policy and serializer alias behavior remain intact.

## Executed acceptance

All commands ran from:

```text
/workspace/scratch/a472c29da8b3/Hammond-B3-Organ
```

Compiler: `g++ (Debian 14.2.0-19) 14.2.0`, C++20. The focused tests do not use a
runtime profile; `HAMMOND_TEST_PROFILE="unused"` satisfies the shared support
header without loading one. They compile the current source files together,
rather than linking an older library to the enlarged snapshot.

A13 supplied the admitted header under `/tmp/hammond-preset-a13/generated`.
Its reproduction command, from this checkout, is:

```sh
python3 tools/compile_fixed_registrations.py \
  --input data/registrations/atlas-chapel-nominal-v1.json \
  --review-a data/registrations/review-a-chapel.csv \
  --review-b data/registrations/review-b-chapel.csv \
  --output /tmp/hammond-preset-a13/generated/hammond/generated/FixedRegistrationData.h
```

That generator command was executed by A13, not rerun by A15. A15 verified the
resulting header path and retained its hash below.

### Focused optimized suites

```sh
mkdir -p /tmp/hammond-preset-a15
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Werror \
  -Iinclude -Itests -I/tmp/hammond-preset-a13/generated \
  '-DHAMMOND_TEST_PROFILE="unused"' \
  '-DHAMMOND_SOURCE_DIR="/workspace/scratch/a472c29da8b3/Hammond-B3-Organ"' \
  tests/test_control_io.cpp src/ControlStateIO.cpp src/ControlState.cpp \
  src/FixedRegistration.cpp -o /tmp/hammond-preset-a15/test_control_io
/tmp/hammond-preset-a15/test_control_io

g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Werror \
  -Iinclude -Itests -I/tmp/hammond-preset-a13/generated \
  '-DHAMMOND_TEST_PROFILE="unused"' \
  '-DHAMMOND_SOURCE_DIR="/workspace/scratch/a472c29da8b3/Hammond-B3-Organ"' \
  tests/test_pedal_controls.cpp src/ControlStateIO.cpp src/ControlState.cpp \
  src/FixedRegistration.cpp -o /tmp/hammond-preset-a15/test_pedal_controls
/tmp/hammond-preset-a15/test_pedal_controls
```

Both final builds and both runs exited **0**, with no compiler warnings under
`-Werror`. Their observed output was:

```text
Control persistence tests passed; 2240 malformed inputs preserved destination semantics.
Pedal controls passed: 105 round trips, 243 legacy migrations, 134 rejected documents, 494 rejected snapshots; all failures preserve destinations.
```

The IO rejection count includes parser documents and invalid serializer
snapshots, not 2,240 distinct input documents. New IO assertions include:

- All 100 raw fixed-mode pairs × all 16 remembered-bank/route combinations:
  **1,600** exact canonical comparisons and round trips. Fixtures include
  cancelled fixed memory, all four varied banks, negative expression zero,
  nondefault percussion and nonzero pedals.
- All three historical input grammars into every one of those destination
  combinations: **4,800** migrations, explicitly checking the fixed reset and
  each version's percussion/pedal policy. Literal old fixtures remain unchanged.
- Every invalid byte-valued fixed enum, 10 through 255, in either manual with
  its route both enabled and cancelled: **984** serializer rejections preserving
  the previous destination bytes.
- Every catalog-ID character position and every SHA character position mutated,
  including well-formed different hexadecimal digests, uppercase hexadecimal
  letters and invalid lengths. The baseline uses two `none` modes; additional
  rejection fixtures retain fixed rows. All destination fields remain intact.
- Missing, extra, duplicate and reordered records, malformed fixed names and
  numeric aliases, every token truncation/removal/insertion, unsupported version
  5, attempted legacy extensions and late malformed values.
- The existing locale, stream-fault, exception-mask, 16,384/16,385-byte boundary
  and bounded-consumption checks applied to all four grammars. Four rounding
  modes preserve fixed registrations while round-tripping literal binary64
  values, signed zero and subnormals.

The pedal suite retains all 81 position pairs and its 24 expression/rounding
cases, now with independent state4 canonical output. Its migration count grows
from 162 to **243** because version 3 is now a historical reader too, and each
migration destination begins with nonzero fixed modes. Its 134 rejected
documents include a distinct unsupported-version-5 input; the old version-3
grammar's other assertions remain present.

### Focused malformed-state sanitizer check

The new enum indexing and expanded malformed-input cases were also checked with
AddressSanitizer and UndefinedBehaviorSanitizer:

```sh
g++ -std=c++20 -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined \
  -Wall -Wextra -Wpedantic -Werror \
  -Iinclude -Itests -I/tmp/hammond-preset-a13/generated \
  '-DHAMMOND_TEST_PROFILE="unused"' \
  '-DHAMMOND_SOURCE_DIR="/workspace/scratch/a472c29da8b3/Hammond-B3-Organ"' \
  tests/test_control_io.cpp src/ControlStateIO.cpp src/ControlState.cpp \
  src/FixedRegistration.cpp -o /tmp/hammond-preset-a15/test_control_io_sanitized
ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 \
  /tmp/hammond-preset-a15/test_control_io_sanitized
```

Build and run exited **0**. Output was the same 2,240-rejection success line,
with no ASan/UBSan diagnostic. Leak detection was disabled; this is not leak or
real-time allocation qualification. The pedal executable was not separately
sanitized by this worker.

### Fixture preservation and source checks

A Python comparison read the current files and `git show HEAD:<path>`, then
compared the complete literal definitions of `kLegacyCanonical`, `kCanonicalV2`
and `kCanonicalV3` in `test_control_io.cpp`, plus `kManualRecords`, `kPercussion`
and the unchanged `version1`, `version2`, `version3` constructors in
`test_pedal_controls.cpp`. It exited **0** and reported:

```text
Frozen v1/v2/v3 literal fixtures and pedal legacy constructors unchanged from HEAD.
```

`git diff --check` for all owned implementation, test and format-document paths
also exited **0**. The first non-`-Werror` IO compile succeeded with one
`-Wrange-loop-construct` warning in a new test's structured binding; changing
that loop to bind by const reference removed it. No runtime test failed in this
assignment. An initial patch application failed its context check without
changing files and was reapplied with corrected context.

## Tested source identity

The initial repository read identified baseline
`b79086f6bb0c42b97130c721c5c73c7c97a13887`. During the assignment, the integrator
advanced HEAD to `70b335480323329c7f5b207d5f58086c5b854960`; the production changes
tested here were still an uncommitted worktree overlay. These are the actual
source/dependency SHA-256 identities collected after the final focused runs.
The dependency list was checked with compiler `-MM` output; system toolchain
headers are identified by the compiler version rather than individually hashed.

| Path | SHA-256 |
|---|---|
| `include/hammond/ControlStateIO.h` | `7e96c7b27906f7dfe0b9e8337888d5305fc4610f5009301b42cfae563e3ab081` |
| `src/ControlStateIO.cpp` | `3a95b6750fc615b7218da5dd9cb540b30d8a83984374d441f2754c7e66de34fb` |
| `include/hammond/ControlState.h` | `aab82b082f9cf77dadf763148cade9eae04f6f7df68b302b1832f21f78034856` |
| `src/ControlState.cpp` | `9026aa0338b905a005912e4c7734eedd36cbf204ae43fa4631bdc5aadaa86a5d` |
| `include/hammond/FixedRegistration.h` | `4548240ce25f5200442bfe4607ba755feee822a91c8b1a97af9bf7837e3634a0` |
| `src/FixedRegistration.cpp` | `690e45e5738c3c25ae1082e31a49debdfbca994b68d6b0a28ef865df7991769d` |
| `include/hammond/Types.h` | `0abecd960c50186da5348570bfad820cf0f7f3c89c675743eb810b2ebda0dda8` |
| `include/hammond/Percussion.h` | `5eb87fdd2342410b63f7e6ec55ac11c645d2b7185287fb49ff8e5e53095a2722` |
| `include/hammond/PedalVoice.h` | `694961946eac838c689547fc403c84e49a429f3337816ea9ad3a751bf305ddaf` |
| `include/hammond/PedalRouting.h` | `e77c52f1c541ef301fff4c8b0fb9a9449f93be632630326f2d7640694384bea8` |
| `include/hammond/Profile.h` | `b1180b3dc04030e0555ef3eb44a21617fc06e93150a9ecb48ebb05955b3e5fd0` |
| `include/hammond/detail/Decimal.h` | `ae2c63ec61e823fda198a4951e029df11184980c9bc8394142a2d46951338c42` |
| `tests/TestSupport.h` | `8869acab1e7492699b656984c7b24eb6d33f09dad6f989814a8a0c04e3c86be5` |
| `tests/test_control_io.cpp` | `1a310827bb90c492bfa65f1b824563b0214ba39a7191752ad812b2650b54986a` |
| `tests/test_pedal_controls.cpp` | `e31aeddde9fd4b31c205dc9376c7d51d497e44f3da99a8d01da59c4174768055` |
| A13 generated `hammond/generated/FixedRegistrationData.h` | `66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6` |
| `docs/CONTROL_STATE_FORMAT.md` | `3919a828acc343d83e765111f67ac14d06d6ceba3b5407bb6dc4d36a81e3152a` |

## Integration handoff and remaining gates

The state implementation is ready for the integrator's coherent gate. No new
test source target or CMake registration is required: the new assertions run in
the existing `test_control_io` and `test_pedal_controls` executables.

The integrator deliberately deferred full-tree builds while the enlarged
snapshot's publication and host/standalone adapters were incomplete. A15 did
not qualify StateExchange, Session, VST3 streams/controller, native Load/Save,
host automation, thread publication, held-note/history preservation, callback
allocation, platform hosts or devices. Later acceptance must exercise exact
state4 bytes and all legacy readers through those paths, preserving raw fixed
memory while cancelled. Shared status/next steps/log updates and publication
remain with the integrator. Physical latches, loaded gains and measured fidelity
remain outside this software-state gate.
