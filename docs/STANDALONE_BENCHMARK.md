# Offline standalone Session benchmark

`hammond_standalone_benchmark` measures actual SDK-free
[`Session::render`](../apps/standalone/Session.cpp) calls against the unchanged
nominal dry core. It needs no SDL, device, window or host. It reports observed
elapsed intervals and reconciled musical work; it applies no timing pass threshold.

## Build and invoke

```sh
cmake -S . -B ../benchmark-release -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_STANDALONE=OFF
cmake --build ../benchmark-release --target hammond_standalone_benchmark --config Release --parallel 2
../benchmark-release/apps/standalone/hammond_standalone_benchmark \
  --profile ../benchmark-release/nominal.b3p --sample-rate 48000 \
  --buffer-frames 512 --iterations 500 --warmup 16 --workload performance
```

For multi-configuration generators use the executable's `Release` subdirectory.
The compiled profile is required; there is no hidden profile default or output-file
option. Successful runs emit one JSON object to stdout. `--help` must appear alone.
Unknown/duplicate switches, missing/empty/oversized values, invalid integers,
unsupported choices and unreadable/invalid profiles exit nonzero with diagnostics.
Windows uses the shared strict UTF-16-to-UTF-8 `wmain` adapter and native paths.

| Option | Accepted values | Default |
| --- | --- | --- |
| `--profile PATH` | Existing compiled profile, maximum 128 KiB | Required |
| `--sample-rate` | 44100, 48000, 96000 Hz | 48000 |
| `--buffer-frames` | 128, 256, 512, 1024, 2048 | 512 |
| `--iterations` | Decimal integer 100–5000 | 500 |
| `--warmup` | Decimal integer 0–1000 | 16 |
| `--workload` | silence, performance, dense, recovery | performance |

## Fixed workload version 1

Each run prepares one Session with seed 0 and initial frame 0, starts it, performs
one setup zero-frame flush, then runs warmup and measured cycles continuously.
Non-silent registration is Upper B `888000000`, Lower B `008800000`, both A banks
zero, both B banks selected/routes enabled, pedal mixtures `[8,5]`, expression
`0.75`, and percussion enabled/Third/Soft/Fast. The six identified channel-0 holds
are Upper MIDI `[60,64,67]`, Lower MIDI `[48,55]`, and pedal ID `[1]`; note IDs are
1–6 in that order. Manual buses are 0/1; the pedal origin bus is 0; velocity is 127.

| Workload | Setup commands | Each warmup/measured cycle |
| --- | --- | --- |
| silence | None; unchanged muted defaults and no holds | Render the full positive block. Shared sources and frame clock still advance. |
| performance | One full registration restore, then six note-ons | Render with all six logical holds retained and positive finite output. |
| dense | Same seven commands as performance | Admit exactly 256 expression controls: 128 ordered `0.5 → 0.75` pairs; render all of them at the boundary while retaining holds. |
| recovery | One registration restore, no initial holds | Post six note-ons and make an unmeasured zero-frame flush; verify actual holds. Admit 256 expression controls, require the next post to return `QueueFull` and another to return `RecoveryPending`, both sequence zero. Time the positive render that actually discards all 256, completes one global recovery, and publishes empty holds/zero peak. |

The same prebuilt command arrays drive warmup and measurement. Queue posting,
recovery rearming, all zero-frame calls, parsing, preparation, allocation, sample
checking, snapshot reads, hashing, statistics and output are **outside** the two
clock reads around each measured positive `Session::render`. Recovery includes
the actual discard/panic/publication work; its expected overflow is recorded as
intentional workload behavior. The measured loop elapsed time also includes the
outside-interval work and must contain the sum of measured render intervals.

## Report and verification contract

Schema `hammond-standalone-benchmark-v2` includes every chronological raw interval
in `timing.samples_ns`, plus unadjusted minimum, median, p95, p99, maximum and sum
in nanoseconds. Median averages the two middle observations for even counts;
p95/p99 use nearest rank `ceil(p*N)-1`. No outliers are removed. The separate
1,000 empty clock-pair calibration reports its own distribution; nothing is
subtracted. `steady_clock`'s nominal tick is reported, not asserted timer accuracy.
`nominal_callback_period_ns = frames*1e9/sample_rate`; the distribution ratios and
count strictly above that period describe these observations only.

The preallocated stereo/time arrays stay fixed throughout processing. Every
post, lifecycle call, render result and snapshot read is checked. Every positive
output is finite with bit-identical L/R, and its actual peak matches publication.
Setup/warmup/measured stage counts reconcile accepted/applied/discarded commands,
expected failed posts, recoveries, zero/positive calls, sequences and frames.
All four retained snapshots expose exact controls, holds, clock and sticky faults.
Version 2 adds raw `fixed_registrations` and separately derived
`preset_selections` to every controls object; remembered `selected_banks` and
`route_enabled` keep their meanings. The four workload definitions remain version
1 and use no fixed row, so this report migration does not change their scores.
Archived benchmark-v1 reports retain their original bytes and schema.
Stop must clear holds/peak without advancing time or changing retained controls.
Any failed check exits nonzero before constructing a success report; stdout write
failure also returns nonzero. Timing alone never turns a workload failure into success.

Build identity includes compiler/version, configuration, target OS/processor,
C++ version, `NDEBUG`, project sanitizer option and a SHA-256 source manifest.
The manifest hashes sorted `relative-path:sha256\n` records for core sources and
headers, Session, this benchmark, CLI path handling and the actual profile/pedal/
scanner/fixed-registration generation inputs named by CMake; content changes trigger reconfiguration.
The project sanitizer flag does not discover arbitrary external flags; retain
`compile_commands.json` and the CMake cache with a comparison. Profile identity
contains its ID, retained authoring SHA-256, and byte count/FNV-1a64 over the exact
compiled bytes parsed. The retained digest does not authenticate unseen authoring
JSON. Audio FNV-1a64 uses native float object bytes as a same-build diagnostic sink.

These short serial offline runs do not qualify scheduling, concurrent UI load,
real-device deadlines, underruns, physical latency or hardware fidelity. Those
report fields remain unavailable. CPU affinity, power/thermal state and scheduler
contention need separately controlled evidence for performance comparisons.
See the [assignment 29 observations](development/2026-11-13-next-phases/29-session-benchmark.md)
and [Session contract](STANDALONE_SESSION.md); allocation/concurrency/device gates
remain independently scoped.
