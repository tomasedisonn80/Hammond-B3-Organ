# Assignment 12 — independent rotary-reference qualification

## Identity, inputs and scope

- Actual worker identity: `/root/w02_a12_reference_tests`.
- Assignment: 12 of 60, wave 2; execution date: 2026-11-13 UTC.
- Starting repository HEAD: `6b4b6bd3a881dd13e6e3b7f846993f0fbbb977f9`.
- Owned changes: [maintained tests](../../../tests/test_rotary_reference.py),
  [primary-source review](../../research/ROTARY_PRIMARY_REVIEW.md), and this record.
- Instructions read: repository `AGENTS.md`, numerical contract, reference
  boundary, and source-reader notes 04 and 06. Atlas pp. 302–303 were reread
  directly from the previously extracted page text.

The worker did not edit the reference implementation, shared status,
contracts, CMake, fixtures, production DSP or another worker's files. No
commit, push or child-agent spawn was performed by this assignment.

## Maintained qualification

`tests/test_rotary_reference.py` supplies 33 standard-library `unittest`
methods. It can run directly from the repository:

```sh
python3 -B tests/test_rotary_reference.py -v
```

| Group | Independent expectations and behavior covered |
| --- | --- |
| Motion: 14 methods | Constant/zero/signed speed; half-life identities; integrated ODE balance; complementary trajectories; Taylor remainder bounds down to `h=1e-100`; surviving long-decay tails; full-epoch decay; separately integrated RK4 convergence; 1,000 deterministic subdivisions; command ties, reversals and negative startup history; large signed turn counts; frame-time precision; hostile caller Decimal context; malformed inputs. |
| Propagation: 12 methods | Cardinal vectors and incoming bearing; 3–4–5 static distance; constant axial distance; near/far endpoints resolving the cosine sign; constructed tangent and quarter-turn emission times; both Mach-limit Doppler ratios; mirror/translation invariance; emission before a later command and before startup; second-order finite-difference derivative convergence; causality and serialization; strict envelope/budget failures. |
| Scene/CLI: 7 methods | Independent horn/drum histories and immutable scene objects; exact file digests and model/contract identity; exact observation times with no hidden algorithmic latency; byte-format sensitivity of hashes; strict duplicate-key/type/order/size/event admission; nonblocking FIFO rejection; structured CLI errors; no output files in the caller directory; isolated mathematical import without production/profile numerical code. |

The suite does not call an author self-test. ODE conservation, constructed
Cartesian geometry, and RK4 integration provide checks beyond duplicating
the closed-form evaluator. The RK4 check must exhibit fourth-order
convergence; the finite-difference emission derivative must exhibit
second-order convergence, so an arbitrary agreement threshold cannot hide
an incorrect limiting value.

## Executed results and discovered defect

Environment: Python **3.12.14**, Linux x86-64,
`Linux-6.18.57-x86_64-with-glibc2.41`. Only standard-library dependencies were
used. Temporary event/profile/FIFO files and captured run output stayed
outside the repository. Test subprocesses use `-B`; isolated import also
uses `-I`.

1. The first launch failed before creating a process because the exec-server
   transport disconnected. Retrying the same command launched normally.
2. First completed suite run: **31 methods in 2.349 s; 30 passed, two subcase
   errors in the constant-speed method**. Both errors are zero speed at
   the maximum elapsed time and minimum time constant, one per direction.
3. A dedicated full-epoch positive-decay regression was then added and
   executed: **one method, one error**, confirming the same domain issue
   also affects a strictly positive tail.
4. After adding explicit negative-startup propagation coverage, the final
   recorded suite ran **33 methods in 2.050 s; 31 methods passed, three
   subcase errors across two methods**. Exit status was **1**. Measured
   outer subprocess duration was 2.237 s. The reference, validator,
   profile, test, contract and atlas hashes were unchanged before/after
   this execution.

**Gate status: failed pending implementation correction.** Reproductions:

