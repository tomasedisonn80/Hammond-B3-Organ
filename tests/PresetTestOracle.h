#pragma once

#include <cstdint>

// Independent literal test fixture, transcribed by A10 on 2026-11-14 from
// Hammond_B3_Leslie_Research_Atlas_500pp.pdf, printed/PDF page 122 (chapter 019),
// evidence edition 12 November 2026. The original page was read as both an
// image and pdftotext output; no production generator or lookup supplied values.
// PDF SHA-256:
// 4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769
// These are documentary tap indices, not measured gains or linear amplitudes.
// The atlas cites S019-01, Table IV, printed 4-1; that underlying factory page
// and any specimen wiring were not independently verified by this fixture.

namespace preset_test_oracle {

inline constexpr const char* kKeys[9] = {
    "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A",
};

// [manual][fixed key][drawbar]: manuals are Upper=0, Lower=1; key indices
// follow kKeys (there is no None/Cancel/bank row). Drawbar order in feet:
// 16, 5 1/3, 8, 4, 2 2/3, 2, 1 3/5, 1 1/3, 1.
inline constexpr std::uint8_t kPositions[2][9][9] = {
    { // Upper
        {0, 0, 5, 3, 2, 0, 0, 0, 0}, // C# 005320000
        {0, 0, 4, 4, 3, 2, 0, 0, 0}, // D  004432000
        {0, 0, 8, 7, 4, 0, 0, 0, 0}, // D# 008740000
        {0, 0, 4, 5, 4, 4, 2, 2, 2}, // E  004544222
        {0, 0, 5, 4, 0, 3, 0, 0, 0}, // F  005403000
        {0, 0, 4, 6, 7, 5, 3, 0, 0}, // F# 004675300
        {0, 0, 5, 6, 4, 4, 3, 2, 0}, // G  005644320
        {0, 0, 6, 8, 7, 6, 5, 4, 0}, // G# 006876540
        {3, 2, 7, 6, 4, 5, 2, 2, 2}, // A  327645222
    },
    { // Lower
        {0, 0, 4, 5, 4, 5, 4, 4, 0}, // C# 004545440
        {0, 0, 4, 4, 2, 3, 2, 2, 0}, // D  004423220
        {0, 0, 7, 3, 7, 3, 4, 3, 0}, // D# 007373430
        {0, 0, 4, 5, 4, 4, 2, 2, 0}, // E  004544220
        {0, 0, 6, 6, 4, 4, 3, 2, 2}, // F  006644322
        {0, 0, 5, 6, 4, 2, 2, 0, 0}, // F# 005642200
        {0, 0, 6, 8, 4, 5, 4, 3, 3}, // G  006845433
        {0, 0, 8, 0, 3, 0, 0, 0, 0}, // G# 008030000
        {4, 2, 7, 8, 6, 6, 2, 4, 4}, // A  427866244
    },
};

} // namespace preset_test_oracle
