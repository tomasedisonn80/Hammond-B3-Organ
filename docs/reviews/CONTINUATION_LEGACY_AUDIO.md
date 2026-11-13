# Legacy audio compatibility after the console continuation

Assignment 48 independently compared the published console runtime at
`9a5c99a862daf26a2bab9b05613c98803727a3e7` with a newly built renderer from the
pre-continuation commit `9c8068c95f6843dce95f7f22d729738eef8074f6`.
**All 11 complete WAV and decoded PCM comparisons passed exactly.** The current
defaults also matched explicitly selected ideal contacts and percussion Off in
all 11 cases. This is an observed Linux/GCC compatibility result for the retained
nominal model and the cases below.

The [render contract](../RENDER_FORMAT.md) intentionally changes stdout metadata
to schema 2. After removing its three added fields, every one of the 15 earlier
metric fields was exactly equal to the baseline result for each corresponding
invocation. No audio or production defect was found; no implementation change
was needed for this review.

## Source and executable identity

The baseline was built from a fresh `git archive` of the complete pinned commit.
No live worktree file was overlaid. Its tree is
`a8cd06fb906026617c697c514709222c91eb17e3`; the archive SHA-256 is
`c55a8524ce8ce8769ed7ffe42901e8a48ae8e29035f68565f9b9801e9ef9f5a3`.

The current executable is the integrator's coherent wave-07 Release artifact.
Its source archive was checked against all **296 blobs** in published tree
`a85f1bcb43d2815b6f661172f7ab394ad34bee7e`. The integrator had built the runtime
from tree `1132e9cf242997473b87dd64a8a65086580d594c`; the publication changed only
three Markdown result records. Thus no changing live header or later benchmark
work entered this comparison.

Both builds used GCC 14.2.0 on Linux x86_64, C++20, Release `-O3 -DNDEBUG`, the
repository's strict warnings as errors, and sanitizers Off. Python 3.12.14 drove
the external comparison. These build properties were read from the actual
compiler output, CMake caches and compilation commands.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Fresh `9c8068c` baseline renderer | 106368 | `1253b5bae0ce0c40dd1e30595220810e731e93a9eee9bb3a0fd63eff1ce67229` |
| Current wave-07 renderer | 129456 | `cc0f7a98cdc23694e18c8b53a1241704a876331677688950dea0e7cd6a498efd` |
| Previously retained reference renderer | 106368 | `8e781cb1df6f87443c4b6c88587cfa0e7d2bc8e23d32b5ef0a0bfb84d9ee8be4` |
| Common compiled profile | 4545 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

The earlier [assignment 18 experiment](../development/2026-11-13-continuation/18-renderer-tests.md)
retained the third executable above. The [historical demo replay](../DEMO_REPLAY.md)
also records that binary's equality with a clean `6c3dd8b` build. Its bytes differ
from this freshly built `9c8068c` baseline, so this review does **not** assign the
retained executable to `9c8068c` merely from its filename. Instead, the freshly
archived baseline is the primary comparison, and one extra full four-second
render checks the retained executable independently. That render also matches
the fresh baseline and current output exactly.

The catalog, all five legacy event files and the authoring profile JSON were
byte-compared with `9c8068c` and remain unchanged. The catalog's raw SHA-256 is
`98ffa2c3bc30f60ceb839e1fc2ab978e45dcf5f2cb4970fe77f91894344c34f8`.
The authoring JSON's raw byte hash is
`d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff`.
The compiled profile's separately declared canonical authoring digest remains
`49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`.
These are different hash domains, not interchangeable identities. Independently
generated baseline and current compiled profiles were byte-identical.

## Actual comparisons

Each row was rendered three times: the fresh baseline with common legacy flags,
the current executable with contact/percussion flags omitted, and the current
executable with `--contacts ideal --percussion off --percussion-volume normal
--percussion-decay slow`. All used the same compiled-profile bytes and
`--fail-on-clip`; all returned success, emitted no stderr and reported zero
clipped frames.

| Case | Frames | Rate, Hz | Block frames | Seed | Registration / score |
| --- | ---: | ---: | ---: | ---: | --- |
| Two-manual changes | 192000 | 48000 | 127 | 2601 | `006400000`; `two-manual-changes-v1.events` |
| A4 fundamental | 72000 | 48000 | 127 | 2602 | `008000000`; `a4-fundamental-v1.events` |
| Low coherent foldback | 96000 | 48000 | 127 | 2603 | `800000000`; `low-fold-coherent-v1.events` |
| Held-bank/Cancel | 144000 | 48000 | 127 | 2604 | `008000000`; `held-bank-cancel-v1.events` |
| High coherent foldback | 72000 | 48000 | 127 | 2605 | `000800000`; `high-fold-coherent-v1.events` |
| Held-bank/Cancel, one-sample blocks | 144000 | 48000 | 1 | 2604 | Same held-bank score and registration |
| Held-bank/Cancel, maximum blocks | 144000 | 48000 | 65536 | 2604 | Same held-bank score and registration |
| Default note gesture | 5003 | 44100 | 17 | 0 | `888000000`; MIDI 60 |
| Default note gesture | 5003 | 48000 | 64 | 7 | `888000000`; MIDI 60 |
| Default note gesture | 5003 | 96000 | 257 | 18446744073709551615 | `888000000`; MIDI 60 |
| Musical options omitted | 1031 | default 48000 | default 64 | default 0 | Default registration and note |

