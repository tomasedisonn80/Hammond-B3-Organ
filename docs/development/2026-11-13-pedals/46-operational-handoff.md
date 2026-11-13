# Assignment 46 — operational handoff

Owner: /root/w08_a46_operational_handoff

Wave: 08. Session: 2026-11-13 pedal development. This is one actual newly
dispatched worker in the current sixty-assignment, ten-wave session.

## Scope and inspected identities

Owned only `docs/PEDAL_HANDOFF.md`, `docs/PROJECT_GUIDE.md`, `docs/BUILD.md`,
`docs/CI.md` and this note. No code, test, CMake, install manifest, README,
shared status, assignment manifest or root checkpoint edits were made. No
staging, commit, push or additional worker dispatch was performed; root owns
integration and publication under [AGENTS.md](../../../AGENTS.md).

Read the standing instructions, current status/next steps/development log,
project plan, atlas review, current pedal/native contracts, build/install
definitions, both workflows, source lock and retained demo provenance.
This was an operational review, not an additional whole-PDF reading assignment.
The source basis remains the unchanged 500-page atlas and this session's six
documented full-range readers.

Inspected published HEAD `9403debd754f771bf39bc8cd771ecfd86c0f14d6`, tree
`e2a00f7c270317b0f07be8a467120d8a573bb61a`, plus the root's coherent wave-7
archive at tree `7c3e1e2e93932dfa59f20e2be8ee4ab7f46b8f73` and its already
built Linux Release programs. The retained demo identifies the earlier
published commit `d7b886103f8c9d4649ffa1c35930b79808217a3d`, tree
`018c3897889aaae0070f632981e0c889a35cad30`. These distinct identities were not
collapsed into one purported current-source build.

During this assignment root reported the repaired wave-7 tree
`e50351633caddecc212aef3a934378aeda498870`. Its only changes from the first
frozen tree are `tests/test_install.py`, `tests/test_native_bundle_inventory.py`
and `tools/native_bundle_inventory.py`; the native build inputs are unchanged.
The handoff retains the first full run and the separately executed focused
repair checks, without inventing a new full-suite result.

## Documentation changes

- Added the current operational handoff: identified source, clean-build
  instructions, exact current render/evidence/verification/trace/plot commands,
  explicit local offline/native staging, SDK pins, permanent native identities,
  supported formats/buses/controls, artifact scope and concrete resume gates.
- Updated the general guide's obsolete console-only description, planned-pedal
  language, 43-control/state-2 claims and absent-native wording. It now links
  actual pedal Engine/ownership/evidence and native ABI/behavior, allocation,
  automation and concurrency contracts. Historical examples/reviews/ledgers
  remain linked with their original scope.
- Updated build guidance for the default/optional dependency boundary, all
  offline targets, maintained native input aggregate, configuration-aware
  CTest commands, Unicode CLI path contract and explicit install components.
- Split CI guidance into the ordinary four-job matrix and actual three-job
  native matrix. Retained the historical 26-suite qualification as historical,
  and recorded actual later platform failures, repair evidence and the Windows
  artifact-stage blocker rather than claiming a complete native matrix pass.
- Kept the exact current install payload in its authoritative install document
  and module. After root implemented the plotter integration, inspected its real
  `cmake/InstallHammondTools.cmake` definitions and documented the 23-file scope,
  clearly separating it from the earlier 22-file published checkpoint and the
  still-pending combined wave-8 qualification.

## Executed command verification

Used the already coherent, read-only programs in
`/workspace/scratch/f364bc93d920/checkpoint-w07/build-default`; no build or CTest
invocation modified a root checkpoint. Temporary outputs were written only to
`/workspace/scratch/f364bc93d920/agent46-operational-checks/`.
The actual command arrays and captured stdout/stderr are retained locally there
in `commands.json` and named logs; the durable observations and inputs follow.

