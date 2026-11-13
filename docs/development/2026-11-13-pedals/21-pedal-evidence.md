# Assignment 21 — versioned pedal render evidence

Owner: /root/w04_a21_pedal_evidence

Wave: 4 of 10. Assignment: 21 of 60. Scope complete; integration and publication
belong to `/root`.

## Owned changes

- `tools/render_fixture.py`: current producer schema 3, two-digit initial pedal
  registration, four strict pedal commands, exact 28-string invocation and
  independent checks of thirteen additional renderer identity fields.
- `tools/verify_render.py`: strict three-version consumer, independently pinned
  map/reference hashes and nominal transfer, current pedal grammar and preserved
  original schema-1/2 field sets, argument order and command restrictions.
- `tests/test_pedal_render_evidence.py`: independent contract expectations,
  real renderer/PCM checks, unchanged historical bundles and adversarial
  evidence mutations.
- `docs/PEDAL_RENDER_EVIDENCE.md`: complete current version contract, exact
  numeric/string representation, source hashes, historical policy and limits.
- This assignment note.

No other files were edited. In particular, renderer implementation, existing test
suites, CMake, shared status documents, assignment manifest and historical
bundles remained outside this assignment's ownership. No commit or push was
performed by this worker.

## Agreed interface and evidence basis

Root approved the schema and field set before implementation. Assignment 20
owns the native renderer and froze it before this worker built a coherent test
source. Both sides use the four exact score verbs `pedal_on`, `pedal_off`,
`pedal_drawbar` and `pedal_all_notes_off`, each with canonical `lower` in the
unchanged five-field score format. Initial `--pedal-drawbars NN` defaults to
`00`; it follows `--drawbars` and its value in the wrapper's complete argument
vector. There are no extra state-file flags in this scope.

The current manifest has fourteen parameter fields. Current renderer metrics
have thirty-one flat scalar fields: eighteen existing names, integer render
version 3, and thirteen new names. New names declare routing, voice, gain,
contact policy, map ID, raw/canonical map hashes, both reference CSV hashes,
the canonical numerator matrix `4,2,1,1;1,4,2,1`, integer denominator eight for
matrix/gain, and the all-200-unit-positive weight policy. The voice identity
versions that exact chosen rational representation. Values come from
[the adopted contract](../../PEDAL_INTEGRATION_CONTRACT.md), unchanged
`data/pedal-map.json` and both retained pedal CSVs, never from an invented
physical transfer.

The producer and consumer retain separate literal expectations; the consumer
does not import the producer, execute a renderer, or trust one metadata copy
as the other copy's oracle. Its checks still do not authenticate the process,
establish source/build association, replay audio, or prove instrument fidelity.

Schema-1/2 retained bundles remain valid only under their exact old contracts.
They reject all new pedal commands, parameters and metrics. New production
always writes schema 3 and fails its metrics gate if actual renderer stdout
does not satisfy version 3. No old bundle or its WAV is migrated in place.

## Coherent source and native build

Used `/workspace/scratch/f364bc93d920/a21-source`, copied from root's frozen
wave-3 archive tree `24f80c3e8405fa0a49500a080967279e615a9b97`, then overlaid only
assignment 20's frozen `tools/render.cpp` and this assignment's two Python tools
and new test. Concurrent ownership/input files were excluded. The binary and
all its headers were built from that one source. Exact commands:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  -S /workspace/scratch/f364bc93d920/a21-source \
  -B /workspace/scratch/f364bc93d920/build-a21-evidence \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  --build /workspace/scratch/f364bc93d920/build-a21-evidence \
  --target hammond_render -j 4
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/build-a21-evidence \
  -R '^python_test_pedal_render_evidence$' --output-on-failure