```python
evaluate_segment(MotionState(".7", 0), 0, ".001", 1, 86400)
evaluate_segment(MotionState(0, 38), 0, ".001", 1, 86400)
```

Both raise `ReferenceError("scalar exponent is outside the reference domain")`.
For the first, the physical result is unchanged angle and exactly zero
speed. For the second, `ln(speed) = ln(38) - 86400000` and the angle tends
to `0.038 rad`. Decimal can represent this tail with a compact exponent;
the implementation's ingress exponent guard rejects the internally
derived `MotionState`. A zero multiplied by the extreme exponential also
retains an extreme exponent and is rejected. Both cases lie inside the
frozen elapsed-time/time-constant domain.

The defect and both reproductions were sent to the integrator. The
regressions remain strict failures; they were not weakened, skipped or
changed to expect rejection. This worker did not modify the implementation.
All other recorded methods passed, including caller Decimal independence,
geometry endpoints, derivative convergence, event histories and CLI tests.
Final owned-file checks confirmed UTF-8 readability, final newlines, no
trailing whitespace, and all seven relative Markdown links resolving.

## Exact tested inputs

| Input | SHA-256 at final recorded execution |
| --- | --- |
| `tools/rotary_reference.py` | `603f28969b6d59399c9295eaf7c1dbbefe31bf244e9c08aee38815c84beee352` |
| `tools/validate_rotary_profile.py` | `260b63aaf3e22e136ce85143565c5df721ad2869b4ed377f1c5e95d454de5279` |
| `data/rotary/nominal-research-v1.json` | `c0473cb20604726d989d7c280700109f647f7b227edb71c61d275ed9bfd67443` |
| `tests/test_rotary_reference.py` | `1f4b86baa292723027a65349a113d1e6fec21477a92516d4cba2951c43c0c223` |
| `docs/ROTARY_NUMERICAL_CONTRACT.md` | `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63` |
| `Hammond_B3_Leslie_Research_Atlas_500pp.pdf` | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |

## Primary-source check

The publisher's DAFx-02 paper was opened independently and the relevant
text examined at §3.3, §4.1/Eq. (18), §§4.2–4.3 and §5. The two
atlas-identified formula/listing discrepancies were confirmed by
coordinate expansion and interpolation endpoint reasoning. Exact printed
and PDF page locators, the Model 600 measurement scope, and limits are
recorded in the [primary review](../../research/ROTARY_PRIMARY_REVIEW.md).
No externally sourced PDF or measurement data was added to the repository.
The web screenshot endpoint returned text placeholders; this assignment
does not claim independent pixel inspection of those primary pages.

## Next owner action and limits

The integrator should correct the derived-state exponent admission while
preserving strict untrusted-input validation, then rerun all 33 methods
against a stable source snapshot and append the new exact source identity
and result. Register the maintained suite in the appropriate integration
gate; CMake registration was outside this worker's ownership. Preserve
this failed run as defect-discovery evidence.

After that numerical gate, continue native motion/path parity, waveform
interpolation and dynamic alias qualification, lifecycle/allocation checks,
and identified physical acquisitions as separate gates. This assignment
did not execute native builds, CTest, audio rendering, host interaction,
hardware measurements, allocation checks or performance benchmarks. It
does not qualify native rotary behavior, interpolation, real-time use,
cabinet response or physical M7 fidelity.

## Integrator correction and rerun

After the independent failure above, the integrator retained the ordinary scalar
representation guard while admitting compact MotionState exponents throughout the
private 80-digit context. Finite, digit-count and physical bounds remain unchanged;
zero is canonical and positive decay tails are retained. No acceptance assertion
or numerical budget was weakened.

`python3 -B tests/test_rotary_reference.py` then passed all **33 methods**,
exit 0, in **2.227 seconds**. The test file was unchanged. Repaired reference
SHA-256: `4c8bbcdf279f87aaad5b730d60a82958321ba3c1a92e5318eb5e37b1e83c8b0d`. This closes the two implementation defects
reported above; it is still an offline mathematical reference, not native rendering
or physical fidelity acceptance.
