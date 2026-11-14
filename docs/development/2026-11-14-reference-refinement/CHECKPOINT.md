# Live checkpoint

Starting main: `8bd999efc13e309b932e6ac41d72ceb7b9b80a5f`. One fresh shallow checkout is in use. Historical worktrees and the interrupted session remain preserved.

## Completed

Wave 1: all six actual readers accepted; every one of the 500 PDF pages read in full text. Selected original pages and exact reference/native captures were visually inspected. See notes A01-A06 and `docs/research/REFERENCE_REFINEMENT_ATLAS_REVIEW.md`.

The unchanged native baseline built and passed **147/147 CTest suites in 145.26 seconds**, using GCC Release, pinned SDL2, MIDI OFF and VST3 OFF. Native test fixtures selected dummy drivers. Logs and product-source hashes are in `reports/baseline.json` and adjacent logs. This is engineering verification, not physical audio or visual equality.

## In progress

Wave 2 freezes exact layout, materials, desktop acceptance, nominal M7 R2/R3 APIs, inspection/pending behavior and independent setup/scope review. The proposed wide layout moves all 25 pedals beneath the cabinet and deepens both complete 61-key manuals toward 144 px, while preserving compact/Flat operation, all 47 parameters and state4. The actual manifest owns dispatch and acceptance counts.

Root also built an X11-capable native executable with pinned RtMidi and extracted Debian development headers. The actual cloud desktop Terminal is visible. Sky text entry initially reported no focused window; documented key input works. Desktop and executor share workspace files while their process/display namespaces differ. Root owns CUA and will retain only observations actually made.

## Exact setup

Task root: `/workspace/scratch/1bb6ee17ad7e`. Repository: `Hammond-B3-Organ`. Binaries: `build-native/apps/standalone/hammond_standalone` and `build-desktop/apps/standalone/hammond_standalone`. Actual CMake/CTest binaries are under `build-tools/cmake/data/bin/`; Ninja is `build-tools/bin/ninja`. External `SDL2`, `rtmidi` and `native-sysroot` are shared. Configure/build logs are in the task root. No production edits were present at this checkpoint.

CLI Git writes lack credentials. The connected GitHub account confirms repository write access. Publish exact staged trees through GitHub Git-data tools with an expected head and `force=false`; fetch and verify the remote tree before advancing local main. Preserve unfinished worker files and do not ask again for authorized publication.

## Next

Finish wave 2, implement disjoint UI/inspection/M7 files in wave 3, independently verify in wave 4, then continue integration, native checks, actual captures and final documentation in later waves. The requested total is 60 new actual workers in ten logical waves; historical workers never count toward it. Publish coherent accepted checkpoints and verify the exact remote revision.

Initial available space was about 59 GB. Use one checkout, two bounded build trees and shared dependencies. Check disk use at wave boundaries. Preserve compact reports before removing only session-owned reproducible intermediates.
