# Assignment 44 — independent pedal-demo acceptance

Owner: `/root/w08_a44_demo_acceptance`.

Assignment **44/60**, wave **8**, current 2026-11-13 pedal-development session.
This is one newly dispatched worker. The initial spawning UI reported aborted,
but this worker actually ran, notified root, completed its independent checks
and produced the three assigned files. No other agent was dispatched.

## Ownership and source basis

Owned only `tests/test_pedal_demo.py`,
`docs/reviews/PEDAL_DEMO_ACCEPTANCE.md` and this note. No bundle, provenance,
source inventory, core, renderer, CMake, shared status, ledger, existing test or
tool was edited. No staging, commit or push was performed; root integrates and
publishes under [AGENTS.md](../../../AGENTS.md).

Read standing instructions, current plan/handoff and the relevant pedal
catalog/evidence contracts, retained-demo documents, consumer and existing
historical-demo tests. Read the complete extracted text of atlas pages
**139–144 and 447**, including the page-144 shared-state linear-composition
gate and the nominal-model limit. This focused reading is not another claim
to have read the entire PDF. Used the cloud runtime skill; no dependencies or
network access were needed for this assignment.

The demo producer's files were treated as evidence to verify, not as authority
for expected output. Waited for assignment 43's complete 18-file directory to
freeze before pinning final provenance SHA-256
`da04261fe618b457d3e4162550d905efac5faa02049c2d00485ee0a186ea184b`.
The README independently matched
`54433a625801fcf3c1b7bbb9ca35d067118a6eb5eb2af9c46168954f44baf9c8`.

## Implemented gate

The ten-method standard-library Python suite:

- Pins every historical bundle file and the final provenance/source inventory;
  checks the exact 17-entry inventory of all other demo files.
- Reconstructs the retained Git tree from all 474 paths/modes/blob identifiers,
  without requiring historical objects in a shallow CI checkout.
- Parses the raw canonical RIFF header and all PCM frames independently of the
  producer, consumer and analyzer; recomputes all seven retained analysis
  windows using exact integer sums and squared sums.
- Checks the literal 38-event score, copied profile, catalog and schema-3
  nominal/unmeasured scope.
- Calls the existing legitimate consumer and tests relocation without file
  rewriting or execution of historical paths.
- Applies ten targeted changes to private copies, updates payload hashes where
  relevant, requires each intended semantic rejection, and reconfirms the
  original bundle's byte identities.
- Renders the full phrase at blocks 64, 127 and 1,024 and requires current-build
  complete-WAV partition equality.
- Renders separately constructed manual-only and pedal-only scores; requires
  active chord windows, exact silence after independent panics, zero clipping,
  and reconstruction of the full PCM within two quantization codes.

The historical hashes identify immutable evidence. Portable current-renderer
checks deliberately avoid an unpromised cross-platform historical float/PCM
bit-equality requirement. Existing CMake automatically discovers the new test
and supplies `HAMMOND_RENDER_EXECUTABLE` to all Python test entries. No new
hook or missing-binary skip was introduced.

## Actual commands and results

The first focused run passed all ten methods in **1.862 s**. After adding the
final provenance pin and explicit expected mutation diagnostics, the final
focused run passed **10 methods, zero failures, zero errors and zero skips in
1.936 s**. It performed five actual renders, totaling 720,000 stereo frames;
the retained example still represents three seconds of music.

```sh
HAMMOND_RENDER_EXECUTABLE=/workspace/scratch/f364bc93d920/a42-build/hammond_render \
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_pedal_demo.py
python3 tools/verify_render.py examples/demos/pedal-phrase-v1/bundle
```

The final run was invoked through the same unittest loader from a small
scratch-only observation script to retain output and replay metrics. The
script did not alter the tests, input artifacts or returned sample streams.
The consumer returned `verified_retained_bundle`, schema 3, six verified
payload artifacts, external renderer `matched` and replay `not_performed`.
Authentication and source/build association remain `not_established`.

Separately ran `git rev-parse COMMIT^{tree}`, `git ls-tree -rz COMMIT` and
`git cat-file --batch` for source commit
`d7b886103f8c9d4649ffa1c35930b79808217a3d`. All **474** records matched actual
Git file modes, blob identities, bytes and SHA-256, and the tree matched
`018c3897889aaae0070f632981e0c889a35cad30`.

Replay used the existing coherent assignment-42 SDK-free Release build,
renderer SHA-256
`9b80a370078e87b4535b6d4d7fee7ed79f9949c443f1bd0432ed54b21c9e39b6`.
Independently rehashed all **476** source files against its existing
`a42-source-identities.json`, SHA-256
`f252333abfc019e31c85778b34f3eccdcaab3d2bb8f6e242ed6c2414a1a3d508`.
The source is the published W6 base with the frozen assignment-37 CLI and
assignment-42 metadata changes; no core/render DSP change or mismatched live
header/library was used. This assignment reused that build and does not claim
to have compiled a new executable or run the full CTest/platform matrix.

| Independent observation | Result |
| --- | --- |
| WAV format | 576,044 bytes; 144,000 identical-channel stereo PCM16 frames at 48 kHz |
| WAV SHA-256 | `a3d1958189e811b8e353a75380d380016db5286eb08a2005626d95df64dde6f1` |
| PCM SHA-256 | `3107d186bb811b2cf1a2a3497422f5d77169f92ca2c9c7f22a1553482141c77c` |
| Historical versus current blocks 64/127/1,024 | Complete WAV/PCM bytes all identical on this platform |
| Exact integer PCM maximum / sum of squares | `2762 / 81653430143` per channel |
| PCM whole-file peak / RMS | `0.08428955078125 / 0.02298031808643901` |
| Float peak / RMS | `0.08429475128650665 / 0.022980303816301697` |
| Clipped frames / channel samples | `0 / 0` |
| Leading / trailing silence | Every 4,800 / 24,000 frame pair is zero |
| Component sum maximum error | One PCM code, within the two-code bound |
| Component sum exact / one-code frames | `115107 / 28893` |
| Combined versus manual-only differing frames | `115074` |
| Altered copies | All ten reject for their intended semantic reason |

No production, render or test defect was found. All expected negative cases
failed in private copies; the retained bundle stayed unchanged. An initial
documentation lookup used the nonexistent
`docs/reviews/PEDAL_AUDIO_ACCEPTANCE.md`; the correct
`docs/PEDAL_AUDIO_ACCEPTANCE.md` was then read. This was a read-path error,
not an acceptance failure or an implementation change.

Scratch-only `a44-tests.log` and `a44-acceptance-run.json` retain the immediate
test/replay observations for root's inspection. Durable commands, source
identities, metrics, rejection reasons and limits are retained in this note
and the [acceptance review](../../reviews/PEDAL_DEMO_ACCEPTANCE.md), so future
agents do not depend on these temporary files.

## Handoff and next step

Root should freeze the three owned files with assignment 43's unchanged demo,
run `python_test_pedal_demo` in the combined coherent checkpoint, update shared
status/navigation and commit/push the accepted work. The WAV and compiled
profile are globally ignored and need root's explicit staging. No permission
request is needed for the already authorized integration/publication workflow.

The review contains the complete independent result and ten mutation reasons.
Preserve the historical artifact when introducing future measured models;
admit a new named demo and keep the current model identity and evidence scope
visible. No subjective listening, measured physical fidelity, calibrated
pedal footage, reactor/loading behavior, low-wheel spectra, contact timing,
scanner/AO-28/Leslie model, native DAW/device operation or deadline performance
was established here.
