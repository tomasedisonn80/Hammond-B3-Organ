# Independent legacy PCM compatibility

A33 compared the preserved pre-selector executable with the newly built A31
combined-source renderer. **All 63 paired cases passed on their first run.**
Every pair produced identical complete PCM16 WAV bytes and byte-identical native
schema-3 JSON, including float-derived peak/RMS, clipping and model identities.
No production defect or production change was found.

The [execution note](../development/2026-11-14-preset-continuation/33-legacy-pcm.md)
and [complete machine record](../development/2026-11-14-preset-continuation/reports/a33-legacy-pcm.json)
retain commands, input identities, all summaries and individual results. This
qualifies the frozen contract's requirement to preserve the existing dry path
when fixed selection is unused. It does not test the new selector by comparing
it with itself, and it does not establish a measured instrument match.

## Independent executable reference

The reference is the integrator's untouched `build-baseline/hammond_render`,
whose production source is commit `b79086f6bb0c42b97130c721c5c73c7c97a13887`.
It was built before the selector implementation, not recompiled against new
headers. A33 never configured, built, relinked or changed it.

The subject is `/tmp/hammond-preset-a31/build/hammond_render`, built from A31's
complete frozen source with standalone, MIDI and VST3 enabled. A31's full-suite
qualification is separate from this executed PCM comparison. The original core
is non-PIC and the combined candidate core uses PIC; both use GNU C++ 14.2.0,
Release `-O3 -DNDEBUG`, C++20 and the repository's strict warning policy.

| Identity | SHA-256 |
|---|---|
| Preserved baseline renderer | `9b80a370078e87b4535b6d4d7fee7ed79f9949c443f1bd0432ed54b21c9e39b6` |
| A31 combined candidate renderer | `1f41ef4a9023c31228f86d851ae3220f1d1d78d48707b54875a6249949904730` |
| Common compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| A31 complete source manifest | `1f805c9257e2843c8ac1345938ff28603e2780e93831f0e2c02c907cc420ac8b` |

Before rendering, all selected core, data and renderer inputs were checked.
Of **133** selected frozen source/data/tool files, the sole difference from the
live tree was A32's subsequent `compile_fixed_registrations.py` repair, which
avoids stale timestamp bytecode when loading the adjacent admission compiler.
A separate actual invocation of that current generator produced bytes identical
to the candidate's 2,099-byte immutable header, SHA-256
`66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6`.
There was no runtime/data/table-format difference. The final checks preserved
all 133 inspected live hashes, both executable hashes, the profile, and all
12 identified historical score/profile/WAV/manifest files.

## Executed matrix

Two independently written **133-event** scores contain no `select_preset`.
Literal bank values and explicit event order exercise all **45 original
parameter identities** through their legacy score commands: 36 bank drawbars,
two manual bank selectors, expression, four percussion controls and two pedal
mixtures. Coverage is checked against the original commit's registry records;
that registry does not construct expected audio. The old executable is the
independent audio reference.

The scores include all four distinct banks, audible A/B returns, old selected-bank
`drawbar` edits, Cancel/reconnect with held chords, inactive-bank edits, folded
end notes on both manuals, three concurrent pedals, pedal zero-velocity release,
shared percussion on/off/harmonic/volume/decay changes, partial recovery and
legato histories, and negative-zero expression followed by audible restoration.
The nominal score includes partial travel targets; the ideal score uses only
its valid endpoints. Frame 0 overrides follow the CLI's documented zero-frame
initial control flush. Tied commands and events immediately around common block
boundaries preserve their literal input order. The final interval includes
release and silence while source phase continues.

| Family | Paired cases | Conditions |
|---|---:|---|
| Independent legacy control/history grid | 36 | Ideal/nominal contacts × 44.1/48/96 kHz × blocks 1/17/64/127/1024/65536; 24,577 frames each. Seeds 0, 731 and unsigned 64-bit maximum. |
| Ordinary default note gesture | 18 | Both contact policies × three rates × Off/Second/Third percussion; low/middle/high notes, normal/soft and slow/fast settings; 8,193 frames each. |
| Unchanged archived scores | 9 | Console, pedal phrase and two-manual examples, each at blocks 17/127/1024 with its original rate, seed, registration and contact/percussion options. |
| **Total** | **63** | **126 actual renderer child processes**, all exit 0 with empty stderr. |

For each pair, A33 checked the full WAV file, RIFF channel/sample/rate/frame
properties, equal stereo channels, nonempty audible PCM, and the entire native
stdout JSON bytes. Within the nine repeated-score groups, all **36** additional
block-partition comparisons also matched WAV bytes and every summary field
except the deliberately different `block_size`. All **nine** archive renders
also matched the original retained WAV file exactly.

| Aggregate observation | Result |
|---|---:|
| Compared frames per executable | 2,328,246 |
| Compared stereo PCM samples | 4,656,492 |
| Nonzero compared stereo PCM samples | 3,740,094 |
| Exact complete native JSON comparisons | 63 |
| Clipped frames | 0 |
| Largest reported float peak | 0.2968674302101135 |
| Matrix wall time | 11.103111 seconds |

The wall time is an engineering observation, not a callback deadline. There
were no failed renderer cases, compatibility mismatches or unchanged retries.
The [progress transcript](../development/2026-11-14-preset-continuation/reports/a33-legacy-pcm.txt)
retains the actual final counters.

## Limits and continuation

PCM16 equality plus exact float-derived peak/RMS summaries does **not** prove
that every unquantized float sample is bit-identical; neither renderer exports
that complete stream. Arbitrary zero-frame API operations, disconnected audio
outputs, new fixed selection, saved-state migration, host automation, allocation
and concurrent publication retain their separate core/native acceptance.
This assignment exercised the renderer's initial zero-frame flush and actual
positive render calls, not a second custom API harness.

These results apply to the named Linux GNU builds and nominal profile. There
was no physical device, hardware fidelity, AppleClang/MSVC, sanitizer or native
host run. The integrator retains the full integrated and platform gates for the
published source. Reuse this result only while the relevant runtime inputs and
compiled data remain equivalent; deliberate future model changes need a newly
stated compatibility boundary.
