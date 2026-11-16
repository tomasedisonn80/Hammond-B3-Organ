# Proposed starter registration auditions

This is a reader copy of the successful original audition report. The original
101 files, including all 32 WAVs, per-run stdout/stderr, scores and reports, are
available in [starter-auditions-originals.tar.gz](starter-auditions-originals.tar.gz).
Extract that archive into an empty directory and open its original `report.md`
to use the relative audio links. The [exact original report](starter-auditions-original.md.gz)
and [original manifest](starter-auditions.json) preserve the source-bound record.
The table below shows filenames rather than links to files outside this report
directory. No audio or original report bytes were regenerated.

Status: **succeeded**. 32 of 32 renders succeeded.

These are proposed, unmeasured recipes for the nominal dry Engine. They are not specimen measurements, factory recipes, or live-app evidence.

Each WAV is stereo PCM16, 48 kHz, exactly one second, with nominal contacts, seed 73, block size 64 and fail-on-clip. No normalization is applied.

Both suffixes use `--controls`: full state **including saved expression**. This does not perform Registration's expression-preserving library recall. Matching suffix pairs must produce identical complete WAV bytes.

## Listening order

`audition` is note-only: Upper C4/G4 at frames 0/9000, Lower C3 at 16000, pedal ID 1 at 26000, then Upper E4 + Lower G3 + pedal ID 8 at 36000. Manual notes use MIDI numbers; pedals use one-based IDs. Recipe 10's manual passages are silent; its pedals sound. Recipe 12's Upper remains cancelled.

`banks-reveal` (09–11) starts with the saved routes/fixed modes, selects both A banks at 12000, then both B banks at 24000. Selection reconnects routes and clears fixed modes. Recipe 11 initially sounds its saved D#/F modes.

`manual-return` (12) holds Upper C silently, reselects retained G# at 8000, selects both A banks at 18000, then both B banks at 30000. The later Upper-B attack makes saved percussion eligible. These explicitly named companion scores change selections; the initial-state provenance remains unchanged.

## Results

| Render | Result | WAV |
| --- | --- | --- |
| 01-audition-registration | succeeded | `01-audition-registration.wav` |
| 01-audition-performance | succeeded | `01-audition-performance.wav` |
| 02-audition-registration | succeeded | `02-audition-registration.wav` |
| 02-audition-performance | succeeded | `02-audition-performance.wav` |
| 03-audition-registration | succeeded | `03-audition-registration.wav` |
| 03-audition-performance | succeeded | `03-audition-performance.wav` |
| 04-audition-registration | succeeded | `04-audition-registration.wav` |
| 04-audition-performance | succeeded | `04-audition-performance.wav` |
| 05-audition-registration | succeeded | `05-audition-registration.wav` |
| 05-audition-performance | succeeded | `05-audition-performance.wav` |
| 06-audition-registration | succeeded | `06-audition-registration.wav` |
| 06-audition-performance | succeeded | `06-audition-performance.wav` |
| 07-audition-registration | succeeded | `07-audition-registration.wav` |
| 07-audition-performance | succeeded | `07-audition-performance.wav` |
| 08-audition-registration | succeeded | `08-audition-registration.wav` |
| 08-audition-performance | succeeded | `08-audition-performance.wav` |
| 09-audition-registration | succeeded | `09-audition-registration.wav` |
| 09-audition-performance | succeeded | `09-audition-performance.wav` |
| 09-banks-reveal-registration | succeeded | `09-banks-reveal-registration.wav` |
| 09-banks-reveal-performance | succeeded | `09-banks-reveal-performance.wav` |
| 10-audition-registration | succeeded | `10-audition-registration.wav` |
| 10-audition-performance | succeeded | `10-audition-performance.wav` |
| 10-banks-reveal-registration | succeeded | `10-banks-reveal-registration.wav` |
| 10-banks-reveal-performance | succeeded | `10-banks-reveal-performance.wav` |
| 11-audition-registration | succeeded | `11-audition-registration.wav` |
| 11-audition-performance | succeeded | `11-audition-performance.wav` |
| 11-banks-reveal-registration | succeeded | `11-banks-reveal-registration.wav` |
| 11-banks-reveal-performance | succeeded | `11-banks-reveal-performance.wav` |
| 12-audition-registration | succeeded | `12-audition-registration.wav` |
| 12-audition-performance | succeeded | `12-audition-performance.wav` |
| 12-manual-return-registration | succeeded | `12-manual-return-registration.wav` |
| 12-manual-return-performance | succeeded | `12-manual-return-performance.wav` |

`manifest.json` records exact argv, actual executable/profile/payload/score SHA-256, raw stdout JSON/stderr and WAV identities, input recheck, and each attempt's status. A failed JSON capture may contain incomplete/non-JSON bytes; `stdout_is_json` states what was observed. Hashes identify files, not physical fidelity.

The batch stops on its first failure and retains actual partial outputs. There is no overwrite, rollback, automatic retry, or resume; choose another fresh output directory for a new run.
