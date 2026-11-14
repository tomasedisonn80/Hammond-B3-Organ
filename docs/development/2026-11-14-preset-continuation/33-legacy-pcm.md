# A33 — Old-executable legacy PCM acceptance

Actual worker `/root/w06_a33_legacy_pcm`, logical wave 6, 2026-11-14.
Repository `/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`; observed checkout
context `35554c068492fe2b20c1f8a602d8354ae762dc42`. The current implementation is
an overlay, not the source identified by that baseline commit alone.

Read `AGENTS.md`, the complete M0–M9 plan, current README/status/next-step/log
context, frozen selection/core contracts, renderer grammar and A14/A19/A24
acceptance. The source readers' complete PDF coverage remains their own work;
A33 did not claim another full-PDF read.

## Result and owned work

The [independent review](../../reviews/PRESET_LEGACY_PCM_ACCEPTANCE.md) accepts
**63 old/current paired cases**, with **126 actual render processes**, on the
first matrix run. Complete WAV bytes and native JSON summaries matched across
2,328,246 frames per executable. All 36 cross-partition comparisons and all nine
comparisons with the three original archived WAVs also matched. No production
defect, modification, rebuild or repair was required.

Owned additions are this note, the review, and these retained evidence files:

- [Complete commands/results/source identity](reports/a33-legacy-pcm.json).
- [Actual progress and counters](reports/a33-legacy-pcm.txt).
- [Ideal legacy score](reports/a33-legacy-control-grid-ideal.events).
- [Nominal-contact legacy score](reports/a33-legacy-control-grid-nominal.events).

No production, existing test, archived fixture, shared status, assignment
manifest, dependency, Git ref or remote was changed. No child agent, commit or
push was performed. Existing baseline/native build directories remained read-only.

## Executables and coherent inputs

The original executable remains
`/workspace/scratch/a472c29da8b3/build-baseline/hammond_render`, SHA-256
`9b80a370078e87b4535b6d4d7fee7ed79f9949c443f1bd0432ed54b21c9e39b6`.
The integrator's [baseline record](reports/baseline.json) identifies its unchanged
production source as `b79086f6bb0c42b97130c721c5c73c7c97a13887` and GNU 14.2.0
Release build. A33 never rebuilt it or linked its library against current headers.

Initially inspected A24's qualified offline renderer, SHA-256
`ade81c8062b28a862a01c48f86220320558d893f19ab78a073deb1acf754f93b`; all 133 selected
source/data/tool inputs then matched the live tree. Before any comparison render
was started, A31 provided its fresh combined renderer. The matrix therefore used
only A31's candidate, SHA-256
`1f41ef4a9023c31228f86d851ae3220f1d1d78d48707b54875a6249949904730`, at
`/tmp/hammond-preset-a31/build/hammond_render`. This was a built coherent candidate;
A31's separate full 143-suite gate was still running when the matrix began.
No duplicate A24 matrix was executed.

A31's frozen source is `/tmp/hammond-preset-a31/source`; its full
`source-manifest.json` SHA-256 is
`1f805c9257e2843c8ac1345938ff28603e2780e93831f0e2c02c907cc420ac8b`.
Its core is PIC because VST3 is enabled; the original core is non-PIC. Both actual
`flags.make` files use Release `-O3 -DNDEBUG`, C++20 and the same strict warning
set. Both compiled profile files have identical bytes and SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
The exact baseline profile path was supplied to both processes.

The machine record retains the 133 selected candidate/current path-hash pairs.
After A32's generator repair, their sole difference is
`tools/compile_fixed_registrations.py`. A33 independently invoked the current
source with the actual admitted JSON and both CSV readings:

```sh
python -B tools/compile_fixed_registrations.py \
  --input data/registrations/atlas-chapel-nominal-v1.json \
  --review-a data/registrations/review-a-chapel.csv \
  --review-b data/registrations/review-b-chapel.csv \
  --output /tmp/hammond-preset-a33/current-FixedRegistrationData.h
```

It exited 0 without stdout/stderr and produced bytes identical to A31's compiled
2,099-byte header, SHA-256
`66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6`.
Current generator SHA-256 is
`770eff9d031961de81d4520136d1781795a9e2b494f2a9c4a44c727b5c0f1644`;
A31's preceding generator is
`234d2430d202873e3211c11cd0a1317bb7b73d6722ed3b12992083cb1fe5d3bd`.
A32 confirmed no runtime/data/header-format change. A31's build was untouched.

## Executed matrix and reproduction

Actual harness: `/tmp/hammond-preset-a33/run_legacy_matrix.py`, invoked once as:

```sh
python /tmp/hammond-preset-a33/run_legacy_matrix.py \
  > /tmp/hammond-preset-a33/matrix.log 2>&1
```

The complete retained JSON contains the two exact argument arrays for every
case, all options, input score identities, report bytes, WAV hashes and results.
No undocumented flag was used: both executable help outputs and the current
renderer grammar were inspected first. Each subprocess ran in its new case
folder under `/tmp/hammond-preset-a33/runs`, used a distinct output filename,
and had a finite 30-second process guard. There were no setup or renderer failures.

For example, replace `RENDERER` with either named executable and choose a fresh
output filename to repeat the 48 kHz ideal/block127 grid case from the repository:

```sh
RENDERER --profile /workspace/scratch/a472c29da8b3/build-baseline/nominal.b3p \
  --output /tmp/choose-a-new-legacy-grid.wav --sample-rate 48000 \
  --block-size 127 --frames 24577 --seed 731 --drawbars 000000000 \
  --pedal-drawbars 00 --contacts ideal --percussion off \
  --percussion-volume normal --percussion-decay slow --fail-on-clip \
  --events docs/development/2026-11-14-preset-continuation/reports/a33-legacy-control-grid-ideal.events
```

The review lists the bounded 63-case matrix and its musical coverage. Both
133-event scores cover the legacy 45 record identities without new selectors;
all original archived inputs remain unchanged. The first and only matrix
finished in 11.103111 seconds, with zero clipping and maximum float peak
0.2968674302101135. All executable/profile, archived-file and selected live-source
hash checks still matched afterward.

The original local runs retain both WAVs and raw stdout/stderr per pair. The
machine record retains full common stdout for each identical pair, so it does
not rely only on a pass boolean or aggregate counts. Original score files and
all 12 historical event/profile/WAV/manifest hashes are also retained there.
No WAV or historic report was rewritten. The machine record SHA-256 is
`e485c26467f342e5b544f337d1c66c18f0651a83ceb3390d7d5e9367f123a4ee`.

## Handoff and limits

Root owns acceptance, coherent final-source/platform qualification, shared
status and publication. This Linux process comparison establishes complete
PCM16 and native float-summary compatibility for the named cases; it cannot
establish every unquantized float sample's equality because the CLI does not
export that stream. It uses the real zero-frame initialization flush, not
arbitrary zero-frame API test calls. No physical audio, device, host, callback
allocation, sanitizer or other-platform claim follows. The new fixed rows and
state/parameter migration retain their separate qualified tests.