Read the generated `CTestTestfile.cmake` files and CMake caches directly.
The SDK-free tree registers **68** ordinary suites. The native tree registers
**76** in total, including these **eight** focused entries:
`hammond_vst3_validator`, `test_native_controller`, `test_native_abi`,
`test_native_behavior`, `test_native_automation`, `test_native_concurrency`,
`test_native_realtime` and `test_native_install`. This is configuration
discovery, not execution. The maintained input target and `check_vst3` regex
match those entries; the Linux-only allocation condition explains the platform
boundary. The generated bundle-path file points to the actual Linux bundle.

Executed five actual executable `--help` commands, actual model and normalized
parameter exports, the 144,000-frame phrase render, all three 48 kHz pedal
traces, independent retained-bundle verification, read-only existing-SDK
verification and inventory `--help`: **14 commands, all exit 0**. Also executed
the stable wave-8 pedal plotter on the generated routing trace: **exit 0**.
The helper's source-tree `render_fixture.py --help` was separately checked
against the documented bundle-generation arguments. No clean/full build, local
install or new native harness execution is claimed by this worker.

The render used the exact documented score and flags:

```sh
./build-release/hammond_render \
  --profile build-release/nominal.b3p \
  --events examples/fixtures/pedals/pedal-phrase-v1.events \
  --output NEW_OUTPUT/pedal-phrase.wav \
  --sample-rate 48000 --frames 144000 --block-size 127 --seed 2704 \
  --drawbars 006400000 --pedal-drawbars 32 --contacts ideal \
  --percussion off --percussion-volume normal --percussion-decay slow \
  --fail-on-clip
```

For the actual run, the executable/profile paths above were the absolute
wave-7 build paths and `NEW_OUTPUT` was the new temporary directory named
above. It produced **576,044 bytes**, SHA-256
`a3d1958189e811b8e353a75380d380016db5286eb08a2005626d95df64dde6f1`, exactly
matching the retained wave-6 demo WAV. That is an observed Linux cross-check of
these two source snapshots, not a cross-platform determinism guarantee.

The parameter export contains exactly **45** records, diagnostic schema **2**
and registry schema **3**. Its scope is `sdk-free-core-parameter-mapping`;
`host_exports_verified` and `native_host_curves_verified` are both false.
The revised instructions explain these as the diagnostic tool's limited evidence
scope and direct native claims to the actual module tests.

Each `hammond_pedal_trace` invocation used the coherent compiled profile,
`--sample-rate 48000 --seed 0` and one of `unmute`, `overlap`, `routing` with
a fresh output. The routing CSV is **2,427,951 bytes**, SHA-256
`3ff70b36b23e012112b6038cd450b6716d0fa1d32a0f18579e8578cad0b89374`.
After coordination with assignment 45, its frozen plotter SHA-256
`45b28978924e88ac09b95bc6e5c9671e2b2f5059f9bd79df47565e8659f10f15`
accepted that actual CSV using the documented `--input` / `--output` interface.
The resulting SVG is **197,130 bytes**, SHA-256
`c9cff420597e862644bbc8b2f68080757c1c1a1c8c192dc3118341e97764a255`.
This worker checked successful conversion and identities; assignment 45 owns
visual inspection and the independent plotter tests.

`tools/verify_render.py examples/demos/pedal-phrase-v1/bundle` accepted schema 3
and six artifacts plus the manifest. It matched the present recorded renderer,
left authentication/source-build association `not_established`, and performed
no replay. This worker's separate direct render above does not change the
verifier's verdict. `tools/acquire_vst3_sdk.py --verify-existing` accepted the
actual external checkout, all four module pins, five primary license hashes
and embedded parser identity with `network_used: false`.

## Documentation verification

