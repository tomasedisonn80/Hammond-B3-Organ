# Console capture JSON numeric admission

Worker: A31, `/root/w06_a31`, wave 6 of the console continuation.
Source base: `9d60dbf462a90fe422fd4e69757fe202264acb7c`.
Working directory: `/workspace/scratch/21cce69f7784/Hammond-B3-Organ`.

**Decision: source-only patch ready for root integration.** The candidate closes
a finite-number admission gap in `read_json`. A31 prepared it under the timing
freeze. Root subsequently reported release of that freeze and review of the
source-ready patch, while retaining application and execution ownership. The
live tool and test files have not been changed by A31, and no test suite, native
process, build, benchmark or capture was run by A31. Execution acceptance is
pending root integration.

## Inspected inputs

Read the complete `AGENTS.md` and M0–M9 `docs/PLAN.md`, the current console
README/checkpoint/actual assignments, the atlas coverage receipt, A15's capture
note and original test receipt, and both complete Python source files. No code
or acceptance evidence was imported from the separate UI-delivery workspace.

| Input | SHA-256 before this work |
| --- | --- |
| `tools/capture_standalone_interface.py` | `975aee1c2261114bb5e899a336567a47b7b3541eac5c75fe1b055244d9c1975f` |
| `tests/test_capture_standalone_interface.py` | `40035a5aceda7b13392d35fd1a81f3e2190d4994e94604273dfc9c65a882fd81` |
| A15 capture note | `f881018419e2b42da6d95ede7deceb76ee6bd1e285ac0dd7d7e288db94c2a19a` |
| A15 original Python test receipt | `5f7e6fcf8430dfa2253f4787f0401a101d00dd165433a11de2cf5c1d6c5f7848` |

The [A15 note](../development/2026-11-16-console-completion/notes/A15.md) and
[receipt](../development/2026-11-16-console-completion/reports/A15-capture-tests.json)
retain their original 39-method execution result and source identity. They do
not qualify this unexecuted candidate.

## Concrete acceptance risk

The existing [decoder](../../tools/capture_standalone_interface.py) rejects the
nonstandard constants `NaN`, `Infinity` and `-Infinity` with `parse_constant`.
Ordinary JSON numeric tokens such as `1e999` use the float conversion path
instead. An out-of-range exponent can therefore produce positive or negative
infinity without invoking that rejection hook.

This matters to the existing evidence assertions. The following is a
source-derived risk analysis, not a newly executed native or synthetic result.
Starting with otherwise valid diagnostics, each listed substitution can satisfy
the shown comparisons. These fields are absent from the returned validation
record, so the later `write_json(..., allow_nan=False)` cannot reject them.

| Diagnostic field | Overflow token | Relevant unchanged comparison |
| --- | --- | --- |
| `runtime.rendered_images` | `1e999` | The count is greater than zero and bounds the finite painted image ordinal from above. |
| `replay.before_shutdown.resolved_sequence` | `1e999` | The resolved sequence is at least the last submitted sequence. |
| `replay.before_shutdown.last_applied_sequence` | `1e999` | The applied sequence is at least the last submitted sequence. |
| `replay.last_submitted_sequence` | `-1e999` | Both finite acknowledgement sequences compare above the negative-infinite threshold. |

The raw diagnostic file is retained and hashed, while the successful validation
record contains selected facts. Hashing those raw bytes does not check the
omitted numeric values. Consequently this is a possible false acceptance of
malformed evidence, not merely a late serialization error. Other fields that
are copied into provenance can instead trigger a late writer failure. None of
this establishes that a native application emitted such a token or that any
retained gallery is invalid. All other ownership, state, delivery and shutdown
assertions remain necessary.

The same `read_json` entry point admits the source qualification report before
capture. The proposed check also rejects nonfinite numbers in its nested or
otherwise unused members, before any qualification facts can be accepted.

## Minimal candidate

The [patch](../development/2026-11-16-console-completion/reports/A31-capture-finite-json.patch)
adds a local `parse_float` hook. It converts the literal with the same built-in
`float` used by the default decoder, checks `math.isfinite`, and returns the
unchanged finite value. Failure raises `ValueError` with the exact literal, for
example `non-finite JSON numeric token: -1e999`. The existing `math` import is
reused; no dependency is added.

