# Chapel registration audition files

[`chapel_controls.py`](../tools/chapel_controls.py) copies selected rows of the
[reviewed documentary catalog](CHAPEL_PRESETS_CATALOG.md) into a fresh, complete
[`B3CONTROLS3`](CONTROL_STATE_FORMAT.md) audition file. The resulting digits use
the current Engine's **nominal drawbar-position controls**. Documentary tap
connections do not establish measured transformer gains or factory preset timbre.
The atlas's primary factory Table IV and specimen wiring remain unverified.

Default bank A and percussion Off are explicit audition choices. This utility
implements no physical fixed-key latch, loading, simultaneous latches or
percussion interlock. It changes no Engine code, parameter identity or saved-state
format. Its output contains musical controls only, with no held notes or history.

## Generate and use

Use Python 3.10+ from the source checkout; its standard library and the adjacent
public authoring validator are the only dependencies. First generate the catalog
using its [compiler instructions](CHAPEL_PRESETS_CATALOG.md), or the repository's
`hammond_chapel_catalog` build target. With `build/chapel-catalog.json` available
and an existing `out` directory, choose a new filename:

```sh
python3 tools/chapel_controls.py --catalog build/chapel-catalog.json \
  --upper 'C#' --lower A --bank A --expression 0.75 \
  --output out/chapel-csharp-a.b3controls
build-native/apps/standalone/hammond_standalone \
  --state out/chapel-csharp-a.b3controls
```

The second command requires the [optional native app](STANDALONE_APP.md); adapt
the executable path to the selected build configuration/platform. The generated
control file needs no catalog or Python process when the app loads it. Loading
this complete state replaces all retained controls with its explicit values.

| Option | Contract |
| --- | --- |
| `--catalog PATH` | Required bounded compiled catalog, already admitted by the source compiler. |
| `--output PATH` | Required new file in an existing directory. Every existing leaf rejects. |
| `--upper KEY`, `--lower KEY` | Each defaults to `off`; keys are C#, D, D#, E, F, F#, G, G#, A or `off`. At least one part must be selected. |
| `--bank A\|B` | Default A; one common selected-bank label for both manuals. |
| `--expression TOKEN` | Default `0.75`; `0`, `1`, or `0.<digits ending nonzero>`, at most 64 characters. |
| `--help` | Help only; must be used alone. |

Expression examples `0.1` and `0.001` are valid. Integer leading zeros, trailing
fractional zeros, signs, exponents, whitespace and partial tokens reject.
Thus `00.1`, `0.10`, `1.0`, `+0.1` and `1e-1` reject. Fractional leading zeros
remain meaningful. Conversion is to the existing finite double control in [0,1];
output uses 17 significant digits, so `0.1` writes `0.10000000000000001`.
Options cannot be abbreviated or repeated; `--name=value` is accepted.
Success is silent, exit 0; usage errors return 2, admission/publication errors 1.

## Complete state mapping

The selected bank receives the chosen nine digits on each enabled manual.
The other bank is explicitly zero. An `off` part has both banks zero and route
disabled, while retaining the same selected-bank label. Both pedal positions
are zero. Percussion is Off / Second / Normal / Slow. Expression is the requested
normalized nominal value. Every record uses the existing canonical order,
single ASCII spaces and LF line endings, including the final newline.

## Catalog and publication boundary

Input must be a stable nonsymlink/non-reparse regular file of 1..65,536 bytes.
Duplicate JSON members, unknown fields, float/nonfinite JSON tokens and wrong
types reject. The public `validate_authoring` function checks all documentary
semantics. The wrapper additionally requires the exact format, input fields,
lowercase SHA-256 strings, authoring byte count 1..65,536, and both frozen review
hashes with exact integer byte counts 466. The canonical semantic authoring hash
is independently recomputed. Raw authoring hash/count remain declared metadata;
the unavailable original bytes are not authenticated. A valid wrapper is not
proof that the producer read the cited PDF or independently acquired its source.

The public API raises `ChapelControlsError`: `load_catalog(path)` returns the
validated object; `validate_catalog(data)` returns its authoring view;
`render_controls(catalog, upper="off", lower="off", bank="A", expression="0.75")`
returns text; `write_controls_file(output, text, catalog_path)` publishes it.
The writer revalidates catalog and bounded canonical audition text, including
reviewed selected rows, zero unused banks and fixed percussion/pedal settings.

A same-parent temporary file is written, flushed and file-synced, then an atomic
hard link creates the destination without replacement. The filesystem must
support hard links. Existing files, directories, symlinks, reparse leaves and
aliases reject; a competing destination appearing after preflight also survives.
Before that link succeeds, ordinary rejection/failure leaves no output and
preserves inputs. Temporary cleanup follows publication; if cleanup itself
fails, a complete newly published output may remain while an error is reported.
Hostile concurrent filesystem mutation and power-loss durability are unclaimed.

## Executed evidence and next gate

[Assignment 38](development/2026-11-13-next-phases/38-chapel-controls.md) records
205 complete exported states, 57 API rejections, 19 actual file rejections,
14 CLI invocations and two injected publication failures, all passing on Linux.
These producer probes do not establish native parsing or physical fidelity.
Assignment 39 independently checks exact state bytes and actual app loading;
root owns its CMake, coherent integration, hosted-platform and publication gates.
