# Interface resource budget — A33

The measured workspace has **39,915,786,240 bytes available** (37.17 GiB).
There is no immediate disk-pressure finding. This bounded audit observes the
current session and three short native processes; it is not a performance,
leak, callback-deadline or product memory guarantee.

## Storage and reuse

The [storage record](../development/2026-11-14-interface-continuation/reports/a33-storage.json)
retains exact paths, byte counts, source hashes and commands. Allocated sizes
below come from separate `du -s -B1` calls; nested rows are not additive.

| Measured directory | MiB allocated |
|---|---:|
| Checkout, including Git and evidence | 90.02 |
| Current session evidence within checkout | 3.84 |
| Current eight-image gallery within checkout | 2.79 |
| Shared native Release build | 81.74 |
| Shared SDK-free Release build | 9.96 |
| Actual MIDI-off Release build | 35.03 |
| Frozen repair source / build | 29.14 / 35.10 |

All three active builds name the same checkout. Native and MIDI-off caches
reuse SDL source `5d249570393f7a37e037abf22cd6012a4cc56a71`; enabled MIDI
reuses RtMidi `1e5b49925aa60065db52de44c366d446a902547b`. The separate repair
checkpoint is retained evidence, not another per-worker SDK. No other worktree
was scanned or changed. Among 1,600 indexed files, no compiled executables,
object/library files or build/cache directories were found. The largest file
is the intended original atlas, 21,248,265 bytes.

## Native observations

After root released its full gate, exactly three serial 600 ms smokes used
the pinned executable SHA-256
`55b0947985ee562cce3d04eae66cc4d44f805420f475dd578f00373dd2bef6cd`.
Each used independent absent state files and actual 1672×941 window/drawable
dimensions. Diagnostics identify SDL 2.32.10, dummy audio/video and the
**software renderer**, not accelerated hardware. All exited zero, completed
held/released-note smoke assertions, reported zero errors and retained two
untruncated presentation observations. No screenshot was requested.

| Case | Peak RSS, KiB | Wall, seconds | User / system CPU, seconds |
|---|---:|---:|---:|
| Play dimensional | 25,700 | 0.751 | 0.607619 / 0.097918 |
| Service dimensional | 22,020 | 0.729 | 0.635615 / 0.011779 |
| Play Flat | 16,712 | 0.678 | 0.464330 / 0.007642 |

[Per-process evidence](../development/2026-11-14-interface-continuation/reports/a33-runtime.json)
uses Linux `wait4` resource usage; monotonic wall measurement has up to 10 ms
polling quantization. `/usr/bin/time` was unavailable before any app launched;
the setup correction is retained. These single samples establish neither a
mode ranking nor physical-device timing. They precede A31's Drawing repair.

## Source bounds and their limits

`UiModel.h` owns fixed arrays: 68 control records including presets, 147 playing
keys, three workspace focus memories and four actions per result.
`InspectionModel.h/.cpp` uses six cards with six row slots each, six Rotary
rows and 128-byte text cells with at most 127 payload bytes. Formatting uses
copied state and bounded local buffers. These are source-inspection findings;
existing allocation/PCM gates were not repeated.

`main.cpp` caps presentation history at 512 transitions, retaining the latest
paint separately. Replay histories cap at 512 UI or 8,704 MIDI observations.
Capture is attempted once; `Drawing::save_bmp` frees its temporary RGBA surface.
Five textures are prepared at initialization rather than cached per frame.

The 8,192 limit applies to logical window and admitted embedded-asset dimensions.
Capture allocates **actual renderer output** without a separate drawable cap.
At 8,192², one four-byte surface is arithmetically 268,435,456 bytes (256 MiB);
HiDPI output can exceed that logical size, and other SDL allocations are additional.
No such surface was allocated here. Future display/capture qualification must
measure actual drawable dimensions before choosing any product memory ceiling.

## Cleanup and resumption

No BMP remained in eight explicitly inspected session build/capture directories.
Two optional temporary candidates total 4,742,916 bytes: the pinned A33 executable
and A22 contact sheet. Their exact paths, hashes, sizes and retained proof are in
the storage record. **Nothing was deleted.** Keep them until root reviews the
evidence; preserve source material and original failures.

At the inventory snapshot, the manifest contained 33 actual rows, 30 accepted
and three running. The 6,789-byte checkpoint names current HEAD
`5d81199a9822874b55f3b0a124715cbd6eadf0e5`, ownership, shared builds and concrete
next integration actions. Resume there instead of rereading historical logs.
Root owns subsequent count/status changes and publication.
