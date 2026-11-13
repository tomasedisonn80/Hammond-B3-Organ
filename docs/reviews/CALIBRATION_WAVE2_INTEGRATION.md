# Calibration wave 2: coherent foundation acceptance

## Qualified source and scope

Local commit `ff18b5dc9acdb4b488f3df8c87e4f5277d212a57`, tree
`f49f229d0291a6dc1e2b114319573ff0493019bc`, contains the twelve accepted
assignments, the completed fresh PDF review, three independently reviewed
contracts, shared JSON primitives and this session's accounting checker.
It excludes the unfinished decoder, corpus auditor and metric producer.

The source was exported with `git archive` into a separate directory. Configure
and every selected test used that immutable export. Linux x86-64, GCC 14.2.0,
CMake/CTest 4.4.4 and Python 3.12.14 were the local tools. Both optional native
adapters were OFF. The original 85-suite full baseline remains separately
recorded in [CALIBRATION_BASELINE.md](CALIBRATION_BASELINE.md).

## Commands and observed results

From the frozen source, with matching CMake and CTest on PATH:

```sh
cmake -S . -B ../w2-build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
cmake --build ../w2-build --target hammond_profile --parallel 2
ctest --test-dir ../w2-build --output-on-failure --no-tests=error \
  -R '^python_test_(capture_common|calibration_session_records|repository_integrity)$'
python3 tools/check_calibration_session.py --repo . --expected-complete 12 --json
```

The focused CTest integration passed **3/3 suites**, zero failures, in **3.85
seconds**. It includes the 49-method independent JSON acceptance and 27-method
accounting acceptance plus repository integrity. The exact completion gate
reported twelve complete, three running and 45 planned, with complete waves 1-2
and zero errors. Its distinct recorded dispatch count was fifteen; running
workers are not counted as completed.

The live source-archive audit immediately before staging separately passed with
448 Markdown files, 2,567 local links and the unchanged 500-page PDF hash. The
frozen integrity suite above is the coherent checkpoint result; live-tree counts
are retained only as that earlier observation. No full 87-suite rerun is claimed.

## Repairs and remaining evidence

Independent testing reproduced fdopen-failure descriptor leaks and cleanup
errors masking publication outcomes in the newly authored JSON helper. Those
paths were repaired, and all four regressions now pass. If a post-publication
temporary cleanup fails, the complete new file remains and the DataError states
that outcome. Existing destinations are preserved.

Independent contract review verified the literal sample identities/equations and
clarified the final-to-final_test purpose mapping and explicit `2e18` comparison
report guard. The report retains the authors' earlier and final reviewed hashes.

Decoder/corpus/metric implementations and their separate acceptance are next.
This checkpoint does not qualify actual audio files, cross-capture independence,
physical acquisition/calibration, native devices, new hosted platforms or M8
fidelity. A subsequent publication containing this report has the same executed
production/test inputs; its documentation-only tree difference is not a new run.
