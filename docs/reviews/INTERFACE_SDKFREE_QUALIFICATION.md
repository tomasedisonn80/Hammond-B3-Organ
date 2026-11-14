# Interface SDK-free qualification and Windows fixture repair

**A40, wave 7, 2026-11-14 — local qualification passed; hosted Windows closure pending.**
The rebuilt SDK-free Release configuration passed **130/130 tests**, with no
disabled or skipped cases. The three repaired fixtures also passed the focused
native gate. [The result record](../development/2026-11-14-interface-continuation/reports/a40-result.json)
retains commands, source identities, configuration, binary identities and the
original Windows failures.

## Observed failure and bounded repair

Published `aea58bb85bc66a5feaff66a0b8a388e7c3f9e630` failed during both Windows
build jobs: core job `132445644167` and native job `132445644432`. Their retained
diagnostics report C4244 at the two resize expressions in
`test_standalone_workspace_acceptance.cpp` and C4996 at the optional capture
environment reads in `test_standalone_scaled_view.cpp` and
`test_standalone_workspace_raster.cpp`. `/WX` correctly made those warnings fatal.
The [original failure record](../development/2026-11-14-interface-continuation/reports/root-ui-ci-windows-failures.json)
keeps exact diagnostics, job URLs and full decoded-log identities.

The acceptance fixture now explicitly converts each integer resize choice to
`float`. Its four possible values, 819, 820, 1399 and 1400, are exactly
representable; branch conditions and expected behavior are unchanged. The two
SDL fixtures now use the already available `SDL_getenv`, matching other native
fixtures. Optional arguments still take precedence over environment variables;
missing variables retain the existing empty-path behavior.

Only those three test sources changed in A40. There are no production, CMake,
timeout, warning-policy or assertion changes. The
[preservation check](../development/2026-11-14-interface-continuation/reports/a40-repair-preservation.json)
reverses precisely the intended replacements and recovers the original files.
All 186 `CHECK` calls in workspace acceptance and every native `check`/`require`
remain intact. The exact repair is retained as
[a40-repair-diff.patch](../development/2026-11-14-interface-continuation/reports/a40-repair-diff.patch).

## Qualified inputs and execution

The source basis is `aea58bb85bc66a5feaff66a0b8a388e7c3f9e630` plus the existing
A34/A36 presentation/status overlay, frozen A39 workflow and A40 fixture repair.
The [source manifest](../development/2026-11-14-interface-continuation/reports/a40-source-freeze.json)
pins 335 code/data/workflow inputs with digest
`0a988b9ad1519255ff98da3133e1b9ff670e6aacde138566aedc94359f901c2d`.
The complete relevant overlay patch is retained separately. These local results
identify that working source; they do not retroactively qualify the unmodified
published Windows revision.

The Linux toolchain was GCC 14.2.0, CMake/CTest 4.4.4 and Python 3.12.14. Native
fixtures used existing SDL 2.32.10 and the shared pinned MIDI-enabled build.
Dependency commits, selected cache values and executable hashes are retained in
[native inputs](../development/2026-11-14-interface-continuation/reports/a40-native-inputs.json).
Compilation retained `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion
-Wshadow -Werror` throughout.

| Executed gate | Observed result |
|---|---|
| Rebuild the three affected native targets | Pass, 13.21 seconds. |
| Exact native CTest filter: workspace acceptance, workspace raster, scaled view | **3/3 pass**, 29.75 seconds, `--no-tests=error`. |
| Reconfigure and rebuild reusable SDK-free Release | Pass; build 61.73 seconds. |
| Freshly discovered full SDK-free CTest inventory | **130/130 pass**, 85.00 seconds, `--parallel 3 --no-tests=error`. |

Native acceptance retained 42 layout cases, 5,740 hidden-control rejections,
56 focus returns and 14 real-Session ownership runs. Raster acceptance exercised
150 frames; scaled rendering exercised 168 frames/states, 90 clipped frames,
16 scaled focus cases and 56 service values, with zero failures. These are
software-surface fixture observations.

SDK-free configuration explicitly disabled standalone, VST3, physical MIDI and
sanitizers, with all three SDK roots empty. Its 101 generated compile commands
contain no SDL, RtMidi or VST3 SDK paths. The
[discovery](../development/2026-11-14-interface-continuation/reports/a40-sdkfree-discovery.json),
[inputs](../development/2026-11-14-interface-continuation/reports/a40-sdkfree-inputs.json)
and [CTest log](../development/2026-11-14-interface-continuation/reports/a40-sdkfree-ctest.txt)
retain actual inventory, cache, link recipes and results rather than a historical
count. Command arrays include exact tool paths and working directories.

## Preservation and next action

The final [recheck](../development/2026-11-14-interface-continuation/reports/a40-post-gate-recheck.json)
found zero changes among the 335 frozen inputs, 75 SDK-free binaries/profile
outputs and A12's 114 protected files. Core models, parameters, saved-state
formats, source assets and VST3 identities therefore retain their original bytes.
A39's workflow remains SHA-256
`527d1cdb692cd5d837f0436ee68b2026878b10c5db1553459ca623060e4c1d34`.
Both reusable build leases are released.

No local MSVC or clang-cl is installed. Root can publish the frozen repair;
A48 must observe both Windows jobs at that exact published revision before
closing their build failures. Physical devices, actual displays, host deadlines,
accessibility, specimen fidelity and the complete M0–M9 plan retain their
separate gates.
