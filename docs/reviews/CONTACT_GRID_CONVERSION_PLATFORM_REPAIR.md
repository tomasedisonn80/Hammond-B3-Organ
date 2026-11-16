# Contact-grid conversion test portability repair

**Owner:** A33, wave 6, `/root/w06_a33`. **Date:** 2026-11-16.
**Disposition:** two test premises repaired; production behavior and the published
conversion contract are unchanged. Local qualification passes. Repaired native
macOS and Windows qualification remains a separate root-owned publication gate.

## Published failure evidence

The original published source was
`3520c96adcdcf4ce4bcb860082354bf0050a89c3`, tree
`1013bbd914a0957ca2c164ef02ca5410a8dcde6b`.
The [completed job receipt](../development/2026-11-16-conversion-material/reports/wave04-hosted-complete.json)
records 11/13 successful jobs. Both failures occurred in the core Release matrix;
all five standalone and three VST3 jobs passed for that original source.

| Job in run `43801643469` | Original result | Observed failure |
| --- | --- | --- |
| macOS AppleClang, `133083059424` | 188/190 registered tests passed | Arbitrary-byte fixture creation raises `EILSEQ` before invoking the CLI; sequencing callback compares resolved `/private/var/...` with lexical `/var/...`. |
| Windows MSVC, `133083060473` | 189/190 registered tests passed | The same sequencing callback compares resolved `C:/Users/runneradmin/...` with lexical `C:/Users/RUNNER~1/...`. |

The [macOS log](../development/2026-11-16-conversion-material/reports/hosted-3520c96-macos-core.log)
retains the actual `OSError: [Errno 92] Illegal byte sequence` at
`source.write_bytes(data)`. The [Windows raw log](../development/2026-11-16-conversion-material/reports/hosted-3520c96-windows-core.raw.log)
retains its original CRLF bytes; the separate plain `.log` is a normalized reading
copy. Their byte counts, hashes and newline distinction are recorded in the
[log identities](../development/2026-11-16-conversion-material/reports/wave04-hosted-log-identities.json).
The converter's operational-refusal diagnostic in the sequencing cases contains
the test callback's `AssertionError`, not an independently observed filesystem
publication failure.

Exact original test files were saved before editing as
[CLI snapshot](../development/2026-11-16-conversion-material/reports/A33-before-test_contact_grid_conversion_cli.txt)
and [adversarial snapshot](../development/2026-11-16-conversion-material/reports/A33-before-test_contact_grid_conversion_adversarial.txt).
The [before bindings](../development/2026-11-16-conversion-material/reports/A33-before-bindings.json)
bind those bytes, production modules, contract and corpus manifest to the original
source. Original failures remain evidence; they are not replaced by later passes.

## Why the production path handling is correct

Section 5 of the [conversion contract](../CONTACT_GRID_CONVERSION_CONTRACT.md)
allows a resolved input and output parent reached through a symlink. Output leaf
symlinks, input/output aliases, missing parents and nonregular endpoints remain
refusals. In [path preflight](../../tools/contact_switching_io.py), the input and
parent are resolved with `strict=True`; `OutputPlan.output_path` is constructed
under that resolved parent and its identity is retained for rechecks.

The [CLI publisher](../../tools/convert_contact_grid.py) passes that admitted
parent to `tempfile.mkstemp` only after encoding the complete certificate and
rechecking provenance. Comparing the argument to the caller's lexical spelling
therefore contradicted admission. Changing production to keep that spelling would
be an unjustified contract change. No production change is included here.

POSIX membership alone also does not establish that the actual filesystem accepts
every byte sequence as a filename. The macOS exception occurred while building a
test fixture, so it supplied no failed converter execution for that case.

## Scoped test changes

In [the CLI suite](../../tests/test_contact_grid_conversion_cli.py), the existing
sequencing test now compares the actual `mkstemp(dir=...)` argument with
`self.destination.parent.resolve(strict=True)`. The actual argument is not itself
normalized by the assertion: an incorrectly noncanonical argument still fails.
All existing encode-before-temporary events, success checks, certificate checks
and cleanup checks remain. The old public test method name remains registered.

