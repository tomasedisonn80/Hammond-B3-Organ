# Assignment 38 — chapel registration control exporter

Actual agent `/root/w07_a38_chapel_controls`; wave 7, assignment 38 of this
session's sixty distinct assignments. Owned only `tools/chapel_controls.py`,
`docs/CHAPEL_CONTROLS.md` and this note. Root owns integration, shared status,
ledger and publication. No commits, core/native/CMake edits or new dependencies.

Read AGENTS, current scope/status/next steps/handoff/log, the M0–M9 plan,
remaining M3 gate, B3CONTROLS3 contract, catalog/compiler public interface and
both independent chapel source reviews. This work consumes their documentary
atlas p122 import; it did not independently inspect factory Table IV or a specimen.

Starting HEAD `219821dfaca6bfee8ba0905993ed8deec7a66396`, tree
`f2db7aee1d45a897273e4e68a2fefc6a2de4d433`, with concurrent unfinished workers.
The new file identities below, rather than that baseline alone, identify this
qualification. Working directory:
`/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.

## Implemented contract

The [guide](../../CHAPEL_CONTROLS.md) freezes CLI, state mapping, public APIs and
publication semantics. Required catalog/output, optional upper/lower keys,
common A/B bank and canonical decimal expression create a fresh complete state.
Selected rows populate the chosen bank; other/disabled banks are zero; omitted
parts are routed off. Pedals are zero and percussion Off/Second/Normal/Slow.
The default bank A and expression 0.75 are explicit audition choices. The digits
become existing nominal drawbar positions, not measured loaded transformer gains.

Catalog admission uses only the public `validate_authoring` function and checks
its own exact wrapper, canonical hash, frozen review identities and byte counts.
Raw authoring metadata is shape-checked, not authenticated without raw input.
Stable bounded nonsymlink regular-file reads, duplicate/type rejection and
preservation of all leading tap zeros are explicit. No physical selector,
percussion-interlock behavior, parameter/state identity or transient history is added.

Publication is same-directory temporary write/flush/fsync followed by atomic
no-clobber hardlink. A preexisting or racing destination survives. The writer
also revalidates canonical audition text; it never silently replaces an existing
saved file. A post-publication temporary-cleanup failure can leave complete new
output while reporting error; ordinary pre-publication failures leave no output.

## Executed checks

Python **3.12.14**, Linux, standard-library probes. Root supplied the actual
compiled catalog `../build-baseline/chapel-catalog.json`. A private scratch
driver under `../a38-evidence/probe.py` exercised real temporary files and CLI
processes; `probe-result.json` retains counts and source/input hashes.

```sh
python3 tools/chapel_controls.py --help
python3 -m py_compile tools/chapel_controls.py
PYTHONDONTWRITEBYTECODE=1 python3 ../a38-evidence/probe.py
```

| Executed scope | Result |
| --- | --- |
| Complete state creation | **205 pass**: all 198 allowed upper/lower/off combinations across A/B, plus seven expression cases; exact written bytes and 73 tokens checked. |
| API rejection | **57 pass**: 20 expression tokens/types; six selection/bank cases; 19 semantic/wrapper/hash/type mutations; 12 malformed/forged text cases. |
| Actual file rejection | **19 pass**: empty/malformed/duplicate/float/nonfinite/oversized/BOM/UTF-8 inputs; missing/directory/symlink/FIFO input; existing/aliased/symlink/dangling/hardlink/directory/missing-parent output. |
| Actual CLI | **14 invocations pass**: help, ordinary and Unicode/space-path success; repeated/unknown/abbreviated/missing/mixed-help/bad expression/bank/no-part/existing-output rejections. |
| Injected publication faults | **2 pass**: real temporary write followed by forced fsync or hardlink failure; no output or leaked owned temporary, original catalog unchanged. |

All probes completed with exit 0. Every published file was byte-identical to its
rendered text. The original catalog and sentinel output survived every rejection.
All owned temporary files were removed in the executed ordinary-failure cases.
Before qualification, code review hardened LF validation against `splitlines`
accepting vertical-tab/form-feed separators; only exact LF reconstruction passes.
No production defect was suppressed and no frozen acceptance threshold changed.

## Exact identities and handoff

| Input/artifact | SHA-256 |
| --- | --- |
| Exporter | `dc390c74ac9af31322d73a116dfd61cd353c6e2ee309a7871c571bca1c3904a8` |
| Public authoring validator/compiler | `fcfdb3342478d8a4369f1080d234515c59a87a0094db522c1f44a8e7ddd61210` |
| Actual 4,837-byte compiled catalog | `f500fa0aaca0ba8652eeede330094deb888f6a516b5c51958fd2381778fb5a91` |
| Both independently frozen CSV inputs | `dc2a8fd4e9750133c982bb42fd6cc7c12908f011154826035bb623f52d8de694` |

Worker 39 received the frozen CLI/API/wrapper/state/publication contract and
exporter hash before independent qualification. Its real C++/application loading,
canonical state byte comparisons and maintained tests are a separate next gate;
these producer probes do not substitute for them. Root will retain executable
and integration evidence under the actual changed source revision.

No Windows/macOS execution, native physical device, gain calibration, latch,
factory timbre, hardware fidelity or production-release result is claimed here.
The tool needs a hardlink-capable output filesystem; no fallback overwrites are
permitted. Future work may add a separately qualified selector/state contract,
primary factory comparison and actual loading/contact/percussion evidence.
