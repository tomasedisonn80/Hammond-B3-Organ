# Current checkpoint

Starting source: `2e161dc3a60fc3442051799574feed37bffbfc5c`, matched to remote main.
The isolated source is `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.
Other session changes in `/workspace/scratch/1bb6ee17ad7e` are preserved.

Wave1 is complete: A01–A06 are accepted for full atlas pages1–500, with no
gaps/overlaps and selected original-page visuals. The
[consolidated reading](../../research/WAVEFORM_ATLAS_REVIEW.md) retains actual
coverage and whole-plan implications. Wave2 A07–A09 are active: concrete R4 API,
independent oracle/acceptance and reference-led native refinement design. The
manifest records actual tasks; no planned worker is counted complete.

Build setup: system `cmake` was absent (exit 127). Reused the existing CMake
binary `/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/cmake`, Ninja
and locked SDL2 sources. The fresh Release standalone/MIDI-OFF build passed
in sibling `../build`; full CTest passed **155/155 in 152.15 seconds**. The
[baseline record](reports/baseline.json) identifies production inputs and
[raw test output](reports/baseline-ctest.txt). A real application frame at
1672×941 was captured with dummy SDL drivers and software rendering. Physical
devices are not implied. Initial free space: approximately 58 GiB; isolated
checkout 123 MiB and fresh build 74 MiB.

Shell Git push dry-run failed for missing credentials. The connected GitHub
account has verified push permission; use exact Git-data blobs/tree/commit and
`update_ref` with a freshly observed expected head and `force=false`, fetch,
then verify the staged tree and remote commit. Never reset other session files.

Next: finish the complete atlas reading, freeze the R4 ownership/API and
independent test boundary, establish baseline tests, then implement the
waveform renderer and a bounded native visual refinement. Preserve upstream
active refinement changes and integrate published advances before pushing.
