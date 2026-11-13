# Assignment 45 — bounded pedal trace plots

Owner: `/root/w08_a45_pedal_plots`.

## Scope and status

Assignment 45 of the current 60-assignment, 10-wave continuation; wave 8.
Implemented the standalone standard-library pedal CSV→SVG tool, independent
plotter acceptance, public usage/interpretation documentation and three retained
48 kHz SVG examples. No production DSP, trace producer, shared project documents,
CMake, install module or manifest changed in this assignment. Root owns install
integration, coherent combined testing, the continuation ledger, commit and push.
No child commit, push or additional agent was created.

Reviewed `AGENTS.md`, current status/plan/next steps/handoff, the full pedal trace
contract and existing console plot workflow. Re-read atlas pp. 139–144 from the
full extracted PDF: 25 pedals, eight physical contacts, 200 positions including
five disconnected contacts, four buses, shared sources and separately declared
physical unknowns. The plot does not promote the nominal matrix or linear
position law into measured pedal-network behavior.

## Files and runtime contract

- `tools/plot_pedal_trace.py`: exact supported schema/domain/provenance checks,
  eight min/max envelopes, exact registration/contact/manual state transitions,
  complete source-byte SHA-256 and all metadata embedded in standalone SVG,
  bounded memory/file size and atomic no-replacement publication.
- `tests/test_plot_pedal_trace.py`: fifteen fixture/render/publication tests and
  one test executing all nine actual producer scenario/rate pairs.
- `docs/PEDAL_TRACE_PLOTS.md`: reproducible invocation, five-panel interpretation,
  explicit rejection policy, reduction math, limitations and next gates.
- `docs/examples/pedal-traces/`: three precise SVG source artifacts; total
  603,020 bytes. CSVs and rasterized QA files remain reproducible local evidence.

Stable interface: `python3 tools/plot_pedal_trace.py --input TRACE.csv --output
NEW.svg`, or `--help` alone. No runtime imports beyond the standard library and
no repository-relative runtime inputs. Root was notified after this real script
and its passing tests existed so it can add the script to the install module and
update the exact installed-file inventory from 22 to 23. Tests consume the
existing `HAMMOND_PEDAL_TRACE_EXECUTABLE` and `HAMMOND_TEST_PROFILE` variables.

The parser checks exactly 37 metadata lines and 27 columns, the known model/map
identifiers and hashes, finite bounded decimal values, exact row count, contiguous
frames/rate/next clock, time tags, target/held-count consistency and all 200 ideal
contact bits. It checks recorded mixtures and position gains algebraically.
Unknown declared models/versions/profiles/maps and independent contact timing
are rejected. It does not simulate source phases, enforce the scenario schedule,
authenticate an unseen profile or validate the final audio sum.

At most 1,000 uniform integer-frame bins preserve each signal's actual minimum
and maximum. Every input sample participates, including isolated peaks and the
final sample. Every position and binary-state transition remains at its sample
boundary; excessive transition complexity rejects at the 1 MiB SVG budget.
Contact grouping is safe only after all eight bits equal the pedal's target;
all five disconnected `c1` positions are still checked and represented.

## Coherent source and artifact identities

Used the existing frozen wave-6 `checkpoint-w06/build-default` native executable
and nominal profile without changing that checkpoint. Root's recorded tested
source tree is `b2dae50dcde294bde8e7acb7addb14456197a779`, archived at
`/workspace/scratch/f364bc93d920/checkpoint-w06/source`; publication is
`d7b886103f8c9d4649ffa1c35930b79808217a3d`, with only final evidence Markdown
added after the tested tree. See the root integration record in
[DEVELOPMENT_LOG.md](../../DEVELOPMENT_LOG.md). This assignment adds separate
Python files against that frozen producer; it does not claim the moving shared
working tree was jointly tested.

