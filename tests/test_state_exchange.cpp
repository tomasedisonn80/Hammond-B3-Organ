#include "TestSupport.h"
#include "hammond/ControlStateIO.h"
#include "hammond/Engine.h"
#include "hammond/StateExchange.h"

#include <array>
#include <atomic>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <sstream>
#include <string>
#include <thread>

namespace {
using namespace hammond;
constexpr auto ok = StateExchangeStatus::Ok;

// Expression encodes a unique test generation exactly; every other field is
// independently derived from it. A torn read cannot pass by checking only a
// generation field. Tags used below stay below 65536.
ControlSnapshot pattern(std::uint64_t tag) {
    ControlSnapshot state{};
    std::size_t flat = 0;
    for (auto& manual : state.drawbars) {
        for (auto& bank : manual) {
            for (auto& position : bank) {
                position = static_cast<std::uint8_t>((tag * 7 + flat * 3) % 9);
                ++flat;
            }
        }
    }
    state.expression = static_cast<double>(tag) / 65536.0;
    state.selected_banks = {static_cast<DrawbarBank>(tag & 1U),
                            static_cast<DrawbarBank>((tag >> 1U) & 1U)};
    state.route_enabled = {(tag & 4U) != 0, (tag & 8U) != 0};
    state.percussion = {(tag & 16U) != 0,
                        static_cast<PercussionHarmonic>((tag >> 5U) & 1U),
                        static_cast<PercussionVolume>((tag >> 6U) & 1U),
                        static_cast<PercussionDecay>((tag >> 7U) & 1U)};
    state.pedal_drawbars = {static_cast<std::uint8_t>((tag * 2 + 1) % 9),
                            static_cast<std::uint8_t>((tag * 4 + 2) % 9)};
    state.fixed_registrations = {static_cast<FixedRegistration>(tag % 10),
                                static_cast<FixedRegistration>((tag / 10) % 10)};
    return state;
}

void same(const ControlSnapshot& actual, const ControlSnapshot& expected) {
    CHECK(actual == expected);
    CHECK(std::bit_cast<std::uint64_t>(actual.expression) ==
          std::bit_cast<std::uint64_t>(expected.expression));
}

void same(const StatePublishedControls& actual, const StatePublishedControls& expected) {
    same(actual.controls, expected.controls);
    CHECK(actual.acknowledged_sequence == expected.acknowledged_sequence);
    CHECK(actual.publication_revision == expected.publication_revision);
}

StatePublishedControls published(const StateExchange& exchange) {
    StatePublishedControls result{};
    CHECK(exchange.read_published(result));
    return result;
}

StateExchangeBatch peek(StateExchange& exchange) {
    StateExchangeBatch result{};
    CHECK(exchange.audio_peek(result) == ok);
    return result;
}

void test_defaults_queue_and_save() {
    StateExchange exchange;
    const auto initial = published(exchange);
    same(initial.controls, ControlSnapshot{});
    CHECK(initial.acknowledged_sequence == 0 && initial.publication_revision == 0);
    auto saved = pattern(99);
    CHECK(exchange.ui_snapshot_for_save(saved));
    same(saved, ControlSnapshot{});

    const auto empty = peek(exchange);
    CHECK(empty.size() == 0 && empty.last_sequence() == 0);
    CHECK(exchange.audio_can_commit(empty) == ok);
    for (std::uint64_t seq = 1; seq <= kStateQueueCapacity; ++seq) {
        auto original = pattern(seq);
        const auto accepted = exchange.ui_enqueue(original);
        CHECK(accepted && accepted.sequence == seq);
        original = pattern(100 + seq); // The queue owns a copy.
        CHECK(exchange.ui_snapshot_for_save(saved));
        same(saved, pattern(seq));
    }
    const auto full = exchange.ui_enqueue(pattern(5));
    CHECK(full.status == StateExchangeStatus::QueueFull && full.sequence == 0);
    CHECK(exchange.ui_snapshot_for_save(saved));
    same(saved, pattern(4));
    same(published(exchange), initial);

    // Appending even a full queue cannot invalidate an earlier empty token.
    CHECK(exchange.audio_can_commit(empty) == ok);
    CHECK(exchange.audio_commit(empty, pattern(77)) == ok);
    CHECK(exchange.ui_snapshot_for_save(saved));
    same(saved, pattern(4));
    CHECK(published(exchange).acknowledged_sequence == 0);
    CHECK(exchange.audio_commit(empty, pattern(88)) == StateExchangeStatus::InvalidBatch);
    CHECK(exchange.ui_enqueue(pattern(5)).status == StateExchangeStatus::QueueFull);

    const auto pending = peek(exchange);
    CHECK(pending.size() == 4 && pending.last_sequence() == 4);
    for (std::size_t i = 0; i < pending.size(); ++i) same(pending.snapshots()[i], pattern(i + 1));
    const auto second_peek = peek(exchange);
    CHECK(second_peek.size() == pending.size());
    CHECK(second_peek.last_sequence() == pending.last_sequence());
    CHECK(exchange.audio_can_commit(pending) == ok);
    CHECK(exchange.audio_commit(pending, pattern(4)) == ok);
    CHECK(peek(exchange).size() == 0);
    CHECK(exchange.audio_can_commit(second_peek) == StateExchangeStatus::InvalidBatch);
    CHECK(exchange.ui_snapshot_for_save(saved));
    same(saved, pattern(4));
    CHECK(published(exchange).acknowledged_sequence == 4);

    // After acknowledgement, an empty callback's automation becomes save state.
    CHECK(exchange.audio_commit(peek(exchange), pattern(450)) == ok);
    CHECK(exchange.ui_snapshot_for_save(saved));
    same(saved, pattern(450));
    CHECK(exchange.ui_enqueue(pattern(5)).sequence == 5);
    const auto one = peek(exchange);
    CHECK(exchange.audio_can_commit(one) == ok);
    CHECK(exchange.ui_enqueue(pattern(6)).sequence == 6);
    CHECK(exchange.audio_can_commit(one) == ok);
    CHECK(exchange.audio_commit(one, pattern(500)) == ok);
    CHECK(exchange.ui_snapshot_for_save(saved));
    same(saved, pattern(6));
    const auto remaining = peek(exchange);
    CHECK(remaining.size() == 1 && remaining.last_sequence() == 6);
    same(remaining.snapshots()[0], pattern(6));
    CHECK(exchange.audio_commit(remaining, pattern(600)) == ok);
    CHECK(exchange.ui_snapshot_for_save(saved));
    same(saved, pattern(600));
}

void test_invalid_values_tokens_and_signed_zero() {
    StateExchange exchange;
    StateExchange other;
    CHECK(exchange.audio_can_commit(StateExchangeBatch{}) == StateExchangeStatus::InvalidBatch);
    CHECK(exchange.audio_commit(peek(other), pattern(1)) == StateExchangeStatus::InvalidBatch);
    CHECK(exchange.ui_enqueue(pattern(1)));
    const auto batch = peek(exchange);
    const auto before = published(exchange);
    const auto reject = [&](const ControlSnapshot& invalid) {
        CHECK(!is_valid_control_snapshot(invalid));
        const auto result = exchange.ui_enqueue(invalid);
        CHECK(result.status == StateExchangeStatus::InvalidSnapshot && result.sequence == 0);
        CHECK(exchange.audio_can_commit(batch) == ok);
        CHECK(exchange.audio_commit(batch, invalid) == StateExchangeStatus::InvalidSnapshot);
        same(published(exchange), before);
        const auto after = peek(exchange);
        CHECK(after.size() == 1 && after.last_sequence() == 1);
        same(after.snapshots()[0], pattern(1));
    };
    for (const double value : {-1.0, std::nextafter(1.0, 2.0),
                               std::numeric_limits<double>::infinity(),
                               std::numeric_limits<double>::quiet_NaN()}) {
        auto invalid = pattern(1);
        invalid.expression = value;
        reject(invalid);
    }
    auto invalid = pattern(1);
    invalid.drawbars[1][1][8] = 9;
    reject(invalid);
    invalid = pattern(1);
    invalid.selected_banks[0] = static_cast<DrawbarBank>(2);
    reject(invalid);
    invalid = pattern(1);
    invalid.pedal_drawbars[1] = 255;
    reject(invalid);
    invalid = pattern(1);
    invalid.percussion.harmonic = static_cast<PercussionHarmonic>(2);
    reject(invalid);
    invalid = pattern(1);
    invalid.percussion.volume = static_cast<PercussionVolume>(2);
    reject(invalid);
    invalid = pattern(1);
    invalid.percussion.decay = static_cast<PercussionDecay>(2);
    reject(invalid);
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (unsigned value = 10; value <= 255; ++value) {
            invalid = pattern(1);
            invalid.route_enabled[manual] = false; // Hidden invalid modes still reject.
            invalid.fixed_registrations[manual] = static_cast<FixedRegistration>(value);
            reject(invalid);
        }
    }

