# Conversion/material continuation: current setup and handoff

This is the active 16 November 2026 continuation from base `a411268fd498f65c083203137831bf5afed83bd8`. Read [AGENTS.md](../AGENTS.md) and the entire [M0–M9 plan](PLAN.md) before selecting work. The [session entry](development/2026-11-16-conversion-material/README.md), [checkpoint](development/2026-11-16-conversion-material/CHECKPOINT.md), [scope](development/2026-11-16-conversion-material/SCOPE.md) and [actual assignments](development/2026-11-16-conversion-material/assignments.json) govern recovery. This handoff is updated as later waves are accepted; it is not final closure.

## Published and accepted

- All 500 atlas pages were freshly covered by six distinct readers; [coverage](development/2026-11-16-conversion-material/reports/atlas-reading-coverage.json) binds ranges and extract identities. This supplies no missing physical measurements.
- Explicit `fractional-to-contact-grid-rne-v1` uses exact nearest/even arithmetic, preserves the complete event preorder or refuses, and produces a reconstructible trajectory certificate. All 71 retained inputs have independently checked outcomes: 51 accepted, 20 refused. The [guide](CONTACT_GRID_CONVERSION_GUIDE.md), [contract](CONTACT_GRID_CONVERSION_CONTRACT.md) and independent [native review](reviews/CONTACT_GRID_CONVERSION_NATIVE_REVIEW.md) distinguish trajectory, native-grid and audio claims. The current review records 557 native processes with complete padded snapshots. Audio accuracy remains unqualified.
- The atomic CLI preserves existing outputs on precommit refusal. Independent resource/transaction tests retain observed defects and fixes. The separate [five-file installer](CONTACT_GRID_CONVERSION_INSTALL.md) preserves the original 48-file component. Independent [installation acceptance](reviews/CONTACT_GRID_CONVERSION_INSTALL_REVIEW.md) passes 13 methods / 93 processes, including relocation after private source/build deletion.
- Accepted Lower-rack material is bound by the [v2 result](reviews/LOWER_RACK_COMPARISON_V2_RESULT.md): all 98 pairs / 35 inequalities / 166 extra foreground guards. Original v1 failure stays visible. The [actual gallery](../examples/demos/lower-rack-material-v2/README.md) and [compatibility review](reviews/CONVERSION_MATERIAL_COMPATIBILITY.md) retain source/pixel and dry-audio evidence.
- First publication is `3520c96adcdcf4ce4bcb860082354bf0050a89c3`, exact tree `1013bbd914a0957ca2c164ef02ca5410a8dcde6b`, parent `a411268fd498f65c083203137831bf5afed83bd8`. [Receipt](development/2026-11-16-conversion-material/reports/wave04-publication.json). Completed exact-source matrix: **11 of 13 jobs pass**. macOS core fails two test-only path assumptions; Windows core fails the same unresolved-parent comparison. All five native standalone and all three native VST3 jobs pass. [Evidence](development/2026-11-16-conversion-material/reports/wave04-hosted-complete.json) and [raw macOS log](development/2026-11-16-conversion-material/reports/hosted-3520c96-macos-core.log) are retained. A33 repaired the two test portability assumptions without changing production. The [repair review](reviews/CONTACT_GRID_CONVERSION_PLATFORM_REPAIR.md) retains original failures, Unicode coverage and narrowly scoped capability handling. Its 46 methods pass locally; exact repaired macOS/Windows hosted runs remain pending. Old hosted successes do not qualify changed source.

## Current development and next sequence

**Waves 1–5 are accepted. Wave 6 has dispatched all six actual workers, A31–A36.** The [actual ledger](development/2026-11-16-conversion-material/assignments.json) records acceptance independently from dispatch; followups do not count as new workers.

The scoped T1 manual footage typography is admitted by A25/A28/A29/A32: 44 independent cases, 110 paired full frames, zero changes outside the independent glyph allowance, 44 exact whole frames and complete literal labels. The [visual admission](reviews/FOOTAGE_TYPOGRAPHY_VISUAL_ADMISSION.md) reviews all eighteen labels at three sizes; the [actual gallery](../examples/demos/footage-typography-v1/README.md) contains unchanged application captures. The precise Upper/Lower material fixture transitions retain their original non-typography requirements. Whole-interface 1:1 remains unmet.

The coherent all-target build succeeded and the [full local run](development/2026-11-16-conversion-material/reports/wave06-before-rim-qualification.json) passed **218 of 219** tests with all 506 tracked inputs unchanged during execution. The sole failure is the broader product fixture's old manual-label font expectation. A35 owns the precise transition and reversible audit. Root rebuilt it successfully, then its fresh 76-case test passed in 18.25 seconds. All other 505 recorded inputs remained identical; the [composite qualification](development/2026-11-16-conversion-material/reports/rim-before-qualified.json) binds this sequence. The original failure remains in the complete test log. Do not describe this initial full run as all passing.

