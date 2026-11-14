# A27 — MIDI and reference interface operations handoff

Actual worker: `/root/w05_a27_operations_handoff`, MIDI/UI wave 5, assignment 27.
Owned only `docs/MIDI_UI_RUNBOOK.md`, `docs/STANDALONE_APP.md`,
`docs/STANDALONE_MODEL.md` and this note. No code, CMake, tests, source assets,
shared status, README, assignment accounting or history was changed by this
worker. A26 owns installation/notices and packaging acceptance; A25 owns the
retained native acceptance updates. No subagents or commits were created.

## Delivered operational contract

The new [runbook](../../MIDI_UI_RUNBOOK.md) provides the ordinary SDK-free build,
explicit SDL2/RtMidi acquisition and verification, both native build modes,
source-backed platform prerequisites, exact-name input selection, distinct
one-based channels, keyboard/pointer MIDI settings, complete supported controller
map, bank/Save distinctions, recovery and bounded diagnostics examples.

The [application guide](../../STANDALONE_APP.md) now describes native MIDI,
the reference view, `--midi-script`, schema-2 diagnostics and scoped retirement.
The [model guide](../../STANDALONE_MODEL.md) replaces its stale claim that native
MIDI still needs implementation, while retaining the actual dry/unmeasured sound
boundary, unchanged 45 parameters and `B3CONTROLS3`.

Only links among the four shipped guides remain relative. Repository-only docs,
source and examples use canonical GitHub URLs. These URLs were checked against
the corresponding local source targets; this is not a claim that pending
unpublished changes were fetched from the public branch. Guide bodies remain
readable after relocation, with network access needed for external references.

The runbook was created and announced early so A26's required-input preflight
could proceed. Final APP/MODEL/RUNBOOK inputs were frozen and their identities
sent to A26 before its final copied-payload qualification. The guide delegates
the exact enabled/disabled package inventory to A26's installation contract;
clean local staging is not called a signed installer or release qualification.

## Read and inspected source

Read `AGENTS.md`, current session scope/manifest entry points, current README,
status/next-step/log entry points, the M0–M9 plan, relevant standalone handoff,
MIDI input/backend/replay contracts, SDL/RtMidi dependency instructions, existing
APP/MODEL/INSTALL guides, reference layout/provenance and independent visual
review. Used the latest full-atlas review for the sound/UI evidence boundary;
this worker makes no new full-PDF reading or screenshot-comparison claim.

Inspected actual `main.cpp` option parsing/help, MIDI modal controls, retirement,
audio restart and diagnostics, the root/standalone CMake options, native backend
selection and existing native CI prerequisite commands. Reviewed A23/A24 evidence
and A25's finished retained-suite record. Source-backed instructions preserve
one selected input, wire channels 1–16 with defaults 1/2/3, manual 36–96/pedal
36–60 ranges, fixed manual-B CC16–24, pedal CC16/17, shared CC11 and scoped CC123.
Unsupported messages, callback-boundary timing, best-effort disconnection and
explicit reconnect remain visible.

Observed checkout HEAD was `e09107414896c2c53dad124a74f60c8043fadfe4`, with the
concurrent uncommitted MIDI/UI candidate present. The runtime checks below use
root's coherent existing binary; the base commit alone does not identify it.
No remote fetch, publication or complete frozen-tree qualification was run.

| Inspected/tested input | SHA-256 |
| --- | --- |
| `apps/standalone/main.cpp` | `22719975ed910b0b23db841617446e492890d89f2106cc04279fc9e46824f42e` |
| Native executable | `e8871447021a1373e2bfdc262a513d12487e49fd0e833bad068f226a6938ed2d` |
| Frozen `STANDALONE_APP.md` | `2f6d76e94ad16fbde2192e97bc7bb852b26620423155d03e2fccaeb283c34bab` |
| Frozen `STANDALONE_MODEL.md` | `a68ca7d836050f687ba0ec87933f7f3c0417356a03bf6d75aacfdf1409ed9051` |
| Frozen `MIDI_UI_RUNBOOK.md` | `bc088e41621a0fa5363b3206e1ca71bbf4518a0492f46d842c415ab116bb779d` |

Toolchain inspection: GNU C++ 14.2.0, Python 3.12.14, configured CMake 4.4.4.
The bare `cmake --version` attempt initially returned command-not-found in this
worker's shell. The configured absolute CMake executable from `CMakeCache.txt`
then returned 4.4.4 successfully:
`/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake`.
The published recipes require a usable CMake on PATH; no fresh configure or
build was needed for this documentation assignment.

The native cache has Release, `HAMMOND_BUILD_STANDALONE=ON`,
`HAMMOND_ENABLE_MIDI=ON`, the pinned RtMidi checkout, the explicitly provided
ALSA sysroot and `SDL_ALSA=OFF`. The latter is a local SDL/header compatibility
workaround, not a product setup recommendation. All successful runtime probes
below explicitly select dummy SDL audio/video. No physical input was opened.

## Executed checks

Working directory for source commands:
`/workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ`.

1. The actual native `--help` returned 0 and matched the documented options,
   channel constraints, Ctrl+M controls and replay exclusions. Both acquisition
   tools' `--help` returned 0 and confirmed their documented operation names.
