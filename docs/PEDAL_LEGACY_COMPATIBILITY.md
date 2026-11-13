# Pedal extension: exact legacy rendering compatibility

Assignment 23 compared the new renderer against the frozen pre-pedal baseline
`b4fc61ccfcc59724f14fb0cee947ed7bb7142075`. **All eight retained catalog scores
produced identical WAV bytes and identical PCM bytes** in three executed cases:
the baseline, the new renderer with its default muted pedal controls, and the
new renderer with explicit `--pedal-drawbars 00`. Every retained renderer metric
also matched, except the intentionally advanced metadata version.

This is an executed same-toolchain software comparison. It covers the stated
scores and controls; it does not promise cross-compiler/libm byte identity,
measured instrument fidelity, realtime deadlines or native-host behavior.

## Exact scope and identities

The candidate uses published wave-3 core commit
`e493b9fed9e3ed8a294fb5d95af447132776cb3a` plus the frozen renderer/evidence files
listed in [assignment 23](development/2026-11-13-pedals/23-render-compatibility.md).
All native source, headers and consumers were built from one coherent copied
source tree. No later live ownership or automation changes were linked into it.
Both executables were built as Linux GCC 14.2.0 Release with CMake 3.31.6.
The Python checks used Python 3.12.14.

| Input | SHA-256 |
| --- | --- |
| Baseline executable, 129,456 bytes | `eee31ffdef6275165fe6b492b34e04c9739e7d6bec6199fbebd16901550a129b` |
| Candidate executable, 135,320 bytes | `42e4373f6ea80eb0c87238b009283b729e89d71858fc73085831069e84f79d59` |
| Both compiled profiles, 4,545 bytes | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Original five-score catalog | `98ffa2c3bc30f60ceb839e1fc2ab978e45dcf5f2cb4970fe77f91894344c34f8` |
| Console three-score catalog | `f66d31d43e67b52fb2044a680c9c6ca6f02608bd94eac1988ed56edc1f28a27b` |
| Replay helper | `a1d97629bd543af692ba56276b2cfb2c6e2b6d49603a111e093942035fb339be` |

The two catalogs and all eight score files were independently compared with
`git show b4fc61c:PATH` and remain byte-identical. The helper verifies each score
against its retained catalog hash. It rechecks all executable, profile, catalog
and score bytes after replay, rejecting an observed input change.

Every score uses its catalog's **48,000 Hz** rate and **127-frame** block size.
Registrations, seeds, event files and console choices are read from the retained
catalogs without changing them:

| Fixture | Frames per variant | Seed | Initial upper registration |
| --- | ---: | ---: | --- |
| `two-manual-changes-v1` | 192,000 | 2601 | `006400000` |
| `a4-fundamental-v1` | 72,000 | 2602 | `008000000` |
| `low-fold-coherent-v1` | 96,000 | 2603 | `800000000` |
| `held-bank-cancel-v1` | 144,000 | 2604 | `008000000` |
| `high-fold-coherent-v1` | 72,000 | 2605 | `000800000` |
| `console-travel-v1` | 14,400 | 2623 | `008000000` |
| `console-percussion-legato-v1` | 42,000 | 2624 | `000000000` |
| `console-routing-mask-v1` | 38,400 | 2625 | `000000008` |

The first five use ideal manual contacts with percussion Off/Normal/Slow. The
three console fixtures use their explicit nominal contact and percussion choices.
Each invocation requires zero clipped frames with `--fail-on-clip`. There were
**24 renderer executions**, comprising 670,800 frames per variant and 2,012,400
rendered mono frames in total. Both stored dry channels are part of the exact
WAV/PCM comparison. No tolerance, rescaling or sample trimming was used.

## Reproduce the comparison

Build the baseline and candidate in separate coherent checkouts or archives.
Keep the baseline checkout at the exact commit above; use the documented project
Release build for each. Do not pair an old library with newer headers. Then run
from the candidate repository, supplying the actual executable/profile paths:

```sh
cmake -E make_directory out
python3 tools/compare_legacy_renders.py \
  --baseline-renderer /path/to/baseline/build/hammond_render \
  --baseline-profile /path/to/baseline/build/nominal.b3p \
  --current-renderer /path/to/candidate/build/hammond_render \
  --current-profile /path/to/candidate/build/nominal.b3p \
  --output-dir out/pedal-legacy-replay
```

