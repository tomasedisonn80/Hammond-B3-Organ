# Streaming/material final source admission

**A43, wave 8, 16 November 2026: admit the published implementation and its
composed local qualification within the declared M3/M9 scope. No source or
evidence-lineage blocker found.** Current-source hosted outcomes and session
closure remain separate gates.

Read complete AGENTS/M0–M9 plan, active ownership/scope/checkpoint, current
handoff/navigation, frozen contracts and A19/A21/A24/A25/A26/A28/A29/A30/A36
admissions. Inspected the complete grid header/implementation and production
painter/build/workflow diff. This review performed no build, test-body rerun,
recapture, source edit, fetch or commit.

## Published source and reproducible verification

The admitted commit is `af2b74760ee195c9497b314a1a29172f5238dd44`, tree
`fb7d9ef7d1fcf24a70395c0671b75eb9c31558d4`, parent
`4aac394cde4da40906b615573a8779aee2d9a37a`. Local Git objects independently
confirm these identities. Root's [publication receipt](../development/2026-11-15-streaming-continuation/reports/implementation-publication.json)
owns the remote API/fetch observation; A43 does not claim another remote fetch.

From the repository root:

```sh
python3 -B docs/development/2026-11-15-streaming-continuation/reports/A43-source-audit.py
```

The [independent audit](../development/2026-11-15-streaming-continuation/reports/A43-source-audit.json)
exits 0 with no errors. All **505 publication inputs** match both their published
Git blobs and working bytes; their path set exactly covers the declared tracked
code/test/tool/data/build scope. All **three workflow hashes** also match.
The audit checks retained log bytes, binaries, 31 published evidence files and
162 unchanged original core/header/plugin/asset/data inputs. These are source
and evidence checks, not a hermetic rebuild attestation.

| Input | SHA-256 |
| --- | --- |
| Publication inventory, decompressed | `8fe23b387457bbe8c7e97962742a4f78c1f8c50bcd4507f530b3d44785232e0e` |
| Grid header | `69c655897b24688873472c559c952d9932f76b0cbed5c3eabd9a9da5b3a5d89f` |
| Grid implementation | `17c1c1cdb8e0edb1c90f098e4e92f351eea4f2c50fab1e2282d3f7f304f9e9bd` |
| Upper-rack painter | `30ac6cec988ec1834f36456d25d1e53113642071d844d53f81b62b3474cf2c37` |
| `.github/workflows/ci.yml` | `bafc57fa861490ffe89f3103c16c0dbe03afcdb35948faa11c25614d161b889f` |
| `.github/workflows/native-vst3.yml` | `2376f41bfd96ff5afa2c821299588de05e5c49221879aef91a82074955649721` |
| `.github/workflows/standalone.yml` | `766fb1c2cb890af1b921ce66b4a58f656a20f5e5ff6e00481fbccb39d8c41961` |

## Qualification lineage, without replacing older observations

The [publication-source receipt](../development/2026-11-15-streaming-continuation/reports/publication-source-qualification.json)
correctly composes three distinct observations:

| Observation | Independently verified retained evidence |
| --- | --- |
| Original coherent run | 131-step all-target rebuild; 210 passing result lines, zero failures, **191.89 s**. Its 505-input raw inventory hash is `85b57e7d333f717c177238066221e812dbc43e3241d9aa758bdf5bf7ee992252`. |
| Post-review coherent run | Ninja reports no work required; 210 passing result lines, zero failures, **191.90 s**. Its distinct 505-input raw inventory hash is `82c29cef72b58ece7058cbc3c136e89cc14eb13aa3a0bb0535772a7d4ab1b250`. Named native probe, app and renderer binaries match the original coherent receipt and current files. |
| Sole later source cleanup | One trailing `0a` removed from `tests/test_causal_contact_grid_resources.cpp`; two affected build steps and **1/1 resource CTest, 0.01 s**. Current resource executable remains byte-identical. No other publication-inventory path changes after the full rerun. |

Only the CLI and differential Python suites differ between the original and
post-review 505-input inventories. The separately bound workflow change adds
the raster fixture as sanitizer gate 22; source inspection preserves the old
21 mappings and budgets. This selection repair is not an executed sanitizer pass.

All **eight** retained missing-probe cases are distinct suite/mode combinations:
unset, empty, missing and nonexecutable for each native-consuming Python suite.
Each receipt records exit 5; every rehashed log contains an explicit
`RuntimeError`, zero executed tests and failure, without a skip. The positive
log contains both configured suites passing **2/2 in 1.80 s**.