    // Validation precedes capacity failure and preserves every pending record.
    for (std::uint64_t seq = 2; seq <= 4; ++seq) CHECK(exchange.ui_enqueue(pattern(seq)));
    CHECK(exchange.ui_enqueue(invalid).status == StateExchangeStatus::InvalidSnapshot);
    CHECK(peek(exchange).size() == 4);
    CHECK(exchange.audio_can_commit(batch) == ok);
    CHECK(exchange.audio_commit(batch, pattern(1)) == ok);
    CHECK(peek(exchange).size() == 3);
    CHECK(exchange.audio_commit(peek(exchange), pattern(4)) == ok);

    for (const double value : {-0.0, 0.0, std::nextafter(0.5, 0.0),
                               0.5, std::nextafter(0.5, 1.0), 1.0}) {
        auto exact = pattern(1535);
        exact.expression = value;
        CHECK(exchange.ui_enqueue(exact));
        auto copied = peek(exchange);
        same(copied.snapshots()[0], exact);
        CHECK(exchange.audio_commit(copied, exact) == ok);
        same(published(exchange).controls, exact);
        auto saved = pattern(7);
        CHECK(exchange.ui_snapshot_for_save(saved));
        same(saved, exact);
    }
}

void test_every_retained_preset_publication() {
    static_assert(kStatePublicationCellCount == 50);
    StateExchange exchange;
    std::uint64_t sequence = 0;
    for (unsigned upper = 0; upper < 10; ++upper) {
        for (unsigned lower = 0; lower < 10; ++lower) {
            for (unsigned routing = 0; routing < 16; ++routing) {
                auto expected = pattern(upper * 160 + lower * 16 + routing + 1);
                expected.fixed_registrations = {static_cast<FixedRegistration>(upper),
                                                static_cast<FixedRegistration>(lower)};
                expected.selected_banks = {static_cast<DrawbarBank>(routing & 1U),
                                           static_cast<DrawbarBank>((routing >> 1U) & 1U)};
                expected.route_enabled = {(routing & 4U) != 0, (routing & 8U) != 0};
                expected.expression = (routing & 1U) != 0 ? -0.0 : 0.0;
                const auto before = published(exchange);
                CHECK(exchange.ui_enqueue(expected).sequence == ++sequence);
                auto saved = pattern(65000);
                CHECK(exchange.ui_snapshot_for_save(saved));
                same(saved, expected); // Pending saves use a copied UI snapshot.
                same(published(exchange), before);
                const auto batch = peek(exchange);
                CHECK(batch.size() == 1 && batch.last_sequence() == sequence);
                same(batch.snapshots()[0], expected);
                CHECK(exchange.audio_can_commit(batch) == ok);
                CHECK(exchange.audio_commit(batch, expected) == ok);
                const auto applied = published(exchange);
                CHECK(applied.acknowledged_sequence == sequence);
                CHECK(applied.publication_revision == sequence * 2);
                same(applied.controls, expected); // This read decodes all atomic cells.
                saved = pattern(64000);
                CHECK(exchange.ui_snapshot_for_save(saved));
                same(saved, expected); // Acknowledged save must retain cancelled modes.
            }
        }
    }
    CHECK(sequence == 1600);
}

