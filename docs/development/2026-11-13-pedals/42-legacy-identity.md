# Assignment 42 — legacy identity and diagnostic scope

Owner: `/root/w07_a42_legacy_identity`.

Assignment **42/60**, wave **7**. Owned only the parameter-info source, its Python
bridge test, PARAMETERS/PARAMETER_BRIDGE contracts, the independent review and
this note. No shared CMake, core, native production, profile, registry, map,
fixture, historical bundle, shared status or manifest was changed. No staging,
commit, push or subagent dispatch was performed by this worker.

## Source basis and adopted decision

Read AGENTS, README, current status/next steps/latest development log, historical
continuation handoff, PLAN/atlas review and relevant earlier compatibility notes.
Reread atlas pp. 397–402 from the retained full extraction: permanent identities,
normalized laws, gesture boundaries, native curves, versioned state and evidence
separation. This is a targeted reread; wave 1 owns complete fresh PDF coverage.
Independent `pdfinfo` and byte comparison confirm 500 pages, 21,248,265 bytes and
unchanged source SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

Parent approved diagnostic schema 2 after the concrete obsolete-claim review.
The old `native_host_curves_implemented:false` implied a project-wide absence
which is no longer true. The replacement `native_host_curves_verified:false`
plus `verification_scope: sdk-free-core-parameter-mapping` states this offline
command's real scope. `host_exports_verified:false` remains; no native module is
loaded. Help and docs point to separate artifact-specific native evidence.
The registry's original authoring provenance, all 45 records, CLI numeric grammar
and Unicode wrapper remain intact. Exact-root consumers must adopt the documented
schema-1 → schema-2 export migration. Registry/render/state versions do not change.

## Coherent source and the initial overlay failure

Created `/workspace/scratch/f364bc93d920/a42-source` from a `git archive` of
`d7b886103f8c9d4649ffa1c35930b79808217a3d`. Added only assignment 37's frozen
`CliArguments.h`, six CLI files, Unicode test and three root-CMake CLI hooks,
plus this assignment's diagnostic source/test/contracts. The source manifest
records all **476 files**, including exact bytes/hashes and overlay provenance.
No live library/header mixture was used.

The initial automatic application of assignment 37's original CMake patch failed:
its context expected BUILD_TESTING directly after pedal_trace, while W6 inserted
the optional native block there. No build/test ran from that incomplete overlay;
one base-archive configuration had succeeded. Reconstructed the private CMake
from the pinned base with the same three reviewed CLI-only edits reconciled
around the native block, completed the source overlay, then reconfigured before
compiling. This local preparation failure is retained in
`a42-snapshot-attempt1.log`; no shared CMake or production fix was necessary.
Concurrent installation/native acceptance files and root's platform portability
repairs were excluded. The native feature remains OFF in this scoped build.

## Commands and actual results

Actual CMake/CTest directory:
`/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/`.
GCC 14.2.0, CMake 3.31.6, Python 3.12.14; Linux Release.

```sh
cmake -S /workspace/scratch/f364bc93d920/a42-source \
  -B /workspace/scratch/f364bc93d920/a42-build -DCMAKE_BUILD_TYPE=Release
cmake --build /workspace/scratch/f364bc93d920/a42-build \
  --target hammond_render hammond_parameter_info hammond_benchmark \
  hammond_model_info hammond_console_trace hammond_pedal_trace \
  test_parameter_bridge test_source_rate test_tonewheel test_pedal_sources -j2
ctest --test-dir /workspace/scratch/f364bc93d920/a42-build \
  -R '^(test_parameter_bridge|test_source_rate|test_tonewheel|test_pedal_sources|python_test_parameter_bridge|python_test_parameters|python_test_cli_unicode)$' \
  --output-on-failure --output-junit /workspace/scratch/f364bc93d920/a42-ctest.xml \
  --output-log /workspace/scratch/f364bc93d920/a42-ctest.log
```

The first complete execution passed **7/7 suites in 3.55 seconds**, zero failures
and zero skips. Python methods: Unicode 11, bridge 11, registry 28 — **50 total**.
The bridge made **100 actual CLI calls**, and the Unicode suite made **81** across
all six tools. The core bridge checked 5,933 independent conversions, 33,461
atomic rejections and all 45 live targets under all four rounding modes.
Source-rate/tonewheel/pedal-source checks passed with the counters and bounds
retained in the [review](../../reviews/PEDAL_LEGACY_FINAL.md). No code or test
repair followed that complete gate.

