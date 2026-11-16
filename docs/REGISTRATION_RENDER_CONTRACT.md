# Offline rendering from saved controls

Contract: `registration-render-controls-v1`, 16 November 2026. Proposed
implementation input; independent admission and executed acceptance are required.
Basis: [state format](CONTROL_STATE_FORMAT.md), [renderer](RENDER_FORMAT.md),
[library scopes](REGISTRATION_LIBRARY_CONTRACT.md) and current-session
[A01](development/2026-11-16-preset-library-continuation/notes/A01.md),
[A02](development/2026-11-16-preset-library-continuation/notes/A02.md),
[A03](development/2026-11-16-preset-library-continuation/notes/A03.md) and
[A05](development/2026-11-16-preset-library-continuation/notes/A05.md).

## Invocation and precedence

Add one value-taking option to `hammond_render`:

```sh
hammond_render --profile profile.b3profile --controls saved.b3registration \
  --events phrase.events --output audition.wav
```

`--controls FILE` restores **all saved controls, including expression**, regardless
of `.b3registration`, `.b3performance`, `.b3controls` or another suffix. It performs
no scope merge and claims no live-session state. Registration expression
preservation belongs to the separate library recall/materialization operation;
render its already materialized output when that behavior is wanted.

Reject duplicate/missing/oversized values through existing option admission.
Reject `--controls` combined with an explicitly supplied `--drawbars`,
`--pedal-drawbars`, `--percussion`, `--percussion-volume` or `--percussion-decay`,
even when that value equals a default. Never resolve conflicts by argument order.
Allow `--events`; its stable score ordering runs after restoration, including
frame-zero overrides. Without a score, retain the existing default-note/`--note`
behavior. Preserve the existing explicit `--note`/`--events` conflict.

`--contacts ideal|nominal` remains an independent console-physics choice, with
its existing default and evidence limits. Profile, seed, source leakage and its
explicit gain, rate, duration, block size and clipping policy remain separate
existing options. A controls file installs no physical profile or audio effect.

## Admission, restoration and preservation

Reuse the core-only `tools/ControlFileInput.{h,cpp}` helper specified by the
[headless CLI contract](REGISTRATION_CLI_CONTRACT.md):
`hammond::tools::read_control_file` supplies a copied
`ControlFileInput` with snapshot, canonical text, source version and byte count.
It uses no-follow/nonblocking regular-file admission, `parse_controls` and
`serialize_controls`; no SDL/Session/Engine dependency or duplicated OS reader.
Do not canonicalize away the final-component symlink before helper admission.
Apply its **16,384-byte whole-input limit**, including whitespace, with bounded
excess-byte detection. A size precheck cannot replace bounded parsing.
Accept state versions 1–4 with their unchanged migrations. Refuse malformed,
future, truncated, trailing-data, nonfinite and wrong-catalog inputs transactionally.
Never rewrite the source or silently repair its fields.

Validate controls and every other input before creating a temporary WAV directory,
opening a WAV or publishing output. Preserve every input and existing destination
on failure. Include controls in input/output collision protection: canonical
paths and symlink aliases must reject; an existing hard-link alias or any other
existing destination must also reject. Retain atomic no-replace WAV publication
for a destination appearing after preflight. Test spaces and non-ASCII path names
through the existing portable path utilities.

Prepare Engine using the existing profile/spec/console selection; restore the
validated snapshot with `Engine::restore_controls` while stopped, before any
scored event, default note or positive processing call. Check restoration success
and a zero frame clock. With `--controls`, skip the old initial drawbar/percussion/
pedal event flush entirely. No default setter may subsequently overwrite restored
controls. Score parsing may precede restoration; score **application** may not.

Restore all 36 positions, both remembered banks, both routes, both retained fixed
modes, both pedal positions, all four percussion settings and expression. Hidden,
cancelled and currently ineligible fields remain exact. Restore no held notes,
contact history, percussion readiness, phase or clock. Preserve the 47 parameter
identities, frozen catalog, 91 sources, nominal Engine and existing state APIs.
No native app, browser, LibraryModel or processing-callback changes belong here.

## Versioned output provenance

Renders **without** `--controls` retain exact existing audio, stdout JSON shape,
schema selection and behavior: currently schema 3, or 5 with leakage; retain
separately owned schema 4 if that source path is integrated. Help gains the option
and its full-state/expression explanation. Do not broaden old evidence readers.

With controls, emit `render_schema_version: 6`, retain every applicable existing
base/source/leakage field, and add exactly this `controls` object:

| Field | Value |
| --- | --- |
| `schema_version` | Integer `1` |
| `restore_policy` | `full-state-including-expression` |
| `path` | Resolved input path in valid UTF-8, correctly JSON-escaped; informational locator |
| `source_version` | Integer `1` through `4`, from the successfully admitted header |
| `source_bytes` | Actual admitted raw byte count, including whitespace |
| `canonical_b3controls4` | Exact successful `serialize_controls` output for the initial parsed snapshot, including final LF, JSON-escaped |

The canonical text is the **exact semantic identity** used for restoration,
including migrated defaults and signed zero; it is not the post-score state.
Validate path conversion and UTF-8 before WAV mutation; reject non-UTF-8 POSIX
names or failed conversion explicitly. Never emit invalid JSON or lossy path text.
Whitespace-equivalent inputs can share this identity. Do not invent a runtime
hash or treat a path as identity. Evidence tooling may separately retain SHA-256
of actual raw controls, score, profile, executable and output bytes. Raw identity
and canonical identity answer different questions. Keep `unmeasured` evidence
labels and existing success/error/clipping exit meanings.

## Required independent acceptance

1. Exercise the actual executable with literal states 1–4; all fixed modes on
   both manuals; cancelled fixed memory; distinct hidden banks; nondefault pedals,
   percussion and expression, including signed zero. Compare canonical summary
   text with independently expected complete snapshots.
2. Compare complete WAV bytes against an equivalent independently authored score
   that initializes every control at frame zero before notes. Reveal retained
   banks through later selections; compare fixed selections with literal known
   rows. Include cancellation, reselect, pedal notes and eligible/ineligible
   percussion. Mere parse/serialize equality is insufficient audio evidence.
3. Prove score precedence at frame zero and later tied events. At 44.1/48/96 kHz,
   compare complete PCM/WAV under block sizes 1, 17, 64, 127 and 512 with both
   contact choices, boundary events and a fixed seed; require nonempty audible
   fixtures where expected. Do not normalize outputs.
4. Verify conflicts, bounds at 16,384/16,385 bytes, malformed/future/catalog
   refusals, aliases, destination races and no input/output mutation. Cover
   controls plus leakage without weakening existing headroom admission.
5. Compare representative no-controls WAV **and stdout bytes** with a retained
   genuine baseline executable; rerun existing renderer/state suites and explicit
   schema assertions. Record source, executable, inputs, commands and limitations.
