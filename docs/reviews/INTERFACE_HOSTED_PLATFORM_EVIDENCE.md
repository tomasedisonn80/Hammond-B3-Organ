# Hosted platform evidence — A48

## Exact revision and independent observation

The published UI polish and Windows fixture repair at
`8673713a484c40e26ac7810c7c4cbc22fa874426`, tree
`e11bd68d6051f663631579ef235325a8775f8133`, has **eleven completed, successful
hosted jobs**. A48 independently read the GitHub Git Data commit, workflow runs,
complete job pages and artifact metadata through the GitHub connector. All three
runs were push-triggered attempt 1 on `main`; every job's own `head_sha` matches
the commit. The API page totals are 4 + 4 + 3, with no missing first-page jobs.
The [retained audit](../development/2026-11-14-interface-continuation/reports/a48-hosted-platform.json)
contains canonical URLs, timestamps, job identities and the bounded log evidence.

| Published workflow | Run | Completed successful jobs |
|---|---|---:|
| CI | [43596362824](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43596362824) | 4: Linux, macOS and Windows Release; existing core ASan/UBSan/leaks |
| Native standalone | [43596362938](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43596362938) | 4: Linux MIDI ON/OFF, Windows ON, macOS ON |
| Native VST3 | [43596362881](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43596362881) | 3: Linux, Windows, macOS |

A47 owns the detailed VST3 boundary and its three logs. This audit counts those
completed jobs without duplicating that work. Non-Windows core and existing core
sanitizer conclusions here are job-level API evidence; their logs were not
downloaded by A48.

## Windows failures closed on the repaired source

The original `aea58` failures remain preserved in
[the failure report](../development/2026-11-14-interface-continuation/reports/root-ui-ci-windows-failures.json).
They identified C4244 integer-to-float conversion in workspace acceptance and
C4996 `getenv` deprecation in the two raster fixtures. A48 verified that all
three files at the published commit exactly match A40's qualified repair hashes.
The existing assertions, warning policy and normal Release timeouts remain the
basis of this closure; A40's [repair record](../development/2026-11-14-interface-continuation/reports/a40-result.json)
retains the explicit casts and `SDL_getenv` substitutions.

Windows core job
[132451604650](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43596362824/job/132451604650)
and standalone job
[132451604523](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43596362938/job/132451604523)
both identify MSVC **19.44.35230.0**. The affected compilation commands retain
`/W4 /WX`; both builds report **0 warnings, 0 errors**. Neither current log
contains a C4244 or C4996 compiler diagnostic. Core executes **130/130** tests,
including workspace acceptance. Standalone executes **38/38**, including
workspace acceptance, workspace raster and scaled view. Their observed times
are 0.06, 8.75 and 21.54 seconds in the standalone run. These new successful
runs close the reported build defects without relabelling the historical failures.

## Native acceptance and package evidence

| Configuration | Job | Tests passed | CTest real seconds | Compiler / MIDI backend |
|---|---:|---:|---:|---|
| Linux ON | 132451604316 | 38/38 | 207.43 | GCC 13.3.0 / ALSA |
| Windows ON | 132451604523 | 38/38 | 270.58 | MSVC 19.44.35230.0 / WinMM |
| macOS ON | 132451604553 | 38/38 | 243.77 | AppleClang 17.0.0.17000013 / CoreMIDI |
| Linux OFF | 132451604586 | 38/38 | 229.06 | GCC 13.3.0 / unavailable |

All four logs contain the same 38 distinct passing test names and successful
discovery of the **21 required names** from the published workflow. All **13
native-labelled tests** from the published CMake are present and pass, including
drawing, quad drawing, preset/workspace raster, scaled view, device removal,
application, MIDI CLI/replay, workflows, workspace replay, replay boundaries and
chapel. The report retains both exact name sets. Every execution uses
`--no-tests=error`; there are no omitted, failed or skipped tests within these
38-test selections.

The package steps verify **19 installed files** for each MIDI-ON configuration
and **15** for Linux OFF, with relocated help/dummy smoke and archived-byte
checks. The four package artifact IDs are `14114517880`, `14114787477`,
`14115061756` and `14115280266`, respectively. API sizes and SHA-256 digests match
the upload log entries. The report retains expiry metadata as observed. A48 did
not download or independently rehash the ZIP archives; these are retained hosted
assertions and primary artifact metadata.

## Raw evidence and next boundary

Five complete logs remain outside the repository under
`/workspace/scratch/601951e27dc3/a48-hosted-primary/`. Each retained SHA-256 hashes
the exact connector-decoded text re-encoded as UTF-8, preserving its BOM and
original CRLF/LF endings. Only bounded excerpts, names, counts and metadata enter
the report.

Checkpoint 5, `cdbb2beaa28bf136f9a8db6213819129514e2ae9`, adds the native SDL
sanitizer/leak job. Its [single initial observation](../development/2026-11-14-interface-continuation/reports/a48-checkpoint5-initial.json)
records standalone run `43597589820`, new job `132455309517`, **in progress with
no conclusion**. A58 owns final closure; these eleven earlier passes do not
qualify that later source. Dummy SDL and injected replay establish no physical
audio/MIDI-device, persistent desktop-pointer, DAW, native-accessibility,
deadline, literal reference-pixel equality, measured-fidelity or whole-M9
production-readiness result.