Because conversion occurs while JSON is decoded, the check covers values at
every object/array nesting depth and does not depend on which fields the
validator later selects. The patch leaves `parse_constant`, the duplicate-member
hook and the required top-level object intact. It does not change integer
parsing, strings, booleans, null, finite float rounding, subnormals, underflow to
signed zero or finite zero with a large exponent. In particular a token just
above the largest float that rounds to that finite float remains admissible;
this is a check of the decoded value, not an arbitrary decimal exponent limit.

Every production definition outside `read_json` is unchanged. The replay/state
generators, case selection, validation assertions, timeout handling and writer
are untouched. Default replay scale remains 1 and duration 1800 ms; admitted
scales remain integers 1–10. The separate timeout remains finite 4–60 seconds
with default 12. No retry or implicit timing adjustment is added. A15's frozen
six default replay byte checks and all 39 existing test methods and helpers
remain text-identical in the candidate.

This is an on-disk JSON admission fix. The direct programmatic `validate(dict)`
interface is unchanged; callers that bypass `read_json` do not acquire an
additional recursive finiteness check through this patch.

## Focused regression delivery

Six new methods use literal JSON text or copied diagnostic dictionaries written
to temporary test files. They do not modify original fixtures or native evidence.

| Added coverage | Scope |
| --- | --- |
| Positive and negative overflow | Eight numeric spellings, including lowercase/uppercase exponents, the finite-range boundary and long decimal fractions, in three object/array shapes. |
| Finite numeric compatibility | Fifteen literal cases, each at two depths: maximum finite values, values rounding to that maximum, minimum normal, signed subnormals, signed underflow/zero, and ordinary exponent/fraction notation. Float type and exact hexadecimal values, including zero sign, are checked. |
| Other JSON behavior | An exact 401-digit integer, booleans, null, numeric-looking strings, repeated names in separate objects and refusal of six non-object top-level inputs. |
| Duplicate policy | Direct, nested and Unicode-escaped equivalent duplicate member names remain refused. |
| Nonstandard constants | All three previous constant spellings remain refused at direct and nested locations with their existing error. |
| Evidence boundary | Each of the four risky fields above receives a literal overflowing token and must fail during decode before `validate` can admit it. |

The prospective suite has **45 methods: 39 existing plus 6 new**. This is a
source count, not an execution result.

## Source-only verification and handoff

Both candidate Python files parse with `ast.parse`. Comparing the production
AST outside `read_json` found no change; comparing every preexisting test/helper
source segment found exact preservation. The patch applies to the pinned live
files under this non-mutating check:

```sh
git apply --check --whitespace=error docs/development/2026-11-16-console-completion/reports/A31-capture-finite-json.patch
```

Exit code: **0**. The live files retain the two before hashes above. The
[integrity receipt](../development/2026-11-16-console-completion/reports/A31-capture-integrity.json)
binds the patch, candidate hashes and source-only checks.

| Candidate artifact | SHA-256 |
| --- | --- |
| Patch | `7b53d360c1aaa73e6e87a8bdd6a4793127135cbd44e8317e494f1d07e2e2b268` |
| Tool after applying the patch | `ad0b813a378f259e471a9b2901902cc4f75f0ba7feb021e6c3c1c929bdb5b487` |
| Tests after applying the patch | `a4148ccaf5343934bec07068518a3c7e80172f67355ef2757f5ef773814b8a56` |

Root should review and apply the exact patch only after releasing the timing
freeze, verify the candidate identities, then execute:

```sh
python3 -B tests/test_capture_standalone_interface.py -v
```

Retain the actual result, including any failure. No new Python pass, native
capture, visual comparison, platform result or publication is claimed here.
Existing galleries keep their original tool and input identities. Literal
whole-interface 1:1, physical fidelity, real devices, accessibility and the
remaining M0–M9 exits remain open. A31 returns ownership to root at handoff.
