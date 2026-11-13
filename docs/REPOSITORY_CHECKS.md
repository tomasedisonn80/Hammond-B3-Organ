# Source-archive integrity checks

[check_repository.py](../tools/check_repository.py) checks retained source
relationships with Python 3.10+ and its standard library. It works in a source
archive with no `.git` directory, compiler, generated profile, renderer, network
access, factory manual, or measurement corpus. It opens files for reading only.

```sh
python3 tools/check_repository.py
python3 tools/check_repository.py --json
python3 tools/check_repository.py --root /path/to/source-archive --json
```

The default permits incomplete agent-session progress. To close a session with
an explicitly chosen assignment count, require the exact ID set `1..N`:

```sh
python3 tools/check_repository.py --expected-agents 60 --json
```

That explicit invocation requires all 60 notes. Ordinary checks and the CTest
suite do not require future assignments to exist. The same option accepts other
positive counts through 10,000; it is not tied to a particular commit or test
total. Missing and unexpected IDs are reported separately.

Exit status is **0** on success, **1** for an integrity/read/bound failure, and
**2** for invalid command-line usage. JSON mode prints one object with `status`,
per-check results, located `errors`, and a separate `physical_fidelity` field.
Readable mode prints the same check outcomes and explanations. The importable
`check_repository(root, expected_agents=None)` function returns the report.

## Checked contracts

| Check | Retained relationship and failure conditions |
| --- | --- |
| Source identity | Stream the file named by the [source manifest](research/source-manifest.json); compare its exact length and SHA-256, and require the atlas's declared 500-page identity. Missing files, malformed metadata and mismatches fail. |
| Reconstructed chapter index | Reconcile [chapter-index.json](research/chapter-index.json) with the manifest; require front matter 1–12, 80 ordered six-page chapters 13–492, and source directory 493–500. Validate chapter IDs, contents-page locators, ten research-wave spans, contiguous disjoint review coverage of 1–500, and existing review notes that cover each chapter. Preserve the index's explicit reconstruction status. |
| Markdown links | Check actual local inline links, images, and used full/collapsed/shortcut reference links. Resolve relative destinations from the Markdown file, and leading-slash destinations from the repository root. Report the referring file, line and target on failure. |
| Agent notes | Require direct Markdown notes in [agent-notes](development/agent-notes/) to have canonical positive IDs in filenames such as `01-task-name.md`; reject duplicate IDs, zero, missing padding and malformed names. Gaps are permitted unless `--expected-agents` is given. Filenames are assignment identities, not evidence that their contents are true. |
| Existing data references | Reconcile atlas path/hash/edition in the [nominal profile](../data/profiles/nominal-unmeasured-v1.json), [pedal map](../data/pedal-map.json), and [profile schema](../data/profile.schema.json) with the manifest. Resolve the [fixture catalog](../examples/fixtures/catalog-v1.json)'s root-relative authoring path, check its canonical JSON hash/profile ID, and check each catalog-relative event filename and raw-byte hash. |

Canonical authoring JSON uses sorted keys, compact comma/colon separators,
UTF-8, `ensure_ascii=False`, `allow_nan=False`, and no final newline, as specified
in [PROFILE_FORMAT.md](PROFILE_FORMAT.md). Harmless source whitespace changes
therefore do not change that digest. Fixture event hashes bind exact source
bytes, including line endings. Source references in the chapter index are
checked independently of the three data documents above.

The tool interprets only those named data contracts. A parameter registry's
logical `path`, a prose mention of an absent companion, or a historical external
source locator is not treated as a local file requirement. The catalog's
`compiled_sha256` is reported as `not_checked_generated_build_artifact`: the
compiler and catalog tests own the generated profile contract, and this check
does not inspect build directories or compile/run repository code.

## Markdown scope and bounds

The scan includes root-level Markdown and Markdown under `.github`, `data`,
`docs`, `examples`, `include`, `src`, `tests`, and `tools`. It does not recursively
search arbitrary root directories. Within those source scopes it prunes build
directories named `build`, `build-*`, `build_*`, `cmake-build-*`, and common
output/dependency directories, and prunes directories containing `CMakeCache.txt`
or `CMakeFiles`. Directory symlinks are not traversed. File targets must resolve
inside the selected source root; regular files and directory links are accepted.

Fenced examples (backticks or tildes, including block quotes), inline code and
HTML comments do not contribute links. External URI schemes and protocol-relative
URLs are skipped. URL escapes and HTML entities are decoded; query strings and
fragments are omitted when checking a file. Anchor-only links need no file check.
Balanced/escaped destination parentheses, angle destinations and optional titles
are supported. Unused and undefined reference labels are not rendered links.
This is a focused Markdown reader, not a complete CommonMark/HTML renderer:
HTML `href`/`src`, heading anchors, external URL availability and renderer-specific
extensions are outside scope. Plain prose and inline-code paths are not links.

Reads are bounded: the atlas is at most 64 MiB and is streamed in 64 KiB chunks;
each Markdown/schema document is at most 1 MiB; all reads together are at most
128 MiB. The manifest is at most 64 KiB, index/profile 256 KiB each, catalog
128 KiB, pedal map 64 KiB and each event score 16 KiB. The source inventory is
bounded to 10,000 visited entries and 24 directory levels. JSON rejects duplicate
keys and nonfinite values, limits numeric tokens to 128 characters, and caps
the parsed tree at 100,000 values and 48 levels. Markdown has limits of 20,000
links per file, 128 bracket levels and 32 destination-parenthesis levels.
The report retains at most 100 error messages and reports truncation explicitly.
A bound failure is a failed check, never a silent success or skipped assertion.

The five check groups run independently so an ordinary failure still permits
other groups to report. Most groups stop at their first failing assertion;
Markdown target errors are collected across links. Files should be quiescent
during a run: this is not an atomic snapshot or an adversarial filesystem-race
verifier. Re-run after concurrent source edits settle.

## Verification and evidence limits

[test_repository_integrity.py](../tests/test_repository_integrity.py) is discovered
by the existing CMake `test_*.py` registration. It needs no built renderer:

```sh
python3 -B tests/test_repository_integrity.py -v
ctest --test-dir build -R '^python_test_repository_integrity$' \
  --output-on-failure --no-tests=error
```

The suite has a real repository/PDF smoke and isolated archive mutations for
source bytes/length, index coverage and locators, local links and code examples,
note IDs, declared data paths/hashes, resource bounds and CLI failures. Small
cases use tiny synthetic source bytes and metadata; they neither copy nor
hard-link the supplied PDF. A CLI test removes Git from `PATH` and compares the
archive's before/after file contents and inventory to check read-only operation.

Matching hashes establish agreement with the supplied manifest, whose authenticity
is not independently established. Index checks validate the retained 500-page
navigation contract; they do not parse the PDF page tree, compare all titles to
its rendered pages, or reperform the reviewers' reading. A matching source and
valid links do not establish specimen identity, physical fidelity, source rights,
build provenance, audio correctness, platform qualification or session completion.
Those retain their separate [project evidence gates](PLAN.md).