The same assertion helper also runs through a real directory symlink. That case
requires the alias spelling to differ from its resolved spelling, then checks
the complete sequence and successful publication. It uses the suite's existing
symlink capability helper; it adds no OS-wide exclusion. This Linux alias is a
real path-identity regression, not a claim of native Windows 8.3 execution.

In [the adversarial suite](../../tests/test_contact_grid_conversion_adversarial.py),
the existing POSIX byte-name case first tries to create both exact fixture names.
Only an actual `OSError` with `errno.EILSEQ` at this preparation boundary causes a
capability skip. Other errors propagate. The destination probe is removed before
the CLI runs, preserving the original absent-output case. Converter invocation
and assertions are outside that exception handler. There is no macOS-wide skip.

An additional Unicode-path test runs without a platform or capability skip. It
uses Japanese and Greek names in a nested directory and launches the real CLI
three times: successful replacement of prior output through Unicode paths,
successful creation through ASCII paths from identical input bytes, and an
`event_order` refusal through Unicode paths. It checks silent success, identical
certificate bytes across path spellings, exact input hash and byte count,
unchanged input, preserved prior output on refusal, and no owned temporary files
in the actual output parents. This remains useful coverage on filesystems that
cannot represent the arbitrary-byte fixture.

## Qualification and retained limits

The [original reproduction script](../development/2026-11-16-conversion-material/reports/A33-reproduce-original.py)
loads the retained original test bytes. A real local alias reproduces the old
sequencing failure; an injected `EILSEQ` at fixture creation reproduces the old
pre-invocation error. Its [receipt](../development/2026-11-16-conversion-material/reports/A33-original-reproduction.json)
and [raw unittest output](../development/2026-11-16-conversion-material/reports/A33-original-reproduction.log)
record one expected assertion failure and one expected fixture error. The
injection is explicitly not a native macOS replay.

| Local qualification | Observed result |
| --- | --- |
| `python3 -B tests/test_contact_grid_conversion_cli.py -v` | 34/34 pass, zero skips, 0.261 s unittest time. |
| `python3 -B tests/test_contact_grid_conversion_adversarial.py -v` | 12/12 pass, zero skips, 0.871 s unittest time. |
| Capability boundary probe, each of input and output leaf | 10/10 expected outcomes: two `EILSEQ` skips; eight `EACCES`, `ENOSPC`, `EIO` or `EINVAL` errors retained; zero CLI invocations. |

The [CLI output](../development/2026-11-16-conversion-material/reports/A33-cli-initial-local.log),
[adversarial output](../development/2026-11-16-conversion-material/reports/A33-adversarial-initial-local.log)
and [capability policy receipt](../development/2026-11-16-conversion-material/reports/A33-capability-policy.json)
are separate evidence. The latter is generated by the retained
[injection script](../development/2026-11-16-conversion-material/reports/A33-capability-policy.py).
The [qualification receipt](../development/2026-11-16-conversion-material/reports/A33-platform-qualification.json)
binds the changed sources, exact original snapshots, logs, methods and unchanged
production/contract/corpus bytes. All local execution used Python 3.12.14 on
Linux `6.18.57-x86_64-with-glibc2.41`.

| Repaired source | SHA-256 |
| --- | --- |
| CLI tests | `03b3311910ec016dd5254a22f59e88afab070e7885337894b46c303e4a5dad12` |
| Adversarial tests | `1030e5439a34d29e680e3dfa08b752dad036dcda53d1c92477dfc549cd94a1e1` |

Reproduction from the repository root:

```sh
python3 -B tests/test_contact_grid_conversion_cli.py -v
python3 -B tests/test_contact_grid_conversion_adversarial.py -v
python3 -B docs/development/2026-11-16-conversion-material/reports/A33-capability-policy.py --report /tmp/a33-fresh-capability-policy.json
python3 -B docs/development/2026-11-16-conversion-material/reports/A33-reproduce-original.py --report /tmp/a33-fresh-original.json --log /tmp/a33-fresh-original.log
```

The scripts require fresh result paths. The original reproduction intentionally
expects the retained failures and verifies the watched production bindings.
These local receipts do not establish repaired macOS/Windows passes. Root must
publish the bound test sources with the rest of the reviewed wave, preserve the
new commit/tree identities, and observe that exact source's native core jobs.
Any later failure must be investigated from its own source-bound log. No shared
build, workflow, CMake, DSP, production module, commit or push was made by A33.