```sh
python3 /workspace/scratch/f364bc93d920/a42-source/tools/compare_legacy_renders.py \
  --baseline-renderer /workspace/scratch/f364bc93d920/baseline/build/hammond_render \
  --baseline-profile /workspace/scratch/f364bc93d920/baseline/build/nominal.b3p \
  --current-renderer /workspace/scratch/f364bc93d920/a42-build/hammond_render \
  --current-profile /workspace/scratch/f364bc93d920/a42-build/nominal.b3p \
  --output-dir /workspace/scratch/f364bc93d920/a42-legacy-replay
python3 /workspace/scratch/f364bc93d920/a42-source/tools/verify_render.py \
  /workspace/scratch/f364bc93d920/a42-source/examples/rendered/nominal-two-manual-v1/bundle
python3 /workspace/scratch/f364bc93d920/a42-source/tools/verify_render.py \
  /workspace/scratch/f364bc93d920/a42-source/examples/rendered/nominal-console-v2/bundle
```

Observed **8/8 byte-identical groups, 24 successful renders**, 670,800 frames per
variant (baseline/current-default/current-explicit00). Both compiled profiles
are byte-identical. Full WAV, PCM and all retained common metrics match except
the documented render-schema advance. Both original retained bundles verify
under their own schema 1/2 contracts, with 192,000/96,000 frames respectively.
The review records all eight WAV identities and current/baseline executable IDs.

Separately compared 57 baseline files with exact `git show b4fc61c:<path>` bytes:
PDF; ten original data files; ten original catalog/score inputs; all 34 retained
rendered-evidence files; shared-source header/cpp. Fourteen earlier core/header
files are unchanged in total. The old 43 complete parameter records match both
baseline JSON and the immutable version-2 fixture with fixed canonical digest
`5e161206e203cce130330b993590d892182c4ead62daba50b468b5348d70bed2`.
Ten actual old/new parameter-info invocations at five values compared **215
complete retained record objects**, all equal.

## Frozen files

The four implementation/test/contract files match the tested archive byte for
byte. The review and note add only observed results after testing.

| File | SHA-256 |
| --- | --- |
| `tools/parameter_info.cpp` | `4a8fd0fd0e55f882bd8b94519ed57798ce307100b5215df96964f52d2b885ce6` |
| `tests/test_parameter_bridge.py` | `01f10762079ddc9c8812850f816bb991f51eb43b59431250692368414f07caa7` |
| `docs/PARAMETERS.md` | `1334a8b720d1a3d1de531d3bce61b508a737561552b8f43fcc59a19a47ecf3b2` |
| `docs/PARAMETER_BRIDGE.md` | `196f9b9e718232549f0aaf0f3bc6f79f4aaa2dca2834131c7559ec37f6d96a07` |
| `docs/reviews/PEDAL_LEGACY_FINAL.md` | `fb400782ca35c927490497fbe64daa0105cd147c3eee1cc62638b87f6a158b6b` |

Current renderer SHA-256:
`9b80a370078e87b4535b6d4d7fee7ed79f9949c443f1bd0432ed54b21c9e39b6`.
Current parameter-info SHA-256:
`e66ebd2334836874f045d1a92fd456796b1e74bc495804220abfd8f3c7ed0e23`.
Compiled profile SHA-256:
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.

| Temporary evidence | SHA-256 |
| --- | --- |
| `a42-source-identities.json` | `f252333abfc019e31c85778b34f3eccdcaab3d2bb8f6e242ed6c2414a1a3d508` |
| `a42-ctest.log` | `a3be3dcda7de5c099b0f5ef567f80dabce35e77d67d2ee304b51373f41ae363c` |
| `a42-ctest.xml` | `246bdbe0170c9f6b5e05535b314d48b95c3243e52b497284bac6552cd67c793c` |
| `a42-immutable-audit.json` | `605488e20ab40b81c35d974767b6d0d5bc0361e4dbb01beda18695d2545d0cea` |
| `a42-legacy-replay/comparison.json` | `121f77476c9be1787800791e7888d8c01d11e13be671c5eb7668fe585598cc0a` |
| `a42-retained-bundle-verification.json` | `25d873d78b8817a02407993934c60a9b7ab381827fb005671a41b5ccfa0563e0` |
| `a42-compiled-legacy-parameter-replay.json` | `ccb70e5b8ab9a0da11fb95e15a0800593400f29e0fcdb3da18ab2c6f577b6803` |

These local result files are temporary diagnostics, not asserted durable hosted
artifacts. Exact commands, named source/inputs and essential results are retained
here so another agent can reproduce the gate. Final owned-file whitespace,
UTF-8/LF, Python syntax and local Markdown-link checks passed.

## Integration and remaining limits

Root should include the frozen diagnostic/test/contracts and review in the
combined seventh-wave gate, then publish and observe its exact hosted outcomes.
No root CMake change is requested; test discovery already covers the updated
Python suite. Schema-2 diagnostic adoption is the only intended consumer change.
The retained old musical outputs and per-parameter records do not change.

This scoped Linux SDK-free gate does not execute a DAW, instrument a loaded native
module, qualify Windows/macOS runtime behavior or establish physical calibration.
Root's concurrent native portability work has separate execution and publication
evidence. Continue with the combined source gate, retained musical pedal demo,
operational handoff and actual platform qualification; do not inherit a later
binary's pass from these earlier hashes.
