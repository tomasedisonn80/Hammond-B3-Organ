# A20 — Persistence integration acceptance

Assignment: **A20, wave 4**, worker `/root/w04_a20_persistence_acceptance`.
Date: **2026-11-14 UTC**. This worker independently audited the shared control
grammar and standalone file transaction, repaired two stale integration tests,
and ran their focused coherent-source acceptance. The
[review](../../reviews/PRESET_PERSISTENCE_REVIEW.md) records the findings and
behavioral coverage.

## Ownership and changes

Owned paths:

- `apps/standalone/tests/test_standalone_state_files.cpp`
- `tests/test_pedal_integration.cpp`
- `docs/reviews/PRESET_PERSISTENCE_REVIEW.md`
- This assignment note.

The state-file test compares actual new saves with independent canonical v4
literals. It retains the original legacy1/2 components, varied v3 constructor and
complete default v3 literal, now exercising all three old readers and explicit
file upgrades. The added focused paths cover cancelled raw fixed memory,
different remembered banks, all four retained arrays, negative zero, mandatory
catalog validation with both modes `none`, invalid cancelled enums and target
preservation during bounded temporary-write failure.

The pedal integration test replaces `old_control_text(current, version)` with an
independent literal legacy1/2/3 constructor. It compares the current writer to a
complete v4 literal and restores both fixed/cancelled and old-format controls
while notes, partial contacts, phases, pedals and percussion history are live.
Its original rate, independent audio, partition and rollback scenarios remain.

No production file was changed. In particular, A20 did not edit `Session`,
`UiModel`, `main.cpp`, `ControlStateIO`, `StateFiles`, other tests, shared status
documents or the assignment manifest. There were no child agents, commits or
pushes. `/workspace/scratch/a472c29da8b3/build-baseline` was not used or modified.

## Source and isolation

Initial inspection saw HEAD `352a398e4f004467c2dab081168be3d8b5206ea9` with the
other owners' uncommitted fixed-registration work. The integrator advanced HEAD
to `35554c068492fe2b20c1f8a602d8354ae762dc42` before the isolated copy. That commit
alone is **not** the tested implementation: the copied worktree overlay is the
source being qualified.

All 1,233 then-present tracked and untracked, nonignored source files were copied
by value to `/tmp/hammond-preset-a20/source`, outside the live repository. The
copy recorded each file's SHA-256 in sorted relative-path order. The complete
final manifest at `/tmp/hammond-preset-a20/source-sha256.txt` has SHA-256:

`2d0de75547d318bf006459d37b473f1ab7d8d05a8be66e7c2947354de9ea03d5`

Immediately after copying, all 63 selected production/header/configuration and
owned-test files still matched the live source. The initial two-target run used
manifest `8df99585f465106d402f368b8e8e0deca7cce7926c1f5d1cded6997200698d6c`.
After that pass, final review amended only the owned pedal test to keep its
original upper-B re-enable continuation alongside the new fixed continuation.
That one file was recopied, the manifest updated, and the affected target rebuilt
and rerun. All 1,233 copied files matched the corresponding recorded manifest
after each run. Both final live owned test files also matched their compiled
copies. The build never links an earlier library to newer live headers.

Key retained source and generated-data identities:

| Path | SHA-256 |
| --- | --- |
| `CMakeLists.txt` | `1e3d06b974697be6ac58fe3d01507878ee59ef4dafe741724c76eac7b666b0f3` |
| `apps/standalone/CMakeLists.txt` | `80f65c37c7feee61ad30346a937ba167abe594d80cf25a48fa83267e612e9c50` |
| `apps/standalone/StateFiles.cpp` | `6cd0d2f26bb2f938781561d278f15f9230e5d84b6052e8554761dc8e96dfd3b6` |
| `apps/standalone/StateFiles.h` | `ccf0aa7cb6d88df7c5e582a6154a12d28d9db97ab97d2833529ba8a328354a67` |
| `src/ControlStateIO.cpp` | `3a95b6750fc615b7218da5dd9cb540b30d8a83984374d441f2754c7e66de34fb` |
| `include/hammond/ControlStateIO.h` | `7e96c7b27906f7dfe0b9e8337888d5305fc4610f5009301b42cfae563e3ab081` |
| `src/ControlState.cpp` | `9026aa0338b905a005912e4c7734eedd36cbf204ae43fa4631bdc5aadaa86a5d` |
| `include/hammond/ControlState.h` | `aab82b082f9cf77dadf763148cade9eae04f6f7df68b302b1832f21f78034856` |
| `src/Engine.cpp` | `ea94f27be2ce6e374537c616bdde34c32c3276df6f7f24e112f52a35d1a4bd3a` |
| `include/hammond/Engine.h` | `da1adc2e635e5acfa3f214447b722122c3a162eb9ec602ba14fa744eb9d39ba6` |
| `src/FixedRegistration.cpp` | `690e45e5738c3c25ae1082e31a49debdfbca994b68d6b0a28ef865df7991769d` |
| `include/hammond/FixedRegistration.h` | `4548240ce25f5200442bfe4607ba755feee822a91c8b1a97af9bf7837e3634a0` |
| `apps/standalone/tests/test_standalone_state_files.cpp` | `e65ea2d7c86fc049cc66c27f8c347f0fe818a12e681a56d75196528b3057e441` |
| `tests/test_pedal_integration.cpp` | `bcecb79226deb7e364ce3fc571e8eb34ae9baa7618cf437263dc3bb69b70f898` |
| `tests/TestSupport.h` | `8869acab1e7492699b656984c7b24eb6d33f09dad6f989814a8a0c04e3c86be5` |
| `data/profiles/nominal-unmeasured-v1.json` (file bytes) | `d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff` |
| `data/registrations/atlas-chapel-nominal-v1.json` | `c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf` |
| `data/references/review-a-pedal.csv` | `b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1` |
| `data/references/review-b-pedal.csv` | `b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1` |
| Generated `hammond/generated/FixedRegistrationData.h` | `66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6` |
| Generated `hammond/generated/PedalRoutingData.h` | `efddce2ea3619a7dd9e153382e307928f7aed60bdb8a0318ca6c0e71ee5f6034` |
| Generated `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

Generated paths are under `/tmp/hammond-preset-a20/build`; source paths above
are relative to its sibling `source` tree. The source-manifest temporary path
is a local reproduction aid; this note retains the important input identities
without treating that temporary tree as a published repository revision.

## Executed commands and outcomes

Working directory:

```text
/workspace/scratch/a472c29da8b3/Hammond-B3-Organ
```

Toolchain: CMake/CTest **4.4.4**, GNU C++ **14.2.0**
(`g++ (Debian 14.2.0-19) 14.2.0`), Python **3.12.14**, Linux. CMake used
`/usr/bin/c++` and its normal strict project flags, including `-Wconversion`,
`-Wsign-conversion`, `-Wshadow` and `-Werror`.

The fresh configure and focused build were:

```sh
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  -S /tmp/hammond-preset-a20/source -B /tmp/hammond-preset-a20/build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_ENABLE_MIDI=OFF

