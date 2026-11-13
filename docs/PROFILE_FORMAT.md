# Profile boundary, version 1

This contract is original implementation design. It reconstructs the atlas's
provenance and runtime separation; the absent original companion schema is not
being recovered.

## Authoring JSON

Use an explicit schema version, profile ID, named algorithm, evidence status,
source PDF SHA-256/pages, unresolved specimen fields, units and fixed model
parameters. The nominal authoring record contains all 91 source IDs/frequencies,
peak amplitudes and base phases, an explicit 61-by-9 manual tone-ID map, nine
physical-position gain levels (0-8), and one fixed output gain. Units are Hz,
normalized_peak, turns and dimensionless gain. Runtime values must be finite.
Only the named `ideal-shared-sine-v1` / `nominal-unmeasured-v1` baseline is supported
initially. No measured specimen is implied.

Generate manual routes from atlas pp. 98-99, then retain them explicitly in the
JSON; compare printed rows from p. 102 independently. Tone IDs are one-based.
Frequencies use the explicitly proposed 12-TET equation on pp. 61-66. Base phases
are proposed zero offsets; the engine adds deterministic seeded initial offsets.
The runtime seed is not a measurement and never changes on note events.

## Compiled text interchange

The Python compiler validates the complete authoring profile before writing a
bounded, deterministic UTF-8 text file. The C++ loader runs with audio stopped,
reads a maximum 128 KiB file, rejects unknown/duplicate/out-of-order records or
trailing tokens, and populates a value-owned fixed-size `RuntimeProfile`.

The exact token order is:

```text
B3PROFILE 1
profile_id nominal-unmeasured-v1
authoring_sha256 <64 lowercase hex characters>
output_gain <finite nonnegative number>
drawbar_gains <9 finite nonnegative numbers>
sources 91
<tone_id> <frequency_hz> <peak_amplitude> <base_phase_turns>
... 91 rows in tone_id order ...
manual_map 61 9
<9 one-based tone IDs>
... 61 rows in key order ...
end
```

Whitespace is insignificant; comments and extension records are not accepted.
Numbers are round-trip decimal strings using the classic locale. Phase values
are in [0,1), peak amplitude in [0,1], output gain in [0,1], drawbar gains in
[0,1] with exact mute at0 and full-scale at8. Source frequency must be positive
and below Nyquist at prepare time; supported rates are 44100, 48000 and 96000 Hz.
Reject manual IDs outside13-91 for this named baseline. The semantic compiler
also verifies the declared baseline equations/routes rather than accepting a
misleading nominal identity with arbitrary data.

The authoring digest identifies canonical JSON as defined by the compiler
(sorted keys, compact separators, UTF-8, no NaN). This is a project convention,
not a claim of RFC8785 canonicalization. The offline fixture manifest separately
hashes the actual compiled bytes and output WAV. A standalone C++ loader treats
the embedded authoring digest as provenance supplied by the compiler, not as
proof that its numeric payload matches an unseen JSON document.

## Runtime ownership

Preparation validates then copies the fixed-size profile. Changes to the caller's
copy cannot alter active audio state. Source storage, mapping and gains have no
borrowed authoring pointers. A profile can be replaced only while processing is
stopped; cross-thread exchange and exact DSP checkpointing are future work.
