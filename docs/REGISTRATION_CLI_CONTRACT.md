# Headless registration CLI contract v1

**Proposed for independent admission, 16 November 2026.** This adds file
preparation to M9; it establishes no live recall, audio acknowledgment, physical
registration provenance or browser completion.

## Boundary and implementation paths

Implement `hammond_registration` in `tools/registration.cpp`; optional
`tools/RegistrationToolIO.h/.cpp` contain only JSON/argv transport. Share
`tools/ControlFileInput.h/.cpp` with `hammond_render` for arbitrary-file reads.
Reuse
[`RegistrationLibrary`](../apps/standalone/RegistrationLibrary.h) for root
resolution, catalog admission, selected reads, scope merging and create-only
saves; reuse [`ControlStateIO`](../include/hammond/ControlStateIO.h) for every
musical parse/serialization. Do not reproduce its musical grammar or migrations.
Root owns build/install integration. The ordinary non-SDL build must expose the
tool; it needs no profile, display, audio device, Engine instance, Session,
LibraryModel, browser or native application integration.

Preserve 47 parameter identities, all retained control fields, the fixed-catalog
identity, `B3CONTROLS4`, readers 1–3 and the nominal dry Engine. No saved document
contains notes, phase, contacts, percussion readiness, clocks or host state.

## Command and argument grammar

```text
hammond_registration list --library DIR
hammond_registration inspect --library DIR --key KEY
hammond_registration import --input FILE --library DIR --name NAME --scope registration|performance
hammond_registration materialize --library DIR --key KEY [--current FILE] --destination DIR --name NAME
hammond_registration --help
```

`--current` is **mandatory for Registration and forbidden for Performance**.
Materialize always creates `NAME.b3performance`. Import chooses the suffix using
its explicit scope, irrespective of the input filename. Both retain expression
in their stored payloads. There is no overwrite, batch, stdin, response-file,
report-file or arbitrary-output-filename mode.

After the verb, option/value pairs may appear in any order, exactly once.
Reject unknown/missing/duplicate options, extra positionals, `--opt=value`,
abbreviations, empty values and values beginning `--` (use `./` for such paths).
`--help` must stand alone. Validate before filesystem mutation. Limit argc to
12 including executable, each user token to 4,096 UTF-8 bytes and their total to
16,384 bytes; reject invalid UTF-8 and ASCII control bytes, including DEL.
Resolve relative paths against the invocation working directory once; limit
resolved native paths to 8,192 bytes on POSIX or 8,192 UTF-16 code units on
Windows. Use native Unicode paths on Windows. No environment-selected default
directory is consulted.

Use a local registration Windows entry adapter: strictly convert UTF-16 user
arguments and route invalid encoding/count/byte-limit failures through the same
JSON `UsageError`/exit 2 reporter, with command null when unavailable. Unexpected
adapter exceptions use `InternalError`. Do not reuse or change the shared
`CliArguments.h::run_windows` error path, which reports plain stderr.

Use the existing name validator: 1–48 ASCII bytes, alphanumeric ends, interior
alphanumerics/spaces/hyphens/underscores, existing DOS-reserved-name exclusions.
KEY is an exact validated relative filename including its case-sensitive
`.b3registration` or `.b3performance` suffix; no normalization or path separators.
Malformed key syntax is `UsageError`/2; a valid absent key is `NotFound`/3.

## Reads, catalog selection and scope

`list` returns the entire bounded scan, in the library's deterministic order.
Retain its 128-candidate, 512-directory-item and diagnostic limits, invalid-name
counts and disabled entries. Missing/empty directories are distinguishable,
complete read-only results; neither is created. Failed scans expose no partial
rows as a complete catalog.

`inspect` and `materialize` first require a complete catalog and an exact-key
row with `Valid` status. A complete scan can contain unrelated warning rows;
those remain reported. A missing key fails; an ambiguous key fails even when
one spelling is an exact match. Only then call `read_registration_entry` and
require validity and full `ControlSnapshot` equality with the scanned copy.
Any intervening semantic change fails as `SourceChanged`; scoped equality is
insufficient because it ignores Registration expression. Inspect serializes
that validated copy to canonical state4 for its report.

