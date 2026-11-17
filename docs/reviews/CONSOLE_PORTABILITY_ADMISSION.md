# Console portability source admission

**A34, 17 November 2026 UTC: admit continued integration of the inspected
sources; no new blocking C++ portability defect identified.** This is source
inspection, not Windows, macOS or sanitizer qualification. No source patch is
recommended. The inherited H1/T3 source-pin boundary below is a concrete limit
on reusing historical comparison protocols.

The checkout was `/workspace/scratch/21cce69f7784/Hammond-B3-Organ`, HEAD
`9d60dbf462a90fe422fd4e69757fe202264acb7c`; additions and modifications are
identified by the [24-file hash receipt](../development/2026-11-16-console-completion/reports/A34-portability.json),
not by that base commit alone. I read the complete LibraryModel, five new library
tests, P1 fixture and Flat companion; inspected the UiModel/A18 diffs, storage
boundaries, CMake and workflow changes; and checked raw bytes and exact reversals.
I ran **no build, test suite, native process or sanitizer**. Root's retained
[complete native build](../development/2026-11-16-console-completion/reports/integrated-build-result.json)
and [five passing library CTests](../development/2026-11-16-console-completion/reports/library-integrated-result.json)
are separate executed GCC evidence. The wider regression run was still active
when this review was written.

## C++ and filesystem findings

| Boundary | Source finding and admission limit |
| --- | --- |
| Integer width and signedness | LibraryModel checks each issuance counter against its `uint64_t` limit before incrementing and checks `now <= UINT64_MAX - 2000` before deadline addition. Catalog sizes/counts are bounded before addition: at most 128 rows/candidates and 512 directory items. Relative selection widens the pointer difference and full-range `int` delta to `int64_t`, then clamps before converting to `size_t`. This is safe for the matrix's LP64/LLP64 targets. Invalid-name and diagnostic strings are bounded; no locale-dependent character classification is used. |
| PIMPL, ownership and exceptions | The owning `unique_ptr<Impl>` is destroyed out of line after the complete implementation. Copy and move are explicitly deleted. Returned views, entries and intents own strings, vectors and snapshots; no iterator or path handle escapes. Allocating model construction, copy-return and mutating methods are not falsely declared `noexcept`. Pure validation/comparison helpers are nonallocating. The new `UiModel::recall_controls` validates first and uses the existing fixed-size action publisher; its `noexcept` contract adds no allocating operation, saved-baseline write or class data. |
| Five test files | Bounds are expressed with fixed-width integers or `size_t`; full-range selection, saturated counters and deadline overflow are explicitly represented. Float/double bit comparisons use `bit_cast`, not pointer punning or struct padding. The target ABIs use the 32-bit float/64-bit double representation required here; P1 explicitly asserts binary32. The Session oracle's `long double` readiness check uses a numerical tolerance, not an assumption that it is wider than MSVC `double`. No new thread, sleep, native SDK or platform-specific test dependency appears. |
| Paths and collisions | LibraryModel performs no filesystem I/O. The real storage tests use `filesystem::path`, binary streams, native-code-unit staging-prefix checks and `path(u8"caf\u00e9 staging")`; no Unicode parent is narrowed to `string()`. Temporary directories are exclusively reserved with bounded retries. Test expectations do not require case-distinct siblings or a particular temporary-directory spelling. Portable ASCII names and case-fold collision preflight remain shared with RegistrationLibrary. |
| Actual publication boundary | The unchanged storage helper retains native wide Windows paths, ambiguous-component refusal, protected-path identity checks and the conservative Unicode-alias limit. The Unicode test's distinct ASCII `source`/`output` branches respect that limit. Final authorization precedes Windows `MoveFileExW` without replace-existing, or POSIX `link`; late exact-target creation is tested without assuming an overwrite. A copied catalog remains preflight, not filesystem authority. Legacy StateFiles replacement semantics are separate and unchanged. |
| Build isolation | `hammond_standalone_support` includes LibraryModel unconditionally and the five tests enter through the existing `tests/test_*.cpp` glob. SDL and the P1 fixture remain inside `HAMMOND_BUILD_STANDALONE`; RtMidi requires its separate option. The root requires C++20, disables compiler extensions, retains MSVC `/W4 /WX /permissive-` and GCC/Clang/AppleClang conversion/sign/shadow warnings as errors. ASan+UBSan explicitly rejects MSVC/clang-cl. A32 owns the separate SDK-free execution; this row establishes source wiring only. |

