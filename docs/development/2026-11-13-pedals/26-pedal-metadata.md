# Assignment 26 — compiled pedal model metadata

Owner: /root/w05_a26_pedal_metadata

Wave: 5. Status: complete within the scope below; combined publication and hosted
qualification belong to the integrator.

## Scope and implementation

Extended `hammond_model_info` to schema **2**, appending one `pedal_model` to the
existing report. All previous console/source fields retain their values and
serialized order; only the outer version changes. Parameter diagnostic schema
1, renderer summary schema 3 and musical-state format `B3CONTROLS3` retain their
separate meanings.

The approved schema exports all eight strings from `compiled_pedal_identity()`;
dimensions, bus counts, null records and repeated-source pairs calculated from
the compiled routes; all 200 actual branch weights; and actual compiled voice
IDs, labels, matrix, nine gains, default pedal controls, units and limits.
The descriptive ideal-contact policy does not pretend that the core supplies a
contact-ID getter. `runtime_state_included` is false.

Before returning JSON, the tool prepares the compiled table/weights, validates
default controls and checks matrix/gain/limit finiteness. Its existing classic
locale, full double precision, final LF, Windows binary stdout, strict argument
handling and output-error behavior are preserved. The complete report remains
strictly smaller than 128 KiB. No source-profile, map or CSV file is read by the
runtime exporter.

The source basis was the actual public pedal/control interfaces and Engine
contract, [atlas pp. 139–144](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=139)
and [p. 447](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=447), together
with the adopted [nominal integration contract](../../PEDAL_INTEGRATION_CONTRACT.md).
The fixed transfer is proposed engineering data. Documentary routing agreement
does not change the original map's derived authoring provenance or supply
specimen continuity, reactor values, loading or calibrated pedal color.

## Owned files

- `tools/model_info.cpp`
- `tests/test_model_info.py`
- `tests/test_install.py`, limited to separate model-schema-2 and parameter-schema-1 assertions
- `docs/MODEL_METADATA.md`
- This assignment note

No Engine/core header, runtime DSP, registry, CMake, install file inventory,
shared status, manifest, previous evidence or unrelated worker file was changed.
No commit, push or additional worker was created by this assignment.

## Coherent source and exact executed commands

The isolated source started from published wave-3 commit
`e493b9fed9e3ed8a294fb5d95af447132776cb3a`. A Python subprocess ran `git archive`
for that exact commit and extracted it with `tarfile.extractall(filter="data")`
to `/workspace/scratch/f364bc93d920/a26-metadata/source`.
Only the three owned code/test files and the explicitly frozen assignment-20
`tools/render.cpp` were copied over the archive with `shutil.copy2`.
The native renderer dependency was checked against its agreed SHA-256 before
copying. Live wave-4 ownership/facade files and wave-5 trace/CMake edits were
excluded. Preparation saved all overlay hashes in `source-identity.json`.

Executed build and test commands:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  -S /workspace/scratch/f364bc93d920/a26-metadata/source \
  -B /workspace/scratch/f364bc93d920/a26-metadata/build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  --build /workspace/scratch/f364bc93d920/a26-metadata/build \
  --target hammond_model_info hammond_render hammond_parameter_info hammond_console_trace -j 2
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/a26-metadata/build \
  -R '^python_test_(model_info|install)$' --output-on-failure \
  --output-junit /workspace/scratch/f364bc93d920/a26-metadata/ctest.xml
```

Configure, build and CTest output were retained in `configure.log`, `build.log`
and `ctest.log` under that checkpoint. The project compiled with GCC 14.2.0,
CMake 3.31.6, Python 3.12.14 and the existing warnings-as-errors options.

## Observed results

**2/2 Release CTest suites passed, zero failures or skipped methods, 2.22 seconds.**
The actual model suite ran ten Python methods; the real install/relocation suite
ran one. No build/runtime repair or failed test run occurred in this scope.

The metadata suite independently reads both retained 25-by-8 CSV maps and derives
the counts, null records and repeated-source pairs without using the generated
C++ table or the map's source-selection formula. It hashes the original map,
project-canonical JSON, comparison manifest and both CSVs directly. Independent
rational expectations verify all weights, both mixture rows, nine gains, default
positions, units and the conservative mathematical bounds.

| Observed property | Result |
| --- | --- |
| Connected / disconnected positions | 195 / 5 |
| Repeated connected-source pairs within one pedal | 7 |
| Connections in Brown, Red, Orange, Yellow order | `[45,50,50,50]` |
| Explicit null records | Pedals 8–12, contact index 1, Brown bus, null source |
| Default pedal controls / freshly prepared closed contacts | `[0,0]` / 0 |
| Current metadata bytes | 108,255, below 131,072 |
| Earlier metadata bytes | 105,377 |

An actual audible pedal render using the matching compiled renderer verified its
schema-3 model/map/reference identities and rational transfer description against
the metadata tool. The run had positive peak and zero clipped frames. The
install test moved the complete existing 16-file component to a prefix containing
spaces, ran it from an unrelated directory, and compared installed metadata
bytes with the original executable. The model tool reported schema 2; the
parameter tool continued reporting schema 1 and 45 controls.

A separate Python comparison invoked the preceding wave-3 metadata executable
and the new one. After changing only the old report's outer version from 1 to 2,
all **105,375 bytes of the earlier serialized field prefix** were preserved
before the newly appended pedal object. Every earlier parsed field also compared
equal. This is an observed same-toolchain comparison, not a universal
cross-compiler serialization promise. Repeated/locale-environment checks and
actual read-only stdout-handle failure checks also passed in the retained suite.

## Frozen identities

| Input or output | SHA-256 |
| --- | --- |
| `tools/model_info.cpp` | `b9ecd03c79f1cf5f28b145a444876c072d98a4d0b3dcfaf4d7a70a1f29a66afd` |
| `tests/test_model_info.py` | `abc652b77e9fe3f31df551b6ab8301391bc9a438e456fb60e460948c0e49ce79` |
| `tests/test_install.py` | `61742d7ce45db38c2b171c622a80d80374087da69a01b414094a5a32881d9f64` |
| Frozen renderer dependency | `b8c9f631575ffdd6e198f4811e8add1b301534ca709654aaad1078ec235d08b7` |
| Earlier metadata JSON | `22b4b3d01719aae9bdc258498cd3b743dc9345be91fb074f40892fe6b432f364` |
| Current metadata JSON | `11a28002347425e56898115148f5c2ccb53364a0d6c62903da80ebf42126bfd3` |

All four copied overlays were rehashed after execution and remained byte-identical
to their live frozen files. The scoped code/test/doc whitespace, UTF-8, LF,
owner-identity and local-link checks passed.

## Next step and limits

Root can integrate these files with the other frozen wave-5 scopes and run the
complete exact-tree regression before publication. Later package work can add the
pedal trace/catalog without conflating those install changes with this schema
update. Use [MODEL_METADATA.md](../../MODEL_METADATA.md) for the public contract.

This result qualifies the named local offline exports, actual matching renderer
summary and existing install component. It does not measure an instrument,
inspect arbitrary custom pedal weights or active Engine history, establish
callback allocation/deadline behavior, run a native host, or close physical M3
or product M9 gates. Those require their own retained evidence.
