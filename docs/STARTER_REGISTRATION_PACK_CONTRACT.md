# Proposed starter registration pack

Contract: `starter-registration-pack-v1`, 16 November 2026. These are twelve
**original proposed musical recipes for the nominal dry Engine**, requiring
independent review and native acceptance. Names describe intended use; they make
no factory, artist, measured-specimen, physical-expression, scanner or Leslie claim.
Basis: [library contract](REGISTRATION_LIBRARY_CONTRACT.md),
[state format](CONTROL_STATE_FORMAT.md), [render contract](REGISTRATION_RENDER_CONTRACT.md)
and current-session A01–A03/A05 scope findings linked there.

## Exact recipe proposal

Use the table's exact portable filename stems. Each nine-digit vector follows
physical drawbar order and retains leading zeroes. UA/UB/LA/LB mean Upper A/B and
Lower A/B. `P` gives the two pedal positions; `E` is saved expression.

Unless explicitly overridden below, **every** row selects B/B, enables both
manual routes, retains fixed modes none/none and stores percussion
Off/Second/Normal/Slow. Overrides change only the named fields. This shorthand
is confined to this contract: the independent JSON manifest must expand every
field literally, without defaults or inheritance.

| Stem / intended use | UA | UB | LA | LB | P | E | Overrides |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 Quiet Foundation / sparse chords | 008000000 | 008400000 | 008000000 | 004000000 | 20 | 0.5 | none |
| 02 Warm Comp / chord support | 808000000 | 808400000 | 008400000 | 008300000 | 30 | 0.625 | none |
| 03 Clear Lead / melody over soft chords | 008400000 | 808600000 | 006000000 | 006400000 | 20 | 0.625 | none |
| 04 Reed Edge / focused upper melody | 008620400 | 008640400 | 008200000 | 008300000 | 20 | 0.5 | none |
| 05 Bright Ensemble / full chord accents | 808600004 | 808600008 | 008400000 | 008440000 | 40 | 0.5 | none |
| 06 High Shimmer / upper partial color | 008000248 | 008000468 | 008000000 | 008200000 | 10 | 0.5 | none |
| 07 Percussive Pair / short upper accents | 888000000 | 888000000 | 008400000 | 008400000 | 40 | 0.5 | percussion On/Third/Normal/Fast |
| 08 Slow Accent / sustained upper attacks | 808000000 | 808000000 | 008000000 | 008200000 | 30 | 0.625 | percussion On/Second/Soft/Slow |
| 09 Split Dialogue / contrasting manuals | 008400000 | 008600004 | 808000000 | 808400000 | 40 | 0.5 | selected A/B |
| 10 Pedal Study / pedals with muted manuals | 008000000 | 008400000 | 008000000 | 008200000 | 62 | 0.5 | selected A/B; routes Off/Off |
| 11 Fixed Contrast / compare existing fixed modes | 008000000 | 808400000 | 008400000 | 008440000 | 30 | 0.5 | selected B/A; fixed D#/F |
| 12 Manual Return / lower support before upper return | 808000000 | 808600000 | 008400000 | 008440000 | 40 | 0.5 | selected A/B; routes Off/On; fixed G#/none; percussion On/Third/Soft/Fast |

Rows 11–12 select existing documentary modes within an original combined snapshot;
they create no new fixed rows or documentary recipe attribution. Upper percussion
requires its existing eligible route; retained settings in row 12 do not sound
while cancelled. Audition instructions must make necessary manual/pedal notes and
later selections explicit. Individual preferences and headroom need listening;
the table is not a physical-fidelity or clipping guarantee.

## Assets, provenance and production

Proposed source layout: `data/registrations/starter-v1/entries/` contains exactly
24 payloads. For every stem, provide `.b3registration` and `.b3performance` files
with **identical canonical `B3CONTROLS4` bytes**, including expression and final LF.
Use no envelope, comments, trailing metadata, per-entry sidecar or index. Suffixes
carry existing library scope only: Registration recall preserves current desired
expression; Performance restores saved expression. Generic Load and renderer
`--controls` both restore the entire payload regardless of suffix.

