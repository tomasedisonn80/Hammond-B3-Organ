# Assignment 23 — renderer/evidence compatibility and exact legacy replay

Owner: /root/w04_a23_render_compatibility

## Scope and ownership

Updated only the six assigned existing test files, added the optional bounded
`tools/compare_legacy_renders.py` helper, this note and
[the compatibility report](../../PEDAL_LEGACY_COMPATIBILITY.md).
No core, renderer, producer/verifier, fixture/catalog, CMake, shared status,
manifest or other worker file was modified. Root owns integration and publication;
this assignment made no commit or push and dispatched no additional workers.

Read the standing instructions/current entry points, project milestones and
atlas review, the new renderer/pedal contracts and the precise schema-3 evidence
contract. Coordinated the source freeze directly with assignments 20 and 21.
The acceptance target was exact legacy audio plus explicit old/current evidence
version behavior, without substituting synthetic PCM for measured instrument data.

## Coherent tested source

Base commit: `e493b9fed9e3ed8a294fb5d95af447132776cb3a`.
Created `/workspace/scratch/f364bc93d920/a23-source` from its `git archive`, then
copied only the following frozen files. The native build uses that same source
and its headers throughout. Final live hashes still equal the tested copies.

| Overlay | SHA-256 |
| --- | --- |
| `tools/render.cpp` | `b8c9f631575ffdd6e198f4811e8add1b301534ca709654aaad1078ec235d08b7` |
| `tools/render_fixture.py` | `f8da8a3a5633eb4d28e32a9e607ff579f188c520a89ae84dbc0c03684ccadcb1` |
| `tools/verify_render.py` | `0f212fd56423de617953be200bdfeacfeb807a3b6e280c8f0576242d79fd0539` |
| `tests/test_render.py` | `af8026874bd2e673d92bd2d3516715ac9a5eed104220aae056e513e4db621a28` |
| `tests/test_partial_key_render.py` | `aa12ba418d549979b437ab1358caafec23c0cbe827da23f3e96ed3a881af49a4` |
| `tests/test_console_catalog.py` | `1c66d48815e598c2941797dc83cb339a84d03c91dff0780695ec0ab45477ce24` |
| `tests/test_render_fixture.py` | `6edb0c3bfa2c205a72b22c9ff10c0e03777034863abe01532d8ad3f719c7cb45` |
| `tests/test_verify_render.py` | `a05abc2d995b74a858d324114b372f5d198b6534feeae5ff8ebd264406f854b5` |
| `tests/test_console_evidence.py` | `c587aa1b831689aaf62113360352379d3697d96b38c3bcfa74d3c7ab9b731366` |

The independently executed replay helper SHA-256 is
`a1d97629bd543af692ba56276b2cfb2c6e2b6d49603a111e093942035fb339be`. Its CLI does not enter core DSP or
introduce a build dependency. It takes explicit trusted executables/profiles,
admits fixed catalog and input bounds, drains bounded logs, imposes per-process
timeouts, rejects an existing output directory, and retains exact comparison
results only after all eight cases pass.

## Commands and actual results

```sh
cmake -S /workspace/scratch/f364bc93d920/a23-source \
  -B /workspace/scratch/f364bc93d920/build-a23 -DCMAKE_BUILD_TYPE=Release
cmake --build /workspace/scratch/f364bc93d920/build-a23 \
  --target hammond_render -j 4
ctest --test-dir /workspace/scratch/f364bc93d920/build-a23 \
  --output-on-failure \
  -R '^python_test_(render|partial_key_render|console_catalog|render_fixture|verify_render|console_evidence)$'
```

The actual CMake/CTest executable directory was
`/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/` (3.31.6). Compiler GCC
14.2.0; Python 3.12.14; Linux Release. First run: **4/6 passed**, with only the
omitted default `pedal_drawbars` dictionary entry and the timestamp-reader's old
1 KiB test limit failing. Repaired those two test assumptions; did not edit
production or relax audio tolerances. Final run: **6/6 passed, zero failures,
15.79 seconds**. The complete `LastTest.log` records **112 methods**:
console catalog4, console evidence3, partial key7, renderer35, producer28 and
verifier35. Zero methods were skipped. Initial and final logs/XML remain in task
scratch; final source hashes are retained above.

```sh
python3 tools/compare_legacy_renders.py \
  --baseline-renderer /workspace/scratch/f364bc93d920/baseline/build/hammond_render \
  --baseline-profile /workspace/scratch/f364bc93d920/baseline/build/nominal.b3p \
  --current-renderer /workspace/scratch/f364bc93d920/build-a23/hammond_render \
  --current-profile /workspace/scratch/f364bc93d920/build-a23/nominal.b3p \
  --output-dir /workspace/scratch/f364bc93d920/a23-legacy-replay-final
```

Result: **8/8 fixture groups byte-identical, 24 successful renderer invocations**,
670,800 frames per variant. Baseline/current-default/current-explicit00 agree in
complete WAV bytes, PCM bytes and all retained common metrics except the declared
schema advance. The two compiled profile inputs are identical. The report above
retains executable, catalog and all eight output identities. Every catalog/score
was also byte-compared with baseline `b4fc61c` via `git show`.

The final temporary `comparison.json` SHA-256 is `2cf9ab3691170ed216b2c7cf3cc0435193acb329d7c5fbfdca7f5aa7befa4cf0`.
The helper was additionally exercised against an existing result directory,
mismatched profile, and each oversized stdout/stderr stream. All four rejected;
the existing-directory case preserved all 49 artifacts, and the wrong-profile
case created no output directory. The helper's final replay also rechecked all
executables, profiles, catalogs and scores after execution.

## Preserved evidence and next step

Schema3 expectations are explicit; schema1/2 fixtures stay under their own
field/argv/event contracts. Constructed old parser fixtures are labelled as such;
actual old-executable comparison is a separate gate. Metadata mutation tests
retain invalid values after the version change and continue testing every
existing contract. Source/model identities and profile/fixture bytes are unchanged.

This result qualifies the stated local software cases only. It does not claim
cross-toolchain WAV identity, audible physical pedal calibration, realtime
performance, a plugin/DAW test or complete M3. Root should integrate these frozen
files with wave4 ownership/evidence work, run the full coherent suite and observe
the exact published commit's hosted qualification. Future changed runtimes can
rerun the retained helper against the same baseline.
