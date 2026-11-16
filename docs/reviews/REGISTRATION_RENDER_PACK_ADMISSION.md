# Registration renderer and starter-pack admission

Independent reviewer: A11, `/root/w02_a11`, 16 November 2026.

## Decision and evidence boundary

Admit `registration-render-controls-v1` for implementation. Admit
`starter-registration-pack-v1` after the manifest clarification below is added
before independent manifest/generator authoring. Root agreed to that clarification.
The remaining requirements are sufficient; no new model, diagnostic API or
product gate is required. These are proposed contracts: **no implementation,
asset, build, audio, installation or platform pass is claimed**.

Reviewed [renderer contract](../REGISTRATION_RENDER_CONTRACT.md),
[pack contract](../STARTER_REGISTRATION_PACK_CONTRACT.md), the shared reader and
transport requirements in [CLI contract](../REGISTRATION_CLI_CONTRACT.md),
`tools/render.cpp`, `tools/CliArguments.h`, `ControlState`, `ControlStateIO`,
`Engine::restore_controls` and `RegistrationLibrary` APIs/implementations.
The session note records reviewed input hashes. Full AGENTS and PLAN obligations
remain binding.

## Required pack clarification

Replace “native enum token spellings” with explicit **state-format tokens**:
selected banks `A`/`B`; fixed modes
`none`, `C#`, `D`, `D#`, `E`, `F`, `F#`, `G`, `G#`, `A`;
percussion harmonic `second`/`third`, volume `normal`/`soft`, decay `slow`/`fast`.
This avoids C++ spellings such as `None`/`DSharp` disagreeing with the native
parser's `none`/`D#`.

Freeze `drawbars` as an outer two-element Upper/Lower array, each containing two
A/B nine-digit strings. `selected_banks`, `route_enabled` and
`fixed_registrations` are two-element Upper/Lower arrays; `pedal_drawbars` is a
two-integer Mixture 1/2 array. Keep Boolean routes/percussion-enabled and numeric
expression. Specify `name` as the exact numbered filename stem and both file
fields as exact basenames resolved beneath `entries/`. These declarations fix
the already requested literal oracle; they add no payload or musical fields.

## Renderer findings

The existing renderer prepares Engine, applies fifteen default drawbar/percussion/
pedal events through a zero-frame flush, then processes the stable score. The
new branch must skip that entire flush. Restoring before any score application
or positive process call, at clock zero, is the correct boundary. The unchanged
`Engine::restore_controls` directly delegates to the validated full assignment
in `ControlState::restore` and marks coefficients dirty; it does not reset
phase, contacts, readiness or clock.

The proposed conflicts use explicit flag presence, so even explicitly supplied
default values reject. Score overrides and tied-event order remain valid.
Equivalent independent initialization scores must write all banks, select each
remembered bank, then select its fixed mode if present, then Cancel if required,
before notes. Otherwise selecting a bank clears the fixed memory that the oracle
was supposed to reproduce.

Signed zero survives the existing decimal parser, serializer and direct restore.
`ControlSnapshot::operator==` nevertheless compares `+0.0` and `-0.0` equal, and
PCM cannot distinguish their silent expression results. Existing acceptance must
therefore compare literal canonical `expression -0` and trace the actual restore
branch without a later setter. If a focused native snapshot comparison is used,
include `std::signbit`; default equality alone is insufficient. The report's
canonical text describes the initial admitted snapshot, never the post-score
state. No new diagnostics are needed.

Legacy migrations are correctly delegated: versions 1–3 set fixed modes None,
1–2 mute pedals, and 1 supplies all four percussion defaults. Suffixes do not
alter full-state rendering. Expression-preserving Registration behavior belongs
to materialization. Contacts/profile/seed/leakage remain independent physics and
render choices, preserving the nominal dry boundary.

## Compatibility, provenance and file policy

The inspected source emits schema 3, or 5 with leakage. Controls must select
schema 6 only on their own branch, retaining applicable leakage/headroom fields.
Schema 4 is an integration obligation only if its separately owned source path
is actually integrated. Retained-baseline comparisons must include exact stdout
and WAV bytes; help's documented addition is the explicit exception.

The shared no-follow reader must receive an unchanged leaf: reusing existing
`checked_input` first would resolve away its symlink rejection. Preserve bounded
16,385-byte excess detection and all existing no-replace publication checks.
Renderer controls-path UTF-8 validation must precede WAV mutation and stay on
the new path. Do not impose it on old no-controls invocations. The CLI's exact
native-path hexadecimal objects and the renderer's explicitly admitted UTF-8
string are different documented transports, not a shared JSON schema.

Schema 6 correctly separates raw byte count/source version from canonical
state4 identity. Final LF, migrated fields, JSON escaping, signed zero and
pre-score provenance all require exact assertions. Paths remain locators;
neither paths nor canonical text are raw-file hashes.

## Pack production and delivery

The proposal contains twelve complete recipes and twenty-four payloads, with
identical canonical bytes within each suffix pair. The independently authored
manifest must expand every retained field; generation must neither consume nor
produce its expectations. Regeneration equality alone cannot establish recipe
correctness. Rows 10–12 need pedal/cancelled/fixed-memory journeys; rows 7–8 need
eligible percussion notes, with later bank selections exposing hidden values.

Create-only storage, all-recipes prevalidation, explicit empty staging and
immutable-intent final authorization are appropriate. Report committed files,
`SavedWithWarning`, the first failure and the unattempted remainder accurately;
preserve partial results without retries or rollback claims. Fixed-list,
copy-only installation contains exactly 24 payloads plus README/manifest and
must not invoke generation or populate a user's library. Existing collision,
relocation/DESTDIR, installed-consumption and independent state/audio checks
are sufficient. Native browser, physical and whole-interface claims remain
outside this admission.