The first five cases use exactly their catalog settings. The two extra held-bank
cases exercise the minimum and maximum admitted block sizes and a partial final
block. Their complete WAVs also match the block-127 output independently for all
three renderer selections: **six additional partition comparisons**. The short
gesture cases cover every supported rate, several partitions, seed zero, a
nonzero seed and the maximum unsigned 64-bit seed. The final case omits rate,
block, seed, registration and note flags to exercise actual CLI defaults.

There were **34 renderer invocations**: 33 for the 11 three-way cases and one
retained-reference cross-check. Each main renderer selection produced 880040
frames, or 1760080 interleaved channel samples. The total across all invocations
was 2832120 model frames. Every WAV was independently opened as two-channel,
16-bit PCM at its requested rate/count; its payload length and equal dry channels
were checked. Whole-file and PCM-payload equality were required, without an
amplitude tolerance or reliance on RMS alone.

| Case | Common complete-WAV SHA-256 |
| --- | --- |
| Two-manual changes | `9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd` |
| A4 fundamental | `01f6efe7eb581e702cd59efc19b2df75ab0ddeee945ae7550c8bbfe9ed36e4d3` |
| Low coherent foldback | `564cc10d284a3b5213d39a82569690621c715a3c2c927b57aca4ca25d7e7d33a` |
| Held-bank/Cancel, all three partitions | `5a55f8fa6583a52abae58a9dc048a765082a11b2168b17a1d0f0078ad81cc09e` |
| High coherent foldback | `0becb5e51a8ae9ab3db474de719de000050fae5df68c8020d8dcf29ac1dcbd17` |
| 44100 Hz gesture | `d3122f8e5d8f9591782cd19807054f965905351d69975c1179dbf1302e568207` |
| 48000 Hz gesture | `1baf7c3ee19c2cd30883e0b70a159e5176b281d49afa45bd32115e250e9a739c` |
| 96000 Hz gesture | `de4326acbab47c054c063dd75938e710683467057ea5c0b60664732215ded952` |
| Musical options omitted | `653af6c6ac7d89e5d43e7563386c26908c2504ca11bcb73ce24f081815d68126` |

## Metadata and historical evidence compatibility

The baseline emitted exactly 15 metric fields. Current output emitted exactly
18, with these additions checked explicitly:

| Added field | Expected value |
| --- | --- |
| `render_schema_version` | Integer `2` |
| `contact_model` | `ideal-contacts-v1` |
| `percussion_model` | `shared-readiness-v1` |

Removing only those fields produced a dictionary exactly equal to the corresponding
baseline dictionary in all 11 cases. Current omitted/default and explicit ideal/off
reports were fully equal, including all three new fields. This is intentional
audio compatibility with a documented metadata migration; strict old consumers
must support the new metadata contract explicitly.

The current independent verifier was also invoked on the unchanged retained
[schema-1 demo](../../examples/rendered/nominal-two-manual-v1/README.md).
It returned `verified_retained_bundle`, schema 1, six checked artifacts, 192000
frames at 48000 Hz, and the WAV hash shown above. The manifest remains
`74ad49caa3cc5170870bed1002ea64ffaaf8a202c0614095b31fdcd8308da2ce`.
All seven bundle-file hashes were checked before and after and were unchanged.
The recorded renderer was available and matched its recorded hash. Verification
itself executed no recorded command; the separate renders described above provide
the replay evidence. Its original build-association and authenticity fields remain
unestablished, exactly as reported by the verifier.

## Reproduction and scope

The [assignment note](../development/2026-11-13-continuation/48-legacy-audio-compatibility.md)
retains the actual commands and scratch-record identities. To repeat the comparison,
build the two pinned revisions coherently, use the unchanged catalog inputs and
the parameter table above, and compare the resulting full WAV and decoded PCM
bytes. The five catalog fixtures retain their permanent acceptance tests; no
session-specific executable path was added to production tests.

The scope follows the atlas's phase/replay and partition requirements in
[pp. 103-108 and 385-390](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf).
This review covers the ideal-contact, percussion-Off compatibility path. It does
not require nominal contact travel or enabled percussion to reproduce old audio.
It does not establish exhaustive behavior for every input, universal cross-compiler
or cross-library byte identity, native host/device operation, real-time deadlines,
or measured instrument fidelity. The later wave-eight integration and its hosted
qualification remain the integrator's separate gate.