| Artifact | SHA-256 |
| --- | --- |
| Frozen native `hammond_pedal_trace` | `e231a10e15b94cf790fada38e0c4807420c82ce1b114f934c36f7c50a504745b` |
| Frozen `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| New plotter | `45b28978924e88ac09b95bc6e5c9671e2b2f5059f9bd79df47565e8659f10f15` |
| New tests | `4a15024dc338eb5bda60c375c538357e2ea17fea23d155e190e1cb0e5447f167` |
| Public plot documentation | `2458cfdfcc070905df92c1dd8c5bba803ca6276de6dad175cad09201ccd3aec9` |
| Test transcript `tests-first.log` | `c4d590a0f97053607edc97cba2b8a407d9b302e5b24c3179ac33d7b2a46c272e` |

Local evidence directory: `/workspace/scratch/f364bc93d920/a45-pedal-plots`.
Python was 3.12.14. No dependencies were installed. Inkscape 1.4
(`e7c3feb100`, 2024-10-09), already available, was used only for visual QA.

## Exact commands and results

Executed from `/workspace/scratch/f364bc93d920/Hammond-B3-Organ`:

```sh
HAMMOND_PEDAL_TRACE_EXECUTABLE=/workspace/scratch/f364bc93d920/checkpoint-w06/build-default/hammond_pedal_trace \
HAMMOND_TEST_PROFILE=/workspace/scratch/f364bc93d920/checkpoint-w06/build-default/nominal.b3p \
python3 tests/test_plot_pedal_trace.py \
  > /workspace/scratch/f364bc93d920/a45-pedal-plots/tests-first.log 2>&1
```

**PASS: 16 tests in 14.158 seconds, zero failures, zero skips.** The test JSON
reports nine actual trace producer calls and nine actual plots, thirteen actual
plot CLI calls (including simultaneous writers), and two executed native symlink
preservation cases. The suite's handwritten known answer is buses `(8,4,2,0)` →
mixtures `(5.25,3.5)` and positions `(4,2)` → `P=3.5`; it does not import a producer
matrix to manufacture that expected answer. Handwritten small-bin and interval
oracles retain isolated spikes and final-sample changes. Additional tests cover
nonfinite/underflowing values, null-contact corruption, exact output bounds,
Unicode CLI paths, race preservation, cleanup, escaped XML and complete source
provenance. The actual-producer cases additionally inspect scenario anchors such
as muted `P` with nonzero mixtures, Lower Cancel preserving pedal contacts and
pedal panic preserving the Upper key.

| Actual scenario | Rate (Hz) | Rows | SVG bytes | Exact CSV SHA-256 |
| --- | ---: | ---: | ---: | --- |
| unmute | 44100 | 5292 | 202547 | `eae2eff6f43bc5c9b3cad198a994805d0d91da2c88d508f8981614abeb4fc44d` |
| unmute | 48000 | 5760 | 202662 | `47890dac0847125ffeae159e4ec8dc1326e6277baec0a1e76484340db2d8faa1` |
| unmute | 96000 | 11520 | 202700 | `64609cb2f3e3526fd86c81f7938993646899b9299e384c1011c252981769de3f` |
| overlap | 44100 | 5292 | 202937 | `92b952bff90a0dcea1fe8774d8dffdcb217d81c0618f067c791c714b2d7a0194` |
| overlap | 48000 | 5760 | 203228 | `eb9104804095053877a8195a98d3265184c2ef59df79537b2853011e0f00b2f5` |
| overlap | 96000 | 11520 | 203249 | `44777c35eb41efa6e1f59eec33f57eb5991839a3ccc884cf243def01e991f5fb` |
| routing | 44100 | 5292 | 196829 | `af29708884c5f4a900ba9334e7fb1eaf4f34b52602d686510a0b70c04966a32f` |
| routing | 48000 | 5760 | 197130 | `3ff70b36b23e012112b6038cd450b6716d0fa1d32a0f18579e8578cad0b89374` |
| routing | 96000 | 11520 | 197064 | `60896c3f6d45150f9887b467aed2d3a83733e1cf62d3cc8980754806edbee69e` |

Every native producer invocation used the following exact option pattern, with
`SCENARIO` substituted by `unmute`, `overlap`, `routing` and `RATE` by `44100`,
`48000`, `96000`. The test uses a new private directory for each run; no destination
is overwritten:

```sh
/workspace/scratch/f364bc93d920/checkpoint-w06/build-default/hammond_pedal_trace \
  --profile /workspace/scratch/f364bc93d920/checkpoint-w06/build-default/nominal.b3p \
  --scenario SCENARIO --sample-rate RATE --seed 0 --output NEW.csv