The setup receipt's CLI source is
`015a1ef3f5e436a629c7f4885c3f3ed03f4e2b88071cad6bbd7cbc73e6efa6e3`;
its documented later docstring revision becomes published
`cda3e12ed7d5df2ca79999aadf01185c3107a597e62423573b189170ad6710aa`.
The later full suite qualifies that final file. Published differential source
`eb15efa27f30c5ba813fe2d4255de6010d5f3a8da2f8be29b09bcf8de3ede812`
already matches its setup receipt. Current setup bodies still fail closed.
A21/A24's original method/process counts and unset-environment skips retain their
original `d73dc8aa…` / `cf286e63…` test-source identities; no older result is
silently relabeled as a run of modified bytes.

Likewise, A23/A28 resource observations continue to name fixture
`fcb153c854d788f6b97859364088655ed7a81399818246c754e6c9409ab2515c`.
Appending exactly one newline to published fixture
`201a0772a587e2af34f652deb2a29d79ba6d80f51554e52bb5a769554996026d`
reconstructs that historical hash and length. The bridge is the affected build,
test and identical executable
`79a426f9f2855925f982d8130d52accd139c37b252a16420746bcadda49cdacf`.
All other 18 A28 identities still match. Original reports and failures are
preserved; the 192 scopes, zero hooked C++ allocations/frees and 113,056-byte
object remain finite, ABI-specific observations.

## Source supports the bounded M3/M9 claims

The grid enforces three rates, 1–4 keys, nine independent contacts, integer
positions through `2^48`, 4,096 frames and 512 supplied commands per epoch.
Widened unsigned products, quotient/remainder root construction before narrowing,
exact fraction comparison, persistent command anchors and incoming-edge ordering
support the admitted integer-domain argument. Fixed snapshots, 4,608 staged
edges and 36-edge interval batches supply the declared storage structure;
all failure/capacity checks precede caller-output writes and state commit.

Production references to `CausalContactGrid` occur only in its own header and
implementation. The static-archive/probe additions do not introduce an Engine,
standalone or plugin call, waveform, source-phase schedule, converter, filter
or drain. Unchanged original musical source supports the compatibility review;
the separate one-fixture dry-WAV result remains bounded to its original workload.
This is finite trajectory admission, not completion of M3 or live audio.

The painter adds a private default-off material path, opted into only for
`registration_panels[0]` in the existing active wide Dimensional Play path.
Field/grain replace the inset fill between unchanged border/shadow operations
and later children; shared layout, hit geometry, state and audio source remain
unchanged. The helper uses the actual mapped inset, physical clipping and
binary64 evaluation barriers; guards restore scale/color without resetting the
stored viewport, clip or blend. Its 65-column field and fixed 2,048 grain pairs
support bounded work, not an SDL or callback-deadline result.

## Gallery and mask admission survives unrelated test edits

All **117 gallery production inputs**, **13 selected build inputs**, copied
ten-source qualification, capture tool, current app and **57 payload members**
still match. The app remains
`c29495e98148767c0d55cab4adc18a245659cea891deb0f37fa160ea976c3cc1`.
The production aggregate is
`557b032ba9d56ce9e42aa612deb6d6f23d7d60001f4e8199129020b1ddc9de48`;
the selected build aggregate is
`a076e2400b253282414e1a5fa2154ad83c46a9d6eeae471d2d1689c9016eb815`.
Every recorded production input also matches the published Git tree. None of
the three later test-source edits belongs to this production inventory, so
their new hashes do not invalidate unrelated capture inputs.

The original paired report's raw hash remains
`20651ce04553a3cfd1d56c9c8e997765072d3d0223b1b5cc28aff0816cb0bbf9`;
its 96 cases sum to **307,095,606 pixels**. The unchanged
[comparison admission](UPPER_RACK_COMPARISON_ADMISSION.md) owns zero escapes,
37 required exact whole frames, five local screens and retained baseline failures.
The unchanged [gallery admission](UPPER_RACK_GALLERY_ADMISSION.md) owns its
641 checks and direct inspection of twelve genuine application captures.
A43 establishes continuing identity, without repeating either visual admission.
Resource crops still protect zero exterior pixels; runtime meter/counter drift
still distinguishes gallery captures from identical-state raster pairs.
Original BMP bytes remain unavailable; PNGs and conversion receipts remain.

## Remaining gates and handoff

The retained [initial hosted observation](../development/2026-11-15-streaming-continuation/reports/hosted-initial-observation.json)
names this exact commit, three workflows and thirteen jobs, with workflows
in progress and no final conclusion. A43 did not refresh hosted status and
does not promote dispatch, old-source CI, local Release or workflow inspection
to a hosted pass. Root must retain final exact-source platform, sanitizer,
native VST3 and standalone outcomes and reconcile shared publication/status
wording and the actual worker ledger.

Converter/audio contracts, full-organ indefinite capacity, host scheduling,
callback resources/deadlines, physical calibration, real display/input and
semantic accessibility remain open. Literal whole-interface **1:1 remains
unmet and unwaived**. No broader product or earlier-session closure follows
from this scoped source admission.
