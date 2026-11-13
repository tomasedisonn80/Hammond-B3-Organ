# Standalone control-state files

`apps/standalone/StateFiles.h` provides `load_control_file(path, destination,
error)` and `save_control_file(path, controls, error)`. Both accept native
`std::filesystem::path` values. They are main-thread operations: parsing,
formatting, allocation, file access and cleanup stay outside the audio callback.
The caller supplies a safely copied control snapshot and publishes a successful
load through the standalone Session protocol; these helpers never access Engine.

## Retained musical state

The existing [control-state format](CONTROL_STATE_FORMAT.md) remains authoritative.
New saves contain canonical `B3CONTROLS3`: all 45 retained controls and both
manual route-enable bits, including hidden banks and inaudible settings. Held
notes/pedals, ownership, contact movement, percussion readiness, source phases,
processing clocks, filter histories, device choices and window state are absent.
Saving is not an exact audio-resumption checkpoint.

Loading accepts versions 1, 2 and 3. Version 1 explicitly supplies default
Off/Second/Normal/Slow percussion and muted pedals; version 2 supplies muted
pedals. Existing destination values never fill omitted legacy fields. Re-saving
either legacy version writes version 3. The inclusive input limit is 16,384
bytes, including whitespace; malformed, truncated, extended, oversized and
unsupported-version documents reject as specified by the existing parser.

## File policy and failure behavior

| Operation | Contract |
| --- | --- |
| Load | The named leaf must already be a regular file. A successful call replaces the complete destination snapshot and clears `error`; a rejected call preserves all destination fields and supplies a diagnostic. |
| Save | Controls validate before file work. An existing named leaf must be regular; a missing leaf is allowed. A successful call publishes the complete canonical document and clears `error`; a rejected call preserves the existing destination file. |
| Filenames | Empty paths, trailing separators and `.`/`..` as the filename reject for saves. Missing parents are errors; callers create or select their destination directory. |
| Nonregular leaves | Directories, symbolic links and other nonregular entries reject. A dangling symbolic link also rejects, and neither its link nor its referent is changed. |
| Native paths | Spaces and Unicode names use the filesystem path API; file contents retain the ASCII control grammar. |

The regular-file test uses the final entry's link status. It does not prohibit
symlinks in parent directories or establish security against hostile concurrent
path replacement. Callers own path selection and access to the containing
directory. A save does not promise preservation of the old file's permissions,
ownership, hard-link relationship or other filesystem metadata.

Save writes and closes a complete document in a newly created `.b3-save-*`
directory within the destination's parent, then replaces the named file. The
temporary file and directory are scoped for cleanup on successful and rejected
calls. Existing content is not opened for in-place truncation. Ordinary failures
are reported by `false` and a diagnostic; allocation exceptions can propagate,
as in the underlying control serializer/parser.

The same-filesystem rename/replacement is the publication step. Atomic visibility
of a replacement is distinct from power-loss durability: C++ stream flush/close
and the current platform replacement calls do not establish a retained crash or
power-loss recovery guarantee. Directory durability, abrupt process termination,
hostile filesystem races, concurrent saves and metadata preservation are separate
policies. This helper creates no backup, history, directory tree or recovery UI.

## Maintained acceptance

`test_standalone_state_files` is discovered by the SDK-free standalone test glob.
It links the real support/core libraries and uses independent literal grammar
and field expectations. Its seven scenario groups cover:

- Complete controls, native Unicode/space paths, exact canonical bytes and overwrite.
- Literal version-1/version-2 migration followed by canonical version-3 saves.
- Corrupt/truncated/trailing/future-version/oversized input, unchanged destinations,
  unchanged source files and the inclusive maximum input length.
- Invalid drawbars, selectors, expression, percussion enums and pedals preserving
  existing bytes; invalid input also cannot create a new target.
- Missing parents, directory leaves, a file used as a parent and empty filenames.
- Regular and dangling symbolic-link rejection with unchanged links/referents.
- Failure after temporary creation and a successful retry with unchanged old bytes.

Every API call is followed by a recursive check for orphan `.b3-save-*` entries.
Fixtures live only in a uniquely created temporary tree, with exception-unwinding
RAII cleanup and explicit successful cleanup verification.

POSIX builds force a bounded write failure with `RLIMIT_FSIZE`, restoring the
process limit and signal handler afterward. Windows builds hold the destination
without delete sharing to force replacement failure. Symbolic-link creation
capability is reported explicitly: an unavailable capability is **not tested**,
not an exercised pass. POSIX final-rename failure is explicitly not tested when
there is no deterministic non-racing fixture; root-sensitive permission tests
are not used.

The [assignment-20 report](development/2026-11-13-next-phases/20-state-files.md)
records the actual Linux run, hashes and commands. Windows/macOS execution,
abrupt termination, power-loss behavior, native application publication and
physical-device/audio fidelity remain outside that result.
