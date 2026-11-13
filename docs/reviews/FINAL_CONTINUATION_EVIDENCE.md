# Final continuation review: offline evidence and publication

Assignment 57 independently reviewed the frozen wave-09 source tree
`805900d2339eb3975019581de5f8469e72e7509f` and the retained nominal-console example.
It found one actionable renderer exit-status defect, reproduced it, and repaired
it with the integrator's authorization. The repaired renderer's full **35-method
suite passes**, and its two-second demo replay remains byte-identical to the
retained WAV. This is a scoped software review, not final publication or hosted
qualification.

## Sources and coherent build identity

The review used the complete frozen `checkpoint-w09-src` archive and its matching
`checkpoint-w09-build` tools. All **338 tracked blobs** were independently checked
against the named Git tree before review and again after the repair work. The
shared frozen source/build were not modified by this assignment. At initial
inspection, repository HEAD and origin/main both named
`2046b9388f6aab1122e37646b2f20199b5c6079f`; the wave-09 work was staged separately.

Read the standing workflow, current handoff, plan, evidence contracts and source
code for the renderer, producer, verifier, trace and plotter. Read complete atlas
pp. **355–360**, whose evidence contracts distinguish byte identity, structural
validation, execution records and physical claims. Those pages' historical
companion validation results are not counted as tests run here. Relevant current
contracts are [rendering](../RENDER_FORMAT.md), [production](../RENDER_EVIDENCE.md),
[independent verification](../RENDER_VERIFICATION.md), [trace](../CONSOLE_TRACE.md)
and [plotting](../CONSOLE_TRACE_PLOTS.md).

The repair was built from a private copy of the exact frozen tree with only these
source/test overlays. After execution, all **336 other tracked blobs** still
matched that base tree exactly; no live headers or older library were mixed.

| Overlay | SHA-256 of tested file |
| --- | --- |
| `tools/render.cpp` | `292d277dd6728ed5241af2ca163a943140c0165711a399c08ce3c82c8168490f` |
| `tests/test_render.py` | `db8411241338a3e9ad51c0b34abd5afb675f179f22416f9ba19a45d0830a8ac7` |

GCC 14.2.0 built the repair in Release with the repository's strict warnings;
Python 3.12.14 ran the tests. The repaired renderer SHA-256 is
`eee31ffdef6275165fe6b492b34e04c9739e7d6bec6199fbebd16901550a129b`.
The compiled profile remains
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
These are observed local build identities, not signed source/build attestation.

## Retained artifacts and independent replay

All **16 entries** in the example's
[provenance inventory](../../examples/rendered/nominal-console-v2/provenance.json)
match their recorded byte counts and SHA-256 values. The inventory intentionally
does not recursively hash its own provenance document or README. All five named
Python tool hashes match the inspected frozen source, and the external original
score equals the bundle's retained `events.txt` exactly. The recorded original
source remains `9a5c99a862daf26a2bab9b05613c98803727a3e7`, distinct from the
reviewed wave-09 tree and the later repaired renderer.

The current independent verifier accepted both genuine retained bundles:

| Bundle | Schema | Frames / rate | Observed result |
| --- | ---: | --- | --- |
| [Nominal console](../../examples/rendered/nominal-console-v2/README.md) | 2 | 96,000 / 48,000 Hz | Six artifacts verified; recorded executable currently matched; replay explicitly not performed by the verifier |
| [Original dry manuals](../../examples/rendered/nominal-two-manual-v1/README.md) | 1 | 192,000 / 48,000 Hz | Six artifacts verified; original executable currently matched; replay explicitly not performed by the verifier |

A separate actual producer invocation used the frozen build, the retained input
profile/score, the same nominal console settings and **block size 257**. It
succeeded, its new bundle passed verification, and all **384,044 WAV bytes**
matched the retained block-size-127 example. A second actual producer invocation
with the repaired renderer repeated that result. Historical manifest paths,
timestamps and executable hashes were not rewritten to make either comparison.

The common WAV SHA-256 is
`3cbfc2a80ee5ed014782d9abe33d5afc2cd7e494f3efdba280939b4d3d8f56b5`.
This is exact local replay evidence for these builds and settings, not a universal
cross-toolchain byte-identity promise. The producer reports zero clipped frames
and channel samples; its float peak/RMS remain separate from serialized PCM.

An additional small independent decoder unpacked the stereo PCM16 bytes directly
and recomputed integer-square RMS, peak, nonzero samples and endpoint counts for
all five retained analysis windows. Both channels are identical. Every retained
peak/RMS and nonzero count agreed exactly with the independent calculation.

| Half-open frame window | PCM peak | PCM RMS | Nonzero samples per channel |
| --- | ---: | ---: | ---: |
| Whole `[0, 96000)` | 0.195281982421875 | 0.03740763139903497 | 83,155 |
| Partial hold `[1920, 4800)` | 0.062408447265625 | 0.035385101888239186 | 2,880 |
| Legato `[26880, 29760)` | 0.0899658203125 | 0.030566215370660146 | 2,878 |
| Lower only `[58560, 62400)` | 0.029998779296875 | 0.021238250349728878 | 3,839 |
| Tail `[88320, 96000)` | 0 | 0 | 0 |

The final 7,680 frames are therefore exactly silent on both channels. PCM endpoint
counts do not independently establish pre-quantization clipping. The retained
crossing-rate pitch estimate was not independently recalculated in this assignment;
its input report and hash were checked, and its qualified interpretation remains
in the example rather than becoming a new physical frequency claim.

## Trace/plot boundary

