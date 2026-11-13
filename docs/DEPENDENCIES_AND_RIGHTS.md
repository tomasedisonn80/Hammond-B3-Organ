# Dependencies, distributed material and rights handoff

**Review date: 2026-11-13; scope: wave-08 working tree based on `7c2ad20`.** This inventory records actual files and configured outputs, including the new factory/capture records and local-install rules. The later integration update includes Agent 50's retained nominal demo generated at `6c3dd8b`. It does not grant rights or choose a project license. No project `LICENSE` existed at baseline or at this review.

Evidence: tracked plus proposed nonignored files, C++ includes, Python imports, [CMake](../CMakeLists.txt), [CI workflow](../.github/workflows/ci.yml), [source manifest](research/source-manifest.json), [source-rights record](research/RIGHTS_AND_SOURCES.md), and the linked primary license files below. Recheck the final staged payload when creating a release; this is not a claim about an uninspected future archive.

## Distribution boundaries

| Boundary | Actual contents / consequence |
| --- | --- |
| Repository/source archive | Project C++ headers/source, Python tools/tests, build configuration, original documentation, reconstructed/proposed JSON, factual CSVs, text event fixtures, and the supplied atlas PDF. The imported SplitMix64 routine is identified below. No SDK/framework source tree, recorded audio, standalone font, extracted atlas image or additional manual PDF was found among tracked/proposed files. |
| Local `OfflineTools` install | Exactly eight configured files: `bin/hammond_render` (`.exe` on Windows), `share/hammond-b3-organ/nominal.b3p`, and `fixtures/catalog-v1.json` plus its five `.events` files. See the [exact layout](OFFLINE_INSTALL.md). The atlas, CSVs, Python, core archive/headers and toolchain libraries are not copied by these rules. |
| CI execution | GitHub fetches the three pinned actions below; setup-python selects Python `3.12`; hosted images supply compilers/CMake and platform tools. Their implementation payloads are not vendored into the repository or local install. Current uploads are named logs/cache/configuration diagnostics, not application packages; see [CI](CI.md). |
| Generated outputs | `.b3p` profiles and WAV/evidence bundles are generated from declared project inputs. The [five fixture scores](../examples/README.md) contain original synthetic gestures and no recorded samples. The retained [four-second dry demo](../examples/rendered/nominal-two-manual-v1/README.md) adds one generated WAV and its compiled-profile/evidence bundle; no executable or hardware recording is included. A shared render must retain its actual input/output identities and synthetic, nominal-engine description. |

The local install currently stages neither `THIRD_PARTY_NOTICES.md` nor this inventory. It is a tested local layout, not a completed redistribution package. Packaging work must carry applicable notices into the selected output and inventory any compiler/OS runtime files actually bundled; the C++ executable still requires a compatible platform/runtime. Python is used to build the profile and run tooling, not to execute the installed renderer. [Install contract](OFFLINE_INSTALL.md)

## Software dependencies actually used

| Component | Current role and provenance | Current distribution treatment |
| --- | --- | --- |
| C++20 and its standard library | `src/`, `include/hammond/`, C++ CLI/benchmark/tests use standard headers and project headers. `hammond_core` is an internal static target; consumers link it. | Zero external runtime audio, GUI or plugin-SDK dependencies. No third-party framework/library source is vendored. This does not mean zero OS/compiler-runtime dependencies. |
| Python 3.10+ | Profile compiler, evidence/validation tools and Python tests use the standard library and local project modules. The apparent nonstdlib import `analyze_wav` resolves to `tools/analyze_wav.py`. | No pip dependencies, copied interpreter or Python package tree. CI selects 3.12; exact patch/runtime builds remain environment-specific. |
| CMake/CTest 3.21+ | Build/profile generation and test orchestration; CMake modules come from the installed toolchain. | No `FetchContent`/`ExternalProject`, downloaded audio/GUI dependency, or bundled CMake distribution. |
| SplitMix64 | `src/TonewheelBank.cpp::next_phase_bits` adapts the 2015 Sebastiano Vigna reference, using caller-owned state. Primary source: [splitmix.c](https://prng.di.unimi.it/splitmix.c), inspected 2026-11-13. | The primary source states a worldwide public-domain dedication to the extent possible under law, a permissive use/copy/modify/distribute grant, and an as-is disclaimer. Attribution and a linked terms summary are retained in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md). No separate upstream file is vendored. |

No universal license is assigned here to GCC/libstdc++, Clang/libc++, MSVC/UCRT, Python, CMake or hosted runner images. Select and inspect exact versions and bundled runtime payloads before making a binary-distribution claim. Tool availability and a CI pass do not resolve that package-specific review.

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

No VST3 SDK, GUI framework or audio-device library is selected or present. The atlas's historical SDK/framework licensing observations do not select today's version. For a future addition, retain this short record before integration/distribution:

1. **Identity and purpose:** component/asset name, author/provider, exact version or commit, primary source URL, acquisition date, original and shipped SHA-256, intended use and destination paths. Include transitive components and derivative ancestry.
2. **Actual terms:** inspect the selected revision's primary license/permission text and retain it; record attribution, modification notices, source-offer or other applicable conditions, and a reviewed compatibility decision for the intended distribution and the owner's eventual project-license choice. Record unresolved items against the affected component/use.
3. **Build/runtime boundary:** state whether it is system-provided, fetched only by CI, vendored source, statically linked, dynamically linked or copied into the package. Review the actual runtime files included; naming an SDK or passing a build does not complete this record. VST3/GUI/device choices remain **not selected** here.
4. **Recordings and pictures:** separately record permission to access and capture the instrument/location and permission to store, analyze, derive models from and redistribute the resulting masters/derivatives. Identify recorder/photographer, operator/session and any included performances or other third-party material. Physical access permission is not a software license; an SDK license does not cover a recording or photograph. [Acquisition admission](CAPTURE_PROTOCOL.md)
5. **Fonts and UI assets:** record each actual font/image license, creator, version, embedding/distribution scope and alterations; preserve required credit and modification history. An atlas reference or an absent original notice cannot substitute for the acquired file's record.
6. **Final payload:** enumerate staged files and hashes, include the applicable notices/license texts, check for unintended scans/source trees/captures, and retain the manifest with build/test identities. Resolve the owner's project-license choice and affected PDF/asset permissions for the proposed use; do not mark those questions complete because this inventory exists.

The retained demo WAV is 768,044 bytes, SHA-256
`9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd`.
Its package retains original inputs, logs and independent reports; all audio is
synthetic nominal-engine output. The exact package inventory and provenance
limits are in its linked README. This addition does not change the eight-file
local install payload.
