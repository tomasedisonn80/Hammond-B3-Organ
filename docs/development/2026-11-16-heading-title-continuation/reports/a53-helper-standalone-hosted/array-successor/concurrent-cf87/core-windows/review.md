# Original Windows Core failure and incoming path fixes

## Original outcome remains failed

For exact source `cf87a587d0002d106e5210b57a39fd1967245a8f`, Core run [44030833273](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44030833273), attempt 1, Windows job **133862108675** successfully built Release and executed all **209 CTests**. **207 passed and two failed**, in 219.81 seconds; CTest exited 8. Neither failed result was a timeout.

The [original observation](original-observation.json) retains every result row, runner 1000001432, compiler MSVC 19.44.35230.0, actual source checkout and all step outcomes. The job used a 20-minute allowance and invoked CTest with `--parallel 2 --timeout 300 --no-tests=error`. Its non-verbose log does not print each computed timeout property. The exact top-level CMake registration assigns no named timeout override to either failed Python gate. No timeout or workload change is proposed.

| Failed CTest | CTest seconds | Actual Python result |
| --- | ---: | --- |
| `python_test_capture_standalone_interface` | 4.51 | 45 methods, three errors in one method's scale/timeout subtests |
| `python_test_compare_header_material` | 0.89 | 24 methods, seven errors across five methods/subtest groups |

The original capture subtests are scale/timeout pairs **1/12 s, 3/30 s and 10/12 s**. All three stop at test line 366 with `KeyError: 'inputs/play-dimensional.b3uireplay'`. They do not reach the following exact-hash comparison. The header suite errors are `FileNotFoundError [WinError 3]` for retained historical Unix input/object paths after its identity mock falls through to the real filesystem.

Subsequent standard-library apron, actual Windows Unicode starter-generator, completed interface/refinement session and actual product-session verification steps were skipped. Their status remains unreached. The separate standalone P1 compiler failure is independently frozen in the parent directory and is not substituted for this Core failure.

## Source-proven diagnosis and incoming correction

The unchanged capture producer deliberately inventories keys using `str(path.relative_to(root))` and writes replay files using `Path.write_text(script, encoding="ascii")`. The failing unit test instead assumes a literal POSIX key. Incoming source **d2ed03b94114e35d0caa65968d11afe896a5e9f5**, tree `45f3f2bc1bc844061be7d1303b13b10bfaba9938`, already repairs that expectation with native `Path` construction.

It also derives the expected exact on-disk bytes as `script.replace("\\n", os.linesep).encode("ascii")`, preserving the existing single SHA-256 equality. This addresses default text-write newline translation without normalizing actual evidence, accepting multiple hashes or changing production serialization. The latent newline mismatch is inferred from exact source; the original Windows KeyError prevented observing a subsequent hash failure.

The header mock stores raw POSIX receipt strings as dictionary keys, but its existing identity wrapper first constructs a native `Path`. Incoming d2ed normalizes only insertion keys with `str(Path(row["path"]))`. The copied identity record retains its original path, byte count and hash unchanged. Unknown paths still use the real identity implementation. Production baseline admission, protected source pins, exact fixture reversals and semantic refusals remain strict.

The [incoming-source review](incoming-d2ed-review.json) verifies the complete two-file differences and A56's preserved original evidence. A53's independently fetched decoded Windows log is byte-identical to A56's retained log. A56's source suites passed 45 capture and 24 header methods **on Linux**, with mocked native/image boundaries; those runs do not establish Windows acceptance.

## Composition with the current header additions

The incoming header normalization has now been independently checked against root's combined file. [The conformance receipt](integrated-core-test-conformance.json) verifies that reversing only that insertion-key line restores A52's exact prior file SHA `4832837c0465e875ac7873ada1d7b005f7da8c727fa7467621f85aa6d7adb8f8`. All **32 current header test method ASTs**, top-level constants and indexed-array additions are unchanged.

The integrated header test is `2f376e5505975e3ecc60ea16949e2562e2c90c74b2a359d8ca3bb0abab520b72`. The current capture test exactly equals incoming d2ed, `2ee08931dbef930c91d6b1f591592c65dec359c3de089c6bcf3841b686ab9ccc`. The capture producer remains `ad0b813a378f259e471a9b2901902cc4f75f0ba7feb021e6c3c1c929bdb5b487`; A52's admitted header comparator remains `9cbaea0e495a0ad07276095dd81f0fcd126fee2aef1f5e9607de4740eb600328`.

Pure standard-library inspection of all **14 genuine retained input/object records** shows 14 original Windows mock-key misses and zero after normalization. POSIX lookups remain unchanged; every stored identity value remains exact, and substituted hashes still compare unequal. This used AST/source and PurePath operations only, with no project module imported or project test/native process executed.

## Evidence and next gate

[The retention receipt](failure-retention.json) binds the complete original 606,646-byte log, compressed losslessly to 61,091 bytes, and all original CRLF capture/header/final-summary failure blocks. Readable LF views are separately hashed and verified as newline-only transformations. Original decoded SHA-256 is `c47eee99796358d5a7f0cba50883c62d63df69994e701b96d5758f68d1de3d95`.

**Preserve the incoming repairs; no duplicate repair is needed.** Actual Windows execution of the combined source, including all three Python gates and the affected native tests, remains the next qualification gate. Original cf87 failures and all earlier reviews remain unchanged. A53 made no live source edit, project execution, CI retry or remote mutation.
