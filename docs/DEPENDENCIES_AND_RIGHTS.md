# Dependencies, distributed material and rights handoff

**Current review: 2026-11-13, pedal-session assignment 52.** The current boundaries
below include the implemented optional module, actual published Linux/Windows
bundle artifacts and the 23-file OfflineTools rules prepared in wave 8. The
original inventory was based on `7c2ad20`; original-session assignment 50 added
the demo generated at `6c3dd8b`, and pedal assignment 15 selected the SDK
foundation. Those dated results remain historical. This inventory identifies
actual material and unresolved decisions; it grants no rights and selects no
project-wide license. No project `LICENSE` file was present in the inspected
source. The [independent artifact review](reviews/PEDAL_DEPENDENCY_ARTIFACT_FINAL.md)
records exact source, artifact and verification scope.

Evidence: tracked plus proposed nonignored files, C++ includes, Python imports, [CMake](../CMakeLists.txt), [CI workflow](../.github/workflows/ci.yml), [source manifest](research/source-manifest.json), [source-rights record](research/RIGHTS_AND_SOURCES.md), and the linked primary license files below. Recheck the final staged payload when creating a release; this is not a claim about an uninspected future archive.

## Distribution boundaries

| Boundary | Actual contents / consequence |
| --- | --- |
| Repository/source archive | Project C++ headers/source, Python tools/tests, build configuration, original documentation, reconstructed/proposed JSON, factual CSVs, text event fixtures, and the supplied atlas PDF. The imported SplitMix64 routine is identified below. The standalone adds two unmodified DejaVu 2.37 font inputs, their complete notice and generated glyph data, with exact manifests. No SDL2/VST3 SDK source tree, extracted atlas image or additional manual PDF is vendored. Retained demo WAVs are explicitly synthetic engineering output. |
| Local `OfflineTools` install | Exactly 23 configured files: five native executables, two standalone standard-library plot scripts, the compiled nominal profile, three catalogs and twelve event scores. See the [exact layout and current qualification](OFFLINE_INSTALL.md). The atlas, factual CSVs, Python interpreter, core archive/headers and toolchain runtime libraries are not copied. |
| CI execution and artifacts | Both workflows fetch the three pinned actions below; setup-python selects Python `3.12`; hosted images supply compilers/CMake and platform tools. Core CI retains diagnostics. The separate [native workflow](VST3_CI.md) also uploads the actual validated platform bundle, byte inventory and archive hash. These are development artifacts, not signed release installers. Action implementations and runner images are not vendored into the repository or installed payload. |
| Generated outputs | Profiles, diagnostic SVGs and WAV/evidence bundles are generated from declared project inputs. Original, console and pedal catalogs contain synthetic gestures without recorded samples. Retained [dry](../examples/rendered/nominal-two-manual-v1/README.md), [console](../examples/rendered/nominal-console-v2/README.md) and [pedal](../examples/demos/pedal-phrase-v1/README.md) examples include actual generated audio and evidence, with no executable or hardware recording in those example bundles. Keep their input/output identities and nominal-engine scope. |

The OfflineTools component currently stages neither `THIRD_PARTY_NOTICES.md`
nor this inventory. It remains a local tool layout; a redistribution package
must carry its applicable notices and identify any included compiler/OS runtime
files. The native component already includes the selected SDK license and
project notices, as described below. Python is required for the installed plot
scripts, but not for the five native executables. Both components still require
a compatible platform/runtime; see the [offline](OFFLINE_INSTALL.md) and
[native](VST3_LOCAL_INSTALL.md) staging contracts.

## Software dependencies actually used

