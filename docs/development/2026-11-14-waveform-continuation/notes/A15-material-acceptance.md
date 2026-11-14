# A15 — Independent waveform material acceptance

- Actual worker: `/root/w03_a15_material_acceptance`; wave 3 of this session,
  14 November 2026. No nested workers, commits, pushes or manifest/status edits.
- Owned files: `apps/standalone/native_tests/test_standalone_waveform_material.cpp`,
  `docs/reviews/WAVEFORM_MATERIAL_ACCEPTANCE.md`, and this note.
- Outcome: **pass for the exact frozen drawbar/idle-front paint slice**;
  [retained review](../../../reviews/WAVEFORM_MATERIAL_ACCEPTANCE.md).
- Read: `AGENTS.md`, complete `PLAN.md`, atlas review, current scope/checkpoint/
  assignments, README/status/next steps/log, accepted waveform material design,
  A09 evidence, public geometry/model/paint/Drawing code, existing independent
  material harness and native CMake declarations. Inspected the actual original
  reference and native before/after images. No whole-PDF rereading is claimed.

## Frozen inputs and independence

Observed starting HEAD/local origin was
`26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`. Before painter SHA-256
`428f74c4b2aae72e1ee048d1fa878575d0cd2edc064b1a3865ba40c446c30da2`
also matches that published commit's exact file. Frozen after SHA-256 is
`6570c97f1c62b555a1df3477954514e379d61165a36cf20f879dea5151ff866b`.
A15 made no product edit. The source diff was inspected as the prescribed
drawbar and idle natural-front changes only. Concurrent other-session header
work was not borrowed, ignored or included in a material claim.

The optional comparator links both exact painters with three before-export
symbol renames and identical shared drawing/model/font/art/support archives.
Fixed copied controls, holds, status and renderer state make all pixels
comparable. The oracle uses independent long-double half-planes on public
vertices, resolves accidental occlusion, and excludes held fronts. It never
calls production containment, hit-test, span or inset/band helpers. Slot/cap
allocations follow independently derived public track/control dimensions.

## Actual execution

Toolchain: Linux x86-64/glibc 2.41, GCC 14.2.0, C++20 Release `-O3 -DNDEBUG`,
strict warning-as-error compilation, SDL 2.32.10 software surfaces. Reused
`/workspace/scratch/e3cacb90cc81/build` archives and pinned SDL sources in
`/workspace/scratch/1bb6ee17ad7e/SDL2`. No shared build/CMake mutation by A15.

1. Initial renderer compilations passed; the ordinary fixture compile found
   two baseline-only unused helpers. Conditional compilation fixed the test;
   no production change or weakened raster assertion was needed.
2. First optional comparison passed 79 pairs / 158 frames in 21.128 seconds.
3. Final fixture reports whether baseline comparison actually ran. Strict
   rebuild and exact final comparison passed **2,219 assertions**, 79 pairs,
   **149,100,628 examined pixels**, **zero escapes**, in **19.896 seconds**.
   The 5,382,830 changed pixels are confined to 2,963,899 slot/cap pixels and
   2,418,931 idle-front pixels. Eighteen Flat and twelve hidden Play pairs are
   byte-identical (six overlapping pairs).
4. Final portable ordinary test passed **1,917 assertions / 55 frames** in
   **7.199 seconds**. It measures the new cap joins, stems and fronts and tests
   the cut focused states; it explicitly reports `baseline_comparison:false`.
5. Eight actual native before/after processes at 1672×941, 1280×900, 960×700
   and minimum Flat passed smoke, screenshot, held/release observations and
   shutdown. All used explicit dummy video/audio, software rendering, MIDI OFF,
   48 kHz/512 frames and `--smoke-ms 1000`. Their exact binary/PNG identities
   are in the review; no physical device is implied.
6. A separately executed public-geometry half-plane mask on those actual
   application PNGs found 75,180 / 72,931 / 32,654 changed pixels at the three
   sizes, with **zero escapes**. The actual Flat pair is byte-identical.

The reference front median changed **159.0608 → 129.9874**, while its adjacent
top stayed **240.8184**. Exposed stem rows changed **3/3/3 → 9/9/9**. Across the
bounded matrix, 780 observed cap joins meet the 7/6-unit ±1 rule, 830 exposed
shaft sections pass, 234 idle-front patches pass, and sixteen clipped/offset
focused states pass. The four scales are 1, 1.25, 1.5 and 2. No existing gate was
edited or reclassified. Whole-test durations above are not UI draw timing.

## Retained evidence and continuation

Final test SHA-256 is
`1060ee4c062bb129ba58c082cc98921e478a7221a287acc4022401e41b13b81c`.
All exact source/dependency/executable/log hashes and compact results are in
the review. Larger evidence is bounded in
`/workspace/scratch/e3cacb90cc81/a15-material/`: `compile-commands.json`,
`link-commands.json`, `baseline-final.jsonl`, `default-final.jsonl`,
`executed-results.json`, `application-captures.json`,
`application-containment.json`, `identities.json`, frozen painter/executable
copies, and PNG/BMP captures. Existing supplied `baseline-ui/` and
`material-ui/` files were read without modification. Root retains control of
the coherent final gallery; these captures remain scratch evidence.

Root was sent CMake linkage requirements early and reports the target is now
registered. Root's canonical build/CTest integration remains separate from
A15's direct compile execution. Next: run the current coherent native fixture,
perform the separately owned 30-warmup/300-draw timing comparison, integrate
other-session header changes without weakening this slice's comparison, then
capture the coherent product and update the actual gallery/README. Literal
reference equality, real-display/DPI/device acceptance, accessibility and
M5/M6/M7 sound integration remain open.
