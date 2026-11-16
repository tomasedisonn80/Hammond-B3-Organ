# Registration first-use admission

16 November 2026; A43, independent wave-eight operator review. **Conditionally
admitted on Linux with separate ASCII `inputs` and `outputs` branches beneath
the shared Unicode working directory.** Distinct Unicode-named sibling
directories can still be refused. The original failed journey remains evidence;
the successful repeat does not turn it into a pass.

## User-facing limitation and disposition

**A43-F1:** from `../a43-first-use/First session Ω`, import into
`Ma bibliothèque Ω` succeeded. Materializing either scope into sibling
`Auditions été` returned exit **3**, `ProtectedPath`, `committed: false`, with
“Cannot establish distinctness from a protected application path.” No destination
directory or output was created. Subsequent output inspections correctly returned
`NotFound`; the intended materialization collision check could not be reached.

This exposes the existing conservative policy described by the
[path admission](REGISTRATION_PATH_ADMISSION.md): an unequal pair of wholly
ASCII path components can establish lexical distinction, while differing Unicode
components can remain uncertain. No production code changed for either first-use
journey. Root corrected the [guide](../REGISTRATION_GUIDE.md#7-install-explicitly-and-relocate)
after receiving the finding; its reviewed bytes state the limitation and put both
the source library and current file beneath `inputs/`.

The original observer also raised `FileNotFoundError` when it attempted a byte
comparison after the refused materialization. This separate observer defect is
recorded; all fourteen native command records and original stdout/stderr had
already been saved. Finalization independently confirmed that inputs were
unchanged and the intended outputs absent.

## Supported journey

Root authorized one repeat, using the same unrelated working directory and
unchanged executable. Both source library and current input sit under `inputs/`:

| Role | Path relative to the working directory |
| --- | --- |
| Fresh imported library | `inputs/Ma bibliothèque Ω` |
| Literal current snapshot | `inputs/Current état.b3controls` |
| New materialized library | `outputs/Auditions été` |

Every native subprocess used that working directory and absolute quoted-equivalent
argument paths. The process records retain the complete argv and shell spellings.

| Calls | Observed result |
| --- | --- |
| 1 | Help returned its JSON usage. |
| 2–4 | Listed all 24 supplied entries and inspected both Warm Comp scopes. |
| 5 | Listing the absent private library returned `MissingDirectory` without creating it. |
| 6–8 | Explicitly imported Registration and Performance; listed exactly two files. |
| 9–10 | Materialized Registration with `--current` and Performance without it. |
| 11–12 | Inspected both resulting `.b3performance` files. |
| 13–14 | Repeated import and materialization each returned exit 3, `NameExists`, `committed: false`. |

The repeat passes **100 observer conditions over 14 native processes**. There
were 28 native processes across both journeys, not 28 successful operations or
100 independent test methods. No additional permutations were run.

## Independent state and inventory checks

The current snapshot was authored as literal version-4 bytes, with expression
`0.375` and deliberately contrasting banks, selectors, cancelled routes, retained
fixed modes, pedals and percussion. Expected Warm Comp fields were transcribed
from the independent recipe manifest and documented grammar. No production parser
or generator supplied the oracle.

Both imported files exactly equal the complete literal Warm Comp payload at
`0.625`. Each materialized file is exactly 459 canonical bytes, including final
newline:

| Output filename | Expression | Every other saved field |
| --- | --- | --- |
| `Warm Current.b3performance` | `0.375` | Literal Warm Comp values |
| `Warm Saved.b3performance` | `0.625` | Literal Warm Comp values |

Whole-file comparisons cover all 36 drawbar positions, both remembered selectors,
route bits and fixed modes, both pedal positions, four percussion settings and
the catalog identity. The inspect JSON canonical text independently matches those
same literals. Four save-path reports decode to the exact native Unicode path
bytes.

The complete 26-file supplied pack, current snapshots and imported libraries
retain their recorded bytes, filenames, modes and mtimes. Inspection and refused
repeats leave committed outputs unchanged. Final inventory is exactly the three
preserved original-layout files plus five supported-layout files; no sidecars or
staging leftovers appear.

## Evidence and boundary

The [compact receipt](../development/2026-11-16-preset-library-continuation/reports/a43-first-use.json)
identifies commands, outcomes, exact inventories and the
[original evidence archive](../development/2026-11-16-preset-library-continuation/reports/a43-first-use-originals.tar.gz).
The archive retains both observers, literal fixtures, actual files, command
records, raw native stdout/stderr, failure metadata and detailed hash receipts.

Both journeys observed HEAD `20739f6280b95e567e84615d5c5aee443fc3b93d` and executable
SHA-256 `872a343f20eb6710e6867fc4d1c0fe0b95118b883de21035ee70774f8762e13f`.
Eleven relevant CLI/core/storage source files matched HEAD and remained unchanged.
This used the existing Linux x86_64 Ninja Release build; it neither rebuilt nor
qualifies concurrent unrelated working-tree changes, publication or hosted CI.

No installer, renderer, generator, CTest suite, native browser or physical device
was invoked. Windows/macOS, live-library acceptance, physical fidelity and
literal whole-interface 1:1 remain open. **Next action:** publish the guide's
precise layout limitation with these receipts; platform owners can subsequently
qualify that bounded workflow at their exact executable sources.

## Separate Windows proposal review

At root's later request, A43 independently admitted the bounded
[ambiguity-guard proposal](../development/2026-11-16-preset-library-continuation/reports/a43-windows-path-proposal.json)
before implementation: check raw requested components in both `identify_path`
and `resolve_root` before normalization, retain both resolved checks and existing
failure statuses, and exempt only exact `.`/`..` navigation. The receipt specifies
raw-path positive cases and refusal/no-authorization/no-creation checks. This
read-only source assessment neither executes Windows nor changes the Unicode
sibling admission above. Later repaired binaries require their own qualification.