## Native fixtures, binary transport and source identity

P1 selects only its fixed case inventory. Checked surface dimensions bound the
largest packed output to **33,928,016 bytes**; conversion to `streamsize` and
`width * 4` stay in range. Float-to-int geometry conversions operate on bounded
finite fixture coordinates. Index/pitch products widen before multiplication.
The 8192 resource case allocates only its 64×64 crop. The fixture includes the real
painter once; CMake does not compile a duplicate painter translation unit.

P1's `--case` path and the capture-only Flat entry both check
`_setmode(_fileno(stdout), _O_BINARY)` before any raw stream output on Windows.
They emit packed RGBA rows without pitch padding or struct serialization.
P1 flushes and checks its stream; the fixed Flat witness declares exactly
**6,293,408 pixel bytes**. These guards are source facts, not executed Windows CRT
proof. The Flat companion is outside the ordinary CMake/CTest target set; its
retained manual build uses `SDL_MAIN_HANDLED`, the pinned benchmark include and
matching libraries. Existing Linux capture receipts do not qualify that companion
on Windows/macOS or establish new timing results.

A18 changes exactly one fixture line: four exactly representable dimension
literals gain `.0F`. Independent byte reversal reproduces the base fixture
SHA-256 `a6b65d06067d8941e44ef8680f309433a3c82ce1d6bd54d6f3f5bf8d4bde82d2`.
The current fixture remains
`1e5ced9f7644506863a514ee06b452601b3861ab2e581c6dff7e67c5cf7c275d`.
The [original Windows C4244/C2220 failure](../development/2026-11-16-console-completion/reports/A18-source-transition.json)
at job `133764382636` is retained; no Windows success is inferred from this repair.

All 24 inspected files currently contain LF text, no CRLF or NUL, and resolve to
`text=auto eol=lf` through [.gitattributes](../../.gitattributes). Binary assets
remain separate; raw `.b3controls` replay evidence has its explicit `-text`
exception. A26's two inserted blocks each occur once and reverse to the complete
original UiModel files. A30 accepts that exact coherent pair only in P1
candidate-only mode. It preserves the original paired pins and genuine binaries.

**Historical protocol boundary:** `compare_header_material.py` inherits the old
UiModel pins from `compare_title_typography.py`. Its full static/paired source
admission therefore refuses the current A26 tree. The focused A18 transition
tests do not claim otherwise. The next H1 session must recover its owner, rebase
the intended source and independently admit an exact source transition and
coherent comparison inputs before rerunning H1/T3 comparisons. Do not repin old
reports or extend A30's P1-only exception. The original LibraryModel oracle
failure, P1 paired-v1 metadata failures and Flat-v1 setup failure are also retained
and hashed in the receipt.

## Remaining concrete qualification

- At the exact published source, observe the existing Windows MSVC x64 core and
  native jobs through compilation, the five library suites, P1 ordinary/numerical
  export gates, corrected header fixture and downstream packaging. The source
  review found no additional concrete `/W4 /WX` blocker.
- Obtain actual AppleClang execution in both existing macOS architectures,
  including the real storage/Unicode/collision tests and native P1 exports.
  Cancellation or an unacquired runner does not execute those gates.
- Execute the existing instrumented native job with its required **37 CTest
  names / 35 binaries**, confirming the five library targets and P1's compiled
  painter/support/core inputs remain instrumented. A configured workflow is not
  a sanitizer pass.
- Keep the Flat companion's Windows/macOS qualification explicitly unrun unless
  separately built and exercised with retained source, library and raw-output
  identities. Apply the H1 source-admission requirement above in its own session.

Root owns acceptance/publication and the complete workflow matrix; this review
does not duplicate or waive it. Browser integration, devices, native accessibility,
physical fidelity and literal whole-interface 1:1 remain separate open gates.

