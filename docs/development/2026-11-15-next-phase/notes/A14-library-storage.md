# A14 — registration storage and scope implementation

Assignment `/root/w03_a14`, Wave 3, 15 November 2026. Writable checkout:
`/workspace/scratch/116ca0948095/Hammond-B3-Organ`. Owned files are
`apps/standalone/RegistrationLibrary.h`, `RegistrationLibrary.cpp`,
`apps/standalone/tests/test_standalone_registration_library.cpp`, and this note.
Root owns CMake, the coordinated build, shared navigation and publication. This
worker performed no Git operation, configure/build invocation, child dispatch,
shared-navigation edit or independent remote observation.

## Inputs and implementation boundary

Read the entire AGENTS.md, PLAN.md and reviewed library contract, the active
session entry/checkpoint/assignments, A11 review, current shared recovery headings,
and the existing control snapshot, parser/writer, state-file implementation and
tests. Truncated combined reads were followed by bounded reads of affected
required documents. The contract SHA-256 was verified as
`4760d65b27aa154fd86ee09c2cda87bd30f532874cc1a35c62a5b359889703fa`.
Musical/source scope comes from its explicit whole-registration table and the
retained A05/A06 atlas readings; this worker claims no new complete PDF reading.

The new header was published to root before implementation and directly
coordinated with A15. Storage owns no Session, Engine, UiModel or mutable browser
catalog. A15 retains the single catalog, selection/current references and receipt
authority. `LibraryEntryKey` is an exact ASCII filename; copied entries carry
scope, independent status/reason and optional validated controls. Catalogs carry
generation, complete/failure status, item/candidate counts and warning counts.
The caller supplies generations; post-save refresh returns generation zero for
the model to stamp without silently wrapping its own revision.

Implemented behavior:

- Portable 48-byte ASCII names and separately permissive bounded drafts; reserved
  stems, invalid keys, separators, non-ASCII code units and unknown scopes reject.
  Native filename suffix inspection precedes narrowing. Recognized invalid names
  count toward candidate admission but never become truncated path inputs.
- Complete, deterministic, nonrecursive scans bound all directory items to 512
  plus one sentinel and all recognized candidates to 128 plus one sentinel.
  Failure returns no arbitrary prefix. Missing, empty, invalid and unavailable
  roots are distinct. Same-name/scope ASCII case variants disable every matching
  row; the two different scopes may share a name.
- POSIX reads use `O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC`, verify the opened handle
  with `fstat`, and read at most 16 KiB plus one byte. Windows uses native wide
  `CreateFileW` with `FILE_FLAG_OPEN_REPARSE_POINT`, verifies the same disk handle,
  rejects reparse points/directories and performs the same bounded read. Only
  that copy reaches the unchanged transactional parser. No status-check/ifstream
  race is used for library leaves.
- Registration copies all current fields while preserving latest desired
  expression; Performance copies all fields. Scoped equality ignores expression
  only for Registration. Invalid inputs preserve the destination.
- One-time absolute root resolution follows existing ancestors; a scan creates
  nothing. Explicit Save may create only the missing root when its parent exists.
  Creation paths include root, final destination, staging directory and file.
  Protection checks resolve existing ancestors, check existing identity, compare
  absent suffixes through existing directory identity and fold ASCII names.
  Unresolved links or native conversion/case ambiguity fail conservatively.
  Windows ambiguous trailing-dot/space/stream components are rejected.
- Save performs fresh initial and staged complete scans, reserves one of at most
  32 owned staging directories, writes canonical existing `B3CONTROLS4`, flushes
  and checks close, rechecks protection and capacity, then calls the mandatory
  synchronous final authorizer. Cancellation/throwing retains bounded diagnostics
  and removes only known owned staging paths. POSIX publication uses `link`;
  Windows uses `MoveFileExW` without replace-existing. No replacing fallback exists.
- Successful commit retains exact committed key/scope/controls independently from
  refresh. Cleanup or refresh failures produce `SavedWithWarning`; cleanup never
  recursively removes another occupant. A concurrent exact-path creator is
  preserved by the native commit, including when it appears after final checks.

The ordinary `StateFiles` module, state grammar/writer/readers, 47 parameter
identities and all core/Session/UI paths were not edited by this worker. The
storage guarantees do not isolate hostile replacement of ancestor namespaces,
provide directory-wide atomic case-folded uniqueness, or claim power-loss
durability beyond actual native flush/publication behavior.

## Executed verification and exact evidence

