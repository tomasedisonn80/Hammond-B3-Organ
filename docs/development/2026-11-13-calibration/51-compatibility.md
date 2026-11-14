# Assignment 51 — compatibility, source rights and original bytes

## Actual assignment and outcome

- Actual agent: `/root/cal_w9_a51`.
- Assignment: **51**, logical wave **9**, executed 2026-11-14 UTC.
- Owned files: this note and `docs/reviews/CALIBRATION_COMPATIBILITY_AUDIT.md`.
- Result: **18/18 finite audit cases passed**, with 158 frozen source/data file
  identities checked and rechecked. These are audit cases, not new maintained
  test methods or a fresh native product qualification.
- Production code, shared documents, repository Git state and original sample/PDF
  bytes were not modified by this assignment. A separate disposable Git repository
  was used for the authorized raw-byte filter experiment and removed afterward.
- One concrete central dependency-inventory gap was reported. Root subsequently
  corrected that shared document; the response is identified separately below.

The [concise review](../../reviews/CALIBRATION_COMPATIBILITY_AUDIT.md) develops
what the observations establish and what they do not. Root owns shared status,
assignment acceptance, the coherent build gate and commit/push publication.

## Instructions and frozen source boundary

Read the repository standing instructions, plan, current calibration scope and
handoff, active standalone/rotary scopes and scanner handoff, source consolidation,
control-state contract and dependency inventory before auditing. The relevant
atlas extracts were pages 355, 449 and 484. This agent did not perform a second
complete 500-page reading; the session's six original readers and
[consolidation](../../research/CALIBRATION_ATLAS_REVIEW.md) retain that evidence.

| Boundary | Identity |
| --- | --- |
| Session baseline | `38c1fac949368fa54bd86c6c00a5997a73480f5e` |
| Accepted assignments 1–48 frozen commit | `48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a` |
| Frozen tree | `3edea0838b75feb06c19e151ec8539e80646fc03` |
| Already published concurrent-work comparison | `3b0979bd0d30ce96bca0bcd57bd8f730eaadd1bf` |
| Repository used for read-only Git queries | `/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ` |
| Immutable extracted source used for byte checks | `/workspace/scratch/c9f3ead4c910/w8-combined-source` |

The accepted source includes the final CLI guards, raw binary-marker regression
fixture and `*.f32 binary` repair. Later review/status documentation is outside
this source freeze. Source comparison uses `git ls-tree -r -z`, `git show` and
`git rev-parse`; the real archive bytes are independently compared with their
Git objects. No remote fetch, merge or publication was attempted by this agent.

## Executed command, environment and retained failure