python3 tools/plot_pedal_trace.py --input NEW.csv --output NEW.svg
```

Separately retained the three 48 kHz CSVs under the local evidence directory,
then invoked the actual Python CLI for each retained example. The command below
was executed for all three names by a Python subprocess loop:

```sh
python3 tools/plot_pedal_trace.py \
  --input /workspace/scratch/f364bc93d920/a45-pedal-plots/routing-48000.csv \
  --output docs/examples/pedal-traces/routing-48000.svg
inkscape docs/examples/pedal-traces/routing-48000.svg --export-type=png \
  --export-filename=/workspace/scratch/f364bc93d920/a45-pedal-plots/routing-48000-qa.png
```

## Retained visual artifacts and inspection

| Scenario | SVG SHA-256 | QA PNG SHA-256 |
| --- | --- | --- |
| [unmute](../../examples/pedal-traces/unmute-48000.svg) | `1d5feffd0303cc66e51bb987766b93e710be5f82b75ade351acf10548cfbd0a9` | `280218cc584ff190083ad106e28f0af6a62b404373c630ba65bac14cbbdc43f1` |
| [overlap](../../examples/pedal-traces/overlap-48000.svg) | `14153cd569670793680bc107d7d9d6555f6629fa86b1e261cced09a1e857b4ba` | `55f2623d44af0e0700490a46fe6691cd0bfd4d7258b579b0c62ef5f1e331ca05` |
| [routing](../../examples/pedal-traces/routing-48000.svg) | `c9cff420597e862644bbc8b2f68080757c1c1a1c8c192dc3118341e97764a255` | `089516bf4623452595636b72c6fe9281135130ea0872526fd2845c55f395e60a` |

All three Inkscape executions exited 0. Opened and inspected all three 1200 × 1535
PNG renderings. Titles, time/vertical labels, legends, group markers, scope text
and full source hashes fit the panels without clipping or overlap. The unmute
plot visibly separates continuing pre-control mixtures from muted `P`/audio;
registration steps occur at their documented times. Overlap shows both pedal
lanes and separate Upper/Lower held-key intervals. Routing shows all 25 groups
held through Lower Cancel, Lower release at 60 ms, pedal panic at 80 ms, Upper
release at 100 ms and the final silent interval. The CSV's actual final audio
remains an envelope without clipping; no physical units or calibration are claimed.

The renderer printed local `PangoFT2FontMap` and `GtkRecentManager` wrapper warnings
in all three QA logs, despite successful exits and visibly correct text. Those
warnings were retained in `unmute-inkscape.log`, `overlap-inkscape.log` and
`routing-inkscape.log`. No generated bitmap is used by the plotter or retained as
the canonical artifact. The exact SVG is the source; PNG pixel hashes are only
local QA identities.

One read-only provenance probe, `git rev-parse HEAD` inside the frozen source
archive, exited 128 because the archive deliberately has no `.git` directory.
Resolved identity through the root's retained frozen-tree record and the actual
binary/profile hashes above; no checkpoint or Git metadata was modified. The
first complete plotter test execution passed without a test or implementation
repair. No other observed product/test failure was suppressed.

Final artifact review passed: both Python files parse as ASTs; all three SVGs
parse as XML; all seven owned files have UTF-8/LF text without trailing
whitespace; all fourteen relative documentation links resolve to existing files.
This review did not change the frozen plotter or tests.

## Remaining gates and next assignment

Root must add the frozen Python tool to `InstallCoreTools.cmake`, update the exact
install inventory/acceptance assertions, run the combined test set from a new
coherent source checkpoint, and exercise the installed plotter from an unrelated
working directory before claiming packaged availability. Root should add the
public documentation and assignment ledger links in its owned shared documents,
then commit and push the complete reviewed checkpoint under the standing rule.

This assignment validates Linux Python/producer behavior and locally renders
three SVGs. It does not claim hosted Windows/macOS plotter execution, a live UI,
DSP replay from CSV, source authenticity, phase continuity, full M3 completion,
physical contact/reactor calibration, scanner/AO-28/Leslie behavior or a released
plugin. Independent physical reference capture and model fitting remain the
separate scientific gate. The next diagnostic/UI consumer can reuse the strict
CSV contract and retained provenance, but must introduce a new declared model
and new lane representation before admitting independently timed pedal contacts.
