# A12 - Independent crossover contract review

Actual worker `/root/w02_a12_crossover_review`, wave 2. Reviewed complete
AGENTS/plan/session instructions, the [crossover contract](../../../LESLIE_CROSSOVER_CONTRACT.md)
and its registry at HEAD `da48180390a9fd473643d1759c153cb9d37ecfb6`.
Contract/registry were uncommitted work; this review does not qualify a native
implementation. Only this note changed; no build or product edit occurred.

## Independent circuit check

With A=1 and B=0, I independently formed node equations
`H*(Y_AH+s*C16A)=Y_AH` and `W*(Y_AW+s*C16B+1/RW)=Y_AW`, where
`Y_AH=1/(s*L2)+1/RT` and `Y_AW=1/(s*L3)`. Outputs are `1-H`, `W` and
`(1-H)*Y_AH+(1-W)*Y_AW`. Thus the treble load remains floating A-H;
neither output polarity nor input-current sign is reversed.

Python standard-library complex arithmetic compared those nodal equations with
separate series/parallel reduction at 121 logarithmic frequencies, 10–20000 Hz,
plus the three printed checkpoints. Maximum normalized complex error was
**8.520790882018641e-16** over all three outputs at **124 frequencies**.

| Hz | Treble dB / degrees | Bass dB / degrees | Input impedance magnitude, ohm |
| --- | --- | --- | --- |
| 400 | -15.87815330 / +149.17391003 | -0.06297618 / -54.18525735 | 15.63398287 |
| 800 | -4.60021838 / +110.17359323 | -4.88733013 / -111.46352407 | 23.82990440 |
| 1600 | +0.00174910 / +52.86454582 | -16.20042828 / -149.60136978 | 15.45404816 |

The four differential equations follow KCL and inductor voltage laws. Expanding
the stated energy derivative gives exactly `u*Iin-VT²/RT-VW²/RW`.
One thousand deterministic asymmetric real-state substitutions retained maximum
floating-point residual **1.4210854715202004e-14 W**. Both second-order branch
polynomials have positive damping and stiffness for admitted positive loads;
trapezoidal transformation preserves their strict linear stability.

For `z=exp(j*omega)`, the actual endpoint recurrence response is
`X=solve(I-F/z,G*(1+1/z))`; outputs follow the same differential ports. The
contract's warped analog frequency is consistent with this expression. Midpoint
power, not endpoint rectangular power, gives its discrete energy identity.
DC is now explicitly admitted; negative/nonfinite frequencies and Nyquist reject.

## Clarifications accepted before implementation

Root added the exact infinity-norm residual
`norm(M*X-R)/max(1,norm(M)*norm(X)+norm(R))`, using row-sum matrix norms,
maximum-entry vector norms and complex magnitudes. Preparation reports the
maximum F/G solve residual; response uses its actual recurrence solve.

Root also froze block precedence: unprepared, unequal counts, over-capacity,
frame overflow, overlap, then sample/intermediate admission. Scalar precedence
is preparation, overflow, then numerical admission. Bounded counts therefore
precede byte-range arithmetic; equal empty spans succeed at maximum frame count.
Interpret the explicitly inclusive `<=` computational limits literally; only
exceeding a bound rejects, without clipping.

The revised contract is suitable to implement. Its stopped reconfiguration, exact physical-state preservation,
whole-block transaction and default-load/physical-evidence distinctions are
coherent. Native execution, allocation behavior, decay, source admission and
same-Hz error characterization remain implementation acceptance, not this review.

Reviewed contract SHA-256: `752a52ee973db2ad80071eb1c1586aee5d8e52e510e0c64d2526e85176f32f82`.
Registry SHA-256: `f55fa98c246b4a19dce12ca829a141cff744f71242cccb68db12b404400319cc`.
