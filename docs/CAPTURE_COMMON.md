# Shared offline capture JSON primitives

`tools/capture_common.py` supplies dependency-free Python 3.10+ primitives for the
new capture tools. It does not replace capture v1 validation and has no command-line
side effects. Import it from the tools directory. Contract-specific validators
still own required keys, exact numeric types, units, semantics and confined roots.

## Public API

| API | Result and scope |
| --- | --- |
| `read_bytes(path, *, max_bytes=1048576)` | Exact bytes from a bounded regular, nonsymlink, non-reparse file. Detects observed size/identity/stat changes during reading. |
| `parse_json_bytes(payload, *, max_bytes=1048576, max_nodes=65536, max_depth=32, max_number=1e12)` | Strict UTF-8 JSON from an exact `bytes` object, rejecting duplicate keys, nonfinite/excessive numbers, malformed Unicode, oversized tokens and bounded nesting/nodes. |
| `read_json(path, *, same limits)` | `(value, {sha256, size_bytes})`, where the identity belongs to exactly the bytes parsed, including whitespace. |
| `validate_json_value(value, *, max_nodes=65536, max_depth=32, max_number=1e12)` | Nonmutating bounded admission of direct JSON values; rejects tuples, non-string keys and other non-JSON objects. Semantic validators separately distinguish Boolean and integer fields. |
| `canonical_json_bytes(value)` | UTF-8, sorted keys, two-space indentation and one final newline. No ASCII escaping, NaN/Infinity or silent non-string-key coercion. This is a reproducible project encoding, not a signature standard. |
| `write_json_new(path, value)` | Writes complete canonical bytes to a fresh same-directory temporary file, flushes/fsyncs it, creates the new target through a non-replacing hard link, and removes the temporary name. Returns the exact digest/byte count. |

Invalid inputs and normal filesystem/serialization failures raise
`DataError(ValueError)`. All defaults and limits above are engineering bounds,
not instrument measurements. Callers may tighten them. `max_bytes` is 1..16 MiB,
`max_nodes` 1..1,048,576, container nesting 0..128 (root container depth 0),
and `max_number` positive finite and at most 1e100. Numeric JSON tokens have at
most 64 characters. Canonical output uses the largest node/depth/number bounds.
JSON scalar leaf depth does not count as another container level.

## Filesystem and failure behavior

Input leaf symlinks/reparse points, directories and special files are rejected.
Ancestors may contain ordinary OS aliases; the capture/corpus root caller owns
artifact-relative confinement. POSIX input opens use `O_NOFOLLOW` when available;
all platforms check the observed path and descriptor independently before/after.
The archive must remain quiescent. This is not a claim of a portable adversarial
concurrent-filesystem sandbox, or a detector of changes deliberately restored
between observations.

Output parents must already exist, and the filesystem must support hard links.
An existing file, directory or dangling symlink at the target is preserved and
causes rejection; no replacement mode exists. Serialization and the complete
temporary write precede target creation. Ordinary failures before publication
remove the owned temporary file. This does not promise crash recovery, directory
fsync, permission preservation from another file, or multi-file transactions.
No source audio or existing manifest is modified.

If cleanup itself is denied, `DataError` retains both the primary publication
failure and the cleanup failure. If linking already published the complete new
file, that file remains complete and the error explicitly says it was published;
the caller must inspect that outcome before retrying. Descriptor ownership is
released even if construction of the Python stream wrapper fails.

The root integrator authored these common primitives. Independent acceptance is
assigned separately before the production corpus/comparison tools depend on them.
