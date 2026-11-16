# Portable registrations: operator and developer guide

`hammond_registration` inspects, imports and materializes saved musical controls
without a display, audio device, profile or running instrument. Every directory
is explicit. It neither imports installed files automatically nor recalls them at
startup. Live library/browser integration has separate acceptance.

The starter pack contains twelve original **proposed, unmeasured** recipes for
the nominal dry Engine, each supplied in two scopes. They are not physical
factory or artist presets. Installation and rendering establish no connected
scanner/rotary audio, physical fidelity or whole-interface 1:1 result.

## 1. Build without SDL

From the repository root, use CMake 3.21+, Python 3.10+ and a C++20 compiler:

```sh
cmake -S . -B build-headless -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=OFF -DHAMMOND_BUILD_STANDALONE=OFF \
  -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_ENABLE_MIDI=OFF
cmake --build build-headless --config Release \
  --target hammond_registration hammond_render
build="$PWD/build-headless"
tool="$build/hammond_registration"
"$tool" --help
```

The renderer build also produces `nominal.b3p`. Multi-configuration generators
usually place executables in `Release/`; adjust `tool` and the renderer path,
and add `.exe` on Windows. The examples below use a POSIX shell. Registration
preparation itself does not need the renderer or its profile.

## 2. Inspect and import selected recipes

Use a fresh demonstration directory; choose a different name for another run:

```sh
pack="$PWD/data/registrations/starter-v1/entries"
work="$PWD/registration-demo"
mkdir "$work"
"$tool" list --library "$pack"
"$tool" inspect --library "$pack" --key '02 Warm Comp.b3registration'
"$tool" import --input "$pack/02 Warm Comp.b3registration" \
  --library "$work/library" --name 'Warm Comp' --scope registration
"$tool" import --input "$pack/02 Warm Comp.b3performance" \
  --library "$work/library" --name 'Warm Performance' --scope performance
"$tool" list --library "$work/library"
```

The pack scan has 24 entries. Import creates `Warm Comp.b3registration` and
`Warm Performance.b3performance`; **the explicit import scope chooses the
suffix, regardless of the input filename**. Both store the complete payload,
including expression. Missing destination directories may be created only when
their parent already exists. Read-only `list`/`inspect` create nothing.

Names are 1–48 ASCII bytes, start and end with a letter or digit, and allow only
letters, digits, spaces, hyphens and underscores inside. Omit the suffix from
`--name`. DOS device names such as `CON`, `NUL`, `COM1` and `LPT1` are reserved.
Use the exact filename, including its case-sensitive suffix, for `--key`; paths
and separators are invalid keys. Case-colliding entries are ambiguous and cannot
be selected even with an exact spelling.

Libraries are flat, bounded catalogs: at most 128 candidates and 512 directory
items. Keep README/metadata outside `entries/`. Disabled entries and unrelated
warnings remain visible; an incomplete scan cannot authorize selection or saves.

## 3. Choose expression behavior explicitly

| Operation | Expression used |
| --- | --- |
| Materialize `.b3registration` | From mandatory `--current FILE` |
| Materialize `.b3performance` | From the entry; `--current` is forbidden |
| Renderer `--controls FILE` or generic standalone Load/`--state` | From the complete file, regardless of suffix |

Registration materialization takes **only expression** from the supplied current
snapshot; every other field comes from the entry. The entire current file must
still validate. Performance materialization uses the complete entry. Both
operations create a new `.b3performance` file.

For a reproducible example, Quiet Foundation supplies current expression `0.5`,
while Warm Comp stores `0.625`. In normal use, supply your own saved current
controls instead of this demonstration copy:

```sh
cp "$pack/01 Quiet Foundation.b3performance" "$work/current.b3controls"
"$tool" materialize --library "$work/library" \
  --key 'Warm Comp.b3registration' --current "$work/current.b3controls" \
  --destination "$work/auditions" --name 'Warm Current'
"$tool" materialize --library "$work/library" \
  --key 'Warm Performance.b3performance' \
  --destination "$work/auditions" --name 'Warm Saved'
"$tool" inspect --library "$work/auditions" --key 'Warm Current.b3performance'
"$tool" inspect --library "$work/auditions" --key 'Warm Saved.b3performance'
```

The inspected canonical expressions are `0.5` and `0.625`. Directly rendering
`02 Warm Comp.b3registration` would restore `0.625`: its suffix does not ask the
renderer to preserve another expression. Materialize with `--current` first
when that preservation is wanted.

## 4. Render and apply a score

This half-second score overrides expression at frame zero, then plays both
manuals and one pedal. `lower` is the required unused-manual convention for
pedal events; pedal index `1` is a one-based pedal ID, not a MIDI note.

```sh
cat > "$work/phrase.events" <<'EOF'
0 expression upper 0 0.375
0 note_on upper 60 100
0 note_on lower 48 100
0 pedal_on lower 1 100
18000 note_off upper 60 0
18000 note_off lower 48 0
18000 pedal_off lower 1 0
EOF
"$build/hammond_render" --profile "$build/nominal.b3p" \
  --controls "$work/auditions/Warm Current.b3performance" \
  --events "$work/phrase.events" --output "$work/warm.wav" \
  --sample-rate 48000 --frames 24000 --block-size 64 --seed 0 --fail-on-clip
```

Restoration happens before every score event, including frame-zero events;
equal-frame events keep file order. Without `--events`, the default upper note
gesture remains available. Explicit `--note` conflicts with `--events`.
`--controls` conflicts with explicit `--drawbars`, `--pedal-drawbars`,
`--percussion`, `--percussion-volume` and `--percussion-decay`, even if their
values match defaults. Contact choice, profile, seed and rendering options
remain independent.

