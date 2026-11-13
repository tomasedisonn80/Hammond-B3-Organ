# Independent legacy identity review — pedal/native wave 7

Assignment 42 compared the current SDK-free runtime and frozen Unicode CLI
integration with session baseline `b4fc61ccfcc59724f14fb0cee947ed7bb7142075`.
The coherent current source starts from published
`d7b886103f8c9d4649ffa1c35930b79808217a3d`, adds assignment 37's reviewed CLI
files/hooks, and adds the parameter-diagnostic scope correction below. Active
installation/native-test and integrator portability repairs were excluded.
No source, profile, routing, registry, fixture, existing bundle or DSP file was
modified by this review. The [assignment note](../development/2026-11-13-pedals/42-legacy-identity.md)
retains exact commands, source overlay, failures and temporary result identities.

## Observed acceptance

| Check | Observed result |
| --- | --- |
| Frozen baseline files | 57/57 byte-identical: PDF, ten original data files, ten original catalog/score inputs, 34 retained rendered-evidence files and both shared-source implementation files |
| Source PDF | 500 pages; 21,248,265 bytes; unchanged SHA-256 below |
| Earlier control records | All 43 complete records equal baseline and immutable version-2 fixture |
| Actual diagnostic compatibility | 215 complete record comparisons across five normalized values; ten actual old/new CLI invocations |
| Actual legacy audio | 8/8 fixture groups; 24 successful renders; 670,800 frames per baseline/current-default/current-explicit00 variant; complete WAV, PCM and retained common metrics exact |
| Historical evidence acceptance | Both genuine schema-1/2 bundles independently verified, with 192,000 and 96,000 frames respectively |
| Focused coherent Release gate | 7/7 suites passed in 3.55 s; 50 Python methods, zero skips; 100 parameter diagnostic calls and 81 Unicode calls |

No production DSP defect was found in this scope. All executions used GCC
14.2.0, CMake 3.31.6 and Python 3.12.14 on Linux. Exact replay is a same-toolchain
software observation, not a claim of cross-platform binary identity, measured
instrument fidelity, native DAW compatibility or audio-device deadlines.

## Preserved inputs and phase ownership

