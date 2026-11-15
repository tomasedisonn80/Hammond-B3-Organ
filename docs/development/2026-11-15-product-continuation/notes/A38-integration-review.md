# A38 — integrated targets and portable fixture repair

Actual worker `/root/w07_a38_integration_review`, wave 7. Recovered standing
instructions, complete M0–M9 plan, current checkpoint/assignments, feature
contracts and source. Reviewed base `b9d352a82ac1afdec70c76ec5b1987785a37762e`
plus the explicitly hashed wave-7 overlay in
[`PRODUCT_INTEGRATION_REVIEW.md`](../../../reviews/PRODUCT_INTEGRATION_REVIEW.md).

Confirmed root's numeric `while(1)` repair for the CMake 3.31.6 install-script
CMP0012 failure without relaxing any preflight assertion. Remaining crossover
conditions use explicit predicates/comparisons; the six-file component stays
explicit and excluded from default/other-component installation.

Root expanded ownership after two observed Windows failures. Repaired only:

- `calibration_lifecycle_driver.cpp`: immediately own both SDL environment
  values, preserving scenario and trace across SDL's shared Windows buffer and
  later app environment reads. SHA-256
  `e33b17f3f9642d17e21e5d645f8f3d82a176ca030b78164521af2e530ce57dd6`.
- `test_crossover_install.py`: normalize only Windows stdout CRLF pairs before
  the existing exact LF-file comparison; all content and output-safety
  assertions remain. SHA-256
  `8daf656ad24f812d9d11920c35c846ec46d344e4b7fc78ed330ae9f764ffcd03`.

Also identified the fixture's missing MinGW wide-entry link option; root added
`-municode`. Identified A37's erroneous one-failed-replay summary assertion;
A37 corrected it to two. Neither finding is an executed MinGW/sanitizer pass.

Read-only CTest JSON discovers 178 entries, including 48 standalone-prefixed
names. Generated commands confirm isolated fake/native test inputs, inherited
thread support, app/test target separation and aggregate dependencies. The
fixture proves real app/discovery/SDL callback lifecycle with synchronous fake
MIDI offers; it does not qualify asynchronous driver races or hardware.
Engine/profile, all 47 parameters, state4/readers1–3 and plugin identities remain
unchanged. Crossover remains independent of Engine; R4 ownership is preserved.

**Verification:** A38 ran source/hash/diff checks, Python AST parsing and
`ctest --show-only=json-v1`; no build or test execution. Root reconfigured,
rebuilt and ran the strict focused gate: **2/2 passed in 21.92s** (installation
1.47s; native calibration 20.44s), CMake4.4.5/GCC14.2 Release/MIDI-OFF/dummy SDL.
Repaired probe summary confirms 10 subprocesses, seven lifecycles and two
intentional failed replays. Reports retain original Linux/Windows failures and
new source identities separately.

**Next:** publish the repaired source and inspect replacement Windows and
CMake3.31.6 hosted results plus A37's expanded leak-enabled native gate. Earlier
`ff41d412` passes and current discovery do not qualify this overlay.