Arbitrary `--input`/`--current` files need the same safe bounded policy as library
entries. Open the leaf without following symlinks/reparse points, inspect the
opened handle, and accept regular disk files only. POSIX uses
`O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC` plus `fstat`; Windows opens with
`FILE_FLAG_OPEN_REPARSE_POINT|FILE_FLAG_BACKUP_SEMANTICS`, checks file type and
rejects directory/reparse attributes. Reject Windows device/pipe namespaces
before opening. Existing directory symlink ancestors may resolve normally;
never canonicalize away a file's leaf link before opening. A pre-open
`is_regular_file` check followed by `ifstream` is insufficient.

Reject reported sizes above 16,384 bytes; read at most 16,385 bytes to detect
growth, handle interrupted reads, and report read/close failure. No FIFO/device
read may hang. Only pass admitted bytes to `parse_controls`; it owns malformed,
trailing, unsupported-version and catalog-identity rejection. Readers 1–3 retain
their published migrations: fixed modes become None; versions 1–2 also zero
pedals; version 1 additionally supplies Off/Second/Normal/Slow percussion.
Every output uses `serialize_controls` and canonical state4.

The shared header declares, in `hammond::tools`:

```cpp
enum class ControlFileInputStatus {
    Read, Unavailable, NotRegularFile, TooLarge, InvalidPayload
};
struct ControlFileInput {
    ControlSnapshot controls;
    std::string canonical_controls;
    unsigned source_version{};
    std::size_t source_bytes{};
};
struct ControlFileInputResult {
    ControlFileInputStatus status;
    std::string reason;
};
ControlFileInputResult read_control_file(
    const std::filesystem::path&, ControlFileInput& destination);
```

Failure preserves the entire destination; success replaces it with the parsed
snapshot, canonical state4 string and original version/byte count. Determine
version from the already admitted header only after `parse_controls` succeeds;
this is provenance extraction, not independent format admission. Diagnostics
are bounded to 256 bytes. The helper depends on core only; CLI and renderer
must share it rather than copy OS read code.

Registration materialization calls `merge_registration_controls` with the entry
and validated current-file snapshot: only current expression survives; every
other field comes from the entry. Performance uses its whole saved snapshot.
Generic standalone `--state` Load restores the entire produced document,
regardless of suffix; the CLI performs the expression merge beforehand.

## Single-file write and authorization

Import/materialize call `save_registration_entry_new`, never the replacing
legacy state-file helper. Protect every supplied input file and selected library
entry, retaining both invocation paths and resolved-parent/unchanged-leaf paths.
Pass these to the existing alias/case-aware protected-path checks for destination,
root and staging creations. Do not weaken unresolved-alias refusal. The writer
owns collision/capacity checks, bounded staging, flush/close, final admission and
atomic no-replace publication. A missing destination may be created only with
an existing parent; failure can leave an empty created directory or cleanup
diagnostic. Existing destination bytes must survive every refusal.

The mandatory final authorizer means **“this explicit offline file request still
matches its admitted input snapshots,” never “live controls acknowledged.”**
It re-reads input/current files safely and compares full snapshots. For
materialize it also repeats complete source-catalog admission and fresh exact-key
read against the captured snapshot. Any failure/change denies authorization;
no event pumping, Session receipt, retry or new intent is permitted. Equivalent
whitespace/version representations may compare equal after migration. No file
lock or immunity to changes after these checks is claimed.

Preserve `SavedWithWarning` and `committed_entry` when cleanup/refresh fails.
Never remove or retry a committed output automatically. Single-file publication
does not imply batch atomicity or power-loss durability. Shell redirection is
outside this writer: it may truncate a file before process startup, so callers
must not redirect reports onto inputs or intended outputs.

## JSON and process results

Except a failed output stream, every invocation emits one JSON object plus LF
on stdout, without progress text. `--help` also uses this envelope. Stderr is
empty normally; on stdout failure, emit one bounded fallback diagnostic there.
Use locale-independent formatting and JSON escaping; replace invalid UTF-8 in
OS diagnostics with U+FFFD. Cap each diagnostic at 256 UTF-8 bytes without
splitting a codepoint; cap the whole encoded report at 1 MiB. Reserve its bounded
buffer before writes. No timestamps, addresses or implicit live-state claims.

All envelope fields are present:

