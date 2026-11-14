# Offline fixed-registration selection

The offline renderer accepts `select_preset` in the existing five-field score
format. It uses the immutable, build-admitted eighteen-row catalog under the
[exclusive selection contract](PRESET_SELECTION_CONTRACT.md), through the same
Engine event as the native adapters. The CLI does not parse catalog JSON or
controls files at runtime. The result remains a synthetic, unmeasured dry-organ
render, with the existing nominal drawbar gain law.

## Event grammar and ordering

```text
absolute_frame select_preset upper|lower 0 selection
```

The frame and index retain the unsigned-decimal token grammar. Index must be
exactly zero. The value must parse as a finite binary64 integer in `0..11`;
equivalent decimal spellings such as `1.0`, `+2`, `3e0` and `11.0` are admitted.
Signed negative zero is an admitted zero and means Cancel. Fractions, other
indices, unknown manuals, nonfinite values, overflow and underflow-to-zero reject.

| Value | Reverse key | Action |
|---:|---|---|
| 0 | C | Cancel this manual's route |
| 1 | C# | Select the manual's fixed C# row |
| 2 | D | Select the manual's fixed D row |
| 3 | D# | Select the manual's fixed D# row |
| 4 | E | Select the manual's fixed E row |
| 5 | F | Select the manual's fixed F row |
| 6 | F# | Select the manual's fixed F# row |
| 7 | G | Select the manual's fixed G row |
| 8 | G# | Select the manual's fixed G# row |
| 9 | A | Select the manual's fixed A row |
| 10 | A# | Select retained adjustable bank A |
| 11 | B | Select retained adjustable bank B |

Fixed A (9) and adjustable A# / bank A (10) are distinct. The atlas does not
publish historical voice names for these rows. Each manual has its own nine
fixed rows; choosing a row does not copy its positions into either retained bank.

A fixed selection reconnects its manual. Cancel preserves the retained fixed
choice and A/B values while muting the manual route. Held keys and continuously
running source phases remain intact. A later fixed or bank selection reconnects
the held notes. Both the old `select_bank` event and selector values 10/11 clear
fixed mode, including when the requested bank was already remembered. `drawbar`
still edits that remembered bank; `bank_drawbar` still edits its explicit bank.
Neither edit leaves fixed mode or reconnects a cancelled route.

Equal-frame commands act in file order. For example, these two commands finish
on bank B even when B was remembered before the fixed selection:

```text
36000 select_preset upper 0 3
36000 select_bank upper 0 1
```

Reversing those lines finishes on fixed D#. A fixed selection followed by Cancel
at the same frame leaves no sounding interval between the commands. Selection
does not itself advance time, create a note gesture or reset contact/percussion
history. Fixed upper registrations are outside upper-B percussion eligibility.

The complete score is admitted before rendering or publishing output. A later
invalid selector rejects earlier valid lines together with it. The producer
rejects the score before launching the renderer or creating an evidence result
directory. Existing outputs and input bytes remain untouched. Existing time,
file, line, total-event and same-frame limits are unchanged; see
[RENDER_FORMAT.md](RENDER_FORMAT.md).

## Catalog and demonstration provenance

| Identity | Frozen value |
|---|---|
| Catalog ID | `atlas-chapel-nominal-v1` |
| Authoring file | `data/registrations/atlas-chapel-nominal-v1.json` |
| Authoring raw-byte SHA-256 | `c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf` |
| Atlas PDF SHA-256 | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Source locator | Printed/PDF page 122; chapel preset tap table |
| Selection contract | `exclusive-fixed-registration-v1` |

The native-data build checks the authoring file and both frozen independent CSV
readings before admitting the fixed matrix. These are documentary tap indices,
not measured loaded gains or a physical multi-latch/contact model. The underlying
factory Table IV and specimen wiring remain separately unverified; the
[catalog documentation](CHAPEL_PRESETS_CATALOG.md) retains that boundary.

The new [selector demonstration](../examples/fixtures/presets/selector-events-v1.txt)
includes the catalog and PDF identities in score comments. It holds upper and
lower chords, changes fixed rows, uses negative-zero Cancel, and returns to the
remembered B bank through both the old and new commands. The same-frame pair at
36000 ends on B; the pair at 60000 ends cancelled. Render it with an existing
`out` parent and an unused result directory:

```sh
python3 tools/render_fixture.py \
  --renderer build/hammond_render \
  --output-dir out/preset-selector-evidence \
  --events examples/fixtures/presets/selector-events-v1.txt \
  --frames 96000 --sample-rate 48000 --block-size 127 --seed 7 \
  --drawbars 000000000 --pedal-drawbars 00 --percussion off
python3 tools/verify_render.py out/preset-selector-evidence
```

The source score is new. Previously retained chapel bank-copy controls,
event/WAV/catalog fixtures and evidence bundles keep their original bytes and
meaning. This demonstration does not change the legacy `chapel_controls.py`
audition workflow.

## Current and historical evidence

`select_preset` is supported only by the current **manifest schema 3** event
grammar. Renderer stdout remains `render_schema_version: 3`; the exact existing
31 metrics, fourteen parameters, 28 invocation strings and retained artifact
inventory are unchanged. No fixed-catalog metric or new manifest field is
invented. The saved-control format's independent version 4 does not change the
render-evidence envelope.

The independent verifier explicitly rejects `select_preset` under schemas 1
and 2, including when an event file and its manifest hashes are rewritten
consistently. Their historical event meanings remain frozen. Current consumers
must understand this schema-3 command to admit a bundle containing it; earlier
consumers that do not know the command reject it.

The existing source/profile, wrapper, executable and exact event-byte hashes
remain the evidence records. The catalog identity above and the demonstration's
retained comments explain this new selector's source basis; they do not
retroactively authenticate an old executable or rewrite older bundles. A
successful independent verification checks retained bytes and assertions; source
build association, executable authenticity, replay and physical fidelity retain
the limits documented in [RENDER_VERIFICATION.md](RENDER_VERIFICATION.md) and
[PEDAL_RENDER_EVIDENCE.md](PEDAL_RENDER_EVIDENCE.md).

## Acceptance entry points

Build `hammond_render` and its generated profile from one coherent source tree,
then run:

```sh
ctest --test-dir build --output-on-failure --no-tests=error \
  -R '^python_test_(render|render_fixture|verify_render)$'
```

The focused additions compare every fixed row with independent literal bank
events through the real CLI and independently verify real schema-3 bundles.
They also cover stable ties, Cancel and existing-bank return, accepted decimal
spellings, full-file rejection before output/launch, exact event bytes, and
rehashed invalid or historical-schema inputs. The
[A24 execution record](development/2026-11-14-preset-continuation/24-offline-events.md)
identifies the tested source, commands, actual results and remaining gates.
The core's broader continuous-history and lifecycle acceptance remains separate.
