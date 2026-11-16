# Starter audio provenance admission — A45

16 November 2026, actual worker `/root/w08_a45`, wave 8. **Admit the retained
32-clip batch as bounded, proposed nominal dry Engine evidence.** The independent
[audit](../development/2026-11-16-preset-library-continuation/reports/a45-audio-provenance-audit.json)
passes 400/400 checks against actual files, the
[original manifest](../development/2026-11-16-preset-library-continuation/reports/starter-auditions.json),
[pack provenance](../development/2026-11-16-preset-library-continuation/reports/starter-provenance.json)
and frozen [pack](../STARTER_REGISTRATION_PACK_CONTRACT.md)/[render](../REGISTRATION_RENDER_CONTRACT.md)
contracts. This is independent byte inspection, with no new render, project
executable run, build, capture or perceptual listening.

## Actual bytes and numerical checks

Working directory was `/workspace/scratch/3edffb787db3/Hammond-B3-Organ`, HEAD
`20739f6280b95e567e84615d5c5aee443fc3b93d` plus the recorded working overlay.
An inline `python3 -B -` observer used standard-library `hashlib`, `wave`,
`array`, `struct`, `json`, `math`, `gzip` and `tarfile`. It independently enumerated
the expected jobs and compared each pair's complete bytes directly.

| Checked property | Observed result |
| --- | --- |
| WAV inventory | 32 files; 6,145,408 bytes total |
| Each WAV | 192,044 bytes: exact 44-byte RIFF/WAVE header plus 192,000 PCM bytes |
| Format and duration | PCM format 1, signed little-endian 16-bit, two channels, 48,000 frames at 48,000 Hz: exactly one second |
| Complete suffix pairs | All 16 pairs identical, including headers |
| Decoded samples | 3,072,000 channel samples; finite integers; identical left/right channels |
| Content/headroom | Every clip nonzero; absolute peaks 682–2201; zero samples at either PCM saturation rail |
| Retained renderer metrics | Finite peak/RMS; all clipping counts zero; peak range 0.02080640383064747–0.06717231124639511 |

Every WAV, stdout and stderr size/SHA-256 matches its original manifest entry;
all 32 stderr files are empty. Every retained stdout is schema 6 with the exact
initial canonical payload, source version 4, raw byte count, path and
`full-state-including-expression` policy. Independently parsed fields in all
24 payloads match every literal recipe field and both A27/A28 identities.
The twelve payload pairs remain identical; their ordered aggregate is
`8618b545b1c04bdf1370478259967125cb63b09a81bbb6748f6990788578de11`.

All three copied scores equal their source bytes. Each recorded argv has nominal
contacts, seed 73, block 64 and `--fail-on-clip`; the raw stdout independently
reports the corresponding rate/frame/block/seed/contact settings and profile
identity. Historical process exits remain the manifest's recorded zero exits,
not fresh observations. The inspected renderer encodes Engine samples directly,
without per-clip normalization; the profile's `output_gain 0.03` belongs to the
nominal model. PCM peak/RMS agree with reported prequantization metrics within
the rounding bound `0.5/32768`.

## Literal states and score windows

Intervals below are half-open frame ranges; both suffixes give identical results.

| Recipe/score | State and event relationship | Actual PCM result |
| --- | --- | --- |
| 10, audition | Routes Off/Off, banks A/B, pedals `[6,2]`, expression 0.5; manual-only passage `[0,26000)` | Exactly zero |
| 10, audition | Pedal ID 1 at 26000; pedal ID 8 at 36000 | Peaks 682 and 523; released gaps exactly zero |
| 10, banks-reveal | Both routes initially cancelled; explicit A selections at 12000, B at 24000 | `[0,12000)` zero; later A/B peaks 982/946 |
| 12, audition | Upper Off, retained G#; Lower On/B, pedals `[4,0]` | `[0,16000)` zero; Lower/pedal passages nonzero |
| 12, manual-return | Upper C held while cancelled; explicit G# code 8 at 8000 | `[0,8000)` zero; `[8000,16000)` has 7,997 nonzero mono frames, peak 1200 |

Recipe 12 retains On/Third/Soft/Fast percussion and expression 0.5. Explicit
A/B selections at 18000/30000 produce nonzero passages and clear fixed mode
under the inspected control implementation. Upper B becomes percussion-eligible
under the Engine rule. This audit does not isolate percussion amplitude or
validate G# timbre. The score explicitly selects G# again; it does not exercise
an implicit last-preset recall mechanism.

## Source identity and retained delivery

| Object | SHA-256 |
| --- | --- |
| Original manifest, 80,972 bytes | `01ae18231688c215512059850a7784c4451e502b37a640b2ef34934d55e3160d` |
| Actual renderer, 212,888 bytes | `671375f6f9d393295bca148bcb546a1eb387dd865e994e755f16933389a16263` |
| Actual profile, 4,545 bytes | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Original helper, 20,121 bytes | `60a2e20d0a60a6e6e18ea55913e69fd1bedb81f52ae8ae0558cacf0ac09a173a` |
| A40 corrected helper, 21,687 bytes | `1ff78d28e74c7556aa525f5eb779d40ced76b7f913c1ec38085b4c2def216157` |
| Complete original archive, 1,698,038 bytes | `e61f5ff3b95966504f4261914339bc0eee759db1837993bbf9d29742b81f9858` |
| Original report, 5,396 decompressed bytes | `8960f21cf554e7f82210b6984bcd08de00878626804507d38a9a7768f40b7b8b` |
| Derived reader, 5,064 bytes | `e3477f7b6352bc7b5f1130e5bc81b49da034cfe7e20064cd478e85c67c62f075` |

The original helper is recoverable byte-for-byte from HEAD's Git object. A40's
[correction](STARTER_FAILURE_BOUNDARY_ADMISSION.md) changes reporting failures
and prose; input/job/execution/WAV-inspection function ASTs are unchanged.
The historical manifest correctly retains its original helper hash.

Root's broken-link repair preserves all **101 original files / 6,300,666 bytes**
in the [archive](../development/2026-11-16-preset-library-continuation/reports/starter-auditions-originals.tar.gz).
Every member equals the corresponding original file; the
[original report gzip](../development/2026-11-16-preset-library-continuation/reports/starter-auditions-original.md.gz)
decompresses exactly. The separately identified
[reader](../development/2026-11-16-preset-library-continuation/reports/starter-auditions.md)
changes delivery links only. All original bytes and checked inputs remain unchanged.

## Limits and next action

No expected A27 raw artifact is missing. Prequantization float buffers are absent;
nonfinite-sample rejection is source evidence, corroborated by finite summaries and
PCM bounds. A28 inspection stdout is hash-recorded without separate retained
paths; this admission uses independent payload parsing. An initial observer
variable-shadowing error occurred during report assembly, wrote nothing, and is
recorded in the corrected audit. Root owns final integration/publication.
Listening preference, factory/artist attribution, measured physical fidelity,
live-browser/device/host, platform and whole-interface acceptance remain separate.
