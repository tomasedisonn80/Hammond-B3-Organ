# Calibration compatibility and original-byte audit

## Decision and exact scope

Assignment **51**, `/root/cal_w9_a51`, logical wave **9**, completed **18/18
finite audit cases** against the accepted eight-wave source. The inspected
core, public controls, state implementation, plugin identities, existing model
inputs and supplied PDF retain their baseline bytes. The new capture runtime
has no observed external Python import dependency. The independent private Git
probe confirms the root's `.f32` binary classification repair.

One central documentation omission was found: the dependency/rights inventory
did not yet describe CaptureTools. Root added a dated, bounded inventory update
after this finding. No additional production repair is requested by this audit.
Existing project-license and research-permission decisions remain unresolved;
this review neither grants rights nor introduces an approval requirement.

| Source boundary | Exact identity |
| --- | --- |
| Session baseline | `38c1fac949368fa54bd86c6c00a5997a73480f5e` |
| Frozen accepted source | `48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a` |
| Frozen Git tree | `3edea0838b75feb06c19e151ec8539e80646fc03` |
| Published comparison for concurrent work | `3b0979bd0d30ce96bca0bcd57bd8f730eaadd1bf` |
| Immutable archive | `/workspace/scratch/c9f3ead4c910/w8-combined-source` |

The [assignment note](../development/2026-11-13-calibration/51-compatibility.md)
retains the exact executable audit, complete case list, key identities, original
harness failure and root response. The comparison used immutable Git objects
and checked actual archive bytes, rather than treating the later working tree as
the frozen source. It identified and rechecked **158 files**. This is source and
data preservation evidence, not a fresh native ABI, audio, host or fidelity test.

## Existing engine and public identities are preserved

The following five groups are byte-, mode- and Git-object-identical to the
session baseline. The selected archive files also equal those Git objects.

| Protected group | Files | Consequence within this review |
| --- | ---: | --- |
| All `src/` and `include/` files | 42 | Core algorithms, headers, controls, state exchange, nominal scanner/rotary foundations and their existing interfaces are unchanged. |
| All `plugins/vst3/` files | 19 | Native adapter implementation, identifiers, selected build rules and its maintained tests are unchanged. |
| Existing `data/` except the explicitly reviewed capture schema | 17 | Registry, nominal profile, routing/reference inputs, scanner/rotary fixtures and two optional-dependency locks are unchanged. |
| State contract, legacy fixture/render bundles and selected build/render tools | 57 | Existing musical examples, render inputs, serializers' documented grammar and OfflineTools installation rules are preserved. |
| Existing CI workflows, standalone font assets and dependency verification/configuration inputs | 12 | The inspected pins, font inputs and selected optional-dependency boundaries remain unchanged. |

The complete parameter-registry document is unchanged, including all metadata,
normalization rules, defaults, limits and **45 ordered, unique IDs**. Its current
schema version remains 3. The independently enumerated ID groups are:

| Controls | Ordered IDs | Count |
| --- | --- | ---: |
| Upper A drawbars | 4096–4104 | 9 |
| Upper B drawbars | 4112–4120 | 9 |
| Lower A drawbars | 4128–4136 | 9 |
| Lower B drawbars | 4144–4152 | 9 |
| Expression | 8192 | 1 |
| Upper/lower selected bank | 8208, 8209 | 2 |
| Percussion enabled, harmonic, volume, decay | 12288–12291 | 4 |
| Pedal Mixture 1/2 | 16384, 16385 | 2 |

The unchanged [control-state contract](../CONTROL_STATE_FORMAT.md) still writes
`B3CONTROLS3` and retains the version-1/version-2 migrations. The corresponding
parser, serializer, state structures and parameter bridge are among the identical
source files. This audit inspected their identities and version declarations;
it did not rerun their native migration tests or claim that a different compiled
binary has already been qualified.

The VST3 processor's four declared words remain
`19F9ADC0 533F42B4 B96BD51D 6547E838`, and the controller's remain
`0DEE76AB 26BC475A BF64F138 C89FB0E0`. These are the literal source declarations;
the SDK's platform-specific binary UUID representation is not reinterpreted here.
Plugin name/version declarations and the rest of that file are also unchanged.

The supplied atlas remains **21,248,265 bytes**, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
The full-file hash and baseline/frozen bytes were checked. This assignment read
the session's [complete-source consolidation](../research/CALIBRATION_ATLAS_REVIEW.md)
and relevant extracted pages 355, 449 and 484; it does not claim another complete
500-page reading or new verification of external research sources.

## Changes are scoped; the whole repository is not unchanged

The baseline-to-frozen comparison includes separately owned native standalone,
chapel-catalog, example and build work. Across 74 inspected standalone-related
paths, **53 differ from the session baseline**, but every one of the 74 equals
the already published `3b0979b` source. This preserves that concurrent work;
it does not attribute it to the calibration implementation or erase its own
qualification history. The standalone, scanner and rotary scopes remain separate.

In the root `CMakeLists.txt`, the baseline comparison adds two includes: the
concurrent documentary chapel compiler and the capture installation component.
The capture helper defines a separate opt-in source/data/document package; it
does not add capture processing to the Engine or a callback. The existing
OfflineTools helper is byte-identical to baseline. No new capture component
downloads or vendors an SDK during configuration.

The original capture validator is deliberately **not** claimed byte-identical:
the final CLI repair adds its local standard-library finalization guard and
executable entrypoint handling. Independent AST comparison shows all **27
pre-existing top-level function/class definitions** unchanged from the baseline.
The only added definition is `_cli_exit`. Imported validation and `main` bodies
retain their original implementation.

