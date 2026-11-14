# A34 — Dry audio and state isolation

Actual worker `/root/w06_a34_audio_state_isolation`, wave 6. Reviewed the standing
instructions, current scope/checkpoint, full M0–M9 plan, source delta and existing
independent continuity/persistence/parameter assertions. Owned only this note and
the [report](../reports/A34-audio-state-isolation.json) / [raw log](../reports/A34-audio-state-isolation.log).
No product, test, build configuration or shared documentation changed; no commit
or push was performed.

## Source boundary

Published source is `2e161dc3a60fc3442051799574feed37bffbfc5c`, tree
`17f8e4d698f903c37bff09deee196ea73e0da108`. Against session start `8bd999e`,
**92 existing core/header/plugin/data files are byte-identical**. Changes in those
roots are confined to repaired `RotaryMotion.cpp` and the new propagation header
and implementation. Eight separately checked Session, StateFiles, MidiInput and
AudioDevice files also retain exact baseline bytes.

The UiModel changes affect layout allocation only; inspection changes singular
wording. Native main adds copied observation fields and saturating capture
counters without changing its dispatch/release decisions. None of 55 production
caller translation units/headers references the nominal rotary interfaces.
The coherent standalone executable contains no defined `hammond::rotary::`
symbol. Its SHA-256 is
`0ef37dd5a0501da08df302027b31791b7917705e00cb32017b035a145ceb3811`.
Being present in the static core archive does not connect these primitives to
the dry signal path.

## Executed acceptance

Root granted exclusive use of the existing GCC 14.2 Release `build-native`
configuration (MIDI OFF, VST3 OFF). No configure, build or stress run occurred.
Discovered exactly the four required suites before execution. **112 source
inputs** match the coherent-build inventory and published bytes; relevant source,
three test executables, two archives and compiled nominal profile stayed unchanged
across the run. Exact identities and CTest commands are retained in the report.

From `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`:

```sh
../build-tools/cmake/data/bin/ctest --test-dir ../build-native -C Release --output-on-failure --no-tests=error -V -R '^(test_control_io|test_parameter_bridge|python_test_parameters|test_standalone_workspace_continuity)$'
```

**4/4 pass in 4.80 seconds.** The unchanged continuity test independently commands
two real Sessions and an Engine; only one UI changes views/geometry. It compares
each stereo sample bit pattern with the Engine result, not merely a final hash.

| Observed check | Result |
| --- | ---: |
| Cases / rendered frames | 63 / 719,289 |
| Matched stereo sample positions | 1,438,578 |
| Presentation transitions / generated view commands | 1,662 / 0 |
| Matched musical commands / state-byte comparisons | 1,419 / 14,190 |
| Source-phase / percussion-readiness checks | 170,352 / 1,872 |
| Isolated percussion samples / cancelled-Upper blocks | 271,224 / 36 |

Coverage includes overlapping owners, zero-frame acknowledgement, saved controls,
silent phase/recharge and future attacks at 44.1/48/96 kHz. Aggregate PCM FNV-1a
is `9b6fbb0939b79179`. Native parameter acceptance retains all **47** live targets,
6,327 conversions, 42,666 atomic rejections and four rounding modes; registry
acceptance passes **32 Python methods**. Persistence retains state4 writing,
readers1–3 and 2,240 malformed-input destination-preservation cases.

## Limits and continuation

No defect was found. This is an executed current-source navigation/control/Engine
comparison plus baseline source identity, **not** a historical/new executable PCM
comparison. It qualifies the nominal dry engineering boundary, not physical sound,
real devices, callback deadlines or cross-platform PCM hashes. Preserve this
boundary while finishing the gallery and hosted gates; R4 waveform work needs
its own reviewed ownership and integration acceptance before entering Engine.