void test_finite_lifetimes() {
    // Small immutable limits execute the same checked-before-addition paths as
    // the maximum lifetime. No test hook writes a private cursor or payload.
    StateExchange exchange({2, 2});
    CHECK(exchange.ui_enqueue(pattern(1)).sequence == 1);
    CHECK(exchange.audio_commit(peek(exchange), pattern(1)) == ok);
    CHECK(exchange.ui_enqueue(pattern(2)).sequence == 2);
    CHECK(exchange.audio_commit(peek(exchange), pattern(2)) == ok);
    const auto final = published(exchange);
    CHECK(final.acknowledged_sequence == 2 && final.publication_revision == 4);
    CHECK(exchange.ui_enqueue(pattern(3)).status == StateExchangeStatus::SequenceExhausted);
    const auto exhausted = peek(exchange);
    CHECK(exchange.audio_can_commit(exhausted) == StateExchangeStatus::SequenceExhausted);
    CHECK(exchange.audio_commit(exhausted, pattern(9)) == StateExchangeStatus::SequenceExhausted);
    same(published(exchange), final);

    StateExchange no_loads({0, 1});
    CHECK(no_loads.ui_enqueue(pattern(1)).status == StateExchangeStatus::SequenceExhausted);
    CHECK(no_loads.audio_commit(peek(no_loads), pattern(1)) == ok);
    CHECK(published(no_loads).acknowledged_sequence == 0);
    StateExchange no_publications({1, 0});
    CHECK(no_publications.ui_enqueue(pattern(1)));
    const auto pending = peek(no_publications);
    CHECK(no_publications.audio_can_commit(pending) == StateExchangeStatus::SequenceExhausted);
    CHECK(no_publications.audio_commit(pending, pattern(1)) == StateExchangeStatus::SequenceExhausted);
    CHECK(peek(no_publications).size() == 1);
    auto saved = pattern(2);
    CHECK(no_publications.ui_snapshot_for_save(saved));
    same(saved, pattern(1));

    const auto maximum = std::numeric_limits<std::uint64_t>::max();
    StateExchange maximum_limits({maximum, maximum / 2});
    CHECK(maximum_limits.ui_enqueue(pattern(1)));
    CHECK(maximum_limits.audio_commit(peek(maximum_limits), pattern(1)) == ok);
    for (const auto invalid_limit : {maximum / 2 + 1, maximum}) {
        StateExchange invalid({maximum, invalid_limit});
        CHECK(invalid.ui_enqueue(pattern(1)).status == StateExchangeStatus::InvalidLimits);
        auto preserved = peek(maximum_limits);
        const auto count = preserved.size();
        const auto sequence = preserved.last_sequence();
        CHECK(invalid.audio_peek(preserved) == StateExchangeStatus::InvalidLimits);
        CHECK(preserved.size() == count && preserved.last_sequence() == sequence);
        CHECK(maximum_limits.audio_can_commit(preserved) == ok);
        CHECK(invalid.audio_can_commit(preserved) == StateExchangeStatus::InvalidLimits);
        CHECK(invalid.audio_commit(preserved, pattern(1)) == StateExchangeStatus::InvalidLimits);
        auto result = final;
        CHECK(!invalid.read_published(result));
        same(result, final);
        saved = pattern(321);
        CHECK(!invalid.ui_snapshot_for_save(saved));
        same(saved, pattern(321));
    }
}

