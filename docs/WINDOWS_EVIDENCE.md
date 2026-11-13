# Windows render-evidence portability

## Observed failure and scope

The first hosted [CI run 43361632464](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43361632464)
at `b9c1cac` used Windows Server 2022, MSVC 19.44.35229.0 and CPython 3.12.10.
Compilation succeeded; 10 of 12 CTest suites passed. The two failed suites were
`python_test_fixture_catalog` and `python_test_render_fixture`. The Linux repair
checks below do not establish a subsequent native Windows pass. The integrator
must retain the next hosted run and resolve any remaining failures before closing
that platform gate.

## Findings and repair

### Checkout bytes

All five catalog score hashes in the Windows failure log exactly match the
SHA-256 obtained by replacing the original files' LF endings with CRLF. For
example, `two-manual-changes-v1.events` has the catalog identity
`d86b7fb3e3a62865b218400828aaef7ee176c39da7f08ef29aed5ae5b0627ae8`;
the CRLF version is
`79d771e4f0942ce1e079ae6b6b3885be5e5ce8450a4061ed87829c7e8c4b5b1e`,
exactly the observed failure. This was reproduced for every catalog entry.

`.gitattributes` now sets `text=auto eol=lf` and marks `*.pdf`, `*.wav` and
`*.b3p` as binary. Git documents that `eol=lf` keeps working-tree text line
endings equal to the index, overriding the platform/default checkout conversion;
unsetting `text` prevents conversion of binary paths. See the official
[Git attributes contract](https://git-scm.com/docs/gitattributes#_text).
Catalog digests remain unchanged. Supplied profile/score bytes and captured logs
remain exact bytes; runtime hashing never normalizes CRLF.

### Path and descriptor metadata

The old producer compared `(device, inode, size, mtime_ns, ctime_ns)` from
`Path.stat()` directly with `os.fstat()` and rejected the unchanged renderer at
the preflight read. Its WAV inspector used the same cross-API assumption.

That equality is not a portable change detector. The official
[Python 3.12 stat documentation](https://docs.python.org/3.12/library/os.html#os.stat_result)
deprecates Windows `st_ctime`/`st_ctime_ns` and describes the creation-time
compatibility behavior. CPython [change a01fb672](https://github.com/python/cpython/commit/a01fb672d23b1bec5c98685c18ed8eb47529faff)
shows the shared Windows conversion taking `ChangeTime` while `win32_xstat`
restores birth time for the path API. The upstream
[CPython issue 157671](https://github.com/python/cpython/issues/157671) demonstrates
an unchanged file whose path/descriptor `st_ctime_ns` differ. The initial project
log did not print the individual metadata fields, so it does not independently
identify which fields differed on that particular executable.

Both producer readers now require a regular nonsymlink path, a regular opened
file and matching sizes. They compare full stamps within each API before/after
reading, including mode and timestamps; POSIX additionally binds the opened file
to the path's device/inode identity. Bounded binary reads and raw SHA-256 checks
remain. The hash reader also requires the observed size to equal bytes read.
This is observed-change detection, with the existing limit that a concurrent
change restored between observations is not an authenticated history.

### Child-process fixture bytes

The timeout test used text `print('started')` but required LF bytes. Native
Windows produced CRLF. It now emits explicit binary LF bytes. A separate capture
assertion requires literal CRLF and Ctrl-Z bytes to survive stdout capture, and
literal CRLF to survive stderr capture. The capture implementation is unchanged.

## Executed local evidence — 13 November 2026

Linux, GCC 14.2.0, CPython 3.12.14 and Git 2.52.0; a fresh Release renderer and
profile were built in `../agent33-release` using the native CMake distribution.

```sh
cmake -S . -B ../agent33-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build ../agent33-release --target hammond_render -j 2
ctest --test-dir ../agent33-release \
  -R '^python_test_(render_fixture|fixture_catalog|verify_render)$' \
  --output-on-failure --no-tests=error -V
```

All three selected CTest suites passed: 19 producer test methods, two catalog
methods covering all five real renders, and 27 independent verifier methods.
No assertions were suppressed and no tests skipped. The new checks include:

- Stable simulated Windows descriptor/path differences with a real renderer,
  exact CRLF profile/score copies and unchanged compiled profile bytes.
- Rejection of device, inode, mode, size, mtime and ctime changes within either
  API by both the hash reader and WAV inspector; POSIX identity mismatch rejection.
- Nonsymlink/regular-file checks and a streaming byte-limit case even when
  simulated metadata understates the actual size.
- A temporary Git index/checkout with `core.autocrlf=true`: original catalog,
  profile, wrapper and all five scores retain their bytes and hashes. Text-looking
  PDF/WAV/B3P sentinels retain deliberate CRLF, proving binary rules take effect.
  Every Git override is per command; the project configuration is not modified.

The source atlas remains 21,248,265 bytes with SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
Native Windows rerun, other platform qualification and physical fidelity are
separate evidence gates. This assignment establishes the local repair/regression
results only; current hosted status belongs in the shared development log.
