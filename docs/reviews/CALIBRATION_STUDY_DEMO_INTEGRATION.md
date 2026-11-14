# Calibration study and demo integration

## Exact coherent source

The first **34 actual calibration assignments** are accepted: waves 1–5 and the
study/demo producer/acceptance pairs in wave 6. Replay and installation work
was active and deliberately excluded from this freeze. The local source commit
is `1aef68489fc18b860bbab8fd06a65fdde8a4d6cd`, tree
`5ed86b2f0eeee4e00926aebaaf4432ec61760328`. The retained GitHub source commit
`783363f627afeb07f1401fcff042d1a24df094dd` has that exact verified tree.

Its parent evidence is the [combined wave-5 gate](CALIBRATION_WAVE5_INTEGRATION.md):
99/99 complete SDK-free Release suites at tree
`3329cf68bb9ea84479e254934778935bb5c44773`, including remote standalone
`0085e33`. The new study/demo source changes no C++ source, public parameter,
state format, native identity or the existing install component. The private
job seam shares its existing implementation and adds early consumed-job binding
and a shared study snapshot; the ordinary public signature/report stay intact.

Root extracted the committed source into a fresh directory with `git archive`,
configured Release with tests enabled and both optional native adapters disabled,
built the renderer, and ran the affected capture/legacy/integrity suites.
All **16/16 suites passed in 40.21 seconds**, zero failed suites. This is a
focused gate; it is not reported as a second unfiltered 101-suite run.

## Commands and actual scope

Toolchain: GCC 14.2.0, CMake/CTest 4.4.4, Python 3.12.14, Linux x86_64.
The actual CMake binary is recorded in the wave-5 report. Equivalent commands:

```sh
cmake -S /workspace/scratch/c9f3ead4c910/w6-study-demo-source -B /workspace/scratch/c9f3ead4c910/w6-study-demo-build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
cmake --build /workspace/scratch/c9f3ead4c910/w6-study-demo-build --target hammond_render --parallel 2
ctest --test-dir /workspace/scratch/c9f3ead4c910/w6-study-demo-build --output-on-failure --no-tests=error --output-junit /workspace/scratch/c9f3ead4c910/checks/w6-study-demo-ctest.xml -R '^python_test_(audio_analysis|capture|capture_audio|capture_audio_admission|capture_common|capture_comparison|capture_corpus|capture_corpus_admission|capture_policy|capture_job|capture_readiness|capture_numerics|capture_study|capture_demo|calibration_session_records|repository_integrity)$'
```

The selected suites include independent audio, corpus, metrics, policy, admission,
job, readiness, high-precision numerics, study and demo acceptance; shared JSON,
retained session accounting and repository integrity; and existing capture-v1
and renderer-backed analyzer checks. Study has 61 methods and demo 43; their
frozen independent notes retain exact counterexamples, source identities and
honest resource/platform limits. The final job regression has 81 methods.
Audio admission retains two explicit native-capability skips; a passed CTest
suite is not a claim that every capability ran on this host.

The actual manifest from this snapshot reports 34 complete, three running,
23 planned and 37 distinct actual identities, five complete logical waves and
no consistency errors. Later dispatches remain later observations. The checker
is retained-record consistency only, with `external_dispatch_attested: false`;
root's actual orchestration supplies the distinct dispatch evidence.

## Preserved outcomes and next gate

The 16-file demo retains literal original float32 vectors and independent raw/
decoded identities. The quarter-offset policies give pass and inconclusive;
the half-offset policy fails. The study deliberately retains all three reports
and returns failed. Source/runtime identities and complete original bytes remain
visible. Expected nonzero exits are tested, not converted into successful
comparisons. Generator inventory and `EXPECTED.json` say execution not_run;
new reports are produced only by actual tool execution.

No production defect or weakened expectation was required by the study/demo
independent acceptance. Earlier Windows/macOS failures and root's actual repairs
remain in [the hosted follow-up](CALIBRATION_HOSTED_PORTABILITY.md). This focused
Linux pass does not close the fresh hosted gate, installed-prefix qualification,
real-device or physical-fidelity requirements. Continue independently reviewed
report replay, CaptureTools installation/relocation and actual hosted observation.

## Local observation identities

| Observation | Bytes | SHA-256 |
| --- | ---: | --- |
| w6-study-demo-configure.log | 708 | e2a02b9c1db67f3dd150374fefc48fe0314728601aacedf3aac045cb55a495bb |
| w6-study-demo-build.log | 2253 | 804252a9c2a624bd71b0b24da0b5098f06beaf74d8fd20b996dcc31d5d978225 |
| w6-study-demo-ctest.log | 2148 | 2350477aaacfc2e579eff7e9ce4a6632e3a143844ebc816dfd9fe2d0d85b4053 |
| w6-study-demo-ctest.xml | 6304 | cc411081e88c02c236a5e4e5383282fc8f1894a0242920e3509f4f9e533a516f |