```

Toolchain: GCC 14.2.0, CMake 3.31.6, Python 3.12.14, Linux Release with the
project's warnings-as-errors configuration. Configuration and native build
succeeded. Final focused result: **1/1 CTest passed, 17 Python methods, zero
failures or skips, 1.41 seconds**. Python's method-run interval was 1.202 seconds;
neither interval is an audio deadline measurement.

The first focused invocation passed sixteen methods and exposed one error in
the new test's interception helper: it attempted to parse Git metadata stdout
as renderer JSON because the wrapper shares `_invoke` between both commands.
The helper was narrowed to calls of the actual renderer path, and the complete
17-method suite then passed. No producer, verifier or native runtime repair was
needed for that failure. The corrected test was copied into the same coherent
source before the final invocation.

## Actual exercised checks

| Executed scope | Result |
| --- | --- |
| Actual renderer invocations | 13, including one deliberate post-render stdout mutation used to test rejection |
| All 25 pedal IDs | Real scores at 44.1, 48 and 96 kHz with initial registrations `10`, `01` and `12`: nine successful evidence bundles |
| Retained source identity | Raw/canonical map and both CSV hashes recomputed directly from source bytes and matched with actual native stdout |
| Current schema | Exact fourteen parameters, thirty-one metric fields, 28-string argv, CRLF/BOM score byte preservation and actual event count |
| PCM evidence | Nonzero pedal signal, exact silence after separate pedal panic, stereo identity, independent integer sum of squares, peak and raw WAV hash |
| Legacy arithmetic example | Muted held pedals preserve the actual manual WAV bytes for the tested score |
| Parser boundaries | All pedal IDs, both mixture indices/all nine positions, zero-velocity release, value spellings, 1,024 ties admitted and 1,025 rejected |
| Invalid inputs | Canonical-manual, ID, index, velocity, finite-number and registration failures reject before directory creation or process launch |
| Genuine historical bundles | Both retained schema-1 and schema-2 demo bundles verify; all bundle file hashes remain unchanged |
| Full-bundle mutation rejection | 80 cases, including synchronized stdout/manifest changes with recomputed artifact hashes, missing fields, wrong types, matrix changes, argv/parameter disagreement, old-version pedal injection, mixed versions, failed producer output and unexpected files |
| Publication behavior | Existing result directory and sentinel bytes preserved; malformed CLI option, duplicate flag and abbreviation reject |

The 80 rejection cases are full consumer calls. Separate direct parser cases
are additional and are not counted as full-bundle verifications. These are
software consistency/admission checks. The numerical pedal bus/voice oracle
and phase behavior are qualified by the separate Engine assignments, and
broader current-versus-baseline PCM qualification remains a later worker's gate.

## Frozen identities

At handoff, all four overlaid executable-source/tool/test files still match
their tested coherent copies byte for byte:

| File | SHA-256 |
| --- | --- |
| `tools/render.cpp` (assignment 20) | `b8c9f631575ffdd6e198f4811e8add1b301534ca709654aaad1078ec235d08b7` |
| `tools/render_fixture.py` | `f8da8a3a5633eb4d28e32a9e607ff579f188c520a89ae84dbc0c03684ccadcb1` |
| `tools/verify_render.py` | `0f212fd56423de617953be200bdfeacfeb807a3b6e280c8f0576242d79fd0539` |
| `tests/test_pedal_render_evidence.py` | `028c0d8b66e639c21aee2a38d67a884cc19bdbd0dd887deef4f087c0b233cd9a` |
| Built Linux `hammond_render` | `42e4373f6ea80eb0c87238b009283b729e89d71858fc73085831069e84f79d59` |

AST parsing and owned-file `git diff --check` passed. The test's normal temporary
fixtures are removed after execution; results and commands are retained here.
The exact native executable, coherent source and CTest log are task scratch
evidence, not redistributed release artifacts.

## Integration handoff and next step

Assignment 23/root must adapt existing renderer/evidence suites to current
schema 3 without weakening their historical fixtures. Known affected suites
include `test_render_fixture.py`, `test_verify_render.py` and
`test_console_evidence.py`; assignment 20 separately identified other renderer
expectations. In particular, the old consumer test's constructed schema-1
fixture must first remove current pedal metadata, initial registration and its
argv pair, then apply the original console-to-schema-1 transformation. The
genuine committed old bundles remain untouched.

Root should include this new suite in the combined frozen wave-4 gate, inspect
source/contract changes, then publish under the standing authorized workflow.
This worker does not claim a complete repository regression, hosted platform
pass, native-host qualification, measured pedal response or full M3 completion.