The raw profile bytes, its embedded manual routing, the pedal map, both independent
manual CSVs, both independent pedal CSVs and the factory comparison manifest are
unchanged from the starting revision. Original capture schemas/planned metadata
are unchanged too. The profile's raw file hash below is distinct from its
canonical authoring identity `49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`.
The baseline and current compiled profiles are identical 4,545-byte files with
SHA-256 `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.

| Source | SHA-256 |
| --- | --- |
| `Hammond_B3_Leslie_Research_Atlas_500pp.pdf` | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| `data/profiles/nominal-unmeasured-v1.json` | `d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff` |
| `data/pedal-map.json` | `58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd` |
| `data/references/factory-table-iii.json` | `8c52ccca13653c6e379da33a10197bfc9ac1a1f3ab6bea6bbe8edf81f7a47b52` |
| `data/references/review-a-manual.csv` | `23ade40234db10d0bf99cd5acf9ee0ff29e4656e847e61409ebe8717f7cb9dc6` |
| `data/references/review-b-manual.csv` | `23ade40234db10d0bf99cd5acf9ee0ff29e4656e847e61409ebe8717f7cb9dc6` |
| `data/references/review-a-pedal.csv` | `b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1` |
| `data/references/review-b-pedal.csv` | `b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1` |
| `include/hammond/TonewheelBank.h` | `694acaece901e18b4e089264218d8f217cfe3d2f8ea2a9adfb5ff6773b2f756b` |
| `src/TonewheelBank.cpp` | `ebc26e2e61cc88d5525e390abf3897ebeae38e652c13ea3ef02818b2b3849e0b` |

Fourteen earlier core/header files remain byte-identical, including the shared
source implementation, profile loading, contact model, percussion model, manual
ownership/input and decimal helper. The Engine itself intentionally changed for
pedals. Inspection of its baseline diff confirms one shared source-frame advance
per rendered sample; pedal buses consume that same frame. The old manual and
percussion mixing order is retained, and a zero pedal contribution does not add
an extra floating operation to the old sum. The fresh source-rate, tonewheel and
pedal-source suites exercise that contract separately from retained WAV replay.

The source-rate suite checked 42 transitions, 80 rejections, 15,561 phase/sample
oracle pairs and 61,772 exact future frames. The pedal-source harness checked
3,188,913 phase values, 57 rate changes and twelve partitions, with maximum
coherence error `3.81639164714897561e-16` below fixed tolerance
`1.1368683772161603e-13`. These are nominal source/history tests; factory gear
ratios, pickup waves and physical phase/loading remain separate evidence.

## Permanent parameter identities

The 43 complete earlier registry records retain every field, including their
original proposed evidence/source metadata. Their independently fixed canonical
SHA-256 remains
`5e161206e203cce130330b993590d892182c4ead62daba50b468b5348d70bed2`.
The immutable version-2 fixture also equals the baseline registry byte for byte.
The current inventory remains 45 records, with only the two already approved
pedal mixture IDs appended by the earlier integration.

Actual old/current `hammond_parameter_info` executions at `0`, `0.375`,
`0.49999999999999994`, `0.5` and `1` returned exactly equal complete objects for
all 43 retained parameters: IDs, metadata, defaults and converted event targets.
This supplements the independent Python-registry comparison rather than deriving
expected records from the current C++ table.

### Diagnostic scope correction

The optional native wrapper and HostTimeline now exist, so the offline diagnostic's
old root field `native_host_curves_implemented:false` was a misleading project-wide
statement. Export **schema 2** adds
`verification_scope: "sdk-free-core-parameter-mapping"` and replaces that field
with `native_host_curves_verified:false`. `host_exports_verified` remains false:
this executable does not inspect a plugin binary. Its help explicitly names that
scope and the separate artifact-specific verification.

All 45 per-parameter records and normalized conversion results remain unchanged.
Registry schema 3 and its original authoring provenance are untouched. Exact-root
consumers must explicitly adopt diagnostic schema 2; there is no old-format output
mode. [PARAMETER_BRIDGE](../PARAMETER_BRIDGE.md) documents the migration, and
[PARAMETERS](../PARAMETERS.md) distinguishes the adopted native mapping from
registry provenance and actual module evidence. The focused tests enforce the
new exact root-field shape, false invocation-specific verification claims, absence
of the obsolete implementation field, strict input rejection and preserved
Unicode startup/argument behavior.

## Exact legacy audio replay

The actual baseline executable SHA-256 is
`eee31ffdef6275165fe6b492b34e04c9739e7d6bec6199fbebd16901550a129b`.
The coherent current executable SHA-256 is
`9b80a370078e87b4535b6d4d7fee7ed79f9949c443f1bd0432ed54b21c9e39b6`.
Every score ran once on the baseline and twice on current code: omitted pedal
registration and explicit `--pedal-drawbars 00`. Full WAV and PCM bytes match in
all three variants. All recorded clipping counters remain zero, and common
render metrics match except the already documented render-schema advance.

| Fixture | Frames per variant | Shared full-WAV SHA-256 |
| --- | ---: | --- |
| `two-manual-changes-v1` | 192,000 | `9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd` |
| `a4-fundamental-v1` | 72,000 | `01f6efe7eb581e702cd59efc19b2df75ab0ddeee945ae7550c8bbfe9ed36e4d3` |
| `low-fold-coherent-v1` | 96,000 | `564cc10d284a3b5213d39a82569690621c715a3c2c927b57aca4ca25d7e7d33a` |
| `held-bank-cancel-v1` | 144,000 | `5a55f8fa6583a52abae58a9dc048a765082a11b2168b17a1d0f0078ad81cc09e` |
| `high-fold-coherent-v1` | 72,000 | `0becb5e51a8ae9ab3db474de719de000050fae5df68c8020d8dcf29ac1dcbd17` |
| `console-travel-v1` | 14,400 | `5a198d76abb321d0c94d1559d2ae6a658f2771518743ce3096bbad4a96dc434d` |
| `console-percussion-legato-v1` | 42,000 | `8fed69e2aed6af4979cd74136d34e52b992644930f85cd43c01509dd681663c3` |
| `console-routing-mask-v1` | 38,400 | `9bc4f1dbd09cb5d7879cc4101e0e280c031be505d0f08f6165c115fed66a4f52` |

The retained comparison report also records every PCM digest, exact argv, score,
catalog, executable/profile identity and raw renderer metrics. It contains actual
invocations, not constructed substitute waveforms. Historical schema-1 and schema-2
evidence files were not migrated, regenerated or modified to make verification
pass. Their newer independent verifier accepted their original contracts.

## Handoff

Integrate the frozen diagnostic source/test and two contracts with the complete
seventh-wave source, then run its ordinary and native gates on that exact tree.
Observe hosted results separately. The source hash/legacy replay evidence here
does not qualify concurrent native platform repairs or any changed binary that
has not been executed. Retain stable IDs, the original source/reference inputs,
historical bundles and explicit nominal model identities during later M3/M4 and
product work.