The v1 machine schema also changed. Its outer schema and all definitions except
`text`, `id`, `utc` and `file` remain equal. Those inspected changes explicitly
exclude forbidden/control characters or add exact length bounds, correcting the
terminal-newline pattern gap against the already strict semantic validator.
This review does not call the machine schema unchanged or repeat the separate
[665-case schema qualification](../CAPTURE_SCHEMA_REVIEW.md).

## Runtime closure and material inventory

An AST walk over the final ten capture modules found **98 import observations**.
Every imported root resolves to the observed Python 3.12 standard-library set or
one of the ten explicitly packaged project modules. No external Python package
import was found. This is a static closure observation; installed execution and
relocation are qualified separately by the installation and clean-setup reviews.

Both the demo generator and legacy v1 validator retain standard-library-only
static imports. Their independent single-script execution is owned by the
[CLI pipeline acceptance](CALIBRATION_CLI_PIPELINE.md), including the retained
first candidate's generator-dependency failure. This audit does not reclassify
that earlier candidate as compatible.

The actual CMake declarations match the existing 57-file CaptureTools inventory:
10 Python modules, 8 schema/example data files, 16 demo files, 21 documents, a
generated README and unchanged project notices. The helper contains no download
or external-project acquisition operation. It includes no PDF, native executable,
SDK source, font or Python package tree. Its complete
[installation contract](../CAPTURE_TOOLS_INSTALL.md) remains the authority for
copy/preflight behavior and disclosed package limits.

The sixteen-file demo remains **32,831 bytes**, with every file identical to
the published `3b0979b` archive. Its three raw files total only 48 bytes and
independently decode to these literal arrays:

| File | Little-endian float32 samples |
| --- | --- |
| `reference.f32` | `[1, -1, 1, -1]` |
| `quarter.f32` | `[1.25, -0.75, 1.25, -0.75]` |
| `half.f32` | `[1.5, -0.5, 1.5, -0.5]` |

These are constructed software inputs, with explicit synthetic provenance,
unknown rights declarations and no acquired instrument samples. No newly
vendored external recording, library tree or research asset is observed in the
calibration runtime/package closure. That finite inventory and the literal byte
reconstruction do not independently attest the historical originality of every
line of project code or establish redistribution rights.

`THIRD_PARTY_NOTICES.md` is unchanged from `3b0979b`, but **differs from the
session baseline**: the concurrent standalone work added its retained SDL
yuv2rgb, HIDAPI and conditional Sun math notices. The capture component copies
that current notice without assigning a project license. The frozen source has
no root project `LICENSE`/`LICENCE`/`COPYING` file. The supplied PDF's existing
rights record remains unresolved. Those are retained source/distribution facts,
not new permission requests or legal conclusions from this audit.

## Independent raw float32 Git-filter reproduction

Root's [raw-byte record](CALIBRATION_RAW_GIT_IDENTITY.md) identified a real
classification gap: valid float32 data can look like text to Git. This reviewer
reproduced it in a new temporary repository, using exact baseline/frozen
`.gitattributes` bytes, an explicitly disabled global/system Git configuration
and `core.autocrlf=false`. The original repository's Git state and files were
never modified. The private repository was removed afterward.

Two independent four-byte inputs contain a CRLF pair and no binary-identifying
NUL. Both decode to finite samples inside the inspector's amplitude bound:

| Original bytes | Decoded sample | Raw Git blob | Old path-filtered blob |
| --- | ---: | --- | --- |
| `41 0d 0a 3f` | 0.5392647385597229 | `12235b56bbf4ac33203be36891af64da460aaf8c` | `b913eb88f077f3eb3c6d0e829ed805d180889535` |
| `42 0d 0a 3f` | 0.5392647981643677 | `491e6f24b8461bde874c3e843c9c0e262b5b7e11` | `b892c612742ab77fbc5a294a4616f6e93be3667e` |

With the final `*.f32 binary` rule, the path-filtered identity equals the raw
identity for both inputs. All three original demo streams are preserved under
both old and new rules; no existing demo corruption is claimed. A separate JSON
text control still normalizes CRLF to LF under both rules. These are **twelve
observations inside one audit case**: five raw specimens and one text control,
each under the two attribute sets.

The rule covers the declared lower-case `.f32` extension. It does not prevent
external editing or guarantee arbitrary unnamed raw formats. Future formats
still require correct binary classification and original-byte verification.
No root Git objects were written by the probe; `hash-object` ran without `-w`.

## Documentation finding, execution limits and next step

The frozen central [dependency inventory](../DEPENDENCIES_AND_RIGHTS.md) lacked
a CaptureTools distribution row/update even though the component's own guide
already gave the correct inventory and rights boundary. Root subsequently
added a dated 2026-11-14 row and bounded explanation. This reviewer reread the
new text: it identifies the 57 files, standard-library runtime, original
synthetic arrays, excluded native/research assets and authoring-only `jsonschema`
use, while preserving the existing project/PDF decisions. The note records the
later file's identity; it is not presented as part of the earlier frozen tree.

Execution used CPython 3.12.14, Git 2.52.0 and Linux x86_64. The first audit
attempt stopped on a harness-only filename capitalization error,
`cmake/VerifySDL2.cmake`; the actual tracked path is `cmake/VerifySdl2.cmake`.
Only that path spelling changed. The original harness remains identified in the
note; the corrected complete eighteen-case scope passed without production edits.

Root should accept these two records, retain the corrected central inventory
and the binary rule, and complete its coherent build/publication gates. This
review does not claim root's concurrently running full suite, a new hosted
platform result, binary compatibility across different toolchains, measured
organ fidelity, acquired permissions or completed release clearance. A later
change to a preserved interface, profile, format or package closure requires
its affected qualification again, with its own source identity.