`git diff --check` passed for the owned files. All **186** local Markdown link
targets in the five owned files resolved. `python3 -B tools/check_repository.py
--json` passed with zero errors: 285 Markdown files, 1,725 local links and the
unchanged 21,248,265-byte PDF identity were checked in that observed working
tree. Its 60-note count is explicitly the original session's historical scope;
it does not validate the new pedal session's assignment total. A final direct
whole-file comparison confirmed the generated phrase WAV equals the retained
demo bytes. Local `git rev-parse HEAD HEAD^{tree}` confirmed the published
wave-7 identities reported below.

## Independent Windows inventory review

Reviewed `_walk`, per-file hashing and final stability comparison without editing
the inventory tool. Inspected the official
[CPython 3.12.10 Windows implementation](https://github.com/python/cpython/blob/v3.12.10/Modules/posixmodule.c),
specifically `find_data_to_file_info`, `DirEntry_from_find_data`,
`DirEntry_get_lstat` and `os_DirEntry_stat_impl`.

The source confirms that Windows `entry.stat(follow_symlinks=False)` uses
cached `WIN32_FIND_DATAW` enumeration metadata. It does not perform a fresh path
query. `find_data_to_file_info` zero-initializes its struct, so uninitialized
fields are **not** a supported diagnosis. Enumeration also lacks the complete
file identity supplied by fresh path metadata. Recommended fresh `path.lstat()`
for both walks while retaining full same-API signatures, type/symlink rejection,
per-file identity/hash checks and bounded differing-field diagnostics.

This supports the repair mechanism and avoids weakening stability checks.
The failed pre-diagnostic hosted logs did not identify which field changed, so
the review does not claim a directly captured exact cause or an observed Windows
repair pass. Sent the concrete source-backed assessment to root. Root owns its
implementation, regression tests and new hosted qualification.

## Integrated evidence received from root

The first wave-7 ordinary run passed **67/68** in **70.98 seconds**; the sole
failure was an install assertion still expecting diagnostic schema 1 after the
intentional schema-2 metadata change. All **8/8** focused native suites passed
in **6.68 seconds**, with no failed/skipped tests. The repaired tree's two install
methods then passed in **3.067 seconds**, and its 19 inventory methods passed
in **0.203 seconds**, using the original configured CTest environment and unchanged
build inputs. These are root's integration observations, not this worker's runs.
No new full 68/68 run was claimed at this point.

Root subsequently published and fetched wave 7 as
`7fb9b6121b729f46a9e18d80e8620eb21dc0847b`, tree
`19239e05f6c5219b50d3f398ba9a6eb3acc2a1ac`, and confirmed exact local/remote
identity. Only six Markdown result files differ from the repaired tree above;
the historical 42-complete assignment manifest remained frozen. Core run
43415692328 and native run 43415692247 were queued at that observation. The
handoff and CI page link those actual runs without inventing their outcomes.

Published repair `9403debd…` had actual four-suite native passes on all three
platforms, but Windows failed its later artifact inventory. Core Windows passed
66/67 suites and failed two synthetic cases in the inventory suite. Complete
Linux/macOS native jobs and Linux/macOS/sanitizer core jobs succeeded. The docs
retain that separation and link the exact runs and portability review.

## Limitations and next gate

The commands were checked against real interfaces, discovered tests, current
build/install definitions and coherent executables. This documentation work did
not repeat a full clean build, install into a prefix, execute Windows/macOS,
run TSAN or qualify a DAW/device. File-count claims remain tied to the actual
selected install manifest. Root's now-implemented 23-file plotter extension was
inspected in the real install module and tests; its combined wave-8 gate remains
pending at this note.

Root should observe every affected job on the newly published wave-7 source,
including Windows inventory and final bundle artifacts. Integrate
the retained demo, its independent replay, plotter and install extension, then
complete the new session's remaining actual assignments and independent final
reviews. Preserve exact source identities and record later evidence in status,
next steps and the session ledger. Full M3 physical behavior, M4 numerical/model
work, actual acquisitions, DAW/device scheduling, accessible UI, signing and
rights remain explicit separate product gates.