constexpr std::string_view manual_records =
    "manual upper selected A route_enabled 0\n"
    "bank A 0 1 2 3 4 5 6 7 8\n"
    "bank B 8 7 6 5 4 3 2 1 0\n"
    "manual lower selected B route_enabled 1\n"
    "bank A 1 3 5 7 0 2 4 6 8\n"
    "bank B 8 6 4 2 0 7 5 3 1\nend\n";
constexpr std::string_view percussion_record =
    "percussion enabled 1 harmonic third volume soft decay fast\n";
constexpr std::string_view current_manual_records =
    "manual upper selected A fixed_registration none route_enabled 0\n"
    "bank A 0 1 2 3 4 5 6 7 8\n"
    "bank B 8 7 6 5 4 3 2 1 0\n"
    "manual lower selected B fixed_registration none route_enabled 1\n"
    "bank A 1 3 5 7 0 2 4 6 8\n"
    "bank B 8 6 4 2 0 7 5 3 1\nend\n";

ControlSnapshot historical(std::uint32_t version) {
    std::string bytes = "B3CONTROLS" + std::to_string(version) + "\nexpression 0.375\n";
    if (version >= 2) bytes += percussion_record;
    if (version >= 3) bytes += "pedal drawbars 2 7\n";
    bytes += manual_records;
    std::istringstream input(bytes);
    auto result = pattern(555);
    std::string error;
    CHECK(parse_controls(input, result, error));
    CHECK(error.empty());
    ControlSnapshot expected{};
    expected.expression = 0.375;
    expected.selected_banks = {DrawbarBank::A, DrawbarBank::B};
    expected.route_enabled = {false, true};
    expected.drawbars[0][0] = {0, 1, 2, 3, 4, 5, 6, 7, 8};
    expected.drawbars[0][1] = {8, 7, 6, 5, 4, 3, 2, 1, 0};
    expected.drawbars[1][0] = {1, 3, 5, 7, 0, 2, 4, 6, 8};
    expected.drawbars[1][1] = {8, 6, 4, 2, 0, 7, 5, 3, 1};
    if (version >= 2) expected.percussion = {true, PercussionHarmonic::Third,
        PercussionVolume::Soft, PercussionDecay::Fast};
    if (version >= 3) expected.pedal_drawbars = {2, 7};
    same(result, expected);
    return result;
}