Working directory was `/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.
Prerequisites were Python 3.12.14, Git, the three locally available commits above,
and the immutable source archive. The audit uses only Python standard modules.

```sh
python3 -B /workspace/scratch/c9f3ead4c910/a51-compatibility-audit.py
```

The final command exited successfully with all eighteen cases passed. Observed
runtime was `3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]`,
`Linux-6.18.57-x86_64-with-glibc2.41`, and `git version 2.52.0`.
No native binary was built or executed by this assignment. Root's separate
full coherent suite was still running when the source freeze was supplied; its
result is not attributed to this audit.

The first scratch-harness attempt exited 1 before completing the audit because
it requested nonexistent `cmake/VerifySDL2.cmake`. Git reported:

```text
fatal: path 'cmake/VerifySDL2.cmake' does not exist in '48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a'
```

The actual tracked path is `cmake/VerifySdl2.cmake`. Only that path spelling was
corrected; no production change, expected-result relaxation or scope reduction
was made. The complete corrected scope then passed. The initial harness was
15,479 bytes, SHA-256
`fd69c7351c73b168c98c8382a21a489149f4c02c49555a98a28af8db6720c806`.
Its exact bytes can be reconstructed from the retained final script by replacing
its single `cmake/VerifySdl2.cmake` occurrence with `cmake/VerifySDL2.cmake`.

| Retained execution identity | Bytes | SHA-256 |
| --- | ---: | --- |
| Exact successful script, embedded below | 15479 | `7dee332b832acb73717290add6ff5debe3b5b56c58c7380f4ea390fb9be3930b` |
| Original scratch result `a51-compatibility-result.json` | 94848 | `4260553c098347b007ccf548d6ea75ccc164daecc41e3048e82089a10e60c94c` |
| Canonical 158-file identity inventory in that result | — | `912c559e14bf2d140055ae51c4b28557d823073926355b4548fc28b60f161089` |

The JSON uses sorted keys, two-space indentation, UTF-8 and a final LF. Its
runtime field describes this execution, so an execution on another host need
not reproduce the whole result-file hash. The immutable source identities and
case expectations remain explicit. The executable embedded below reproduces
all path inventories and observations; the selected identities and full case
ledger are retained in this note rather than depending on scratch longevity.

## Complete finite case ledger

| # | Audit case | Result and observation |
| ---: | --- | --- |
| 1 | `frozen_tree_identity` | Pass. Exact frozen commit resolves to the expected tree. |
| 2 | `core_headers_and_implementations` | Pass. 42 files: all core headers and implementations match baseline mode/type/blob and archive bytes. |
| 3 | `native_vst3_code_and_tests` | Pass. 19 files: native VST3 source, identifiers, build rules and maintained tests match baseline. |
| 4 | `model_routing_registry_and_dependency_data` | Pass. 17 pre-existing data files excluding the explicitly reviewed capture schema match baseline. |
| 5 | `state_contract_and_legacy_render_inputs` | Pass. 57 files: state contract, legacy fixtures/render bundles, selected render/build tools and OfflineTools helper match baseline. |
| 6 | `optional_dependency_locks_workflows_fonts` | Pass. 12 workflow/font/configuration/dependency-verifier files match baseline. |
| 7 | `public_parameter_id_order_and_all_records` | Pass. 45 ordered unique parameter IDs; entire registry including all metadata and schema version 3 equals baseline. |
| 8 | `public_plugin_identifiers` | Pass. Both source UUID declarations equal the literal expected four-word sequences. |
| 9 | `supplied_pdf_original_bytes` | Pass. 21,248,265 original PDF bytes and SHA-256 equal baseline and frozen archive. |
| 10 | `v1_runtime_body_preservation_and_schema_scope` | Pass. All 27 original top-level definitions retained; only added definition is _cli_exit. Four reviewed schema definitions changed; outer schema unchanged. |
| 11 | `ten_runtime_module_static_import_closure` | Pass. 98 import observations across ten runtime modules: standard library or explicit project module; no external import found. |
| 12 | `two_independent_script_static_closures` | Pass. Generator and v1 validator each have only standard-library static imports; separate execution belongs to other assignments. |
| 13 | `capture_package_inventory_and_no_new_download` | Pass. 57 declared files: 10 modules, 8 data, 21 documents, 16 demo, README and notices; no inspected download operation or native/PDF asset. |
| 14 | `original_synthetic_demo_bytes` | Pass. All 16 demo files equal published source and total 32,831 bytes; three raw arrays decode exactly to independently stated literals. |
| 15 | `concurrent_standalone_work_preserved` | Pass. 74 standalone-related paths equal published 3b0979b; 53 differ from the original session baseline, so whole-repository preservation is not claimed. |
| 16 | `rights_and_material_inventory_boundaries` | Pass. No root project license file; current notices equal published source. Frozen central inventory omission observed; existing rights decisions retained. |
| 17 | `independent_git_raw_byte_before_after` | Pass. 12 private-Git observations reproduce two corruptible CRLF-containing floats, preserve all raw specimens under binary rules and preserve JSON LF normalization. |
| 18 | `selected_frozen_files_unchanged_after_audit` | Pass. All 158 identified actual archive files retain the recorded SHA-256 after the audit. |

These counts remain distinct: 18 audit cases, 158 identified files, 98 static
import observations and 12 Git-filter observations. They are not added to the
root test suite's method count. A subsequent read-only schema check also confirmed
that the baseline/frozen `$defs` key sets match; this strengthens the description
of the four-definition change and is not counted as a nineteenth audit case.

## Exact preserved identities and boundaries

The five protected file groups total 147 files. Adding the ten capture modules
and supplied PDF gives the 158-file identity inventory. The core, VST3 and
protected data sets compare the complete file representation, including Git mode
and type; the archive bytes also match. The nominal profile remains explicitly
unmeasured. Pedal maps, scanner/rotary profiles, control-state grammar and public
parameter defaults are retained. No synthetic capture result is promoted to a
new physical constant or hardware fidelity evidence.

| Selected frozen file | Bytes | SHA-256 |
| --- | ---: | --- |
| `data/parameter-registry.json` | 34769 | `a80b0f391a37dd9264dc6962131e61c6ba8a0b8ce570d15e89042abe13d148c4` |
| `include/hammond/ControlState.h` | 4898 | `2fb1b7b7fc39363f7e53eb81e2edf3ddb88944b4aa20969b92a90f5c584b2edb` |
| `src/ControlStateIO.cpp` | 11261 | `a1043d29d2321cccad4e994afbf62e16d93ce6cd15ce5c7593556daff1b0a8cf` |
| `include/hammond/ParameterBridge.h` | 2643 | `da68b2e5e2dae211597270924dbdad33c6be8606c5aaa164bd8de92878ea90a0` |
| `src/ParameterBridge.cpp` | 9688 | `14d7dcfd24f5e7d6d59de8b31999ee52b33c64f73df453bff82b9eaa4f89dce0` |
| `plugins/vst3/PluginIds.h` | 746 | `2bc93839216f52d5920046931d83ba14fd2d01e15fdbdd477b71b15ebb8415fc` |
| `data/profiles/nominal-unmeasured-v1.json` | 19627 | `d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff` |
| `data/pedal-map.json` | 3267 | `58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd` |
| `data/references/factory-table-iii.json` | 6647 | `8c52ccca13653c6e379da33a10197bfc9ac1a1f3ab6bea6bbe8edf81f7a47b52` |
| `data/scanner/atlas-late-b3-nominal-v1.json` | 26228 | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |
| `data/rotary/nominal-research-v1.json` | 19988 | `c0473cb20604726d989d7c280700109f647f7b227edb71c61d275ed9bfd67443` |
| `data/dependencies/sdl2-lock.json` | 375 | `ddc78f8cbe3deea26a71109f24e4121551af798f8347bbc3f6fabb8f87950e84` |
| `data/dependencies/vst3-sdk-lock.json` | 3796 | `ef3dfdf3feb5747967fe205ba196f5ef1b01457653f6ad7a62fffefd702ba965` |
| `docs/CONTROL_STATE_FORMAT.md` | 11071 | `c49b96dd14a09cb00f2439b52764957628b0b02f5d59250c53e9fd9d9b126708` |
| `Hammond_B3_Leslie_Research_Atlas_500pp.pdf` | 21248265 | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| `tools/capture_audio.py` | 30313 | `f6f059a81078982d1061637c84836bef9564d51215cb37e0c120046ba0d7b216` |
| `tools/capture_common.py` | 12774 | `f583dbfde3d164157d7e5aa1c601878e3f7d44b4eb7fb059426b92045ac793ab` |
| `tools/capture_corpus.py` | 39476 | `baf4aac2fc87e322d2e5d663f4de9da8118559100ad7de1e6f77feba606779a8` |
| `tools/capture_job.py` | 24433 | `a12645460b4c35400e5f851ac61f7bf273741a3c8d249ee186e93c46ba43a92b` |
| `tools/capture_readiness.py` | 11630 | `816ae53470e54c428cf53bbcf566ddf9a46ad422e427f3bfb28d9b47ca7e64e1` |
| `tools/capture_study.py` | 16849 | `5147b3f7b959ff6e2e1c7ca4b49154579a212af1cf2604bb6272fd9a212f5f98` |
| `tools/compare_capture.py` | 33448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `tools/make_capture_demo.py` | 25734 | `67a49b81f009677a7d2ac62c7f6b95a50e5dd885dca0cc2ac04ca42655f79535` |
| `tools/validate_capture.py` | 28237 | `f17ac8e24c98c792364bfdcc10c41bf410853ba19654eaa36482596d5881f3aa` |
| `tools/verify_capture_report.py` | 23489 | `6c100e976cbe9fa4748a66fe7c6a9488f4e87b4227edc2d88ddf83913b8e91ba` |

The last ten module identities qualify new or revised capture source, rather
than asserting that each existed unchanged at the original baseline. The v1
validator specifically adds its CLI guard while retaining all old definition
bodies. The capture schema's final SHA-256 is
`51fbfdbcc92d9cdb3b71d4b55618840a806e2847b49c93e6aa7d926621661a74`;
its reviewed `$defs` changes are `file`, `id`, `text` and `utc`.

The state writer remains `B3CONTROLS3`; the source retains its version-1 and
version-2 migrations. Processor ID words are
`19F9ADC0 533F42B4 B96BD51D 6547E838`; controller words are
`0DEE76AB 26BC475A BF64F138 C89FB0E0`. These preserve source declarations without
asserting a fresh compiled ABI or reinterpreting SDK-specific UUID byte order.

The entire registry was compared, not only the following selected columns.
Ordering and all 45 records are retained here for direct review:

| Order | ID | Parameter path | Minimum | Maximum | Default | Step count |
| ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 1 | 4096 | `manual.upper.bank.A.drawbar.16ft` | 0 | 8 | 0 | 8 |
| 2 | 4097 | `manual.upper.bank.A.drawbar.5_1/3ft` | 0 | 8 | 0 | 8 |
| 3 | 4098 | `manual.upper.bank.A.drawbar.8ft` | 0 | 8 | 0 | 8 |
| 4 | 4099 | `manual.upper.bank.A.drawbar.4ft` | 0 | 8 | 0 | 8 |
| 5 | 4100 | `manual.upper.bank.A.drawbar.2_2/3ft` | 0 | 8 | 0 | 8 |
| 6 | 4101 | `manual.upper.bank.A.drawbar.2ft` | 0 | 8 | 0 | 8 |
| 7 | 4102 | `manual.upper.bank.A.drawbar.1_3/5ft` | 0 | 8 | 0 | 8 |
| 8 | 4103 | `manual.upper.bank.A.drawbar.1_1/3ft` | 0 | 8 | 0 | 8 |
| 9 | 4104 | `manual.upper.bank.A.drawbar.1ft` | 0 | 8 | 0 | 8 |
| 10 | 4112 | `manual.upper.bank.B.drawbar.16ft` | 0 | 8 | 0 | 8 |
| 11 | 4113 | `manual.upper.bank.B.drawbar.5_1/3ft` | 0 | 8 | 0 | 8 |
| 12 | 4114 | `manual.upper.bank.B.drawbar.8ft` | 0 | 8 | 0 | 8 |
| 13 | 4115 | `manual.upper.bank.B.drawbar.4ft` | 0 | 8 | 0 | 8 |
| 14 | 4116 | `manual.upper.bank.B.drawbar.2_2/3ft` | 0 | 8 | 0 | 8 |
| 15 | 4117 | `manual.upper.bank.B.drawbar.2ft` | 0 | 8 | 0 | 8 |
| 16 | 4118 | `manual.upper.bank.B.drawbar.1_3/5ft` | 0 | 8 | 0 | 8 |
| 17 | 4119 | `manual.upper.bank.B.drawbar.1_1/3ft` | 0 | 8 | 0 | 8 |
| 18 | 4120 | `manual.upper.bank.B.drawbar.1ft` | 0 | 8 | 0 | 8 |
| 19 | 4128 | `manual.lower.bank.A.drawbar.16ft` | 0 | 8 | 0 | 8 |
| 20 | 4129 | `manual.lower.bank.A.drawbar.5_1/3ft` | 0 | 8 | 0 | 8 |
| 21 | 4130 | `manual.lower.bank.A.drawbar.8ft` | 0 | 8 | 0 | 8 |
| 22 | 4131 | `manual.lower.bank.A.drawbar.4ft` | 0 | 8 | 0 | 8 |
| 23 | 4132 | `manual.lower.bank.A.drawbar.2_2/3ft` | 0 | 8 | 0 | 8 |
| 24 | 4133 | `manual.lower.bank.A.drawbar.2ft` | 0 | 8 | 0 | 8 |
| 25 | 4134 | `manual.lower.bank.A.drawbar.1_3/5ft` | 0 | 8 | 0 | 8 |
| 26 | 4135 | `manual.lower.bank.A.drawbar.1_1/3ft` | 0 | 8 | 0 | 8 |
| 27 | 4136 | `manual.lower.bank.A.drawbar.1ft` | 0 | 8 | 0 | 8 |
| 28 | 4144 | `manual.lower.bank.B.drawbar.16ft` | 0 | 8 | 0 | 8 |
| 29 | 4145 | `manual.lower.bank.B.drawbar.5_1/3ft` | 0 | 8 | 0 | 8 |
| 30 | 4146 | `manual.lower.bank.B.drawbar.8ft` | 0 | 8 | 0 | 8 |
| 31 | 4147 | `manual.lower.bank.B.drawbar.4ft` | 0 | 8 | 0 | 8 |
| 32 | 4148 | `manual.lower.bank.B.drawbar.2_2/3ft` | 0 | 8 | 0 | 8 |
| 33 | 4149 | `manual.lower.bank.B.drawbar.2ft` | 0 | 8 | 0 | 8 |
| 34 | 4150 | `manual.lower.bank.B.drawbar.1_3/5ft` | 0 | 8 | 0 | 8 |
| 35 | 4151 | `manual.lower.bank.B.drawbar.1_1/3ft` | 0 | 8 | 0 | 8 |
| 36 | 4152 | `manual.lower.bank.B.drawbar.1ft` | 0 | 8 | 0 | 8 |
| 37 | 8192 | `global.expression` | 0 | 1 | 1 | 0 |
| 38 | 8208 | `manual.upper.selected_bank` | 0 | 1 | 1 | 1 |
| 39 | 8209 | `manual.lower.selected_bank` | 0 | 1 | 1 | 1 |
| 40 | 12288 | `percussion.enabled` | 0 | 1 | 0 | 1 |
| 41 | 12289 | `percussion.harmonic` | 0 | 1 | 0 | 1 |
| 42 | 12290 | `percussion.volume` | 0 | 1 | 0 | 1 |
| 43 | 12291 | `percussion.decay` | 0 | 1 | 0 | 1 |
| 44 | 16384 | `pedal.drawbar.mixture1` | 0 | 8 | 0 | 8 |
| 45 | 16385 | `pedal.drawbar.mixture2` | 0 | 8 | 0 | 8 |

## Concurrent work and rights inventory

The baseline includes fewer standalone/chapel features than the frozen source.
The selected 74 standalone-related paths all equal already published `3b0979b`,
with 53 differences from the baseline retained intentionally. The exact path
selection and complete changed-path list are produced by the executable below.
Root `CMakeLists.txt` changes include the concurrent chapel compiler and the
separate CaptureTools installer; they do not add capture work to Engine audio
processing. The existing OfflineTools helper remains identical to baseline.

The capture runtime's ten modules have only standard-library/local static import
roots on the observed Python 3.12 runtime. The install helper declares exactly
57 source/data/document files and contains no inspected `FetchContent`,
`ExternalProject` or `file(DOWNLOAD)` acquisition. Neither an SDK, native binary,
font, external recording, interpreter nor PDF asset is in that package inventory.
The static source scan is not a proof of every possible dynamic execution path
or a new native/platform run. Separate install and clean-setup records own those
actual executions.

The sixteen original demo files equal the published source. Independent raw
sample reconstruction is retained below. Their explicit synthetic and unknown
rights declarations remain intact. No borrowed external dataset/library tree was
observed in this finite calibration closure; source inspection cannot independently
establish historical authorship of every line or grant redistribution permission.
`THIRD_PARTY_NOTICES.md` differs from the baseline because concurrent standalone
work added SDL yuv2rgb, HIDAPI and conditional Sun math notices. It is unchanged
from the published comparison. No project-wide license is selected, and the
supplied PDF's existing unresolved rights record remains unchanged.

The concrete gap was that the frozen `docs/DEPENDENCIES_AND_RIGHTS.md` lacked a
CaptureTools distribution row/update while the component-specific install guide
already stated its boundaries. Root accepted this finding and added a dated
2026-11-14 row plus bounded explanation. This reviewer reread the working response:
it describes 57 files (10 modules, 8 data, 16 demo, 21 documents, README and
notices), Python standard-library runtime, original synthetic arrays, exclusion
of native/research assets and authoring-only `jsonschema` usage. It retains
existing project/PDF decisions without introducing a permission flow.

Observed post-freeze response: `docs/DEPENDENCIES_AND_RIGHTS.md`, **25,664 bytes**,
SHA-256 `6e49d4470e205d21ec6b3348e64a8a74b4ef57ff49144d0e0073899872fad9a1`.
This later root edit is not relabeled as a file in frozen tree `3edea083` and does
not change the frozen source audit result.

## Independent original-byte experiment

Exact baseline/frozen attributes were placed in a newly initialized private
temporary Git repository. The probe disabled global/system Git configuration
with `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=os.devnull`; the clean-filter
query explicitly used `core.autocrlf=false`. `git hash-object --no-filters --stdin`
was compared with `git -c core.autocrlf=false hash-object --path=... --stdin`.
Neither call used `-w`; the real repository's object store was untouched.

Before-attribute SHA-256:
`00dcf34b90ce5b61c0596ca66382c98b12c9f8fca20e6987d74dc0fda28eaf34`.
After-attribute SHA-256:
`8542587b919ae11040aea5fcaaf1d2d836139bd81a7fbc2e9e2aee2ce2299e2d`.

| Raw specimen | Exact bytes in hexadecimal | Little-endian float32 samples |
| --- | --- | --- |
| `printable_crlf_a` | `410d0a3f` | `[0.5392647385597229]` |
| `printable_crlf_b` | `420d0a3f` | `[0.5392647981643677]` |
| `reference` | `0000803f000080bf0000803f000080bf` | `[1.0, -1.0, 1.0, -1.0]` |
| `quarter` | `0000a03f000040bf0000a03f000040bf` | `[1.25, -0.75, 1.25, -0.75]` |
| `half` | `0000c03f000000bf0000c03f000000bf` | `[1.5, -0.5, 1.5, -0.5]` |

The two four-byte samples are finite values within the inspector's amplitude
bound. The old text-auto/LF rule changes their path-filtered identities; the
new `*.f32 binary` rule preserves them. All three actual demo streams were already
preserved under the old rule and remain preserved. The JSON control is
`{"same":"text"}` followed by CRLF; both attribute sets still normalize it to LF.

| Original raw specimen | Bytes | SHA-256 |
| --- | ---: | --- |
| `printable_crlf_a` | 4 | `b6ef8d51b79b02f5bbd9091f2b23a1ae8be45bbc8021e557b61730d14dabb3a9` |
| `printable_crlf_b` | 4 | `ec5298f215266208c87e843c5d47774409f28028b1b6f535d5f57b0a69296535` |
| `reference.f32` | 16 | `fd801740524b1e1c23a61b5400725b76428652827ba1261b83243eb5ce551402` |
| `quarter.f32` | 16 | `bac1c395abe23908b8c106a28b6c151bc25b9473d470f4d942775b5dfdf523e2` |
| `half.f32` | 16 | `36d231b4ecc15924aea04f08725924f18ae4346fd287747791d7396eca3d5758` |

The following twelve observations are one audit case:

| Attributes | Specimen | Raw blob, or normalized LF control blob | Path-filtered blob | Expected outcome |
| --- | --- | --- | --- | --- |
| before | `printable_crlf_a` | `12235b56bbf4ac33203be36891af64da460aaf8c` | `b913eb88f077f3eb3c6d0e829ed805d180889535` | old text rule changes bytes |
| before | `printable_crlf_b` | `491e6f24b8461bde874c3e843c9c0e262b5b7e11` | `b892c612742ab77fbc5a294a4616f6e93be3667e` | old text rule changes bytes |
| before | `reference` | `568817ce5ef18985f3a94c757b09d3b1587576be` | `568817ce5ef18985f3a94c757b09d3b1587576be` | raw preserved |
| before | `quarter` | `0e1162b0ef76407c5d93e9b476dc7c2ab459967c` | `0e1162b0ef76407c5d93e9b476dc7c2ab459967c` | raw preserved |
| before | `half` | `d3e3d6ef2a358ff2b21357cbb761e1b582cf1d0b` | `d3e3d6ef2a358ff2b21357cbb761e1b582cf1d0b` | raw preserved |
| before | `text_normalization_control` | `e8af47d6e95538ec7251cb2769a89dee86877143` | `e8af47d6e95538ec7251cb2769a89dee86877143` | text normalization retained |
| after | `printable_crlf_a` | `12235b56bbf4ac33203be36891af64da460aaf8c` | `12235b56bbf4ac33203be36891af64da460aaf8c` | raw preserved |
| after | `printable_crlf_b` | `491e6f24b8461bde874c3e843c9c0e262b5b7e11` | `491e6f24b8461bde874c3e843c9c0e262b5b7e11` | raw preserved |
| after | `reference` | `568817ce5ef18985f3a94c757b09d3b1587576be` | `568817ce5ef18985f3a94c757b09d3b1587576be` | raw preserved |
| after | `quarter` | `0e1162b0ef76407c5d93e9b476dc7c2ab459967c` | `0e1162b0ef76407c5d93e9b476dc7c2ab459967c` | raw preserved |
| after | `half` | `d3e3d6ef2a358ff2b21357cbb761e1b582cf1d0b` | `d3e3d6ef2a358ff2b21357cbb761e1b582cf1d0b` | raw preserved |
| after | `text_normalization_control` | `e8af47d6e95538ec7251cb2769a89dee86877143` | `e8af47d6e95538ec7251cb2769a89dee86877143` | text normalization retained |

The root's retained [binary identity record](../../reviews/CALIBRATION_RAW_GIT_IDENTITY.md)
contains the production repair and its regression evidence. This independent
probe adds a second valid CRLF-containing float. The rule covers lower-case
`.f32`, not arbitrary unnamed formats or edits outside Git. Original hashes and
sample metadata still matter at acquisition and handoff.

## Exact executable retained for reproduction

The following fence contains the successful 15,479-byte script verbatim. Extract
only its body, including the trailing LF, to reproduce the recorded script hash.
The absolute paths are retained because they describe the actual execution. To
repeat in another workspace, recreate the corresponding frozen archive and
explicitly change only the two input locations and scratch output location;
retain the immutable commit/tree constants and report any adjusted script hash.
The output result includes the complete source identity map and all observations.
This is retained audit evidence, not an added maintained project test.

<!-- BEGIN EXACT A51 AUDIT SCRIPT -->
```python
#!/usr/bin/env python3
"""Finite read-only compatibility audit; private Git attribute probes only."""
import ast
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys
import tempfile

