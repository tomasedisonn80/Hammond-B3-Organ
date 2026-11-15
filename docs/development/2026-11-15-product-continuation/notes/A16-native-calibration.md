# A16 — native expression configuration and lifecycle

Actual worker `/root/w03_a16_native_calibration`, wave 3. Read the standing
instructions, whole M0–M9 plan, session scope/checkpoint, complete expression and
channel-mode contracts, and A10 review. Starting HEAD
`af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d`. Owned only
`apps/standalone/main.cpp` and this note; preserved concurrent adapter, painter,
crossover and test work.

Implemented strict decimal `--expression-min`/`--expression-max` and duplicate
checked `--expression-invert`, with combined validation before SDL initialization
or outputs. Native and synthetic requests copy calibration into each epoch;
changed requests retain the joined retirement/scoped release acknowledgment
barrier. Healthy identical native requests preserve the active epoch. Configured
settings survive disconnect/restart; applying them sends no musical expression
command.

MIDI now has eleven ordered focus stops using A18's shared rectangles. Endpoints
clamp, direction toggles, Home/End select boundaries, edits remain selected until
Apply, and reopening restores configured settings. Invalid Apply validates before
discovery mutation or the synthetic early return. Valid synthetic Apply retains
script-owned routing/calibration. Disconnect remains operational. Original UI
key-up dispatch still precedes modal/modifier/focus gates; Audio/Help retain six
controls.

Diagnostics add `midi.expression_calibration` with model, configured, selected,
selected-valid, active, pending request, reconnect/release pending, and separately
retained `pre_shutdown_active`. Inactive means JSON null, including after shutdown.
Replay observations capture settings/focus/error changes per modal input and
synthetic connection event; painted observations retain the actual displayed
settings/focus. Their `expression_calibration` members use the same schema.

Verification from the repository directory: `git diff --check --
apps/standalone/main.cpp` passed. GCC 14.2.0 isolated `-fsyntax-only` passed with
`-std=c++20 -O3 -DNDEBUG -DSDL_MAIN_HANDLED -Wall -Wextra -Wpedantic -Wconversion
-Wsign-conversion -Wshadow -Werror`, repository standalone/include paths and the
existing build's generated profile/SDL include paths. This read shared headers
but did not configure, link, run or mutate the shared build.

Checked main source SHA-256:
`937b837d4ef4317d02ea2862ac34dc95031c73f0f32719b0924de29f4b721027`.
Next: integrator builds coherent A14/A16/A18 source; independent native acceptance
must exercise CLI refusals, selected-versus-active replay, invalid/script Apply,
reconfiguration barriers and minimum/reference/Flat captures. No runtime,
physical-device or visual-fidelity pass is claimed here. No commits or publication
were performed by this worker.
