# Registration path and input admission review

16 November 2026; A20, independent wave-four review against the
[CLI filesystem contract](../REGISTRATION_CLI_CONTRACT.md),
[starter-pack contract](../STARTER_REGISTRATION_PACK_CONTRACT.md) and
[store contract](../REGISTRATION_LIBRARY_CONTRACT.md). Base HEAD:
`54df95fe343d417dd89bb7a91f85e4f51c08dfe7`. This review admits the narrow source
repair; native qualification and platform observations are recorded separately.

## Observed false refusal

The unchanged first generator-suite failure remains in
[the original compressed log](../development/2026-11-16-preset-library-continuation/reports/w03-generator-tests-first-failure.log.gz),
SHA-256 `102eaba43d8339cbe56953f291c491958782557e3262311e3aef057853df40f8`.
Nineteen of twenty author methods passed. The Unicode-parent method returned
`ProtectedPath`, committed zero files and preserved the destination. Its ASCII
staging ancestor and compiled source-protection ancestor were already distinct.

Before editing, A20 independently ran the existing generator twice from the
writable checkout, with a 30-second subprocess timeout and automatically cleaned
scratch directories inside that checkout. An ASCII destination committed all 24
files and exited 0; a missing child of `café staging` committed none and exited 4.
Both stderr streams were empty. The tested executable SHA-256 was
`6ba8be7b6b1679be8a949d0e75837932818d76a005944c7cd6f0fde5410d8cc2`.
This observation qualifies the pre-edit failure, not the repaired source.

## Narrow proof and preserved protections

`portable_path_compare` previously compared flat native strings. Any mismatched
non-ASCII code unit made the entire comparison uncertain, even when unrelated
ASCII ancestors already established distinction. Giving arbitrary flat-byte
differences priority would be unsafe: Unicode encoding or normalization lengths
can shift subsequent ASCII characters and separators.

The added pass iterates corresponding `std::filesystem::path` components. It
proves distinction only when **both complete components are ASCII** and differ
after the existing ASCII case fold. Component boundaries remain aligned despite
encoding-length differences. Otherwise the original comparison runs unchanged,
including its non-ASCII uncertainty. No Unicode case mapping or normalization is
invented, and different spelling within an uncertain Unicode component is not
promoted to a new proof.

This lexical proof still passes through all existing admission guards:

- `identify_path` resolves existing ancestors and rejects unavailable ancestors,
  unresolved links and ambiguous Windows components.
- Existing paths still receive `filesystem::equivalent` checks; equivalence
  errors remain refusal, including hard-link identity where reachable.
- Equivalent existing ancestors still require distinct reserved suffixes.
- Root, destination, staging directory and staging file receive the same checks,
  including final admission before authorization and no-replace publication.

The patch changes no public signature, save status, control grammar, field,
scope, catalog identity or SDK dependency. It does not add a stronger guarantee
against concurrent hostile namespace replacement than the existing contract.

## Focused regressions

The existing store fixture gains successful missing/existing Unicode-root saves
under an unrelated ASCII sibling, and success beneath an exactly shared Unicode
ancestor. It retains conservative refusal for composed/decomposed and Unicode
case variants with identical case-folded ASCII suffixes. Those refusals occur
before authorization or root creation. Additional cases preserve missing
case-aliased destinations through a directory symlink, existing hard-link bytes
through collision refusal, dangling links and Windows trailing-dot/space/stream
ambiguity. No existing assertion or threshold is removed.

The new `test_control_file_input` directly seeds all four output fields and
checks complete preservation for unavailable, nonregular, oversize and malformed
inputs. It covers exact 16,384-byte success, 16,385-byte refusal, trailing/NUL/
catalog/version failures, successful original-version/byte metadata, migrations
1–3, canonical state4, Unicode paths, leaf-link refusal, permitted ancestor links,
hard links, POSIX FIFO and Windows device/pipe namespace guards. Input bytes
remain unchanged. Link creation failures are explicitly counted.

## Shared-reader review and qualification boundary

Read-only inspection of `tools/ControlFileInput.*` found no required production
change: both platform branches inspect the opened handle, bound reads, check
close, and parse/serialize into a private candidate before replacing the complete
destination. The already admitted header supplies version provenance afterward.
The fixture does not inject interrupted reads, late growth, close failures or
allocation exceptions; their source paths are reviewed, not executed evidence.

Root linked the new fixture to `hammond_control_file_input` with a 30-second
timeout, then successfully rebuilt the five affected targets in the coordinated
Linux Ninja Release build. A20 inspected root's build and test logs and verified
that all three owned source/test hashes below remained unchanged. All six
focused CTests passed in **1.18 seconds**:

| CTest | Result |
| --- | --- |
| `test_control_file_input` | Pass |
| `test_standalone_registration_library` | Pass |
| `python_test_registration_cli` | Pass |
| `python_test_registration_cli_admission` | Pass |
| `python_test_render_controls` | Pass |
| `python_test_starter_registration_generator` | Pass; all 20 methods, including Unicode and exact 24-file regeneration |

The [qualification receipt](../development/2026-11-16-preset-library-continuation/reports/w04-path-qualification.json)
binds these sources, rebuilt executables and compressed original logs.
Root log `w04-path-build.log` has SHA-256
`87f33a732ed195204e8bd3a3a6b6d1a89e941a91682cdaf2cef74cfdf3cc5151`;
`w04-path-tests.log` has SHA-256
`56929cf86f8047f632ea95d3149149e4701ca14ed8f51bfc224ca7e7b5c45c26`.
These are root-executed, worker-inspected results, distinct from A20's pre-edit
reproduction. macOS/Windows execution and forced I/O failures remain unobserved.
The original failed log retains its original bytes and identity.

| Reviewed source | SHA-256 |
| --- | --- |
| `RegistrationLibrary.cpp` | `e45fd2671558e0725468c18b59dc5ef8e7436600910633f73035ce81da4d3a4a` |
| Store test | `841f21c17f6fab449e8ce8ac345cf5af17257a17f5266afe6ffd372708f204cc` |
| Shared-reader test | `ed1df67d1d95f597113139bbefab2b92488b990e2171a86cb309d53227957642` |
| Unchanged shared-reader implementation | `0a174b171dfb3f0253cd6beb12707fda4da5ffb88c898727fb80ca111049cf5d` |