REPO = Path('/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ')
SOURCE = Path('/workspace/scratch/c9f3ead4c910/w8-combined-source')
BASE = '38c1fac949368fa54bd86c6c00a5997a73480f5e'
FINAL = '48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a'
PUBLISHED = '3b0979bd0d30ce96bca0bcd57bd8f730eaadd1bf'
EXPECTED_TREE = '3edea0838b75feb06c19e151ec8539e80646fc03'

def git(*args, data=None):
    return subprocess.check_output(['git', *args], cwd=REPO, input=data)

def blob(ref, path):
    return git('show', ref + ':' + path)

def tree(ref):
    answer = {}
    for row in git('ls-tree', '-r', '-z', ref).split(b'\0'):
        if not row:
            continue
        metadata, path = row.split(b'\t', 1)
        mode, kind, digest = metadata.decode().split()
        answer[path.decode()] = {'mode': mode, 'type': kind, 'git_object': digest}
    return answer

def sha(data):
    return hashlib.sha256(data).hexdigest()

def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode()

before, final, published = tree(BASE), tree(FINAL), tree(PUBLISHED)
cases = []
identities = {}

def check(name, condition, observation):
    cases.append({'case': name, 'passed': bool(condition), 'observation': observation})
    if not condition:
        raise AssertionError(name)