Worker-executed checks were source/document inspection, focused `rg`, SHA-256
inspection and an owned-source whitespace check (zero trailing-whitespace lines).
Root then added the support source and a 30-second test timeout, rebuilt coherent
inputs with strict GCC 14.2 Release flags, and ran the focused CTest selection.
The worker inspected the original build/CTest logs and `LastTest.log` after root
reported completion. No implementation bytes changed after that passing build.

Reproduction commands, coordinated by root, from
`/workspace/scratch/116ca0948095/Hammond-B3-Organ`:

```sh
/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/cmake --build /workspace/scratch/116ca0948095/build-native --target test_standalone_registration_library --parallel 3
/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/ctest --test-dir /workspace/scratch/116ca0948095/build-native -R '^test_standalone_registration_library$' --output-on-failure --no-tests=error
```

Observed result: **1/1 passed, 0.02 seconds**. Original test output:

```text
registration_library checks=167 symlink_unavailable=0
```

The build is Release, native standalone ON, MIDI OFF, VST3 OFF, sanitizers OFF,
with the existing pinned SDL 2.32.10 checkout
`5d249570393f7a37e037abf22cd6012a4cc56a71` reused read-only. This storage test does
not use SDL interaction. Optional SDL dependency-detection messages and the
upstream CMake deprecation warning are retained in the build log; compilation
and linking succeeded under the project's strict warning policy.

The 167 checks cover independent literal field and save-byte oracles, full four
banks/pedals/cancelled fixed memory/routes/percussion, desired-expression
preservation, invalid-input preservation, state4 and historical readers 1–3,
16-KiB exact/overflow, malformed/future/trailing payloads, invalid native names,
stable sorting, changed re-read versus retained preview, case ambiguity and
cross-scope names, symlink/directory/FIFO refusal, missing/invalid roots, exact
128/512 bounds and one-over cases, stale prior-catalog preservation, canonical
save, case-folded collision, protected absent destination/root/ancestor aliases,
authorizer cancellation/exception, a late exact-path winner, synchronized
concurrent creators with exactly one valid winner, owned cleanup, committed
cleanup warning and committed refresh-capacity warning. Symlink and FIFO checks
actually ran on this Linux filesystem; no symlink case was skipped.

| Evidence | SHA-256 |
| --- | --- |
| `apps/standalone/RegistrationLibrary.h` | `6a3d75bd9fac8f70520c0847f8f98f4a33dd013a4d26fbaa3555e966880100eb` |
| `apps/standalone/RegistrationLibrary.cpp` | `bf576627ef534e1db399c45570d0435182c18228852e915bbe7c18a7ea88ac86` |
| `apps/standalone/tests/test_standalone_registration_library.cpp` | `0bbd08a531c17d29b16c2b590c3fce524b2766bb8ae6c4c81d9d52b168966f1b` |
| Root-owned `apps/standalone/CMakeLists.txt` at focused build | `ff149917c14dd1dafb872a4587088ef375fdd40e52e3ae5513bf4e3318e19302` |
| `/workspace/scratch/116ca0948095/a14-build.log` | `b698fb105c0286b2cdee5d10b0011fe42dc11a413236fbb52d871602035a4678` |
| `/workspace/scratch/116ca0948095/a14-ctest.log` | `598cbc4d79e6ba7e562b4be44cb02410a400c910567685f8daaf1ffcf72df988` |
| Built `test_standalone_registration_library` executable | `f26a60800ca04b6c5ee0c6b6cc2a60289332775239c076e9f1332e6faa6073e7` |
| Unchanged `apps/standalone/StateFiles.cpp` | `6cd0d2f26bb2f938781561d278f15f9230e5d84b6052e8554761dc8e96dfd3b6` |
| Unchanged `src/ControlStateIO.cpp` | `3a95b6750fc615b7218da5dd9cb540b30d8a83984374d441f2754c7e66de34fb` |
| Unchanged `include/hammond/ControlState.h` | `aab82b082f9cf77dadf763148cade9eae04f6f7df68b302b1832f21f78034856` |

## Remaining admission

A21 independent storage/race/platform audit is still required. This worker did
not run Windows or macOS compilation/execution, sanitizers, permission-restricted
enumeration, replacement-before-open fault injection, write/flush/close failure
injection, staging-name protection collision injection, exhaustive counter/time
receipt tests, SDL browser/input journeys or the full legacy compatibility suite.
The native branches implement the required primitives but are not platform
acceptance evidence. A15 owns receipt semantics; A17/A18 own browser/app effects.
Root should retain the original compact logs before reusing the shared build's
temporary test report, and run the remaining gates against coherent later inputs.
No whole-interface 1:1, real-device, accessibility, physical-fidelity, callback
deadline, connected rotary audio or release/publication claim follows from this
focused filesystem pass.
