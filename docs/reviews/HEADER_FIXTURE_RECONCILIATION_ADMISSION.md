# Header fixture reconciliation admission

**A45, 17 November 2026 UTC: admit precisely the two reviewed, value-preserving
Windows fixture repairs.** Preserve the published cast form during reconciliation.
This admission concerns source identity; it supplies no new H1 numerical,
native, visual, timing or platform result.

## Concrete overlap and exact identities

Published source `03c70c103a4a0dd72b323529416b909c19a4e139` independently fixes
the same two integer-to-float assignments on line 156 that this session's
[A18 repair](../development/2026-11-16-console-completion/notes/A18.md) fixes
with float literals. Its active
`apps/standalone/native_tests/test_standalone_header_statistics.py` checks the
cast fixture's whole-file digest before and after native execution. Replacing
that source with the literal form would violate its existing pin.

| Complete fixture form | SHA-256 |
| --- | --- |
| Original genuine baseline | `a6b65d06067d8941e44ef8680f309433a3c82ce1d6bd54d6f3f5bf8d4bde82d2` |
| A18 float literals | `1e5ced9f7644506863a514ee06b452601b3861ab2e581c6dff7e67c5cf7c275d` |
| Published explicit float casts | `96149cf482ad0a57512257a519b89198113f21b06c33b073b2861e13349d1809` |

Read-only inspection of immutable Git blobs confirms that each repaired file
differs from the original by exactly one complete line. Reversing that line
reproduces every original byte. The literal form adds `.0F` to 1920, 1400, 820
and 1080; the other wraps each unchanged conditional expression in
`static_cast<float>(...)`. All four integers are exactly representable in
binary32. Dimensions, case selection, assertions and warning policy remain
unchanged.

## Narrow admission and retained baseline

The [comparator](../../tools/compare_header_material.py) retains
`PINNED[FIXTURE]` and the original comparator digest
`ff3e9015364c1a773bfb8ea90a0138eb9df5f2b03075e49dc8ea4457b76b5760`.
Current admission first requires one of the two complete repaired-file hashes.
It then requires exactly one matching complete line, no original or alternate
repair line, and the original whole-file hash after reversal. Substituting a
new current hash alone cannot admit another edit, relocated line, partial
repair, mixed syntax or malformed source.

Runtime metadata records the actual `current_fixture_sha256`, its
`current_fixture_repair`, both `reviewed_current_fixture_sha256` identities,
and the distinct original baseline identities. The genuine-baseline supplement
must still name the original fixture, comparator and before painter; retained
fixture, object, executable, input and receipt checks remain required.

Comparison against the preserved pre-A45 source finds **56 of 58 existing
function/class definitions unchanged**. Only the transition function changes
behavior; `baseline_inputs` changes its returned explanation alone. Every
existing top-level assignment remains identical, including all original pins,
thresholds, geometry and protocol bounds. Static/native entry checks and all
numerical, support, state and build-validation logic are unchanged.

## Executed evidence and limits

The [focused tests](../../tests/test_compare_header_material.py) pass **17
methods / 56 refusal cases**, using:

```sh
python3 -S -B tests/test_compare_header_material.py -v
```

All nine original methods and their 22 refusal cases remain. Added coverage
constructs both complete repairs deterministically, admits both against the
original baseline, checks actual runtime identity, and rejects mixed repairs,
malformed/duplicate/commented lines, changed values, relocated repairs,
unrelated changes after attempted repinning, substituted baseline/current
identities, and changed UiModel/main sources. Tests require neither Git nor
network access. Baseline file identities are explicitly simulated; historical
binaries are not independently revalidated.

The single run used the literal checkout and completed in 0.565 seconds as
reported by unittest. Root subsequently selected the cast fixture; that
post-run source observation is separate. The
[receipt](../development/2026-11-16-console-completion/reports/A45-header-transition.json)
retains the exact pre-A45 tool/test bytes, hashes, complete successful log,
source identities, immutable remote comparison and preservation analysis.

Historical H1/T3 UiModel/main pins remain binding, as described in the
[portability admission](CONSOLE_PORTABILITY_ADMISSION.md). This repair does not
admit the integrated tree to old static/paired comparisons. Root owns the
merged-source regression and coherent native/platform qualification. A45 ran
no build, native executable, capture, benchmark, static comparison or CTest;
original failures and baseline evidence remain untouched. Literal whole-interface
1:1, physical fidelity, devices, native accessibility and release remain open.