2. Both exact existing dependency checkouts passed the read-only verification
   commands below, with `network_used: false`. SDL reports release 2.32.10,
   commit `5d249570393f7a37e037abf22cd6012a4cc56a71`; RtMidi reports tag 6.0.0,
   commit `1e5b49925aa60065db52de44c366d446a902547b`, two checked source files
   and its primary license. No acquisition, dependency repair or build occurred.

   ```sh
   python3 tools/acquire_sdl2.py --verify-existing /workspace/scratch/7ffc2842608b/SDL2
   python3 tools/acquire_rtmidi.py --verify-existing /workspace/scratch/cd4bd06ce68f/rtmidi
   ```

3. A one-off documentation check inspected all **49 Markdown links** in the
   three guides: **10 retained sibling links** and **39 canonical source links**.
   Every local target existed; the runbook heading fragment resolved. All
   **11 shell blocks** passed `bash -n`. All three files had terminal newlines
   and no trailing whitespace. The runbook's complete `B3MIDIREPLAY1` text
   matched the executed fixture byte-for-byte.
4. `git diff --check` passed for the tracked owned changes; direct whitespace
   inspection also included the new runbook. The finished note receives the
   same final owned-file whitespace/link check before handoff.
5. Ran five small actual application processes, each under a 15-second outer
   timeout, without repeating the full acceptance suites. Both successful
   cases used an absent private state path, explicit dummy drivers and copied
   schema-2 JSON. Native source/executable hashes were checked around this work.

| Process | Actual outcome |
| --- | --- |
| `--smoke-ms 600` | Exit 0; `Native SDL smoke passed`; 59 callbacks, 30,208 frames, 14 images; `errors.count=0`, MIDI source `none`, no held notes after joined shutdown. These counts are observations, not deadline requirements. |
| Runbook's 1200 ms MIDI script | Exit 0; 114 actual audio callbacks; complete/delivered/passed/final-acknowledged all true; 9 events, 7 accepted packets, no dropped packets, 3 Note Ons and 3 Offs, one connect/one disconnect, expression exactly 64/127, empty pre-shutdown notes and no held notes after shutdown. Native generation/callback counts remain zero. |
| `--list-midi` | Exit 1; printed `MIDI backend: ALSA`, then the real `/dev/snd/seq` missing-device error and failed ALSA client construction. This was not relabeled successful empty enumeration. |
| `--midi-upper-channel 2` | Exit 2; rejected duplication of the default lower channel with the exact distinct-1-through-16 error. |
| `--midi-script ... --smoke-ms 600` | Exit 2; exact mutually exclusive option error. |

The native executable used was:
`/workspace/scratch/cd4bd06ce68f/build-native/apps/standalone/hammond_standalone`.
The runtime working directory was
`/workspace/scratch/cd4bd06ce68f/a27-runbook-checks`. That scratch directory holds
the exact `example.b3midi`, `smoke.json`, `replay.json`, per-case stdout/stderr,
`results.json` and `docs-validation.json`. The complete replay text and expected
stable observations are preserved in the runbook, so reproduction does not
depend on retaining scratch.

The successful command forms were:

```sh
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  /workspace/scratch/cd4bd06ce68f/build-native/apps/standalone/hammond_standalone \
  --state /workspace/scratch/cd4bd06ce68f/a27-runbook-checks/smoke.b3controls \
  --smoke-ms 600 \
  --diagnostics /workspace/scratch/cd4bd06ce68f/a27-runbook-checks/smoke.json
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  /workspace/scratch/cd4bd06ce68f/build-native/apps/standalone/hammond_standalone \
  --state /workspace/scratch/cd4bd06ce68f/a27-runbook-checks/replay.b3controls \
  --midi-script /workspace/scratch/cd4bd06ce68f/a27-runbook-checks/example.b3midi \
  --diagnostics /workspace/scratch/cd4bd06ce68f/a27-runbook-checks/replay.json
```

## Integration handoff and open gates

[A24](24-midi-cli-modal.md) independently retains 15/15 methods and 95 actual
processes on the same final native executable, including 13 enumeration errors
and 11 correctly expected failed modal replays in this ALSA environment. That
record is separate from A27's five usage probes. [A25](25-legacy-native-acceptance.md)
now retains 4/4 suites, 40 methods and 240 native processes on schema 2/new
layout, preserving all historical fixture/demo bytes. Current operational
fixtures use `examples/standalone-input-v2/`; their grammar remains
`B3UIREPLAY1`. No broader acceptance count is inferred from either record.

A26 has the final three guide hashes and owns exact package inventory, copied
input qualification, installed-link acceptance and relocation. The integrator
owns current status/next steps/development log, the remaining actual assignments,
coherent-source qualification, README captures and guarded publication. This
note makes no all-sixty, full-project, newly completed CI or signed-release claim.

The next visual task must resolve the demonstrated thin-glyph failure and retain
fresh minimum/default/reference-size application captures, comparing with the
exact generated atlas image. Physical MIDI and audio acquisition, real hotplug,
timing/dropouts, native screen readers and Windows/macOS operation of this MIDI
slice need named devices/platforms and retained observations. The independent
scanner G5 failure, connected AO-28/Leslie work and measured calibration remain
open model gates. Source-art cabinet decoration and successful synthetic
transport do not close any of them.