The helper accepts trusted, already-built project executables. It does not fetch,
compile or authenticate an executable's source association. Its default catalogs
are the two retained repository catalogs. Inputs have fixed size/type bounds;
execution is limited to 30 seconds per invocation; each stdout/stderr stream is
drained concurrently and retained only up to 16 KiB, with overflow rejected.
WAV reads are bounded by the catalogs' 192,000-frame maximum. Existing result
directories, including symlink destinations, are rejected before executing a
renderer. The new directory contains 24 WAVs, 24 exact stdout records and one
`comparison.json` with invocation arguments, input identities, actual metrics,
and WAV/PCM hashes. A failure may leave diagnostic outputs in that newly created
directory; it never upgrades a partial result to successful comparison evidence.

Observed successful stdout:

```json
{"status": "byte_identical", "fixture_count": 8, "render_invocations": 24}
```

A separate existing-directory check preserved all 49 completed replay files.
A mismatched-profile check rejected before directory creation. Both stdout and
stderr overflow checks rejected at 16,385 bytes while keeping retained buffers
bounded. Those checks concern this helper, not the audio callback.

## Retained output hashes

These hashes identify the observed local outputs, which were equal in all three
variants. They are not universal golden hashes for other toolchains.

| Fixture | Complete WAV SHA-256 | PCM payload SHA-256 |
| --- | --- | --- |
| `two-manual-changes-v1` | `9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd` | `1c2216be3fced52b677be9e09393d0edccf98292529668019f88495a7c88600f` |
| `a4-fundamental-v1` | `01f6efe7eb581e702cd59efc19b2df75ab0ddeee945ae7550c8bbfe9ed36e4d3` | `857172f9eca01ea3a7ccc308f1610eb58122129fbe947bf4c7fba71ade2516ce` |
| `low-fold-coherent-v1` | `564cc10d284a3b5213d39a82569690621c715a3c2c927b57aca4ca25d7e7d33a` | `3823dce9e87ad5e821ec2750548593966da011dc2ff5a3fa73bfc0a0ad288f99` |
| `held-bank-cancel-v1` | `5a55f8fa6583a52abae58a9dc048a765082a11b2168b17a1d0f0078ad81cc09e` | `3de836c123116802f60a2d507739a711bab67b7d76d9c6f755e1abca0606acdc` |
| `high-fold-coherent-v1` | `0becb5e51a8ae9ab3db474de719de000050fae5df68c8020d8dcf29ac1dcbd17` | `e7d1554480d6a181b8f7119d109da055f5a4fdb0c7fc2d8fd95f619f2f37f84b` |
| `console-travel-v1` | `5a198d76abb321d0c94d1559d2ae6a658f2771518743ce3096bbad4a96dc434d` | `a91444093253f80b43949e676f7d3f8fa9aafece397570e378532b0924aa3e68` |
| `console-percussion-legato-v1` | `8fed69e2aed6af4979cd74136d34e52b992644930f85cd43c01509dd681663c3` | `fbca0074aeb4658c1a16792c3d1963c9def5233cc190772d5e577383124649fd` |
| `console-routing-mask-v1` | `9bc4f1dbd09cb5d7879cc4101e0e280c031be505d0f08f6165c115fed66a4f52` | `f348f261e0d11f228b7be46fde9ee100e96487d9632e6bd8f033bf2b58f71ecd` |

## Evidence format migration

Current renderer and producer expectations now use [schema 3](PEDAL_RENDER_EVIDENCE.md):
14 parameter fields, 31 renderer fields and 28 invocation tokens. Historical
schema 1 remains at its original grammar; schema 2 retains its console grammar,
13 parameter fields, 18 renderer fields and 26 tokens. Historical parsing never
silently gains pedal controls or commands.

The six existing renderer/partial-key/catalog/producer/consumer/console suites
passed **6/6 CTest suites and 112 Python methods, zero failures and zero skips**,
in 15.79 seconds. The consumer suite preserves explicit schema-1 fixtures and
adds separate constructed schema-2 note, event and nominal-console fixtures;
model, field and invalid-percussion rejection checks run against both schema 2
and current schema 3. Constructed parser fixtures rewrite metadata deliberately
and make no claim of historical executable execution. The separate baseline
replay above supplies that runtime evidence. Genuine retained historical bundles
remain unchanged and are also covered by the pedal-evidence assignment.

The first migration run passed four of six suites and exposed two remaining
fixture assumptions: an exact default-parameters dictionary omitted the new
muted pedal field, and a descriptor-timestamp test used a 1 KiB read limit for a
larger current summary. Both were repaired to the documented current contract;
no core, renderer, producer or verifier repair was required. All earlier audio,
publication, malformed-input, independent PCM and historical grammar assertions
remain active.

The next gate is root's full coherent wave-4 regression and hosted matrix,
including independent ownership/clock acceptance. Later runtime changes should
rerun this exact comparison with their actual candidate executable. The complete
M3 console, physical calibration and product-host gates remain separate.
