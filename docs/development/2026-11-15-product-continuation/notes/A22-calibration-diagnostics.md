# A22 — independent expression diagnostics

Actual worker `/root/w04_a22_calibration_diagnostics`, wave 4. Read the standing
instructions, complete M0–M9 plan, current session records and expression
calibration contract. Starting HEAD `af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d`;
qualification uses the integrator's explicitly identified uncommitted native
build, not that documentation commit alone.

Updated only `apps/standalone/native_tests/test_standalone_app.py`, added
`test_standalone_expression_diagnostics.py` beside it, and wrote this note.
The public diagnostics remain additive schema 3. Exact members and types are
still required; booleans cannot satisfy integer endpoints. Reusable schemas
separate settings, observations and the final-only `pre_shutdown_active` field.
`assert_expression_calibration` independently validates endpoint bounds,
selected validity, nullable active state, pending request channels and reconnect
consistency. Presentation observations validate calibration and modal focus.

The new native gate observes non-default inverted configuration without an
epoch; active calibration surviving selected edits, reopening and an invalid
selected pair; and a copied reconnect request followed by retirement. Actual
painted diagnostics retain active versus selected settings. Shutdown reports
active null while separately retaining a previously active interval; retirement
before shutdown retains no active claim. Adapter edits/connections leave the
original musical controls and state bytes unchanged. Twenty altered records
exercise exact-schema and contradictory-lifecycle rejection.

## Executed checks

From the repository directory, with `PYTHONDONTWRITEBYTECODE=1` and
`HAMMOND_STANDALONE_EXECUTABLE=/workspace/scratch/5b7d983ac078/build-native/apps/standalone/hammond_standalone`:

- `python3 apps/standalone/native_tests/test_standalone_app.py`: **21/21**, all
  original **184** native subprocesses, **14.749 s**.
- `python3 apps/standalone/native_tests/test_standalone_expression_diagnostics.py`:
  **4/4**, three native subprocesses, final **2.942 s**. Ordered observations
  replace narrow elapsed-time assertions so delayed event delivery remains valid.
- Scoped `git diff --check`: passed. Logs remain in sibling `a22-checks/`.

SHA-256 identities: native executable
`7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`;
main `937b837d4ef4317d02ea2862ac34dc95031c73f0f32719b0924de29f4b721027`;
updated app test `5514d229bb969feeedd1be060d7e64dbd63cff22a08f0a70bd313d6308ae7236`;
new gate `8a6e5bd218a36858af1a7ce2269f3b1c73fcbd20a607d037c62f380b27de3fea`.

Next: root registers `test_standalone_expression_diagnostics` with the same
executable environment, timeout 90, labels standalone/native/midi. A24 migrates
the existing MIDI replay observation schema using `REPLAY_EXPRESSION_FIELDS`.
These explicit dummy-driver runs do not qualify hardware, display fidelity,
native port reconnect or physical pedal calibration. No production edits,
shared-build mutation, commits or publication were performed.