A31 admitted the [decorative rim contract](design/KEYBOARD_RIM_CONTRACT.md), exact manifest and independent 32-case fixture after source/SDL preflight. A genuine pre-rim application and fixture set is retained in `../baseline-typography`, bound by [identity](development/2026-11-16-conversion-material/reports/rim-before-identity.json). Its 32-case rim baseline passed. A34 remains read-only until root qualifies and commits the T1 checkpoint. A36 prepares independent paired comparison. The proposed crop is decorative only; raw pixels, unoccluded final rows and retained shadow composition are distinct assertions. Scaled SDL clipping has an independently reproduced interior sampling difference; caller-exterior preservation remains exact.

Next: accept A35's final review, publish T1 and the platform-test repair, then release A34 and complete A36's candidate comparison. Independently qualify the rim compiler, optional texture lifecycle, packaging and actual native captures before acceptance. Further reference typography, native interaction journeys, converter boundary coverage and complete publication/recovery documentation remain dependency-aware work in waves 7–10.

## Working setup

| Resource | Identity and owner |
| --- | --- |
| Writable checkout | `/workspace/scratch/0d55e62af118/Hammond-B3-Organ`; root integrates and publishes; workers edit assigned paths only |
| Coordinated build | `/workspace/scratch/0d55e62af118/build-native`; one Ninja Release configuration |
| SDL | Read-only `/workspace/scratch/ade21b726509/SDL2`, 2.32.10, commit `5d249570393f7a37e037abf22cd6012a4cc56a71` |
| Local tools | GCC 14.2, Python 3.12.14, CMake 3.31.6 |
| Preserved genuine stages | `../baseline` original app/painter/fixtures; `../baseline-lower` accepted Lower and pre-T1 fixture; `../baseline-typography` genuine T1/pre-rim application and fixtures |
| Active settings | Tests/standalone ON; MIDI/VST3/sanitizers OFF; X11/Wayland/ALSA/PulseAudio/JACK OFF |
| Storage | One shared checkout/build; 46 GiB free at latest observation. Never delete other sessions' data |

Recover the existing cache rather than substituting a new backend. Inspect source/index before reconfiguration. Root's reproducible dummy-SDL setup is:

```sh
python3 -B tools/acquire_sdl2.py --verify-existing /workspace/scratch/ade21b726509/SDL2
cmake -S . -B ../build-native -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=ON \
  -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_ENABLE_MIDI=OFF \
  -DHAMMOND_ENABLE_SANITIZERS=OFF \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/ade21b726509/SDL2 \
  -DSDL_X11=OFF -DSDL_WAYLAND=OFF -DSDL_ALSA=OFF \
  -DSDL_PULSEAUDIO=OFF -DSDL_JACK=OFF
cmake --build ../build-native --parallel 3
ctest --test-dir ../build-native --output-on-failure --no-tests=error --parallel 3
```

The original baseline passed 210/210. Wave 3 rebuilt all affected targets and passed 212/213; its sole archived-relative-link failure was repaired without modifying the archived bytes, and the focused integrity rerun passed. Five repaired converter suites then passed. These are distinct source-bound results. The current coherent run is 218/219 with the isolated historical product-label expectation described above; its repair needs fresh compilation and focused qualification.

For an ordinary desktop, use [README setup](../README.md#build-and-launch-the-native-application) in a distinct native-backend configuration. Launch 1672×941 for the wide interface; default 1280×900 is compact. Dummy captures do not qualify physical display/DPI, MIDI, audio device callbacks or semantic accessibility.

## Publication and recovery

The current shell can read the HTTPS Git remote but cannot authenticate a Git push. The connected `tomasedisonn80` GitHub account successfully published exact Git objects and moved main with an expected-head, nonforced update. Remote tree creation returned a timeout despite the complete exact tree existing; independent tree retrieval established success before commit/ref publication. Never assume timeout means failure or success; read back the addressed object/ref. After fetch, root preserved the original local commit under `refs/checkpoints/local-wave04` and aligned HEAD to the identical published tree without changing index/work files.

For each next accepted chunk: freeze the intended committed tree, inspect new remote head, publish exact contents without force, fetch independently, compare commit/tree/parent/content, and observe hosted jobs at the exact new revision. Preserve original failures and immutable receipts. Do not stage active workers' unfinished paths. Final strict session validation requires all 60 actual accepted notes in ten waves; it verifies record consistency only.

The nominal dry Engine, 91 free-running sources, 47 parameter identities, B3CONTROLS4/readers1–3, plugin UUIDs, all 147 playing keys, 24 presets, four banks and 68 controls remain preserved. Missing specimen calibration, loaded AO-28/scanner/Leslie modeling, live contact audio, indefinite/full-organ capacity, release rights and signed distribution remain substantive future work under M0–M9.
