# A47 — Native callback ownership and recovery review

Actual worker `/root/w08_a47_native_recovery_review`, wave 8. Read the complete
AGENTS/plan, current session recovery and ownership, feature contracts, accepted
A26/A38 reviews, actual adapter/application/dependency code and relevant tests.
Inspected HEAD/tree `d556da017ea0a5d4f2d231416782dbc5066e58c2` /
`a3150fd2489a50a430b02c01eadd5e0c180bc7f9`; read-only live remote query matched.
Other workers' uncommitted changes remain separate.
Final checks observed the integrator's local `d8c39f7986746eacc991747153c7dbb012bb9a32`
advance; all fourteen current native-summary source hashes and the app still
matched. The earlier remote query does not verify that later commit remotely.

The [review](../../../reviews/PRODUCT_NATIVE_RECOVERY_REVIEW.md) found no new
application-level CC120/121/calibration ownership defect. Native callbacks never
read calibration or post to Session. Changed configuration stops translation,
closes native input, discards only after quiescence, and waits for the complete
applied scoped-release barrier. Discovery publishes owned results and joins;
normal/exception shutdown retains the required audio/Session/SDL lifetimes.

**A47-N1:** pinned RtMidi WinMM ignores close/reset/stop return values and
CoreMIDI ignores disposal results before clearing connection state. The wrapper
can therefore miss a native-close failure. Real native callbacks access RtMidi
storage before the wrapper's entered counter; a post-destructor poison check
cannot preserve dependency storage already freed. This is a source-proven
error-observability gap and specific risk model, not an observed hardware
failure/use-after-free. The review gives exact source/hash locators and a narrow
below-RtMidi fault-injection/checked-close proposal. Root agreed to retain this
boundary; no production/test change or new leak exception was made.

Distinguished A26's synchronous facade, the backend fixture's direct saved
wrapper calls, threaded inbox tests and actual OS callback ownership. Retained
current root evidence is seven native lifecycles/ten processes/two intentionally
failed replays; the repaired facade's ordinary gate passed 20.50 s. The original
GCC13 expanded-sanitizer build failure remains; its 21 gates did not execute.

**A47 checks:** source/executable hashes, locked prepared-source transformation,
Python AST parsing, owned links/whitespace and this note's size. The
[bounded receipt](../reports/A47-native-recovery-review.json) records inputs and
scope. No build, CTest, app/device execution or sanitizer run. Production app
SHA remains `7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`.

**Next:** qualify the repaired hosted selection, then assign A47-N1's platform
fault/retirement gate. Preserve 47 parameters, state4/readers1–3, 91 sources,
the dry Engine, existing quarantine policy and all unrun physical-device gates.