struct DynamicHistory {
    std::uint64_t frame{0};
    double rate{0};
    std::array<double, kToneSourceCount> phases{};
    std::array<std::array<ContactKeySnapshot, kManualKeyCount>, kManualCount> contacts{};
    std::array<std::array<bool, kManualKeyCount>, kManualCount> keys{};
    PedalContactStates pedal_contacts{};
    std::array<bool, kPedalCount> pedals{};
    PedalRenderDiagnostics last_pedal{};
    double readiness{0};
    bool detector{false};
    std::size_t manual_count{0};
    std::size_t pedal_count{0};

    bool operator==(const DynamicHistory&) const noexcept = default;
};

DynamicHistory history(const Engine& engine) {
    DynamicHistory result{};
    result.frame = engine.frame_clock();
    result.rate = engine.sample_rate();
    result.manual_count = engine.active_key_count();
    result.pedal_count = engine.active_pedal_count();
    for (std::size_t i = 0; i < kToneSourceCount; ++i) {
        CHECK(engine.source_phase_turns(static_cast<ToneId>(i + 1), result.phases[i]));
    }
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        for (std::size_t key = 0; key < kManualKeyCount; ++key) {
            const auto note = static_cast<std::uint32_t>(kMinManualMidiNote + key);
            CHECK(engine.contact_snapshot(static_cast<Manual>(manual), note,
                                           result.contacts[manual][key]));
            result.keys[manual][key] = engine.key_down(static_cast<Manual>(manual), note);
        }
    }
    CHECK(engine.pedal_contacts_snapshot(result.pedal_contacts));
    for (std::size_t i = 0; i < kPedalCount; ++i) {
        result.pedals[i] = engine.pedal_down(PedalId{static_cast<std::uint8_t>(i + 1)});
    }
    result.last_pedal = engine.last_pedal_frame();
    const auto percussion = engine.percussion_diagnostics();
    result.readiness = percussion.readiness;
    result.detector = percussion.physical_detector;
    return result;
}

