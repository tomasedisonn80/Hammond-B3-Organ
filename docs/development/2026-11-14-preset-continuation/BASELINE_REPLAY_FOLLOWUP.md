# Remaining hosted baseline replay failures

At published `35554c068492fe2b20c1f8a602d8354ae762dc42`, ten of eleven hosted
jobs passed. The macOS standalone job compiled, installed and passed all startup,
output-path, state, musical-workflow and other checks affected by the two prior
repairs. It finished **22/24 CTests**, leaving two replay tests to diagnose.
This is a baseline result, before publication of the preset implementation.

The [retained job identities and copied diagnostic](reports/baseline-macos-replay-followup.json)
identify the exact source and failing job. The actual failures were:

| Suite / case | Observed failure | What the evidence establishes |
| --- | --- | --- |
| `test_standalone_midi_cli` / modal Escape and unapplied channels | Replay did not finish delivery/acknowledgment within the existing two-second drain allowance. | The test printed the application error but did not retain its copied diagnostic on this assertion. Its cause remains unclassified. |
| `test_standalone_native_midi_replay` / focus, resize, Help and MIDI Apply | No fully acknowledged observation in the test's `[400,590)` ms interval. | The captured run completed successfully and retained the correct external notes/pedal. Focus release was submitted at 483 ms, applied by the observation at 664 ms; the next fully acknowledged observation was 723 ms. The narrow interval was missed. |

The second captured run reports both UI and MIDI replay `passed=true`, zero
application errors, zero Session recovery, zero queue overflow and the expected
final external owners. Its software renderer painted 30 images during a 1.832-second
process run. These observations are evidence to investigate scheduling and test
boundaries; they do not establish a callback or display deadline pass.

The native integration owner must retain complete diagnostics on failed replay,
reproduce or isolate the remaining cases, and distinguish an application defect
from a test that assumes an unqualified wall-clock observation latency. Preserve
ordered events, acknowledgment and musical ownership assertions. Do not relabel
the failed run as a pass or hide it with an unchanged retry. Actual hosted
verification remains required after a justified correction.
