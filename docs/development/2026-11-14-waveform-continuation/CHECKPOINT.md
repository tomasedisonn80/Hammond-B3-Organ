# Waveform continuation checkpoint

## Current ownership and progress

This owner-requested session starts at `2e161dc3a60fc3442051799574feed37bffbfc5c`.
The actual assignment manifest records **29 dispatched distinct workers** in ten
logical waves of six: A01–A26 accepted, A27–A29 running. Dependency-ready tasks
can overlap the preceding wave while the three worker slots are reused. Other
sessions and historical workers are never counted here. The complete 500-page
atlas reading is recorded in `docs/research/WAVEFORM_ATLAS_REVIEW.md`.

Current local HEAD is `0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b`, integrating
the concurrently published header refinement without discarding local renderer,
UI paint or documentation work. The exact integration receipt is
`reports/wave3-concurrent-integration.json`. Our earlier published checkpoint is
`26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`; its twelve hosted jobs passed, but
those jobs do not qualify the later uncommitted renderer. A new coherent source
checkpoint will be published after the running source-bound full experiment.

## Implemented and accepted slices

Independent R4 histories, streaming propagation and transactional stereo
renderer are implemented. Fixed storage, two-frame algorithmic lag, four paths,
same-cubic interpolation, signed summation, offset-N/zero-frame event semantics,
reset and stopped reconfiguration follow the frozen renderer contract. The dry
Engine, 47 parameters, B3CONTROLS4/readers1–3 and existing R2/R3 remain unchanged.
R5 audible policy, R6 live integration and physical M7 gates remain separate.

Independent history acceptance passed 774,721 checks and all 33,280 static grid
coordinates. Low-band error 0.00348056414 passes the frozen 0.005 budget; full-band
error 0.99539807929 remains characterization. Analytical renderer acceptance
passed 57,568 samples; streaming paths passed 345,828 checks including 3,940 exact
R3 comparisons. Both actual late rollback fixtures passed 4,725,072 field-word
comparisons across repeated ring wraps and continuation after restoration.
The four-rate, six-partition smoke passes 98,328 native frames. Strict report
admission and high-precision selected-root checks pass; the full experiment is
now running, not yet accepted.

The native drawbar/key-front refinement passed 79 fixed-state comparison pairs
with zero escaped pixels, eight actual application smokes and paired timing
limits. Its retained baseline isolates that paint slice. The newly integrated
header belongs to the concurrent accepted source; combined-source native checks
and a fresh actual gallery remain next. Literal 1:1 reference fidelity is not
claimed. Original v1/v2/v3 galleries and prior evidence remain immutable.

The first integrated run was **160/161**, with a reproducible initial Play dwell
failure in the workspace replay. A test-only 600ms visual dwell repair preserves
all 132 assertion ASTs and the existing nine-second process deadline. A targeted
rerun passed **2/2**, including all thirty workspace processes. Keep these results
separate; they are not a new full-suite pass. Original failure, exact patch,
recheck logs and compact raw archive are retained.

## Completed full run and current work

The build-before-run full qualification **passed** in 649.663 seconds at the
frozen `0881d1f` plus source overlay. All 82 source hashes, native executable and
build metadata remained stable; all sixteen runner groups pass. The exact
[retained receipt](reports/full-waveform/qualification.json), original native
stdout/stderr, build log and retention hashes remain separate artifacts.

The run covers ten seconds at 44.1, 48, 96 and 192 kHz; 24 total partitions;
3,801,000 independent reference frames; 22,806,000 native frames; 91,224,000
native path solutions; 840 events; and 38,010,000 exact alternate-partition
scalar comparisons. Maximum normalized error is 1.935740205876292e-9 against
2e-5. All 176 selected 80/100-digit reference checks pass; maximum independent
root difference is 4.837748053930666e-15 seconds against 1e-14. These are R4
numerical observations, not R5 audible or R6 audio-device deadline evidence.

The full-run source freeze has ended. A25/A26 completed the offline CLI and profile compiler; the root wired and
built the CMake tool and passed a fresh 4,800-input-frame integration. Its
compiler/private-install CTests passed 2/2. A27 owns the remaining all-rate lifecycle and scene-symmetry
suite. A24 already passed isolated core-only testing ON/OFF configuration,
probe build, 2/2 smoke/admission and eighteen generated-graph checks. Next admit
A28's independent full-receipt review, publish completed source and complete independent offline-tool acceptance.
The combined native material/header and late-transaction gates now pass 3/3
in 12.42 seconds; capture the actual combined-source gallery next.

## Setup, storage and publication

Repository: `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.
Build: `/workspace/scratch/e3cacb90cc81/build`.
CMake: `/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/cmake`.
CTest is beside it; Ninja is
`/workspace/scratch/1bb6ee17ad7e/build-tools/bin/ninja`; locked SDL2 is
`/workspace/scratch/1bb6ee17ad7e/SDL2`. Release, BUILD_TESTING=ON,
HAMMOND_BUILD_STANDALONE=ON, HAMMOND_ENABLE_MIDI=OFF, SDL_ALSA=OFF.
System CMake was unavailable; use these observed tools. Free space remains
approximately 58 GiB. Reuse these trees and keep compact evidence; never remove
another session's source/build. Other checkout ownership is documented in the
reference-refinement concurrent handoff.

Shell Git push has no credentials. The connected GitHub account has verified
push permission: upload exact Git blobs/tree, require equality to `git write-tree`,
create commit, update main with a fresh expected SHA and force=false, fetch and
verify exact remote commit/tree. Inspect concurrent advances before each update.
Never reset a worktree or overwrite concurrent evidence to make publication easy.

Next: admit the full run, finish offline tool/compiler and independent allocation,
lifecycle/event gates, rebuild combined native UI and publish its actual gallery,
continue all remaining real workers through A60, run coherent final checks and
hosted CI, refresh setup/status/next actions and publish verified commits.
