# Assignment 20 — schema-2 render-evidence producer

Agent: `/root/w04_a20_evidence_producer`

Wave: 04, continuation assignment 20 of 60

Date: 2026-11-13

## Scope and changed files

Read `AGENTS.md`, the current status/plan/handoff, the atlas review, the integrated
[renderer contract](../../RENDER_FORMAT.md), and the existing producer/evidence
contract before changing the assigned files:

- `tools/render_fixture.py`
- `docs/RENDER_EVIDENCE.md`
- This note.

No core, renderer, profile, catalog, tests, shared status files or Git history was
edited by this assignment. Agent 21 independently owns consumer migration and
agent 22 independently owns producer tests. The schema and argument order below
were sent to the integrator and both agents before their integration work.

## Frozen producer contract

The producer now writes manifest `schema_version: 2`. It retains every previous
parameter and adds four required string fields:

| API / manifest name | CLI flag | Allowed values | Default |
| --- | --- | --- | --- |
| `contacts` | `--contacts` | `ideal`, `nominal` | `ideal` |
| `percussion` | `--percussion` | `off`, `second`, `third` | `off` |
| `percussion_volume` | `--percussion-volume` | `normal`, `soft` | `normal` |
| `percussion_decay` | `--percussion-decay` | `slow`, `fast` | `slow` |

All four are optional keyword-only API arguments and strict CLI choices. Invalid
choices or nonstring API values fail before creating an output directory. All
four flags are passed explicitly to the renderer, including defaults. The fixed
26-entry argument vector is:

```text
RENDERER --profile PROFILE_COPY --output WAV --frames FRAMES
  --sample-rate RATE --block-size BLOCK --seed SEED --drawbars DRAWBARS
  --contacts CONTACTS --percussion PERCUSSION
  --percussion-volume VOLUME --percussion-decay DECAY --fail-on-clip
  (--events EVENTS_COPY | --note NOTE)
```

The schematic's final parenthesized choice is exactly one two-element pair.
There are 13 exact parameter keys. Successful renderer metrics retain the prior
15 fields and add exactly `render_schema_version` (integer 2), `contact_model`
(`ideal-contacts-v1` or `nominal-linear-travel-v1`, matched to the parameter), and
`percussion_model` (`shared-readiness-v1`). The source `model` remains
`ideal-shared-sine-v1`; `evidence_status` remains `unmeasured`.

The score parser now accepts `percussion` only for `upper`, unsigned index 0..3,
and a finite parsed numeric value exactly 0 or 1. Indices are enabled, harmonic,
volume and decay. Decimal representations such as `1.0` and `1e0` match the
C++ numeric grammar. Score order and all existing limits remain intact. Score
counts exclude the renderer's separate 13-control initialization flush.

The producer does not rewrite older bundles or accept old unversioned renderer
metrics. The independent consumer must select the strict version-1 or version-2
contract. Failed rendering or validation still retains the applicable raw logs,
parsed metrics and failed manifest, with no successful WAV record. No hashes,
input byte preservation, no-clobber behavior, bounds, PCM checks, or build/Git
limitations were relaxed.

## Executed verification

Built an isolated current-source Release renderer with GNU C++ 14.2.0:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/Hammond-B3-Organ \
  -B /workspace/scratch/60e8291da354/a20-evidence-build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a20-evidence-build \
  --target hammond_render -j 2
```

A focused Python 3.12 smoke used the actual executable and the public API/CLI.
Its temporary evidence remains at
`/workspace/scratch/60e8291da354/a20-evidence-smoke-wmtcrucz` for this session;
permanent tests do not depend on this path.

| Check | Observed result |
| --- | --- |
| Default API bundle, explicit-default API bundle, nominal score bundle, nominal/third/soft/fast CLI bundle | All four succeeded; exact retained JSON, field counts, invocation, integrity flag and PCM comparison checked |
| Default versus explicit defaults | Identical actual WAV SHA-256 |
| Default versus retained legacy renderer, 8192 frames / 48 kHz / block 64 / seed 7 / `008000000` / note 60 | Identical complete WAV bytes; all 15 legacy metrics identical after removing only the three additions |
| CRLF score containing all four percussion controls, including `1.0` and `1e0` | Six score events accepted; retained bytes identical; nominal model selected and nonzero audio |
| Invalid API string/type for every new choice | All 12 rejected before directory creation |
| Lower manual, index 4, fractional value, negative value, and value 2 in percussion score | All five rejected |
| Existing result directory | Rejected; every existing file's hash unchanged |
| Missing render schema, float schema 2.0, wrong contact identity, wrong percussion identity, extra metric field | Five injected captured-summary cases failed at `metrics`; raw injected stdout, actual parsed metrics, return code 0 and failure manifest retained; no successful WAV record |
| Legacy executable supplied to schema-2 producer | Failed at `renderer`; nonzero exit and stderr retained; no WAV published |
| `git diff --check` for assigned files | Passed |

The injected-summary checks intentionally altered the captured JSON after actual
renderer execution. They verify wrapper rejection, not an observed renderer bug.
An initial scratch harness asserted the console flags at an incorrect argument
index and stopped after the first successful bundle. Correcting that harness to
the documented 26-entry order produced the complete passing run above; no
production fix was necessary.

Observed SHA-256 identities:

- Current isolated renderer:
  `b9c0acab7615820091bd7baaf782d894a8b85bb910a2dfba72b84463445d74c9`
- Compiled profile:
  `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`
- Default comparison WAV:
  `10a5d7507d22f2d1bf1403ed0b10eb0d958f98fc3a1da818c0d3038680aba04c`

## Handoff and limits

Agent 22 owns the independent permanent producer regression suite. Agent 21 owns
strict historical/current bundle verification and its regression suite. The
integrator should run those focused suites, then the integration gates against
the exact publication tree, update shared handoff files and publish. This agent
did not run the unrelated full suite, stage files, commit or push.

This evidence is local Linux software evidence. Default byte identity is a
same-toolchain observation at the stated fixture, not a cross-compiler promise.
Git metadata still does not authenticate a binary build. Model names, stable
hashes and PCM consistency establish no physical contact/percussion calibration,
acoustic match, hardware fidelity, callback deadline or host qualification.