All 36 drawbar positions, remembered banks, route bits, retained fixed modes,
pedal positions, percussion settings and expression restore, including hidden
or currently inaudible values. Held notes, phase, contact/percussion histories
and clocks are not saved. Recipe 10 needs pedal events because both manuals are
cancelled; recipe 12 needs a later upper selection to reconnect that route.

With controls, stdout provenance uses `render_schema_version: 6` and
`controls.restore_policy: "full-state-including-expression"`. Its
`canonical_b3controls4` identifies the initial restored snapshot, before score
overrides. This example therefore reports initial expression `0.5` while playing
at `0.375`. WAV publication requires an existing parent and a new filename.
Renderer exits are 0 for success, 1 for an error and 2 for `--fail-on-clip`
refusal; these differ from registration-tool exits below.

## 5. Old files and canonical output

Inputs accept `B3CONTROLS1` through `B3CONTROLS4`. Import/materialize always write
canonical version 4 with the frozen catalog identity and final newline.

| Input | Migration defaults |
| --- | --- |
| Version 1 | Percussion Off/Second/Normal/Slow; pedals `[0,0]`; fixed modes none/none |
| Version 2 | Pedals `[0,0]`; fixed modes none/none |
| Version 3 | Fixed modes none/none |
| Version 4 | Requires all fields and the exact catalog identity |

Other supplied fields retain their meaning. Sources are never rewritten.
Changing a header alone cannot migrate a document. Inputs must be regular files
of at most 16,384 bytes, including whitespace; leaf symlinks/reparse points,
malformed/trailing data, future versions and catalog mismatches are refused.

## 6. Read results and handle publication

The registration CLI writes one JSON object plus newline, including for help
and errors. Check `schema`, `outcome`, `code`, `committed` and the applicable
`catalog`, `entry`, `input`, `save` fields. Catalog warnings can accompany a
successful operation. Paths are exact native-byte hex objects, not ordinary
path strings: `posix-bytes-hex` or `windows-utf16le-hex`.

| Exit | Meaning |
| --- | --- |
| 0 | Success without warnings; an empty/missing listed directory also succeeds |
| 1 | Success with catalog warnings or `SavedWithWarning` |
| 2 | Usage/name/scope/argument error |
| 3 | Admission refusal, including collision or changed-source authorization |
| 4 | Filesystem failure before publication |
| 5 | Report output failed; publication may already have happened |
| 70 | Internal error; publication may be unknown (`committed: null`) |

Import and materialize are create-only. Repeating a successful destination name
refuses with `NameExists`; choose another name. Inputs are revalidated before
publication. There is no overwrite mode, live-control acknowledgment or file
lock. A committed warning retains its output: inspect it before deciding what
to do, and never blindly retry. Publication is one-file no-replace, not batch
atomicity or power-loss durability. Failure may leave an empty new directory.
Never redirect stdout onto an input or intended output: shell redirection runs
before the tool can protect it.

Use separate option/value tokens; `--option=value`, duplicate options and values
beginning `--` are rejected. Prefix such paths with `./`.

## 7. Install explicitly and relocate

These copy-only components are `EXCLUDE_FROM_ALL`; ordinary installation does
not select them. Choose a prefix with no existing component targets:

```sh
prefix="$PWD/registration-install"
cmake --install "$build" --config Release --prefix "$prefix" \
  --component RegistrationTools
cmake --install "$build" --config Release --prefix "$prefix" \
  --component StarterRegistrations
"$prefix/bin/hammond_registration" list \
  --library "$prefix/share/hammond/registrations/starter-v1/entries"
```

Default locations are `bin/hammond_registration` (Windows: `.exe`) and
`share/hammond/REGISTRATION_GUIDE.md`, plus exactly 24 payloads under
`share/hammond/registrations/starter-v1/entries/`; pack `README.md` and
`recipes.json` sit beside that directory. Relative CMake install-directory
overrides change these locations. The renderer, profile and system runtime
libraries are not bundled by these two components.

The components may share a prefix and run in either order. Existing tool/guide
targets or an existing starter package cause refusal, including a repeated
install; nothing is replaced or merged. Preflight checks required sources and
destinations before copying. A later copy failure can leave a partial new
installation, with no automatic cleanup. Keep `CMAKE_INSTALL_MODE` unset or
`COPY`. Installation runs no generator, parser, renderer or Python interpreter
and touches no user library/preferences.

Move the complete prefix to a new location on a compatible system, then invoke
the executable and `--library` using their new paths. Spaces and Unicode paths
are supported; keep shell quotes. POSIX package staging supports, for example,
`DESTDIR="$PWD/stage" cmake --install "$build" --prefix /opt/hammond --component StarterRegistrations`.
Import selected installed entries using section 2, with `pack` set to their
installed `entries/` directory.

**Verification boundary:** the list/import/materialize/render examples were
exercised on the session's Linux native executables, with scope values and
score precedence checked. Root also executed both actual installation components,
renamed the prefix and used the relocated native tool; the ten-method installer
suite covers custom directories, staging, relocation and partial-copy refusal.
The original installation receipt retains the guide text from before this
qualification update. A clean no-SDL build and Windows/macOS execution remain
separate pending gates; installation does not qualify live-browser or physical
behavior. Repository details are
in `docs/REGISTRATION_CLI_CONTRACT.md`, `docs/REGISTRATION_RENDER_CONTRACT.md`
and `docs/CONTROL_STATE_FORMAT.md`.