def preserved(name, paths):
    paths = sorted(paths)
    changed = [p for p in paths if before.get(p) != final.get(p)]
    for p in paths:
        payload = blob(FINAL, p)
        identities[p] = {**final[p], 'size_bytes': len(payload), 'sha256': sha(payload)}
        assert (SOURCE / p).read_bytes() == payload
    check(name, not changed, {'files': len(paths), 'paths': paths, 'changed': changed})

actual_tree = git('rev-parse', FINAL + '^{tree}').decode().strip()
check('frozen_tree_identity', actual_tree == EXPECTED_TREE, actual_tree)
preserved('core_headers_and_implementations', {
    p for p in before | final if p.startswith(('src/', 'include/'))})
preserved('native_vst3_code_and_tests', {
    p for p in before | final if p.startswith('plugins/vst3/')})
preserved('model_routing_registry_and_dependency_data', {
    p for p in before if p.startswith('data/') and p != 'data/capture.schema.json'})
preserved('state_contract_and_legacy_render_inputs', {
    p for p in before | final if p.startswith(('examples/fixtures/', 'examples/rendered/'))} | {
        'docs/CONTROL_STATE_FORMAT.md', 'tools/compile_profile.py',
        'tools/embed_profile.py', 'tools/render.cpp', 'tools/parameter_info.cpp',
        'tools/model_info.cpp', 'tools/validate_parameters.py',
        'cmake/InstallHammondTools.cmake'})
