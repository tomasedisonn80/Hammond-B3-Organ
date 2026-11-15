# A25 — prepared crossover allocation acceptance

Actual worker `/root/w05_a25_crossover_allocation`, wave 5. Read complete standing
instructions, plan, session checkpoint and crossover contract. Starting HEAD
`af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d`. Owned only
`tests/test_leslie_crossover_allocation.cpp` and this note.

Added a current-thread global C++ allocation/deallocation observer following the
existing calibrated probe convention. Explicit volatile function-pointer calls
exercise twelve scalar/array, sized, aligned and nothrow allocation/deletion
pairs before and after fixtures, preventing allocation-elision false passes.
Native aligned allocators retain requested payload boundaries on Linux/macOS/MSVC;
no sanitizer exclusion or leak-policy change was introduced.

Strict GCC 14.2 C++20 Release passed: 12 rate/load fixtures, 26 calibration sweeps,
312 observed allocations and 312 frees; then zero allocation/free calls across
2,478 API observations. These include 1,550 scalar frames, 473,952 block frames,
492 successful blocks, 24 empty calls, 120 observations and 158 rejections, including
last-input NaN, overlap, capacity/clock overflow and proven third-interval
numerical failure. First calls are observed without warmup. Assertions, storage
and reporting remain outside recording. Offline prepare/restore/rate/response
have separate 134 call totals; their zero counts do not make them realtime APIs.
Release execution took 0.0151 s. Scoped whitespace checks passed.

From repository root, actual Release command used:

```sh
g++ -std=c++20 -O2 -DNDEBUG -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror -Iinclude -Itests \
  '-DHAMMOND_SOURCE_DIR="/workspace/scratch/5b7d983ac078/Hammond-B3-Organ"' \
  '-DHAMMOND_TEST_PROFILE="/workspace/scratch/5b7d983ac078/build-native/nominal.b3p"' \
  tests/test_leslie_crossover_allocation.cpp ../build-native/libhammond_core.a \
  -o ../a25-checks/test_leslie_crossover_allocation
../a25-checks/test_leslie_crossover_allocation
```

The isolated test plus `src/LeslieCrossover.cpp` also compiled with
`-O1 -g1 -fsanitize=address,undefined -fno-omit-frame-pointer`. Leak-enabled
execution exited 1: LeakSanitizer cannot operate under ptrace. An independent
`int main(){return 0;}` sanitizer control reproduced that environment failure.
Neither run is a sanitizer pass; no leak check was disabled. Original logs and
Release JSON remain in sibling `a25-checks/` for integrator retention.

SHA-256: test `4d652c1d39e504a64e5febab9b52ae8e78ee5c40276e2b0f4bb697ebe5f77950`;
model source `1a1bdde72af95709143afc4f62991c138ff3458cc78765fbe49a229d82693525`;
linked core `d110f7523afcc3ae1ab6053da7dfc86dfcddc66d4bfe19aabf1f0458fb1bd13f`.
The core object's undefined symbols were only complex/arithmetic math helpers.
C heap/system allocation, other threads, locking and deadlines are not observed.
Next: root's coherent CTest and leak-enabled hosted sanitizer gate. No production,
shared-build or commit changes.
