# Checkpoint

## Current state

Forty-one actual workers are dispatched; 38 are accepted and Waves 1–6 are complete. Independent comparison, gallery, resource, compatibility, painter and build integration admissions are accepted. Current README, status, next actions, full project/reading guide and handoff have been reconciled. Wave 7 is deriving concrete next converter, causal-audio and full-window visual gates. The ledger owns exact accepted counts. Earlier sessions never contribute worker credit to this request.

**First coherent local qualification passed:** the 131-step all-target rebuild and all **210/210 CTests in 191.89 seconds**, with no failures. All 505 recorded source/test/tool/data inputs stayed unchanged through qualification. See reports/coherent-qualification.json, its compressed inventory and original logs. This is Linux GCC Release with dummy SDL, not hosted platform or physical-device qualification.

Post-review hardening makes missing or empty probe setup fail both native Python suites and adds the Upper-rack raster fixture as native sanitizer gate 22, preserving the previous 21 mappings and all timeouts. Eight negative setup cases and both configured suites pass. The refreshed whole suite passes 210/210 in 191.90 seconds against 505 unchanged inputs; see reports/final-coherent-qualification.json. One later EOF empty-line cleanup has its own affected rebuild/test receipt, with identical binary bytes; reports/publication-source-qualification.json binds the composed final inputs. Original receipts remain unchanged.

M3: isolated integer-grid trajectory, exact Fraction oracle, known answers, lifecycle rollback and strict transport are implemented. Differential testing passed 11 methods and 199 native probe invocations. CLI testing passed 17 methods and 150 processes; a source-identified Windows CRLF/Ctrl-Z issue was repaired with guarded raw-stdin setup, then all native tests passed. Windows execution remains pending CI. The resource receipt and independent admission verify 192 zero-allocation/deallocation API scopes, 113,056-byte local object, fixed staging and measured per-call bounds including 4,608 edges and 80,640 comparisons. No audio filter, converter, full-organ indefinite runtime, Engine integration, deadline or physical model is claimed.

M9: all 96 genuine paired cases pass across 307,095,606 pixels, with zero changes outside the independently derived Upper-inset support and 37 exact required whole frames. Five local reference screens pass; baseline failures remain. Original report bytes are losslessly retained in reports/A20-raster-run1/report.json.gz. Independent comparison admission is accepted. Twelve actual app captures in examples/demos/upper-rack-material-v1 passed a separate 641-check gallery audit and direct full-frame inspection. Literal whole-interface 1:1 remains unmet.

Compatibility: original Engine, 91 shared sources, 47 parameters, state4/readers 1–3, UUIDs, PDF, art and prior fixtures are preserved. The dry fixture's entire WAV and all 16,384 decoded samples are identical; A30 distinguishes the old baseline report's mislabeled whole-WAV hash from the actual decoded-PCM hash without altering that original report.

The runnable causal-grid guide and README's current UI section are written. Remaining workers, final integrity, guarded main publication and exact-source hosted outcomes remain to complete. Latest remote main observation remains base 4aac394cde4da40906b615573a8779aee2d9a37a. Storage remains approximately 51 GiB free; original binaries are preserved in ../baseline/ and optional scratch instrumentation in ../resource-work/.

## Setup

Writable checkout: `/workspace/scratch/177e78b1ac09/Hammond-B3-Organ`. Base `4aac394cde4da40906b615573a8779aee2d9a37a`. One intended Release native build: `/workspace/scratch/177e78b1ac09/build-native`. Existing SDL in `/workspace/scratch/ade21b726509/SDL2` is a read-only dependency, never edited or cleaned by this session.

Initial free storage: approximately 54 GiB. Root preserves actual logs and baseline binaries before source changes.

## Next

Execute the remaining independent integration/continuation/publication reviews using sixty actual distinct workers in ten groups of six. Preserve the qualified production inputs. Resolve any concrete remaining findings and rerun only affected gates. Update the actual ledger, checkpoint, status, README and next-step instructions; check repository integrity after prose changes. Fetch and inspect fresh remote changes, publish accepted commits to main without force, independently fetch/verify commit/tree/parent and observe the thirteen required hosted jobs at the published source.

## Local build recipe

From the writable repository (the pinned SDL checkout is verified and read-only):

```sh
python3 -B tools/acquire_sdl2.py --verify-existing /workspace/scratch/ade21b726509/SDL2
cmake -S . -B ../build-native -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_ENABLE_MIDI=OFF \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/ade21b726509/SDL2 \
  -DSDL_X11=OFF -DSDL_WAYLAND=OFF -DSDL_ALSA=OFF -DSDL_PULSEAUDIO=OFF -DSDL_JACK=OFF
cmake --build ../build-native --config Release --parallel 3
ctest --test-dir ../build-native -C Release --output-on-failure --no-tests=error --parallel 3
```

This local configuration uses dummy SDL and cannot qualify real display/audio/MIDI devices. Normal desktop acquisition/setup remains in the project README. Baseline binaries, the unchanged painter and dry WAV are in `../baseline/`, owned by this session. Full baseline results: 203/203 passed, 192.21 seconds; executable SHA-256 `eb9a501ec60d5a90a398ffbf14e21a21967712589c155b54c8be164a71bd823c`.
