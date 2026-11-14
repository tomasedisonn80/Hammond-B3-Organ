# Preserve raw float32 bytes in Git

Root found and repaired a concrete raw-byte preservation gap while integrating
the capture tools. The repository forces text files to LF, but initially relied
on automatic binary detection for the newly supported `.f32` artifacts. A valid
float32 stream can consist entirely of printable bytes and line endings, so
automatic detection does not guarantee its preservation.

The four literal bytes `41 0d 0a 3f` are one finite little-endian float32 sample,
exactly `0.5392647385597229`, within the audio inspector's supported amplitude
bound. Their SHA-256 is
`b6ef8d51b79b02f5bbd9091f2b23a1ae8be45bbc8021e557b61730d14dabb3a9`.
No fixture or real acquisition file was written into the repository for this
probe. The bytes were supplied directly to Git without object storage:

```python
import subprocess

payload = bytes.fromhex("410d0a3f")
raw = subprocess.check_output(
    ["git", "hash-object", "--no-filters", "--stdin"], input=payload)
filtered = subprocess.check_output(
    ["git", "hash-object", "--stdin",
     "--path=examples/capture-demo/corpus/audio/git-byte-probe.f32"], input=payload)
```

Before the repair, `git check-attr --all` reported `text: auto` and `eol: lf`.
The raw Git blob identity was `12235b56bbf4ac33203be36891af64da460aaf8c`, while
the path-filtered identity was `b913eb88f077f3eb3c6d0e829ed805d180889535`.
The Git clean filter therefore changed actual supported input bytes.

`.gitattributes` now explicitly marks `*.f32 binary`, beside the existing PDF,
WAV and compiled-profile binary rules. The same actual probe returns
`12235b56bbf4ac33203be36891af64da460aaf8c` through both paths. Its attributes
are `binary: set`, `diff: unset`, `merge: unset`, `text: unset`; the inherited
`eol: lf` cannot enable translation when text processing is disabled.

This is a file-classification fix. The three retained demo streams already
contained binary-identifying bytes and were not found corrupted. Their content,
hashes, expected outcomes and all production numerical code remain unchanged.
The probe establishes the specific before/after Git behavior, not preservation
under arbitrary external editors or transformations. Future raw formats still
need appropriate binary classification and original-byte identity checks.

The exact probe observations are retained in scratch
`checks/f32-git-before.json` and `checks/f32-git-after.json` under
`/workspace/scratch/c9f3ead4c910`; this record retains the substantive data and
reproduction without requiring those temporary files. Include the rule and
this finding in the next coherent publication and compatibility review.
