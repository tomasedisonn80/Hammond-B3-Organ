# Assignment 57 — whole-project milestone reconciliation

Actual worker: `/root/cal_w10_a57`, logical wave 10 of the
`2026-11-13-calibration` session, 2026-11-14. This is one newly dispatched
assignment; no child or prior-session worker was counted. Owned only this note
and [CALIBRATION_MILESTONE_RECONCILIATION.md](../../reviews/CALIBRATION_MILESTONE_RECONCILIATION.md).
Root owns shared documents, substantive acceptance, ledger and publication.

## Result and decisions

The review maps M0–M9 to present engineering, evidence and concrete missing
software/physical inputs. Engine's actual graph remains nominal dry; separate
scanner/rotary research classes do not implement an audible AO-28/Leslie chain.
It preserves the scanner G5 failure, physical unknowns, existing track ownership
and concrete pilot/MIDI/accessibility/typed-registration next outputs.

The 106-suite calibration source, historical native configurations and d7 hosted
review owned by 55 stay distinct. Inspection is not another runtime test, and
worker counts do not complete the instrument. No production change was needed.

## Actual source and evidence read

Inspected published source `d7f6100010eb4cdd028ec93000cd9e893ac6d190`, tree
`0140c737de4db28288b118744c2beef57976697f`, against full-gate local source
`48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a`. At first inspection local HEAD was
`7296af05d846a89f8975ffb309191a332a0686c2`, tree
`589eaedabc917c2cfe53d5b0ad51e0b0cc186ae8`; `origin/main` resolved to d7. Root
subsequently recorded the nine-wave handoff at `eb490af`, which I reread for
current continuation wording. No uncommitted code was used as a new qualified
source. Remote publication/fetch was performed by root; this worker read the
fetched objects and independently checked their local contents and ancestry.

Read AGENTS/PLAN, relevant current README/status/next-step/log/handoff sections,
ROTARY_SCOPE/session README, current release assessment, both atlas review
navigation records and the acquisition guide's scope/A1–A6 dependencies.
Inspected actual Engine members/rendering, TonewheelBank, RotaryMotion interface,
CMake selection, adapter input paths and four data documents. Test paths were
checked for presence/source identity, not executed. Truncated read output was
reread in smaller calls. Complete PDF reading belongs to the six session readers;
this worker rehashed it but did not claim new full-text/image/external-source
review or measurements.

## Executed finite checks

One independent read-only Python audit used `git show` for each selected path.
Every **48-file** live byte sequence equals both the d7 and 48a1907 blob. The
ordered inventory of `{path, bytes, sha256}` rows, serialized with
`json.dumps(rows, sort_keys=True, indent=2) + "\n"` and UTF-8, is **7,307 bytes**,
SHA-256 `6af696a3be2f4e177f075d48573532010013ff1f95ddd3aa95e1ee1510ff15a6`.
The order is retained below; individual blobs remain recoverable from both exact
Git objects. The private execution result is
`/workspace/scratch/c9f3ead4c910/a57-milestone-check.json`; its presence is not a
setup dependency or a substitute for the retained source identities.

```text
CMakeLists.txt
include/hammond/Engine.h
src/Engine.cpp
include/hammond/TonewheelBank.h
src/TonewheelBank.cpp
include/hammond/Types.h
include/hammond/ControlState.h
src/ControlState.cpp
src/ControlStateIO.cpp
src/ContactBank.cpp
src/Percussion.cpp
src/PedalVoice.cpp
include/hammond/ScannerLine.h
src/ScannerLine.cpp
include/hammond/ScannerRotor.h
src/ScannerRotor.cpp
include/hammond/RotaryMotion.h
include/hammond/RotaryTypes.h
src/RotaryMotion.cpp
tools/rotary_reference.py
data/profiles/nominal-unmeasured-v1.json
data/parameter-registry.json
data/registrations/atlas-chapel-nominal-v1.json
data/capture-planned-example.json
tools/capture_audio.py
tools/capture_common.py
tools/capture_corpus.py
tools/compare_capture.py
tools/capture_job.py
tools/capture_readiness.py
tools/capture_study.py
tools/verify_capture_report.py
tools/make_capture_demo.py
tools/validate_capture.py
apps/standalone/main.cpp
apps/standalone/Session.cpp
apps/standalone/InstrumentView.cpp
plugins/vst3/Processor.cpp
plugins/vst3/Controller.cpp
tests/test_engine.cpp
tests/test_console_engine.cpp
tests/test_pedal_engine.cpp
tests/test_scanner_native_ac.py
tests/test_scanner_rotor.cpp
tests/test_rotary_reference.py
tests/test_capture_cli_pipeline.py
tests/test_capture_graph_scale.py
apps/standalone/native_tests/test_standalone_workflows.py
```

Additional actual assertions:

- `git diff --name-only 48a1907 d7f6100` returns **40 paths**, all AGENTS/README or
  under `docs/`. No production/test/build/model/data difference is present.
- `git merge-base --is-ancestor` succeeds separately for qualified full source
  `5e19022c8696023bb1aa841ebea2eaeec0d719a3`, allocation source
  `d377fab7a840dc6d7a499fdf576d0dd8bb5dd4c1` and preserved standalone follow-up
  `7ec79fb1c80793cf2f1bd6418abc081a547528c5`, against d7.
- Actual JSON contains **91** profile sources, **45** parameter records and
  **18** chapel registrations. The planned capture remains `planned` and has
  **zero** files. These are structure/data observations, not played-note,
  instrument or acquisition tests.
- The PDF remains **21,248,265 bytes**, SHA-256
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Final owned-document checks verify all 23 relative Markdown targets, UTF-8, final LF,
  no CR/trailing whitespace, and no repository writes outside these two records.

An initial read-only search guessed absent `include/hammond/Parameters.h`;
the actual registry is `data/parameter-registry.json`. No mutation resulted.
The finite audit completed on its first run, with no changed expectations.

## Handoff and limits

The initial shared current-status prose still pointed to the earlier publication
and counts. Root was already reconciling it and supplied `eb490af`; the updated
next steps now names d7, nine accepted waves and the concrete acquisition output.
No additional correction was requested. Link this reconciliation from the final
handoff if useful, preserving the source-specific historical records.

No C++ build, CTest/unittest suite, CLI workflow, native app, hosted job, actual
hardware acquisition, constrained fitting, listening, device/DAW test or release
qualification was run by this worker. Those results belong to their named
owners and sources. Assignment 55's d7 hosted results were still being reviewed
when this record was prepared; no future pass is inferred here. Root's final
manifest/checker must follow acceptance of every actual worker, including this
one, and must not count these inspection assertions as new runtime tests.
