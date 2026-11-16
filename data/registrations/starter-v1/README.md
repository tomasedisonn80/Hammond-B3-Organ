# Starter registrations v1

Twelve original, project-authored software recipes for the **nominal dry Engine**,
pack ID `starter-registration-pack-v1`, evidence status **`proposed-unmeasured`**.
Names describe intended musical use. They carry no factory-preset, artist-tone,
measured-instrument, physical-expression or connected scanner/rotary attribution.
Listening preference and headroom remain dependent on the notes and settings used.

## Exact contents

This directory contains `README.md`, the independently authored
[recipes.json](recipes.json), and [entries/](entries/): **26 files total**.
The flat `entries/` directory contains exactly these 24 payloads, with no metadata,
sidecars or nested directories. Each row supplies both linked suffixes.

| Exact numbered stem | Intended use | Saved expression | Registration file | Performance file |
| --- | --- | --- | --- | --- |
| 01 Quiet Foundation | Sparse chords | 0.5 | [.b3registration](entries/01%20Quiet%20Foundation.b3registration) | [.b3performance](entries/01%20Quiet%20Foundation.b3performance) |
| 02 Warm Comp | Chord support | 0.625 | [.b3registration](entries/02%20Warm%20Comp.b3registration) | [.b3performance](entries/02%20Warm%20Comp.b3performance) |
| 03 Clear Lead | Melody over soft chords | 0.625 | [.b3registration](entries/03%20Clear%20Lead.b3registration) | [.b3performance](entries/03%20Clear%20Lead.b3performance) |
| 04 Reed Edge | Focused upper melody | 0.5 | [.b3registration](entries/04%20Reed%20Edge.b3registration) | [.b3performance](entries/04%20Reed%20Edge.b3performance) |
| 05 Bright Ensemble | Full chord accents | 0.5 | [.b3registration](entries/05%20Bright%20Ensemble.b3registration) | [.b3performance](entries/05%20Bright%20Ensemble.b3performance) |
| 06 High Shimmer | Upper partial color | 0.5 | [.b3registration](entries/06%20High%20Shimmer.b3registration) | [.b3performance](entries/06%20High%20Shimmer.b3performance) |
| 07 Percussive Pair | Short upper accents | 0.5 | [.b3registration](entries/07%20Percussive%20Pair.b3registration) | [.b3performance](entries/07%20Percussive%20Pair.b3performance) |
| 08 Slow Accent | Sustained upper attacks | 0.625 | [.b3registration](entries/08%20Slow%20Accent.b3registration) | [.b3performance](entries/08%20Slow%20Accent.b3performance) |
| 09 Split Dialogue | Contrasting manuals | 0.5 | [.b3registration](entries/09%20Split%20Dialogue.b3registration) | [.b3performance](entries/09%20Split%20Dialogue.b3performance) |
| 10 Pedal Study | Pedals with muted manuals | 0.5 | [.b3registration](entries/10%20Pedal%20Study.b3registration) | [.b3performance](entries/10%20Pedal%20Study.b3performance) |
| 11 Fixed Contrast | Compare existing fixed modes | 0.5 | [.b3registration](entries/11%20Fixed%20Contrast.b3registration) | [.b3performance](entries/11%20Fixed%20Contrast.b3performance) |
| 12 Manual Return | Lower support before upper return | 0.5 | [.b3registration](entries/12%20Manual%20Return.b3registration) | [.b3performance](entries/12%20Manual%20Return.b3performance) |

Every file is a complete canonical `B3CONTROLS4` snapshot, including the final
newline. The two files in each row have **identical bytes**. They retain all 36
drawbar positions, selected banks, route bits, fixed-mode memory, two pedal
positions, four percussion settings and expression. Held notes, source phase,
contacts, percussion history and clocks are outside the snapshot.

The manifest expands every field literally. Array order is Upper/Lower, then
A/B for the four nine-digit drawbar strings; pedal order is Mixture 1/2.
Leading zeroes matter. The frozen catalog is `atlas-chapel-nominal-v1`.
Recipes 11–12 select existing documentary fixed modes within original combined
snapshots; they add no fixed rows or documentary attribution for these recipes.

