# Registration CLI implementation admission — A19

16 November 2026. Independent review against the frozen
[CLI contract](../REGISTRATION_CLI_CONTRACT.md), after reading the current
session, standing obligations, complete M0–M9 plan, author tests and the CLI,
shared reader and registration-library source. Base HEAD is
`54df95fe343d417dd89bb7a91f85e4f51c08dfe7`; reviewed additions were uncommitted.

**Disposition: no production defect found in this bounded Linux admission.**
The 14 author methods passed independently; ten additional blackbox methods
passed. This does not close the native fault-seam, macOS/Windows, installation,
or whole-project qualification gates.

## Executed checks

Working directory: `/workspace/scratch/3edffb787db3/Hammond-B3-Organ`.
Python 3.12.14; the root-provided build cache reports Release and C++ compiler
14.2.0. No configure, build, commit, CTest or production edit was performed here.

```sh
HAMMOND_REGISTRATION_EXECUTABLE=/workspace/scratch/3edffb787db3/build-native/hammond_registration python3 -B tests/test_registration_cli.py -v
HAMMOND_REGISTRATION_EXECUTABLE=/workspace/scratch/3edffb787db3/build-native/hammond_registration python3 -B tests/test_registration_cli_admission.py -v
```

The author suite passed **14/14 methods, 76 processes, 0.207 s**. The independent
suite passed **10/10 methods, 46 processes, 0.132 s**, with 15-second per-process
timeouts. Every ordinary result is parsed as strict UTF-8 JSON with duplicate
members/nonfinite constants refused; exactly one LF, no raw CR, all envelope and
nested fields, diagnostic byte bounds, result classification and the 1-MiB report
limit are checked. Closed stdout is exercised separately because its contract
permits no complete stdout object.

The additional cases address concrete gaps in the author suite:

- Eight distinct malformed UTF-8 classes in command and value positions; an
  exactly 4,096-byte multibyte token reaches filesystem admission, while 4,097
  bytes is a usage refusal. ASCII controls are refused, while a valid non-ASCII
  control codepoint remains an admissible path token.
- Malformed import options fail before opening a missing input or creating a
  destination. The documented `./` prefix admits option-shaped file/directory
  names and preserves their exact informational paths.
- Candidate overflow and directory-item overflow block both inspect and
  materialize before selected-entry/current-file admission. Existing destination
  bytes remain identical and no partial rows are exposed.
- Explicit import scope overrides the input suffix. Same-stem Registration and
  Performance entries are unambiguous across scopes; missing/forbidden current
  arguments fail before the current path is opened or destination created.
- Successful materialization retains source-catalog warnings and exits 1 even
  with a clean destination. A later missing-current failure exits 4, retains the
  captured source report and leaves existing output bytes intact.
- A normal ASCII argument reaching a linked ancestor with non-UTF-8, quote,
  backslash and newline bytes reports exact native hexadecimal input/output
  identities in valid single-line JSON.
- One materialization reports two complete 128-row catalogs, each with 127
  invalid rows, without dropping rows or exceeding the report bound.
- Closed stdout overrides help, usage refusal, a warning-bearing materialize
  commit and its subsequent create-only collision with exit 5 and one bounded
  fallback diagnostic. The committed output and all inputs remain byte-identical.

## Source findings and report bound

`parse_arguments` validates byte counts, strict UTF-8, option grammar, names and
keys before mutation. Selected-entry admission requires a complete catalog,
valid exact key, fresh read and full snapshot equality. The final authorizer
rechecks both invocation and resolved input/source identities using full
snapshot equality, including Registration expression. The CLI delegates musical
grammar, scope merge and publication to their existing owners.

The writer's post-publication branch retains `committed_entry`, the actual failed
`refreshed_catalog` and `SavedWithWarning`. `save_outcome` maps that status to
exit 1, and report serialization prefers the committed key/scope. It does not
reinterpret an incomplete refresh as prepublication failure. Before entering the
writer, publication becomes unknown; normal return immediately records the
writer's known result. Unexpected exceptions and emergency reporting preserve
that known/unknown distinction. No retry or committed-output deletion is present.

The report reserves 1 MiB before execution. `Json::raw` checks every append;
encoding failure produces a fixed emergency envelope, while write/flush failure
produces exit 5. POSIX ignores SIGPIPE so this exit remains observable. Diagnostic
repair consumes complete UTF-8 sequences, substitutes U+FFFD for invalid bytes,
then applies the 256-byte bound before JSON escaping.

For admitted values, a conservative source bound is **804,864 bytes**: 257 row
metadata objects at 2,048 bytes each (two 128-row catalogs plus selected entry),
two 16,384-byte canonical strings at worst sixfold JSON escaping, two native
paths at 32,768 encoded bytes each on Windows, and 16,384 bytes for remaining
metadata/diagnostics. Rows have at most 63 key bytes, 48 name bytes and a
256-byte reason; the other row fields are fixed tokens. POSIX paths are smaller.
This is a source argument, not a measured worst-case transport result. The
capacity-catalog test exercises maximum row counts, not forced report overflow.

## Remaining evidence boundaries

No deterministic seam in the supplied CLI executable exposes source mutation,
postcommit cleanup/refresh failure, allocation failure or invalid Windows UTF-16.
The existing native library tests contain authorizer seams for denied/throwing
authorization, cleanup warnings and incomplete committed refreshes; their source
was inspected here, but those native tests were not executed by A19. Root retains
that qualification and any CLI-specific fault-seam follow-up. No timing race was
used to substitute for deterministic evidence. No file-lock, race-immunity,
power-loss durability, Windows/macOS execution, live-control acknowledgment or
physical fidelity is claimed. Root has wired the new test's executable environment;
its coherent affected/full CTest gates remain pending.

## Reviewed identities (SHA-256)

| Input | SHA-256 |
| --- | --- |
| `docs/REGISTRATION_CLI_CONTRACT.md` | `cab55c11a1f211e47e73b18db5f5f33cfd5b3fa2d066361f0842c9ea3b0041fa` |
| `tools/registration.cpp` | `4fbf8f9e9a8c04713ee7aa28e089e02dbd5955ceb38e478673aa1f5da2f37ff3` |
| `tools/ControlFileInput.cpp` | `0a174b171dfb3f0253cd6beb12707fda4da5ffb88c898727fb80ca111049cf5d` |
| `tools/ControlFileInput.h` | `74fe88ed36c8b00b56f3a3f15874f22ec418ce4ea8932995c7829b68c4f02ade` |
| `apps/standalone/RegistrationLibrary.cpp` | `bf576627ef534e1db399c45570d0435182c18228852e915bbe7c18a7ea88ac86` |
| `apps/standalone/RegistrationLibrary.h` | `6a3d75bd9fac8f70520c0847f8f98f4a33dd013a4d26fbaa3555e966880100eb` |
| `src/ControlStateIO.cpp` | `3a95b6750fc615b7218da5dd9cb540b30d8a83984374d441f2754c7e66de34fb` |
| `tests/test_registration_cli.py` | `57bfc35df1fdc46c001417da53ec97965a1e724376b6921cbd0ba1b0876b7c0c` |
| `tests/test_registration_cli_admission.py` | `6ee135cac2a11f230909d851f00c0ab951e7fa2da429f703d0cd1e8ea4fa1974` |
| Supplied `build-native/hammond_registration` | `f7dfe8de955a22bbd412d182729b4fe361661a4fe73dd48246372837ec4831b0` |
