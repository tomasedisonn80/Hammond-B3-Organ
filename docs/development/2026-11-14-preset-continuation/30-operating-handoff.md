# A30 — current operating guide and resumable handoff

Actual worker `/root/w05_a30_operating_handoff`, logical wave 5, 2026-11-14.
Owned only `docs/PRESET_RUNBOOK.md`, `docs/PRESET_HANDOFF.md` and this note.
No production, existing guide, CMake/install, shared status, manifest or Git ref
was edited. No commit, push or child agent. No preserved build was reconfigured
or rebuilt.

Read `AGENTS.md`, README/current status/next steps/log, the complete M0–M9 plan,
the preset source-review consolidation and frozen selection/core/state/UI
contracts. Reviewed accepted focused records and the current native diagnostic
contract. The six designated readers remain the complete-PDF readers; A30
does not claim a seventh complete reading.

## Delivered guidance

The runbook gives current source and installed operation: exact build options
and test aggregates, pinned dependency acquisition, native/MIDI/VST3 paths,
all twelve selector meanings, independent editing and sounding, Cancel memory,
upper-B percussion eligibility, state4 with legacy readers, bounded native
replay/capture, verified offline rendering, staging and failure recovery.
Repository URLs keep optional references usable from an installed copy; essential
launch/preset/state/recovery instructions are self-contained.

The initial handoff distinguishes the current development overlay from its
published baseline, maps implementation to authoritative contracts, links
accepted focused evidence and makes the remaining integrated/platform/visual
and physical gates explicit. The integrator or later assigned handoff owner
must update its final publication/source checkpoint; it is not a declaration
that all sixty assignments or the whole M0–M9 instrument are complete.

Identified an installation/documentation gap: the package currently stages the
older MIDI guide with 45-parameter, state3, PLAY/CANCEL and diagnostic2 prose.
Reported it to root. Root assigned the later install owner to stage the current
guide and coordinate exact payload acceptance, and the later documentation
owner to reconcile the older guide. A30 did not modify either owner's paths.

## Source inspection and executed commands

Working directory:
`/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`.
Inspected HEAD `35554c068492fe2b20c1f8a602d8354ae762dc42`, tree
`6a6881eeee1943665694e988208b2d6710731919`. The active preset code is an
uncommitted overlay, so those identities alone do not identify the executables.
Checked the shown options/targets against root/app/plugin CMake, the actual
main CLI parser/help, fixed-data generation, current state/parameter contracts
and pinned dependency locks. The 17-input inspection map at
`/tmp/hammond-preset-a30/review-inputs.json` has SHA-256
`e0ea3571e9968e4889cb8f8724d5e997cb31345c29e87389082d4a06d02763c9`.
This map is a documentation review record, not a coherent-build manifest.

Executed help successfully for A28's native binary, A24's renderer, current
`render_fixture.py` and `verify_render.py`. Then executed the runbook's exact
seven-action script with a private temporary state/screenshot/report directory:

```sh
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  /tmp/hammond-preset-a28/build/apps/standalone/hammond_standalone \
  --width 960 --height 700 \
  --state /tmp/hammond-preset-a30/native-example/preset-controls.b3controls \
  --input-script /tmp/hammond-preset-a30/native-example/preset-example.b3ui \
  --screenshot /tmp/hammond-preset-a30/native-example/preset.bmp \
  --diagnostics /tmp/hammond-preset-a30/native-example/preset.json
```

The process exited **0**, with native schema **3**, all replay completion,
delivery, acknowledgment and pass flags true, seven scheduled/pushed actions,
one accepted Note On and no Note Off before shutdown. It retained Upper note 60
while reporting raw fixed modes `[1,0]`, effective selections `[0,11]`, remembered
banks `[1,1]` and routes `[false,true]`. Errors were zero, shutdown released all
notes, the BMP existed, and the saved state4 contained the literal cancelled
Upper C# record. The 175-byte script is printed completely in the runbook.
No new raster/visual-fidelity inspection is claimed by this operational check.

Executed the runbook's producer/verifier commands, substituting A24's exact
renderer path and `/tmp/hammond-preset-a30/offline-evidence` for the unused
result directory. Parameters were the retained selector score, 96,000 frames,
48 kHz, block 127, seed 7, zero initial drawbars/pedals and percussion off.
Both commands exited **0**. Producer status was `succeeded`; the independent
consumer reported `verified_retained_bundle`, schema 3, six retained artifacts
and a matching executable. Verification reported replay `not_performed`, with
authentication, source-build association and physical fidelity not established.

| Actual artifact | SHA-256 |
| --- | --- |
| A28 native executable | `557acb27d16cfc77815c278778335f8418b471b563d1b93a47bf3051eae68c82` |
| Native example script | `bde0e91157b880f68d61eb283f4c7812390e088d1c5c4a438c2ae322f2a180da` |
| Saved state4 | `a9fa2dbcffe9fbd9c96845db39c47226db048a66a569fad864528431ce5e6baf` |
| Native diagnostics | `905e036bbf2ae98033953e02a960f0f0e11645f3e3b7f2b616a6140908c58339` |
| Native BMP | `c6ae2261243c6c3f3642e5da4d25c9438d60c90fe68fee3c3b41c906431d90c9` |
| A24 offline renderer | `ade81c8062b28a862a01c48f86220320558d893f19ab78a073deb1acf754f93b` |
| Offline WAV | `75ba604050b839507208266ec602d336f1aad6882f70163d75d8f5c191427da5` |
| Offline manifest | `ab9cbc5083fb0cde176491cc436ae81f5c3ca1c44a650fdcb4bee20d4e514fa9` |

The native and offline binaries come from **different coherent worker builds**;
these examples are not one combined-source qualification. A28 and A24 own their
build manifests/toolchain evidence. Temporary commands/results and the complete
diagnostics remain under `/tmp/hammond-preset-a30/` for integrator retention.
No dependency was downloaded or package installed. The native run used only
the explicitly selected SDL dummy path; no physical MIDI/audio device was opened.

## Handoff and limits

Source options and target names were checked against actual code; the bounded
native and offline examples passed on their first execution. Source build,
complete CTest matrices, installation, macOS/Windows, DAWs, physical devices,
callback deadlines and literal 1:1 UI fidelity were not executed by A30.
The runbook's commands are setup instructions, not claimed new build passes.
Final scoped whitespace, Markdown heading/fence and link checks passed for all
three owned documents; 47 repository/local link targets resolve. The runbook
script is byte-identical to the executed 175-byte input. All 17 inspected source
inputs still match their recorded hashes. The next owners complete the integrated
gallery, installed guide/payload, exact-source gates and publication while
preserving the original baseline failures and source limits.