Place `README.md` and `recipes.json` beside `entries/`, outside the flat store.
The JSON has integer `schema_version: 1`, `pack_id: "starter-registration-pack-v1"`,
`evidence_status: "proposed-unmeasured"`, authorship/provenance text and twelve
recipes in table order. Each recipe literally supplies `name`, `purpose`,
`registration_file`, `performance_file`, `drawbars` (2x2 nine-digit strings in
Upper/Lower, A/B order), `selected_banks`, `route_enabled`, `fixed_registrations`,
`pedal_drawbars`, `expression` and `percussion` with `enabled`, `harmonic`, `volume`,
`decay`. Use Booleans for routes/enabled, integers for pedal positions and
numeric expression. Freeze array order as Upper, Lower and A, B; `drawbars`
contains two two-element arrays of nine-digit strings. `selected_banks` and
`fixed_registrations` each contain two strings, `route_enabled` two Booleans,
and `pedal_drawbars` two integers in Mixture 1/2 order. Bank strings are `A`/`B`;
fixed strings use state grammar `none`, `C#`, `D`, `D#`, `E`, `F`, `F#`, `G`,
`G#`, `A`. Percussion strings are `second`/`third`, `normal`/`soft` and
`slow`/`fast`. No C++ enum spellings or numeric enum ordinals enter this manifest.
`name` is the exact numbered filename stem; both file fields are exact basenames
resolved beneath `entries/`. Preserve the frozen
`atlas-chapel-nominal-v1` catalog and its exact state4 digest; no catalogue rewrite,
new parameter, state version or model/profile data is allowed.

Prefer a small C++ developer generator, `tools/generate_starter_registrations.cpp`,
using explicit `ControlSnapshot` recipes, `serialize_controls` and existing
`save_registration_entry_new` create-only storage. No hand-maintained control-file
grammar and no runtime JSON dependency. The independently authored literal JSON
is an acceptance oracle, **not generated from or consumed by the generator's
recipe table**. A test must compare those independent representations.

Run the generator only into an explicitly supplied empty staging directory or a
missing child of an existing parent. Validate every recipe/name before writing;
protect source/provenance paths and use the storage API's final synchronous
authorization against this immutable offline batch intent. Report each committed
file and failure truthfully. A multi-file run is not an atomic batch: stop on
failure, preserve committed files, retain `SavedWithWarning`, and never retry or
overwrite automatically. Commit the reviewed resulting 24 small payloads.
Separate evidence may hash actual manifest/generator/payload bytes; hashes do not
turn proposed recipes into measurements.

## Portable delivery and acceptance

Root owns CMake. Provide an explicit optional copy-only `StarterRegistrations`
install component under `share/hammond/registrations/starter-v1/`, using a fixed
24-payload plus README/manifest file list. Installation executes no generator,
parser, renderer or Python and writes no user-library/preference directory.
Support relocatable prefixes, `DESTDIR`, spaces and non-ASCII paths. Explain how
users copy selected files into their chosen library using existing no-replace
export; install must not imply startup recall or browser completion.

Acceptance must check all literal fields through the native parser/inspector,
exact pair equality, canonical serialization, names/count/order and unchanged
catalog identity. Use a nondefault supplied expression to verify Registration
materialization preserves it while Performance restores each recipe's saved
value; render both results under the renderer contract. Reveal hidden banks and
cancelled fixed memory through subsequent controls, and exercise every recipe
with suitable notes, including pedal-only row 10. Keep this separate from actual
live-app/browser acceptance.

Rebuild the generator from the recorded source, regenerate into a fresh temporary
directory and require exact filename/byte equality with all 24 checked-in files;
then independently compare against the literal manifest. Test collisions and
partial-result reporting without modifying source assets. Install into an empty
relocated prefix, compare exact delivered file bytes and consume installed entries
with the public tool and renderer. Retain commands, build identities and failures;
generator self-consistency, installation success and pleasant audio alone do not
close state, platform, physical or whole-interface gates.