void test_state_formats_and_candidate_engine() {
    StateExchange exchange;
    for (std::uint32_t version = 1; version <= 3; ++version) {
        CHECK(exchange.ui_enqueue(historical(version)).sequence == version);
    }
    Engine live;
    CHECK(live.prepare(load_test_profile(), {48000.0, 1024, 17, 0},
                       make_nominal_console_model()) == Status::Ok);
    auto controls = pattern(8192);
    controls.selected_banks = {DrawbarBank::B, DrawbarBank::B};
    controls.fixed_registrations = {FixedRegistration::None, FixedRegistration::None};
    controls.route_enabled = {true, true};
    controls.percussion.enabled = true;
    CHECK(live.restore_controls(controls));
    const std::array<Event, 4> initial_events{{
        {0, EventType::NoteOn, Manual::Upper, 60, 100},
        {0, EventType::NoteOn, Manual::Lower, 48, 100},
        {0, EventType::PedalOn, Manual::Lower, 1, 100},
        {0, EventType::PedalOn, Manual::Lower, 25, 100}}};
    CHECK(live.process(512, {}, initial_events));
    const std::array<Event, 2> moving_events{{
        {0, EventType::NoteOn, Manual::Upper, 64, 100},
        {0, EventType::KeyPosition, Manual::Lower, 48, 0.25}}};
    CHECK(live.process(32, {}, moving_events));
    const auto active = history(live);
    CHECK(active.manual_count == 3 && active.pedal_count == 2);
    CHECK(active.readiness < 1.0 && active.readiness > 0.0 && active.detector);
    CHECK(active.contacts[0][64 - kMinManualMidiNote].position > 0.0);
    CHECK(active.contacts[0][64 - kMinManualMidiNote].position < 1.0);

    const auto batch = peek(exchange);
    CHECK(batch.size() == 3 && exchange.audio_can_commit(batch) == ok);
    const auto before_publication = published(exchange);
    auto candidate = live;
    for (const auto& restore : batch.snapshots()) {
        CHECK(candidate.restore_controls(restore));
        CHECK(history(candidate) == active);
    }
    std::array<float, 8> output{};
    output.fill(42.0F);
    const auto output_before = output;
    const std::array<Event, 1> rejected{{
        {0, EventType::Expression, Manual::Upper, 0,
         std::numeric_limits<double>::quiet_NaN()}}};
    CHECK(candidate.process(8, output, rejected).status == Status::InvalidEvent);
    CHECK(output == output_before);
    CHECK(history(live) == active);
    same(live.controls_snapshot(), controls);
    // A rejected whole callback never installs its candidate or commits token.
    same(published(exchange), before_publication);
    CHECK(peek(exchange).size() == 3);
    CHECK(exchange.audio_can_commit(batch) == ok);

    candidate = live;
    for (const auto& restore : batch.snapshots()) CHECK(candidate.restore_controls(restore));
    CHECK(candidate.process(0, {}, {}));
    CHECK(history(candidate) == active);
    auto reference = live;
    CHECK(reference.restore_controls(historical(3)));
    live = candidate;
    CHECK(exchange.audio_commit(batch, live.controls_snapshot()) == ok);
    CHECK(history(live) == active);
    CHECK(published(exchange).acknowledged_sequence == 3);
    auto save = pattern(400);
    CHECK(exchange.ui_snapshot_for_save(save));
    same(save, historical(3));
    std::string bytes;
    std::string error;
    CHECK(serialize_controls(save, bytes, error));
    CHECK(bytes == std::string("B3CONTROLS4\nregistration_catalog atlas-chapel-nominal-v1 sha256 "
        "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf\nexpression 0.375\n") +
        std::string(percussion_record) + "pedal drawbars 2 7\n" + std::string(current_manual_records));
    std::istringstream restored_stream(bytes);
    auto parsed_again = pattern(401);
    CHECK(parse_controls(restored_stream, parsed_again, error));
    same(parsed_again, save);

    std::array<float, 128> actual_audio{};
    std::array<float, 128> reference_audio{};
    CHECK(live.process(128, actual_audio, {}));
    CHECK(reference.process(128, reference_audio, {}));
    CHECK(actual_audio == reference_audio);
    CHECK(history(live) == history(reference));
    CHECK(live.active_key_count() == 3 && live.active_pedal_count() == 2);

    // Unsupported persisted versions fail before any enqueue or DSP mutation.
    std::istringstream future("B3CONTROLS5\nend\n");
    const auto saved_before = save;
    CHECK(!parse_controls(future, save, error));
    same(save, saved_before);
    CHECK(peek(exchange).size() == 0);
}

void test_delayed_reader() {
    StateExchange exchange;
    constexpr std::uint64_t publications = 24000;
    for (std::uint64_t generation = 1; generation <= publications; ++generation) {
        const auto batch = peek(exchange);
        CHECK(batch.size() == 0 && exchange.audio_can_commit(batch) == ok);
        CHECK(exchange.audio_commit(batch, pattern(generation)) == ok);
    }
    // No UI read occurred during these publications; the writer never needs
    // a reader-owned slot, acknowledgement or retry to make progress.
    const auto current = published(exchange);
    CHECK(current.acknowledged_sequence == 0);
    CHECK(current.publication_revision == 2 * publications);
    same(current.controls, pattern(publications));
    auto saved = pattern(1);
    CHECK(exchange.ui_snapshot_for_save(saved));
    same(saved, pattern(publications));
}