preserved('optional_dependency_locks_workflows_fonts', {
    p for p in before | final if p.startswith(('.github/', 'assets/standalone/'))} | {
        'CMakePresets.json', 'cmake/VerifyVst3Sdk.cmake', 'cmake/VerifySdl2.cmake'})

registry = json.loads(blob(FINAL, 'data/parameter-registry.json'))
parameters = registry['parameters']
ordered = [{k: p[k] for k in ('id', 'path', 'kind', 'minimum', 'maximum', 'default', 'step_count')}
           for p in parameters]
check('public_parameter_id_order_and_all_records',
      len(parameters) == 45 and len({p['id'] for p in parameters}) == 45
      and registry == json.loads(blob(BASE, 'data/parameter-registry.json')),
      {'schema_version': registry['schema_version'], 'ordered_records': ordered})
ids = blob(FINAL, 'plugins/vst3/PluginIds.h').decode()
expected_ids = [
    ['19F9ADC0', '533F42B4', 'B96BD51D', '6547E838'],
    ['0DEE76AB', '26BC475A', 'BF64F138', 'C89FB0E0']]
observed_ids = [re.findall(r'0x([0-9A-F]+)', part)
                for part in re.findall(r'ClassId\{([^}]+)\}', ids)]
check('public_plugin_identifiers', observed_ids == expected_ids,
      {'processor_words': observed_ids[0], 'controller_words': observed_ids[1]})