| Component | Current role and provenance | Current distribution treatment |
| --- | --- | --- |
| C++20 and its standard library | `src/`, `include/hammond/`, C++ CLI/benchmark/tests use standard headers and project headers. `hammond_core` is an internal static target; consumers link it. | The ordinary core/offline targets have zero external runtime audio, GUI or plugin-SDK dependencies. No third-party framework/library source is vendored. The separately acquired optional VST3 SDK is inventoried below. This does not mean zero OS/compiler-runtime dependencies. |
| Python 3.10+ | Profile compiler, evidence/validation tools and Python tests use the standard library and local project modules. The apparent nonstdlib import `analyze_wav` resolves to `tools/analyze_wav.py`. | No pip dependencies, copied interpreter or Python package tree. CI selects 3.12; exact patch/runtime builds remain environment-specific. |
| CMake/CTest 3.21+ | Build/profile generation and test orchestration; CMake modules come from the installed toolchain. | No implicit `FetchContent`/`ExternalProject` download or bundled CMake distribution. The selected optional VST3 SDK requires CMake 3.25+ only when the implemented optional plugin target is enabled. |
| SplitMix64 | `src/TonewheelBank.cpp::next_phase_bits` adapts the 2015 Sebastiano Vigna reference, using caller-owned state. Primary source: [splitmix.c](https://prng.di.unimi.it/splitmix.c), inspected 2026-11-13. | The primary source states a worldwide public-domain dedication to the extent possible under law, a permissive use/copy/modify/distribute grant, and an as-is disclaimer. Attribution and a linked terms summary are retained in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md). No separate upstream file is vendored. |

No universal license is assigned here to GCC/libstdc++, Clang/libc++, MSVC/UCRT, Python, CMake or hosted runner images. Select and inspect exact versions and bundled runtime payloads before making a binary-distribution claim. Tool availability and a CI pass do not resolve that package-specific review.

## Optional VST3 SDK foundation: selected, separately acquired

Assignment 15 selected the official **Steinberg VST 3 SDK 3.8.1**, tag
`v3.8.1_build_84`, commit `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96`, for a
minimal headless instrument sharing this core. Acquisition/review date:
2026-11-13. The [machine-readable lock](../data/dependencies/vst3-sdk-lock.json)
retains exact repository URLs, commits, license identities, excluded modules,
build options and permanent processor/controller class IDs. The
[implementation contract](VST3_SPIKE_CONTRACT.md) defines the optional boundary.

| Required source | Exact commit | Inspected primary terms |
| --- | --- | --- |
| [SDK root](https://github.com/steinbergmedia/vst3sdk/tree/3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96) | `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` | Root `LICENSE.txt`, MIT |
| [base](https://github.com/steinbergmedia/vst3_base/tree/fcf9da0bd27a16f7f03773a3a39822f28f5c8477) | `fcf9da0bd27a16f7f03773a3a39822f28f5c8477` | Module `LICENSE.txt`, MIT |
| [cmake](https://github.com/steinbergmedia/vst3_cmake/tree/054c9143cbb8d47fc4694e473f2ee3b4d951a8f5) | `054c9143cbb8d47fc4694e473f2ee3b4d951a8f5` | Module `LICENSE.txt`, MIT |
| [pluginterfaces](https://github.com/steinbergmedia/vst3_pluginterfaces/tree/4f547e8e102b47de4a8b8aaf343c73b700786372) | `4f547e8e102b47de4a8b8aaf343c73b700786372` | Module `LICENSE.txt`, MIT |
| [public.sdk](https://github.com/steinbergmedia/vst3_public_sdk/tree/586dc5e6c8012c3e4b01c79389375cbe96bdb1da) | `586dc5e6c8012c3e4b01c79389375cbe96bdb1da` | Module `LICENSE.txt`, MIT; embedded third-party exception below |

All five inspected license files are byte-identical: 1,094 bytes, SHA-256
`e86d79e19e4a33ebc442d2e0d083887dfc75a2a8de9fe17eeddedb84810ad74e`, copyright
2026 Steinberg Media Technologies GmbH. The complete MIT text is retained in
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md). Copies or substantial portions
of covered software must retain its copyright and permission notice. This
selected SDK does not require importing the atlas's historical SDK license
assumptions, nor does its license choose this project's own license or grant
rights to research assets, trademarks or other components.

The SDK's embedded `public.sdk/source/vst/moduleinfo/json.h` declares
**Unlicense**, not MIT. Its exact file is 100,775 bytes, SHA-256
`098ca68126cb34f7369388d49890d0a5d5ba731b76fbae0c2790377a663e9d41`, in the pinned
`public.sdk` revision. It is used by the module-info parser and SDK validator.
Its retained notice and [upstream source](https://github.com/sheredom/json.h) are
identified separately. Other sample-only dependencies (including NanoVG and
MetalNanoVG) are outside the selected headless build; their existence prevents
a blanket claim that every SDK file is MIT. This is an inspected selected-path
inventory, not a complete transitive audit of omitted SDK samples.

Acquisition remains external to the project tree. No SDK source tree or built
validator is committed, placed in OfflineTools or copied into the native bundle.
GUI, plugin examples, hosting examples and automatic plugin-directory links
are disabled. The ordinary build stays SDK-free and performs no network
acquisition; optional configuration performs read-only verification of the
existing locked checkout. The explicit acquisition command refuses an existing
destination and checks the root, four gitlinks/checkouts, tracked/untracked/
ignored state, five primary licenses and the embedded JSON header.

The lock's `qualification` block records assignment 15's historical SDK-foundation
observation: a validator build and **51 passed/zero failed selftests**. It is
not a current assertion that the later Hammond module is absent. Subsequent
[actual ABI](VST3_ABI_ACCEPTANCE.md), [behavior](VST3_BEHAVIOR_ACCEPTANCE.md),
[installation](VST3_LOCAL_INSTALL.md) and [platform](reviews/PEDAL_NATIVE_PORTABILITY.md)
records identify their own source and executed scopes. The immutable lock,
original class IDs and selected notice bytes are preserved.

## Actual native development payload

Assignment 52 independently inspected the Linux and Windows bundle ZIPs uploaded
by native [run 43415692247](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43415692247)
at `7fb9b6121b729f46a9e18d80e8620eb21dc0847b`. Their ZIP hashes match freshly read
Actions metadata; the inner archive hashes and every file's bytes, size, mode
and SHA-256 match the retained inventories. The source field is caller-declared;
workflow/run/source association was checked separately, and no signed build
attestation is inferred. The [audit](reviews/PEDAL_DEPENDENCY_ARTIFACT_FINAL.md)
retains all exact identities and observed test-log boundaries.

| Actual payload | Included files and dependency boundary |
| --- | --- |
| Linux artifact `14032125757` | Four files: the x86-64 ELF module, generated `moduleinfo.json`, `VST3_SDK_LICENSE.txt` and `THIRD_PARTY_NOTICES.md`; 456,767 bytes in total. |
| Windows artifact `14032090890` | Six files: the x86-64 PE32+ module and the same three resource roles, plus SDK-provided `PlugIn.ico` and generated/copied `desktop.ini`; 658,056 bytes in total. |
| Notices/profile | Both artifacts include the exact 1,094-byte locked SDK license and source notices. Each actual module contains the unchanged 4,545-byte nominal compiled profile exactly once. The profile is compiled into the module, not copied as another payload file. |
| SDK code and tools | Selected SDK code is linked into the native module. No SDK source tree, validator, module-info generator, test executable, PDF, capture or Python interpreter occurs in either inspected bundle. This is a finite actual-file inventory, not a blanket license assignment to every SDK sample. |
| Runtime imports | The inspected Linux module imports `libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1` and `libc.so.6`. The Windows module imports Windows APIs, MSVC runtime DLLs and UCRT API-set names listed in the audit. Those runtime libraries are not bundled in these payloads; import inspection is not a complete transitive runtime/redistribution review. |

### Windows SDK folder icon and branding decision

The Windows `PlugIn.ico` is byte-identical to the selected CMake submodule's
[`templates/VST_Logo_Steinberg.ico`](https://github.com/steinbergmedia/vst3_cmake/blob/054c9143cbb8d47fc4694e473f2ee3b4d951a8f5/templates/VST_Logo_Steinberg.ico):
254,170 bytes, SHA-256
`1dda09aceb9fa930a3894cce4ad57edd8fa48ce58157c97ba5f971d2d4e79821`.
`desktop.ini` is the unchanged 44-byte SDK template selecting that icon. These
are actual copied assets, not inferred from the SDK's name. The
[pinned SDK README](https://github.com/steinbergmedia/vst3sdk/blob/3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96/README.md#trademark-and-logo-usage)
separately describes conditions for optional VST names/logos; this audit has not
completed a review of the intended product branding against those conditions.

For a future original project icon, the selected SDK supports setting
`SMTG_PACKAGE_ICON_PATH` to an existing owned ICO before `smtg_add_vst3plugin`.
The pinned helper falls back to the SDK logo if that path is empty or missing;
those values do not omit it. The inspected helper path has no separate
omit-icon option. Turning off Windows bundle creation changes the package
contract and is not a scoped icon replacement. Choose and record the intended
asset/branding treatment, then requalify the actual Windows payload; no SDK,
build, icon, notices or license-lock mutation was made in assignment 52.

## Source and data provenance

| Material | Origin, identity and applicable limit |
| --- | --- |
| Supplied research atlas | `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, present in baseline `501c68b`; evidence edition 2026-11-12; 500 pages; 21,248,265 bytes. Raw SHA-256: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`, rechecked unchanged. Supplier authorship, publication/derivative rights and underlying asset permissions remain unresolved. A matching hash establishes identity, not permission. [Source record](research/RIGHTS_AND_SOURCES.md) |
| Nominal model and project contracts | `data/profiles/nominal-unmeasured-v1.json`, `data/pedal-map.json`, `data/parameter-registry.json`, profile/capture schemas, planned capture record, tooling and documentation are new implementations, proposals or labeled reconstructions. They are not recovered atlas companion files. The [source manifest](research/source-manifest.json) retains the baseline absence; [profile](PROFILE_FORMAT.md), [pedal](PEDAL_ROUTING.md) and [capture](CAPTURE_FORMAT.md) contracts preserve their individual provenance. No project-wide reuse grant is supplied by this inventory. |
| Independent factual CSVs | `data/references/review-a-manual.csv`, `review-b-manual.csv`, `review-a-pedal.csv`, `review-b-pedal.csv`: new literal transcriptions of Table III identifiers, not facsimiles. Agents 37/38 entered source-image cells independently and froze hashes before comparison with each other or derived data. [Review A](research/FACTORY_REVIEW_A.md), [review B](research/FACTORY_REVIEW_B.md) and [comparison manifest](../data/references/factory-table-iii.json) retain the procedure. |
| Comparison/capture evidence | `factory-table-iii.json` is a new comparison/provenance record, not a recovered numeric companion. `capture-planned-example.json` has `status: planned`, no artifact files and unresolved permissions. No hardware recordings or impulse responses have been admitted. Synthetic test bytes and generated WAVs do not constitute licensed hardware captures. [Factory comparison](FACTORY_REFERENCE.md), [capture protocol](CAPTURE_PROTOCOL.md) |

The factual CSVs cite the separately acquired [factory service scan](https://medias.audiofanzine.com/files/hammond-service-manual-a-a-100-ba-bc-bcv-bv-b2-b3-c-cv-c2-c2-text-470145.pdf): 220 pages, 7,077,593 bytes, SHA-256 `ec2ac51f363dcd1ee039f7711acda32fd014e15ad80dcb77ae199545f9130cc9`. This inventory inherits its acquisition/identity evidence from the retained reviews; it did not reacquire or redistribute that PDF or its rendered pages. Public accessibility is not recorded as redistribution permission.

Manual cells are PDF 155-156 / printed 3-76 to 3-77; pedal cells are PDF 157 / printed 3-78. The section names B-3/C-3 at PDF 148 / printed 3-69. Exact edition, print date and applicable production revisions remain unestablished; applicability to a particular specimen is also unknown. Both readings agree on 549 manual assignments and 200 pedal positions, including five disconnections; this is documentary routing evidence, not measured tuning or physical fidelity. [Retained source locators and comparison](FACTORY_REFERENCE.md)

| Frozen CSV identity, independently rehashed in this review | Bytes each | SHA-256 |
| --- | ---: | --- |
| Review A and review B manual, each | 1,852 | `23ade40234db10d0bf99cd5acf9ee0ff29e4656e847e61409ebe8717f7cb9dc6` |
| Review A and review B pedal, each | 677 | `b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1` |

The atlas's references to third-party photographs, patent plates, fonts, manuals and studied programs are discovery/provenance leads. Its original catalogs and `THIRD_PARTY_FONT_NOTICES.txt` are absent here. Embedded atlas material remains part of its unresolved rights scope; this inventory neither extracts it nor recreates missing permission records. Merely citing setBfree, a paper, an SDK or a framework does not import that source or license. [Atlas source-rights review](research/RIGHTS_AND_SOURCES.md), atlas pp. 475-480.

## CI action pins and verified primary licenses

Only these actions occur in the workflow. The version labels below are the workflow comments; the full SHAs are the actual selections. Each official `LICENSE` was fetched at that SHA on 2026-11-13 and states MIT, with `Copyright (c) 2018 GitHub, Inc. and contributors`.

| Action | Version comment | Actual pin / primary license |
| --- | --- | --- |
| `actions/checkout` | `v7.0.1` | [`3d3c42e5aac5ba805825da76410c181273ba90b1` / LICENSE](https://github.com/actions/checkout/blob/3d3c42e5aac5ba805825da76410c181273ba90b1/LICENSE) |
| `actions/setup-python` | `v7.1.0` | [`6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` / LICENSE](https://github.com/actions/setup-python/blob/6d4fd22b20465ccc0f7354476588e8df7c9ca0e0/LICENSE) |
| `actions/upload-artifact` | `v7.0.2` | [`cf430e030ddbb5b0abf93d22962f4752f3646cd9` / LICENSE](https://github.com/actions/upload-artifact/blob/cf430e030ddbb5b0abf93d22962f4752f3646cd9/LICENSE) |

These are top-level action-license checks, not a transitive-dependency audit of action bundles, Node, downloaded Python or runner images. No complete dependency tree was fetched. If any such implementation is later copied into a distribution, review its complete included payload and preserve all applicable notices. [CI maintenance procedure](CI.md)

## Gate for the next dependency, asset or release

The selected optional VST3 SDK and native module now have scoped executed evidence above. A complete release, DAW/device operation and project-wide rights review remain separate gates. The later standalone update below selects pinned SDL2 and DejaVu inputs; the earlier pedal assessment did not yet select a GUI/device dependency. The atlas's historical SDK/framework licensing observations do not select today's version. For every further addition, retain this short record before integration/distribution:

1. **Identity and purpose:** component/asset name, author/provider, exact version or commit, primary source URL, acquisition date, original and shipped SHA-256, intended use and destination paths. Include transitive components and derivative ancestry.
2. **Actual terms:** inspect the selected revision's primary license/permission text and retain it; record attribution, modification notices, source-offer or other applicable conditions, and a reviewed compatibility decision for the intended distribution and the owner's eventual project-license choice. Record unresolved items against the affected component/use.
3. **Build/runtime boundary:** state whether it is system-provided, fetched only by CI, vendored source, statically linked, dynamically linked or copied into the package. Review the actual runtime files included; naming an SDK or passing a build does not complete this record. The VST3 foundation and later SDL2/DejaVu standalone selection have their own exact records; future additions need equivalent review.
4. **Recordings and pictures:** separately record permission to access and capture the instrument/location and permission to store, analyze, derive models from and redistribute the resulting masters/derivatives. Identify recorder/photographer, operator/session and any included performances or other third-party material. Physical access permission is not a software license; an SDK license does not cover a recording or photograph. [Acquisition admission](CAPTURE_PROTOCOL.md)
5. **Fonts and UI assets:** record each actual font/image license, creator, version, embedding/distribution scope and alterations; preserve required credit and modification history. An atlas reference or an absent original notice cannot substitute for the acquired file's record.
6. **Final payload:** enumerate staged files and hashes, include the applicable notices/license texts, check for unintended scans/source trees/captures, and retain the manifest with build/test identities. Resolve the owner's project-license choice and affected PDF/asset permissions for the proposed use; do not mark those questions complete because this inventory exists.

The retained demo WAV is 768,044 bytes, SHA-256
`9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd`.
Its package retains original inputs, logs and independent reports; all audio is
synthetic nominal-engine output. The exact package inventory and provenance
limits are in its linked README. At that historical checkpoint, the addition did not change its eight-file
local install payload. The current 23-file layout and actual native development
artifacts are described above; their existence does not grant redistribution
permission for unrelated project or research material.


## Standalone dependency update — 2026-11-13

The independent native adapter introduces explicitly acquired, locked SDL2
2.32.10 and source-controlled DejaVu 2.37 font inputs. Exact source/license/font
hashes and authoring dependencies are retained in
[STANDALONE_DEPENDENCY.md](STANDALONE_DEPENDENCY.md) and
[STANDALONE_FONTS.md](STANDALONE_FONTS.md). The
[third-party notices](../THIRD_PARTY_NOTICES.md) retain the SDL2 primary license,
bundled yuv2rgb notice, selected HIDAPI BSD option and conditional Sun libm
fallback permission notice, and point to the complete DejaVu notice. These
secondary notices were added after review of the actual pinned source and a
linked yuv2rgb implementation in the Linux executable. Platform-selected system
and transitive runtime contents still require their own exact payload review.

SDL2 is a static optional native build target, while system audio/window and
C/C++ runtime linkage remains platform-specific. The generated glyph header
requires neither source font files nor a font rasterizer at runtime. The nine-file
standalone component accompanies the executable with the combined notices and
separate primary SDL2/DejaVu texts,
a model-scope description and actual runtime-dependency inventory. Building or
staging an unsigned prototype does not select the missing project-wide license,
clear supplied research/branding rights or qualify signed public distribution.