/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  --build /tmp/hammond-preset-a20/build --parallel 4 \
  --target test_standalone_state_files test_pedal_integration

/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/ctest \
  --test-dir /tmp/hammond-preset-a20/build -C Release \
  -R '^(test_standalone_state_files|test_pedal_integration)$' \
  --output-on-failure --no-tests=error -V
```

Configure, build and CTest each exited **0**. The actual CMake generators admitted
the fixed registrations and pedal routes and built the nominal runtime profile.
Both required targets were built before running CTest. The test output was:

```text
Pedal Engine integration: both 200-cell CSV maps; 2203 independent oracle frames; 32600 contact checks; 200837 bitwise source-phase checks; 17676 bitwise partition samples; 10 late-invalid transactions.
Peak absolute bus/voice/audio error: 7.64666108210576567e-15 / 3.40005801291454191e-15 / 1.08423013451923456e-07
TESTED: regular and dangling symbolic-link load/save rejection
TESTED: failed write under RLIMIT_FSIZE and temporary cleanup
NOT TESTED: POSIX failed replacement after a complete temporary write; no deterministic non-racing fixture
Standalone state-file acceptance: 7 scenarios completed; platform exclusions are reported above
100% tests passed out of 2
```

The two-target CTest run reported total real test time **0.11 seconds**. Final
review preserved the original upper-B percussion re-enable/future-audio check
as its own step before the added fixed restore/future-audio check. Only that
owned test source changed after the first pass. Its affected-target rerun was:

```sh
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  --build /tmp/hammond-preset-a20/build --parallel 4 --target test_pedal_integration

/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/ctest \
  --test-dir /tmp/hammond-preset-a20/build -C Release \
  -R '^test_pedal_integration$' --output-on-failure --no-tests=error -V
```

Both commands exited **0**, with **1/1 passed** and the same pedal counts/errors
shown above; CTest reported **0.09 seconds**. These are focused semantic test
durations, not callback-deadline or performance qualification. The unchanged
state-file target and all its dependencies retain the preceding pass.

Additional source checks exited **0**:

- A Python comparison extracted and compared `kManualRecords`, `kPercussion`,
  `kDefaultPercussion`, the old `kDefaultDocument` against the renamed
  `kLegacyDefaultDocument`, and the old `canonical_document` body against
  `legacy_version3_document`, using `git show 352a398...:<path>` as the original.
  The literal version-1/2 compositions and original version-3 bytes are unchanged.
- Literal extraction checked the new fixed-file, default-file and live-history
  documents as exactly 81 tokens, 12 LF lines and a final `end\n`.
- SHA-256 checks verified source-copy stability before/after the build and
  equality of the two compiled test sources with the live owned files.
- `git diff --check` passed for both test files and the two final review notes.

## Failures, limits and next acceptance

Source inspection found the stale current-writer v3 expectations and the
production-writer-derived historical fixture helper described above. No
pre-edit runtime run was made. No compiler diagnostic or runtime failure
occurred in the final focused build/test. No production defect was found in the
audited IO path, so its accepted implementation remains unchanged.

A15's exhaustive mode-pair, migration, enum, malformed-stream, rounding and
sanitizer suites were read as prior evidence and **not rerun by A20**. This
assignment does not add those counts to its own two-target result. No full-tree
CTest, sanitizer, callback-allocation, native window, VST3, Windows/macOS,
physical device or host test was performed here. Compiling standalone support
as a target dependency does not qualify Session/UI runtime behavior.

The retained Windows sharing-lock branch awaits a Windows runner. Failed POSIX
replacement after a complete write remains explicitly untested; bounded Linux
write failure was exercised, without racing a path or adding injection to
production. Crash durability and hostile concurrent filesystem mutation remain
outside these deterministic API tests.

The integrator should include these two targets in its next coherent build and
keep the actual native Save/Load path, queued Session publication and VST3
state streams assigned to their separate acceptance owners. Their tests must
retain cancelled fixed memory, remembered banks, negative zero and literal old
inputs while expecting canonical state4 on explicit new saves. Shared status,
manifest updates and publication remain with the integrator; physical console
latches/loading and instrument fidelity remain separate research gates.