| Field | Value |
| --- | --- |
| `schema` | `hammond-registration-cli-v1` |
| `command` | Verb, `help`, or null for invalid command grammar |
| `outcome` | `ok`, `warning`, or `error` |
| `code`, `message` | Stable status token and bounded explanatory text |
| `committed` | True/false for known publication; null only if a save throws with unresolved publication |
| `catalog` | Source catalog for list/inspect/materialize, otherwise null |
| `entry` | Selected entry for inspect/materialize, otherwise null |
| `input` | Supplied input/current object, otherwise null |
| `save` | Save result object, otherwise null |
| `usage` | Array of the five syntax strings for help, otherwise null |

Catalog objects contain `status`, `complete`, `reason`, `directory_items`,
`candidate_count`, `invalid_name_count`, `invalid_entry_count`,
`ambiguous_entry_count`, `warning_count`, and `entries`. Rows contain `key`,
`name`, `scope` (lowercase), `status`, and `reason`. Selected entries additionally
contain `canonical_controls`, or null when invalid. Save objects contain
`status`, `reason`, `key`, `scope`, `path`, and `refreshed_catalog`; absent results
are null. Library status tokens exactly match their public enum spellings.
Canonical text exposes every retained field without introducing another state
schema. Input objects contain `path`, `source_version`, `source_bytes` and
`canonical_controls`; unavailable fields are null. Report source key and
captured canonical controls even if later authorization fails.

Every non-null `path` is an informational object with `encoding` and `value`:
`posix-bytes-hex` encodes exact native POSIX bytes as lowercase hexadecimal;
`windows-utf16le-hex` encodes native UTF-16 code units low-byte-first. This covers
resolved ancestors containing non-UTF-8 bytes without invalid JSON or lossy
identity. Paths are never inserted as raw native strings. Diagnostic replacement
does not substitute for this exact path encoding.

| Exit | Meaning and code policy |
| --- | --- |
| 0 | Successful, warning-free result; list may be Empty/MissingDirectory; help code `Help` |
| 1 | Successful with catalog warnings or `SavedWithWarning`; retain actual save status |
| 2 | `UsageError`, including invalid name/scope and scope-dependent current argument |
| 3 | Admission refusal: invalid/nonregular/oversize payload, missing/invalid/ambiguous entry, incomplete capacity/root admission, collision, protection or authorization refusal |
| 4 | Filesystem open/read/close, directory, staging, write/flush/close or commit failure before publication |
| 5 | `ReportFailed`: stdout write/flush/broken pipe failed; a write may already have committed |
| 70 | `InternalError`: unexpected exception/invariant failure; preserve known publication, otherwise report unknown after entering save |

Code uses the applicable public catalog/entry/save status. Additional tokens are
`NotFound`, `SourceChanged`, `InputUnavailable`, `InputNotRegularFile`,
`InputTooLarge`, `InvalidPayload`, `UsageError`, `Help`, `ReportFailed`, and
`InternalError`. Source revalidation refusal reports save status `NotAuthorized`.
Failure takes precedence over warnings; a successful operation with any reported
catalog warning exits 1. An incomplete catalog cannot authorize a read selection
or publication. An incomplete post-publication refreshed catalog retains
`SavedWithWarning`, `committed: true`, the committed entry and exit 1; report the
actual failed refreshed-catalog status. POSIX report handling must prevent default
SIGPIPE termination so the existing `ReportFailed`/5 outcome remains observable.

## Required acceptance

Add subprocess coverage in `tests/test_registration_cli.py` and focused native
I/O tests if needed. Exercise all commands, argv bounds/rejections, JSON escaping,
native non-UTF-8 ancestor path encoding, stdout failure, deterministic ordering,
missing/empty/unavailable/overflow
catalogs, exact capacity edges and exact-key case ambiguity. Verify inspect
creates nothing and every refusal preserves existing output bytes.

Check all retained fields, leading zeros, cancelled-manual memory, state1–3
migrations, state4 catalog mismatch, trailing/malformed input, 16-KiB boundaries,
and both expression scopes with a nondefault current value. Test directories,
leaf/ancestor links, hard-link/case aliases and FIFO rejection under subprocess
timeouts. Exercise source mutation between admission and authorization,
collisions, denied authorization and committed-warning reporting through
test-only seams, without production fault flags. Independently load/reinspect
produced state4 files. Root qualifies Linux/macOS/Windows and the non-SDL build;
this contract records no executed implementation passes.