A fresh actual trace run at 48 kHz, seed zero, `partial`, followed by the current
plotter, reproduced the retained CSV and SVG exactly:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| CSV | 1,194,816 | `dbaa075fcd7bea24b4a61a5df8f55faab53053244ad1e59126ba3f4d80fd89b2` |
| SVG | 117,510 | `76d8583e00977856e54e61fbb1691ff2f7ffb3e2e9f86e0ee5f807e9bdc203a4` |

This trace is **5,760 rows / 120 ms with all sustained drawbars zero**. It uses a
separate built-in schedule from the two-second audio score. At frames 600 and
2000, both position and target are exactly 0.5, while four and five contacts are
closed respectively. Both snapshots have an open physical detector. The first
768 rows retain readiness exactly one. These direct observations support the
README's stated hysteresis and harmonic-before-detector interpretation without
pretending the plot is a visualization of the WAV's score.

The SVG's XML metadata identifies the complete CSV hash, 1,010 time bins,
first/minimum/maximum/last trajectory reduction, minimum/maximum audio reduction
and no contact/target transition reduction. XML inspection found no script,
image, foreign-object or external-link resource. No fresh visual-rendering or
subjective listening claim is made here; the earlier byte-identified visual review
remains the example's stated basis.

The plot parser accepts structure, domains and the stated routing relationships.
It does not reenact the Engine or authenticate a profile, executable, source
instrument or physical capture. CSV metadata calls its authoring digest a
**declared authoring identity**, not a hash calculated over the compiled input.
Those limitations are accurately exposed in the contracts and retained example.

## Publication and bounded failure review

Renderer, trace and plot publication write a complete private sibling file and
use a hard link that refuses an existing destination. The producer instead
claims a new evidence directory with exclusive creation and preserves failed or
incomplete evidence after that point. These are distinct transactions; neither
is a power-failure durability or adversarial concurrent-filesystem guarantee.

Seven actual independent no-clobber probes passed: renderer, trace and plot each
rejected an existing regular file and a dangling symlink; the producer rejected
an existing evidence directory. Every case returned 1, preserved the original
bytes/link target and left no temporary publication residue. Source inspection
confirmed the final hard-link refusal protects against a destination appearing
between preflight and publication. This assignment did not rerun the separate
competing-writer stress case, disk exhaustion simulation or all historical
mutation tests.

The inspected boundaries remain finite: 600 seconds per render at the supported
rates, 16 MiB scores, 262,144 events, 1,024 events at a frame, 4,096 bytes per score
line, 8 MiB/11,520 rows per trace and 1 MiB per SVG. The verifier selects strict
schema-specific fields and grammar; schema 1 does not silently acquire percussion
or partial-key commands. Successful retained verification establishes internal
agreement, not an authenticated origin. The new replay supplies additional local
execution evidence separately.

## Found and repaired: false success on stdout failure

**Before repair:** redirecting the frozen renderer's stdout to a file opened
read-only made both `--help` and a one-frame silent render return **0 with empty
stderr**. The sentinel file stayed unchanged. The render had already published a
complete WAV. Both output paths checked `std::cout` while their small output was
still buffered; the eventual failed flush during process teardown happened after
the return status was chosen.

The new permanent method
`RendererTests.test_help_and_summary_stdout_failures_are_not_success` reproduced
**two failing subcases** against the frozen binary: one test method, 0.007 seconds,
actual exit 0 versus expected 1. It uses the portable read-only-file-descriptor
technique already present in the benchmark suite; it needs no `/dev/full` device
or platform-specific permission assumptions.

**Repair:** explicitly flush the final JSON and help text before inspecting the
stream. A failed write returns status 1 with a stderr diagnostic. The regression
also proves that the stdout sentinel and input profile remain unchanged, that no
temporary files remain, and that the completed one-frame stereo WAV is valid and
silent after a summary failure.

WAV publication still precedes summary delivery. A later stdout error does **not**
roll back or delete the complete artifact. The corrected
[renderer contract](../RENDER_FORMAT.md) documents this boundary and requires both
a successful exit and a valid summary for successful evidence collection.

## Executed repair checks and handoff

The private source/build directories were
`a57-final-evidence/repaired-source` and `a57-final-evidence/repaired-build`
beside the repository. Commands used the available CMake 4.4.4 executable:

```sh
cmake -S REPAIRED_SOURCE -B REPAIRED_BUILD -DCMAKE_BUILD_TYPE=Release
cmake --build REPAIRED_BUILD --parallel 2 --target hammond_render
python3 -B REPAIRED_SOURCE/tests/test_render.py   --renderer REPAIRED_BUILD/hammond_render --profile REPAIRED_BUILD/nominal.b3p   RendererTests.test_help_and_summary_stdout_failures_are_not_success
python3 -B REPAIRED_SOURCE/tests/test_render.py   --renderer REPAIRED_BUILD/hammond_render --profile REPAIRED_BUILD/nominal.b3p
```

| Executed gate | Result |
| --- | --- |
| Strict Release configure/build of the coherent overlay | Passed |
| New focused method, both stdout paths | Passed, 0.006 seconds |
| Complete renderer suite including the new method | **35 passed**, zero skips, 2.174 seconds |
| New actual schema2 producer + independent verifier after repair | Passed; 96,000-frame WAV exactly matches retained bytes |
| Post-execution source identity check | Original 338 blobs unchanged; repaired copy differs only in the two authorized source/test overlays |

The integrator must include the two repaired files and narrow contract correction
in the next coherent full-source gate, then record actual remote publication and
hosted results. This worker ran no broad CTest matrix, native Windows/macOS test,
sanitizer qualification, audio-device/plugin, callback deadline, subjective
listening or physical-fidelity test. The observed stdout defect is repaired in
the frozen handoff files; final integrated/platform qualification remains with
root. No additional actionable evidence or artifact-integrity defect was found
within this review's inspected scope.
