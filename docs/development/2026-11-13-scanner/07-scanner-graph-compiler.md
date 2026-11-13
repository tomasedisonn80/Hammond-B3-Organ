# Assignment 07 - strict scanner graph admission and compiler

## Identity and owned changes

Actual worker: `/root/w02_a07_scanner_graph_compiler`, assignment 07 of 60,
wave 2 of the `2026-11-13-scanner` session. Starting commit:
`6dc0702d5473912268e8af8f852b9b9984198ef3`; its tree is
`a4f1d4b300de236436e22b748b1d4c46ed501ceb`.

Owned additions:

- `data/scanner/atlas-late-b3-nominal-v1.json`
- `data/scanner-line.schema.json`
- `tools/compile_scanner_line.py`
- `docs/SCANNER_GRAPH.md`
- This evidence note.

The integrator owns CMake and shared status/ledger files. Other workers' changes
were present and left untouched. No Git mutation or additional agent dispatch
was performed by this assignment.

## Source basis and implemented behavior

Read the standing agent contract, current scanner handoff/plan context,
`M3_REMAINING_AND_SCANNER_GATE.md`, and the fresh source readings in assignments
02/03. This compiler implementation uses the atlas graph on pp. 157-158,
175 and 182, independently transcribed in those readings. It does not claim a
new full-PDF reading or a separately performed primary-paper comparison.

The new fixture admits exactly 27 nodes, 18 inductors, 18 capacitors,
14 resistors and 19 signed ground-referenced outputs. Every early divider is
attached before its inductor. Ideal source and return switch are explicit
boundaries; vibrato contracts return to ground and chorus opens that switch.
The same source values and ASCII unit transcriptions are retained with page
locators and an explicit absent-uncertainty marker.

Three named ideal approximations remain separate from eight physical unknowns.
Unknown winding/coupling/stray/source/receiver/voltage-scale/revision quantities
retain null values and concrete acquisition descriptions. The authoring record
is `documentary-reconstruction`, never specimen-measured.

The compiler is standard-library-only Python. It rejects duplicate JSON keys,
unknown fields, wrong identities/endpoints/values/units/source locators,
nonpositive/nonfinite quantities, wrong node/component/output counts, malformed
return states, and invented values for physical unknowns. Input bytes, recursive
values, depth, strings and collections are bounded. Metadata booleans and floats
cannot stand in for integers. A nonblocking regular-file read checks for changes
during reading. `load_profile_with_digest` supplies a validated dictionary and
the hash of that same byte snapshot to independent consumers.

Normalization copies the authoring record and converts declared decimal units
once into SI values, retaining the printed evidence. Graph lists have canonical
order. Output contains no timestamps or machine paths. The generated C++20 header
uses the requested `hammond::scanner_generated` constants; no runtime code or
organ control identity is introduced here.

Publication constructs the whole output before writing a temporary file beside
the destination, then flushes and atomically replaces it. Input aliases,
nonregular destinations and output symlinks are rejected. Failed admission or
publication preserves existing output and cleans the temporary file. The CLI
returns 0 silently on success or reports rejection to stderr with exit 2.

## Actual checks and observed outcomes

Working directory was `/workspace/scratch/1742da7072be/Hammond-B3-Organ`.
Checks used Python 3.12.14 and the available GCC 14.2.0 C++20 compiler.

| Executed check | Result and scope |
| --- | --- |
| Inline producer harness: valid fixture, identity-returning validation, input nonmutation, SI conversion and repeated compilation | Passed; 0.5 H, 4e-9 F and final 1e-9 F checked explicitly |
| 25 malformed in-memory profiles and matching CLI inputs | All rejected, CLI exit 2; every rejected CLI invocation preserved an existing sentinel destination |
| Duplicate JSON key and over-256-KiB input | Rejected; previous output preserved for the duplicate-key CLI probe |
| Draft 2020-12 schema validation | Valid fixture accepted; 23 applicable malformed variants rejected. Integral-float lexical probes are compiler-specific because JSON Schema treats equivalent integral values numerically |
| Final simplified exact-record schema | Revalidated fixture and schema; reversed node/component/output/assumption/unknown arrays accepted and normalized identically; six endpoint/count/value/duplicate/extra-field/output-polarity mutations rejected |
| Generated C++ header | Compiled and executed a temporary program with `-std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Werror`; static assertions verified inductance and final capacitor |
| Source alias, hardlink and symlink destination checks | Rejected without changing source bytes or destination links |
| FIFO input | Rejected without waiting; observed duration below one second on this Linux executor |
| Injected `os.replace` publication failure | Previous destination retained and temporary file removed |
| `python3 -m py_compile tools/compile_scanner_line.py` and `git diff --check` | Passed |

The first hardlink test setup attempted to link a repository file into `/tmp`
and failed with `EXDEV` because the paths are on different filesystems. That
attempt did not exercise hardlink admission. Repeating the fixture in a temporary
directory beside the source succeeded and verified rejection; the temporary
directory was removed. This is a retained setup failure, not a production failure.

The final explicit CLI commands were:

```sh
python3 tools/compile_scanner_line.py \
  --input data/scanner/atlas-late-b3-nominal-v1.json \
  --output /workspace/scratch/1742da7072be/a07-scanner-line.json --format json
python3 tools/compile_scanner_line.py \
  --input data/scanner/atlas-late-b3-nominal-v1.json \
  --output /workspace/scratch/1742da7072be/a07-ScannerLineData.h --format header
sha256sum data/scanner/atlas-late-b3-nominal-v1.json \
  data/scanner-line.schema.json tools/compile_scanner_line.py \
  /workspace/scratch/1742da7072be/a07-scanner-line.json \
  /workspace/scratch/1742da7072be/a07-ScannerLineData.h
git diff --check
```

Final identities observed by this assignment:

| Input/output | SHA-256 |
| --- | --- |
| Authoring fixture, 26,228 bytes | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |
| Schema, 43,730 bytes | `577201810fc087ec86ff731c213ada48405faf6f71f07180b2539588cbbd7dbf` |
| Compiler, 18,928 bytes | `56c60cf511144d552fdeb2708711b32469f350593b391c7619ebb92b41b6dd7e` |
| Generated SI JSON | `b027d323f840264faeae0a831e046d2518771fb58aa9b99a6d9388b1ef91ee7b` |
| Generated C++ header | `d508e3856e637a8e107364ad2a8fed09893a2e50ae05d99db3d4b3da37a5a082` |

## Handoff and limits

These are producer checks, not independent literal endpoint acceptance. The
fixture/API were handed to assignment 08 for an independently stamped oracle;
its numerical results belong to that worker's evidence. Independent source and
malformed-graph test assignments remain separately accountable. The integrator
must wire and verify the generated header in the actual build.

No scanner time-domain/runtime, host, audio-device or measured-hardware result
is established here. Next steps are independent graph/source acceptance and
frequency/transient reference qualification before accepting a native prepared
line. The original atlas, source profile, routing tables, 45 parameters and saved
controls were not changed.
