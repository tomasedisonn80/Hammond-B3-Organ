# A35 — Actual component installation and relocation

Actual worker `/root/w06_a35_install_relocation`, wave 6. Read the standing
instructions, current scope/checkpoint, complete M0–M9 plan, component contracts,
actual install rules and source state. Root authorized exclusive install use of
`build-native`; no configure, build, CTest, production edit, commit or push ran.
Only this note and `reports/A35-*` are owned.

## Source and actual payload

The run uses published `2e161dc3a60fc3442051799574feed37bffbfc5c`, GCC Release,
pinned SDL2 and MIDI OFF. The installed native application SHA-256 is
`0ef37dd5a0501da08df302027b31791b7917705e00cb32017b035a145ceb3811`;
it is distinct from A31's MIDI-enabled gallery executable. The
[report](../reports/A35-install-relocation.json) retains each expected file,
exact command, source/output hash and original runtime diagnostics; the
[command log](../reports/A35-install-relocation.log) preserves stdout/stderr.

| Component | Files | Scope |
| --- | ---: | --- |
| OfflineTools | 23 | Five native tools, two plotters, compiled profile and fixtures |
| CaptureTools | 57 | Complete local Python/data/documentation package |
| Standalone | 15 | Native MIDI-off executable and fourteen metadata files |

All **95 files / 5,077,285 bytes** coexist without overlap. Every file matched
its expected source. All **84 repository payload inputs** match the named
published commit; all **94 unique source/build/dependency inputs** retained their
bytes through execution. The complete installed tree remained byte-identical
through relocation and all runs. No task source/build absolute path occurs in
its **85 text files**; no public C++ SDK is installed.

## Executed relocation checks

Working checkout was `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`.
For each component, the reproducible form from that checkout is:

```sh
../build-tools/cmake/data/bin/cmake --install ../build-native --config Release --component COMPONENT --prefix '/workspace/scratch/1bb6ee17ad7e/A35-install-relocation/staged orgue é'
```

The prefix was renamed to `moved orgue Ω`. All subsequent commands ran from
`unrelated working é`, with `PYTHONPATH`, `PYTHONHOME` and `LD_LIBRARY_PATH`
unset; Python used `-B -S`. The report retains expanded absolute arguments.
All **16 commands matched their declared exits**:

- Native model/parameter export succeeded; the actual registry contains **47**
  entries and explicitly does not claim native-host export verification.
- The installed renderer produced 72,000 frames of 48 kHz, stereo PCM16 with
  identical channels and no clipping. Console trace/plot completed; the pedal
  trace/plot entrypoint help commands succeeded.
- The three-job synthetic capture study retained one pass, one inconclusive and
  one deliberate failure (exit 1). Full report replay returned exact match
  (exit 0), preserving that failed engineering outcome.
- The relocated standalone passed a 600 ms actual SDL dummy audio/video smoke,
  producing the 960×700 embedded-resource image, observing held/released notes,
  zero callback/sample errors and cleared shutdown ownership. MIDI remained
  unavailable as declared; no controls file was implicitly saved.
- Temporarily removing only the private installed profile or `capture_common.py`
  caused the expected explicit failure and no output file. Both were restored
  byte-for-byte; source/build inputs were never renamed or removed.

## Findings and continuation

No install/runtime defect was found. Two existing current-guide errors were
reported to A37: `OFFLINE_INSTALL.md` said 45 instead of 47 twice, and
`CAPTURE_TOOLS_INSTALL.md` named `NativeStandalone` instead of `Standalone`.
A37 received the source-freeze release before correcting them; these subsequent
documentation changes are outside this run's exact payload identity.

Root's original 154/155 CTest and separate repaired capture-install recheck remain
distinct. This targeted execution does not repeat or replace that full suite.
Native builds/outputs stay in session-owned scratch; only compact evidence is
proposed for Git. Other-platform runtime libraries, actual display/DPI, physical
audio/MIDI, DAWs, signing, asset rights and release distribution remain separate.
