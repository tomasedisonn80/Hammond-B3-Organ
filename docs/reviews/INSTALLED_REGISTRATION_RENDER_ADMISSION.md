# Installed registration-to-render admission — A44

16 November 2026; actual worker `/root/w08_a44`, wave 8.
**Admitted for the observed compatible Linux installation, relocation and
scope-aware rendering flow. No product defect found.** This review executes
the combined installed flow; it does not rerun the full suite or 32-clip study.

## Exact observation and prerequisites

The [receipt](../development/2026-11-16-preset-library-continuation/reports/a44-installed-flow.json)
records 16 commands, their exact arguments/cwd, exits, timings and stream hashes.
The [originals](../development/2026-11-16-preset-library-continuation/reports/a44-installed-flow-originals.tar.gz)
retain every command stream, both installer scripts, inputs, prepared controls
and both complete WAVs. The 162,084-byte archive SHA-256 is
`5548cc25f3851b73dc3009f3bd9ecb41fd54c40ec950b2ec9073c686d1e731a9`.

Observed HEAD was first publication
`20739f6280b95e567e84615d5c5aee443fc3b93d`, tree
`1e59776459a05a9d934d0b519a45cd4c61b13ae9`, with later tracked changes
recorded separately. The receipt hashes each consumed file rather than treating
HEAD as the identity of pending CI/Load/failure/apron-install overlays.

Existing root `../build-native` inputs were copied read-only: Ninja Release,
GNU C++ 14.2.0, Linux x86-64/glibc 2.41. CMake 3.31.6 and Python standard-library
orchestration were used; no configure, native build, SDK acquisition or CTest
ran. Repeating this observation needs those already built six executables,
`nominal.b3p`, source installer payloads and compatible system runtime libraries.
The installed registration tool itself requires neither a profile nor Python;
rendering explicitly supplies the installed profile. `ldd` found the system
C++/C/math/GCC runtimes and loader, with no missing library. Those libraries
are not bundled by the selected components.

| Copied native input | SHA-256 |
| --- | --- |
| `hammond_registration` | `872a343f20eb6710e6867fc4d1c0fe0b95118b883de21035ee70774f8762e13f` |
| `hammond_render` | `671375f6f9d393295bca148bcb546a1eb387dd865e994e755f16933389a16263` |
| `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

## Actual installation and relocation

Following the copied-root-script fixture in
[`test_registration_install.py`](../../tests/test_registration_install.py),
I copied the actual generated installer and changed only genuine source/build
root strings to private roots in `../a44-installed-flow`. Each explicit
`cmake -P` dispatch used `CMAKE_INSTALL_LOCAL_ONLY=1`; even its manifest writes
went into the private build. No component rule was replaced or simulated.

All three real components succeeded with **51 ordinary files: 23 OfflineTools,
2 RegistrationTools and 26 StarterRegistrations**. Exact paths, byte lengths and
SHA-256 values matched the original copied inputs. Directory inventory was also
exact, with no symlinks or special files.

I renamed the prefix to `installed/package é音`, then removed only this
fixture's copied `source/` and `build/`. Both private input directories and the
old prefix were absent before native execution. All actual commands ran from
the initially empty `work/use é音`, using absolute installed paths and an
environment containing only empty `PATH`, UTF-8 locale and UTC. Distinct ASCII
branches precede differing Unicode leaves, respecting conservative path admission.

**This demonstrates that the retained package does not need its private
installer inputs.** The genuine checkout, build, dependencies and system
runtime remained accessible; this is not a sandboxed proof that every original
path was inaccessible. All watched genuine inputs stayed unchanged.

## Scope, provenance and audio

Installed `list` returned the complete exact 24-entry catalog without creating
working files. Installed `inspect` matched both recipe-12 payloads exactly.
Current controls came from installed Quiet Foundation with expression changed
to `0.25`; its other fields deliberately differ from Manual Return.

Materializing Manual Return Registration retained **only current expression
0.25**. Performance restored **stored expression 0.5**. Both new outputs were
canonical `.b3performance` files; every remaining byte matched the selected
entry, including all four banks, selected banks, cancelled Upper route, retained
G# mode, Lower route, pedal positions and Third/Soft/Fast percussion.

The independently authored score holds both manuals and a pedal, reconnects
Upper G#, reveals both A then B banks, and releases at frame 40,000. It contains
no expression override. Each installed render used 48,000 frames at 48 kHz,
block 64, seed 44, ideal contacts and `--fail-on-clip`.

| Materialization | Expression | Float peak | Float RMS | PCM16 peak | Clipped frames |
| --- | ---: | ---: | ---: | ---: | ---: |
| Registration | 0.25 | 0.035344198346138 | 0.010922684753210 | 1,158 | 0 |
| Performance | 0.5 | 0.070688396692276 | 0.021845369506420 | 2,316 | 0 |

Both exits were zero with empty stderr. Schema 6 reported exact path, raw byte
count, source version 4, `full-state-including-expression` and the entire exact
initial canonical snapshot. Installed-profile/catalog hashes agreed. Both
192,044-byte WAVs contain 48,000 stereo PCM16 frames with identical channels,
nonzero samples and no saturated values. Reported metrics were finite; the
renderer also rejects nonfinite source samples before WAV publication. The
two PCM hashes differ as expected for their distinct expression values.

Afterward the package inventory was unchanged. The unrelated cwd contained
exactly two explicit inputs, two materialized controls and two WAVs in three
ordinary directories; no temporary residue appeared.

## Boundaries and replay

This is a bounded nominal, unmeasured dry-engine observation. It establishes no
physical fidelity, audible preference, live browser/native Load journey, callback
deadline, device behavior, whole-interface 1:1, macOS/Windows execution or signed
distribution. Exact-source hosted acceptance remains separate.

From the repository root, choose a fresh work directory/report name:

```sh
python3 -B docs/development/2026-11-16-preset-library-continuation/reports/a44-installed-flow.py \
  --repo . --work ../a44-installed-flow-repeat --report-stem a44-installed-flow-repeat
```

The replay refuses an existing work directory or evidence destination. It removes
only its two private input directories and retains its relocated package.