void test_concurrent_producer_audio_and_observer() {
    StateExchange exchange;
    constexpr std::uint64_t total = 12000;
    std::atomic<bool> started{false};
    std::atomic<bool> finished{false};
    std::uint64_t producer_reads = 0;
    std::uint64_t observer_reads = 0;
    std::uint64_t observer_busy = 0;
    std::uint64_t callback_count = 0;
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(60);
    const auto check_deadline = [&] { CHECK(std::chrono::steady_clock::now() < deadline); };

    std::thread producer([&] {
        for (std::uint64_t seq = 1; seq <= 4; ++seq) {
            CHECK(exchange.ui_enqueue(pattern(seq)).sequence == seq);
        }
        CHECK(exchange.ui_enqueue(pattern(5)).status == StateExchangeStatus::QueueFull);
        started.store(true, std::memory_order_release);
        std::uint64_t accepted = 4;
        std::uint64_t iteration = 0;
        while (accepted < total) {
            const auto result = exchange.ui_enqueue(pattern(accepted + 1));
            if (result) {
                ++accepted;
                CHECK(result.sequence == accepted);
            } else {
                CHECK(result.status == StateExchangeStatus::QueueFull);
                std::this_thread::yield(); // Test scheduling only, never production audio.
            }
            auto saved = pattern(64000);
            if (exchange.ui_snapshot_for_save(saved)) {
                same(saved, pattern(accepted));
                ++producer_reads;
            } else {
                same(saved, pattern(64000));
            }
            if ((++iteration & 1023U) == 0) check_deadline();
        }
        while (!finished.load(std::memory_order_acquire)) {
            auto saved = pattern(64000);
            if (exchange.ui_snapshot_for_save(saved)) {
                same(saved, pattern(total));
                ++producer_reads;
            } else {
                same(saved, pattern(64000));
            }
            if ((++iteration & 1023U) == 0) check_deadline();
        }
    });
    std::thread audio([&] {
        while (!started.load(std::memory_order_acquire)) {
            check_deadline();
            std::this_thread::yield();
        }
        std::uint64_t acknowledged = 0;
        std::uint64_t iteration = 0;
        while (acknowledged < total) {
            const auto batch = peek(exchange);
            CHECK(exchange.audio_can_commit(batch) == ok);
            if (batch.size() == 0) {
                std::this_thread::yield();
            } else {
                for (std::size_t i = 0; i < batch.size(); ++i) {
                    same(batch.snapshots()[i], pattern(acknowledged + i + 1));
                }
                CHECK(batch.last_sequence() == acknowledged + batch.size());
                const auto value = batch.snapshots().back();
                // Give the producer a chance to append between preflight and
                // commit. Its release store must not invalidate this token.
                if ((iteration & 31U) == 0) std::this_thread::yield();
                CHECK(exchange.audio_commit(batch, value) == ok);
                acknowledged = batch.last_sequence();
                ++callback_count;
            }
            if ((++iteration & 1023U) == 0) check_deadline();
        }
        finished.store(true, std::memory_order_release);
    });
    std::thread observer([&] {
        std::uint64_t last_ack = 0;
        std::uint64_t last_revision = 0;
        std::uint64_t iteration = 0;
        do {
            StatePublishedControls value{pattern(64000), 64001, 64002};
            const auto sentinel = value;
            if (exchange.read_published(value)) {
                CHECK(value.acknowledged_sequence >= last_ack);
                CHECK(value.publication_revision >= last_revision);
                CHECK((value.publication_revision & 1U) == 0);
                if (value.publication_revision == 0) same(value.controls, ControlSnapshot{});
                else same(value.controls, pattern(value.acknowledged_sequence));
                last_ack = value.acknowledged_sequence;
                last_revision = value.publication_revision;
                ++observer_reads;
            } else {
                same(value, sentinel);
                ++observer_busy;
            }
            if ((++iteration & 1023U) == 0) check_deadline();
        } while (!finished.load(std::memory_order_acquire) || observer_reads == 0);
    });
    producer.join();
    audio.join();
    observer.join();
    CHECK(callback_count >= total / kStateQueueCapacity);
    CHECK(callback_count <= total);
    CHECK(observer_reads > 0);
    // Joining provides a quiescent ownership handoff for this final UI read.
    const auto final = published(exchange);
    CHECK(final.acknowledged_sequence == total);
    CHECK(final.publication_revision == callback_count * 2);
    same(final.controls, pattern(total));
    auto saved = pattern(1);
    CHECK(exchange.ui_snapshot_for_save(saved));
    same(saved, pattern(total));
    std::cout << "concurrent callbacks=" << callback_count
              << " producer_reads=" << producer_reads
              << " observer_reads=" << observer_reads
              << " bounded_read_failures=" << observer_busy << '\n';
}

} // namespace

int main() {
    test_defaults_queue_and_save();
    test_invalid_values_tokens_and_signed_zero();
    test_every_retained_preset_publication();
    test_finite_lifetimes();
    test_state_formats_and_candidate_engine();
    test_delayed_reader();
    test_concurrent_producer_audio_and_observer();
    std::cout << "StateExchange: queue, publication, migration and engine history checks passed\n";
}