## Choose the scope

| Operation | Expression behavior |
| --- | --- |
| Registration materialization | Preserve expression from mandatory `--current FILE`; restore every other field from the entry. |
| Performance materialization | Restore the entry's saved expression; `--current` is forbidden. |
| Generic Load/`--state` or renderer `--controls FILE` | Restore the complete file, including expression, regardless of suffix. |

## Import or copy selected entries explicitly

Set the paths below to this pack and your built or installed tool. Use a fresh
working directory whose parent already exists. The tool's import operation
validates and copies selected controls through create-only export:

```sh
pack="/path/to/starter-v1"
tool="/path/to/hammond_registration"
work="$PWD/starter-demo"
mkdir "$work"
"$tool" list --library "$pack/entries"
"$tool" import --input "$pack/entries/02 Warm Comp.b3registration" \
  --library "$work/library" --name 'Warm Comp' --scope registration
"$tool" materialize --library "$work/library" \
  --key 'Warm Comp.b3registration' \
  --current "$pack/entries/01 Quiet Foundation.b3performance" \
  --destination "$work/prepared" --name 'Warm Current'
"$tool" materialize --library "$pack/entries" \
  --key '02 Warm Comp.b3performance' \
  --destination "$work/prepared" --name 'Warm Saved'
```

`Warm Current.b3performance` preserves the supplied `0.5`; `Warm Saved.b3performance`
restores `0.625`. Normally supply your own saved current controls. Both outputs
are complete files suitable for `hammond_render --controls`. Explicit import
scope determines the destination suffix, regardless of the input suffix.

Choose another name after a collision; there is no overwrite mode. Inspect any
reported committed warning before retrying. For a direct file-manager copy,
copy only selected payloads into your chosen flat library and refuse replacement
of existing names. Keep this README and manifest outside that library. Nothing
imports or recalls these entries automatically.

For auditions, play both manuals and pedals as appropriate. Recipe 10 requires
pedal notes because both manual routes are cancelled. Recipe 12 starts with
Upper cancelled: select an Upper bank/fixed preset to reconnect it, and Upper B
for its retained percussion. Recipes 7–8 use Upper B percussion. The
[operator guide](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/REGISTRATION_GUIDE.md)
provides exact note-event and render examples.

## Optional installation

From an already configured build, select the copy-only component explicitly:

```sh
cmake --install /path/to/build --config Release --prefix /chosen/prefix \
  --component StarterRegistrations
```

Default pack location: `/chosen/prefix/share/hammond/registrations/starter-v1/`.
Relative install-directory overrides may change it. `RegistrationTools` separately
installs the CLI and `share/hammond/REGISTRATION_GUIDE.md`; the renderer/profile
are separate build products. Existing package destinations are refused. Installation
copies the fixed 26-file inventory without generation, parsing or rendering and
does not write a user library or preferences. Relocated prefixes and POSIX
`DESTDIR` staging are supported; quote paths containing spaces or Unicode.

## Reproduction and evidence

The native developer generator uses explicit `ControlSnapshot` recipes, the
existing serializer and create-only storage. It neither reads nor generates the
independent JSON oracle. After building `hammond_generate_starter_registrations`,
run it into a fresh staging directory outside this pack:

```sh
/path/to/build/hammond_generate_starter_registrations --output /existing/parent/fresh-entries
```

The destination must be empty or a missing child of an existing parent. The
generator reports each save and stops on failure/warning, retaining committed
files; the batch is not atomic. Compare all 24 filenames and raw bytes, then run
the independent native-parser/manifest checks.

[Frozen recipe contract](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STARTER_REGISTRATION_PACK_CONTRACT.md),
[generator source](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/tools/generate_starter_registrations.cpp),
[independent admission](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/reviews/STARTER_REGISTRATION_ADMISSION.md)
and [byte identities](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/development/2026-11-16-preset-library-continuation/reports/starter-provenance.json)
record the source and qualification boundaries. Native data admission covers all
literal fields, exact regeneration and expression preservation/restoration.
It supplies no live-browser, device, cross-platform, physical or whole-interface
acceptance.