pdf_path = 'Hammond_B3_Leslie_Research_Atlas_500pp.pdf'
pdf = blob(FINAL, pdf_path)
check('supplied_pdf_original_bytes', before[pdf_path] == final[pdf_path]
      and pdf == (SOURCE / pdf_path).read_bytes()
      and len(pdf) == 21248265
      and sha(pdf) == '4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769',
      {'size_bytes': len(pdf), 'sha256': sha(pdf)})
identities[pdf_path] = {**final[pdf_path], 'size_bytes': len(pdf), 'sha256': sha(pdf)}

def definitions(payload):
    return {n.name: ast.dump(n, include_attributes=False)
            for n in ast.parse(payload).body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}

old_defs = definitions(blob(BASE, 'tools/validate_capture.py'))
new_defs = definitions(blob(FINAL, 'tools/validate_capture.py'))
schema_before = json.loads(blob(BASE, 'data/capture.schema.json'))
schema_final = json.loads(blob(FINAL, 'data/capture.schema.json'))
changed_definitions = sorted(k for k in schema_before['$defs']
                             if schema_before['$defs'][k] != schema_final['$defs'][k])
schema_outer_before = {k: v for k, v in schema_before.items() if k != '$defs'}
schema_outer_final = {k: v for k, v in schema_final.items() if k != '$defs'}
check('v1_runtime_body_preservation_and_schema_scope',
      all(new_defs[k] == v for k, v in old_defs.items())
      and set(new_defs) - set(old_defs) == {'_cli_exit'}
      and changed_definitions == ['file', 'id', 'text', 'utc']
      and schema_outer_before == schema_outer_final,
      {'unchanged_preexisting_definitions': len(old_defs),
       'added_definitions': sorted(set(new_defs) - set(old_defs)),
       'changed_schema_definitions': changed_definitions,
       'schema_sha256': sha(blob(FINAL, 'data/capture.schema.json'))})

