# Synthetic source-leakage audition v1

Six actual two-second renders demonstrate the separately identified static source
coupling layer. The paired comparisons use **the same explicit input gain 0.75**,
nominal profile, seed 1939, event bytes, rate 48000 Hz and block size 127. They are
stereo PCM16 with identical dry channels. No file is separately normalized.

| Recording | What to listen for | Pre-PCM peak |
| --- | --- | ---: |
| [solo-identity-g075.wav](solo-identity-g075.wav) | Ideal-contact C3/C4, empty graph at 0.75. | 0.022500 |
| [solo-pair-g075.wav](solo-pair-g075.wav) | Same solo with signed synthetic donor contribution. | 0.023526 |
| [solo-legacy-g100.wav](solo-legacy-g100.wav) | Legacy no-flags reference, gain 1. | 0.030000 |
| [solo-identity-g100.wav](solo-identity-g100.wav) | Explicit identity at gain 1; byte-identical to legacy. | 0.030000 |
| [phrase-identity-g075.wav](phrase-identity-g075.wav) | Manuals, percussion and pedals; empty graph at 0.75. | 0.055698 |
| [phrase-pair-g075.wav](phrase-pair-g075.wav) | Same full phrase with signed synthetic coupling. | 0.055913 |

## Listening sequence

Compare the two **solo g075** files first. MIDI 48/C3 opens source 25 at the 8-foot
drawbar. The synthetic pair adds source 37/C4 at **+1/16**, although its own key is
released. From 0.50–0.75s the Upper route is cancelled: the output is exactly silent
while phases continue. At 0.75s it reconnects the held C3. At 1.00s the score releases
C3 and plays C4/source 37; this recipient instead receives source 25 at **−1/32**.
All notes release at 1.75s. These signs and gains are invented numerical fixtures,
not estimates of physical generator adjacency or measured pickup coupling.

Then compare the **phrase g075** files. This original two-second gesture uses
Upper nominal contact travel and second-harmonic percussion, Lower sustain and
both nominal pedal mixtures. Upper Cancel/reconnect does not mute independently
sounding Lower/pedal routes. The phrase is a listening/behavior demonstration;
it is not the independently quantified solo oracle.

The two **solo g100** files retain an explicit default-path control: legacy with
no leakage flags and empty graph at gain 1. Their complete WAV bytes are identical.
Their higher level must not be confused with the g075 coupling comparison.

## Reproduce into a new directory

From the repository root, after building `hammond_render`:

```sh
python3 tools/build_source_leakage_demo.py \
  --renderer build/hammond_render --output out/source-leakage-audition
```

On multi-configuration builds use `build/Release/hammond_render.exe` (Windows)
or the corresponding configuration directory. The output parent must already
exist; an existing file, directory or dangling symlink at the output is refused.
The builder uses only Python 3.10+ standard-library code. It invokes the actual
nominal-profile and leakage compilers and renderer, verifies all six WAVs and
receipts, then publishes the new bundle from private staging. Publication uses
exclusive directory/file creation with rollback and provenance last; visibility
of the whole directory is not atomic. Source inputs and the executable are
hashed before/after. Filesystems without hard-link support fail safely.

For an individual repeat, choose a new WAV filename and use these retained inputs:

```sh
build/hammond_render --profile examples/demos/source-leakage-audition-v1/nominal.b3p \
  --events examples/demos/source-leakage-audition-v1/solo.events --frames 96000 \
  --sample-rate 48000 --block-size 127 --seed 1939 --drawbars 008000000 \
  --contacts ideal --percussion off --pedal-drawbars 00 \
  --source-leakage examples/demos/source-leakage-audition-v1/pair.b3leakage \
  --leakage-input-gain 0.75 --output out/solo-repeat.wav --fail-on-clip
```

## Retained evidence and limits

[provenance.json](provenance.json) retains every actual command and receipt,
source/executable/input/output SHA-256, data format, unchanged-input result and
comparison. The builder's source inventory identifies inspected bytes; it is
not an independent attestation that a supplied executable was built from them.
The integrating session owns coherent build qualification.

All four solo files were checked against an independent Python direct-time sine,
literal routing and PCM16 oracle, including exact cancellation/release silence.
The permitted difference was fixed at **one integer quantization step per channel
sample**; the observed maximum is **0**.
The unconfigured/empty-gain-one WAV control is byte-exact. The two gain-matched
pairs contain nonzero differences; detailed counts are in provenance.

The model is synthetic and unmeasured, with no scanner, AO-28 or Leslie audio
connected here. This bundle does not establish physical fidelity, contact
bandwidth, a host callback deadline, or harmonic-source composition. Review the
[frozen audition contract](../../../docs/SOURCE_LEAKAGE_AUDITION_CONTRACT.md)
and [core/data contract](../../../docs/SOURCE_LEAKAGE_CONTRACT.md) for exact
scope, source pages, safety limits and separate acceptance requirements.