modules = ['capture_audio', 'capture_common', 'capture_corpus', 'capture_job',
           'capture_readiness', 'capture_study', 'compare_capture',
           'make_capture_demo', 'validate_capture', 'verify_capture_report']
imports, external = [], []
for name in modules:
    path = 'tools/' + name + '.py'
    payload = blob(FINAL, path)
    assert payload == (SOURCE / path).read_bytes()
    identities[path] = {**final[path], 'size_bytes': len(payload), 'sha256': sha(payload)}
    for node in ast.walk(ast.parse(payload)):
        values = [a.name for a in node.names] if isinstance(node, ast.Import) else (
            [node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
        for value in values:
            first = value.split('.')[0]
            kind = 'project' if first in modules else 'stdlib' if first in sys.stdlib_module_names else 'external'
            row = {'file': path, 'line': node.lineno, 'module': value, 'kind': kind}
            imports.append(row)
            if kind == 'external':
                external.append(row)
check('ten_runtime_module_static_import_closure', not external,
      {'module_count': len(modules), 'import_observations': len(imports),
       'external_imports': external, 'imports': imports})
check('two_independent_script_static_closures', not [
    row for row in imports if row['file'] in ('tools/make_capture_demo.py', 'tools/validate_capture.py')
    and row['kind'] != 'stdlib'],
      {'paths': ['tools/make_capture_demo.py', 'tools/validate_capture.py'],
       'scope': 'static imports; actual execution belongs to assignments46/47/50'})

helper = blob(FINAL, 'cmake/InstallCaptureTools.cmake').decode()
groups = {}
for key in ('modules', 'data', 'documents', 'demo'):
    body = re.search(r'set\(_hammond_capture_' + key + r'\s+(.*?)\)', helper, re.S).group(1)
    groups[key] = body.split()
package = sum(groups.values(), []) + ['README.md', 'THIRD_PARTY_NOTICES.md']
check('capture_package_inventory_and_no_new_download',
      [len(groups[k]) for k in ('modules', 'data', 'documents', 'demo')] == [10, 8, 21, 16]
      and len(set(package)) == 57
      and not re.search(r'FetchContent|ExternalProject|file\s*\(\s*DOWNLOAD', helper, re.I),
      {'group_counts': {k: len(v) for k, v in groups.items()}, 'total': len(package),
       'includes_notices': 'THIRD_PARTY_NOTICES.md' in package,
       'includes_pdf_or_native_binary': any(p.endswith(('.pdf', '.exe', '.so', '.dll')) for p in package)})

demo_paths = sorted(p for p in final if p.startswith('examples/capture-demo/'))
demo_inventory = []
for p in demo_paths:
    data = blob(FINAL, p)
    demo_inventory.append({'path': p, 'size_bytes': len(data), 'sha256': sha(data)})
expected_arrays = {'reference': [1.0, -1.0, 1.0, -1.0],
                   'quarter': [1.25, -0.75, 1.25, -0.75],
                   'half': [1.5, -0.5, 1.5, -0.5]}
observed_arrays = {k: list(struct.unpack('<4f', blob(FINAL, f'examples/capture-demo/corpus/audio/{k}.f32')))
                   for k in expected_arrays}
check('original_synthetic_demo_bytes', len(demo_paths) == 16
      and sum(p['size_bytes'] for p in demo_inventory) == 32831
      and all(final[p] == published[p] for p in demo_paths)
      and observed_arrays == expected_arrays,
      {'files': demo_inventory, 'literal_arrays': observed_arrays})

parallel_prefixes = ('apps/standalone/', 'assets/standalone/', 'data/registrations/',
                     'examples/demos/standalone-', 'examples/standalone-input/')
parallel_extra = {'cmake/CompileChapelCatalog.cmake', 'cmake/InstallStandalone.cmake',
                  'cmake/StandaloneBenchmark.cmake', 'tools/chapel_controls.py',
                  'tools/compile_chapel_presets.py', 'data/chapel-presets.schema.json',
                  'THIRD_PARTY_NOTICES.md'}
parallel = {p for p in final | published if p.startswith(parallel_prefixes)} | parallel_extra
changed_since_baseline = sorted(p for p in parallel if before.get(p) != final.get(p))
check('concurrent_standalone_work_preserved', all(final.get(p) == published.get(p) for p in parallel),
      {'observed_paths': len(parallel), 'changed_from_session_baseline': changed_since_baseline,
       'unchanged_against_published': PUBLISHED})

license_names = [p for p in final if '/' not in p and p.lower().startswith(('license', 'licence', 'copying'))]
rights = blob(FINAL, 'docs/DEPENDENCIES_AND_RIGHTS.md').decode()
check('rights_and_material_inventory_boundaries', not license_names
      and 'no project-wide license' in blob(FINAL, 'THIRD_PARTY_NOTICES.md').decode().lower()
      and final['THIRD_PARTY_NOTICES.md'] == published['THIRD_PARTY_NOTICES.md'],
      {'root_project_license_files': license_names,
       'notices_changed_since_baseline': before['THIRD_PARTY_NOTICES.md'] != final['THIRD_PARTY_NOTICES.md'],
       'notices_equal_last_published': True,
       'capturetools_missing_from_central_inventory': 'CaptureTools' not in rights,
       'review_limit': 'No history/originality or legal clearance attestation; no new third-party runtime/library tree observed in this calibration closure.'})

old_attributes = blob(BASE, '.gitattributes')
new_attributes = blob(FINAL, '.gitattributes')
probe_rows = []
git_environment = dict(os.environ)
git_environment['GIT_CONFIG_NOSYSTEM'] = '1'
git_environment['GIT_CONFIG_GLOBAL'] = os.devnull
with tempfile.TemporaryDirectory(prefix='a51-git-bytes-') as directory:
    work = Path(directory)
    subprocess.run(['git', 'init', '-q', directory], check=True, env=git_environment)
    specimens = {'printable_crlf_a': bytes.fromhex('410d0a3f'),
                 'printable_crlf_b': bytes.fromhex('420d0a3f'),
                 **{k: struct.pack('<4f', *v) for k, v in expected_arrays.items()}}
    for label, attributes in [('before', old_attributes), ('after', new_attributes)]:
        (work / '.gitattributes').write_bytes(attributes)
        for name, payload in specimens.items():
            path = f'capture/{name}.f32'
            raw = subprocess.check_output(['git', 'hash-object', '--no-filters', '--stdin'],
                                          cwd=work, input=payload, env=git_environment).decode().strip()
            clean = subprocess.check_output(['git', '-c', 'core.autocrlf=false', 'hash-object',
                                            '--path=' + path, '--stdin'], cwd=work, input=payload,
                                           env=git_environment).decode().strip()
            probe_rows.append({'attributes': label, 'case': name, 'bytes_hex': payload.hex(),
                               'samples': list(struct.unpack('<' + 'f' * (len(payload)//4), payload)),
                               'raw_blob': raw, 'clean_blob': clean, 'unchanged': raw == clean})
        text = b'{"same":"text"}\r\n'
        clean_text = subprocess.check_output(['git', '-c', 'core.autocrlf=false', 'hash-object',
                                             '--path=text.json', '--stdin'], cwd=work, input=text,
                                            env=git_environment).decode().strip()
        raw_lf = subprocess.check_output(['git', 'hash-object', '--no-filters', '--stdin'],
                                        cwd=work, input=text.replace(b'\r\n', b'\n'),
                                        env=git_environment).decode().strip()
        probe_rows.append({'attributes': label, 'case': 'text_normalization_control',
                           'clean_blob': clean_text, 'raw_lf_blob': raw_lf,
                           'text_rule_preserved': clean_text == raw_lf})
    check('independent_git_raw_byte_before_after',
          all(not row['unchanged'] for row in probe_rows
              if row['attributes'] == 'before' and row['case'].startswith('printable'))
          and all(row['unchanged'] for row in probe_rows
                  if row['attributes'] == 'after' and 'unchanged' in row)
          and all(row['unchanged'] for row in probe_rows
                  if row['attributes'] == 'before' and row['case'] in expected_arrays)
          and all(row['text_rule_preserved'] for row in probe_rows if 'text_rule_preserved' in row),
          {'private_repo_removed_afterward': True, 'observations': probe_rows,
           'before_attributes_sha256': sha(old_attributes),
           'after_attributes_sha256': sha(new_attributes)})

check('selected_frozen_files_unchanged_after_audit', all(
    sha((SOURCE / p).read_bytes()) == row['sha256'] for p, row in identities.items()),
      {'identified_files': len(identities)})
result = {'assignment': 51, 'agent': '/root/cal_w9_a51',
          'baseline_commit': BASE, 'frozen_commit': FINAL, 'frozen_tree': actual_tree,
          'published_comparison': PUBLISHED,
          'runtime': {'python': sys.version, 'platform': platform.platform(),
                      'git': git('--version').decode().strip()},
          'cases': cases, 'case_count': len(cases),
          'passed': sum(c['passed'] for c in cases), 'identities': identities,
          'identity_inventory_sha256': sha(canonical(identities)),
          'production_or_repo_git_mutated': False}
Path('/workspace/scratch/c9f3ead4c910/a51-compatibility-result.json').write_bytes(canonical(result))
print(json.dumps({'cases': len(cases), 'passed': result['passed'],
                  'identified_files': len(identities), 'identity_sha256': result['identity_inventory_sha256'],
                  'group_counts': {c['case']: c['observation'].get('files') for c in cases
                                   if isinstance(c['observation'], dict) and isinstance(c['observation'].get('files'), int)}}, indent=2))
```
<!-- END EXACT A51 AUDIT SCRIPT -->

## Record validation

Both owned Markdown files decode as UTF-8, end with LF and contain no CR or
trailing whitespace. All eleven relative Markdown links resolve in the current
repository. Extracting the exact script fence reproduces its recorded 15,479
bytes and SHA-256, and `ast.parse` accepts it. Replacing the single corrected
filename spelling reproduces the original failed harness's SHA-256. These are
documentation-integrity checks; no extra production qualification or maintained
test is added to the eighteen-case result.

## Remaining gates and next concrete action

Root should accept these two owned records, retain the completed dependency
inventory correction and `.f32` binary rule, and finish its independently
identified coherent build/publication gates. This assignment neither commits nor
pushes and makes no claim about hosted CI, a native host, devices, Windows/macOS,
licensing clearance, source acquisition or completed instrument fidelity.

The useful next physical step remains an explicitly scoped acquisition with
original bytes, measurement/variant/uncertainty metadata and an authorized source
basis; synthetic arrays do not supply the missing calibrated scanner, AO-28 or
Leslie observations. Numerical thresholds in the new analysis contracts remain
software policies until independently justified for the target physical capture.
When a later change touches a preserved public interface, state grammar, nominal
profile, dependency lock, capture schema or package closure, identify the new
source and repeat the affected qualification rather than citing this frozen
review as evidence for changed code.
